from backend.dataiku_api import dataiku_api
from logging.config import dictConfig
import os
import pandas as pd
# Replace by your default project key that you are working on in dev
DEFAULT_PROJECT_KEY = "SOL_CLAIM_MODELING"

# TODO : Add dip_home to a .env file
CONFIG = {
    # put your webapp desired config
    "webapp_config": {
        "model_id": "aHJZVrBQ",
    },
    "default_project_key": DEFAULT_PROJECT_KEY,
    "training_dataset_string": "claim_train",
}

os.environ["DKU_CURRENT_PROJECT_KEY"] = CONFIG.get("default_project_key")


def get_setup_for_dataiku_client():
    return {
        "webapp_config": CONFIG.get("webapp_config"),
        "default_project_key": CONFIG.get("default_project_key"),
        "training_dataset_string": CONFIG.get("claim_train")
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

    
dummy_models = [{"id": "model_1", "name": "GLM 1"}, {"id": "model_2", "name": "GLM 2"}]

dummy_variables = [{'variable': 'Variable1', 'isInModel': True, 'variableType': 'categorical'},
                    {'variable': 'Variable2', 'isInModel': False, 'variableType': 'numeric'}]

dummy_df_data = pd.DataFrame({
            'definingVariable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
            'Category': ['January', 'February', 'March', 'April', 10, 20, 30, 40],
            'Value': [0.2, 0.05, 0.3, 0.15, 0.4, 0.5, 0.6, 0.4],
            'observedAverage': [0.4, 0.5, 0.6, 0.4, 0.2, 0.05, 0.3, 0.15],
            'fittedAverage': [0.4, 0.7, 0.9, 0.8, 0.4, 0.5, 0.6, 0.4],
            'baseLevelPrediction': [0.5, 0.55, 0.6, 0.7, 0.5, 0.5, 0.4, 0.45]
        })

dummy_lift_data = pd.DataFrame({
            'Category': ['0.1', '0.15', '0.2', '0.3', '0.4', '0.6', '0.8', '1'],
            'Value': [100, 103, 101, 98, 100, 100, 101, 102],
            'observedAverage': [0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1],
            'fittedAverage': [0.12, 0.16, 0.19, 0.32, 0.37, 0.55, 0.83, 1.02]
        })

dummy_get_updated_data  = pd.DataFrame({
            'definingVariable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
            'Category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
            'inModel': [True, True, True, True, False, False, False, False],
            'Value': [0.2, 0.05, 0.3, 0.15, 0.4, 0.5, 0.6, 0.4],
            'observedAverage': [0.4, 0.5, 0.6, 0.4, 0.2, 0.05, 0.3, 0.15],
            'fittedAverage': [0.4, 0.7, 0.9, 0.8, 0.4, 0.5, 0.6, 0.4],
            'baseLevelPrediction': [0.5, 0.55, 0.6, 0.7, 0.5, 0.5, 0.4, 0.45]
        })

dummy_relativites= pd.DataFrame({'variable': ['Variable1','Variable1','Variable1','Variable1', 'Variable2','Variable2','Variable2','Variable2'],
                        'category': ['January', 'February', 'March', 'April','January', 'February', 'March', 'April'],
                        'relativity': [1.0, 1.087324, 0.98091882, 0.7929717, 1.0, 0.992374, 1.19274, 1.052333]})

dummy_model_metrics ={
        "models": {
            "Model_1": {
            "AIC": 100,
            "BIC": 120,
            "Deviance": 5.5
            },
            "Model_2": {
            "AIC": 95,
            "BIC": 110,
            "Deviance": 5.0
            }
        }
        }

def get_dummy_model_comparison_data():
    df = pd.DataFrame()
    df['variable_values'] = [0,10,20,30,40,50,60,70,80,90,100]
    df['model_1_claim_frequency'] =  np.random.uniform(50, 60, size=11)
    df['model_2_claim_frequency'] =  np.random.uniform(45, 55, size=11)
    df['observed_average'] =  np.random.uniform(15, 30, size=11)
    df['exposure'] = np.random.uniform(0, 100, size=11)
    return df