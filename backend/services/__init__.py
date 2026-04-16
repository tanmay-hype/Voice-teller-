def __init__(self):
    self.api_key = settings.ELEVENLABS_API_KEY
    print(f"🔑 ElevenLabs API Key Loaded: {'Yes' if self.api_key else 'No'}")

    