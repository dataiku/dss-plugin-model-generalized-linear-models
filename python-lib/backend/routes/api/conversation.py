from flask import Blueprint, request, g
from ..utils import return_ok, before_request
from model_assist.logging import logger

conversation_blueprint = Blueprint("conversation", __name__, url_prefix="/conversation")


@conversation_blueprint.before_request
def before_conversation_request():
    before_request()
