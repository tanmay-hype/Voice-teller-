import asyncio
import os
from worker.celery_app import celery_app
from services.elevenlabs_svc import elevenlabs_svc
from services.media_storage import media_storage_svc
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from models.story import Story

@celery_app.task(name="worker.tasks.generate_tts_task")
def generate_tts_task(story_id: str, text: str, voice_id: str):
    async def run_tts():
        try:
            audio_bytes = await elevenlabs_svc.text_to_speech(text, voice_id)
            filename = f"{story_id}.mp3"
            audio_url = await media_storage_svc.store_audio(
                filename=filename,
                audio_bytes=audio_bytes,
                folder="stories",
                content_type="audio/mpeg",
            )
                
            # Update database
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Story).where(Story.id == story_id))
                story = result.scalars().first()
                if story:
                    story.audio_url = audio_url
                    await session.commit()
            print(f"Successfully generated and saved TTS for story {story_id}")
        except Exception as e:
            print(f"Error generating TTS for story {story_id}: {e}")
            
    asyncio.run(run_tts())
    return True
