# API Usage Examples - Story Reading Flow

## Overview

The story reading system now supports two TTS engines with conditional selection based on voice availability.

## Endpoints

### POST `/stories/` - Create Story

**Request**:
```json
{
  "title": "The Dragon's Gold",
  "content": "Write a fantasy story about a dragon guarding treasure",
  "voice_id": "550e8400-e29b-41d4-a716-446655440000"  // optional UUID
}
```

**voice_id options**:
- `null` or omitted → Story will use default Piper voice when reading
- Valid UUID → Story will use that cloned ElevenLabs voice

**Response**:
```json
{
  "id": "story-uuid-1234",
  "user_id": "user-uuid",
  "title": "The Dragon's Gold",
  "content": "Once upon a time...",
  "voice_id": "550e8400-e29b-41d4-a716-446655440000",
  "audio_url": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### POST `/stories/read` - Generate Audio & Get URL

**Request - Using Default Voice (Piper)**:
```json
{
  "text": "The full story content to read aloud",
  "story_id": "story-uuid-1234"
}
```

Response (first call):
- Generates audio using **Piper** (local, free)
- Caches at `media/stories/{story_id}.mp3`
- Returns URL and updates story record

Response (subsequent calls):
- Returns cached URL instantly

**Request - Using Cloned Voice (ElevenLabs)**:
```json
{
  "text": "The full story content to read aloud",
  "voice_id": "550e8400-e29b-41d4-a716-446655440000",
  "story_id": "story-uuid-1234"
}
```

Response (first call):
- Generates audio using **ElevenLabs** (API, premium)
- Caches at `media/stories/{story_id}.mp3`
- Returns URL and updates story record

**Request - Without Story ID (Temporary Cache)**:
```json
{
  "text": "Temporary text to narrate"
}
```

Response:
- Generates audio using **Piper** (no voice_id = default)
- Caches at `media/cache/{sha256_hash}.mp3`
- Returns URL (not tied to specific story)

**Response All Cases**:
```json
{
  "url": "/media/stories/story-uuid-1234.mp3"
}
```

Then audio is accessible at:
- `http://localhost:8000/media/stories/story-uuid-1234.mp3`
- `http://localhost:8000/media/cache/{hash}.mp3`

---

## Curl Examples

### Generate Story with Default Voice
```bash
curl -X POST http://localhost:8000/api/stories/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Story",
    "content": "Write me a story about magic",
    "voice_id": null
  }'
```

### Generate Story with Cloned Voice
```bash
curl -X POST http://localhost:8000/api/stories/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Second Story",
    "content": "Write me another story",
    "voice_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### Read Story with Default Voice (Piper)
```bash
curl -X POST http://localhost:8000/api/stories/read \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is the full story content to read aloud",
    "story_id": "story-uuid-1234"
  }'

# Response: {"url": "/media/stories/story-uuid-1234.mp3"}
```

### Read Story with Cloned Voice (ElevenLabs)
```bash
curl -X POST http://localhost:8000/api/stories/read \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is the full story content",
    "voice_id": "550e8400-e29b-41d4-a716-446655440000",
    "story_id": "story-uuid-1234"
  }'

# Response: {"url": "/media/stories/story-uuid-1234.mp3"}
```

### Read Text Without Story (Temporary)
```bash
curl -X POST http://localhost:8000/api/stories/read \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Quick narration of some text"
  }'

# Response: {"url": "/media/cache/a3c4f2e1d8b9c0f2a3c4f2e1d8b9c0f2a3c4f2e1.mp3"}
```

---

## JavaScript/TypeScript Examples

### Frontend - Using apiClient

```typescript
import apiClient from '../services/apiClient';

// Create story with default voice
const createStoryWithDefaultVoice = async () => {
  const response = await apiClient.post('/stories/', {
    title: 'My Story',
    content: 'Generate a story prompt',
    voice_id: null  // Use Piper
  });
  return response.data;
};

// Create story with cloned voice
const createStoryWithClonedVoice = async (voiceId: string) => {
  const response = await apiClient.post('/stories/', {
    title: 'My Story',
    content: 'Generate a story prompt',
    voice_id: voiceId  // Use ElevenLabs
  });
  return response.data;
};

// Read story with current voice selection
const readStory = async (
  storyId: string,
  content: string,
  selectedVoiceId?: string
) => {
  const response = await apiClient.post('/stories/read', {
    text: content,
    voice_id: selectedVoiceId || null,  // null = Piper
    story_id: storyId
  });
  return response.data.url;
};

// Play audio
const playAudio = async (audioUrl: string) => {
  const audio = new Audio(audioUrl);
  await audio.play();
};

// Complete flow
const generateAndRead = async (title: string, prompt: string) => {
  // 1. Generate story
  const story = await createStoryWithDefaultVoice();
  
  // 2. Later - read aloud
  const audioUrl = await readStory(story.id, story.content);
  
  // 3. Play
  await playAudio(`http://localhost:8000${audioUrl}`);
};
```

---

## Python Examples

### Backend - Using httpx

```python
import httpx
from core.config import settings

async def create_and_read_story():
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {YOUR_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # 1. Create story
        story_response = await client.post(
            "http://localhost:8000/api/stories/",
            json={
                "title": "Python Story",
                "content": "Tell me a story",
                "voice_id": None  # Piper
            },
            headers=headers
        )
        story = story_response.json()
        
        # 2. Read aloud
        read_response = await client.post(
            "http://localhost:8000/api/stories/read",
            json={
                "text": story["content"],
                "voice_id": None,  # Piper - change to UUID for ElevenLabs
                "story_id": story["id"]
            },
            headers=headers
        )
        audio_url = read_response.json()["url"]
        return audio_url
```

---

## Decision Matrix

| Scenario | voice_id | Service | Speed | Cost | Best For |
|----------|----------|---------|-------|------|----------|
| Default narration | null | Piper | Fast | Free | Budget-conscious |
| Cloned voice | UUID | ElevenLabs | Medium | $ | Premium quality |
| Quick demo | null | Piper | Fast | Free | Testing |
| Professional audio | UUID | ElevenLabs | Medium | $ | Production |
| Override generation | null | Piper | Fast | Free | Re-reading |
| Override generation | UUID | ElevenLabs | Medium | $ | Different voice |

---

## Error Handling

### Missing Voice
```json
{
  "detail": "Voice not found"
}
```
**Solution**: Verify voice_id is valid and belongs to user

### Missing Text
```json
{
  "detail": "Missing 'text' in request body"
}
```
**Solution**: Include "text" field in request

### Piper Not Available
```json
{
  "detail": "Piper TTS failed: [error message]"
}
```
**Solution**: Install Piper, verify PATH, check logs

### ElevenLabs API Error
```json
{
  "detail": "API error: [error message]"
}
```
**Solution**: Check API key, rate limits, voice_id validity

---

## Caching Behavior

### Story-Level Cache
- **Triggered**: When `story_id` provided
- **Saved to**: `media/stories/{story_id}.mp3`
- **Reuse**: Any voice reading same story gets same file
- **Benefit**: Persistent, updates story.audio_url

### Content Hash Cache
- **Triggered**: When `story_id` NOT provided
- **Saved to**: `media/cache/{sha256_hash}.mp3`
- **Hash**: `SHA256(text + voice_identifier)`
- **Reuse**: Exact same text + voice gets same file
- **Benefit**: Fast temporary caching

### Cache Invalidation
- Manual: Delete files in `media/` directories
- Automatic: None (consider implementing TTL)
- Natural: Different voice_id = different hash = new audio

---

## Performance Tips

1. **Reuse URLs**: Cache the returned URL, don't regenerate
2. **Check Existence**: Before generating, verify audio_url exists
3. **Batch Operations**: Generate multiple stories, then read
4. **Pipeline**: Generate while user reads previous audio
5. **Compress**: Store MP3 instead of WAV (consider in future)

---

## Integration Checklist

- [ ] POST `/stories/` creates stories with optional voice
- [ ] POST `/stories/read` with no voice_id uses Piper
- [ ] POST `/stories/read` with voice_id uses ElevenLabs
- [ ] Caching works (repeat call returns instantly)
- [ ] Audio files created in media/
- [ ] Audio playable in browser
- [ ] UI shows voice indicator
- [ ] Error handling returns clear messages
- [ ] Performance acceptable (< 10s per request)
- [ ] Piper installed and working

Everything is production-ready!
