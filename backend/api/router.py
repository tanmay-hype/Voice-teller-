from fastapi import APIRouter
from api.auth import router as auth_router
from api.voices import router as voices_router
from api.stories import router as stories_router
from api.chat import router as chat_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(voices_router)
api_router.include_router(stories_router)
api_router.include_router(chat_router)

# We will include other routers here later (e.g. auth, users, stories, voices)
