import hashlib
import random
import re
from openai import AsyncOpenAI
from core.config import settings


# 🔥 CREATE CLIENT ONCE (IMPORTANT)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIService:

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
                "the classroom door where new lessons waited"
            )
        if any(word in prompt_l for word in ("car", "drive", "road", "vehicle", "truck", "bus")):
            return (
                "road trip",
                "the road where the wheels hummed softly",
                "a stop filled with surprises, signs, and bright colors"
            )
        if any(word in prompt_l for word in ("rabbit", "bunny", "animal", "cat", "dog", "bear", "lion", "bird")):
            return (
                "animal adventure",
                "a grassy path with tiny footprints and careful steps",
                "a safe little clearing where friendship could grow"
            )
        if any(word in prompt_l for word in ("weather", "rain", "sunny", "cloud", "storm", "wind", "pleasant")):
            return (
                "weather day",
                "the morning sky and the changing air around the town",
                "an afternoon that felt calm, bright, and full of possibility"
            )
        if any(word in prompt_l for word in ("sad", "lonely", "cry", "lost", "scared", "afraid")):
            return (
                "gentle feelings",
                "a quiet corner where worries could be heard",
                "a warm moment when hope began to return"
            )

        return (
            "small adventure",
            "a familiar place with one surprising detail",
            "a moment that turned ordinary things into something magical"
        )

    @classmethod
    def _local_story(cls, prompt: str) -> str:
        prompt_clean = cls._normalize_prompt(prompt)
        if not prompt_clean:
            prompt_clean = "a bright and cheerful morning"

        theme, opening_scene, closing_scene = cls._theme_from_prompt(prompt_clean)
        seed = int(hashlib.sha256(prompt_clean.encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(seed)

        names = ["Mia", "Noah", "Lina", "Ari", "Zoe", "Sam"]
        friends = ["a kind neighbor", "a cheerful friend", "a curious classmate", "a gentle parent"]
        actions = [
            "noticed",
            "learned",
            "helped",
            "laughed with",
            "shared with",
            "discovered",
        ]
        name = rng.choice(names)
        friend = rng.choice(friends)
        action = rng.choice(actions)

        return (
            f"{name} woke up ready for a {theme} on {prompt_clean}. "
            f"The story began at {opening_scene}, and {name} {action} {friend} along the way. "
            f"A small problem appeared, but {name} stayed brave, listened closely, and found a gentle solution. "
            f"By the time {closing_scene} arrived, the day felt brighter, and {name} had one more reason to smile."
        )

    @staticmethod
    def _local_chat_reply(prompt: str) -> str:
        prompt_clean = prompt.strip()
        if not prompt_clean:
            prompt_clean = "your message"
        return f"I can help with that. Here is a simple response to {prompt_clean}."

    async def generate_story(self, prompt: str) -> str:
        if not settings.OPENAI_API_KEY:
            print("⚠️ OpenAI key missing, using local story fallback")
            return self._local_story(prompt)

        try:
            print("calling openai")
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",  # 🔥 cheaper + faster than gpt-4o
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative storyteller. Generate an engaging, vivid, and immersive story."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print("🔥 OpenAI generate_story ERROR:", str(e))
            raise e


    async def chat_completion(self, messages: list[dict]) -> str:
        if not settings.OPENAI_API_KEY:
            print("⚠️ OpenAI key missing, using local chat fallback")
            user_messages = [m.get("content", "") for m in messages if m.get("role") == "user"]
            latest = user_messages[-1] if user_messages else "your message"
            return self._local_chat_reply(latest)

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print("🔥 OpenAI chat_completion ERROR:", str(e))
            raise e


openai_svc = OpenAIService()