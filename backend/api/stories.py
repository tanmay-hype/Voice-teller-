import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.user import User
from models.story import Story
from models.voice import Voice
from schemas.story import Story as StorySchema, StoryCreate
from api.deps import get_current_active_user
from services.openai_svc import openai_svc
from services.elevenlabs_svc import elevenlabs_svc

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

    # Generate story using OpenAI
    try:
        generated_content = await openai_svc.generate_story(story_in.content)
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
