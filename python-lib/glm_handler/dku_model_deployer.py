import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelDeployer():
    
    def __init__(self, saved_model, ml_task, saved_model_id):
        self.saved_model = saved_model
        self.saved_model_id = saved_model_id
        self.mltask = ml_task
        self.deployed_models = self.get_deployed_models()

    def get_deployed_models(self):
        return {self.saved_model.get_version_details(version['id']).details['smOrigin']['fullModelId']: version['id'] for version in self.saved_model.list_versions()}

    def set_new_active_version(self, model_id):
        if model_id in self.deployed_models.keys():
            self.saved_model.set_active_version(self.deployed_models[model_id])
            logger.info(f"Model {model_id} activated successfully.")
        else:
            self.mltask.redeploy_to_flow(model_id, saved_model_id=self.saved_model_id, activate=True)
            self.deployed_models = self.get_deployed_models()
            logger.info(f"Model {model_id} deployed successfully and set to active version.")