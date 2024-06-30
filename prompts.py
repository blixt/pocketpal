import json


def get_initial_prompt(story_description):
    return f"""Please take this input JSON:

{json.dumps({"story_premise": story_description}, indent=4)}

And turn it into a new story with only its first paragraph written. Return it as a JSON object matching this TypeScript interface:

interface Story {{
    lang: "es" | "en";
    title: string;
    description: string;
    paragraph: string;
}}

DO NOT PUT BACKTICKS. Only write raw JSON.
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

def get_final_prompt(input, sentiment, lang):
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
{lang}

# Input
{input}

# Sentiment
{sentiment}

# Output
"""