import json
import os

import requests
# Flask
from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

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
    return render_template("index.html")


# Name
@app.route("/<name>")
def name(name):
    return f"Hello {name}!"
