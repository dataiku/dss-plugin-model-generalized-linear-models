from flask import Blueprint, request, g
from ..utils import return_ok, before_request
from .api_response_handler import APIResponseProcessor
from backend.utils.dataiku_api import dataiku_api
import dataiku
from model_assist.logging import logger
from flask import Blueprint, request, Response
from typing import Dict, Union, List, Any
from solutions.service import glm
from typing import Optional

answer_blueprint = Blueprint("answer", __name__, url_prefix="/answer")

@answer_blueprint.before_request
def before_answer_request():
    before_request()