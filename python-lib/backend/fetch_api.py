from flask import Blueprint, jsonify, request, send_file
import pandas as pd
from glm_handler.dku_model_trainer import DataikuMLTask
from glm_handler.dku_model_handler import ModelHandler
from glm_handler.dku_model_deployer import ModelDeployer
from backend.api_utils import format_models
from backend.local_config import dummy_models, dummy_variables, dummy_df_data, dummy_lift_data

from io import BytesIO
import traceback
fetch_api = Blueprint("fetch_api", __name__, url_prefix="/api")
import dataiku
from dataiku.customwebapp import get_webapp_config
import numpy as np

client = dataiku.api_client()
project = client.get_default_project()
web_app_config = get_webapp_config()
saved_model_id = web_app_config.get("saved_model_id")
saved_model = project.get_saved_model(saved_model_id)
global_dku_mltask = saved_model.get_origin_ml_task()
model_deployer = ModelDeployer(global_dku_mltask, saved_model_id)
model_handler = ModelHandler(saved_model_id)

from backend.logging_settings import logger


@fetch_api.route("/models", methods=["GET"])
def get_models():
    if global_dku_mltask is None:
        return jsonify({'error': 'ML task not initialized'}), 500
    try:
        models = format_models(global_dku_mltask)
        return jsonify(models)
    except Exception as e:
        logging.exception("An error occurred while retrieving models")
        return jsonify({'error': str(e)}), 500
    return jsonify(models)
# For local dev
#     return jsonify(dummy_models)
     



@fetch_api.route("/variables", methods=["POST"])
def get_variables():
    request_json = request.get_json()
    full_model_id = request_json["id"]
    web_app_config = get_webapp_config()

    
    model_deployer.set_new_active_version(full_model_id)
    model_handler.update_active_version()
   
    
    try:
        predicted_base = model_handler.get_predicted_and_base()
        if predicted_base is None:
            raise ValueError("predicted_base returned None.")

        relativities = model_handler.get_relativities_df()
        if relativities is None:
            raise ValueError("relativities returned None.")

        variables = model_handler.get_features()
        if variables is None:
            raise ValueError("variables returned None.")

    except ValueError as e:
        logging.error(f"Validation Error: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    
    return jsonify(variables)
# local dev
#     return jsonify(dummy_variables)



@fetch_api.route("/data", methods=["POST"])
def get_data():
    try:
        logger.info("Received a new request for data prediction.")
        request_json = request.get_json()
        full_model_id = request_json["id"]
        
        logger.info(f"Model ID received: {full_model_id}")

        model_deployer.set_new_active_version(full_model_id)
        model_handler.update_active_version()
        logger.info(f"Model {full_model_id} is now the active version.")

        predicted_base = model_handler.get_predicted_and_base()
        predicted_base.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
        logger.info(f"Successfully generated predictions. Sample is {predicted_base.head()}")
        
        return jsonify(predicted_base.to_dict('records'))
#     local dev
    #     return jsonify(dummy_df_data.to_dict('records'))
    
    except Exception as e:
        logger.error(f"An error occurred while processing the request: {e}", exc_info=True)
        return jsonify({"error": "An error occurred during data processing."}), 500



@fetch_api.route("/lift_data", methods=["POST"])
def get_lift_data():
    logger.info("Received a new request for lift chart data.")
    request_json = request.get_json()
    print(request_json)
    full_model_id = request_json["id"]
    
    logger.info(f"Model ID received: {full_model_id}")

    model_deployer.set_new_active_version(full_model_id)
    model_handler.update_active_version()
    logger.info(f"Model {full_model_id} is now the active version.")
    
    
    lift_chart = model_handler.get_lift_chart(8)
    lift_chart.columns = ['Category', 'Value', 'observedAverage', 'fittedAverage']
    logger.info(f"Successfully generated predictions. Sample is {lift_chart.head()}")
    
    return jsonify(lift_chart.to_dict('records'))
#     local dev
#     return jsonify(dummy_lift_data.to_dict('records'))
     



# @fetch_api.route("/update_bins", methods=["POST"])
# def get_updated_data():
#     request_json = request.get_json()
#     print(request_json)
#     feature = request_json["feature"]
#     nb_bins = request_json["nbBin"]
#     predicted_base = glm_handler.model_handler.get_predicted_and_base_feature(feature, nb_bins)
#     df = predicted_base.copy()
#     df.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
#     return jsonify(df.to_dict('records'))
#     if True:
#         df = pd.DataFrame({
#             'definingVariable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
#             'Category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
#             'inModel': [True, True, True, True, False, False, False, False],
#             'Value': [0.2, 0.05, 0.3, 0.15, 0.4, 0.5, 0.6, 0.4],
#             'observedAverage': [0.4, 0.5, 0.6, 0.4, 0.2, 0.05, 0.3, 0.15],
#             'fittedAverage': [0.4, 0.7, 0.9, 0.8, 0.4, 0.5, 0.6, 0.4],
#             'baseLevelPrediction': [0.5, 0.55, 0.6, 0.7, 0.5, 0.5, 0.4, 0.45]
#         })
#     else:
#         df = pd.DataFrame({
#             'definingVariable': ['Variable3','Variable3','Variable3','Variable3', 'Variable4','Variable4','Variable4','Variable4'],
#             'Category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
#             'inModel': [False, False, False, False, True, True, True, True],
#             'Value': [0.2, 0.5, 0.35, 0.15, 0.4, 0.5, 0.3, 0.4],
#             'observedAverage': [0.4, 0.15, 0.6, 0.4, 0.22, 0.05, 0.23, 0.15],
#             'fittedAverage': [0.4, 0.7, 0.39, 0.8, 0.4, 0.5, 0.86, 0.24],
#             'baseLevelPrediction': [0.5, 0.5, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7]
#         })
#     return jsonify(df.to_dict('records'))


# @fetch_api.route("/relativities", methods=["POST"])
# def get_relativities():
#     request_json = request.get_json()
#     model = request_json["id"]
#     df = relativities
#     df.columns = ['variable', 'category', 'relativity']
#     return jsonify(df.to_dict('records'))
#     model="model_1"
#     if model == 'model_1':
#         df = pd.DataFrame({'variable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
#                         'category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
#                         'relativity': [1.0, 1.087324, 0.98091882, 0.7929717, 1.0, 0.992374, 1.19274, 1.052333]})
#     else:
#         df = pd.DataFrame({'variable': ['Variable3','Variable3','Variable3','Variable3', 'Variable4','Variable4','Variable4','Variable4'],
#                         'category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
#                         'relativity': [1.0, 1.08723155, 0.9844522, 0.79251098, 1.0, 0.9951252, 1.10971, 1.0542428]})
#     return jsonify(df.to_dict('records'))


# @fetch_api.route("/get_project_dataset", methods=["GET"])
# def get_project_dataset():
#     try: 
#         web_app_config = get_webapp_config()
#         dataset_name = web_app_config.get("training_dataset_string")
#     except:
#         dataset_name = "claim_train"
#     logging.info(f"Training Dataset name selected is: {dataset_name}")
#     return jsonify(dataset_name)

#     # client = dataiku.api_client()
#     # project = client.get_default_project()
#     # datasets = []
#     # for i in project.list_datasets():
#     #     datasets.append(i.name)
#     # return jsonify(datasets)
    
# #     datasets = ['Dataset1', 'Dataset2', 'Dataset3']
# #     return jsonify(datasets)




# @fetch_api.route("/get_model_comparison_data", methods=["POST"])
# def get_model_comparison_data():
    
    
    
#     request_json = request.get_json()
#     print(request_json)
#     model1, model2 = request_json["model1"], request_json["model2"]
    
    
#     glm_handler.model_handler.switch_model(model1)
#     model_1_lift_chart = glm_handler.model_handler.get_lift_chart(8)
    
#     model_1_lift_chart.columns = ['Category', 'variable_values', 'observedAverage', 'Model_1_fittedAverage']
    
    
#     glm_handler.model_handler.switch_model(model2)
#     model_2_lift_chart = glm_handler.model_handler.get_lift_chart(8)
    
  
#     model_2_lift_chart.columns = ['Category', 'variable_values', 'observedAverage', 'Model_2_fittedAverage']
    
#     merged_model_stats = pd.merge(model_1_lift_chart, model_2_lift_chart, 
#                              on=['observedAverage','Category', 'variable_values'], 
#                              how='outer')
    
#     merged_model_stats['exposure'] = 1
    
#     return jsonify(merged_model_stats.to_dict('records'))
    
    
    
#     # request_json = request.get_json()
#     # model = request_json["id"]
#     # df = relativities
#     # df.columns = ['variable', 'category', 'relativity']
#     # return jsonify(df.to_dict('records'))
# #     df = pd.DataFrame()
# #     df['variable_values'] = [0,10,20,30,40,50,60,70,80,90,100]
# #     df['model_1_claim_frequency'] =  np.random.uniform(50, 60, size=11)
# #     df['model_2_claim_frequency'] =  np.random.uniform(45, 55, size=11)
# #     df['observed_average'] =  np.random.uniform(15, 30, size=11)
# #     df['exposure'] = np.random.uniform(0, 100, size=11)
# #     return jsonify(df.to_dict('records'))

# @fetch_api.route("/get_model_metrics", methods=["POST"])
# def get_model_metrics():
#     # request_json = request.get_json()
#     # model = request_json["id"]
#     # df = relativities
#     # df.columns = ['variable', 'category', 'relativity']
#     # return jsonify(df.to_dict('records'))
#     json_data = {
#         "models": {
#             "Model_1": {
#             "AIC": 100,
#             "BIC": 120,
#             "Deviance": 5.5
#             },
#             "Model_2": {
#             "AIC": 95,
#             "BIC": 110,
#             "Deviance": 5.0
#             }
#         }
#         }

#     return jsonify(json_data)

# @fetch_api.route('/export_model', methods=['GET'])
# def export_model():
#     relativities_dict = glm_handler.model_handler.relativities
    
#     nb_col = (len(relativities_dict.keys()) - 1) * 3
#     variables = [col for col in relativities_dict.keys() if col != "base"]
#     variable_keys = {variable: list(relativities_dict[variable].keys()) for variable in variables}
#     max_len = max(len(variable_keys[variable]) for variable in variable_keys.keys())
    
#     csv_output = ",,\n"
#     csv_output += "Base,,{}\n".format(relativities_dict['base']['base'])
#     csv_output += ",,\n"
#     csv_output += ",,\n"
#     csv_output += ",,,".join(variables) + ",,\n"
#     csv_output += ",,\n"
#     csv_output += ",,,".join(variables) + ",,\n"
    
#     for i in range(max_len):
#         for variable in variables:
#             if i < len(variable_keys[variable]):
#                 value = variable_keys[variable][i]
#                 csv_output += "{},{},,".format(value, relativities_dict[variable][value])
#             else:
#                 csv_output += ",,,"
#         csv_output += "\n"
    
#     csv_data = csv_output.encode('utf-8')
    
#     #data = {'Name': ['John', 'Alice', 'Bob'], 'Age': [30, 25, 35]}
#     #df = pd.DataFrame(data)

#     # Convert DataFrame to CSV format
#     #csv_data = df.to_csv(index=False).encode('utf-8')

#     # Create an in-memory file-like object for CSV data
#     csv_io = BytesIO(csv_data)

#     # Serve the CSV file for download
#     return send_file(
#         csv_io,
#         mimetype='text/csv',
#         as_attachment=True,
#         download_name='model.csv'
#     )



@fetch_api.route("/train_model", methods=["POST"])
def train_model():
    # Log the receipt of a new training request
    global global_dku_mltask
    
    request_json = request.get_json()
    logging.info(f"Received a model training request: {request_json}")
    
    try: 
        web_app_config = get_webapp_config()
        input_dataset = web_app_config.get("training_dataset_string")
        code_env_string = web_app_config.get("code_env_string")
        saved_model_id = web_app_config.get("saved_model_id")
        
    except:
        input_dataset = "claim_train"
        code_env_string="py39_sol"
        
    logging.info(f"Training Dataset name selected is: {input_dataset}") 
    
    distribution_function = request_json.get('model_parameters', {}).get('distribution_function')
    link_function = request_json.get('model_parameters', {}).get('link_function')
    model_name_string = request_json.get('model_parameters', {}).get('model_name', None)
    variables = request_json.get('variables')

    logging.debug(f"Parameters received - Dataset: {input_dataset}, Distribution Function: {distribution_function}, Link Function: {link_function}, Variables: {variables}")
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
        logging.error(f"Missing parameters in the request: {missing_str}")
        return jsonify({'error': f'Missing parameters: {missing_str}'}), 400

    try:
        if global_dku_mltask:
            logger.info("Utilising an existing ML Task at the API")
            
            DkuMLTask = global_dku_mltask

        else: #First initialisation 
            logger.info("Initalising an new ML Task at the API")
            DkuMLTask = DataikuMLTask(input_dataset, saved_model_id)
            global_dku_mltask = DkuMLTask
            
        DkuMLTask.update_parameters(distribution_function, link_function, variables)
        DkuMLTask.create_visual_ml_task()
        logging.debug("Visual ML task created successfully")

        DkuMLTask.enable_glm_algorithm()
        logging.debug("GLM algorithm enabled successfully")

        settings = DkuMLTask.test_settings()
        settings_new = DkuMLTask.configure_variables()
        logging.debug("Model settings configured successfully")

        DkuMLTask.train_model(code_env_string=code_env_string, session_name=model_name_string)
        
        
        logging.info("Model training initiated successfully")
        
        return jsonify({'message': 'Model training initiated successfully.'}), 200
    except Exception as e:
        logging.exception("An error occurred during model training")
        return jsonify({'error': str(e)}), 500

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
            
        logging.info(f"Training Dataset name selected is: {dataset_name}")

        cols_dict = dataiku.Dataset(dataset_name).get_config().get('schema').get('columns')
        column_names = [column['name'] for column in cols_dict]

        logging.info(f"Successfully retrieved column names for dataset '{dataset_name}': {column_names}")

        return jsonify(column_names)
    
    except KeyError as e:
        logging.error(f"Missing key in request: {e}")
        return jsonify({'error': f'Missing key in request: {e}'}), 400
    
    except Exception as e:
        logging.exception(f"Error retrieving columns for dataset '{dataset_name}': {e}")
        return jsonify({'error': str(e)}), 500
