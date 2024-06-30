import json


def get_initial_prompt(story_description):
    return f"""Please take this input JSON:

{json.dumps({"story_premise": story_description}, indent=4)}

Return it as a JSON object matching this TypeScript interface:

interface Story {{
    lang: "es" | "en";
    title: string;
    description: string;
    paragraph: string;
}}
"""


def get_continue_prompt(input, sentiment, lang):
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
{lang}

# Input:
{input}

# Sentiment
{sentiment}

# Output
"""
