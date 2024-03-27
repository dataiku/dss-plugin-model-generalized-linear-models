from flask import Blueprint, jsonify, request
import pandas as pd
from dku_config.dku_model_trainer import DataikuMLTask
from glm_handler.service import glm_handler
import traceback
fetch_api = Blueprint("fetch_api", __name__, url_prefix="/api")
import dataiku
import logging
from dataiku.customwebapp import get_webapp_config
predicted_base = glm_handler.model_handler.get_predicted_and_base()
relativities = glm_handler.model_handler.relativities_df

@fetch_api.route("/train_model", methods=["POST"])
def train_model():
    # Log the receipt of a new training request
    
    
    request_json = request.get_json()
    logging.info(f"Received a model training request: {request_json}")
    try: 
        web_app_config = get_webapp_config()
        input_dataset = web_app_config.get("training_dataset_string")
        code_env_string = web_app_config.get("code_env_string")
    except:
        input_dataset = "claim_train"
        code_env_string="py39_sol"
    logging.info(f"Training Dataset name selected is: {input_dataset}") 
    distribution_function = request_json.get('model_parameters', {}).get('distribution_function')
    link_function = request_json.get('model_parameters', {}).get('link_function')
    model_name_string = request_json.get('model_parameters', {}).get('model_name', None)
    variables = request_json.get('variables')

    # Log the received parameters for debugging
    logging.debug(f"Parameters received - Dataset: {input_dataset}, Distribution Function: {distribution_function}, Link Function: {link_function}, Variables: {variables}")

    if not all([input_dataset, distribution_function, link_function, variables]):
        logging.error("Missing parameters in the request")
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        DkuMLTask = DataikuMLTask(input_dataset, distribution_function, link_function, variables)
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
    
#     try:
#         request_json = request.get_json()
#         if request_json is None:
#             raise ValueError("No JSON payload found in the request")

#         # Debug: Print the JSON content
#         print(request_json)

#         # Your logic here
#         model_name = ['glm_model1.4']
#         return jsonify(model_name)


@fetch_api.route("/models", methods=["GET"])
def get_models():
    versions = glm_handler.model_handler.get_model_versions()
    models = [{'id': k, 'name': v} for k,v in versions.items()]
    return jsonify(models)
    models = [{"id": "model_1", "name": "GLM 1"}, {"id": "model_2", "name": "GLM 2"}]
    return jsonify(models)

@fetch_api.route("/variables", methods=["POST"])
def get_variables():
    request_json = request.get_json()
    model = request_json["id"]
    glm_handler.model_handler.switch_model(model)
    variables = glm_handler.model_handler.get_features()
    return jsonify(variables)
    if model == 'model_1':
        variables = [{'variable': 'Variable1', 'isInModel': True, 'variableType': 'categorical'},
                    {'variable': 'Variable2', 'isInModel': False, 'variableType': 'numeric'}]
    else:
        variables = [{'variable': 'Variable3', 'isInModel': False, 'variableType': 'categorical'},
                    {'variable': 'Variable4', 'isInModel': True, 'variableType': 'numeric'}]
    return jsonify(variables)


@fetch_api.route("/data", methods=["POST"])
def get_data():
    request_json = request.get_json()
    model = request_json["id"]
    df = predicted_base.copy()
    df.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
    return jsonify(df.to_dict('records'))
    if model == 'model_1':
        df = pd.DataFrame({
            'definingVariable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
            'Category': ['January', 'February', 'March', 'April', 10, 20, 30, 40],
            'Value': [0.2, 0.05, 0.3, 0.15, 0.4, 0.5, 0.6, 0.4],
            'observedAverage': [0.4, 0.5, 0.6, 0.4, 0.2, 0.05, 0.3, 0.15],
            'fittedAverage': [0.4, 0.7, 0.9, 0.8, 0.4, 0.5, 0.6, 0.4],
            'baseLevelPrediction': [0.5, 0.55, 0.6, 0.7, 0.5, 0.5, 0.4, 0.45]
        })
    else:
        df = pd.DataFrame({
            'definingVariable': ['Variable3','Variable3','Variable3','Variable3', 'Variable4','Variable4','Variable4','Variable4'],
            'Category': ['January', 'February', 'March', 'April', 10, 20, 30, 40],
            'Value': [0.2, 0.5, 0.35, 0.15, 0.4, 0.5, 0.3, 0.4],
            'observedAverage': [0.4, 0.15, 0.6, 0.4, 0.22, 0.05, 0.23, 0.15],
            'fittedAverage': [0.4, 0.7, 0.39, 0.8, 0.4, 0.5, 0.86, 0.24],
            'baseLevelPrediction': [0.5, 0.5, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7]
        })
    return jsonify(df.to_dict('records'))

@fetch_api.route("/lift_data", methods=["POST"])
def get_lift_data():
    request_json = request.get_json()
    print(request_json)
    model = request_json["id"]
    lift_chart = glm_handler.model_handler.get_lift_chart(8)
    df = lift_chart.copy()
    print(df)
    df.columns = ['Category', 'Value', 'observedAverage', 'fittedAverage']
    return jsonify(df.to_dict('records'))
    if model == 'model_1':
        df = pd.DataFrame({
            'Category': ['0.1', '0.15', '0.2', '0.3', '0.4', '0.6', '0.8', '1'],
            'Value': [100, 103, 101, 98, 100, 100, 101, 102],
            'observedAverage': [0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1],
            'fittedAverage': [0.12, 0.16, 0.19, 0.32, 0.37, 0.55, 0.83, 1.02]
        })
    else:
        df = pd.DataFrame({
            'Category': ['0.1', '0.15', '0.22', '0.3', '0.45', '0.6', '0.8', '1'],
            'Value': [100, 103, 101, 100, 101, 100, 101, 102],
            'observedAverage': [0.1, 0.15, 0.22, 0.3, 0.45, 0.6, 0.8, 1],
            'fittedAverage': [0.12, 0.16, 0.23, 0.32, 0.37, 0.62, 0.83, 1.02]
        })
    return jsonify(df.to_dict('records'))


@fetch_api.route("/update_bins", methods=["POST"])
def get_updated_data():
    request_json = request.get_json()
    print(request_json)
    feature = request_json["feature"]
    nb_bins = request_json["nbBin"]
    # predicted_base = glm_handler.model_handler.get_predicted_and_base_feature(feature, nb_bins)
    # df = predicted_base.copy()
    # df.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
    # return jsonify(df.to_dict('records'))
    if True:
        df = pd.DataFrame({
            'definingVariable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
            'Category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
            'inModel': [True, True, True, True, False, False, False, False],
            'Value': [0.2, 0.05, 0.3, 0.15, 0.4, 0.5, 0.6, 0.4],
            'observedAverage': [0.4, 0.5, 0.6, 0.4, 0.2, 0.05, 0.3, 0.15],
            'fittedAverage': [0.4, 0.7, 0.9, 0.8, 0.4, 0.5, 0.6, 0.4],
            'baseLevelPrediction': [0.5, 0.55, 0.6, 0.7, 0.5, 0.5, 0.4, 0.45]
        })
    else:
        df = pd.DataFrame({
            'definingVariable': ['Variable3','Variable3','Variable3','Variable3', 'Variable4','Variable4','Variable4','Variable4'],
            'Category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
            'inModel': [False, False, False, False, True, True, True, True],
            'Value': [0.2, 0.5, 0.35, 0.15, 0.4, 0.5, 0.3, 0.4],
            'observedAverage': [0.4, 0.15, 0.6, 0.4, 0.22, 0.05, 0.23, 0.15],
            'fittedAverage': [0.4, 0.7, 0.39, 0.8, 0.4, 0.5, 0.86, 0.24],
            'baseLevelPrediction': [0.5, 0.5, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7]
        })
    return jsonify(df.to_dict('records'))


@fetch_api.route("/relativities", methods=["POST"])
def get_relativities():
    request_json = request.get_json()
    model = request_json["id"]
    df = relativities
    df.columns = ['variable', 'category', 'relativity']
    return jsonify(df.to_dict('records'))
    if model == 'model_1':
        df = pd.DataFrame({'variable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
                        'category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
                        'relativity': [1.0, 1.087324, 0.98091882, 0.7929717, 1.0, 0.992374, 1.19274, 1.052333]})
    else:
        df = pd.DataFrame({'variable': ['Variable3','Variable3','Variable3','Variable3', 'Variable4','Variable4','Variable4','Variable4'],
                        'category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
                        'relativity': [1.0, 1.08723155, 0.9844522, 0.79251098, 1.0, 0.9951252, 1.10971, 1.0542428]})
    return jsonify(df.to_dict('records'))


@fetch_api.route("/get_project_dataset", methods=["GET"])
def get_project_dataset():
    try: 
        web_app_config = get_webapp_config()
        dataset_name = web_app_config.get("training_dataset_string")
    except:
        dataset_name = "claim_train"
    logging.info(f"Training Dataset name selected is: {dataset_name}")
    return jsonify(dataset_name)

    # client = dataiku.api_client()
    # project = client.get_default_project()
    # datasets = []
    # for i in project.list_datasets():
    #     datasets.append(i.name)
    # return jsonify(datasets)
    
#     datasets = ['Dataset1', 'Dataset2', 'Dataset3']
#     return jsonify(datasets)


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

        # Assuming you're using Dataiku's Python client to fetch dataset columns
        cols_dict = dataiku.Dataset(dataset_name).get_config().get('schema').get('columns')
        column_names = [column['name'] for column in cols_dict]

        # Log the successfully retrieved column names
        logging.info(f"Successfully retrieved column names for dataset '{dataset_name}': {column_names}")

        return jsonify(column_names)
    except KeyError as e:
        # Log an error message if the dataset name is not provided in the request
        logging.error(f"Missing key in request: {e}")
        return jsonify({'error': f'Missing key in request: {e}'}), 400
    except Exception as e:
        # Log any other errors that occur during the process
        logging.exception(f"Error retrieving columns for dataset '{dataset_name}': {e}")
        return jsonify({'error': str(e)}), 500


#     colum_names = ['column1', 'column2', 'column3', 'column4','column5']
#     return jsonify(colum_names)