import logging
import dataiku

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelDeployer():
    
    def __init__(self, ml_task, saved_model_id):
        
        self.client = dataiku.api_client()
        self.project = self.client.get_default_project()
        self.saved_model = self.project.get_saved_model(saved_model_id)
        self.saved_model_id = saved_model_id
        self.mltask = ml_task
        self.deployed_models = self.get_deployed_models()

    def get_deployed_models(self):
        versions = self.saved_model.list_versions()

        # Initialize an empty dictionary for version mappings
        version_mapping = {}

        # Iterate over each version
        for version in versions:
            # Get detailed information for the current version
            version_details = self.saved_model.get_version_details(version['id'])

            # Extract fullModelId from the version details
            full_model_id = version_details.details['smOrigin']['fullModelId']

            # Map fullModelId to version['id'] in the dictionary
            version_mapping[full_model_id] = version['id']
        
        return version_mapping

    def set_new_active_version(self, model_id):
        
        if model_id in self.deployed_models.keys():
            self.saved_model.set_active_version(self.deployed_models[model_id])
            logger.info(f"Model {model_id} activated successfully.")
        else:
            self.mltask.redeploy_to_flow(model_id, saved_model_id=self.saved_model_id, activate=True)
            self.deployed_models = self.get_deployed_models()
            logger.info(f"Model {model_id} deployed successfully and set to active version.")