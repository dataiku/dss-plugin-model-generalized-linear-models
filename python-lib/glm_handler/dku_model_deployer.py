from logging_assist.logging import logger
from dku_visual_ml.dku_base import DataikuClientProject
import dataiku
import random

class ModelDeployer(DataikuClientProject):
    
    def __init__(self, ml_task, saved_model_id):
        super().__init__()
        
        logger.info(f"Initalising Model deployer for saved_model_id {saved_model_id}")
        self.saved_model_id = saved_model_id
        if saved_model_id:
            self.saved_model = self.project.get_saved_model(saved_model_id)
        else:
            self.saved_model = None
        
        self.mltask = ml_task
        logger.info("Successfully Initalised Model deployer")
    def _set_saved_model_attribute(self,saved_model_id):
        self.saved_model_id = saved_model_id
        self.saved_model = self.project.get_saved_model(saved_model_id)
        
    def get_deployed_models(self):
        
        version_mapping = {}
        print(f"In deployed models the self.savedmodel is {self.saved_model}")
        
        if (self.saved_model == None) or self.saved_model == "None" :
            logger.debug("Saved Model Not initalised, deployed models not retrieved")
            return version_mapping
        
        versions = self.saved_model.list_versions()

        # Initialize an empty dictionary for version mappings
        

        # Iterate over each version
        for version in versions:
            # Get detailed information for the current version
            version_details = self.saved_model.get_version_details(version['id'])

            # Extract fullModelId from the version details
            full_model_id = version_details.details['smOrigin']['fullModelId']

            # Map fullModelId to version['id'] in the dictionary
            version_mapping[full_model_id] = version['id']
        
        return version_mapping
    
    def deploy_model(self, model_id, input_dataset):
        """
        Deploys the latest model to the flow.

        This function first retrieves the ID of the latest model by calling
        `get_latest_model`. It then deploys this model to the flow using the specified
        model name and input dataset.
        """
        logger.info(f"Attempting to deploy the latest model: {model_id}, to the flow.")

        if self.saved_model:
            logger.debug(f"Using existing saved Model ID to deploy {self.saved_model_id}")
            try:
                model_details = self.mltask.redeploy_to_flow(model_id, saved_model_id=self.saved_model_id)
                logger.info(f"Successfully used a saved Model ID to deploy {self.saved_model_id}")
                return model_details
            except Exception as e:
                logger.exception("Failed to deploy model to the flow: %s", e)
        else:
            logger.debug("Saved model not present - Creating new Model ID to deploy")
            model_name = str(input_dataset) + "_Model_"+ str(random.randint(0, 1000))
            model_details = self.mltask.deploy_to_flow(model_id, model_name=model_name, train_dataset=input_dataset)
            saved_model_id = model_details.get("savedModelId")
            self._set_saved_model_attribute(saved_model_id)
            logger.info(f"Successfully Deployed Model")
            return model_details

            
    def set_new_active_version(self, model_id):
        
        self.deployed_models = self.get_deployed_models()
        
        if model_id in self.deployed_models.keys():
            self.saved_model.set_active_version(self.deployed_models[model_id])
            logger.info(f"Model {model_id} activated successfully.")
        else:
            self.mltask.redeploy_to_flow(model_id, saved_model_id=self.saved_model_id, activate=True)
            self.deployed_models = self.get_deployed_models()
            logger.info(f"Model {model_id} deployed successfully and set to active version.")