from backend.dataiku_api import dataiku_api
from logging.config import dictConfig
import os

# Replace by your default project key that you are working on in dev
DEFAULT_PROJECT_KEY = "SOL_CLAIM_MODELING"

# TODO : Add dip_home to a .env file
CONFIG = {
    # put your webapp desired config
    "webapp_config": {
        "model_id": "aHJZVrBQ",
    },
    "default_project_key": DEFAULT_PROJECT_KEY,
}

os.environ["DKU_CURRENT_PROJECT_KEY"] = CONFIG.get("default_project_key")


def get_setup_for_dataiku_client():
    return {
        "webapp_config": CONFIG.get("webapp_config"),
        "default_project_key": CONFIG.get("default_project_key"),
    }


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


def setup_dataiku_client():
    dataiku_setup = get_setup_for_dataiku_client()
    dataiku_api.setup(**dataiku_setup)
