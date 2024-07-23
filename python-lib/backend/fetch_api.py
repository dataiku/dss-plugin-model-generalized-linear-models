from flask import Blueprint, jsonify, request, send_file, current_app
import pandas as pd
import random
import re
from logging_assist.logging import logger
from backend.api_utils import format_models, np_encode
from backend.local_config import *
from dku_visual_ml.dku_train_model_config import DKUVisualMLConfig
from io import BytesIO
from time import time
import traceback
import dataiku
import threading
import numpy as np
import time

is_local = False
visual_ml_trainer = model_cache = model_deployer =relativities_calculator = None

logger.debug(f"Starting web application with is_local: {is_local}")

if not is_local:
    from dku_visual_ml.dku_model_trainer import VisualMLModelTrainer
    from dku_visual_ml.dku_model_retrival import VisualMLModelRetriver
    from glm_handler.dku_model_handler import RelativitiesCalculator
    from glm_handler.dku_model_deployer import ModelDeployer
    from glm_handler.glm_data_handler import GlmDataHandler
    from glm_handler.dku_model_metrics import ModelMetricsCalculator
    from backend.model_cache import setup_model_cache, update_model_cache
    
    visual_ml_config = DKUVisualMLConfig()
    data_handler = GlmDataHandler()
    visual_ml_trainer = VisualMLModelTrainer()
    
    if visual_ml_config.setup_type != "new":
        visual_ml_trainer.setup_using_existing_ml_task(
            visual_ml_config.existing_analysis_id, 
            visual_ml_config.saved_model_id
            )
        model_deployer = ModelDeployer(
            visual_ml_trainer.mltask, 
            visual_ml_config.saved_model_id
            )
        relativities_calculator = RelativitiesCalculator(
            visual_ml_config.saved_model_id, 
            data_handler,
            model_retriever
            )
    
        
def setup_cache():
    global model_cache
    latest_ml_task = visual_ml_trainer.get_latest_ml_task()
    model_cache = setup_model_cache(latest_ml_task, model_deployer, relativities_calculator)

loading_thread = threading.Thread(target=setup_cache)
loading_thread.start()


fetch_api = Blueprint("fetch_api", __name__, url_prefix="/api")
client = dataiku.api_client()
project = client.get_default_project()
@fetch_api.route("/train_model", methods=["POST"])

def train_model():
    logger.info("Initalising Model Traing")
    
    if is_local:
        logger.info("Local set up: No model training completed")
        time.sleep(2)
        return jsonify({'message': 'Model training initiated successfully.'}), 200
    
    global visual_ml_trainer, model_cache, model_deployer, relativites_calculator
    
    visual_ml_config.update_model_parameters(request.get_json())

    try:
        ml_task = visual_ml_trainer.get_latest_ml_task()
        if not ml_task:
            current_app.logger.debug("First time training a model, creating Visual ML Trainer")
            visual_ml_trainer = VisualMLModelTrainer(visual_ml_config)
        
        visual_ml_trainer.update_visual_ml_config(visual_ml_config)
        model_details = visual_ml_trainer.train_model(
            code_env_string=visual_ml_config.code_env_string,
            session_name=visual_ml_config.model_name_string
        )
        
        saved_model_id = model_details.get("savedModelId")
        current_app.logger.info("Model training initiated successfully")
        loading_thread.join()
        
        if not model_cache:
            logger.info("Creating Model cache For the first time")
            latest_ml_task = visual_ml_trainer.get_latest_ml_task()
            model_deployer = ModelDeployer(latest_ml_task, saved_model_id)
            relativities_calculator = RelativitiesCalculator(saved_model_id, data_handler, model_retriever)
            model_cache = setup_model_cache(latest_ml_task, model_deployer, relativities_calculator)
        
        model_cache = update_model_cache(latest_ml_task, model_cache, relativities_calculator)
        
        logger.info("Model trained and cache updated")
        return jsonify({'message': 'Model training completed successfully.'}), 200
    except Exception as e:
        current_app.logger.exception(f"An error occurred during model training {e}")
        return jsonify({'error': str(e)}), 500
    
    
@fetch_api.route("/get_latest_mltask_params", methods=["POST"])
def get_latest_mltask_params():
    
    if is_local:
        setup_params = random.choice([dummy_setup_params, dummy_setup_params_2])
        current_app.logger.info(f"Returning Params {setup_params}")
        return jsonify(setup_params)
    
    request_json = request.get_json()
    full_model_id = request_json["id"]
    current_app.logger.info(f"Recieved request for latest params for: {full_model_id}")
    
    model_retriver = VisualMLModelRetriver(full_model_id)
    setup_params = model_retriver.get_setup_params()
   
    current_app.logger.info(f"Returning setup params {setup_params}")
    return jsonify(setup_params)

@fetch_api.route("/variables", methods=["POST"])
def get_variables():
    if is_local:
        return jsonify(dummy_variables)
    
    request_json = request.get_json()
    full_model_id = request_json["id"]
    try:
        loading_thread.join()
        variables = model_cache[full_model_id].get('features')
        logger.debug(f"Model cache for{full_model_id} is {model_cache[full_model_id]}")
        
    except ValueError as e:
        current_app.logger.error(f"Validation Error: {e}")
        return jsonify({"error": e})        
    except Exception as e:
        current_app.logger.error(f"An error occurred: {e}")
        return jsonify({"error": e})    
        
    if variables is None:
            raise ValueError("No variables returned.")
    else: return jsonify(variables)

@fetch_api.route("/models", methods=["GET"])
def get_models():
    if is_local:
        return jsonify(dummy_models)
    
    latest_ml_task = visual_ml_trainer.get_latest_ml_task()
    
    if latest_ml_task is None:
        return jsonify({'error': 'ML task not initialized'}), 500
    try:  
        current_app.logger.info(f"Mltask has : {len(visual_ml_trainer.mltask.get_trained_models_ids())} Models")
        
        models = format_models(latest_ml_task)
        current_app.logger.info(f"models from global ML task is {models}")
        return jsonify(models)
    except Exception as e:
        current_app.logger.exception("An error occurred while retrieving models")
        return jsonify({'error': str(e)}), 500
    return jsonify(models)


@fetch_api.route("/data", methods=["POST"])
def get_data():
    if is_local:
        import time
        time.sleep(1)
        return jsonify(dummy_df_data.to_dict('records'))
    try:
        loading_thread.join()
        current_app.logger.info("Received a new request for data prediction.")
        request_json = request.get_json()
        full_model_id = request_json["id"]
        train_test = request_json['trainTest']
        dataset = 'test' if train_test else 'train'

        current_app.logger.info(f"Model ID received: {full_model_id}")

        predicted_base = model_cache[full_model_id].get('predicted_and_base')
        predicted_base = predicted_base[predicted_base['dataset']==dataset]
        predicted_base['observedAverage'] = [float('%s' % float('%.3g' % x)) for x in predicted_base['observedAverage']]
        predicted_base['fittedAverage'] = [float('%s' % float('%.3g' % x)) for x in predicted_base['fittedAverage']]
        predicted_base['Value'] = [float('%s' % float('%.3g' % x)) for x in predicted_base['Value']]
        predicted_base['baseLevelPrediction'] = [float('%s' % float('%.3g' % x)) for x in predicted_base['baseLevelPrediction']]
        current_app.logger.info(f"Successfully generated predictions. Sample is {predicted_base.head()}")
        
        return jsonify(predicted_base.to_dict('records'))
    
    except Exception as e:
        current_app.logger.error(f"An error occurred while processing the request: {e}", exc_info=True)
        return jsonify({"error": "An error occurred during data processing."}), 500


@fetch_api.route("/lift_data", methods=["POST"])
def get_lift_data():
    if is_local:
        dummy_lift_data['observedAverage'] = [float('%s' % float('%.3g' % x)) for x in dummy_lift_data['observedAverage']]
        dummy_lift_data['fittedAverage'] = [float('%s' % float('%.3g' % x)) for x in dummy_lift_data['fittedAverage']]
        return jsonify(dummy_lift_data.to_dict('records'))
    current_app.logger.info("Received a new request for lift chart data.")
    loading_thread.join()
    request_json = request.get_json()
    full_model_id = request_json["id"]
    nb_bins = request_json["nbBins"]
    train_test = request_json["trainTest"]
    dataset = 'test' if train_test else 'train'
    
    current_app.logger.info(f"Model ID received: {full_model_id}")

    current_app.logger.info(f"Model {full_model_id} is now the active version.")
    
    lift_chart = model_cache[full_model_id].get('lift_chart_data')
    
    current_nb_bins = len(lift_chart[lift_chart['dataset'] == dataset])
    if current_nb_bins != nb_bins:
        model_deployer.set_new_active_version(full_model_id)
        relativities_calculator.update_active_version()
        lift_chart = relativities_calculator.get_lift_chart(nb_bins)
        model_cache[full_model_id]['lift_chart_data'] = lift_chart
    
    lift_chart.columns = ['Value', 'observedAverage', 'fittedAverage', 'Category', 'dataset']
    lift_chart['observedAverage'] = [float('%s' % float('%.3g' % x)) for x in lift_chart['observedAverage']]
    lift_chart['fittedAverage'] = [float('%s' % float('%.3g' % x)) for x in lift_chart['fittedAverage']]
    lift_chart['Value'] = [float('%s' % float('%.3g' % x)) for x in lift_chart['Value']]
    lift_chart = lift_chart[lift_chart['dataset'] == dataset]
    current_app.logger.info(f"Successfully generated predictions. Sample is {lift_chart.head()}")
    
    return jsonify(lift_chart.to_dict('records'))
#     local dev
    return jsonify(dummy_lift_data.to_dict('records'))


@fetch_api.route("/update_bins", methods=["POST"])
def get_updated_data(): 
    if is_local:
        return jsonify(dummy_get_updated_data.to_dict('records'))
    request_json = request.get_json()

    feature = request_json["feature"]
    nb_bins = request_json["nbBin"]
    predicted_base = relativities_calculator.get_predicted_and_base_feature(feature, nb_bins)
    df = predicted_base.copy()
    df.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
    
    
    return jsonify(df.to_dict('records'))
#     local dev
    return jsonify(dummy_get_updated_data.to_dict('records'))


@fetch_api.route("/relativities", methods=["POST"])
def get_relativities():
    if is_local:
        return jsonify(dummy_relativites.to_dict('records'))
    loading_thread.join()
    request_json = request.get_json()
    full_model_id = request_json["id"]
    
    current_app.logger.info(f"Model ID received: {full_model_id}")
    df = model_cache[full_model_id].get('relativities')
    df.columns = ['variable', 'category', 'relativity']
    current_app.logger.info(f"relativites are {df.head()}")
    return jsonify(df.to_dict('records'))
#     local dev
    return jsonify(dummy_relativites.to_dict('records'))

@fetch_api.route("/get_variable_level_stats", methods=["POST"])
def get_variable_level_stats():
    logger.info("Getting Variable Level Stats")
    if is_local:
        return jsonify(dummy_variable_level_stats)
    
    loading_thread.join()
    request_json = request.get_json()
    full_model_id = request_json["id"]
    current_app.logger.info(f"for Model ID: {full_model_id}")


    df = model_cache[full_model_id].get('variable_stats')
    df.columns = ['variable', 'value', 'relativity', 'coefficient', 'standard_error', 'standard_error_pct', 'weight', 'weight_pct']
    df.fillna(0, inplace=True)
    df.replace([np.inf, -np.inf], 0, inplace=True)
    return jsonify(df.to_dict('records'))




@fetch_api.route("/get_model_comparison_data", methods=["POST"])
def get_model_comparison_data():
    start_time = time()
    
    if is_local:
        df = get_dummy_model_comparison_data()
        current_app.logger.info(f"Data fetched locally in {time() - start_time} seconds.")
        return jsonify(df.to_dict('records'))

    try:
        loading_thread.join()
        current_app.logger.info("Received a new request for data prediction.")
        request_json = request.get_json()
        model1, model2, selectedVariable = request_json["model1"], request_json["model2"], request_json["selectedVariable"]
        
        current_app.logger.info(f"Retrieving {model1} from the cache")
        model_1_predicted_base = model_cache.get(model1).get('predicted_and_base')
        model_1_predicted_base = model_1_predicted_base[model_1_predicted_base['dataset']=='test']
        model_1_predicted_base.columns = ['definingVariable', 'Category', 'model_1_observedAverage', 'model_1_fittedAverage', 'Value', 'model1_baseLevelPrediction', 'dataset']
        current_app.logger.info(f"Successfully retrieved {model1} from the cache")
        
        current_app.logger.info(f"Retrieving {model2} from the cache")
        model_2_predicted_base = model_cache.get(model2).get('predicted_and_base')
        model_2_predicted_base = model_2_predicted_base[model_2_predicted_base['dataset']=='test']
        model_2_predicted_base.columns = ['definingVariable', 'Category', 'model_2_observedAverage', 'model_2_fittedAverage', 'Value', 'model2_baseLevelPrediction', 'dataset']
        current_app.logger.info(f"Successfully retrieved {model2} from the cache")

        merge_time = time()
        merged_model_stats = pd.merge(model_1_predicted_base, model_2_predicted_base, 
                                      on=['definingVariable', 'Category', 'Value'], 
                                      how='outer')
        merged_model_stats = merged_model_stats[merged_model_stats.definingVariable == selectedVariable]
        current_app.logger.info(f"Merged data in {time() - merge_time} seconds. Sample: {merged_model_stats.head().to_string()}")
        
        total_time = time() - start_time
        current_app.logger.info(f"Total execution time: {total_time} seconds.")
        return jsonify(merged_model_stats.to_dict('records'))
    
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500



@fetch_api.route("/get_model_metrics", methods=["POST"])
def get_model_metrics():
    start_time = time()
    
    if is_local:
        response_time = time() - start_time
        logger.info(f"Returned local dummy metrics in {response_time} seconds.")
        return jsonify(dummy_model_metrics)
    
    loading_thread.join()
    request_json = request.get_json()

    
    model1, model2 = request_json["model1"], request_json["model2"]
    
    model_1_metrics = model_cache.get(model1).get('model_metrics')
    model_2_metrics = model_cache.get(model2).get('model_metrics')
    
    metrics = {
        "models": {
            "Model_1": {
                "AIC": model_1_metrics.get('AIC'),
                "BIC": model_1_metrics.get('BIC'),
                "Deviance": model_1_metrics.get('Deviance')
            },
            "Model_2": {
                "AIC": model_2_metrics.get('AIC'),
                "BIC": model_2_metrics.get('AIC'),
                "Deviance": model_2_metrics.get('AIC'),
            }
        }
    }
    return jsonify(metrics)




@fetch_api.route('/export_model', methods=['POST'])
def export_model():

    if is_local:
        data = {'Name': ['John', 'Alice', 'Bob'], 'Age': [30, 25, 35]}
        df = pd.DataFrame(data)

        # Convert DataFrame to CSV format
        csv_data = df.to_csv(index=False).encode('utf-8')
    else:
        try:
            loading_thread.join()
            request_json = request.get_json()
            model = request_json.get("id")
            if not model:
                current_app.logger.error("error: Model ID not provided")

            relativities_dict = model_cache.get(model).get('relativities_dict')
            if not relativities_dict:
                current_app.logger.error("error: Model Cache not found for {model} cache only has {model_cache.keys()}")
            
            current_app.logger.info(f"Relativities dict for model {model} is {relativities_dict}.")
            
            nb_col = (len(relativities_dict.keys()) - 1) * 3
            variables = [col for col in relativities_dict.keys() if col != "base"]
            variable_keys = {variable: list(relativities_dict[variable].keys()) for variable in variables}
            max_len = max(len(variable_keys[variable]) for variable in variable_keys.keys())

            csv_output = ",,\n"
            csv_output += "Base,,{}\n".format(relativities_dict['base']['base'])
            csv_output += ",,\n" * 2
            csv_output += ",,,".join(variables) + ",,\n" * 2

            for i in range(max_len):
                for variable in variables:
                    if i < len(variable_keys[variable]):
                        value = variable_keys[variable][i]
                        csv_output += "{},{},,".format(value, relativities_dict[variable][value])
                    else:
                        csv_output += ",,,"
                csv_output += "\n"

            csv_data = csv_output.encode('utf-8')

        except KeyError as e:
            current_app.logger.error(f"An error occurred: {str(e)}")

    csv_io = BytesIO(csv_data)

    # Serve the CSV file for download
    return send_file(
        csv_io,
        mimetype='text/csv',
        as_attachment=True,
        download_name='model.csv'
    )


@fetch_api.route('/export_variable_level_stats', methods=['POST'])
def export_variable_level_stats():

    if is_local:
        data = {'Name': ['John', 'Alice', 'Bob'], 'Age': [30, 25, 35]}
        df = pd.DataFrame(data)

        # Convert DataFrame to CSV format
        csv_data = df.to_csv(index=False).encode('utf-8')
    else:
        try:
            loading_thread.join()
            request_json = request.get_json()
            full_model_id = request_json["id"]
            
            current_app.logger.info(f"Model ID received: {full_model_id}")

            df = model_cache[full_model_id].get('variable_stats')
            df.columns = ['variable', 'value', 'relativity', 'coefficient', 'standard_error', 'standard_error_pct', 'weight', 'weight_pct']

            csv_data = df.to_csv(index=False).encode('utf-8')

        except KeyError as e:
            current_app.logger.error(f"An error occurred: {str(e)}")

    csv_io = BytesIO(csv_data)

    # Serve the CSV file for download
    return send_file(
        csv_io,
        mimetype='text/csv',
        as_attachment=True,
        download_name='variable_level_stats.csv'
    )


@fetch_api.route('/export_one_way', methods=['POST'])
def export_one_way():

    if is_local:
        data = {'Name': ['John', 'Alice', 'Bob'], 'Age': [30, 25, 35]}
        df = pd.DataFrame(data)

        # Convert DataFrame to CSV format
        csv_data = df.to_csv(index=False).encode('utf-8')
    else:
        try:
            loading_thread.join()
            request_json = request.get_json()
            full_model_id = request_json["id"]
            variable = request_json["variable"]
            train_test = request_json["trainTest"]
            rescale = request_json["rescale"]
            dataset = 'test' if train_test else 'train'

            current_app.logger.info(f"Model ID received: {full_model_id}")
            current_app.logger.info(f"Variable received: {variable}")
            current_app.logger.info(f"Train/Test received: {dataset}")
            current_app.logger.info(f"Rescale received: {rescale}")

            predicted_base = model_cache[full_model_id].get('predicted_and_base')
            predicted_base = predicted_base[predicted_base['dataset']==dataset]
            predicted_base = predicted_base[predicted_base['definingVariable']==variable]

            if rescale:
                relativities = model_cache[full_model_id].get('relativities')
                relativities.columns = ['variable', 'category', 'relativity']
                variable_relativities = relativities[relativities["variable"]==variable]
                base_level = variable_relativities[variable_relativities['relativity']==1]['category'].iloc[0]
                predicted_base_denominator = predicted_base[predicted_base['Category']==base_level].iloc[0]
                predicted_base['observedAverage'] = predicted_base['observedAverage'] / predicted_base_denominator['observedAverage']
                predicted_base['fittedAverage'] = predicted_base['fittedAverage'] / predicted_base_denominator['fittedAverage']
                predicted_base['baseLevelPrediction'] = predicted_base['baseLevelPrediction'] / predicted_base_denominator['baseLevelPrediction']

            csv_data = predicted_base.to_csv(index=False).encode('utf-8')

        except KeyError as e:
            current_app.logger.error(f"An error occurred: {str(e)}")

    csv_io = BytesIO(csv_data)

    # Serve the CSV file for download
    return send_file(
        csv_io,
        mimetype='text/csv',
        as_attachment=True,
        download_name='variable_level_stats.csv'
    )

@fetch_api.route("/get_dataset_columns", methods=["GET"])
def get_dataset_columns():
    
    try:
        # This try statement is just for local development remove the except 
        # which explicitly assins the dataset name
        try: 
            web_app_config = get_webapp_config()
            dataset_name = web_app_config.get("training_dataset_string")
        except:
            dataset_name = "claim_train"
            
        current_app.logger.info(f"Training Dataset name selected is: {dataset_name}")
        
        df = dataiku.Dataset(dataset_name).get_dataframe()
        cols_json = [{'column': col, 'options': sorted([str(val) for val in df[col].unique()]), 'baseLevel': str(df[col].mode().iloc[0])} for col in df.columns]

        current_app.logger.info(f"Successfully retrieved column for dataset '{dataset_name}': {[col['column'] for col in cols_json]}")

        return jsonify(cols_json)
    
    except KeyError as e:
        current_app.logger.error(f"Missing key in request: {e}")
        return jsonify({'error': f'Missing key in request: {e}'}), 400
    
    except Exception as e:
        current_app.logger.exception(f"Error retrieving columns for dataset '{dataset_name}': {e}")
        return jsonify({'error': str(e)}), 500
