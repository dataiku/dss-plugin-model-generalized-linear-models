from flask import Blueprint
from .answer import answer_blueprint
from .conversation import conversation_blueprint
from .config import config_blueprint


api = Blueprint("api", __name__, url_prefix="/api")

api.register_blueprint(answer_blueprint)
api.register_blueprint(conversation_blueprint)
api.register_blueprint(config_blueprint)
