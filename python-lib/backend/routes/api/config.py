from flask import Blueprint, Response
from typing import Dict, List, Union, Any
from backend.utils.dataiku_api import dataiku_api
from backend.utils.knowledge_filters import get_current_filter_config, get_knowledge_bank_name
from ..utils import return_ok
from model_assist.logging import logger

config_blueprint = Blueprint("config", __name__, url_prefix="/config")


def format_feedback_choices(choices: List[Any]):
    choices_final = []
    for choice in choices:
        try:
            choices_final.append(str(choice))
        except Exception as e:
            logger.warning("choice can't be parsed to str")
    return choices_final


@config_blueprint.route("/get_ui_setup", methods=["GET"])
def get_ui_setup() -> Response:
    """
    Fetches the configuration settings for UI setup from Dataiku and returns them.

    Returns:
        Response: A Flask response object containing the UI setup data.
    """

    config: Dict[str, str] = dataiku_api.webapp_config
    examples: List[str] = [
        config.get("example_question_1"),
        config.get("example_question_2"),
        config.get("example_question_3"),
    ]
    title: str = config.get("web_app_title")
    subtitle: str = config.get("web_app_subheading")
    lang: str = config.get("language", "en")
    placeholder: str = config.get("web_app_input_placeholder", "")
    feedback_positive_choices: List[str] = format_feedback_choices(
        config.get("feedback_positive_choices", [])
    )
    feedback_negative_choices: List[str] = format_feedback_choices(
        config.get("feedback_negative_choices", [])
    )
    filters_config = get_current_filter_config()
    knowledge_bank_id = config.get("knowledge_bank_id", None)

    knowledge_bank_name = get_knowledge_bank_name(knowledge_bank_id)

    result: Dict[str, Union[str, List[str]]] = {
        "examples": examples,
        "title": title,
        "subtitle": subtitle,
        "language": lang,
        "input_placeholder": placeholder,
        "project": dataiku_api.default_project_key,
        "feedback_negative_choices": feedback_negative_choices,
        "feedback_positive_choices": feedback_positive_choices,
        "filters_config": filters_config,
        "knowledge_bank": {"knowledge_bank_id": knowledge_bank_id, "knowledge_bank_name": knowledge_bank_name} if knowledge_bank_id else None
    }
    return return_ok(data=result)
