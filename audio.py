import os
import requests


def text_to_audio(text: str):
    """Convert text to audio"""

    # This voice id and model for English
    url = "https://api.elevenlabs.io/v1/text-to-speech/iiidtqDt9FBdT1vfBluA"

    payload = {
        "text": "<string>",
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        },
        # Maybe: "previous_text": "<string>"
        # Or maybe: "previous_request_ids": ["<string>"]
    }
    headers = {
    "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
    }

    # Gives us an MP3 file.
    response = requests.request("POST", url, json=payload, headers=headers)
    import pdb; pdb.set_trace()

    return response