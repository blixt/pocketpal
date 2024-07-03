import json

# TODO: Refactor these prompts into this format:
# 1. System prompt with solid instructions
# 2. Tool calls for gathering structured data from the LLM (even if it's just one string).
#    (Use forced tool calls for this.)
# 3. The user message which should only contain actual user input to avoid confusion between user input and LLM instructions.

# Probably we merge llm.py and prompts.py and use llm.bind_tools(…) and SystemMessage etc.
# - generate_new_story_info(premise)
# - generate_new_branch(language, story, sentiment, final=False)

# Thoughts on prompts below:
# - We should iterate on what "positive" and "negative" mean for the LLM.
#   -> We should not tell the LLM just "positive" or "negative"
#   -> "positive" => "Progress the story, adding a new situation"
#   -> "negative" => "Continue the story, but not in the way the most recent paragraphs were going"
# - If we want to expand the scope, there's no need to tell the LLM anything about "fantasy novels" or "audio-game"
# - Let's try to be more specific about the length of the content the LLM gives us for better consistency
# - The rest seems great (second person, present tense, etc)
# - Consider adding a target audience setting for a story ("for 4-year-olds", "for adults", or just "automatic" to let the LLM choose)


def get_initial_prompt(story_description):
    return f"""Please take this input JSON:

{json.dumps({"story_premise": story_description}, indent=4)}

And turn it into a new story with only its first paragraph written, and not too long.
The paragraph should finish with a situation where there is an alternative choice that will change the original flow of the story. The alternatives should be one that propels the story forward, and one that changes the direction of the story.
You write using the language that was used for the premise and in the second person in the present tense to make the experience more immersive.
The title for the story should be unique and intriguing, fit for the cover of a book, based on the premise and beginning of the story.

Provide a JSON object matching this TypeScript interface:

interface Story {{
    lang: "es" | "en" | "pt" | "se";
    paragraph: string;
    description: string;
    title: string;
}}

DO NOT PUT BACKTICKS. Only write raw JSON.
"""


def get_continue_prompt(story, language, sentiment):
    return f"""# Task
You are a talented fantasy novels writer that is working on an audio-game.
You write using the provided language and the second person in the present tense to make the experience more immersive.
The user will steer the story by providing "positive" input, or "negative" input.
Write a paragraph based on the input and the user signal.
The paragraph should finish with a situation where there is an alternative choice that will change the original flow of the story.

# Example
[Language] en
[Input] You are very tired when you notice a small house in the little of the mountain.
[Positive output] You decide to visit the house, there is a friendly old man that offers you to stay
[Negative output] You decide to continue walking, it may be dangerous to enter the house

# Language
{language}

# Input:
{story}

# Sentiment
{sentiment}

# Output
"""


def get_final_prompt(story, language, sentiment):
    return f"""# Task
You are a talented fantasy novels writer that is working on an audio-game.
You write using the provided language and the second person in the present tense to make the experience more immersive.
The user will decide the end of the story by providing a "positive" or "negative" signal.
If the sentiment is positive, write a happy ending.
If the sentiment is negative, write a tragic ending.

# Example
[Language] en
[Input] You finally found the treasure and the princess is happy to marry you
[Positive output] You have a happy wedding with all your family and friends
[Negative output] The treasure contains a bomb and you all die

# Language
{language}

# Input
{story}

# Sentiment
{sentiment}

# Output
"""
