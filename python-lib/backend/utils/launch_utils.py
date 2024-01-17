from flask import Flask, g, request
from flask_cors import CORS
from backend.utils.dataiku_api import dataiku_api
from model_assist.logging import logger


def run_create_app(app: Flask):
    from backend.routes import api

    CORS(app)

    app.register_blueprint(api)
    return app
