from flask import Blueprint, jsonify, request
import pandas as pd
from glm_handler.service import glm_handler

fetch_api = Blueprint("fetch_api", __name__, url_prefix="/api")

predicted_base = glm_handler.model_handler.get_predicted_and_base('ClaimNb', None)
relativities = glm_handler.model_handler.relativities_df

@fetch_api.route("/models", methods=["GET"])
def get_models():
    models = ["model_1", "model_2"]
    return jsonify(models)

@fetch_api.route("/data", methods=["POST"])
def get_data():
    request_json = request.get_json()
    model = request_json["id"]
    df = predicted_base
    df.columns = ['definingVariable', 'Category', 'observedAverage', 'fittedAverage', 'Value', 'baseLevelPrediction']
    return jsonify(df.to_dict('records'))
    if model == 'model_1':
        df = pd.DataFrame({
            'definingVariable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
            'Category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
            'Value': [0.2, 0.05, 0.3, 0.15, 0.4, 0.5, 0.6, 0.4],
            'observedAverage': [0.4, 0.5, 0.6, 0.4, 0.2, 0.05, 0.3, 0.15],
            'fittedAverage': [0.4, 0.7, 0.9, 0.8, 0.4, 0.5, 0.6, 0.4],
            'baseLevelPrediction': [0.5, 0.55, 0.6, 0.7, 0.5, 0.5, 0.4, 0.45]
        })
    else:
        df = pd.DataFrame({
            'definingVariable': ['Variable3','Variable3','Variable3','Variable3', 'Variable4','Variable4','Variable4','Variable4'],
            'Category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
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
                        'relativity': [1.0, 1.087, 0.98, 0.79, 1.0, 0.99, 1.1, 1.05]})
    else:
        df = pd.DataFrame({'variable': ['Variable3','Variable3','Variable3','Variable3', 'Variable4','Variable4','Variable4','Variable4'],
                        'category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
                        'relativity': [1.0, 1.087, 0.98, 0.79, 1.0, 0.99, 1.1, 1.05]})
    return jsonify(df.to_dict('records'))