import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import tempfile
import os
from model_assist.logging import logger
from typing import Any, List

class DataikuHandler:
    def __init__(self):
        pass
    
    def read_df(self, dataset_name: str) -> pd.DataFrame:
        try:
            dku_dataset_obj = dataiku.Dataset(dataset_name)
            df = dku_dataset_obj.get_dataframe()
            return df
        except Exception as e:
            logger.error(f"Failed to read dataframe: {e}")
            raise e
        
    def save_to_folder(self, save_object:Any, output_folder: str) -> None:
        try:
            output_folder = dataiku.Folder(output_folder)
            with tempfile.TemporaryDirectory() as temp_dir:
                save_object.save_local(temp_dir)
                for f in os.listdir(temp_dir):
                    output_folder.upload_file(f, os.path.join(temp_dir, f))
        except Exception as e:
            logger.error(f"Failed to save to folder: {e}")
            raise e
    
    def read_from_folder(self, folder_name:str) -> dataiku.Folder:
        dku_folder = dataiku.Folder(folder_name)
        return dku_folder
    
    def process_documents_from_folder(self, folder_name: str, processors: dict) -> List:
        dku_folder = self.read_from_folder(folder_name)
        paths = dku_folder.list_paths_in_partition()
        all_processed_docs = []

        for path in paths:
            extension = os.path.splitext(path)[1].lower()
            processor = processors.get(extension)

            # Skip the file if no processor is found for the given extension
            if not processor:
                logger.warning(f"No processor found for file type: {extension}. Skipping file: {path}")
                continue

            with dku_folder.get_download_stream(path) as f:
                data = f.read()

                # Create a temporary file with the correct extension
                temp_file_path = '/tmp' + path
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension, prefix=temp_file_path) as tmp:
                    tmp.write(data)
                    processed_docs = processor.process_document(tmp.name)
                    for doc_number, _ in enumerate(processed_docs):
                        processed_docs[doc_number].metadata['source'] = path

                    all_processed_docs.extend(processed_docs)
                    
                    os.remove(tmp.name)
    
        return all_processed_docs
