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
    # Check children!
    for sentiment in ["positive", "negative"]:
        # Check if `sentiment` child exists
        query = f"""
            SELECT EXISTS (
                SELECT 1 
                FROM branches 
                WHERE previous_branch_id = '{branch_id}' 
                AND sentiment = '{sentiment}'
                AND (status <> 'done' OR status <> 'generating')
            )
        """
        results = run_query(query)
        response = tuple(results[0])[0]
        if not response: # children does not exist
            # Insert new
            # TODO: use uuid b62
            new_branch_id = str(uuid.uuid4)
            # Mark as in generation
            query = f"""
                INSERT INTO branches 
                (
                    branch_id, story_id, previous_branch_id, status, 
                    sentiment, audio_url, paragraph, 
                ) VALUES
                (
                    '{new_branch_id}', '{story_id}', '{branch_id}', 'generating',
                    '{sentiment}', NULL, NULL
                )
            """
            run_query(query)
            # Generate it!
            # TODO: get paragraphs from all ancestors, not only from parent
            query = f"""
                SELECT paragraph 
                FROM branches 
                WHERE story_id = '{story_id}' AND branch_id = '{branch_id}'
            """
            results = run_query(query)
            # Get paragraph
            paragraph = tuple(results[0])[0]
            # Get sentiment prompt
            prompt = get_prompt(paragraph, sentiment)
            # Call LLM
            output = openai_prompt(prompt)
            # To audio
            audio_url = f"audios/{story_id}_{branch_id}.mp3"
            text_to_audio(output, audio_url)
            # Mark as done!
            query = f"""
                    UPDATE branches 
                    SET
                        status = 'done', 
                        audio_url = '{audio_url}',
                        paragraph = '{output}'
                    WHERE branch_id = '{new_branch_id}'
                """
            run_query(query)


# @app.route("/v1/story/<story_id>/branch/<branch_id>/", methods=("GET", "POST"))
# def post_and_get_audio(story_id, branch_id):
#     """Get and post story"""

#     if request.method == "POST":
#         # Get input from user: positive or negative
#         status = request.form["status"]
#         ...
