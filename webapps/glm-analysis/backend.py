from backend.utils.launch_utils import run_create_app
from flask import Flask


def create_app():
    run_create_app(app)
    return app


create_app()
