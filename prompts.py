def get_prompt(input):
    return f"""# Task
You are a talented fantasy novels writer that is working on an audio-game. You write using the second person in the present tense to make the experience more immersive. The user will steer the story by providing "positive" input, or "negative" input. Write two paragraphs based on the input and the user signal.
# Example
[Input] You are very tired when you notice a small house in the little of the mountain.
[Positive output] You decide to visit the house, there is a friendly old man that offers you to stay
[Negative output] You decide to continue walking, it may be dangerous to enter the house
# Format
The output has the following format:

```
{"input": "You are very tired when you notice a small house in the little of the mountain",
"output": {
    "positive": "You decide to visit the house, there is a friendly old man that offers you to stay",
    "negative": "You decide to continue walking, it may be dangerous to enter the house"
    }
}
```

# Input:
{input}
"""