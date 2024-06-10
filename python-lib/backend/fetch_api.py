from io import BytesIO
from time import time

import dataiku
import numpy as np
import pandas as pd
from flask import Blueprint, current_app, jsonify, request, send_file
from glm_handler.dku_model_trainer import DataikuMLTask

from backend.model_cache import update_model_cache
from backend.utils.api_utils import format_models
from backend.utils.dataiku_api import dataiku_api

fetch_api = Blueprint("fetch_api", __name__, url_prefix="/api")


@fetch_api.route("/models", methods=["GET"])
def get_models():
    if dataiku_api.global_dss_mltask is None:
        return jsonify({'error': 'ML task not initialized'}), 500
    try:
        models = format_models(dataiku_api.global_dss_mltask)
        return jsonify(models)
    except Exception as e:
        current_app.logger.exception("An error occurred while retrieving models")
        return jsonify({'error': str(e)}), 500


@fetch_api.route("/variables", methods=["POST"])
def get_variables():    
    request_json = request.get_json()
    full_model_id = request_json["id"]
    try:
        variables = dataiku_api.model_cache[full_model_id].get('features')
        if variables is None:
            raise ValueError("variables returned None.")
        
    except ValueError as e:
        current_app.logger.error(f"Validation Error: {e}")
        return jsonify({"error": e})        
    except Exception as e:
        current_app.logger.error(f"An error occurred: {e}")
    
    return jsonify(variables)


@fetch_api.route("/data", methods=["POST"])
def get_data():
    try:
        current_app.logger.info("Received a new request for data prediction.")
        request_json = request.get_json()
        full_model_id = request_json["id"]
        
        current_app.logger.info(f"Model ID received: {full_model_id}")

        predicted_base = dataiku_api.model_cache[full_model_id].get('predicted_and_base')
        current_app.logger.info(f"Successfully generated predictions. Sample is {predicted_base.head()}")
        
        return jsonify(predicted_base.to_dict('records'))
    
    except Exception as e:
        current_app.logger.error(f"An error occurred while processing the request: {e}", exc_info=True)
        return jsonify({"error": "An error occurred during data processing."}), 500


@fetch_api.route("/lift_data", methods=["POST"])
def get_lift_data():
    current_app.logger.info("Received a new request for lift chart data.")
    request_json = request.get_json()
    full_model_id = request_json["id"]
    
    current_app.logger.info(f"Model ID received: {full_model_id}")

    current_app.logger.info(f"Model {full_model_id} is now the active version.")
    
    lift_chart = dataiku_api.model_cache[full_model_id].get('lift_chart_data')
    lift_chart.columns = ['Category', 'Value', 'observedAverage', 'fittedAverage']
    current_app.logger.info(f"Successfully generated predictions. Sample is {lift_chart.head()}")
    
    return jsonify(lift_chart.to_dict('records'))


@fetch_api.route("/update_bins", methods=["POST"])
def get_updated_data(): 
    request_json = request.get_json()

    feature = request_json["feature"]
    nb_bins = request_json["nbBin"]
    predicted_base = dataiku_api.model_handler.get_predicted_and_base_feature(feature, nb_bins)
    df = predicted_base.copy()
    df.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
    
    
    return jsonify(df.to_dict('records'))


@fetch_api.route("/relativities", methods=["POST"])
def get_relativities():
    request_json = request.get_json()
    full_model_id = request_json["id"]
    
    current_app.logger.info(f"Model ID received: {full_model_id}")
    df = dataiku_api.model_cache[full_model_id].get('relativities')
    df.columns = ['variable', 'category', 'relativity']
    current_app.logger.info(f"relativites are {df.head()}")
    return jsonify(df.to_dict('records'))


@fetch_api.route("/get_variable_level_stats", methods=["POST"])
def get_variable_level_stats():
    request_json = request.get_json()
    full_model_id = request_json["id"]

    current_app.logger.info(f"Model ID received: {full_model_id}")

    df = dataiku_api.model_cache[full_model_id].get('variable_stats')
    df.columns = ['variable', 'value', 'relativity', 'coefficient', 'standard_error', 'standard_error_pct', 'weight', 'weight_pct']
    df.fillna(0, inplace=True)
    df.replace([np.inf, -np.inf], 0, inplace=True)
    return jsonify(df.to_dict('records'))


@fetch_api.route("/get_model_comparison_data", methods=["POST"])
def get_model_comparison_data():
    start_time = time()

    current_app.logger.info("Received a new request for data prediction.")
    request_json = request.get_json()
    model1, model2, selectedVariable = request_json["model1"], request_json["model2"], request_json["selectedVariable"]
    
    current_app.logger.info(f"Retrieving {model1} from the cache")
    model_1_predicted_base = dataiku_api.model_cache.get(model1).get('predicted_and_base')
    model_1_predicted_base.columns = ['definingVariable', 'Category', 'model_1_observedAverage', 'model_1_fittedAverage', 'Value', 'model1_baseLevelPrediction']
    current_app.logger.info(f"Successfully retrieved {model1} from the cache")
    
    current_app.logger.info(f"Retrieving {model2} from the cache")
    model_2_predicted_base = dataiku_api.model_cache.get(model2).get('predicted_and_base')
    model_2_predicted_base.columns = ['definingVariable', 'Category', 'model_2_observedAverage', 'model_2_fittedAverage', 'Value', 'model2_baseLevelPrediction']
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


@fetch_api.route("/get_model_metrics", methods=["POST"])
def get_model_metrics():
    request_json = request.get_json()
    
    model1, model2 = request_json["model1"], request_json["model2"]
    
    model_1_metrics = dataiku_api.model_cache.get(model1).get('model_metrics')
    model_2_metrics = dataiku_api.model_cache.get(model2).get('model_metrics')
    
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

    try:
        request_json = request.get_json()
        model = request_json.get("id")
        if not model:
            current_app.logger.error("error: Model ID not provided")

        relativities_dict = dataiku_api.model_cache.get(model).get('relativities_dict')
        if not relativities_dict:
            current_app.logger.error("error: Model Cache not found for {model} cache only has {dataiku_api.model_cache.keys()}")
        
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


@fetch_api.route("/train_model", methods=["POST"])
def train_model():
    
    request_json = request.get_json()
    current_app.logger.info(f"Received a model training request: {request_json}")
    
    input_dataset = dataiku_api.webapp_config.get("training_dataset_string")
    code_env_string = dataiku_api.webapp_config.get("code_env_string")
    saved_model_id = dataiku_api.webapp_config.get("saved_model_id")

    current_app.logger.info(f"Training Dataset name selected is: {input_dataset}") 
    
    distribution_function = request_json.get('model_parameters', {}).get('distribution_function')
    link_function = request_json.get('model_parameters', {}).get('link_function')
    model_name_string = request_json.get('model_parameters', {}).get('model_name', None)
    variables = request_json.get('variables')

    current_app.logger.debug(f"Parameters received - Dataset: {input_dataset}, Distribution Function: {distribution_function}, Link Function: {link_function}, Variables: {variables}")
    params = {
        "input_dataset": input_dataset,
        "distribution_function": distribution_function,
        "link_function": link_function,
        "variables": variables,
        "saved_model_id":saved_model_id
    }
    missing_params = [key for key, value in params.items() if not value]
    if missing_params:
        missing_str = ", ".join(missing_params)
        current_app.logger.error(f"Missing parameters in the request: {missing_str}")
        return jsonify({'error': f'Missing parameters: {missing_str}'}), 400

    try:
        DkuMLTask = DataikuMLTask(input_dataset, saved_model_id)
        
        DkuMLTask.update_parameters(distribution_function, link_function, variables)
        DkuMLTask.create_visual_ml_task()
        current_app.logger.debug("Visual ML task created successfully")

        DkuMLTask.enable_glm_algorithm()
        current_app.logger.debug("GLM algorithm enabled successfully")

        settings = DkuMLTask.test_settings()
        settings_new = DkuMLTask.configure_variables()
        current_app.logger.debug("Model settings configured successfully")

        DkuMLTask.train_model(code_env_string=code_env_string, session_name=model_name_string)
        
        
        current_app.logger.info("Model training initiated successfully")
                
        dataiku_api.model_cache = update_model_cache(dataiku_api.global_dss_mltask, dataiku_api.model_cache, dataiku_api.model_handler)
        
        return jsonify({'message': 'Model training initiated successfully.'}), 200
    except Exception as e:
        current_app.logger.exception("An error occurred during model training")
        return jsonify({'error': str(e)}), 500


@fetch_api.route("/get_dataset_columns", methods=["GET"])
def get_dataset_columns():
    
    try:
        dataset_name = dataiku_api.web_app_config.get("training_dataset_string")
        
        current_app.logger.info(f"Training Dataset name selected is: {dataset_name}")

        cols_dict = dataiku.Dataset(dataset_name).get_config().get('schema').get('columns')
        column_names = [column['name'] for column in cols_dict]

        current_app.logger.info(f"Successfully retrieved column names for dataset '{dataset_name}': {column_names}")

        return jsonify(column_names)
    
    except KeyError as e:
        current_app.logger.error(f"Missing key in request: {e}")
        return jsonify({'error': f'Missing key in request: {e}'}), 400
    
    except Exception as e:
        current_app.logger.exception(f"Error retrieving columns for dataset '{dataset_name}': {e}")
        return jsonify({'error': str(e)}), 500
