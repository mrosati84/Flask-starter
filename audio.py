import os
import requests
import uuid
from pathlib import Path

def elevenlalbs(text:str, folder_path:str) -> str:
    id = str(uuid.uuid4())

    Path(folder_path).mkdir(parents=True, exist_ok=True)

    speech_file_path = f"{folder_path}/{id}.mp3"

    VOICE_ID = os.environ.get('ELEVENLABS_VOICE_ID') or "gPWeWJBcOrH90ldfr24o"
    MODEL = "eleven_multilingual_v2"

    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    


    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.environ.get('ELEVENLABS_KEY')
    }

    data = {
        "text": text,
        "model_id": MODEL,
        # "voice_settings": {
        #     "stability": 0.5,
        #     "similarity_boost": 0.5
        # }
    }


    response = requests.post(url, json=data, headers=headers)
    with open(speech_file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    
    return speech_file_path