import asyncio
import os
from worker.celery_app import celery_app
from services.elevenlabs_svc import elevenlabs_svc
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from models.story import Story

@celery_app.task(name="worker.tasks.generate_tts_task")
def generate_tts_task(story_id: str, text: str, voice_id: str):
    async def run_tts():
        try:
            audio_bytes = await elevenlabs_svc.text_to_speech(text, voice_id)
            # Find a local path to save the file
            filename = f"{story_id}.mp3"
            filepath = os.path.join(os.getcwd(), "media", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, "wb") as f:
                f.write(audio_bytes)
                
            # Update database
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Story).where(Story.id == story_id))
                story = result.scalars().first()
                if story:
                    story.audio_url = f"/media/{filename}"
                    await session.commit()
            print(f"Successfully generated and saved TTS for story {story_id}")
        except Exception as e:
            print(f"Error generating TTS for story {story_id}: {e}")
            
    asyncio.run(run_tts())
    return True
