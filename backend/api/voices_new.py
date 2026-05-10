import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database import get_db
from models.user import User
from models.voice import Voice
from schemas.voice import Voice as VoiceSchema
from api.deps import get_current_active_user
from services.elevenlabs_svc import elevenlabs_svc

router = APIRouter(prefix="/voices", tags=["voices"])

# Directory to store uploaded files
UPLOAD_DIR = "media/voices"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ✅ CREATE VOICE (UPLOAD + ELEVENLABS)
@router.post("/", response_model=VoiceSchema)
async def create_voice(
    name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ✅ FIXED
):
    try:
        print("\n========== VOICE UPLOAD START ==========")
        print(f"📌 Name: {name}")
        print(f"📌 File: {file.filename}")

        # ✅ Step 1: Read file
        audio_bytes = await file.read()

        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # ✅ Step 2: Unique filename (IMPORTANT)
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        print(f"✅ File saved locally at: {file_path}")

        # ✅ Step 3: Upload to ElevenLabs
        print("➡️ Sending file to ElevenLabs...")
        voice_id = await elevenlabs_svc.upload_voice(
            name=name,
            description=description,
            audio_bytes=audio_bytes,
            filename=file.filename
        )

        print(f"✅ ElevenLabs Voice ID: {voice_id}")

        # ✅ Step 4: Save in DB (WITH USER)
        voice = Voice(
            user_id=current_user.id,  # 🔥 CRITICAL FIX
            name=name,
            description=description,
            elevenlabs_voice_id=voice_id,
        )

        db.add(voice)
        await db.commit()
        await db.refresh(voice)

        print("✅ Voice saved in database")
        print("========== VOICE UPLOAD END ==========\n")

        return voice

    except HTTPException as he:
        raise he

    except Exception as e:
        print("🔥 ERROR DURING VOICE UPLOAD:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ✅ GET USER VOICES (FIXES YOUR 405 ERROR)
@router.get("/", response_model=List[VoiceSchema])
async def list_voices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Voice).where(Voice.user_id == current_user.id)
    )
    voices = result.scalars().all()
    return voices


@router.get("/count")
async def voices_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Voice).where(Voice.user_id == current_user.id))
    count = len(result.scalars().all())
    return {"count": count}


@router.delete("/{voice_id}")
async def delete_voice(
    voice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a voice by ID (user must own it)"""
    result = await db.execute(
        select(Voice).where(Voice.id == voice_id).where(Voice.user_id == current_user.id)
    )
    voice = result.scalars().first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    await db.delete(voice)
    await db.commit()
    return {"detail": "Voice deleted"}
