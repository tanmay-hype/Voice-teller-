from openai import AsyncOpenAI
from core.config import settings


# 🔥 CREATE CLIENT ONCE (IMPORTANT)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIService:

    async def generate_story(self, prompt: str) -> str:
        if not settings.OPENAI_API_KEY:
            print("⚠️ Mocking OpenAI generate_story (No API Key)")
            return f"Mocked story generated for prompt: {prompt}"

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
            print("⚠️ Mocking OpenAI chat_completion (No API Key)")
            return "Mock response from OpenAI Assistant"

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