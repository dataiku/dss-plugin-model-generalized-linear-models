import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
from glm_handler.dku_utils import extract_active_fullModelId
import logging
from backend.logging_settings import logger

class RelativitiesHandler:
    """
    A class to manage relativities calculations for a Dataiku model.
    
    Attributes:
        model_info_handler (PredictionModelInformationHandler): Handler for model information.
        predictor (dataiku.Model.Predictor): The predictor object from the Dataiku model.
        exposure (str): The name of the exposure column, if any.
        features (dict): Feature information retrieved from the model.
        base_values (dict): Base values for features used in relativities calculations.
        modalities (dict): Modalities for categorical features.
    """
    
    def __init__(self, model_info_handler):
        self.model_info_handler = model_info_handler
        self.predictor = model_info_handler.get_predictor()
        self.exposure = None
        self.features = self.model_info_handler.get_per_feature()
        self.base_values = {}
        self.modalities = {}
        self.initialize_feature_variables()

    def initialize_feature_variables(self):
        """ Initializes basic variables related to features. """
        modeling_params = self.model_info_handler.get_modeling_params()
        self.exposure_columns = modeling_params['plugin_python_grid']['params']['exposure_columns']
        if self.exposure_columns:
            self.exposure = self.exposure_columns[0]  # Assumes there is only one exposure column

    def compute_base_values(self):
        """ Computes base values for features based on training data. """
        train_set = self.model_info_handler.get_train_df()[0].copy()
        for feature in self.features:
            if self.features[feature]['type'] == 'NUMERIC' and self.features[feature]['rescaling'] == 'NONE':
                self.compute_base_for_numeric_feature(feature, train_set)

    def compute_base_for_numeric_feature(self, feature, train_set):
        """ Computes base values for numeric features without rescaling. """
        if self.exposure is not None:
            self.base_values[feature] = (train_set[feature] * train_set[self.exposure]).sum() / train_set[self.exposure].sum()
        else:
            self.base_values[feature] = train_set[feature].mean()
        self.modalities[feature] = {'min': train_set[feature].min(), 'max': train_set[feature].max()}

    def calculate_relativities(self):
        """ Calculates relativities based on base values and modalities. """
        sample_train_row = self.initialize_baseline()
        baseline_prediction = self.calculate_baseline_prediction(sample_train_row)
        return self.calculate_relative_predictions(sample_train_row, baseline_prediction)

    def initialize_baseline(self):
        """ Initializes a baseline row for prediction comparisons. """
        train_row = self.model_info_handler.get_train_df()[0].head(1).copy()
        for feature in self.base_values.keys():
            train_row[feature] = self.base_values[feature]
        if self.exposure is not None:
            train_row[self.exposure] = 1
        return train_row

    def calculate_baseline_prediction(self, sample_train_row):
        """ Calculates the baseline prediction for the initialized baseline row. """
        return self.predictor.predict(sample_train_row).iloc[0][0]

    def calculate_relative_predictions(self, sample_train_row, baseline_prediction):
        """ Calculates relative predictions for each feature based on the baseline prediction. """
        relativities = {'base': {'base': baseline_prediction}}
        for feature in self.base_values.keys():
            relativities[feature] = {self.base_values[feature]: 1.0}
            if self.features[feature]['type'] == 'CATEGORY':
                for modality in self.modalities[feature]:
                    train_row_copy = sample_train_row.copy()
                    train_row_copy[feature] = modality
                    prediction = self.predictor.predict(train_row_copy).iloc[0][0]
                    relativities[feature][modality] = prediction / baseline_prediction
            else:
                train_row_copy = sample_train_row.copy()
                min_value, max_value = self.modalities[feature]['min'], self.modalities[feature]['max']
                for value in np.linspace(min_value, max_value, 10):
                    train_row_copy[feature] = value
                    prediction = self.predictor.predict(train_row_copy).iloc[0][0]
                    relativities[feature][value] = prediction / baseline_prediction
        return relativities


