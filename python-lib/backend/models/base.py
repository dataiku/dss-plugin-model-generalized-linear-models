from typing import TypedDict, Dict, Union, List, Optional
from enum import Enum

# TODO: probably feedback needs to be handeled differently, not stored in cache


class Source(TypedDict):
    excerpt: str
    metadata: Dict[str, Union[str, int, float]]


class FeedbackValue(str, Enum):
    NEGATIVE = "NEGATIVE"
    POSITIVE = "POSITIVE"


class Feedback(TypedDict):
    value: FeedbackValue
    choice: Optional[List[str]]
    message: Optional[str]


class QuestionData(TypedDict):
    id: str
    query: str
    filters: Optional[Dict[str, List[Union[str, float, int]]]]
    answer: str
    sources: List[Source]
    feedback: Optional[Feedback]
    timestamp: float


class Conversation(TypedDict):
    id: str
    name: str
    timestamp: float
    auth_identifier: str
    data: List[QuestionData]


class ConversationInfo(TypedDict):
    id: str
    name: str
    timestamp: float


class LlmHistory(TypedDict):
    input: str
    output: str
