import dataiku
from dataiku import pandasutils as pdu
import pandas as pd
import logging 

class DataikuMLTask:
    """
    A class to manage machine learning tasks in Dataiku DSS.
    
    Attributes:
        input_dataset (str): The name of the input dataset.
        distribution_function (str): The distribution function used for the ML task.
        link_function (str): The link function used in conjunction with the distribution function.
        variables (list): A list of dictionaries, each representing a variable and its properties.
        client: Instance of the Dataiku API client.
        project: The default project from the Dataiku API client.
        exposure_variable (str): Name of the exposure variable, if any.
        weights_variable (str): Name of the weights variable, if any.
        offset_variable (str): Name of the offset variable, if any.
    """
    
    def __init__(self, input_dataset, distribution_function, link_function, variables):
        """
        Initializes the DataikuMLTask with the required parameters.
        
        Args:
            input_dataset (str): The name of the input dataset.
            distribution_function (str): The distribution function to use.
            link_function (str): The link function to use.
            variables (dict): A dictionary of variables with their properties.
        """
        self.client = dataiku.api_client()
        self.input_dataset = input_dataset
        self.distribution_function = distribution_function.lower()
        self.link_function = link_function.lower()
        self.variables = [{'name': key, **value} for key, value in variables.items()]
        self.project = self.client.get_default_project()
        
        # Initialize variables
        self.exposure_variable = None
        self.weights_variable = None
        self.offset_variable = None
        
        # Extract special variables based on their roles
        for variable in self.variables:
            role = variable.get("role")
            if role == "exposure":
                self.exposure_variable = variable['name']
            elif role == "weights":
                self.weights_variable = variable['name']
            elif role == "offset":
                self.offset_variable = variable['name']


    
    def disable_existing_variables(self):
            # First, disable all existing variables
        settings = self.mltask.get_settings()   
        for feature_name in settings.get_raw()['preprocessing']['per_feature'].keys():
            if feature_name != self.target_variable:
                settings.reject_feature(feature_name)
        settings.save()
        
    def set_target(self):
        """
        Identifies and sets the target variable from the list of variables.
        Raises a ValueError if no target variable is found.
        """
        for variable in self.variables:
            if variable.get("role").lower() == "target":
                self.target_variable = variable['name']
                return
        raise ValueError("No target variable provided")


    def update_mltask_modelling_params(self):
        """
        Updates the modeling parameters based on the distribution function, link function,
        and any special variables like exposure or offset.
        """
        settings = self.mltask.get_settings()
        algo_settings = settings.get_algorithm_settings('CustomPyPredAlgo_generalized-linear-models_generalized-linear-models_regression')
        algo_settings['params'].update({
            f"{self.distribution_function}_link": self.link_function,
            "family_name": self.distribution_function
        })
        
        # Handle exposure and offset variables
        if self.offset_variable and self.exposure_variable:
            algo_settings['params'].update({
                "offset_mode": "OFFSETS/EXPOSURES",
                "offset_columns": [self.offset_variable],
                "exposure_columns": [self.exposure_variable],
                "training_dataset": self.input_dataset
            })
        elif self.offset_variable:
            algo_settings['params'].update({
                "offset_mode": "OFFSETS",
                "offset_columns": [self.offset_variable],
                "training_dataset": self.input_dataset
            })
        else:
            algo_settings['params']["offset_mode"] = "BASIC"
        
        settings.save()

    
    def create_visual_ml_task(self):
        """
        Creates a new visual ML task in Dataiku.
        """
        self.set_target()
        # Create a new ML Task to predict the variable from the specified dataset
        self.mltask = self.project.create_prediction_ml_task(
            input_dataset=self.input_dataset,
            target_variable=self.target_variable,
            ml_backend_type='PY_MEMORY',  # ML backend to use
            guess_policy='DEFAULT'  # Template to use for setting default parameters
        )
        # Wait for the ML task to be ready
        self.mltask.wait_guess_complete()
        
        self.update_mltask_modelling_params()
        
        
        self.disable_existing_variables()

    def enable_glm_algorithm(self):
        """
        Enables the GLM algorithm for the ML task.
        """
        
        settings = self.mltask.get_settings()
        settings.disable_all_algorithms()
        
        # Assuming GLM is represented as 'GLM_REGRESSION' or 'GLM_CLASSIFICATION', adjust as necessary
        settings.set_algorithm_enabled("CustomPyPredAlgo_generalized-linear-models_generalized-linear-models_regression", True)
        settings.save()

    def test_settings(self):
        return self.mltask.get_settings()
    
    def update_to_numeric(self, fs, variable_preprocessing_method='REGULAR'):
        fs['generate_derivative'] = False
        fs['numerical_handling'] = variable_preprocessing_method
        fs['missing_handling'] = 'IMPUTE'
        fs['missing_impute_with'] = 'MEAN'
        fs['impute_constant_value'] = 0.0
        fs['keep_regular'] = False
        fs['rescaling'] = 'AVGSTD'
        fs['quantile_bin_nb_bins'] = 4
        fs['binarize_threshold_mode'] = 'MEDIAN'
        fs['binarize_constant_threshold'] = 0.0
        fs['datetime_cyclical_periods'] = []
        fs['role'] = 'INPUT'
        fs['type'] = 'NUMERIC'
        fs['customHandlingCode'] = ''
        fs['customProcessorWantsMatrix'] = False
        fs['sendToInput'] = 'main'

    def update_to_categorical(self, fs, variable_preprocessing_method):
        
        fs['missing_impute_with']= 'MODE'
        fs['type']= 'CATEGORY'
        fs['category_handling'] = variable_preprocessing_method
        fs['missing_handling'] = 'NONE'
        fs['dummy_clip'] = 'MAX_NB_CATEGORIES'
        fs['cumulative_proportion'] = 0.95
        fs['min_samples'] = 10
        fs['max_nb_categories'] = 100
        fs['max_cat_safety'] = 200
        fs['nb_bins_hashing'] = 1048576
        fs['hash_whole_categories'] = True
        fs['dummy_drop'] = 'AUTO'
        fs['impact_method'] = 'M_ESTIMATOR'
        fs['impact_m'] = 10
        fs['impact_kfold'] = True
        fs['impact_kfold_k'] = 5
        fs['impact_kfold_seed'] = 1337
        fs['ordinal_order'] = 'COUNT'
        fs['ordinal_ascending'] = False
        fs['ordinal_default_mode'] = 'HIGHEST'
        fs['ordinal_default_value'] = 0
        fs['frequency_default_mode'] = 'EXPLICIT'
        fs['frequency_default_value'] = 0.0
        fs['frequency_normalized'] = True
        fs['role'] = 'INPUT'
        fs['customHandlingCode'] = ''
        fs['customProcessorWantsMatrix'] = False
        fs['sendToInput'] = 'main'
        
        return fs
    
    def configure_variables(self):
        """
        Configures the variables for the ML task, setting the type of processing for each.
        """
        settings = self.mltask.get_settings()
        
        for variable in self.variables:
            variable_name = variable['name']
            if variable_name != self.target_variable and variable['included']:
                settings.use_feature(variable_name)
                fs = settings.get_feature_preprocessing(variable_name)
                
                # Configure categorical variables
                if variable['type'] == 'categorical':
                    variable_preprocessing_method = variable.get('processing', 'NONE')
                    fs = self.update_to_categorical(fs, variable_preprocessing_method)

                
                # Configure numerical variables with specific processing types
                elif variable['type'] == 'numerical':
                    processing = variable.get('processing', 'NONE')
                    fs = self.update_to_numeric(fs,processing)
                    processing = variable.get('processing', 'NONE')
            elif variable_name == self.target_variable:
                    pass
            else:
                settings.reject_feature(variable_name)

        settings.save()
        print('***Updated settings***')
        for feature in settings.get_raw().get('preprocessing').get('per_feature'):
            print(f"Feature {feature} {settings.get_raw().get('preprocessing').get('per_feature').get(feature).get('role')} ")
                            
        return settings


    def set_target_variable(self):
        """
        Sets the target variable for the ML task.
        """
        # This might be part of the task creation process, but if you need to adjust it:
        settings = self.mltask.get_settings()
        settings.set_target_variable(self.target_variable)
        settings.save()

    def train_model(self):
        """
        Trains the model with the current configuration.
        """
        self.mltask.start_train()
        self.mltask.wait_train_complete()
