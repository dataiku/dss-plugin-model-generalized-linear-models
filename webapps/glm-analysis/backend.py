from flask import Flask
from backend.fetch_api import fetch_api
from dotenv import load_dotenv
import os
load_dotenv()

from webaiku.extension import WEBAIKU

WEBAIKU(app, "resource/dist")
WEBAIKU.extend(app, [fetch_api])