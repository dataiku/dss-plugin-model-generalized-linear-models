import dataiku
from dataiku import pandasutils as pdu
import pandas as pd
import logging 

class DataikuMLTask:
    """
    A class to manage machine learning tasks in Dataiku DSS.
    """

    def __init__(self, input_dataset, distribution_function, link_function, variables):
        """
        Initializes the DataikuMLTask with the required parameters.
        """
        self.client = dataiku.api_client()
        logging.info("Dataiku API client initialized.")

        self.input_dataset = input_dataset
        logging.info(f"Input dataset set to '{input_dataset}'.")

        self.distribution_function = distribution_function.lower()
        logging.info(f"Distribution function set to '{distribution_function.lower()}'.")

        self.link_function = link_function.lower()
        logging.info(f"Link function set to '{link_function.lower()}'.")

        self.variables = [{'name': key, **value} for key, value in variables.items()]
        logging.info(f"Variables processed and set: {self.variables}")

        self.project = self.client.get_default_project()
        logging.info("Default project obtained from Dataiku API client.")

        # Initialize variables
        self.exposure_variable = None
        self.weights_variable = None
        self.offset_variable = None
        self.target_variable = None  # Initialize target_variable

        # Extract special variables based on their roles
        for variable in self.variables:
            role = variable.get("role")
            if role == "Exposure":
                self.exposure_variable = variable['name']
                logging.info(f"Exposure variable identified and set to '{self.exposure_variable}'.")
            elif role == "weights":
                self.weights_variable = variable['name']
                logging.info(f"Weights variable identified and set to '{self.weights_variable}'.")
            elif role == "offset":
                self.offset_variable = variable['name']
                logging.info(f"Offset variable identified and set to '{self.offset_variable}'.")
            elif role == "Target":
                self.target_variable = variable['name']
                logging.info(f"Target variable identified and set to '{self.target_variable}'.")

    def set_target(self):
        """
        Identifies and sets the target variable from the list of variables.
        Raises a ValueError if no target variable is found.
        """
        found = False
        for variable in self.variables:
            if variable.get("role") == "Target":
                self.target_variable = variable['name']
                logging.info(f"Target variable set to '{self.target_variable}'.")
                found = True
                break
        if not found:
            message = "No target variable provided."
            logging.error(message)
            raise ValueError(message)
    
    def test_settings(self):
        return self.mltask.get_settings()
    
    def update_mltask_modelling_params(self):
        """
        Updates the modeling parameters based on the distribution function, link function,
        and any special variables like exposure or offset.
        """
        logging.info("Updating ML task modeling parameters.")
        settings = self.mltask.get_settings()
        algo_settings = settings.get_algorithm_settings('CustomPyPredAlgo_generalized-linear-models_generalized-linear-models_regression')
        algo_settings['params'].update({
            f"{self.distribution_function}_link": self.link_function,
            "family_name": self.distribution_function
        })
        logging.info(f"Algorithm settings updated with distribution function '{self.distribution_function}' and link function '{self.link_function}'.")

        # Handle exposure and offset variables
        if self.offset_variable and self.exposure_variable:
            algo_settings['params'].update({
                "offset_mode": "OFFSETS/EXPOSURES",
                "offset_columns": [self.offset_variable],
                "exposure_columns": [self.exposure_variable],
                "training_dataset": self.input_dataset
            })
            logging.info(f"Exposure and offset variables set to '{self.exposure_variable}' and '{self.offset_variable}', respectively.")
        elif self.offset_variable:
            algo_settings['params'].update({
                "offset_mode": "OFFSETS",
                "offset_columns": [self.offset_variable],
                "training_dataset": self.input_dataset
            })
            logging.info(f"Offset variable set to '{self.offset_variable}'.")
        else:
            algo_settings['params']["offset_mode"] = "BASIC"
            logging.info("No exposure or offset variables identified; default offset mode set to 'BASIC'.")

        settings.save()
        logging.info("ML task settings saved with updated modeling parameters.")


    
    def create_visual_ml_task(self):
        """
        Creates a new visual ML task in Dataiku.
        """
        self.set_target()
        logging.info("Creating a new visual ML task in Dataiku.")
        # Create a new ML Task to predict the variable from the specified dataset
        self.mltask = self.project.create_prediction_ml_task(
            input_dataset=self.input_dataset,
            target_variable=self.target_variable,
            ml_backend_type='PY_MEMORY',  # ML backend to use
            guess_policy='DEFAULT'  # Template to use for setting default parameters
        )
        logging.info("New visual ML task created, waiting for guess to complete.")
        # Wait for the ML task to be ready
        self.mltask.wait_guess_complete()
        logging.info("Guess completed for the ML task.")

        self.update_mltask_modelling_params()
        logging.info("ML task modelling parameters updated.")

        self.disable_existing_variables()
        logging.info("Existing variables disabled.")

    def disable_existing_variables(self):
        """
        First, disable all existing variables.
        """
        logging.info("Disabling all existing variables in ML task settings.")
        settings = self.mltask.get_settings()   
        for feature_name in settings.get_raw()['preprocessing']['per_feature'].keys():
            if feature_name != self.target_variable:
                settings.reject_feature(feature_name)
                logging.info(f"Variable '{feature_name}' disabled.")
        settings.save()
        logging.info("ML task settings saved after disabling variables.")

    def enable_glm_algorithm(self):
        """
        Enables the GLM algorithm for the ML task.
        """
        logging.info("Disabling all algorithms for the ML task.")
        settings = self.mltask.get_settings()
        settings.disable_all_algorithms()
        logging.info("All algorithms disabled.")
        
        # Assuming GLM is represented as 'GLM_REGRESSION' or 'GLM_CLASSIFICATION', adjust as necessary
        settings.set_algorithm_enabled("CustomPyPredAlgo_generalized-linear-models_generalized-linear-models_regression", True)
        settings.save()
        logging.info("GLM algorithm enabled and settings saved.")

    def configure_variables(self):
        """
        Configures the variables for the ML task, setting the type of processing for each.
        """
        logging.info("Configuring variables for the ML task.")
        settings = self.mltask.get_settings()
        
        for variable in self.variables:
            variable_name = variable['name']
            if variable_name != self.target_variable and variable['role'] != 'reject':
                settings.use_feature(variable_name)
                logging.info(f"Variable '{variable_name}' used in ML task.")
                fs = settings.get_feature_preprocessing(variable_name)
                
                # Configure categorical variables
                if variable['type'] == 'categorical':
                    fs["category_handling"] = variable.get('processing', 'NONE')
                    logging.info(f"Categorical variable '{variable_name}' processing set to '{variable.get('processing', 'NONE')}'.")
                
                # Configure numerical variables with specific processing types
                elif variable['type'] == 'numerical':
                    processing = variable.get('processing', 'NONE')
                    if processing == 'standardize':
                        fs["rescaling"] = "STANDARD"
                        logging.info(f"Numerical variable '{variable_name}' rescaling set to STANDARD.")
                    elif processing == 'normalize':
                        fs["rescaling"] = "MINMAX"
                        logging.info(f"Numerical variable '{variable_name}' rescaling set to MINMAX.")
            elif variable_name == self.target_variable:
                pass
            else:
                settings.reject_feature(variable_name)
                logging.info(f"Variable '{variable_name}' rejected and not used in ML task.")
                
        try:
            logging.info(f"Attempting to save settings {settings}")
            settings.save()
        except:
            logging.error(f"Failed to save settings. Error: {e}")
            
        logging.info("ML task settings updated with configured variables.")

    def train_model(self):
        """
        Trains the model with the current configuration.
        """
        logging.info(f"Starting model training with these settings {self.mltask.get_settings()}.")
        self.mltask.start_train()
        self.mltask.wait_train_complete()
        logging.info("Model training completed.")