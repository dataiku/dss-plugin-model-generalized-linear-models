import dataiku
from dataiku import pandasutils as pdu
import pandas as pd
import logging
from dataikuapi.dss.ml import DSSMLTask

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataikuMLTask:
    """
    A class to manage machine learning tasks in Dataiku DSS.
    
    Attributes:
        input_dataset (str): The name of the input dataset.
        distribution_function (str): The distribution function used for the ML task.
        link_function (str): The    link function used in conjunction with the distribution function.
        variables (list): A list of dictionaries, each representing a variable and its properties.
        client: Instance of the Dataiku API client.
        project: The default project from the Dataiku API client.
        exposure_variable (str): Name of the exposure variable, if any.
        weights_variable (str): Name of the weights variable, if any.
        offset_variable (str): Name of the offset variable, if any.
    """
    
    def __init__(self, input_dataset, saved_model_id):
        logger.info("Initializing DataikuMLTask")
        self.client = dataiku.api_client()
        self.saved_model_id = saved_model_id
        self.project = self.client.get_default_project()
        self.project_key = self.project.project_key 
        self.dku_model_obj = dataiku.Model(saved_model_id)
        logger.info("Dataiku API client initialized")
        self.input_dataset = input_dataset
        logger.info(f"input_dataset set to {input_dataset}")
        self.model = self.project.get_saved_model(saved_model_id)
        try:
            self.mltask = self.model.get_origin_ml_task()
            self.ml_task_variables = list(self.mltask.get_settings().get_raw().get('preprocessing').get('per_feature').keys())
        except:
            raise ValueError("""There is no associated ML task for your model. 
            This model was likely imported or trained somewhere else and is not compatible.""")
        
        self.analysis_id = None
        self.mltask_id = None
        
        logger.info("DataikuMLTask initialized successfully")
    
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
        elif self.exposure_variable:
            algo_settings['params'].update({
                "offset_mode": "OFFSETS/EXPOSURES",
                "offset_columns": [],
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
    
    def update_parameters(self, distribution_function, link_function, variables):
        
        self.distribution_function = distribution_function.lower()
        logger.info(f"distribution_function set to {self.distribution_function}")

        self.link_function = link_function.lower()
        logger.info(f"link_function set to {self.link_function}")

        self.variables = [{'name': key, **value} for key, value in variables.items()]
        
        variable_names = [var['name'] for var in self.variables]
        settings = self.mltask.get_settings()   
        self.existing_variable_names = settings.get_raw()['preprocessing']['per_feature'].keys()
        # Check if any name in variable_names is not in existing_variable_names
        if any(name not in self.existing_variable_names for name in variable_names):
            raise ValueError(
                """Your original dataset has been updated and the schema has not been propagated. 
                As a result, your training dataset has column names {} but the model 
                only has these available to it {}. Please propagate the schema to fix.""".format(
                    variable_names, self.existing_variable_names
                )
            )
        
        logger.info(f"variables set to {self.variables}")

        self.project = self.client.get_default_project()
        logger.info("Default project obtained from Dataiku API client")

        self.exposure_variable = None
        self.weights_variable = None
        self.offset_variable = None

        for variable in self.variables:
            role = variable.get("role", "").lower()
            if role == "exposure":
                self.exposure_variable = variable['name']
                logger.info(f"exposure_variable set to {self.exposure_variable}")
            elif role == "weights":
                self.weights_variable = variable['name']
                logger.info(f"weights_variable set to {self.weights_variable}")
            elif role == "offset":
                self.offset_variable = variable['name']
                logger.info(f"offset_variable set to {self.offset_variable}")
    
    def create_visual_ml_task(self):
        """
        Creates a new visual ML task in Dataiku.
        """
        
        self.set_target()
        
        # Create a new ML Task to predict the variable from the specified dataset
        if not self.mltask:
            logger.info("No ML task exists check the set up of saved model")
        
#             self.mltask = self.project.create_prediction_ml_task(
#                 input_dataset=self.input_dataset,
#                 target_variable=self.target_variable,
#                 ml_backend_type='PY_MEMORY',  # ML backend to use
#                 guess_policy='DEFAULT'  # Template to use for setting default parameters
#             )


#             # Wait for the ML task to be ready
#             self.mltask.wait_guess_complete()
            
#             self.analysis_id = self.mltask.analysis_id
#             self.mltask_id = self.mltask.mltask_id
            
        else:
            logger.info(f"Using Saved model detected as {self.model.id}, updating existing sessions")
            
#             self.mltask = DSSMLTask(self.client, self.project_key, self.analysis_id, self.mltask_id)
            
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
    
    def update_to_numeric(self, fs, variable_preprocessing_method='NONE'):
        fs['generate_derivative'] = False
#         fs['numerical_handling'] = variable_preprocessing_method
        fs['numerical_handling'] = 'REGULAR'
        fs['missing_handling'] = 'IMPUTE'
        fs['missing_impute_with'] = 'MEAN'
        fs['impute_constant_value'] = 0.0
        fs['keep_regular'] = False
        fs['rescaling'] = variable_preprocessing_method
        fs['quantile_bin_nb_bins'] = 4
        fs['binarize_threshold_mode'] = 'MEDIAN'
        fs['binarize_constant_threshold'] = 0.0
        fs['datetime_cyclical_periods'] = []
        fs['role'] = 'INPUT'
        fs['type'] = 'NUMERIC'
        fs['customHandlingCode'] = ''
        fs['customProcessorWantsMatrix'] = False
        fs['sendToInput'] = 'main'
        return fs
    
    def update_to_categorical(self, fs, variable_preprocessing_method="CUSTOM"):
        
        fs['missing_impute_with']= 'MODE'
        fs['type']= 'CATEGORY'
#         fs['category_handling'] = "variable_preprocessing_method"
        fs['category_handling'] = "CUSTOM"
        fs['missing_handling'] = 'IMPUTE'
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
        fs['customHandlingCode'] = ('import numpy as np\n'
        'import pandas as pd\n'
        'class rebase_mode():\n'
        '    """This processor applies dummy vectorisation, but drops the dummy column with the mode. Only applies to categorical variables\n'
        '    """\n'
        '    def __init__(self):\n'
        '        self.mode_column = None\n'
        '    def fit(self, series):\n'
        '        # identify the mode of the column, returns as a text value\n'
        '        self.modalities = np.unique(series)\n'
        '        self.mode_column = series.mode()[0]\n'
        '        self.columns = set(self.modalities)\n'
        '        self.columns.remove(self.mode_column)\n'
        '        self.columns = list(self.columns)\n'
        '        self.column_name = series.name\n'
        '    def transform(self, series):\n'
        '        to_replace={m: self.mode_column for m in np.unique(series) if m not in self.modalities}\n'
        '        new_series = series.replace(to_replace=to_replace)\n'
        '        # obtains the dummy encoded dataframe, but drops the dummy column with the mode identified\n'
        '        df = pd.get_dummies(new_series.values)\n'
        '        if self.mode_column in df:\n'
        '            df = df.drop(self.mode_column, axis = 1)\n'
        '        for c in self.columns:\n'
        '            if c not in df.columns:\n'
        '                df[c] = 0\n'
        '        df = df[self.columns]\n'
        '        return df\n'
        'processor = rebase_mode()')
        
        return fs
    
    def configure_variables(self):
        """
        Configures the variables for the ML task, setting the type of processing for each.
        """
        settings = self.mltask.get_settings()
        
        for variable in self.variables:
            variable_name = variable['name']
            if variable_name != self.target_variable and variable_name != self.exposure_variable and variable['included']:
                settings.use_feature(variable_name)
                fs = settings.get_feature_preprocessing(variable_name)
                
                # Configure categorical variables
                if variable['type'] == 'categorical':
                    variable_preprocessing_method = variable.get('processing', None)
                    fs = self.update_to_categorical(fs, variable_preprocessing_method)

                
                # Configure numerical variables with specific processing types
                elif variable['type'] == 'numerical':
#                     processing = variable.get('processing', 'NONE')
                    fs = self.update_to_numeric(fs, "NONE")
            elif variable_name == self.target_variable:
                    pass
            elif variable_name == self.exposure_variable:
                settings.use_feature(variable_name)
                fs = settings.get_feature_preprocessing(variable_name)
                fs = self.update_to_numeric(fs, "NONE")
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
    
    def set_code_env_settings(self,code_env_string):
        settings = self.mltask.get_settings()
        settings.mltask_settings['envSelection']['envMode'] = 'EXPLICIT_ENV'
        settings.mltask_settings['envSelection']['envName'] = code_env_string
        settings.save()
        logger.info(f"set code env settings to {self.mltask.get_settings().mltask_settings.get('envSelection')} ")
    
    def get_latest_model(self):
        """
        Retrieves the ID of the latest trained model.

        This function iterates through all the model IDs obtained from the ML task,
        comparing their start times to find the most recently trained model. It returns
        the ID of this model.

        Returns:
            str: The ID of the latest trained model.
        """
        logger.info("Retrieving the latest model ID.")
        latest_model_id = None
        latest_start_time = 0
        ids = self.mltask.get_trained_models_ids()
        if not ids:
            logger.warning("No trained models found.")
            return None

        for model_id in ids:
            details = self.mltask.get_trained_model_details(model_id).get_raw()
            start_time = details['trainInfo']['startTime']
            if start_time > latest_start_time:
                latest_start_time = start_time
                latest_model_id = model_id
                logger.debug(f"New latest model found: {model_id} with start time {start_time}")

        if latest_model_id is None:
            logger.warning("Failed to find the latest model.")
        else:
            logger.info(f"Latest model ID: {latest_model_id}")
        return latest_model_id
    
    def deploy_model(self):
        """
        Deploys the latest model to the flow.

        This function first retrieves the ID of the latest model by calling
        `get_latest_model`. It then deploys this model to the flow using the specified
        model name and input dataset.
        """
        logger.info("Deploying the latest model to the flow.")
        model_id = self.get_latest_model()
        if model_id is None:
            logging.error("No model to deploy. Exiting deployment process.")
            return
#         self.mltask.deploy_to_flow(model_id, self.dku_model_obj.get_name(), self.input_dataset)
        self.mltask.redeploy_to_flow(model_id, saved_model_id=self.saved_model_id)
        logger.info(f"Model {model_id} deployed successfully.")
    
    def train_model(self, code_env_string, session_name=None):
        """
        Trains the model with the current configuration and then deploys it.

        Args:
            code_env_string (str): A string specifying the code environment settings.
            session_name (str, optional): The name of the training session. Defaults to None.

        Trains the model by setting the code environment, starting the training process,
        waiting for it to complete, and then deploying the trained model.
        """
        logging.info("Starting model training.")
        self.set_code_env_settings(code_env_string)
        self.mltask.start_train(session_name=session_name)
        self.mltask.wait_train_complete()
        logging.info("Model training completed. Deploying the model.")
        try:
            self.deploy_model()
        except Exception as e:
            # This logs the error message along with the stack trace.
            logging.exception("Failed to deploy model to the flow: %s", e)
