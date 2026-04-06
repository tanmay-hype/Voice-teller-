from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class VoiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    elevenlabs_voice_id: str

class VoiceCreate(VoiceBase):
    pass

class VoiceInDBBase(VoiceBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Voice(VoiceInDBBase):
    pass
