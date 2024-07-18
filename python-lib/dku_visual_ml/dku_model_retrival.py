import dataiku
import dataikuapi
from logging_assist.logging import logger
import re

class VisualMLModelRetriver():
    """
    An class to retrieve the modelling parameter from a DKU visual ML model
    and format them for the front end
    """

    def __init__(self, full_model_id):
        logger.info(f"Initalising a model retriever for model ID {full_model_id}")
        self.full_model_id = full_model_id
        self.client = dataiku.api_client()
        self.project = self.client.get_default_project()
        self.task = dataikuapi.dss.ml.DSSMLTask.from_full_model_id(
            self.client, 
            full_model_id, 
            self.project.project_key
        )
        self.model_details = self.task.get_trained_model_details(full_model_id) 
        self.algo_settings = self.model_details.get_modeling_settings().get('plugin_python_grid')
        logger.info(f"Model retriever intialised for model ID {full_model_id}")
              
   
    def get_features_dict_and_target(self):
        logger.info("Model getting features")
        preprocessing = self.model_details.get_preprocessing_settings().get('per_feature')
        features = preprocessing.keys()
        exposure_column = self.get_exposure_column()
        
        features_dict = {}
        for feature in features:
            feature_settings = preprocessing.get(feature)
            choose_base_level = feature_settings.get('category_handling') and not ("series.mode()[0]" in feature_settings.get('customHandlingCode'))
            base_level = None
            if choose_base_level:
                pattern = r'self\.mode_column\s*=\s*["\']([^"\']+)["\']'
                # Search for the pattern in the code string
                match = re.search(pattern, feature_settings.get('customHandlingCode'))
                # Extract and print the matched value
                if match:
                    base_level = match.group(1)
                    
            features_dict[feature] = {
                "role": feature_settings.get('role'),
                 'type': feature_settings.get('type'),
                "handling" : feature_settings.get('numerical_handling') or feature_settings.get('category_handling'),
                "chooseBaseLevel": choose_base_level,
                "baseLevel": base_level

            }
            if feature == exposure_column:
                features_dict[feature]["role"]=="Exposure"
            if features_dict[feature]["role"]=="TARGET":
                features_dict[feature]["role"]=="Target"
                target_column = feature
                
        logger.info("Model retriever succesfully got features")    
        logger.debug(f"Features are:{features_dict}")
        return features_dict, target_column
    
    def get_exposure_column(self):
        exposure_column = self.algo_settings.get('params').get('exposure_columns')[0]
        return exposure_column
    
    def get_elastic_net_penalty(self):
        return self.algo_settings.get('params').get('penalty')[0]
    
    def get_l1_ratio(self):
        return self.algo_settings.get('params').get('l1_ratio')[0]
    
    def get_distribution_function(self):
        distribution_function = self.algo_settings.get('params').get('family_name')
        return distribution_function.title()
    
    def get_link_function(self):
        distribution_function = self.get_distribution_function()
        link_function = self.algo_settings.get('params').get(distribution_function.lower()+"_link")
        return link_function.title()
    
        
    def get_setup_params(self):   
        
        logger.debug(f"Retrieving setup parameters for model id {self.full_model_id}")
        logger.debug("Model Parameters")
        features_dict, target_column = self.get_features_dict_and_target()
        setup_params = {
            "target_column": target_column,
            "exposure_column":self.get_exposure_column(),
            "distribution_function": self.get_distribution_function(),
            "link_function":self.get_link_function(),
            "elastic_net_penalty": self.get_elastic_net_penalty(),
            "l1_ratio": self.get_l1_ratio(),
            "params": features_dict
        }
        logger.info(f"Retrieved setup parameters for model id {self.full_model_id}")
        logger.debug(f"Setup params are {setup_params}")
        return setup_params
    
        
    
