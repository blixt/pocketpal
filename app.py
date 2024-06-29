import json
import os
import uuid

import requests
import sqlalchemy
# Flask
from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

from audio import text_to_audio
from db import run_query
from prompts import get_prompt

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


@app.route("/v1/story/<story_id>/branch/<branch_id>/")
def get_audio(story_id, branch_id):
    """Get audio for any node"""

    # Already in DB?
    query = f"""
    SELECT audio_url 
    FROM branch 
    WHERE story_id = '{story_id}' AND id = '{branch_id}'
    """
    results = run_query(query)
    # if it exists, return it
    if len(results) > 0:
        audio_url = tuple(results[0])[0]
        return {
            "audio_url": audio_url
        }
    return {}


@app.route("/v1/story/<story_id>/branch/<branch_id>/", methods=("GET", "POST"))
def stories(story_id, branch_id):
    """Get and post story"""

    if request.method == "POST":
        # Get input from user: text, + or -
        input = request.form["input"]
        # Already in DB?
        query = """
        SELECT story 
        FROM story 
        WHERE id = '{story_id}'
        """
        results = run_query(query)
        if len(results) > 0:
            story = tuple(results[0])[0]
        else:
            prompt = get_prompt(input)
            story = "new story" # call_llm(prompt)
        # Store in DB in an async manner
        query = "INSERT ..."
        run_query(query)
        # Convert to audio and save in storage
        destination_blob_name = f"story_{story_id}_branch_{branch_id}.mp3"
        text_to_audio(story, destination_blob_name)
        # Download audio for it to play
        return destination_blob_name
