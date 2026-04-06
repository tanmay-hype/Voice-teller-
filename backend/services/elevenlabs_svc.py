import json
import httpx
from core.config import settings

ELEVENLABS_API_KEY = settings.ELEVENLABS_API_KEY
BASE_URL = "https://api.elevenlabs.io/v1"

class ElevenLabsService:
    @staticmethod
    async def upload_voice(name: str, description: str, audio_bytes: bytes, filename: str) -> str:
        """Upload a custom voice to ElevenLabs."""
        if not ELEVENLABS_API_KEY:
            print("Mocking ElevenLabs upload_voice (No API Key)")
            return "mocked_voice_id_123"

        url = f"{BASE_URL}/voices/add"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY
        }
        files = {
            'files': (filename, audio_bytes, 'audio/mpeg')
        }
        data = {
            'name': name,
            'description': description
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data, files=files)
            if response.status_code != 200:
                raise Exception(f"Failed to upload voice: {response.text}")
            return response.json().get("voice_id")

    @staticmethod
    async def text_to_speech(text: str, voice_id: str) -> bytes:
        """Convert text to speech."""
        if not ELEVENLABS_API_KEY:
            print("Mocking ElevenLabs TTS (No API Key)")
            return b"mocked_audio_bytes"

        url = f"{BASE_URL}/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            if response.status_code != 200:
                raise Exception(f"TTS failed: {response.text}")
            return response.content

elevenlabs_svc = ElevenLabsService()
