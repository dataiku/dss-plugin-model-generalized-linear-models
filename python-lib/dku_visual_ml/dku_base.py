import dataiku
from logging_assist.logging import logger

class DataikuClientProject:
    """
    A base class to initialize Dataiku client and project
    """
    
    def __init__(self):
        self.client = dataiku.api_client()
        self.project = self.client.get_default_project()
        logger.info(f"Dataiku client and project initialized for project {self.project.project_key}")
