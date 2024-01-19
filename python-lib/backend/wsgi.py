from flask import Flask
from .fetch_api import fetch_api
from dotenv import load_dotenv
import os
#from backend.local_config import setup_dataiku_client

load_dotenv()

from webaiku.extension import WEBAIKU

#setup_dataiku_client()

app = Flask(__name__)
WEBAIKU(
    app, "webapps/vue_template", int(os.getenv("VITE_API_PORT"))
)



WEBAIKU.extend(app, [fetch_api])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("VITE_API_PORT")), debug=True)
