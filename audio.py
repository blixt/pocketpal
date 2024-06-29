import os

import requests
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from google.cloud import storage

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
bucket_name = 'pocketpal-bucket'

def text_to_audio(text: str, destination_blob_name: str):
    """Convert text to audio"""

    client = ElevenLabs(
        api_key=ELEVENLABS_API_KEY,
    )

    response = client.text_to_speech.convert(
        voice_id="iiidtqDt9FBdT1vfBluA",
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Save in storage
    audio_data = b"".join(response)
    client = storage.Client(project="pocketpal-427909")
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(audio_data)

    print(f'File uploaded to {destination_blob_name} in bucket {bucket_name}.')
