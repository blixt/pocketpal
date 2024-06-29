import os

# Flask
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    Response,
    flash,
    redirect,
    url_for,
)
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import requests
import json


# APP
app = Flask(__name__)
app.config["SECRET_KEY"] = "this is my secret key!"
# Bootstrap
Bootstrap(app)
# Static path
uploads_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static", "uploads")


# LANDING
@app.route("/", methods=("GET", "POST"))
def index():
    return "Hello!"
