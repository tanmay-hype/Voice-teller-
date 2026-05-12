from openai import AsyncOpenAI
from core.config import settings


# 🔥 CREATE CLIENT ONCE (IMPORTANT)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIService:

    @staticmethod
    def _local_story(prompt: str) -> str:
        prompt_clean = prompt.strip().rstrip(".")
        if not prompt_clean:
            prompt_clean = "a bright and cheerful morning"

        return (
            f"On {prompt_clean}, a little kid set out for school with a bright smile and a hopeful heart. "
            "The path felt calm and welcoming, with gentle breezes, singing birds, and neighbors waving hello. "
            "Every step turned into a tiny adventure, and by the time the child reached the classroom, the day already felt special. "
            "Inside, new lessons, kind friends, and a world of discoveries waited to be explored."
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