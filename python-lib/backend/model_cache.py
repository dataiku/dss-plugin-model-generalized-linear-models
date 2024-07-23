from glm_handler.dku_relativites_calculator import RelativitiesCalculator
from glm_handler.dku_model_deployer import ModelDeployer
from glm_handler.glm_data_handler import GlmDataHandler
from glm_handler.dku_model_metrics import ModelMetricsCalculator
from backend.api_utils import check_model_conformity
from time import time
from logging_assist.logging import logger
from glm_handler.glm_data_handler import GlmDataHandler
from dku_visual_ml.dku_model_retrival import VisualMLModelRetriver
from chart_formatters.lift_chart import LiftChartFormatter

data_handler = GlmDataHandler()



def setup_model_cache(global_dku_mltask, model_deployer):
    if global_dku_mltask is None or model_deployer is None:
        logger.warning("One or more input parameters are None. Exiting setup_model_cache.")
        return

        return
    
    else:
        logger.info("Updating Model cache")
        model_cache_setup_time = time()
        model_cache = {}
        model_id_list = global_dku_mltask.get_trained_models_ids()
        logger.debug(f"Model ID list obtained for the cache is: {model_id_list}")

        for model_id in model_id_list:
            loop_start_time = time()
            logger.debug(f"Processing model ID: {model_id}")

            model_details = global_dku_mltask.get_trained_model_details(model_id)
            logger.debug(f"Model details for {model_id}: {model_details}")
            
            is_conform = check_model_conformity(model_details)
            logger.debug(f"Model conformity check for {model_id}: {is_conform}")

            if is_conform:
                
                logger.info(f"Model {model_id} conforms to the requirements. Proceeding with deployment.")
                
                # Deploy the model
                step_time = time()
                model_deployer.set_new_active_version(model_id)
                step_elapsed = time() - step_time
                logger.info(f"Step - Deploy model {model_id}: {step_elapsed:.2f} seconds")

                # Update active version
                step_time = time()
                model_retriever = VisualMLModelRetriver(
                    model_id
                )
                relativities_calculator = RelativitiesCalculator(
                    data_handler,
                    model_retriever
                )
                features = relativities_calculator.model_retriever.get_features()
                logger.info(f"Model Features for {model_id}: {features}")

                step_elapsed = time() - step_time
                logger.info(f"Step - Update active version: {step_elapsed:.2f} seconds")

                # Get predicted and base
                step_time = time()
                model1_predicted_base = relativities_calculator.get_predicted_and_base()
                logger.debug(f"Predicted and base data for {model_id}: {model1_predicted_base.head()}")
                
                model1_predicted_base.columns = ['definingVariable', 
                                                 'Category', 
                                                 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction', 'dataset']
                step_elapsed = time() - step_time
                logger.info(f"Step - Get predicted and base: {step_elapsed:.2f} seconds")

                # Get features
                step_time = time()
                features = relativities_calculator.model_retriever.get_features_used_in_modelling()
                step_elapsed = time() - step_time
                logger.info(f"Step - Get features: {step_elapsed:.2f} seconds")

                # Get relativities
                step_time = time()
                relativities = relativities_calculator.get_relativities_df()
                relativities_dict = relativities_calculator.relativities
                step_elapsed = time() - step_time
                logger.info(f"Step - Get relativities: {step_elapsed:.2f} seconds")

                # Get variable level stats
                step_time = time()
                variable_stats=relativities_calculator.get_variable_level_stats()
                step_elapsed = time() - step_time
                logger.info(f"Step - Get variable level stats: {step_elapsed:.2f} seconds")

                # Get lift chart
                step_time = time()
                lift_chart = LiftChartFormatter(
                         model_retriever,
                         data_handler,
                         relativities_calculator
                ) 
                lift_chart_data = lift_chart.get_lift_chart(8)
                
                step_elapsed = time() - step_time
                logger.info(f"Step - Get lift chart: {step_elapsed:.2f} seconds")

                # Calculate model metrics
                step_time = time()
                mmc = ModelMetricsCalculator(model_retriever)
                model_1_aic, model_1_bic, model_1_deviance = mmc.calculate_metrics()
                step_elapsed = time() - step_time
                logger.info(f"Step - Calculate model metrics: {step_elapsed:.2f} seconds")

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
            logger.info(model_id)
        return model_cache

def update_model_cache(global_dku_mltask, model_cache):
    logger.info("Updating model cache")
    
    model_id_list = global_dku_mltask.get_trained_models_ids()
    logger.debug(f"Model ID list obtained: {model_id_list}")
    
    for model_id in model_id_list:
        if model_id not in model_cache.keys():
            logger.debug(f"Model ID {model_id} not found in cache. Updating cache.")

            model_retriever = VisualMLModelRetriver(
                model_id
            )
            relativities_calculator = RelativitiesCalculator(
                model_retriever,
                data_handler
            )
            model1_predicted_base = relativities_calculator.get_predicted_and_base()

            model1_predicted_base.columns = ['definingVariable', 
                                             'Category', 
                                             'observedAverage', 
                                             'fittedAverage', 'Value', 'baseLevelPrediction', 'dataset']
            
            features = relativities_calculator.get_features()
            relativities = relativities_calculator.get_relativities_df()
            relativities_dict = relativities_calculator.relativities
            variable_stats = relativities_calculator.get_variable_level_stats()
            lift_chart = LiftChartFormatter(
                     model_retriever,
                     data_handler,
                     relativities_calculator
            ) 
            lift_chart_data = lift_chart.get_lift_chart(8)
            mmc = ModelMetricsCalculator(model_retriever)
            model_1_aic, model_1_bic, model_1_deviance = mmc.calculate_metrics()

            model_cache[model_id] = {
                'features': features,
                'relativities': relativities,
                'relativities_dict': relativities_dict,
                'predicted_and_base': model1_predicted_base,
                'lift_chart_data': lift_chart_data,
                'variable_stats': variable_stats,
                'model_metrics': {
                    "AIC": model_1_aic,
                    "BIC": model_1_bic,
                    "Deviance": model_1_deviance
                }
            }

            logger.debug(f"Model ID {model_id} cache updated.")
    
    logger.info("Model cache update complete.")
    return model_cache
