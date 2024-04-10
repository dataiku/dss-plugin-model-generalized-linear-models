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
