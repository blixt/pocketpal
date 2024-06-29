import json
import os

import requests
import sqlalchemy
# Flask
from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

from db import get_query_results

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
@app.route("/hello/<name>")
def hello(name):
    return f"Hello {name}!"


# Name
@app.route("/ratings")
def ratings():
    query = "SELECT name FROM ratings"
    results = get_query_results(query)
    results = [tuple(row) for row in results]
    return jsonify(results)
