from abc import ABC, abstractmethod
import pandas as pd
# TODO CHANGE TO RecursiveCharacterTextSplitter AS IT IS THE RECOMMENDED ONE
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader, TextLoader
from langchain.document_loaders.csv_loader import CSVLoader

from typing import List
class ProcessingError(Exception):
    """Base class for exceptions in this module."""
    pass

class LoadError(ProcessingError):
    """Exception raised for errors in the loading process."""
    def __init__(self, file_path: str, file_type: str, reason: str):
        self.file_path = file_path
        self.file_type = file_type
        self.reason = reason
        super().__init__(f"Failed to load {self.file_type} file at path '{self.file_path}'. Reason: {self.reason}")

class SplitError(ProcessingError):
    """Exception raised for errors in the splitting process."""
    def __init__(self, file_path: str, file_type: str, reason: str):
        self.file_path = file_path
        self.file_type = file_type
        self.reason = reason
        super().__init__(f"Failed to split {self.file_type} file content at path '{self.file_path}'. Reason: {self.reason}")


class BaseProcessor(ABC):

    def __init__(self, chunk_size=100, chunk_overlap=0):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap,length_function=len)

    @abstractmethod
    def process_document(self, file_path: str) -> List:
        pass

    def split_documents(self, docs: str, file_path: str) -> List:
        try:
            return self.text_splitter.split_documents(docs)
        except Exception as e:
            raise SplitError(file_path,'text', str(e))
        
    def split_simple_text(self, text_data: str, file_path: str) -> List:
        docs = self.text_splitter.create_documents([text_data])
        return self.split_documents(docs, file_path)




class PDFProcessor(BaseProcessor):

    def process_document(self, file_path: str) -> List:
        try:
            loader = PyPDFLoader(file_path)
            document = loader.load()
            return self.split_documents(document, file_path)
        except Exception as e:
            raise LoadError(file_path, '.pdf', str(e))


class CSVProcessor(BaseProcessor):

    def process_document(self, file_path: str) -> List:
        try:
            loader = CSVLoader(file_path)
            document = loader.load()
            return self.split_documents(document, file_path)
        except Exception as e:
            raise LoadError(file_path, '.csv', str(e))

class PPTProcessor(BaseProcessor):
    def process_document(self, file_path: str) -> List:
        try:
            loader = UnstructuredPowerPointLoader(file_path)
            document = loader.load()
            return self.split_documents(document, file_path)
        except Exception as e:
            raise LoadError(file_path, '.pptx', str(e))

class XLSXProcessor(BaseProcessor):
    def process_document(self, file_path: str) -> List:
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            document = df.to_string()
            return self.split_simple_text(document, file_path)
        except Exception as e:
            raise LoadError(file_path, '.xlsx', str(e))

class TXTProcessor(BaseProcessor):

    def process_document(self, file_path: str) -> List:
        try:
            loader = TextLoader(file_path)
            document = loader.load()
            return self.split_documents(document, file_path)
        except Exception as e:
            raise LoadError(file_path, '.txt', str(e))


processor_classes = {
    '.pdf': PDFProcessor,
    '.csv': CSVProcessor,
    '.pptx': PPTProcessor,
    '.xlsx': XLSXProcessor,
    '.txt': TXTProcessor
}