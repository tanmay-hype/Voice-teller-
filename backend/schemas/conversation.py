from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class ConversationBase(BaseModel):
    role: str
    content: str

class ConversationCreate(ConversationBase):
    pass

class ConversationInDBBase(ConversationBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Conversation(ConversationInDBBase):
    pass
