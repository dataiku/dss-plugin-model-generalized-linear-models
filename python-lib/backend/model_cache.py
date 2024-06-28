from glm_handler.dku_model_trainer import DataikuMLTask
from glm_handler.dku_model_handler import ModelHandler
from glm_handler.dku_model_deployer import ModelDeployer
from glm_handler.glm_data_handler import GlmDataHandler
from glm_handler.dku_model_metrics import ModelMetricsCalculator
from backend.api_utils import check_model_conformity
from time import time
from logging_assist.logging import logger




def setup_model_cache(global_dku_mltask, model_deployer, model_handler):
    model_cache_setup_time = time()
    model_cache = {}
    model_id_list = global_dku_mltask.get_trained_models_ids()

    for model_id in model_id_list:
        loop_start_time = time()  # Start timing the processing for this model
        
        model_details = global_dku_mltask.get_trained_model_details(model_id)
        is_conform = check_model_conformity(model_details)
        if is_conform:

            # Deploy the model
            step_time = time()
            model_deployer.set_new_active_version(model_id)
            step_elapsed = time() - step_time
            logger.info(f"Step - Deploy model {model_id}: {step_elapsed:.2f} seconds")

            # Update active version
            step_time = time()
            model_handler.update_active_version()
            step_elapsed = time() - step_time
            logger.info(f"Step - Update active version: {step_elapsed:.2f} seconds")

            # Get predicted and base
            step_time = time()
            model1_predicted_base = model_handler.get_predicted_and_base()
            print(model1_predicted_base)
            logger.info(f"model1_predicted_base colums are: {model1_predicted_base.columns}")
            model1_predicted_base.columns = ['definingVariable', 
                                             'Category', 
                                             'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction', 'dataset']
            step_elapsed = time() - step_time
            logger.info(f"Step - Get predicted and base: {step_elapsed:.2f} seconds")

            # Get features
            step_time = time()
            features = model_handler.get_features()
            step_elapsed = time() - step_time
            logger.info(f"Step - Get features: {step_elapsed:.2f} seconds")

            # Get relativities
            step_time = time()
            relativities = model_handler.get_relativities_df()
            relativities_dict = model_handler.relativities
            step_elapsed = time() - step_time
            logger.info(f"Step - Get relativities: {step_elapsed:.2f} seconds")
            
            # Get variable level stats
            step_time = time()
            variable_stats=model_handler.get_variable_level_stats()
            step_elapsed = time() - step_time
            logger.info(f"Step - Get variable level stats: {step_elapsed:.2f} seconds")
            
            # Get lift chart
            step_time = time()
            lift_chart_data = model_handler.get_lift_chart(8)
            step_elapsed = time() - step_time
            logger.info(f"Step - Get lift chart: {step_elapsed:.2f} seconds")

            # Calculate model metrics
            step_time = time()
            mmc = ModelMetricsCalculator(model_handler)
            model_1_aic, model_1_bic, model_1_deviance = mmc.calculate_metrics()
            step_elapsed = time() - step_time
            print(f"Step - Calculate model metrics: {step_elapsed:.2f} seconds")

            # Store data in cache
            model_cache[model_id] = {
                'features': features,
                'relativities': relativities,
                'predicted_and_base': model1_predicted_base,
                'relativities_dict': relativities_dict,
                'lift_chart_data':lift_chart_data,
                'variable_stats':variable_stats,
                'model_metrics': {
                    "AIC": model_1_aic,
                    "BIC": model_1_bic,
                    "Deviance": model_1_deviance
                }
            }

            # Print the total time taken for this model
            loop_elapsed = time() - loop_start_time
            print(f"Total processing time for model {model_id}: {loop_elapsed:.2f} seconds")
        
    # Print the total setup time for the model cache
    total_setup_time_elapsed = time() - model_cache_setup_time
    print(f"Total model cache set up time: {total_setup_time_elapsed:.2f} seconds")
    for model_id in model_cache.keys():
        print(model_id)
        print(model_cache[model_id]['lift_chart_data'])
    return model_cache

def update_model_cache(global_dku_mltask, model_cache, model_handler):
    
    model_id_list = global_dku_mltask.get_trained_models_ids()
    
    for model_id in model_id_list:
        if model_id not in model_cache.keys():
            model_handler.update_active_version()
            model1_predicted_base = model_handler.get_predicted_and_base()

            model1_predicted_base.columns = ['definingVariable', 
                                             'Category', 
                                             'observedAverage', 
                                             'fittedAverage', 'Value', 'baseLevelPrediction', 'dataset']
            
            features = model_handler.get_features()
            relativities = model_handler.get_relativities_df()
            relativities_dict = model_handler.relativities
            variable_stats=model_handler.get_variable_level_stats()
            lift_chart_data = model_handler.get_lift_chart(8)
            mmc = ModelMetricsCalculator(model_handler)
            model_1_aic, model_1_bic, model_1_deviance = mmc.calculate_metrics()

            model_cache[model_id]= {
                'features':features,
                'relativities':relativities,
                'relativities_dict':relativities_dict,
                'predicted_and_base': model1_predicted_base,
                 'lift_chart_data':lift_chart_data,
                 'variable_stats':variable_stats,
                'model_metrics': {
                    "AIC": model_1_aic,
                    "BIC": model_1_bic,
                    "Deviance": model_1_deviance
                }
            }
        
    return model_cache
