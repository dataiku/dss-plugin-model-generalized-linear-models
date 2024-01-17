import dataiku
from model_assist.logging import logger
from model_assist.data_management.embeddings_handler import EmbeddingGenerator
from model_assist.dku_handler import DataikuHandler
from model_assist.llm_api_handler import llm_setup

import os

    
class EmbeddingCoordinator:
    def __init__(self, embedding_generator, dataiku_handler):
        self.embedding_generator = embedding_generator
        self.dataiku_handler = dataiku_handler
    
    def process(self, folder_containing_embeddings):
        dku_folder_info = self.dataiku_handler.read_from_folder(folder_containing_embeddings)
        faiss_embeddings =  self.embedding_generator.reload_embeddings_from_dku_folder(dku_folder_info)
        # Add more processing as needed
        return faiss_embeddings


embedding_handler = EmbeddingGenerator()
embedding_handler.set_embeddings_model(config_type="webapp")
dku_handler = DataikuHandler()
coordinator = EmbeddingCoordinator(embedding_handler, dku_handler)
