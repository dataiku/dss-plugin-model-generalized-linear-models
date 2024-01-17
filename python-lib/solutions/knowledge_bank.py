from backend.utils.dataiku_api import dataiku_api
from typing import TypedDict

class KnowledgeParams(TypedDict):
    k: int
    use_mmr: bool
    mmr_k: int
    mmr_diversity: float


def extract_knowldge_params():
    prefix = "knowledge_retrieval_"
    config = dataiku_api.webapp_config
    keys = KnowledgeParams.__annotations__.keys()
    result = {}
    for key in keys:
        if isinstance(key, str):
            key_value = config.get(prefix + key)
            result[key] = key_value
    return KnowledgeParams(**result)