
class ModelDeployer():
    
    def __init__(self, ml_task, saved_model_id):
        self.saved_model_id
        self.mltask = mltask
        
    def deploy_to_flow(self, model_id)
        logger.info(f"Model {model_id} deployed successfully.")
        self.mltask.redeploy_to_flow(model_id, saved_model_id=self.saved_model_id, activate=True)
        logger.info(f"Model {model_id} deployed successfully and set to active version.")