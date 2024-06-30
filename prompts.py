import json


def get_initial_prompt(story_description):
    return f"""Please take this input JSON:

{json.dumps({"story_premise": story_description}, indent=4)}

And turn it into a new story with only its first paragraph written. Return it as a JSON object matching this TypeScript interface:

interface Story {{
    title: string;
    description: string;
    paragraph: string;
}}
"""


def get_continue_prompt(input, sentiment):
    return f"""# Task
You are a talented fantasy novels writer that is working on an audio-game. 
You write using the second person in the present tense to make the experience more immersive. 
The user will steer the story by providing "positive" input, or "negative" input. 
Write a paragraph based on the input and the user signal.
# Example
[Input] You are very tired when you notice a small house in the little of the mountain.
[Positive output] You decide to visit the house, there is a friendly old man that offers you to stay
[Negative output] You decide to continue walking, it may be dangerous to enter the house

# Input:
{input}

# Sentiment
{sentiment}

# Output
"""
