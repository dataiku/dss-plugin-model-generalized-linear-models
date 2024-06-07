from flask import Flask
from dotenv import load_dotenv
import os
import logging
from backend.utils.extensions import setup_dataiku_client


logger = logging.getLogger(__name__)

def register_routes(app: Flask):
    from backend.fetch_api import fetch_api
    from webaiku.extension import WEBAIKU

    WEBAIKU(app, "webapps/vue_template", 5000)
    WEBAIKU.extend(app, [fetch_api])


def register_extensions():
    running_in_dss = os.getenv("DKU_CUSTOM_WEBAPP_CONFIG") is not None
    if not running_in_dss:
        setup_dataiku_client()


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    logger.info("Creating Flask Application")

    register_extensions()
    register_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
