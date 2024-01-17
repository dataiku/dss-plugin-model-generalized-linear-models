import json
from flask import request, g
from backend.utils.dataiku_api import dataiku_api
from model_assist.logging import logger
import numpy as np


def return_ok(data={}):
    def convert_int64(obj):
        if isinstance(obj, np.int64):
            return int(obj)
        raise TypeError

    return json.dumps({"status": "ok", "data": data}, default=convert_int64)


def return_ko(message=""):
    return json.dumps({"status": "ko", "message": message})


def before_request():
    try:
        request_headers = dict(request.headers)
        auth_info_browser = dataiku_api.client.get_auth_info_from_browser_headers(
            request_headers
        )
        g.authIdentifier = auth_info_browser["authIdentifier"]
    except Exception as e:
        logger.warn("Authentication details extraction failed")
        g.authIdentifier = "unknown"
