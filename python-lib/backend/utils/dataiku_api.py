import logging
from typing import Any, Dict
import dataiku
from dataiku.customwebapp import get_webapp_config
import pandas as pd
from dataiku.customrecipe import get_recipe_config
from model_assist.logging import logger
from backend.cache.history import HistoryCacheHandler
import os
import pwd
from typing import Optional
from enum import Enum


class CacheType(str, Enum):
    USER_HOME = "USER_HOME"
    PROJECT_LIB = "PROJECT_LIB"


class DataikuApi:
    def __init__(self, cache_type: CacheType = CacheType.USER_HOME):
        self._cache_type = cache_type
        self._webapp_config = None
        self._default_project = None
        self._default_project_key = None
        self._client = dataiku.api_client()
        self._cache: Optional[HistoryCacheHandler] = None

    def setup(self, webapp_config: Dict, default_project_key: str):
        self._webapp_config = webapp_config
        self._default_project_key = default_project_key

    def cache(self):
        if self._cache:
            return self._cache
        else:
            self._cache = HistoryCacheHandler(directory=self.cache_dir)
        return self._cache

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
        except Exception as err:
            if self._default_project_key:
                return self.client.get_project(self._default_project_key)
            else:
                raise Exception("Please define the default project before using it.")

    @property
    def default_project_key(self):
        try:
            return dataiku.get_custom_variables()["projectKey"]
        except Exception as err:
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

    def get_root_lib_path(self):
        paths = os.environ.get("PYTHONPATH")
        if paths:
            target_directory = "project-python-libs"
            paths_splitted = paths.split(":")
            logger.info("DEBUG SPLITTED PATHS")
            logger.info(os.environ)
            logger.info(paths_splitted)
            for path in paths_splitted:
                if target_directory in path:
                    return os.path.join(
                        path.split(target_directory)[0],
                        target_directory,
                        self.default_project_key,
                    )
        return None

    @property
    def cache_dir(self):
        default_cache_dir = os.path.join(
            pwd.getpwuid(os.getuid()).pw_dir,
            "caches",
            "plugins",
            "document-question-answering",
        )
        if self._cache_type == CacheType.USER_HOME:
            return default_cache_dir
        elif self._cache_type == CacheType.PROJECT_LIB:
            path = self.get_root_lib_path()
            logger.info(f"ROOT LIB PATH IS {path}")
            if path:
                return os.path.join(
                    path, ".caches", "plugins", "document-question-answering"
                )
            return default_cache_dir
        else:
            return default_cache_dir

    @property
    def recipe_config(self):
        try:
            self._recipe_config = get_recipe_config()
            return self._recipe_config
        except:
            return self._recipe_config

    def __str__(self):
        return (
            f"_webapp_config: {self._webapp_config}, "
            f"_default_project: {self._default_project}, "
            f"_default_project_key: {self._default_project_key}, "
            f"_client: {self._client}"
        )


dataiku_api = DataikuApi(cache_type=CacheType.PROJECT_LIB)
