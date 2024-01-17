from backend.utils.dataiku_api import dataiku_api
from model_assist.logging import logger
from dataiku import SQLExecutor2, Dataset
from dataiku.sql import Dialects, toSQL, Column, SelectQuery, Constant, Expression
from dataiku.sql.expression import Operator
import pandas as pd
from typing import List, Union, Optional, Literal, Dict, Tuple
import functools
from werkzeug.exceptions import BadRequest
from backend.models.base import (
    ConversationInfo,
    Conversation,
    QuestionData,
    Feedback,
    Source,
    LlmHistory,
)

from backend.db.sql.queries import (
    InsertQueryBuilder,
    DeleteQueryBuilder,
    UpdateQueryBuilder,
    _get_where_and_cond,
    WhereCondition,
)

from backend.utils.knowledge_filters import get_llm_friendly_name, get_knowledge_bank_name
import json
import uuid
import time
from enum import Enum

DB_NAME_CONF_ID = "logging_dataset"

DIALECT_VALUES = [
    getattr(Dialects, attr)
    for attr in dir(Dialects)
    if not callable(getattr(Dialects, attr)) and not attr.startswith("__")
]

class RecordState(Enum):
    PRESENT = "present"
    DELETED = "deleted"
    CLEARED = "cleared"


COLUMNS = [
    "conversation_id",
    "conversation_name",
    "knwoledge_bank_id",
    "knwoledge_bank_name",
    "llm_name",
    "user",
    "message_id",
    "question",
    "filters",
    "answer",
    "sources",
    "feedback_value",
    "feedback_choice",
    "feedback_message",
    "timestamp",
    "state"
]

CONVERSATION_DEFAULT_NAME = "New chat"


class ConversationSQL:
    def __init__(self):
        self.config = dataiku_api.webapp_config
        self.db_name = self.config.get(DB_NAME_CONF_ID, None)
        self.permanent_delete = self.config.get("permanent_delete", True)
        self.__verify()
        self.dataset = Dataset(
            project_key=dataiku_api.default_project_key, name=self.db_name
        )
        self.__init_dataset()
        self.executor = SQLExecutor2(dataset=self.dataset)

    def __verify(self):
        if self.db_name is None or self.db_name == "":
            logger.error("Logging Database name should not be null")
            raise ValueError("Logging Database name should not be null")
        self.__check_db_exists()
        self.__check_supported_dialect()

    def __check_db_exists(self):
        project = dataiku_api.client.get_project(
            dataiku_api.default_project_key)
        data = project.list_datasets()
        datasets = [item.name for item in data]
        logger.debug(
            f"Searching for {self.db_name} in this project datasets: {datasets}"
        )
        if self.db_name in datasets:
            return True
        else:
            logger.error("Logging dataset does not exist")
            raise ValueError("Logging dataset does not exist")

    def __check_supported_dialect(self):
        # TODO: Limit dialects here is needed
        dataset = Dataset(
            project_key=dataiku_api.default_project_key, name=self.db_name
        )
        dataset_type = dataset.get_config().get("type")
        result = dataset_type in DIALECT_VALUES
        if result:
            return
        else:
            logger.error(f"Dataset Type {dataset_type} is not supported")
            raise ValueError(f"Dataset Type {dataset_type} is not supported")

    def __init_dataset(self):
        try:
            self.dataset.read_schema(raise_if_empty=True)
        except Exception as e:
            logger.info("Initializing the dataset schema")
            df = ConversationSQL.get_init_df()
            self.dataset.write_with_schema(df=df)

    @staticmethod
    def get_init_df():
        data = {col: [] for col in COLUMNS}
        return pd.DataFrame(data=data, columns=COLUMNS, dtype=str)

    def select_columns_from_dataset(
        self,
        columns_name: List[str],
        distinct: bool = False,
        eq_cond: List[WhereCondition] = [],
        format_: Literal["dataframe", "iter"] = "dataframe",
        limit: int = None,
        order_by: str = None,
    ):
        ConversationSQL.__validate_columns(columns_name)
        columns_to_select = [Column(str(col)) for col in columns_name]

        select_query = SelectQuery()
        if distinct:
            select_query.distinct()
        select_query.select_from(self.dataset)

        if columns_name == COLUMNS:
            select_query.select(Column("*"))
        else:
            select_query.select(columns_to_select)

        
        where_cond = _get_where_and_cond(eq_cond)

        select_query.where(where_cond)

        if limit:
            select_query.limit(limit)

        if order_by:
            order_by_col = Column(str(order_by))
            select_query.order_by(order_by_col)

        return self.execute(select_query, format_=format_)

    def execute(
        self,
        query_raw,
        format_: Literal["dataframe", "iter"] = "dataframe",
    ):
        try:
            query = toSQL(query_raw, dataset=self.dataset)
            logger.debug(f"Executing query: {query}")
        except Exception as err:
            raise BadRequest(f"Error when generating SQL query: {err}")

        if format_ == "dataframe":
            try:
                query_result = self.executor.query_to_df(
                    query=query).fillna("")
                return query_result
            except Exception as err:
                raise BadRequest(f"Error when generating SQL query: {err}")
        elif format_ == "iter":
            try:
                query_result = self.executor.query_to_iter(
                    query=query).iter_tuples()
                return query_result
            except Exception as err:
                raise BadRequest(f"Error when executing SQL query: {err}")

    def execute_commit(self):
        return

    def get_user_conversations(self, auth_identifier: str):
        column_names = ["user", "conversation_id",
                        "conversation_name", "timestamp", "state"]
        order_by_column = "timestamp"
        eq_cond_present = [
            WhereCondition(column="user", operator=Operator.EQ,
                           value=auth_identifier),
            WhereCondition(column="state", operator=Operator.EQ, value=RecordState.PRESENT.value)
        ]
        eq_cond_cleared = [
            WhereCondition(column="user", operator=Operator.EQ,
                           value=auth_identifier),
            WhereCondition(column="state", operator=Operator.EQ, value=RecordState.CLEARED.value)
        ]

        format_ = "dataframe"
        result_cleared: pd.DataFrame = self.select_columns_from_dataset(
            columns_name=column_names,
            distinct=True,
            eq_cond=eq_cond_cleared,
            format_=format_,
            order_by=order_by_column,
        )

        result_present: pd.DataFrame = self.select_columns_from_dataset(
            columns_name=column_names,
            distinct=True,
            eq_cond=eq_cond_present,
            format_=format_,
            order_by=order_by_column,
        )

        conversations: Dict[str, ConversationInfo] = {}

        for index, row in pd.concat([result_cleared, result_present]).iterrows():
            conversation_id = row["conversation_id"]

            # Check if the id is not already in the dictionary or if the timestamp is lower
            if (
                conversation_id not in conversations
                or row["timestamp"] < conversations[conversation_id]["timestamp"]
            ):
                conversations[conversation_id] = ConversationInfo(
                    id=conversation_id,
                    name=row["conversation_name"],
                    timestamp=row["timestamp"],
                )
        return list(conversations.values())

    def get_conversation(self, auth_identifier: str, conversation_id: str, only_present: bool = True):
        columns_name = COLUMNS

        eq_cond = [
            WhereCondition(column="user", value=auth_identifier,
                           operator=Operator.EQ),
            WhereCondition(
                column="conversation_id", value=conversation_id, operator=Operator.EQ
            )  
        ]
        if only_present:
            eq_cond.append(
                WhereCondition(
                    column="state", value=RecordState.PRESENT.value, operator=Operator.EQ
                )
            )
        format_ = "dataframe"
        order_by = "message_id"
        result: pd.DataFrame = self.select_columns_from_dataset(
            columns_name=columns_name,
            eq_cond=eq_cond,
            format_=format_,
            order_by=order_by,
        )
        return ConversationSQL.convert_query_result_to_conversation(result)

    def add_record(
        self,
        record: QuestionData,
        auth_identifier: str,
        conversation_id: Optional[str],
        conversation_name: Optional[str] = CONVERSATION_DEFAULT_NAME,
        knowledge_bank_id: Optional[str] = None,
        llm_id: Optional[str] = None
    ):
        conversation = None
        if conversation_id is not None:
            conversation = self.get_conversation(
                auth_identifier, conversation_id, only_present=False)
        record_id = str(0) if conversation is None else str(
            len(conversation["data"]))
        print(f"record is {record['sources']}")
        record_value = [
            conversation_id if not conversation is None else str(uuid.uuid4()),
            conversation_name if conversation is None else conversation["name"],
            knowledge_bank_id,
            get_knowledge_bank_name(knowledge_bank_id),
            get_llm_friendly_name(llm_id),
            auth_identifier,
            record_id,
            record["query"],
            json.dumps({"filters": record["filters"]}),
            record["answer"],
            json.dumps({"sources": record["sources"]}),
            record["feedback"]["value"] if record["feedback"] else "",
            ";".join(record["feedback"]["choice"]
                     ) if record["feedback"] else "",
            record["feedback"]["message"] if record["feedback"] else "",
            time.time(),
            RecordState.PRESENT.value
        ]
        insert_query = (
            InsertQueryBuilder(self.dataset)
            .add_columns(COLUMNS)
            .add_values(values=[record_value])
            .build()
        )
        try:
            logger.debug(f"Executing query {insert_query}")
            self.executor.query_to_df(insert_query, post_queries=["COMMIT"])
            return record_id, ConversationInfo(
                id=record_value[0], name=record_value[1], timestamp=record_value[-1]
            )
        except Exception as err:
            logger.error(err)
            raise BadRequest(f"Error when executing SQL query: {err}")

    def get_conversation_history(self, auth_identifier: str, conversation_id: str):
        conversation = self.get_conversation(
            auth_identifier=auth_identifier, conversation_id=conversation_id
        )
        if conversation:
            return [
                LlmHistory(input=item["query"], output=item["answer"])
                for item in conversation["data"]
            ]
        return []
    
    def clear_conversation_history_permanent(self, auth_identifier: str, conversation_id: str):
        delete_query = (
            DeleteQueryBuilder(self.dataset)
            .add_conds(
                [
                    WhereCondition(
                        column="conversation_id",
                        value=conversation_id,
                        operator=Operator.EQ,
                    ),
                    WhereCondition(
                        column="user", value=auth_identifier, operator=Operator.EQ
                    ),
                    WhereCondition(
                        column="message_id", value=str(0), operator=Operator.NE
                    ),
                ]
            )
            .build()
        )

        cols_to_keep = [
            "conversation_id",
            "conversation_name",
            "user",
            "timestamp",
            "message_id",
        ]

        set_cols = [
                    (
                        column,
                        ""
                        if (column != "sources" and column != "filters")
                        else json.dumps({"filters": None})
                        if column == "filters"
                        else json.dumps({"sources": []}),
                    )
                    for column in COLUMNS
                    if not column in cols_to_keep  
                ]
        
        set_cols.append(
            ("state", RecordState.CLEARED.value)
        )

        set_empty_record_query = (
            UpdateQueryBuilder(self.dataset)
            .add_conds(
                [
                    WhereCondition(
                        column="conversation_id",
                        value=conversation_id,
                        operator=Operator.EQ,
                    ),
                    WhereCondition(
                        column="user", value=auth_identifier, operator=Operator.EQ
                    ),
                    WhereCondition(
                        column="message_id", value=str(0), operator=Operator.EQ
                    ),
                ]
            )
            .add_set_cols(
                set_cols
            )
            .build()
        )
        try:
            self.executor.query_to_df(delete_query, post_queries=["COMMIT"])
            self.executor.query_to_df(
                set_empty_record_query, post_queries=["COMMIT"])
        except Exception as err:
            logger.error(err)
            raise BadRequest(f"Error when executing SQL query: {err}")

    def clear_conversation_history_non_permanant(self, auth_identifier: str, conversation_id: str):
        update_query = UpdateQueryBuilder(self.dataset).add_set_cols(
            [
                    ("state", RecordState.CLEARED.value)
            ]
        ).add_conds([
                    WhereCondition(
                        column="conversation_id",
                        value=conversation_id,
                        operator=Operator.EQ,
                    ),
                    WhereCondition(
                        column="user", value=auth_identifier, operator=Operator.EQ
                    )
        ]).build()

        try:
            self.executor.query_to_df(update_query, post_queries=["COMMIT"])
        except Exception as err:
            logger.error(err)
            raise BadRequest(f"Error when executing SQL query: {err}")


    def clear_conversation_history(self, auth_identifier: str, conversation_id: str):
        # This one is tricky as we need a seperate conversation dataset for this
        # Basic solution would be to delete everything except for the first message
        # and then update the message with blank answer and query
        if self.permanent_delete:
            self.clear_conversation_history_permanent(auth_identifier=auth_identifier, conversation_id=conversation_id)
        else:
            self.clear_conversation_history_non_permanant(auth_identifier=auth_identifier, conversation_id=conversation_id)

    def delete_user_conversation(self, auth_identifier: str, conversation_id: str):
        if self.permanent_delete:
            query = (
                DeleteQueryBuilder(self.dataset)
                .add_conds(
                    [
                        WhereCondition(
                            column="conversation_id",
                            value=conversation_id,
                            operator=Operator.EQ,
                        ),
                        WhereCondition(
                            column="user", value=auth_identifier, operator=Operator.EQ
                        ),
                    ]
                )
                .build()
            )
        else:
            query = UpdateQueryBuilder(self.dataset).add_set_cols(
                [
                    ("state", RecordState.DELETED.value)
                ]
            ).add_conds([
                WhereCondition(
                        column="conversation_id",
                        value=conversation_id,
                        operator=Operator.EQ,
                ),
                WhereCondition(
                        column="user", value=auth_identifier, operator=Operator.EQ
                ),
            ]).build()
        try:
            logger.debug(f"Executing query {query}")
            self.executor.query_to_df(query, post_queries=["COMMIT"])
        except Exception as err:
            logger.error(err)
            raise BadRequest(f"Error when executing SQL query: {err}")

    def delete_all_user_conversations(self, auth_identifier: str):
        if self.permanent_delete:
            query = (
                DeleteQueryBuilder(self.dataset)
                .add_conds(
                    [
                        WhereCondition(
                            column="user", value=auth_identifier, operator=Operator.EQ
                        )
                    ]
                )
                .build()
            )
        else:
            query = query = UpdateQueryBuilder(self.dataset).add_set_cols(
                [
                    ("state", RecordState.DELETED.value)
                ]
            ).add_conds([
                WhereCondition(
                        column="user", value=auth_identifier, operator=Operator.EQ
                ),
            ]).build()
        try:
            logger.debug(f"Executing query {query}")
            self.executor.query_to_df(query, post_queries=["COMMIT"])
        except Exception as err:
            logger.error(err)
            raise BadRequest(f"Error when executing SQL query: {err}")

    def update_feedback(
        self,
        auth_identifier: str,
        conversation_id: str,
        message_id: str,
        feedback: Feedback,
    ):
        update_quey = (
            UpdateQueryBuilder(self.dataset)
            .add_set_cols(
                [
                    ("feedback_value", feedback["value"]),
                    ("feedback_message", feedback["message"]),
                    ("feedback_choice", ";".join(feedback["choice"])),
                ]
            )
            .add_conds(
                [
                    WhereCondition(
                        column="conversation_id",
                        value=conversation_id,
                        operator=Operator.EQ,
                    ),
                    WhereCondition(
                        column="user", value=auth_identifier, operator=Operator.EQ
                    ),
                    WhereCondition(
                        column="message_id", value=str(message_id), operator=Operator.EQ
                    ),
                ]
            )
            .build()
        )
        try:
            logger.debug(f"Executing query {update_quey}")
            self.executor.query_to_df(update_quey, post_queries=["COMMIT"])
        except Exception as err:
            logger.error(err)
            raise BadRequest(f"Error when executing SQL query: {err}")

    @staticmethod
    def __validate_columns(columns_name: List[str]):
        return all(name in COLUMNS for name in columns_name)

    @staticmethod
    def convert_query_result_to_conversation(result: pd.DataFrame):
        if result.empty:
            return None
        else:
            result = result.sort_values(by="message_id", ascending=True)
            id = result["conversation_id"].iloc[0]
            name = result["conversation_name"].iloc[0]
            timestamp = result["timestamp"].iloc[0]
            auth_identifier = result["user"].iloc[0]
            question_data: List[QuestionData] = []
            for index, row in result.iterrows():
                query = row["question"]
                answer = row["answer"]
                feedback_value = row["feedback_value"]
                feedback_choice = row["feedback_choice"]
                feedback_message = row["feedback_choice"]
                message_timestamp = row["timestamp"]
                record_id = row["message_id"]
                feedback = None
                sources = ConversationSQL.load_sources(row["sources"])
                filters = ConversationSQL.load_filters(row["filters"])
                if feedback_value:
                    feedback = Feedback(
                        value=feedback_value,
                        message=feedback_message if feedback_message else "",
                        choice=ConversationSQL.format_feedback_choice(
                            feedback_choice),
                    )
                question_data.append(
                    QuestionData(
                        id=record_id,
                        query=query,
                        answer=answer,
                        filters=filters,
                        sources=sources,
                        feedback=feedback,
                        timestamp=message_timestamp,
                    )
                )
            return Conversation(
                id=id,
                name=name,
                timestamp=timestamp,
                auth_identifier=auth_identifier,
                data=question_data,
            )

    @staticmethod
    def format_feedback_choice(choice: Optional[str]):
        if choice is None or choice == "":
            return []
        return [value.strip() for value in choice.split(";")]

    @staticmethod
    def load_sources(sources: Optional[str]):
        sources_json = json.loads(sources)
        sources = sources_json.get("sources", [])
        result = [
            Source(excerpt=source["excerpt"], metadata=source["metadata"])
            for source in sources
        ]
        return result

    @staticmethod
    def load_filters(filters: Optional[str]):
        filters_json = json.loads(filters)
        filters = filters_json.get("filters", None)
        return filters


conversation_sql_manager = ConversationSQL()
