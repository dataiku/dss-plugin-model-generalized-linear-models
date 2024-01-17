from backend.utils.dataiku_api import dataiku_api
from logging.config import dictConfig
import os

# Replace by your default project key that you are working on in dev
DEFAULT_PROJECT_KEY = "DATAIKUDOC"
LOGGING_DATASET = "pg_sql_logs"

# TODO : Add dip_home to a .env file
CONFIG = {
    # put your webapp desired config
    "webapp_config": {
        "web_app_title": "Ask directly questions to your document corpus",
        "web_app_subheading": "Answers are sourced from the processed documents, delivered in natural language and accompanied by the most relevant references.",
        "example_question_1": "What are the primary causes of the recent increase in global temperatures?",
        "example_question_2": "How does quantum computing differ from classical computing in terms of processing information?",
        "example_question_3": "Whats the most popular language globally?",
        "primer_prompt": "Act like a technical assistant for a team of DataScientists and Software Engineers",
        "llm_id": "openai:bs-openai:gpt-4",
        "language": "en",
        "memory_token_limit": 32768,
        "log_auth_info": True,
        "logging_dataset": LOGGING_DATASET,
        "feedback_positive_choices": [
            "Comprehensive",
            "To the point",
        ],
        "feedback_negative_choices": ["Incoherent", "Incorrect", "Absurd"],
        "knowledge_bank_id": None,
        "knowledge_retrieval_k": 3,
        "knowledge_retrieval_use_mmr": False,
        "knowledge_retrieval_mmr_k": 20,
        "knowledge_retrieval_mmr_diversity": 0.25,
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
