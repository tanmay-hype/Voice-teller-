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
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.5-pro-latest",
]

try:
    NewClient = importlib.import_module("google.genai").Client
except Exception:
    NewClient = None

try:
    LegacyGenAI = importlib.import_module("google.generativeai")
except Exception:
    LegacyGenAI = None


class GeminiService:
    def __init__(self):
        self.client = None
        self.client_kind = None

        if not GEMINI_API_KEY:
            print("⚠️ Gemini key missing")
            return

        if NewClient:
            self.client = NewClient(api_key=GEMINI_API_KEY)
            self.client_kind = "new"
            print("✅ Gemini NEW SDK connected")
            return

        if LegacyGenAI:
            LegacyGenAI.configure(api_key=GEMINI_API_KEY)
            self.client = LegacyGenAI
            self.client_kind = "legacy"
            print("✅ Gemini LEGACY SDK connected")
            return

        print("⚠️ Gemini SDK missing (install google-genai or google-generativeai)")

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

    @staticmethod
    def _is_gemini_config_error(error_text: str) -> bool:
        lowered = error_text.lower()
        return any(
            marker in lowered
            for marker in (
                "api key expired",
                "api key invalid",
                "invalid api key",
                "not found",
                "404",
                "invalid_argument",
            )
        )

    @classmethod
    def _local_story_from_prompt(cls, prompt: str) -> str:
        return openai_svc._local_story(prompt)

    async def _generate_with_gemini(self, contents: str) -> str:
        last_error = None

        for model in GEMINI_CANDIDATE_MODELS:
            try:
                if self.client_kind == "new":
                    response = self.client.models.generate_content(
                        model=model,
                        contents=contents,
                    )
                    text = (response.text or "").strip()
                else:
                    response = self.client.GenerativeModel(model).generate_content(contents)
                    text = (getattr(response, "text", "") or "").strip()

                if text:
                    return text
            except Exception as e:
                last_error = e
                error_text = str(e)
                print(f"🔥 GEMINI ERROR [{model}]:", error_text)

                if self._is_gemini_config_error(error_text):
                    raise RuntimeError(error_text)

                # Retry once if provider returns a short retry window.
                if "RESOURCE_EXHAUSTED" in error_text:
                    retry_seconds = self._extract_retry_seconds(error_text)
                    if 0 < retry_seconds <= 8:
                        await asyncio.sleep(retry_seconds)
                        try:
                            if self.client_kind == "new":
                                response = self.client.models.generate_content(
                                    model=model,
                                    contents=contents,
                                )
                                text = (response.text or "").strip()
                            else:
                                response = self.client.GenerativeModel(model).generate_content(contents)
                                text = (getattr(response, "text", "") or "").strip()

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
        prompt_clean = prompt.strip().rstrip(".")
        if not prompt_clean:
            prompt_clean = "a bright and hopeful day"

        return (
            f"Once upon a time, on {prompt_clean}, there was a little kid who walked to school with a backpack full of dreams. "
            "The clouds were soft, the air felt fresh, and every step felt like the start of a new adventure. "
            "Along the way, the child noticed birds singing, friendly neighbors waving, and little surprises that made the morning feel magical. "
            "By the time the school bell rang, the kid was smiling, ready to learn, play, and share stories with new friends."
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
            if self._is_gemini_config_error(str(e)):
                return self._local_chat_fallback(messages)
            try:
                return await openai_svc.chat_completion(messages)
            except Exception:
                return self._local_chat_fallback(messages)

    async def generate_story(self, prompt: str) -> str:
        if not self.client:
            try:
                return await openai_svc.generate_story(prompt)
            except Exception:
                return self._local_story_from_prompt(prompt)

        try:
            story_prompt = (
                "You are a creative storyteller. Write a vivid, engaging story based on this prompt. "
                "Return only the story text.\n\n"
                f"Prompt: {prompt}"
            )

            return await self._generate_with_gemini(story_prompt)

        except Exception as e:
            print("🔥 GEMINI ERROR:", str(e))
            if self._is_gemini_config_error(str(e)):
                return self._local_story_from_prompt(prompt)
            try:
                return await openai_svc.generate_story(prompt)
            except Exception:
                return self._local_story_from_prompt(prompt)


gemini_svc = GeminiService()