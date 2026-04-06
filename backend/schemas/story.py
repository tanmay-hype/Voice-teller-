from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class StoryBase(BaseModel):
    title: str
    content: str
    audio_url: Optional[str] = None
    voice_id: Optional[UUID] = None

class StoryCreate(StoryBase):
    pass

class StoryInDBBase(StoryBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Story(StoryInDBBase):
    pass
