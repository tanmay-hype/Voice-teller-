from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


# 🔹 Base (shared fields)
class StoryBase(BaseModel):
    title: str
    content: str
    voice_id: Optional[UUID] = None


# 🔥 INPUT SCHEMA (FROM FRONTEND)
class StoryCreate(StoryBase):
    pass


# 🔹 INTERNAL / DB SCHEMA
class StoryInDBBase(StoryBase):
    id: UUID
    user_id: UUID
    audio_url: Optional[str] = None  # ✅ Backend generated
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# 🔥 RESPONSE SCHEMA (WHAT FRONTEND GETS)
class Story(StoryInDBBase):
    pass