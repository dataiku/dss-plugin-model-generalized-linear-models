from pathlib import Path
import json
import os
from backend.utils.dataiku_api import dataiku_api

def load_local_config():
    local_config_path = Path("config.local.json")
    if local_config_path.exists():
        with open(local_config_path, 'r') as local_config_file:
            return json.load(local_config_file)
    return None


def init_config():
    local_config = load_local_config()
    if local_config:
        os.environ["DKU_CURRENT_PROJECT_KEY"] = local_config.get("default_project_key")
        os.environ["DKU_CUSTOM_WEBAPP_CONFIG"] = json.dumps(local_config.get("webapp_config"))
        return local_config


def setup_dataiku_client():
    dataiku_setup = init_config()
    dataiku_api.setup(dataiku_setup, os.environ["DKU_CURRENT_PROJECT_KEY"])
