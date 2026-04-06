import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.user import User
from models.voice import Voice
from schemas.voice import Voice as VoiceSchema, VoiceCreate
from api.deps import get_current_active_user
from services.elevenlabs_svc import elevenlabs_svc

router = APIRouter(prefix="/voices", tags=["voices"])

@router.post("/", response_model=VoiceSchema)
async def create_voice(
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Read audio bytes
    audio_bytes = await file.read()
    
    # Upload to ElevenLabs
    try:
        voice_id = await elevenlabs_svc.upload_voice(
            name=name,
            description=description,
            audio_bytes=audio_bytes,
            filename=file.filename or "sample.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Save to db
    voice = Voice(
        user_id=current_user.id,
        name=name,
        description=description,
        elevenlabs_voice_id=voice_id
    )
    db.add(voice)
    await db.commit()
    await db.refresh(voice)
    
    return voice

@router.get("/", response_model=List[VoiceSchema])
async def list_voices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Voice).where(Voice.user_id == current_user.id))
    return result.scalars().all()
