import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelDeployer():
    
    def __init__(self, saved_model, ml_task, saved_model_id):
        self.saved_model = saved_model
        self.saved_model_id = saved_model_id
        self.mltask = ml_task
        self.deployed_models = {self.saved_model.get_version_details(version['id']).details['smOrigin']['fullModelId']: version['id'] for version in self.saved_model.list_versions()}
        
    def set_new_active_version(self, model_id):
        logger.info(f"Model {model_id} deployed successfully.")
        self.mltask.redeploy_to_flow(model_id, saved_model_id=self.saved_model_id, activate=True)
        logger.info(f"Model {model_id} deployed successfully and set to active version.")