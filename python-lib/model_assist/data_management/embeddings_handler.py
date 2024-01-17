import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from typing import Any, List, Union, Dict
from model_assist.logging import logger
import tempfile
import os
from backend.utils.dataiku_api import dataiku_api

class EmbeddingGenerator:
    def __init__(self):
        self.dataiku_api = dataiku_api 
        self.auth_info = self.dataiku_api.client.get_auth_info(with_secrets=True)
        self.embeddings_model = None

    def set_embeddings_model(self,config_type="recipe"):
        
        if config_type=="recipe":
            self.preset_config = dataiku_api.recipe_config
        else:
            self.preset_config = dataiku_api.webapp_config

        self.embedding_type = self.preset_config.get("embeddings_type")
        logger.info(f"Using {self.embedding_type} for embeddings")

        if self.embedding_type == "AzureOpenAI":
            logger.info(f'Using Azure end point {self.preset_config.get("azure_endpoint")}')
            self.embeddings_model = OpenAIEmbeddings(
                        openai_api_base=self.preset_config.get("embeddings_azure_endpoint"),
                        deployment = self.preset_config.get("embeddings_azure_api_deployment"),
                        model=self.preset_config.get("embeddings_azure_model"),
                        openai_api_key=self.get_api_key(),
                        openai_api_type="azure",
                        openai_api_version=self.preset_config.get("embeddings_azure_api_version"),
                        chunk_size=16
                        )
                                                
        elif self.embedding_type == "OpenAI":
            self.embeddings_model = OpenAIEmbeddings(
                    openai_api_key=self.get_api_key(),
                    model=self.preset_config.get("embeddings_openai_model"),
                    )
        else:
                raise ValueError("LLM provider not supported")


        return self.embeddings_model
    
    def generate_embeddings(self, docs: Union[List[Dict], List[str]]) -> Any:
        try:
            index = FAISS.from_documents(docs, self.embeddings_model)
            return index
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise e
            
    def reload_embeddings_from_dku_folder(self, dku_folder: dataiku.Folder):
        # Load in faiss model we created in the prior step
        with tempfile.TemporaryDirectory() as temp_dir:
            for f in dku_folder.list_paths_in_partition():
                with dku_folder.get_download_stream(f) as stream:
                    with open(os.path.join(temp_dir, os.path.basename(f)), "wb") as f2:
                        f2.write(stream.read())
            index = FAISS.load_local(temp_dir, self.embeddings_model)
        return index
    
    def get_api_key(self):
        secrets_list = self.auth_info.get("secrets", [])

        api_key = None
        
        # Depending on the llm_type, search for the appropriate key in the secrets list
        target_key = "AZURE_OPENAI_EMBEDDINGS_KEY" if self.embedding_type == "AzureOpenAI" else "OPENAI_EMBEDDINGS_KEY" if self.embedding_type == "OpenAI" else None

        if target_key:
            for secret in secrets_list:
                if secret["key"] == target_key:
                    api_key = secret["value"]
                    break

        if not api_key:
            raise ValueError(f"API Key {target_key} is missing from secrets in dataiku administration.")

        return api_key
    