import json
import os

import requests
import sqlalchemy
# Flask
from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

from audio import text_to_audio
from db import run_query
from prompts import get_initial_prompt

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


@app.route("/example")
def example():
    """Get example"""
    query = "SELECT name FROM ratings"
    results = run_query(query)
    results = [tuple(row) for row in results]
    return jsonify(results)


@app.route("/v1/stories/", methods=("GET", "POST"))
def stories():
    """Get and post story"""

    output = None
    if request.method == "POST":
        # Get input from user
        input = request.form["input"]
        # Form prompt with input
        prompt = get_initial_prompt(input)
        # Call LLM and generate output
        output = f"Output of LLM with..."

        # Store in DB in an async manner
        # query = "INSERT ..."
        # run_query()
    else:
        # Get first story
        query = "SELECT initial_prompt FROM story WHERE id = '1'"
        results = run_query(query)
        if len(results) > 0:
            output = tuple(results[0])[0]

    # Convert to audio
    local_audio_path = text_to_audio(output)
    # Save in storage
    
    return "Hello"


@app.route("/v1/story/<story_id>/branch/<branch_id>/", methods=("GET", "POST"))
def branches(story_id, branch_id):

    if request.method == "POST":
        # Get input from user: either positive or negative
        status = request.form["status"]
        # Form prompt with input
        prompt = f"Create a story with {input}"
        # Call LLM and generate output
        llm_output = f"Output of LLM with {prompt}"
        # Store in DB
        query = "INSERT ..."

    return ""