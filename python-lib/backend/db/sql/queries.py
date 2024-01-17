from abc import ABC, abstractmethod
from typing import Optional
import dataiku
from dataiku.sql import Dialects, Column, Constant, toSQL, List as ListBuilder, Expression
from dataiku.sql.expression import Operator
from typing import Dict, Union, List, Tuple, Any, TypedDict
from enum import Enum
import functools



SUPPORTED_OPERATORS = [Operator.EQ, Operator.NE]


class WhereCondition(TypedDict):
    operator: Operator
    value: Union[str, float, int, bool]
    column: str


def get_identifier_quote_char() -> str:
    return '"'


def quote_identifier(string: str) -> str:
    sep = get_identifier_quote_char()
    return sep + string.replace(sep, sep + sep) + sep


def get_string_quote_char() -> str:
    return "'"


def quote_string(value: str) -> str:
    return escape_string(value)


def needs_backslash_doubling(dialect: Dialects) -> bool:
    ## TODO: Implement
    return False


def escape_string(value: str):
    escaped_str = (
        get_string_quote_char() + value.replace("'", "''") + get_string_quote_char()
    )
    return escaped_str


def _sql_true():
    return Constant(1).eq(Constant(1))


def __escape_string(
    match_string: str,
    extra_special_chars: Optional[List[str]] = None,
    double: bool = False,
) -> str:
    special_characters = ["%", "_", "[", "]", "^", "'", '"']
    if extra_special_chars:
        special_characters += extra_special_chars

    escaped_match_string = ""
    for character in str(match_string):
        if character in special_characters:
            character = f"\{character}" if not double else f"\\{character}"
        escaped_match_string += character
    return f"{escaped_match_string}"


## This is slow
def _get_like_string_cond(columns: List[Column], like_string: Union[str, List[str]]):
    cond = _sql_true()
    if isinstance(like_string, str):
        if len(like_string) == 0:
            return cond
        like_string = __escape_string(like_string=like_string).lower()
        like_string = f"%{like_string}%"
        cond = functools.reduce(
            lambda c1, c2: c1.and_(c2.cast("STRING").lower().like(like_string)),
            columns,
            _sql_true(),
        )
    elif isinstance(like_string, list):
        if all([len(ls) == 0 for ls in like_string]):
            return cond
        if len(like_string) != len(columns):
            raise Exception("like_string should have the same length as columns_name.")
        for i, ls in enumerate(like_string):
            if len(ls) > 0:
                ls_ready = __escape_string(match_string=ls).lower()
                like_string = f"%{ls_ready}%"
                cond = cond.and_(columns[i].cast("STRING").lower().like(ls_ready))
    return cond


def _get_where_and_cond(conds: List[WhereCondition]):
    if len(conds) == 0:
        return _sql_true()
    else:
        final_cond = _sql_true()
        for condition in conds:
            if condition["operator"] in SUPPORTED_OPERATORS:
                if condition["operator"] == Operator.EQ:
                    final_cond = final_cond.and_(
                        Column(condition["column"]).eq(Constant(condition["value"]))
                    )
                elif condition["operator"] == Operator.NE:
                    final_cond = final_cond.and_(
                        Column(condition["column"]).ne(Constant(condition["value"]))
                    )

        return final_cond


def get_quoted_table_full_name(
    catalog: Optional[str], schema: Optional[str], table: str
) -> str:
    if not catalog:
        if not schema:
            return quote_identifier(table)
        else:
            return quote_identifier(schema) + "." + quote_identifier(table)
    else:
        if not schema:
            raise ValueError("schema cannot be empty when catalog is present")
        return (
            quote_identifier(catalog)
            + "."
            + quote_identifier(schema)
            + "."
            + quote_identifier(table)
        )


def get_quoted_table_full_name_snowflake(
    catalog: Optional[str], schema: Optional[str], table: str
):
    if not catalog:
        if not schema:
            return quote_identifier(table)
        else:
            return quote_identifier(schema) + "." + quote_identifier(table)
    else:
        quoted_schema = "" if schema is None else quote_identifier(schema)
        return (
            quote_identifier(catalog)
            + "."
            + quoted_schema
            + "."
            + quote_identifier(table)
        )


def get_table_name_from_dataset(dataset: dataiku.Dataset):
    loc = dataset.get_location_info()
    dialect = dataset.get_config().get("type")
    if loc.get("locationInfoType") != "SQL":
        raise ValueError("Cannot only execute query on an SQL dataset")
    table_name = loc.get("info").get("table")
    catalog_name = loc.get("info").get("catalog")
    schema_name = loc.get("info").get("schema")
    if dialect == Dialects.SNOWFLAKE:
        return get_quoted_table_full_name_snowflake(
            catalog=catalog_name, schema=schema_name, table=table_name
        )
    else:
        return get_quoted_table_full_name(
            catalog=catalog_name, schema=schema_name, table=table_name
        )


class QueryBuilder(ABC):
    def __init__(self, dataset: dataiku.Dataset):
        self.dataset = dataset
        self.table_name = get_table_name_from_dataset(dataset=dataset)

    @abstractmethod
    def build(self) -> str:
        """Builds the final Query"""

    @abstractmethod
    def _query_start(self) -> str:
        """Returns the query start string"""


class QueryBuilderWithWhere(QueryBuilder):
    ## Does only handle simple where comparaisons
    def __init__(self, dataset: dataiku.Dataset):
        super().__init__(dataset=dataset)
        self.wheres: List[WhereCondition] = []

    ## Adds only a Like condition
    def _add_cond(
        self, column: str, value: Union[str, bool, int, float], operator: Operator
    ):
        self.wheres.append(
            WhereCondition(operator=operator, column=column, value=value)
        )

    def add_conds(self, conds: List[WhereCondition]):
        for cond in conds:
            self._add_cond(cond["column"], cond["value"], cond["operator"])
        return self
    


    def _has_where_conds(self):
        return len(self.wheres) > 0

    def _traslate_where_conds(self):
        if len(self.wheres) > 0:
            _expr = _get_where_and_cond(self.wheres)
            translation = toSQL(_expr, dataset=self.dataset)
            return translation
        return ""


class UpdateQueryBuilder(QueryBuilderWithWhere):
    def __init__(self, dataset: dataiku.Dataset):
        super().__init__(dataset=dataset)
        self.sets: Dict[str, Union[str, bool, int, float]] = {}  ## values to set

    def _query_start(self) -> str:
        return "UPDATE " + self.table_name

    def _add_set_col(self, column: str, value: Union[str, bool, int, float]):
        self.sets[column] = str(value)

    def add_set_cols(self, sets: List[Tuple[str, Union[str, bool, int, float]]]):
        for set_col in sets:
            self._add_set_col(column=set_col[0], value=set_col[1])
        return self

    def _translate_set_cols(self):
        args = [Column(k).eq(Constant(v)) for k, v in self.sets.items()]
        if len(args) > 0:
            builder = ListBuilder(*args)
            result = toSQL(builder, dataset=self.dataset)
            return result[1:-1]
        return ""

    def _has_set_cols(self):
        return len(self.sets.keys()) > 0

    def build(self):
        if not self._has_set_cols():
            raise ValueError(
                "Update query needs at least one column to be set to a value"
            )
        query_raw = self._query_start() + " SET " + self._translate_set_cols()
        if self._has_where_conds():
            query_raw += " WHERE " + self._traslate_where_conds()
        return query_raw


class DeleteQueryBuilder(QueryBuilderWithWhere):
    def __init__(self, dataset: dataiku.Dataset):
        super().__init__(dataset=dataset)

    def _query_start(self) -> str:
        return "DELETE FROM " + self.table_name

    def build(self):
        query_raw = self._query_start()
        if self._has_where_conds():
            query_raw += " WHERE " + self._traslate_where_conds()
        return query_raw


class InsertQueryBuilder(QueryBuilder):
    def __init__(self, dataset: dataiku.Dataset):
        super().__init__(dataset=dataset)
        self.columns: List[str] = []
        self.values: List[List[str]] = []
        self.TO_PARAM = "?"

    def add_column(self, column: str):
        self.columns.append(column)
        return self

    def add_columns(self, columns: List[str]):
        for column in columns:
            self.add_column(column)
        return self

    def add_value(self, value: List[Any]):
        if len(value) != len(self.columns):
            raise ValueError("Cannot add values to insert query")
        self.values.append([val for val in value])
        return self

    def add_values(self, values: List[List[Any]]):
        for value in values:
            self.add_value(value=value)
        return self

    def _query_start(self) -> str:
        return "INSERT INTO " + self.table_name

    def get_wrapped_cols(self) -> str:
        args = [Column(col) for col in self.columns]
        if len(args) > 0:
            builder = ListBuilder(*args)
            result = toSQL(builder, dataset=self.dataset)
            return result
        return ""

    def get_wrapped_value(self, value: List[str]):
        args = [Constant(val) for val in value]
        if len(args) > 0:
            builder = ListBuilder(*args)
            result = toSQL(builder, dataset=self.dataset)
            return result
        return None

    def get_wrapped_values(self) -> str:
        string_results = []
        for value in self.values:
            res = self.get_wrapped_value(value)
            if res:
                string_results.append(res)
        return ",".join(string_results)

    def parameterized_value(self) -> str:
        return " VALUES " + self.get_wrapped_values() + ";"

    def build(self) -> str:
        if not self.columns:
            raise ValueError("No columns found for the insert query builder")
        return (
            self._query_start()
            + " "
            + self.get_wrapped_cols()
            + self.parameterized_value()
        )
