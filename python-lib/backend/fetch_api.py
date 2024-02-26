from flask import Blueprint, jsonify, request
import pandas as pd
from glm_handler.service import glm_handler

fetch_api = Blueprint("fetch_api", __name__, url_prefix="/api")

predicted_base = glm_handler.model_handler.get_predicted_and_base()
relativities = glm_handler.model_handler.relativities_df

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
    print(variables)
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

@fetch_api.route("/update_bins", methods=["POST"])
def get_updated_data():
    request_json = request.get_json()
    print(request_json)
    feature = request_json["feature"]
    nb_bins = request_json["nbBin"]
    predicted_base = glm_handler.model_handler.get_predicted_and_base_feature(feature, nb_bins)
    df = predicted_base.copy()
    df.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
    return jsonify(df.to_dict('records'))
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