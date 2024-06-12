from typing import Any, Dict

import dataiku
from dataiku.customwebapp import get_webapp_config
from glm_handler.dku_model_deployer import ModelDeployer
from glm_handler.dku_model_handler import ModelHandler
from glm_handler.dku_model_trainer import DataikuMLTask
from glm_handler.glm_data_handler import GlmDataHandler

from backend.model_cache import setup_model_cache


class DataikuApi:
    def __init__(self):
        self._webapp_config = None
        self._default_project = None
        self._default_project_key = None

        self._client = dataiku.api_client()

        self._global_dss_mltask = None
        self._global_dku_mltask = None

        self._model_deployer = None
        self._model_handler = None
        self._model_cache = None

    def setup(self, webapp_config: Dict, default_project_key: str):
        self._webapp_config = webapp_config
        self._default_project_key = default_project_key

    @property
    def client(self):
        if self._client is None:
            raise Exception("Please set the client before using it.")
        else:
            return self._client

    @property
    def default_project(self):
        try:
            return self.client.get_default_project()
        except:
            if self._default_project_key:
                return self.client.get_project(self._default_project_key)
            else:
                raise Exception("Please define the default project before using it.")

    @property
    def default_project_key(self):
        try:
            return dataiku.get_custom_variables()["projectKey"]
        except:
            if self._default_project_key:
                return self._default_project_key
            else:
                raise Exception("Please define the default project before using it.")

    @client.setter
    def client(self, c: Any):
        raise Exception(
            "If working outside of Dataiku, Client can only be set through the function setup()"
        )

    @property
    def webapp_config(self):
        try:
            self._webapp_config = get_webapp_config()
            return self._webapp_config
        except:
            return self._webapp_config
    
    @property
    def global_dss_mltask(self):
        if self._global_dss_mltask is None:
            try:
                saved_model_id = self.webapp_config.get("saved_model_id")
                saved_model = self.default_project.get_saved_model(saved_model_id)
                self._global_dss_mltask = saved_model.get_origin_ml_task()
                return self._global_dss_mltask
            except:
                raise Exception("Please define the default project before using it.")
        else:
            return self._global_dss_mltask
    
    @property
    def global_dku_mltask(self):
        if self._global_dku_mltask is None:
            try:
                saved_model_id = self.webapp_config.get("saved_model_id")
                training_dataset_string = self.webapp_config.get("training_dataset_string")
                self._global_dku_mltask = DataikuMLTask(training_dataset_string, saved_model_id)
                return self._global_dku_mltask
            except:
                raise Exception("Please define the default project before using it.")
        else:
            return self._global_dku_mltask
    
    
    @property
    def model_deployer(self):
        if self._model_deployer is None:
            try:
                saved_model_id = self.webapp_config.get("saved_model_id")
                saved_model = self.default_project.get_saved_model(saved_model_id)
                self._model_deployer =  ModelDeployer(saved_model, self.global_dss_mltask, saved_model_id)
                return self._model_deployer
            except:
                raise Exception("Please define the default project before using it.")
        else:
            return self._model_deployer
    
    @property
    def model_handler(self):
        if self._model_handler is None:
            try:
                saved_model_id = self.webapp_config.get("saved_model_id")
                data_handler = GlmDataHandler()
                self._model_handler =  ModelHandler(saved_model_id, data_handler)
                return self._model_handler
            except:
                raise Exception("Please define the default project before using it.")
        else:
            return self._model_handler
    
    @property
    def model_cache(self):
        if self._model_cache is None:
            try:
                self._model_cache =  setup_model_cache(self.global_dss_mltask, self.model_deployer, self.model_handler)
                return self._model_cache
            except:
                raise Exception("Please define the default project before using it.")
        else:
            return self._model_cache

    
    @model_cache.setter
    def model_cache(self, value):
        self._model_cache = value


dataiku_api = DataikuApi()
