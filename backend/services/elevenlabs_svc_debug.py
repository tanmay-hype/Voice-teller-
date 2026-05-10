import httpx
from core.config import settings

BASE_URL = "https://api.elevenlabs.io/v1"


class ElevenLabsService:

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        print(f"🔧 ElevenLabsService initialized")
        print(f"   API Key present: {bool(self.api_key)}")
        print(f"   API Key length: {len(self.api_key) if self.api_key else 0}")

    def _headers(self, extra=None):
        headers = {
            "xi-api-key": self.api_key
        }
        if extra:
            headers.update(extra)
        print(f"   📋 Headers prepared: {list(headers.keys())}")
        return headers

    async def upload_voice(
        self,
        name: str,
        description: str,
        audio_bytes: bytes,
        filename: str
    ) -> str:
        """Upload a custom voice to ElevenLabs"""
        print(f"\n{'='*50}")
        print(f"🎤 ElevenLabs upload_voice START")
        print(f"   Name: {name}")
        print(f"   Filename: {filename}")
        print(f"   Audio size: {len(audio_bytes)} bytes")

        if not self.api_key:
            print("⚠️  NO API KEY - Mocking response")
            return "mocked_voice_id_123"

        url = f"{BASE_URL}/voices/add"
        print(f"   Target URL: {url}")

        # Detect file type
        content_type = "audio/mpeg"
        if filename.endswith(".wav"):
            content_type = "audio/wav"
        print(f"   Content-Type: {content_type}")

        files = {
            "files": (filename, audio_bytes, content_type)
        }

        data = {
            "name": name,
            "description": description
        }

        try:
            print(f"   ➡️  Creating HTTP client and sending POST request...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"   ⏳ Awaiting response from {url}...")
                response = await client.post(
                    url,
                    headers=self._headers(),
                    data=data,
                    files=files
                )
                print(f"   ✅ Response received!")
                print(f"      Status: {response.status_code}")
                print(f"      Headers: {dict(response.headers)}")

                # Some ElevenLabs API versions use a different path; try a fallback
                if not (200 <= response.status_code < 300):
                    alt_url = f"{BASE_URL}/voices"
                    print(f"   ⚠️  Status {response.status_code} not in 2xx range")
                    print(f"   🔄 Trying fallback endpoint: {alt_url}")
                    response = await client.post(
                        alt_url,
                        headers=self._headers(),
                        data=data,
                        files=files
                    )
                    print(f"   ✅ Fallback response received!")
                    print(f"      Status: {response.status_code}")

            if not (200 <= response.status_code < 300):
                print(f"   ❌ Both endpoints failed!")
                print(f"      Final Status: {response.status_code}")
                print(f"      Response Text: {response.text}")
                raise Exception(f"Voice upload failed with status {response.status_code}")

            print(f"   📦 Parsing JSON response...")
            res_json = response.json()
            print(f"      Response JSON: {res_json}")

            # Try several possible payload shapes returned by ElevenLabs
            voice_id = None
            # common possibilities
            voice_id = res_json.get("voice_id") or res_json.get("id")
            print(f"   🔍 Extracting voice_id...")
            print(f"      Attempt 1 (top-level): {voice_id}")
            
            # nested under 'voice'
            if not voice_id and isinstance(res_json.get("voice"), dict):
                voice_id = res_json["voice"].get("voice_id") or res_json["voice"].get("id")
                print(f"      Attempt 2 (nested voice): {voice_id}")
            
            # sometimes returned as {'voices': [{'id': ...}]}
            if not voice_id and isinstance(res_json.get("voices"), list) and len(res_json["voices"]) > 0:
                first = res_json["voices"][0]
                if isinstance(first, dict):
                    voice_id = first.get("voice_id") or first.get("id")
                    print(f"      Attempt 3 (voices array): {voice_id}")

            if not voice_id:
                print(f"   ❌ Could not extract voice_id from response!")
                print(f"      Full response: {res_json}")
                raise Exception("No voice_id returned from ElevenLabs")

            print(f"   ✅ Voice cloned successfully!")
            print(f"      Voice ID: {voice_id}")
            print(f"{'='*50}\n")
            return voice_id

        except Exception as e:
            print(f"   🔥 ERROR in upload_voice: {str(e)}")
            print(f"{'='*50}\n")
            raise

    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Convert text to speech"""
        print(f"\n{'='*50}")
        print(f"🔊 ElevenLabs text_to_speech START")
        print(f"   Voice ID: {voice_id}")
        print(f"   Text length: {len(text)} chars")

        if not self.api_key:
            print("⚠️  NO API KEY - Mocking response")
            return b"mocked_audio_bytes"

        url = f"{BASE_URL}/text-to-speech/{voice_id}"
        print(f"   Target URL: {url}")

        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        print(f"   Payload: {payload}")

        try:
            print(f"   ➡️  Creating HTTP client and sending POST request...")
            async with httpx.AsyncClient(timeout=60.0) as client:
                print(f"   ⏳ Awaiting audio response from {url}...")
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers({
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json"
                    })
                )
                print(f"   ✅ Response received!")
                print(f"      Status: {response.status_code}")
                print(f"      Content-Type: {response.headers.get('content-type')}")
                print(f"      Content-Length: {len(response.content)} bytes")

            if not (200 <= response.status_code < 300):
                print(f"   ❌ TTS failed!")
                print(f"      Status: {response.status_code}")
                print(f"      Response: {response.text}")
                raise Exception(f"Text-to-speech failed with status {response.status_code}")

            print(f"   ✅ Audio generated successfully!")
            print(f"{'='*50}\n")
            return response.content

        except Exception as e:
            print(f"   🔥 ERROR in text_to_speech: {str(e)}")
            print(f"{'='*50}\n")
            raise


# Singleton instance
print("🚀 Loading ElevenLabsService singleton...")
elevenlabs_svc = ElevenLabsService()
print("✅ ElevenLabsService singleton loaded\n")
