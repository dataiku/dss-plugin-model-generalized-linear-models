import dataiku
import dataikuapi
from logging_assist.logging import logger
import re
from dku_visual_ml.dku_base import DataikuClientProject
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
# need to come up with a structure way of storing features as its being done twice

class VisualMLModelRetriver(DataikuClientProject):
    """
    An class to retrieve the modelling parameter from a DKU visual ML model
    based on a full model Id, and format them for the front end
    """

    def __init__(self, full_model_id):
        super().__init__()

        logger.info(f"Initalising a model retriever for model ID {full_model_id}")
        
        self.full_model_id = full_model_id
        self.task = dataikuapi.dss.ml.DSSMLTask.from_full_model_id(
            self.client, 
            full_model_id, 
            self.project.project_key
        )
        self.model_details = self.task.get_trained_model_details(full_model_id) 
        self.algo_settings = self.model_details.get_modeling_settings().get('plugin_python_grid')
        self.model_info_handler = PredictionModelInformationHandler.from_full_model_id(self.full_model_id)
        self.offset_columns = self.get_offset_columns()
        self.features = self.model_info_handler.get_per_feature()
        self.exposure_columns = self.get_exposure_columns()
        self.target_column = self.get_target_column() 
        self.predictor = self.get_predictor()
        self.get_used_features()
        logger.info(f"Model retriever intialised for model ID {full_model_id}")
              
    def get_offset_columns(self):
        return self.algo_settings['params']['offset_columns']
    

    def get_coefficients(self):
        """
        Retrieves the coefficients of the model predictor.

        Returns:
            dict: A dictionary mapping variable names to their coefficients.
        """
        logger.info("Retrieving model coefficients.")
        
        coefficients = self.get_predictor()
        variable_names = predictor._model.clf.column_labels
        logger.info(f"Model coefficients retrieved: {coefficients_dict}")
        return dict(zip(variable_names, coefficients))
    
    def get_features(self):
        logger.info(f"Getting features for model ID {self.full_model_id}")
        return self.features
    
    def get_feature_type(self, feature):
        logger.debug(f"Getting feature type for {feature}")
        feature_type = self.features.get(feature).get('type')
        logger.debug(f"Feature type is {feature_type}")
        return feature_type
    
    def get_rescaling_type(self, feature):
        logger.debug(f"Getting Rescaling type for {feature}")
        rescaling_type = self.features.get(feature).get('rescaling')
        logger.debug(f"Rescaling type is {rescaling_type}")
        return rescaling_type
    
    def get_full_model_id(self):
        return self.full_model_id
    
    def get_target_column(self):
        target_column = None
        logger.info("Getting the target column for model id {self.full_model_id}")
        preprocessing = self.model_details.get_preprocessing_settings().get('per_feature')
        features = preprocessing.keys()
        for feature in features:
            feature_settings = preprocessing.get(feature)
            if (feature_settings.get('role')=="TARGET") or (feature_settings.get('role')=="Target"):
                target_column = feature
                self.target_column = target_column
                logger.debug(f"Setting target columns to {self.target_column}")
                return feature
            
        if not target_column:
            logger.debug("Unable to find a target column")

    
    def _get_excluded_features(self):
        logger.debug(f"Excluding features exposure {self.exposure_columns}")
        logger.debug(f"Excluding features target {self.target_column}")
        important_columns = []
        important_columns += [self.offset_columns, self.exposure_columns, self.target_column]
        
        return important_columns
    
    def _get_included_features(self):
        logger.debug(f"Getting Included features")
        excluded_features = self._get_excluded_features()
        logger.debug(f"Searching in features")
        logger.debug(f"excluded_features: {excluded_features}")
        self.non_excluded_features = [feature for feature in self.features.keys() if feature not in excluded_features]
        logger.debug(f"Found Included features as {self.non_excluded_features }")
        
        return self.non_excluded_features
    
    def get_used_features(self):
        """
        Filters features based on their importance and role in the model.
        """

        self.non_excluded_features = self._get_included_features()
        self.used_features = [feature for feature in self.non_excluded_features if self.features[feature]['role'] == 'INPUT']
        self.candidate_features = [feature for feature in self.non_excluded_features if self.features[feature]['role'] == 'REJECT']
        logger.info(f"Features filtered: non_excluded_features={self.non_excluded_features}, used_features={self.used_features}, candidate_features={self.candidate_features}")
        return self.used_features
    

    def get_features_used_in_modelling(self):
        """
        Retrieves the features used in the model.

        Returns:
            list: A list of dictionaries with feature details.
        """
        logger.info("Retrieving model features.")
        self._get_included_features()
        features_list = [
            {'variable': feature, 
             'isInModel': self.features[feature]['role'] == 'INPUT', 
             'variableType': 'categorical' if self.features[feature]['type'] == 'CATEGORY' else 'numeric'} 
            for feature in self.non_excluded_features
        ]

        logger.info(f"Features retrieved: {features_list}")
        return features_list
    
    
    def get_rejected_features(self):
        logger.debug(f"Getting Rejected Features")
        self.candidate_features = [feature for feature in self.non_excluded_features if self.features[feature]['role'] == 'REJECT']
        logger.debug(f"Rejected Features are {self.candidate_features}")
        return self.candidate_features
    
        
    def get_features_and_type(self):
        
        logger.info(f"Getting Features for {self.full_model_id }")
        self._get_included_features()
        
        formatted_features = [
            {'variable': feature, 
              'isInModel': self.features[feature]['role']=='INPUT', 
              'variableType': 'categorical' if self.features[feature]['type'] == 'CATEGORY' else 'numeric'
            } for feature in self.non_excluded_features]
        return formatted_features
    
    def get_predictor(self):
        """
        Retrieves a model predictor.

        """
        logger.debug(f"Getting predictor for the model {self.full_model_id}")
        predictor = self.model_info_handler.get_predictor()
        logger.debug(f"Successfully retrieved predictor for the model {self.full_model_id}")
        return predictor
        
    def get_features_dict(self):
        
        logger.info("Model getting features")
        exposure_columns = self.get_exposure_columns()
        
        preprocessing = self.model_details.get_preprocessing_settings().get('per_feature')
        features = preprocessing.keys()
        
        
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
            if feature == exposure_columns:
                features_dict[feature]["role"]=="Exposure"
            if features_dict[feature]["role"]=="TARGET":
                features_dict[feature]["role"]=="Target"
                target_column = feature
                
        logger.info("Model retriever succesfully got features")    
        logger.debug(f"Features are:{features_dict}")
        return features_dict
    
    def get_exposure_columns(self):
        try:
            if self.exposure_columns:
                return self.exposure_columns
            else:
                self.exposure_columns = self.algo_settings.get('params').get('exposure_columns')[0]
                return self.exposure_columns
        except:
            self.exposure_columns = self.algo_settings.get('params').get('exposure_columns')[0]
            return self.exposure_columns

    def get_elastic_net_penalty(self):
        return self.algo_settings.get('params').get('penalty')[0]
    
    def get_l1_ratio(self):
        logger.debug("Getting the L1 Ratio")
        return self.algo_settings.get('params').get('l1_ratio')[0]
    
    def get_distribution_function(self):
        logger.debug("Getting the distribution Function")
        distribution_function = self.algo_settings.get('params').get('family_name')
        return distribution_function.title()
    
    def get_link_function(self):
        logger.debug("Getting the Link Function")
        distribution_function = self.get_distribution_function()
        link_function = self.algo_settings.get('params').get(distribution_function.lower()+"_link").title()
        logger.debug(f"Returning the link_function as {link_function}")
        return link_function
    
        

        
    
