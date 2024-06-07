from flask import Flask
from dotenv import load_dotenv
import os
import logging
from backend.fetch_api import fetch_api
from webaiku.extension import WEBAIKU

#from backend.local_config import setup_dataiku_client



#setup_dataiku_client()

logger = logging.getLogger(__name__)

def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    logger.info("Creating Flask Application")

    WEBAIKU(app, "webapps/vue_template", int(os.getenv("VITE_API_PORT")))
    WEBAIKU.extend(app, [fetch_api])

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=int(os.getenv("VITE_API_PORT")), debug=True)
