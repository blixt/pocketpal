import os
import uuid

import requests
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


def text_to_audio(text: str):
    """Convert text to audio"""

    # # This voice id and model for English
    # url = "https://api.elevenlabs.io/v1/text-to-speech/iiidtqDt9FBdT1vfBluA"

    # payload = {
    #     "text": "<string>",
    #     "model_id": "eleven_turbo_v2",
    #     "voice_settings": {
    #         "stability": 0.5,
    #         "similarity_boost": 0.75
    #     },
    #     # Maybe: "previous_text": "<string>"
    #     # Or maybe: "previous_request_ids": ["<string>"]
    # }
    # headers = {
    #     "Accept": "audio/mpeg",
    #     "Content-Type": "application/json",
    #     "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
    # }

    # # Gives us an MP3 file
    # response = requests.request("POST", url, json=payload, headers=headers)

    client = ElevenLabs(
        api_key=ELEVENLABS_API_KEY,
    )

    response = client.text_to_speech.convert(
        voice_id="iiidtqDt9FBdT1vfBluA",  # Adam pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",  # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Generating a unique file name for the output MP3 file
    save_file_path = f"{uuid.uuid4()}.mp3"

    # Writing the audio stream to the file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"A new audio file was saved successfully at {save_file_path}")

    return save_file_path