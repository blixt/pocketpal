import os
from typing import Dict, Tuple
from urllib.parse import quote

import aiohttp
from elevenlabs import VoiceSettings
from elevenlabs.client import AsyncElevenLabs
from google.auth import default
from google.auth.transport.requests import Request

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
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{quote(destination_blob_name, safe='')}"


async def text_to_audio(language: str, text: str, destination_blob_name: str):
    """Convert text to audio and upload to Google Cloud Storage"""
    if language not in VOICES:
        raise ValueError(f"Language {language} not supported")

    voice_id, model_id = VOICES[language]

    client = AsyncElevenLabs(api_key=ELEVENLABS_API_KEY)

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

    credentials, _ = default()
    credentials.refresh(Request())

    async with aiohttp.ClientSession() as session:
        safe_destination_blob_name = quote(destination_blob_name, safe="")
        url = f"https://storage.googleapis.com/upload/storage/v1/b/{BUCKET_NAME}/o?uploadType=media&name={safe_destination_blob_name}"

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "audio/mpeg",
        }

        async with session.post(url, headers=headers, data=response) as upload_response:
            if upload_response.status != 200:
                error_text = await upload_response.text()
                raise Exception(
                    f"Failed to upload file to {destination_blob_name} in bucket {BUCKET_NAME}. Status code: {upload_response.status}. Error: {error_text}"
                )

    print(f"File uploaded to {destination_blob_name} in bucket {BUCKET_NAME}.")
