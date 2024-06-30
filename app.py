import json
import string
import random
from flask import Flask, render_template, abort, request, jsonify
from flask_bootstrap import Bootstrap
from audio import text_to_audio, get_full_url
from db import run_query, run_query_with_session, Session
from llm import openai_prompt
from prompts import get_continue_prompt, get_initial_prompt

app = Flask(__name__)
Bootstrap(app)


def base62(length):
    """
    Generate a random base62 string of the specified length.
    """
    base62_chars = string.ascii_letters + string.digits
    return "".join(random.choice(base62_chars) for _ in range(length))


# Entrypoint for visitors to the app
@app.route("/")
@app.route("/story/<story_id>")
def index(story_id=None):
    return render_template("index.html")


@app.route("/v1/story/", methods=["POST"])
def create_story():
    """Create a new story"""
    data = request.json
    story_premise = data.get("initial_prompt")

    # Generate content for initial branch
    story_info = json.loads(openai_prompt(get_initial_prompt(story_premise)))
    assert story_info["lang"]
    assert story_info["title"]
    assert story_info["description"]
    assert story_info["paragraph"]

    # Generate initial branch
    story_id = base62(10)
    initial_branch_id = base62(10)

    # Generate audio before the transaction
    audio_url = f"audios/{story_id}_{initial_branch_id}.mp3"
    text_to_audio(story_info["paragraph"], audio_url, story_info["lang"])

    # Create story and initial branch within a transaction
    with Session() as session:
        try:
            # Create story
            run_query_with_session(
                session,
                """
                INSERT INTO stories (story_id, initial_branch_id, title, description, initial_prompt, lang)
                VALUES (:story_id, :initial_branch_id, :title, :description, :initial_prompt, :lang)
                """,
                story_id=story_id,
                initial_branch_id=initial_branch_id,
                title=story_info["title"],
                description=story_info["description"],
                initial_prompt=story_premise,
                lang=story_info["lang"],
            )

            # Create initial branch
            run_query_with_session(
                session,
                """
                INSERT INTO branches 
                (branch_id, story_id, previous_branch_id, status, sentiment, audio_url, paragraph)
                VALUES (:branch_id, :story_id, NULL, 'done', 'initial_branch', :audio_url, :paragraph)
                """,
                branch_id=initial_branch_id,
                story_id=story_id,
                audio_url=audio_url,
                paragraph=story_info["paragraph"],
            )

            session.commit()
        except:
            session.rollback()
            raise

    return jsonify(
        {
            "id": story_id,
            "initial_branch_id": initial_branch_id,
            "title": story_info["title"],
            "description": story_info["description"],
            "initial_prompt": story_premise,
            "lang": story_info["lang"],
        }
    )


@app.route("/v1/story/<story_id>/")
def get_story(story_id):
    """Get story details"""
    story = run_query(
        """
        SELECT story_id, initial_branch_id, title, description, initial_prompt, lang
        FROM stories
        WHERE story_id = :story_id
        """,
        story_id=story_id,
    ).fetchone()

    if not story:
        abort(404, f"Story {story_id} does not exist!")

    return jsonify(
        {
            "id": story.story_id,
            "initial_branch_id": story.initial_branch_id,
            "title": story.title,
            "description": story.description,
            "initial_prompt": story.initial_prompt,
            "lang": story.lang,
        }
    )


@app.route("/v1/story/<story_id>/branches/<branch_id>/")
def get_branch(story_id, branch_id):
    """
    Get branch details and generate child branches if they don't exist.

    - Verify story and branch existence
    - Create child branches if they don't exist
    - Generate content for new branches
    - Create audio for new branches
    - Return branch details
    """

    # Check if story and branch exist
    story_and_branch_exist = run_query(
        """
        SELECT 
            (SELECT EXISTS (SELECT 1 FROM stories WHERE story_id = :story_id)) AS story_exists,
            (SELECT EXISTS (SELECT 1 FROM branches WHERE branch_id = :branch_id)) AS branch_exists
        """,
        story_id=story_id,
        branch_id=branch_id,
    ).fetchone()

    if not story_and_branch_exist.story_exists:
        abort(404, f"Story {story_id} does not exist!")
    if not story_and_branch_exist.branch_exists:
        abort(404, f"Branch {branch_id} does not exist!")

    # Get story language
    lang = run_query(
        """
        SELECT lang
        FROM stories
        WHERE story_id = :story_id
        """,
        story_id=story_id,
    ).scalar()

    # Check and create children branches
    for sentiment in ["positive", "negative"]:
        child_branch = run_query(
            """
            SELECT branch_id, status
            FROM branches 
            WHERE previous_branch_id = :branch_id 
            AND sentiment = :sentiment
            """,
            branch_id=branch_id,
            sentiment=sentiment,
        ).fetchone()

        if child_branch and child_branch.status != "failed":
            continue

        # Create new branch or update failed branch.
        # To reach a 0.01% chance of collision, you need approximately 13M items.
        new_branch_id = child_branch.branch_id if child_branch else base62(10)

        if not child_branch:
            run_query(
                """
                INSERT INTO branches 
                (branch_id, story_id, previous_branch_id, status, sentiment, audio_url, paragraph)
                VALUES (:new_branch_id, :story_id, :branch_id, 'generating', :sentiment, NULL, NULL)
                """,
                new_branch_id=new_branch_id,
                story_id=story_id,
                branch_id=branch_id,
                sentiment=sentiment,
            )

        # Generate content
        story_content = run_query(
            """
            WITH RECURSIVE branch_history AS (
                SELECT branch_id, previous_branch_id, paragraph, 1 AS depth
                FROM branches
                WHERE branch_id = :branch_id

                UNION ALL
                
                SELECT b.branch_id, b.previous_branch_id, b.paragraph, bh.depth + 1
                FROM branches b
                JOIN branch_history bh ON b.branch_id = bh.previous_branch_id
            )
            SELECT string_agg(paragraph, E'\n\n' ORDER BY depth DESC) AS full_story
            FROM branch_history
            WHERE paragraph IS NOT NULL;
            """,
            branch_id=branch_id,
        ).scalar()

        # Generate new content and audio
        prompt = get_continue_prompt(story_content, sentiment, lang)
        new_paragraph = openai_prompt(prompt)
        audio_url = f"audios/{story_id}_{new_branch_id}.mp3"
        text_to_audio(new_paragraph, audio_url, lang)

        # Update child branch with new content and audio
        run_query(
            """
            UPDATE branches SET
                status = 'done', 
                audio_url = :audio_url,
                paragraph = :new_paragraph
            WHERE branch_id = :new_branch_id
            """,
            audio_url=audio_url,
            new_paragraph=new_paragraph,
            new_branch_id=new_branch_id,
        )

        # Update the requested branch with reference to the child branch
        update_query = """
            UPDATE branches SET
        """
        if sentiment == "positive":
            update_query += "positive_branch_id = :new_branch_id"
        else:
            update_query += "negative_branch_id = :new_branch_id"
        update_query += " WHERE branch_id = :branch_id"

        run_query(
            update_query,
            new_branch_id=new_branch_id,
            branch_id=branch_id,
        )

    # Fetch the updated branch details
    branch = run_query(
        """
        SELECT *
        FROM branches
        WHERE branch_id = :branch_id
        """,
        branch_id=branch_id,
    ).fetchone()

    return jsonify(
        {
            "id": branch.branch_id,
            "story_id": branch.story_id,
            "previous_id": branch.previous_branch_id,
            "status": branch.status,
            "audio_url": get_full_url(branch.audio_url),
            "story": branch.paragraph,
            "positive_branch_id": branch.positive_branch_id,
            "negative_branch_id": branch.negative_branch_id,
        }
    )
