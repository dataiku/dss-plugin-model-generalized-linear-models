from langchain.document_loaders import DataFrameLoader
import pandas as pd
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import DataFrameLoader
from model_assist.logging import logger
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from typing import Any, List
from model_assist.logging import logger

class DataFrameHandler:
    def __init__(self,
                 chunk_size: int =1000,
                 chunk_overlap:int =0
                ):
        self.text_splitter= RecursiveCharacterTextSplitter(
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap,
                            length_function=len
                        )
        
    def split_column_in_to_docs(self, 
                                df: pd.DataFrame,
                                page_content_column: str) -> pd.DataFrame:
        try:
            self.langchain_loader = DataFrameLoader(df, page_content_column=page_content_column)
            documents = self.langchain_loader.load()
            docs = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(docs)} documents")

            return docs
        except Exception as e:
            logger.error(f"Failed to split column into docs: {e}")
            raise e