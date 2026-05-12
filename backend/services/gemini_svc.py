import importlib
import os
import re
import asyncio
from core.config import settings
from services.openai_svc import openai_svc

GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_CANDIDATE_MODELS = [
    GEMINI_PRIMARY_MODEL,
    "gemini-2.5-flash"
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.5-pro-latest",
]

try:
    Client = importlib.import_module("google.genai").Client
except Exception:
    Client = None


class GeminiService:
    def __init__(self):
        if GEMINI_API_KEY and Client:
            self.client = Client(api_key=GEMINI_API_KEY)
            print("✅ Gemini NEW SDK connected")
        else:
            self.client = None
            print("⚠️ Gemini key or SDK missing")

    @staticmethod
    def _extract_retry_seconds(error_text: str) -> int:
        match = re.search(r"retry in\s+(\d+(?:\.\d+)?)s", error_text, flags=re.IGNORECASE)
        if not match:
            match = re.search(r"'retryDelay':\s*'(\d+)s'", error_text)
        if not match:
            return 0
        try:
            return int(float(match.group(1)))
        except (TypeError, ValueError):
            return 0

    async def _generate_with_gemini(self, contents: str) -> str:
        last_error = None

        for model in GEMINI_CANDIDATE_MODELS:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                )
                text = (response.text or "").strip()
                if text:
                    return text
            except Exception as e:
                last_error = e
                error_text = str(e)
                print(f"🔥 GEMINI ERROR [{model}]:", error_text)

                # Retry once if provider returns a short retry window.
                if "RESOURCE_EXHAUSTED" in error_text:
                    retry_seconds = self._extract_retry_seconds(error_text)
                    if 0 < retry_seconds <= 8:
                        await asyncio.sleep(retry_seconds)
                        try:
                            response = self.client.models.generate_content(
                                model=model,
                                contents=contents,
                            )
                            text = (response.text or "").strip()
                            if text:
                                return text
                        except Exception as retry_error:
                            last_error = retry_error
                            print(f"🔥 GEMINI RETRY ERROR [{model}]:", str(retry_error))

                continue

        if last_error:
            raise last_error
        raise RuntimeError("Gemini generation failed with no response")

    @staticmethod
    def _local_chat_fallback(messages: list[dict]) -> str:
        user_messages = [m.get("content", "") for m in messages if m.get("role") == "user"]
        latest = user_messages[-1].strip() if user_messages else ""
        if latest:
            return (
                "I am temporarily running in offline fallback mode and could not reach Gemini right now. "
                f"You said: '{latest}'. Please try again in a moment."
            )
        return "I am temporarily running in offline fallback mode and could not reach Gemini right now."

    @staticmethod
    def _local_story_fallback(prompt: str) -> str:
        return (
            "The storyteller is currently running in fallback mode because Gemini is unavailable.\n\n"
            f"Story prompt: {prompt}\n\n"
            "Once Gemini quota is available, story quality will improve automatically."
        )

    async def chat_completion(self, messages: list[dict]) -> str:
        if not self.client:
            try:
                return await openai_svc.chat_completion(messages)
            except Exception:
                return self._local_chat_fallback(messages)

        try:
            prompt = ""
            for msg in messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n"
            return await self._generate_with_gemini(prompt)

        except Exception as e:
            print("🔥 GEMINI ERROR:", str(e))
            try:
                return await openai_svc.chat_completion(messages)
            except Exception:
                return self._local_chat_fallback(messages)

    async def generate_story(self, prompt: str) -> str:
        if not self.client:
            try:
                return await openai_svc.generate_story(prompt)
            except Exception:
                return self._local_story_fallback(prompt)

        try:
            story_prompt = (
                "You are a creative storyteller. Write a vivid, engaging story based on this prompt. "
                "Return only the story text.\n\n"
                f"Prompt: {prompt}"
            )

            return await self._generate_with_gemini(story_prompt)

        except Exception as e:
            print("🔥 GEMINI ERROR:", str(e))
            try:
                return await openai_svc.generate_story(prompt)
            except Exception:
                return self._local_story_fallback(prompt)


gemini_svc = GeminiService()