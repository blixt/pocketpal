import asyncio
import json
from time import time

from quart import Quart, abort, jsonify, render_template, request

from pocketpal.audio import get_full_url, text_to_audio
from pocketpal.db import (
    AsyncSessionFactory,
    query,
    query_one,
    query_scalar,
    query_with_session,
)
from pocketpal.llm import openai_prompt
from pocketpal.prompts import get_continue_prompt, get_final_prompt, get_initial_prompt
from pocketpal.utils import base62

MAX_STORY_LENGTH = 10000  # Approximately 10 branches deep.

app = Quart(__name__)


# Entrypoint for visitors to the app
@app.route("/")
@app.route("/story/<story_id>")
@app.route("/visualize/<story_id>")
async def index(story_id=None):
    return await render_template("index.html")


@app.route("/v1/stories/", methods=["POST"])
async def create_story():
    """Create a new story"""
    data = await request.get_json()
    story_premise = data.get("initial_prompt")

    # Generate content for initial branch
    llm_start = time()
    json_from_llm = await openai_prompt(get_initial_prompt(story_premise))
    llm_duration = time() - llm_start
    app.logger.info(
        f"LLM generated content for new story in {llm_duration:.2f} seconds"
    )
    try:
        story_info = json.loads(json_from_llm)
    except json.JSONDecodeError:
        app.logger.error(f"Failed to parse JSON: {json_from_llm}")
        raise
    assert story_info["lang"]
    assert story_info["title"]
    assert story_info["description"]
    assert story_info["paragraph"]

    # Generate IDs
    story_id = base62(10)
    initial_branch_id = base62(10)
    positive_branch_id = base62(10)
    negative_branch_id = base62(10)
    app.logger.info(
        f"Creating new story: story_id={story_id}, initial_branch_id={initial_branch_id}"
    )

    # Generate audio before the transaction
    audio_url = f"audios/{story_id}_{initial_branch_id}.mp3"
    tts_start = time()
    await text_to_audio(story_info["lang"], story_info["paragraph"], audio_url)
    tts_duration = time() - tts_start
    app.logger.info(
        f"Audio generated for story_id={story_id}, initial_branch_id={initial_branch_id} in {tts_duration:.2f} seconds"
    )

    # Create story and branches within a single transaction
    async with AsyncSessionFactory() as session:
        try:
            # Create story and all branches in a single query
            await query_with_session(
                session,
                """
                WITH story_insert AS (
                    INSERT INTO stories (story_id, initial_branch_id, title, description, initial_prompt, lang)
                    VALUES (:story_id, :initial_branch_id, :title, :description, :initial_prompt, :lang)
                ),
                initial_branch_insert AS (
                    INSERT INTO branches
                    (branch_id, story_id, previous_branch_id, status, sentiment, audio_url, paragraph, positive_branch_id, negative_branch_id)
                    VALUES (:initial_branch_id, :story_id, NULL, 'done', 'initial_branch', :audio_url, :paragraph, :positive_branch_id, :negative_branch_id)
                ),
                positive_branch_insert AS (
                    INSERT INTO branches
                    (branch_id, story_id, previous_branch_id, status, sentiment)
                    VALUES (:positive_branch_id, :story_id, :initial_branch_id, 'new', 'positive')
                )
                INSERT INTO branches
                (branch_id, story_id, previous_branch_id, status, sentiment)
                VALUES (:negative_branch_id, :story_id, :initial_branch_id, 'new', 'negative')
                """,
                story_id=story_id,
                initial_branch_id=initial_branch_id,
                title=story_info["title"],
                description=story_info["description"],
                initial_prompt=story_premise,
                lang=story_info["lang"],
                audio_url=audio_url,
                paragraph=story_info["paragraph"],
                positive_branch_id=positive_branch_id,
                negative_branch_id=negative_branch_id,
            )

            await session.commit()
        except Exception as e:
            await session.rollback()
            app.logger.error(f"Failed to insert story and branches: {e}")
            raise
    app.logger.info(
        f"DB insertions completed for story_id={story_id}, initial_branch_id={initial_branch_id}"
    )

    # TODO: Asynchronously kick off generation of text for the initial branch

    return jsonify(
        {
            "story": {
                "id": story_id,
                "initial_branch_id": initial_branch_id,
                "title": story_info["title"],
                "description": story_info["description"],
                "initial_prompt": story_premise,
                "lang": story_info["lang"],
            },
            "initial_branch": {
                "id": initial_branch_id,
                "story_id": story_id,
                "previous_branch_id": None,
                "status": "done",
                "sentiment": "initial_branch",
                "audio_url": get_full_url(audio_url),
                "paragraph": story_info["paragraph"],
                "positive_branch_id": positive_branch_id,
                "negative_branch_id": negative_branch_id,
                "final_branch": False,
            },
        }
    )


@app.route("/v1/stories/<story_id>/")
async def get_story(story_id):
    """Get story details"""
    app.logger.info(f"Fetching story: story_id={story_id}")
    story = await query_one(
        """
        SELECT story_id, initial_branch_id, title, description, initial_prompt, lang
        FROM stories
        WHERE story_id = :story_id
        """,
        story_id=story_id,
    )

    if not story:
        app.logger.warning(f"Story not found: story_id={story_id}")
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


@app.route("/v1/stories/<story_id>/branches/<branch_id>/")
async def get_branch(story_id, branch_id):
    """
    Get branch details and generate content on demand if necessary.
    """
    # Get the branch information
    branch = await query_one(
        """
        SELECT *, s.lang
        FROM branches b
        JOIN stories s USING (story_id)
        WHERE b.branch_id = :branch_id
        """,
        story_id=story_id,
        branch_id=branch_id,
    )

    if not branch:
        app.logger.warning(
            f"Branch not found: story_id={story_id}, branch_id={branch_id}"
        )
        abort(404, f"Branch {branch_id} does not exist!")
    if branch.story_id != story_id:
        app.logger.warning(
            f"Story mismatch: story_id={story_id}, branch_id={branch_id}"
        )
        abort(404, f"Story {story_id} does not exist!")

    initial_status = branch.status
    is_final_branch = branch.final_branch
    language = branch.lang
    sentiment = branch.sentiment

    # If the branch status is "new", generate its content first
    if initial_status == "new":
        await generate_branch_content(
            story_id, branch_id, language, sentiment, is_final_branch
        )

    if not is_final_branch:
        app.logger.info(
            f"Computing children for branch: story_id={story_id}, branch_id={branch_id}"
        )

        # Get story content
        story_content = await query_scalar(
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
        )

        if not story_content:
            raise ValueError(
                f"Story content not found: story_id={story_id}, branch_id={branch_id}"
            )

        # Story is long enough to become final
        app.logger.info(
            f"Story content length: story_id={story_id}, branch_id={branch_id}, length={len(story_content):,} characters"
        )
        creating_final_branch = len(story_content) > MAX_STORY_LENGTH

        # Generate positive and negative branches in parallel
        await asyncio.gather(
            generate_branch(
                story_id, branch_id, language, "positive", creating_final_branch
            ),
            generate_branch(
                story_id, branch_id, language, "negative", creating_final_branch
            ),
        )

        # Fetch the updated branch details
        app.logger.debug(
            f"Fetching updated branch: story_id={story_id}, branch_id={branch_id}"
        )

    if initial_status == "new" or not is_final_branch:
        branch = await query_one(
            """
            SELECT *
            FROM branches
            WHERE branch_id = :branch_id
            """,
            branch_id=branch_id,
        )
        if not branch:
            raise ValueError(f"Branch not found: branch_id={branch_id}")

    return jsonify(
        {
            "id": branch.branch_id,
            "story_id": branch.story_id,
            "previous_branch_id": branch.previous_branch_id,
            "status": branch.status,
            "sentiment": branch.sentiment,
            "audio_url": get_full_url(branch.audio_url) if branch.audio_url else None,
            "paragraph": branch.paragraph,
            "positive_branch_id": branch.positive_branch_id,
            "negative_branch_id": branch.negative_branch_id,
            "final_branch": branch.final_branch,
        }
    )


async def generate_branch(
    story_id, previous_branch_id, language, sentiment, is_final_branch
):
    app.logger.info(
        f"Generating branch: story_id={story_id}, previous_branch_id={previous_branch_id}, sentiment={sentiment}"
    )
    child_branch = await query_one(
        """
        SELECT branch_id, status
        FROM branches 
        WHERE previous_branch_id = :previous_branch_id 
        AND sentiment = :sentiment
        """,
        previous_branch_id=previous_branch_id,
        sentiment=sentiment,
    )

    if child_branch and child_branch.status != "failed":
        return

    # Create new branch or update failed branch.
    # To reach a 0.01% chance of collision, you need approximately 13M items.
    new_branch_id = child_branch.branch_id if child_branch else base62(10)
    app.logger.info(
        f"{'Updating' if child_branch else 'Creating'} branch: story_id={story_id}, branch_id={new_branch_id}"
    )

    if not child_branch:
        await query(
            """
            INSERT INTO branches 
            (branch_id, story_id, previous_branch_id, status, sentiment, audio_url, paragraph, final_branch)
            VALUES (:new_branch_id, :story_id, :previous_branch_id, 'new', :sentiment, NULL, NULL, :final_branch)
            """,
            new_branch_id=new_branch_id,
            story_id=story_id,
            previous_branch_id=previous_branch_id,
            sentiment=sentiment,
            final_branch=is_final_branch,
        )

    await generate_branch_content(
        story_id, new_branch_id, language, sentiment, is_final_branch
    )

    # Update the requested branch with reference to the child branch
    update_query = "UPDATE branches SET "
    if sentiment == "positive":
        update_query += "positive_branch_id = :new_branch_id"
    else:
        update_query += "negative_branch_id = :new_branch_id"
    update_query += " WHERE branch_id = :previous_branch_id"

    await query(
        update_query,
        new_branch_id=new_branch_id,
        previous_branch_id=previous_branch_id,
    )
    app.logger.info(
        f"DB update completed: story_id={story_id}, branch_id={new_branch_id}"
    )


async def generate_branch_content(
    story_id, branch_id, language, sentiment, is_final_branch
):
    async with AsyncSessionFactory() as session:
        try:
            # Update status from "new" to "generating-text" in a transaction
            result = await query(
                """
                UPDATE branches SET
                    status = 'generating-text'
                WHERE branch_id = :branch_id AND status = 'new'
                """,
                branch_id=branch_id,
            )
            # Make sure there is exactly one row in the result.
            if result.rowcount != 1:
                raise ValueError(
                    f"Could not lock branch {branch_id} for generating text"
                )
            await session.commit()
        except Exception as e:
            await session.rollback()
            app.logger.error(
                f"Failed to update branch status: story_id={story_id}, branch_id={branch_id}, error={str(e)}"
            )
            raise

    # Get story content
    story_content = await query_scalar(
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
    )

    new_paragraph = await generate_text_content(
        story_id, branch_id, story_content, language, sentiment, is_final_branch
    )
    await generate_audio_content(story_id, branch_id, language, new_paragraph)


async def generate_text_content(
    story_id, branch_id, story_content, language, sentiment, is_final_branch
):
    app.logger.info(
        f"Generating text content for branch: story_id={story_id}, branch_id={branch_id}, sentiment={sentiment}"
    )
    if is_final_branch:
        prompt = get_final_prompt(story_content, language, sentiment)
        app.logger.debug(
            f"Final prompt generated: story_id={story_id}, branch_id={branch_id}"
        )
    else:
        prompt = get_continue_prompt(story_content, language, sentiment)
        app.logger.debug(
            f"Continue prompt generated: story_id={story_id}, branch_id={branch_id}"
        )
    llm_start = time()
    new_paragraph = await openai_prompt(prompt)
    llm_duration = time() - llm_start
    app.logger.info(
        f"Paragraph generated: story_id={story_id}, branch_id={branch_id}, duration={llm_duration:.2f}s"
    )

    app.logger.debug(
        f"Updating branch status to 'text-only': story_id={story_id}, branch_id={branch_id}"
    )
    await query(
        """
        UPDATE branches SET
            status = 'text-only',
            paragraph = :new_paragraph
        WHERE branch_id = :branch_id
        """,
        new_paragraph=new_paragraph,
        branch_id=branch_id,
    )

    return new_paragraph


async def generate_audio_content(story_id, branch_id, language, new_paragraph):
    app.logger.debug(
        f"Updating branch status to 'generating-audio': story_id={story_id}, branch_id={branch_id}"
    )
    await query(
        """
        UPDATE branches SET
            status = 'generating-audio'
        WHERE branch_id = :branch_id
        """,
        branch_id=branch_id,
    )

    audio_url = f"audios/{story_id}_{branch_id}.mp3"
    tts_start = time()
    await text_to_audio(language, new_paragraph, audio_url)
    tts_duration = time() - tts_start
    app.logger.info(
        f"Audio generated: story_id={story_id}, branch_id={branch_id}, duration={tts_duration:.2f}s"
    )

    app.logger.debug(
        f"Updating branch status to 'done': story_id={story_id}, branch_id={branch_id}"
    )
    await query(
        """
        UPDATE branches SET
            status = 'done', 
            audio_url = :audio_url
        WHERE branch_id = :branch_id
        """,
        audio_url=audio_url,
        branch_id=branch_id,
    )
