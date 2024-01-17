import os
from backend.utils.dataiku_api import dataiku_api
from model_assist.logging import logger
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from model_assist.logging import logger


class LLM_API_Setup:

    def __init__(self, dataiku_api):
        self.dataiku_api = dataiku_api
        self.llm = self.dataiku_api.webapp_config.get("llm_id")

    def get_llm(self):
        return None


llm_setup = LLM_API_Setup(dataiku_api)
