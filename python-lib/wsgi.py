from flask import Flask
from backend.utils.launch_utils import run_create_app
from backend.local_config import setup_dataiku_client
import os 
from model_assist.logging import logger


def create_app():

    logger.info("Creating Flask Application")
    app = Flask(__name__)
    setup_dataiku_client()
    run_create_app(app)

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(host="127.0.0.1", port=5000, debug=True)
