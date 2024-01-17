from langchain.schema.retriever import BaseRetriever, Document
from typing import List
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.vectorstores.base import VectorStoreRetriever
from pydantic import Field
from backend.utils.dataiku_api import dataiku_api
from model_assist.data_management.embeddings_coordinator import embedding_handler
from model_assist.logging import logger

class SimilarityRetriever(VectorStoreRetriever):


    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve documents relevant to the given query.

        :param query: The search string.
        :return: A list of relevant documents.
        """
        logger.info("Using Similarity Retriever")
        k = int(dataiku_api.webapp_config.get("max_source_article_number"))
        # Fetch top 3 similar documents with their scores.
        logger.info(f'The query used in retrival is {query}')
        docs_and_scores = self.vectorstore.similarity_search_with_score(query=query, k=k)
        threshold = float(dataiku_api.webapp_config.get("similarity_threshold"))

        # Filter out documents that don't meet the similarity threshold.
        filtered_documents = [(doc, score) for doc, score in docs_and_scores if score <= threshold]

        # Update the metadata of each document with its similarity score.
        for doc, score in filtered_documents:
            doc.metadata.update({"score": str(round(score, 2))})

        # Return the list of filtered documents (excluding scores ).
        logger.info(f"Retrived {len(filtered_documents)}")

        return [doc for doc, _ in filtered_documents]

class MMRRetriever(VectorStoreRetriever):


    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve documents relevant to the given query.

        :param query: The search string.
        :return: A list of relevant documents.
        """
        logger.info("Using MMR Retriever")
        k = int(dataiku_api.webapp_config.get("max_source_article_number"))
        # Fetch top 3 similar documents with their scores.
        threshold = float(dataiku_api.webapp_config.get("similarity_threshold"))
        embedded_query = embedding_handler.embeddings_model.embed_query(query)
        docs = self.vectorstore.max_marginal_relevance_search_with_score_by_vector(
                    embedding=embedded_query,
                    k=k,
                    fetch_k=15,
                    lambda_mult=threshold,
                )
        

        # Update the metadata of each document with its similarity score.
        for doc, score in docs:
            doc.metadata.update({"score": str(round(score, 2))})

        # Return the list of filtered documents (excluding scores ).
        return [doc for doc, _ in docs]