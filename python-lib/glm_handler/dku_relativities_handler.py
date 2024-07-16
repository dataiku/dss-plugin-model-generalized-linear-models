import dataiku

from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler

import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
from glm_handler.dku_utils import extract_active_fullModelId
import logging
from backend.logging_assist import logger

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
            
    def compute_column_roles(self):
        """ Computes special columns like exposure and offset columns from modeling params. """
        modeling_params = self.model_info_handler.get_modeling_params()
        self.offset_columns = modeling_params['plugin_python_grid']['params']['offset_columns']
        self.exposure_columns = modeling_params['plugin_python_grid']['params']['exposure_columns']
        if len(self.exposure_columns) > 0:
            self.exposure = self.exposure_columns[0]  # assumes there is only one exposure column