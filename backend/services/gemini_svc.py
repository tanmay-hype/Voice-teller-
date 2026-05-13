import importlib
import os
import re
import asyncio
from core.config import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_CANDIDATE_MODELS = [
    GEMINI_PRIMARY_MODEL,
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

    @staticmethod
    def _normalize_prompt(prompt: str) -> str:
        prompt_clean = re.sub(r"\s+", " ", prompt.strip())
        return prompt_clean.rstrip(".")

    @staticmethod
    def _theme_from_prompt(prompt: str) -> tuple[str, str, str]:
        prompt_l = prompt.lower()

        if any(word in prompt_l for word in ("school", "class", "teacher", "homework")):
            return (
                "school day",
                "the school gate with a backpack full of questions",
                "the classroom door where new lessons waited",
            )
        if any(word in prompt_l for word in ("car", "drive", "road", "vehicle", "truck", "bus")):
            return (
                "road trip",
                "the road where the wheels hummed softly",
                "a stop filled with surprises, signs, and bright colors",
            )
        if any(word in prompt_l for word in ("rabbit", "bunny", "animal", "cat", "dog", "bear", "lion", "bird")):
            return (
                "animal adventure",
                "a grassy path with tiny footprints and careful steps",
                "a safe little clearing where friendship could grow",
            )
        if any(word in prompt_l for word in ("weather", "rain", "sunny", "cloud", "storm", "wind", "pleasant", "sky")):
            return (
                "weather day",
                "the morning sky and the changing air around the town",
                "an afternoon that felt calm, bright, and full of possibility",
            )
        if any(word in prompt_l for word in ("sad", "lonely", "cry", "lost", "scared", "afraid", "lazy", "tired")):
            return (
                "gentle feelings",
                "a quiet corner where worries could be heard",
                "a warm moment when hope began to return",
            )

        return (
            "small adventure",
            "a familiar place with one surprising detail",
            "a moment that turned ordinary things into something magical",
        )

    @classmethod
    def _local_story(cls, prompt: str) -> str:
        prompt_clean = cls._normalize_prompt(prompt)
        if not prompt_clean:
            prompt_clean = "a bright and hopeful day"

        theme, opening_scene, closing_scene = cls._theme_from_prompt(prompt_clean)
        seed = sum(ord(char) for char in prompt_clean)
        names = ["Mia", "Noah", "Lina", "Ari", "Zoe", "Sam"]
        friends = ["a kind neighbor", "a cheerful friend", "a curious classmate", "a gentle parent"]
        actions = ["noticed", "learned", "helped", "laughed with", "shared with", "discovered"]

        name = names[seed % len(names)]
        friend = friends[(seed // 3) % len(friends)]
        action = actions[(seed // 7) % len(actions)]

        return (
            f"{name} woke up ready for a {theme} on {prompt_clean}. "
            f"The story began at {opening_scene}, and {name} {action} {friend} along the way. "
            f"A small problem appeared, but {name} stayed brave, listened closely, and found a gentle solution. "
            f"By the time {closing_scene} arrived, the day felt brighter, and {name} had one more reason to smile."
        )

    @staticmethod
    def _local_chat_reply(messages: list[dict]) -> str:
        user_messages = [m.get("content", "") for m in messages if m.get("role") == "user"]
        latest = user_messages[-1].strip() if user_messages else "your message"
        return f"I can help with that. Here is a simple response to {latest}."

    async def _generate_with_gemini(self, contents: str) -> str:
        last_error = None

        for model in GEMINI_CANDIDATE_MODELS:
            try:
                print(f"➡️ Gemini request start [{model}]")
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                )
                text = (response.text or "").strip()
                if text:
                    print(f"✅ Gemini success [{model}]")
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
        return GeminiService._local_story(prompt)

    async def chat_completion(self, messages: list[dict]) -> str:
        if not self.client:
            return self._local_chat_reply(messages)

        try:
            prompt = ""
            for msg in messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n"
            return await self._generate_with_gemini(prompt)

        except Exception as e:
            print("🔥 GEMINI ERROR:", str(e))
            return self._local_chat_reply(messages)

    async def generate_story(self, prompt: str) -> str:
        if not self.client:
            return self._local_story(prompt)

        try:
            story_prompt = (
                "You are a creative storyteller. Write a vivid, engaging story based on this prompt. "
                "Return only the story text.\n\n"
                f"Prompt: {prompt}"
            )

            return await self._generate_with_gemini(story_prompt)

        except Exception as e:
            print("🔥 GEMINI ERROR:", str(e))
            return self._local_story(prompt)


gemini_svc = GeminiService()