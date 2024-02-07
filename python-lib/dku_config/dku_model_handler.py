import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
import logging 
logger = logging.getLogger(__name__)


class ModelHandler:
    """
    A class to manage interactions with a Dataiku model, including feature computation,
    base value calculation, and relativity computation based on model data.
    """

    def __init__(self, model_id):
        """
        Initializes the ModelHandler with a specific model ID, setting up the model,
        predictor, and handlers for accessing model information and performing initial computations.

        Args:
            model_id (str): The ID of the model to manage.
        """
        self.model_id = model_id
        self.model = dataiku.Model(model_id)
        self.predictor = self.model.get_predictor()
        self.full_model_id = self._extract_active_fullModelId(self.model.list_versions())
        self.model_info_handler = PredictionModelInformationHandler.from_full_model_id(self.full_model_id)

        # Perform initial computations
        self._compute_features()
        self._compute_base_values()
        self._compute_relativities()

    def _compute_features(self):
        """Computes and categorizes features based on their roles and types."""
        self.features = self.model_info_handler.get_per_feature()
        modeling_params = self.model_info_handler.get_modeling_params()
        self.offset_columns = modeling_params['plugin_python_grid']['params']['offset_columns']
        self.exposure_columns = modeling_params['plugin_python_grid']['params']['exposure_columns']

        if len(self.offset_columns) > 1:
            raise ValueError("Only one offset column is allowed. Multiple offset columns provided.")

        if len(self.exposure_columns) > 1:
            raise ValueError("Only one exposure column is allowed. Multiple exposure columns provided.")


        important_columns = self.offset_columns + self.exposure_columns
        non_excluded_features = [feature for feature in self.features if feature not in important_columns]
        
        self.used_features = [feature for feature in non_excluded_features if self.features[feature]['role'] == 'INPUT']
        self.candidate_features = [feature for feature in non_excluded_features if self.features[feature]['role'] == 'REJECT']

    def _compute_base_values(self):
        """Calculates base values for each used feature, considering their type."""
        self.base_values = {}
        collector_data = self.model_info_handler.get_collector_data()['per_feature']
        for feature in self.used_features:
            feature_data = collector_data[feature]
            if self.features[feature]['type'] == 'CATEGORY':
                # Use .get to avoid KeyError if 'dropped_modality' key is missing
                self.base_values[feature] = feature_data.get('dropped_modality')
                if self.base_values[feature] is None:
                    # Handle the case where 'dropped_modality' is not available
                    raise ValueError(f"Warning: 'dropped_modality' not found for feature {feature}. Please ensure drop one dummy is enabled and clipping uses max nb categories")
            elif self.features[feature]['type'] == 'NUMERIC':
                self.base_values[feature] = feature_data['stats']['average']
            else:
                raise ValueError(f"Unsupported feature type:{self.features[feature]['type']}")

    def _compute_relativities(self):
        """Computes relativities for each feature based on their base values."""
        sample_train_row = self.model_info_handler.get_train_df()[0].head(1).copy()
        self.relativities = {}
        for feature in self.base_values.keys():
            sample_train_row[feature] = self.base_values[feature]

        try:
            baseline_prediction = self.predictor.predict(sample_train_row).iloc[0][0]
            # Rest of the method...
        except ValueError as e:
            # Log the error and more details for debugging
            logger.info(f"Error during baseline prediction: {e}")
            logger.info(f"Input shape: {sample_train_row.shape}, Expected shape: {len(self.model_info_handler.get_collector_data().get('feature_order'))}")
            raise
        
        for feature in self.base_values:
            relativity = self._calculate_feature_relativity(feature, sample_train_row, baseline_prediction)
            self.relativities[feature] = relativity
        
        self._prepare_relativities_df()
        

    def _calculate_feature_relativity(self, feature, sample_row, baseline_prediction):
        """Calculates relativity for a single feature."""
        relativity = {self.base_values[feature]: 1.0}
        collector_data = self.model_info_handler.get_collector_data()['per_feature'][feature]

        if self.features[feature]['type'] == 'CATEGORY':
            for modality in collector_data['category_possible_values']:
                sample_row[feature] = modality
                prediction = self.predictor.predict(sample_row).iloc[0][0]
                relativity[modality] = prediction / baseline_prediction
        else:
            min_value, max_value = collector_data['stats']['min'], collector_data['stats']['max']
            for value in np.linspace(min_value, max_value, 10):
                sample_row[feature] = value
                prediction = self.predictor.predict(sample_row).iloc[0][0]
                relativity[value] = prediction / baseline_prediction
        return relativity

    def _prepare_relativities_df(self):
        """Prepares a DataFrame from computed relativities for analysis."""
        coefficients_dict = self.get_coefficients()
        modified_coefficients_dict = {key.split(':', 1)[-1] if ':' in key else key: value for key, value in coefficients_dict.items()}
        logger.info(f"modified_coefficients_dict are {modified_coefficients_dict}")
        self.relativities_df = pd.DataFrame(columns=['feature', 'value', 'relativity', 'coefficent'])
        
        for feature, values in self.relativities.items():
            for value, relativity in values.items():
                coefficient = coefficients_dict.get(f"{feature}:{value}", None)
                logger.info(f"Appending Coefficent {coefficient")
                
                self.relativities_df = self.relativities_df.append({
                    'feature': feature,
                    'value': value, 
                    'relativity': relativity,
                    'coefficent':coefficient
                    }, ignore_index=True)

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
    
    def _extract_active_fullModelId(self, json_data):
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
    
    def get_relativities_df(self):
        """
        Returns the DataFrame containing relativities for each feature and their values.

        Returns:
            pd.DataFrame: A DataFrame with columns ['feature', 'value', 'relativity']
                        showing the relativity of each feature value against the baseline.
        """
        # Check if the relativities DataFrame has already been prepared
        if not hasattr(self, 'relativities_df'):
            self._prepare_relativities_df()

        return self.relativities_df
