from flask import Blueprint, jsonify, request, send_file, current_app
import pandas as pd
import random
import re
is_local = False

if not is_local:
    from glm_handler.dku_model_trainer import DataikuMLTask
    from glm_handler.dku_model_handler import ModelHandler
    from glm_handler.dku_model_deployer import ModelDeployer
    from glm_handler.glm_data_handler import GlmDataHandler
    from glm_handler.dku_model_metrics import ModelMetricsCalculator
    from backend.model_cache import setup_model_cache, update_model_cache
    
from backend.api_utils import format_models
from backend.local_config import (dummy_models, dummy_variables, dummy_df_data,
dummy_lift_data,dummy_get_updated_data, dummy_relativites, get_dummy_model_comparison_data, 
dummy_model_metrics, dummy_setup_params, dummy_setup_params_2)
from backend.logging_settings import logger
from io import BytesIO
from time import time
import traceback
import dataiku
from dataiku.customwebapp import get_webapp_config
import threading

import numpy as np

fetch_api = Blueprint("fetch_api", __name__, url_prefix="/api")
client = dataiku.api_client()
project = client.get_default_project()

if not is_local:   
    web_app_config = get_webapp_config()
    existing_analysis_id = web_app_config.get("existing_analysis_id")
    input_dataset = web_app_config.get("training_dataset_string")
    prediction_type = web_app_config.get("prediction_type")
    setup_type = web_app_config.get("setup_type")
    policy = web_app_config.get("policy")
    test_dataset_string = web_app_config.get("test_dataset_string")
    
    data_handler = GlmDataHandler()
    
    if setup_type != "new":
        saved_model_id = web_app_config.get("saved_model_id")
        global_DkuMLTask = DataikuMLTask(input_dataset, prediction_type, policy, test_dataset_string)
        global_DkuMLTask.setup_using_existing_ml_task(existing_analysis_id, saved_model_id)
        print(f'Savemodel id is {saved_model_id}')
        model_deployer = ModelDeployer(global_DkuMLTask.mltask, saved_model_id)
        model_handler = ModelHandler(saved_model_id, data_handler)
        
        def setup_cache():
            global model_cache
            model_cache = setup_model_cache(global_DkuMLTask.mltask, model_deployer, model_handler)
        
        loading_thread = threading.Thread(target=setup_cache)
        loading_thread.start()
    else:
        global_DkuMLTask = None
        model_cache = None
        model_deployer = None
        model_handler = None
        
        def setup_cache():
            return
        
        loading_thread = threading.Thread(target=setup_cache)
        loading_thread.start()
    





@fetch_api.route("/models", methods=["GET"])
def get_models():
    
    if is_local:
        return jsonify(dummy_models)
    
    if global_DkuMLTask is None:
        return jsonify({'error': 'ML task not initialized'}), 500
    try:
        #refresh the ml task        
        current_app.logger.info(f"global_DkuMLTask.mltask is: {global_DkuMLTask.mltask.get_trained_models_ids()}")
        dku_ml_task = global_DkuMLTask.mltask
        models = format_models(dku_ml_task)
        current_app.logger.info(f"models from global ML task is {models}")
        return jsonify(models)
    except Exception as e:
        current_app.logger.exception("An error occurred while retrieving models")
        return jsonify({'error': str(e)}), 500
    return jsonify(models)

@fetch_api.route("/get_latest_mltask_params", methods=["POST"])
def get_latest_mltask_params():
    
    request_json = request.get_json()
    current_app.logger.info(f"Recieved request with payload in ml task params: {request_json}")
    full_model_id = request_json["id"]
    current_app.logger.info(f"Recieved request for latest params for: {full_model_id}")
    
    if is_local:
        setup_params = random.choice([dummy_setup_params, dummy_setup_params_2])
        current_app.logger.info(f"Returning Params {setup_params}")
        return jsonify(setup_params)
    #try:
    client = dataiku.api_client()
    mltask = global_DkuMLTask.mltask.from_full_model_id(client,fmi=full_model_id)

    model_details = mltask.get_trained_model_details(full_model_id)

    algo_settings = model_details.get_modeling_settings().get('plugin_python_grid')
    algo_settings.get('params').get('exposure_columns')[0]
    exposure_column = algo_settings.get('params').get('exposure_columns')[0]
    distribution_function = algo_settings.get('params').get('family_name')
    link_function = algo_settings.get('params').get(distribution_function+"_link")
    elastic_net_penalty = algo_settings.get('params').get('penalty')[0]
    l1_ratio = algo_settings.get('params').get('l1_ratio')[0]
    preprocessing = model_details.get_preprocessing_settings().get('per_feature')
    features = preprocessing.keys()


    features_dict = {}
    for feature in features:
        feature_settings = preprocessing.get(feature)
        choose_base_level = feature_settings.get('category_handling') and not ("series.mode()[0]" in feature_settings.get('customHandlingCode'))
        base_level = None
        if choose_base_level:
            pattern = r'self\.mode_column\s*=\s*["\']([^"\']+)["\']'
            # Search for the pattern in the code string
            match = re.search(pattern, feature_settings.get('customHandlingCode'))
            # Extract and print the matched value
            if match:
                base_level = match.group(1)
        features_dict[feature] = {
            "role": feature_settings.get('role'),
             'type': feature_settings.get('type'),
            "handling" : feature_settings.get('numerical_handling') or feature_settings.get('category_handling'),
            "chooseBaseLevel": choose_base_level,
            "baseLevel": base_level

        }
        if feature == exposure_column:
            features_dict[feature]["role"]=="Exposure"
        if features_dict[feature]["role"]=="TARGET":
            features_dict[feature]["role"]=="Target"
            target_column = feature
    setup_params = {
        "target_column": target_column,
        "exposure_column":exposure_column,
        "distribution_function": distribution_function.title(),
        "link_function":link_function.title(),
        "elastic_net_penalty": elastic_net_penalty,
        "l1_ratio": l1_ratio,
        "params": features_dict
    }
    current_app.logger.info(f"Returning setup params {setup_params}")
    return jsonify(setup_params)
    #except:
    #    setup_params = {
    #        "target_column": None,
    #        "exposure_column":None,
    #        "distribution_function": None,
    #        "link_function":None,
    #        "params": None
    #    }
    #    current_app.logger.info(f"Failed setup: Returning setup params {setup_params}")
    #    return jsonify(setup_params)




@fetch_api.route("/variables", methods=["POST"])
def get_variables():
    if is_local:
        return jsonify(dummy_variables)
    request_json = request.get_json()
    full_model_id = request_json["id"]
    try:
        loading_thread.join()
        variables = model_cache[full_model_id].get('features')
        print(f"Model cache for{full_model_id} is {model_cache[full_model_id]}")
        print(variables)
        if variables is None:
            raise ValueError("variables returned None.")
        
    except ValueError as e:
        current_app.logger.error(f"Validation Error: {e}")
        return jsonify({"error": e})        
    except Exception as e:
        current_app.logger.error(f"An error occurred: {e}")
    
    return jsonify(variables)
# local dev
    # return jsonify(dummy_variables)



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
        model_handler.update_active_version()
        lift_chart = model_handler.get_lift_chart(nb_bins)
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
    predicted_base = model_handler.get_predicted_and_base_feature(feature, nb_bins)
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
    if is_local:
        df = pd.DataFrame({'variable': ['VehBrand', 'VehBrand', 'VehBrand', 'VehPower', 'VehPower'], 
                       'value': ['B1', 'B10', 'B12', 'Diesel', 'Regular'], 
                       'coefficient': [0, 0.5, 0.32, 0, 0.0234],
                       'standard_error': [0, 1.23, 1.74, 0, 0.9],
                       'standard_error_pct': [0, 1.23, 1.74, 0, 0.9],
                        'weight': [234, 87, 73, 122, 90], 
                        'weight_pct': [60, 20, 20, 65, 35], 
                        'relativity': [1, 1.23, 1.077, 1, 0.98]})
        return jsonify(df.to_dict('records'))
    print("variable level stats")
    loading_thread.join()
    request_json = request.get_json()
    full_model_id = request_json["id"]
    
    current_app.logger.info(f"Model ID received: {full_model_id}")


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
        print(f"Returned local dummy metrics in {response_time} seconds.")
        return jsonify(dummy_model_metrics)
    
    loading_thread.join()
    request_json = request.get_json()
    print(request_json)
    
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


@fetch_api.route("/train_model", methods=["POST"])
def train_model():
    # Log the receipt of a new training request
    request_json = request.get_json()
    current_app.logger.info(f"Received a model training request: {request_json}")
    if is_local:
        import time
        time.sleep(5)
        return jsonify({'message': 'Model training initiated successfully.'}), 200
    global global_DkuMLTask, model_cache, model_deployer, model_handler

    try: 
        web_app_config = get_webapp_config()
        input_dataset = web_app_config.get("training_dataset_string")
        code_env_string = web_app_config.get("code_env_string")
        target_column = web_app_config.get("target_column")
        prediction_type = web_app_config.get("prediction_type")
        
    except:
        input_dataset = "claim_train"
        code_env_string="py39_sol"

        
    current_app.logger.info(f"Training Dataset name selected is: {input_dataset}") 
    
    distribution_function = request_json.get('model_parameters', {}).get('distribution_function')
    link_function = request_json.get('model_parameters', {}).get('link_function')
    elastic_net_penalty = request_json.get('model_parameters', {}).get('elastic_net_penalty')
    l1_ratio = request_json.get('model_parameters', {}).get('l1_ratio')
    model_name_string = request_json.get('model_parameters', {}).get('model_name', None)
    variables = request_json.get('variables')
    policy = web_app_config.get("policy")
    test_dataset_string = web_app_config.get("test_dataset_string")

    current_app.logger.debug(f"Parameters received - Dataset: {input_dataset}, Distribution Function: {distribution_function}, Link Function: {link_function}, Elastic Net Penalty: {elastic_net_penalty}, L1 Ratio: {l1_ratio}, Variables: {variables}")
    params = {
        "input_dataset": input_dataset,
        "distribution_function": distribution_function,
        "link_function": link_function,
        "elastic_net_penalty": elastic_net_penalty,
        "l1_ratio": l1_ratio,
        "variables": variables,
    }
    
    missing_params = [key for key, value in params.items() if value is None]
    if missing_params:
        missing_str = ", ".join(missing_params)
        current_app.logger.error(f"Missing parameters in the request: {missing_str}")
        return jsonify({'error': f'Missing parameters: {missing_str}'}), 400

    try:
        if not global_DkuMLTask:
            current_app.logger.debug("First time training a model, creating global_DkuMLTask")
            global_DkuMLTask = DataikuMLTask(input_dataset, prediction_type, policy, test_dataset_string)
            global_DkuMLTask.create_inital_ml_task(target_column)# defaults to target set in web app settings, this is overriden
            
        global_DkuMLTask.update_parameters(distribution_function, link_function, elastic_net_penalty, l1_ratio, variables)
        global_DkuMLTask.create_visual_ml_task()
        current_app.logger.debug("Visual ML task created successfully")

        global_DkuMLTask.enable_glm_algorithm()
        current_app.logger.debug("GLM algorithm enabled successfully")

        settings = global_DkuMLTask.test_settings()
        settings_new = global_DkuMLTask.configure_variables()
        current_app.logger.debug("Model settings configured successfully")

        model_details = global_DkuMLTask.train_model(code_env_string=code_env_string, session_name=model_name_string)
        current_app.logger.debug(f"Model model_details are {model_details}")
        saved_model_id = model_details.get("savedModelId")
        
        current_app.logger.info("Model training initiated successfully")
        loading_thread.join()
        
        if not model_cache:
            model_deployer = ModelDeployer(global_DkuMLTask.mltask, saved_model_id)
            model_handler = ModelHandler(saved_model_id, data_handler)
            model_cache = setup_model_cache(global_DkuMLTask.mltask, model_deployer, model_handler)
        
        model_cache = update_model_cache(global_DkuMLTask.mltask, model_cache, model_handler)
            

        
        return jsonify({'message': 'Model training completed successfully.'}), 200
    except Exception as e:
        current_app.logger.exception(f"An error occurred during model training {e}")
        return jsonify({'error': str(e)}), 500


def np_encode(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    return obj

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
