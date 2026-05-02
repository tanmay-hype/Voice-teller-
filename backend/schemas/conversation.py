from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

# ✅ Base model (used internally + responses)
class ConversationBase(BaseModel):
    role: str
    content: str


# ✅ Input model (what frontend sends)
class ConversationCreate(BaseModel):
    content: str   # 🔥 ONLY content, no role


# ✅ DB model
class ConversationInDBBase(ConversationBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ✅ Final response model
class Conversation(ConversationInDBBase):
    pass