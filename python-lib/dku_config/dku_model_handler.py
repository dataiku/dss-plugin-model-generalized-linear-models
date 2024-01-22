import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu

class ModelHandler:
    """
    A class to handle interactions with a Dataiku model.

    Attributes:
        model_id (str): The ID of the model.
        model (dataiku.Model): The Dataiku model object.
        predictor (Predictor): The predictor object of the model.
        full_model_id (str): The full model ID of the active model version.
        model_info_handler (PredictionModelInformationHandler): Handler for model information.
    """

    def __init__(self, model_id):
        """
        Initializes the ModelHandler with a specific model ID.

        Args:
            model_id (str): The ID of the model to handle.
        """
        self.model_id = model_id
        self.model = dataiku.Model(model_id)
        self.predictor = self.model.get_predictor()
        self.full_model_id = self.extract_active_fullModelId(self.model.list_versions())
        self.model_info_handler = PredictionModelInformationHandler.from_full_model_id(self.full_model_id)
        
    def get_coefficients(self):
        """
        Retrieves the coefficients of the model predictor.

        Returns:
            dict: A dictionary mapping variable names to their coefficients.
        """
        coefficients = self.predictor._model.clf.coef_
        variable_names = self.predictor._model.clf.column_labels
        return dict(zip(variable_names, coefficients))

    def get_link_function(self):
        """
        Retrieves the link function of the original model as a statsmodel object
        """
        return self.predictor._model.clf.get_link_function()
    
    def get_dataframe(self, dataset_type='test'):
        """
        Retrieves the specified dataset as a DataFrame.

        Args:
            dataset_type (str, optional): The type of dataset to retrieve ('test', 'train', or 'full'). Defaults to 'test'.

        Returns:
            pd.DataFrame: The requested dataset.

        Raises:
            ValueError: If an invalid dataset type is provided.
        """
        if dataset_type == 'test':
            return self.model_info_handler.get_test_df()[0]
        elif dataset_type == 'train':
            return self.model_info_handler.get_train_df()[0]
        elif dataset_type == 'full':
            return self.model_info_handler.get_full_df()[0]
        else:
            raise ValueError("Invalid dataset type")

    def preprocess_dataframe(self, df):
        """
        Preprocesses a DataFrame using the model's preprocessing steps.

        Args:
            df (pd.DataFrame): The DataFrame to preprocess.

        Returns:
            pd.DataFrame: The preprocessed DataFrame.
        """
        column_names = self.predictor.get_features()
        preprocessed_values = self.predictor.preprocess(df)[0]
        return pd.DataFrame(preprocessed_values, columns=column_names)
    
    def extract_active_fullModelId(self, json_data):
        """
        Extracts the fullModelId of the active model version from the given JSON data.

        Args:
            json_data (list): A list of dictionaries containing model version details.

        Returns:
            str: The fullModelId of the active model version, or None if not found.
        """
        for item in json_data:
            if item.get('active'):
                return item['snippet'].get('fullModelId')
        return None