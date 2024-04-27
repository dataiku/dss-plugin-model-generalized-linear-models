if not is_local:
    from glm_handler.dku_model_trainer import DataikuMLTask
    from glm_handler.dku_model_handler import ModelHandler
    from glm_handler.dku_model_deployer import ModelDeployer
    from glm_handler.glm_data_handler import GlmDataHandler
    from glm_handler.dku_model_metrics import ModelMetricsCalculator
    from glm_handler.model_cache import setup_model_cache
    
def setup_model_cache(global_dku_mltask):
    list_ml_id = global_dku_mltask.get_trained_models_ids()
    return list_ml_id