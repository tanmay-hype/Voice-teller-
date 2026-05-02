from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database import get_db
from models.user import User
from models.conversation import Conversation
from schemas.conversation import Conversation as ConversationSchema, ConversationCreate
from api.deps import get_current_active_user
from services.gemini_svc import gemini_svc

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ConversationSchema)
async def chat_interaction(
    chat_in: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
       
        user_msg = Conversation(
            user_id=current_user.id,
            role="user",
            content=chat_in.content
        )
        db.add(user_msg)
        await db.commit()

        
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == current_user.id)
            .order_by(Conversation.created_at.asc())
        )
        history = result.scalars().all()

        
        messages = []
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

       
        reply_content = await gemini_svc.chat_completion(messages)

      
        assistant_msg = Conversation(
            user_id=current_user.id,
            role="assistant",
            content=reply_content
        )
        db.add(assistant_msg)
        await db.commit()
        await db.refresh(assistant_msg)

        return assistant_msg

    except Exception as e:
        print("🔥 CHAT ERROR:", str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ConversationSchema])
async def get_chat_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.asc())
    )
    return result.scalars().all()