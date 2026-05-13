import asyncio
import logging
from google import genai
from core.config import settings

logger = logging.getLogger(__name__)

# Configuration: modern models only
GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
]


class GeminiService:
    def __init__(self) -> None:
        """Initialize Gemini client with masked key logging."""
        masked = None
        try:
            if GEMINI_API_KEY:
                masked = GEMINI_API_KEY[:8] + "..." if len(GEMINI_API_KEY) > 8 else "(set)"
        except Exception:
            masked = None

        logger.info("Gemini init: models=%s key=%s", GEMINI_CANDIDATE_MODELS, masked)

        self.client = None
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set — Gemini disabled")
            return

        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            logger.info("✅ Gemini client initialized")
        except Exception:
            logger.exception("Failed to initialize Gemini client")

    async def _generate_with_gemini(self, contents: str) -> str:
        """Try each model in GEMINI_CANDIDATE_MODELS until one succeeds."""
        last_error: Exception | None = None

        for model in GEMINI_CANDIDATE_MODELS:
            try:
                logger.info("Gemini request start model=%s", model)
                resp = self.client.models.generate_content(model=model, contents=contents)
                text = (resp.text or "").strip()
                if text:
                    logger.info("✅ Gemini success model=%s", model)
                    return text

            except Exception as e:
                last_error = e
                logger.exception("Gemini error for model=%s", model)
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Gemini generation failed with no response")

    @staticmethod
    def _local_chat_reply(messages: list[dict]) -> str:
        """Fallback reply for chat when Gemini is unavailable."""
        user_messages = [m.get("content", "") for m in messages if m.get("role") == "user"]
        latest = user_messages[-1].strip() if user_messages else "your message"
        return f"I can help with that. Here is a simple response to {latest}. (Gemini unavailable)"

    async def chat_completion(self, messages: list[dict]) -> str:
        """Chat completion with fallback for offline mode."""
        if not self.client:
            logger.warning("Gemini client unavailable, using local chat reply")
            return self._local_chat_reply(messages)

        try:
            prompt = ""
            for msg in messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n"
            return await self._generate_with_gemini(prompt)
        except Exception:
            logger.exception("Gemini error during chat completion")
            return self._local_chat_reply(messages)

    async def generate_story(self, prompt: str) -> str:
        """Generate story with Gemini. Raises on error (no fallback)."""
        if not self.client:
            logger.error("Gemini client unavailable: API key missing")
            raise RuntimeError("Gemini client unavailable: API key missing")

        story_prompt = (
            "You are a creative storyteller. Write a vivid, engaging story based on this prompt. "
            "Return only the story text.\n\n"
            f"Prompt: {prompt}"
        )

        try:
            return await self._generate_with_gemini(story_prompt)
        except Exception:
            logger.exception("Gemini error during story generation")
            raise


gemini_svc = GeminiService()
