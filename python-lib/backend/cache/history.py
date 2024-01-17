from diskcache import Cache, Timeout, Index
from backend.models.base import (
    QuestionData,
    Conversation,
    ConversationInfo,
    LlmHistory,
)
import shutil
import hashlib
from typing import List, Optional, Union
from model_assist.logging import logger
import uuid
import time
import io
import json
from model_assist.logging import logger


# TODO: Make cache size limit & expiry time configurable at the plugin level
class HistoryCacheHandler(object):
    CONVERSATION_DEFAULT_NAME = "New chat"

    def __init__(
        self,
        directory: str,
        default_expire_time: int = 2
        * 24
        * 60
        * 60,  ## Conversations expire in two days
        size_limit: int = 2**30,
    ):
        logger.info(f"Started Cache on directory {directory}")
        self.cache = Cache(directory=directory, tag_index=True, size_limit=size_limit)
        ## Index stores conversation { id: name } mappings
        self.index = Index(directory)
        self.default_expire_time = default_expire_time

    def destroy(self):
        ## Destroy the cache permanently
        self.cache.close()
        try:
            shutil.rmtree(self.cache.directory)
        except OSError:  # Windows wonkiness
            pass

    def add_records(
        self,
        auth_identifier: str,
        records: Union[QuestionData, List[QuestionData]],
        conversation_id: Optional[str] = None,
        expire: Optional[int] = None,
    ):
        if conversation_id is None:
            conversation = HistoryCacheHandler.start_conversation_from_records(
                auth_identifier, records
            )
        else:
            conversation = self.read_conversation(auth_identifier, conversation_id)
            if conversation is None:
                conversation = HistoryCacheHandler.start_conversation(auth_identifier)
            if isinstance(records, list):
                conversation["data"].extend(records)
            else:
                conversation["data"].append(records)

        is_saved = self.save_conversation(
            auth_identifier, conversation["id"], conversation, expire
        )
        return ConversationInfo(
            id=conversation["id"],
            name=conversation["name"],
            timestamp=conversation["timestamp"],
        )

    def read_conversation(
        self, auth_identifier: str, conversation_id: Optional[str]
    ) -> Optional[Conversation]:
        if not conversation_id:
            return None
        signature = HistoryCacheHandler.compute_signature(
            auth_identifier, conversation_id
        )
        value = None
        for i in range(10):
            try:
                reader = self.cache.get(
                    key=signature, default=None, read=True, retry=False
                )
                value = json.loads(reader.read().decode())
                break
            except Timeout:
                logger.warning(
                    f"Cache timout exception occured during read on iteration {str(i)}"
                )
        return value

    def save_conversation(
        self,
        auth_identifier: str,
        conversation_id: str,
        conversation: Conversation,
        expire: Optional[int] = None,
    ) -> bool:
        signature = self.compute_signature(auth_identifier, conversation_id)
        tag = self.compute_tag(auth_identifier)
        is_set = False
        expire_time = expire if not expire is None else self.default_expire_time

        value = io.BytesIO(json.dumps(conversation).encode("utf-8"))
        for i in range(10):
            try:
                is_set = self.cache.set(
                    key=signature,
                    value=value,
                    expire=expire_time,
                    tag=tag,
                    read=True,
                    retry=False,
                )
                if is_set:
                    self.add_to_index(conversation)
                    break
            except Timeout:
                logger.warning(
                    f"Cache timout exception occured during set on iteration {str(i)}"
                )
        return is_set

    def delete_conversation(
        self,
        auth_identifier: str,
        conversation_id: str,
    ) -> bool:
        singature = self.compute_signature(auth_identifier, conversation_id)
        is_deleted = False
        for i in range(10):
            try:
                is_deleted = self.cache.delete(key=singature, retry=False)
                if is_deleted:
                    if auth_identifier in self.index:
                        index_value = self.index[auth_identifier]
                        removed_conv = index_value.pop(conversation_id)
                        self.index.update([(auth_identifier, index_value)])
                    break
            except Timeout:
                logger.warning(
                    f"Cache timout exception occured during delete on iteration {str(i)}"
                )
        return is_deleted

    def clear_conversation_history(
        self,
        auth_identifier: str,
        conversation_id: str,
    ):
        conversation = self.read_conversation(auth_identifier, conversation_id)
        if conversation:
            conversation["data"] = []
            self.save_conversation(auth_identifier, conversation_id, conversation)

    def delete_all_user_conversations(
        self,
        auth_identifier: str,
    ) -> int:
        tag = HistoryCacheHandler.compute_tag(auth_identifier)
        rows_count = self.cache.evict(tag=tag, retry=False)
        del self.index[auth_identifier]
        return rows_count

    def get_all_user_conversations(
        self,
        auth_identifier: str,
    ) -> List[ConversationInfo]:
        if auth_identifier in self.index:
            result = [
                ConversationInfo(
                    id=conversation_id,
                    name=self.index[auth_identifier][conversation_id]["name"],
                    timestamp=self.index[auth_identifier][conversation_id]["timestamp"],
                )
                for conversation_id in self.index[auth_identifier]
            ]
            result.reverse()
            return result
        return []

    def extract_llm_memory(
        self, auth_identifier: str, conversation_id: Optional[str]
    ) -> List[LlmHistory]:
        conversation = self.read_conversation(auth_identifier, conversation_id)
        if conversation:
            data = conversation["data"]
            if data:
                return [
                    LlmHistory(input=item["query"], output=item["answer"])
                    for item in data
                ]
            return []
        return []

    def volume(self):
        ## returns the estimated total size of the cache is disk in bytes
        return self.cache.volume()

    def check(self):
        ## verifies cache consistency. It can also fix inconsistencies and reclaim unused space. The return value is a list of warnings.
        warnings = self.cache.check()
        return warnings

    def clear(self):
        ## Clear operation fails silently
        rows_count = self.cache.clear(retry=False)
        return rows_count

    def add_to_index(self, conversation: Conversation):
        index_value = {}

        if conversation["auth_identifier"] in self.index:
            index_value = self.index[conversation["auth_identifier"]]

        index_value[conversation["id"]] = {
            "name": conversation["name"],
            "timestamp": conversation["timestamp"],
        }

        self.index.update([(conversation["auth_identifier"], index_value)])

    @staticmethod
    def compute_signature(auth_identifier: str, conversation_id: str) -> str:
        signature_str = f"{auth_identifier}-{conversation_id}"
        return hashlib.md5(signature_str.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_tag(auth_identifier: str):
        return hashlib.md5(auth_identifier.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_conv_id():
        return str(uuid.uuid4())

    @staticmethod
    def start_conversation(auth_identifier: str) -> Conversation:
        conversation = Conversation(
            auth_identifier=auth_identifier,
            id=HistoryCacheHandler.generate_conv_id(),
            timestamp=time.time(),
            name=HistoryCacheHandler.CONVERSATION_DEFAULT_NAME,
            data=[],
        )
        return conversation

    @staticmethod
    def start_conversation_from_records(
        auth_identifier: str, records: Union[List[QuestionData], QuestionData]
    ) -> Conversation:
        conversation = HistoryCacheHandler.start_conversation(auth_identifier)
        if isinstance(records, list):
            conversation["data"].extend(records)
        else:
            conversation["data"].append(records)
        return conversation
