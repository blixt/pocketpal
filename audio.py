import os
from typing import Dict, Literal, Tuple

from elevenlabs import VoiceSettings
from elevenlabs.client import AsyncElevenLabs
from google.cloud import storage

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
BUCKET_NAME = "pocketpal-bucket"


VOICES: Dict[Literal["en", "es"], Tuple[str, str]] = {
    "en": ("iiidtqDt9FBdT1vfBluA", "eleven_turbo_v2"),
    "es": ("Nh2zY9kknu6z4pZy6FhD", "eleven_multilingual_v2"),
}


def get_full_url(destination_blob_name: str) -> str:
    """Returns the full URL for a given blob name in the bucket."""
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{destination_blob_name}"


async def text_to_audio(
    language: Literal["en", "es"], text: str, destination_blob_name: str
):
    """Convert text to audio"""

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
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    # Upload the MP3 file to a public bucket
    data = b""
    async for chunk in response:
        data += chunk
    blob.upload_from_string(data, content_type="audio/mpeg")

    print(f"File uploaded to {destination_blob_name} in bucket {BUCKET_NAME}.")
