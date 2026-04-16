import httpx
from core.config import settings

BASE_URL = "https://api.elevenlabs.io/v1"


class ElevenLabsService:

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY

    def _headers(self, extra=None):
        headers = {
            "xi-api-key": self.api_key
        }
        if extra:
            headers.update(extra)
        return headers

    async def upload_voice(
        self,
        name: str,
        description: str,
        audio_bytes: bytes,
        filename: str
    ) -> str:
        """Upload a custom voice to ElevenLabs"""

        if not self.api_key:
            print("⚠️ Mocking ElevenLabs upload_voice (No API Key)")
            return "mocked_voice_id_123"

        url = f"{BASE_URL}/voices/add"

        # Detect file type
        content_type = "audio/mpeg"
        if filename.endswith(".wav"):
            content_type = "audio/wav"

        files = {
            "files": (filename, audio_bytes, content_type)
        }

        data = {
            "name": name,
            "description": description
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self._headers(),
                    data=data,
                    files=files
                )

            if response.status_code != 200:
                print("❌ ElevenLabs Upload Error:", response.text)
                raise Exception("Voice upload failed")

            res_json = response.json()

            voice_id = res_json.get("voice_id")
            if not voice_id:
                raise Exception("No voice_id returned from ElevenLabs")

            print(f"✅ Voice cloned successfully: {voice_id}")
            return voice_id

        except Exception as e:
            print("🔥 ERROR in upload_voice:", str(e))
            raise

    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Convert text to speech"""

        if not self.api_key:
            print("⚠️ Mocking ElevenLabs TTS (No API Key)")
            return b"mocked_audio_bytes"

        url = f"{BASE_URL}/text-to-speech/{voice_id}"

        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers({
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json"
                    })
                )

            if response.status_code != 200:
                print("❌ ElevenLabs TTS Error:", response.text)
                raise Exception("Text-to-speech failed")

            print("✅ Audio generated successfully")
            return response.content

        except Exception as e:
            print("🔥 ERROR in text_to_speech:", str(e))
            raise


# Singleton instance
elevenlabs_svc = ElevenLabsService()
