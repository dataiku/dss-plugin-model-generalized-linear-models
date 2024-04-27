from glm_handler.dku_model_trainer import DataikuMLTask
from glm_handler.dku_model_handler import ModelHandler
from glm_handler.dku_model_deployer import ModelDeployer
from glm_handler.glm_data_handler import GlmDataHandler
from glm_handler.dku_model_metrics import ModelMetricsCalculator
from time import time

def setup_model_cache(global_dku_mltask, model_deployer, model_handler):
    model_cache_setup_time = time()
    model_cache = {}
    model_id_list = global_dku_mltask.get_trained_models_ids()
    
    for model_id in model_id_list:
        
        
        model_deployer.set_new_active_version(model_id)
        model_handler.update_active_version()
        model1_predicted_base = model_handler.get_predicted_and_base()
        model1_predicted_base.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
        mmc = ModelMetricsCalculator(model_handler)
        model_1_aic, model_1_bic, model_1_deviance = mmc.calculate_metrics()
        
        model_cache[model_id]= {
            'predicted_and_base': model1_predicted_base,
            'model_metrics': {
                "AIC": model_1_aic,
                "BIC": model_1_bic,
                "Deviance": model_1_deviance
            }
        }
        
    print("Model cache set up time took {model_cache_setup_time - time()}")
    return model_cache

def update_model_cache(model_cache, model_handler):
    
        model_handler.update_active_version()
        model1_predicted_base = model_handler.get_predicted_and_base()
        model1_predicted_base.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
        mmc = ModelMetricsCalculator(model_handler)
        model_1_aic, model_1_bic, model_1_deviance = mmc.calculate_metrics()
        
        model_cache[model_id]= {
            'predicted_and_base': model1_predicted_base,
            'model_metrics': {
                "AIC": model_1_aic,
                "BIC": model_1_bic,
                "Deviance": model_1_deviance
            }
        }
        
    return model_cache
