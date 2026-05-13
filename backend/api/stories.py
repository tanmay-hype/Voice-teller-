import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from fastapi.responses import Response, JSONResponse
import hashlib
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.user import User
from models.story import Story
from models.voice import Voice
from schemas.story import Story as StorySchema, StoryCreate
from api.deps import get_current_active_user
from services.gemini_svc import gemini_svc
from services.elevenlabs_svc import elevenlabs_svc
from services.piper_svc import piper_svc
from services.media_storage import media_storage_svc

router = APIRouter(prefix="/stories", tags=["stories"])

@router.post("/", response_model=StorySchema)
async def create_story(
    story_in: StoryCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify voice belongs to user if provided
    if story_in.voice_id:
        result = await db.execute(
            select(Voice).where(Voice.id == story_in.voice_id).where(Voice.user_id == current_user.id)
        )
        if not result.scalars().first():
            raise HTTPException(status_code=404, detail="Voice not found")

    # Generate story using Gemini or local fallback
    try:
        generated_content = await gemini_svc.generate_story(story_in.content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save to DB
    story = Story(
        user_id=current_user.id,
        title=story_in.title,
        content=generated_content,
        voice_id=story_in.voice_id
    )
    db.add(story)
    await db.commit()
    await db.refresh(story)

    if story.voice_id:
        from worker.tasks import generate_tts_task
        generate_tts_task.delay(str(story.id), story.content, str(story.voice_id))

    return story

@router.get("/", response_model=List[StorySchema])
async def list_stories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Story).where(Story.user_id == current_user.id))
    return result.scalars().all()


@router.get("/count")
async def stories_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Story).where(Story.user_id == current_user.id))
    count = len(result.scalars().all())
    return {"count": count}


@router.post("/read")
async def read_story_tts(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    FLOW:
    1. Generate Story
       ↓
    2. Read Aloud
       ↓
    3. Voice Selection:
       - No voice_id (default) → Piper (free, local TTS)
       - voice_id provided (cloned voice available + selected) → ElevenLabs
    
    Accepts JSON {text, voice_id?, story_id?} and returns JSON {url}.
    - If `story_id` provided and audio exists, return cached URL
    - Otherwise generate audio with appropriate service, save to media, and return URL
    """
    text = payload.get("text")
    voice_uuid = payload.get("voice_id")  # Voice record UUID (if provided)
    story_id = payload.get("story_id")

    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' in request body")

    try:
        # Determine which TTS service to use
        use_piper = not voice_uuid  # No voice_id = use default Piper
        elevenlabs_voice_id = None
        audio_extension = "wav" if use_piper else "mp3"
        audio_content_type = "audio/wav" if use_piper else "audio/mpeg"

        if not use_piper:
            # 🔥 CRITICAL: Look up Voice record to get ElevenLabs voice_id
            result = await db.execute(
                select(Voice).where(Voice.id == voice_uuid).where(Voice.user_id == current_user.id)
            )
            voice = result.scalars().first()
            if not voice:
                raise HTTPException(status_code=404, detail="Voice not found")
            elevenlabs_voice_id = voice.elevenlabs_voice_id

        # If story_id provided, save under media/stories/{story_id}.mp3
        if story_id:
            # Verify ownership
            result = await db.execute(
                select(Story).where(Story.id == story_id).where(Story.user_id == current_user.id)
            )
            story = result.scalars().first()
            if not story:
                raise HTTPException(status_code=404, detail="Story not found")

            if story.audio_url:
                local_audio_path = story.audio_url.lstrip("/")
                if story.audio_url.startswith("http") or os.path.exists(local_audio_path):
                    return JSONResponse({"url": story.audio_url})

            # Generate audio with appropriate service
            if use_piper:
                print("🎙️  Using Piper (default voice)...")
                audio_bytes = await piper_svc.text_to_speech(text)
            else:
                print("🎙️  Using ElevenLabs (cloned voice)...")
                audio_bytes = await elevenlabs_svc.text_to_speech(text, elevenlabs_voice_id)

            filename = f"{story_id}.{audio_extension}"
            story.audio_url = await media_storage_svc.store_audio(
                filename=filename,
                audio_bytes=audio_bytes,
                folder="stories",
                content_type=audio_content_type,
            )
            db.add(story)
            await db.commit()

            return JSONResponse({"url": story.audio_url})

        # No story_id: use content hash cache under media/cache/
        # Hash includes voice info
        voice_key = "piper_default" if use_piper else elevenlabs_voice_id
        combined = (text + voice_key).encode("utf-8")
        h = hashlib.sha256(combined).hexdigest()
        
        filename = f"{h}.{audio_extension}"
        local_cache_path = os.path.join(os.getcwd(), "media", "cache", filename)

        if not media_storage_svc._should_use_supabase() and os.path.exists(local_cache_path):
            return JSONResponse({"url": f"/media/cache/{filename}"})

        # Generate audio with appropriate service
        if use_piper:
            print("🎙️  Using Piper (default voice)...")
            audio_bytes = await piper_svc.text_to_speech(text)
        else:
            print("🎙️  Using ElevenLabs (cloned voice)...")
            audio_bytes = await elevenlabs_svc.text_to_speech(text, elevenlabs_voice_id)

        audio_url = await media_storage_svc.store_audio(
            filename=filename,
            audio_bytes=audio_bytes,
            folder="cache",
            content_type=audio_content_type,
        )

        return JSONResponse({"url": audio_url})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{story_id}")
async def delete_story(
    story_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a story by ID (user must own it)"""
    result = await db.execute(
        select(Story).where(Story.id == story_id).where(Story.user_id == current_user.id)
    )
    story = result.scalars().first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    await db.delete(story)
    await db.commit()
    return {"detail": "Story deleted"}
