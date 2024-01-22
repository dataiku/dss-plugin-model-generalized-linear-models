from flask import Blueprint, jsonify
import pandas as pd
from glm_handler.service import glm_handler

fetch_api = Blueprint("fetch_api", __name__, url_prefix="/")


@fetch_api.route("/hello", methods=["GET"])
def hello():
    return jsonify({"key": "hello"})

@fetch_api.route("/data", methods=["GET"])
def get_data():
    df = pd.DataFrame({
        'definingVariable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
        'Category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
        'Value': [0.2, 0.05, 0.3, 0.15, 0.4, 0.5, 0.6, 0.4],
        'observedAverage': [0.4, 0.5, 0.6, 0.4, 0.2, 0.05, 0.3, 0.15],
        'fittedAverage': [0.4, 0.7, 0.9, 0.8, 0.4, 0.5, 0.6, 0.4],

    })
    return jsonify(df.to_dict('records'))
