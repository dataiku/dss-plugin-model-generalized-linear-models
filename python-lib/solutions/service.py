from backend.utils.dataiku_api import dataiku_api
from model_assist.logging import logger

class GLMHandler:
    """LLM_Question_Answering: A class to facilitate the question-answering process using LLM model"""

    def __init__(self):
        self.project = dataiku_api.default_project

glm = GLMHandler()
