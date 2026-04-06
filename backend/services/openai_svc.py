import openai
from core.config import settings


OPENAI_API_KEY = settings.OPENAI_API_KEY

class OpenAIService:
    @staticmethod
    async def generate_story(prompt: str) -> str:
        if not OPENAI_API_KEY:
            print("Mocking OpenAI generate_story (No API Key)")
            return f"Mocked story generated for prompt: {prompt}"
            
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative storyteller. Generate an engaging story based on the prompt."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content

    @staticmethod
    async def chat_completion(messages: list[dict]) -> str:
        if not OPENAI_API_KEY:
            print("Mocking OpenAI chat_completion (No API Key)")
            return "Mock response from OpenAI Assistant"

        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content

openai_svc = OpenAIService()
