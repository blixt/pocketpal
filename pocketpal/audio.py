import os
from datetime import datetime, timedelta
from typing import Dict, Tuple

import aiohttp
from elevenlabs import VoiceSettings
from elevenlabs.client import AsyncElevenLabs
from google.cloud import storage

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
BUCKET_NAME = "pocketpal-bucket"


VOICES: Dict[str, Tuple[str, str]] = {
    "en": ("iiidtqDt9FBdT1vfBluA", "eleven_turbo_v2"),
    "es": ("Nh2zY9kknu6z4pZy6FhD", "eleven_multilingual_v2"),
    "pt": ("WgE8iWzGVoJYLb5V7l2d", "eleven_multilingual_v2"),
    "se": ("x0u3EW21dbrORJzOq1m9", "eleven_multilingual_v2"),
    # Good but 3x expensive!
    # "en": ("BNgbHR0DNeZixGQVzloa", "eleven_turbo_v2"),
}


def get_full_url(destination_blob_name: str) -> str:
    """Returns the full URL for a given blob name in the bucket."""
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{destination_blob_name}"


async def text_to_audio(language: str, text: str, destination_blob_name: str):
    """Convert text to audio"""

    if language not in VOICES:
        raise ValueError(f"Language {language} not supported")

    voice_id, model_id = VOICES[language]

    client = AsyncElevenLabs(
        api_key=ELEVENLABS_API_KEY,
    )

    response = client.text_to_speech.convert(
        voice_id=voice_id,
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id=model_id,
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Save in storage
    client = storage.Client(project="pocketpal-427909")
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    # Generate a signed URL for uploading
    expiration_time = datetime.utcnow() + timedelta(minutes=10)
    signed_url = blob.generate_signed_url(
        expiration=expiration_time,
        method="PUT",
        content_type="audio/mpeg",
    )

    # TODO: It would be nice if we could multicast this to anyone that wants to listen to the audio before it's complete.
    headers = {"Content-Type": "audio/mpeg"}
    async with aiohttp.ClientSession() as session:
        async with session.put(signed_url, data=response, headers=headers) as resp:
            if resp.status != 200:
                print(f"Error: {await resp.text()}")
                raise Exception(
                    f"Failed to upload file to {destination_blob_name} in bucket {BUCKET_NAME}. Status code: {resp.status}"
                )

    print(f"File uploaded to {destination_blob_name} in bucket {BUCKET_NAME}.")
