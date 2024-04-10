import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
from dku_utils import extract_active_fullModelId


class ModelInformationManager:
    def __init__(self, model_id, full_model_id):
        self.model_id = model_id
        self.full_model_id = full_model_id
        self.model = dataiku.Model(model_id)  # Direct interaction with the Dataiku model.
        self.model_info_handler = PredictionModelInformationHandler.from_full_model_id(self.full_model_id)
        self.predictor = self.model_info_handler.get_predictor()
        self.target = self.model_info_handler.get_target_variable()

    def get_model_versions(self):
        versions = self.model.list_versions()
        return {version['snippet']['fullModelId']: version['snippet']['userMeta']['name'] for version in versions}

    def get_coefficients(self):
        coefficients = self.predictor._model.clf.coef_
        variable_names = self.predictor._model.clf.column_labels
        return dict(zip(variable_names, coefficients))
    
    def get_link_function(self):
        return self.predictor._model.clf.get_link_function()
    
    def compute_features(self):
        self.exposure = None
        self.features = self.model_info_handler.get_per_feature()
        modeling_params = self.model_info_handler.get_modeling_params()
        self.offset_columns = modeling_params['plugin_python_grid']['params']['offset_columns']
        self.exposure_columns = modeling_params['plugin_python_grid']['params']['exposure_columns']
        if len(self.exposure_columns) > 0:
            self.exposure = self.exposure_columns[0] # assumes there is only one
        important_columns = self.offset_columns + self.exposure_columns + [self.target]
        self.non_excluded_features = [feature for feature in self.features.keys() if feature not in important_columns]
        self.used_features = [feature for feature in self.non_excluded_features if self.features[feature]['role']=='INPUT']
        self.candidate_features = [feature for feature in self.non_excluded_features if self.features[feature]['role']=='REJECT']
        
    def get_features(self):
        return [{'variable': feature, 
          'isInModel': self.features[feature]['role']=='INPUT', 
          'variableType': 'categorical' if self.features[feature]['type'] == 'CATEGORY' else 'numeric'} for feature in self.non_excluded_features]
