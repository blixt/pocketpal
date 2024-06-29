from google.cloud import storage
import requests

audio_url = 'https://file-examples.com/storage/fecbba2e0c66800b6a18e9c/2017/11/file_example_MP3_1MG.mp3'
bucket_name = 'pocketpal-bucket'
destination_blob_name = 'audio/file_example_MP3_1MG.mp3'

# Download the audio file
response = requests.get(audio_url)
audio_data = response.content

# Initialize a GCP storage client
client = storage.Client()

# Get the bucket
bucket = client.get_bucket(bucket_name)

# Create a new blob and upload the audio data
blob = bucket.blob(destination_blob_name)
blob.upload_from_string(audio_data)

print(f'File uploaded to {destination_blob_name} in bucket {bucket_name}.')
