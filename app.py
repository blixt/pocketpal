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
from llm import openai_prompt
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
def generate_children_audio(story_id, branch_id):
    """
    - Check if story exists
    - Check if branch exists
    - If story or branch does not exist fail
    - Check if children exist
    - If they don't exist, we create them: concatenate stories from ancestors
    - status pending
    - generate positive and negative audios
    - status ok
    """

    # Check if story exists
    query = f"""SELECT EXISTS (
            SELECT 1 
            FROM stories 
            WHERE story_id = '{story_id}'
        )
    """
    results = run_query(query)
    response = tuple(results[0])[0]
    if not response: # story does not exist
        raise Exception(f"Story {story_id} does not exist!")
    # Check if branch exists
    query = f"""SELECT EXISTS (
            SELECT 1 
            FROM branches 
            WHERE branch_id = '{branch_id}'
        )
    """
    results = run_query(query)
    response = tuple(results[0])[0]
    if not response: # branch does not exist
        raise Exception(f"Branch {branch_id} does not exist!")
    # Check if positive child exists
    query = f"""
        SELECT EXISTS (
            SELECT 1 
            FROM branches 
            WHERE previous_branch_id = '{branch_id}' 
            AND sentiment = 'positive'
            AND (status <> 'done' OR status <> 'generating')
        )
    """
    results = run_query(query)
    response = tuple(results[0])[0]
    print(response)
    # if not response: # children does not exist
        # Mark as in generation
        # new_branch_id = 2
        # query = f"""
        #     INSERT INTO branches 
        #     (
        #         branch_id, story_id, previous_branch_id, status, sentiment, 
        #         audio_url, paragraph, positive_branch_id, negative_branch_id
        #     ) VALUES
        #     (
        #         '{new_branch_id}', '{story_id}', '{branch_id}', 
        #         'generating', 'positive', NULL, NULL, NULL, NULL
        #     )
        # """
        # run_query(query)
        # Generate it!
    query = f"""
    SELECT paragraph 
    FROM branches 
    WHERE story_id = '{story_id}' AND branch_id = '{branch_id}'
    """
    results = run_query(query)
    # Get paragraph
    paragraph = tuple(results[0])[0]
    # Get sentiment prompt
    prompt = get_prompt(paragraph, "positive")
    # Call LLM
    output = openai_prompt(prompt)
    # To audio
    audio_url = f"audios/{story_id}_{branch_id}.mp3"
    text_to_audio(output, audio_url)

    import pdb; pdb.set_trace()
    # generate_child(status=positive)


    # Check if negative child exists
    query = f"""
        SELECT status 
        FROM branches 
        WHERE previous_branch_id = '{branch_id}' 
            AND sentiment = 'negative'
            AND status = 'done'
    """
    results = run_query(query)
    response = False if len(results) == 0 or tuple(results[0])[0] != "done" else True



    # Check if story exists?
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
def post_and_get_audio(story_id, branch_id):
    """Get and post story"""

    if request.method == "POST":
        # Get input from user: positive or negative
        status = request.form["status"]
        # Already present?
        if status == "positive":
            column_name = "positive_branch_id"
        else:
            column_name = "negative_branch_id"
        query = f"""
            SELECT audio_url 
            FROM branch 
            WHERE {column_name} = '{story_id}''
        """
        results = run_query(query)
        # if it exists: return it
        if len(results) > 0:
            audio_url = tuple(results[0])[0]
            return {
                "audio_url": audio_url
            }
        # otherwise: generate it
        prompt = get_prompt(status)
        story = "new story" # call_llm(prompt)
        # Convert to audio and save in storage
        audio_url = f"story_{story_id}_branch_{branch_id}.mp3"
        text_to_audio(story, audio_url)
        # Store in DB in an async manner
        query = "INSERT ..."
        run_query(query)

        return {
            "audio_url": audio_url
        }
        
        # Download audio for it to play
        return destination_blob_name
