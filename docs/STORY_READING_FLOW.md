# Story Reading Flow Implementation

## Overview
This implementation adds a complete voice-based story narration flow to your AI Voice Storytelling application.

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ USER GENERATES STORY                                        │
├─────────────────────────────────────────────────────────────┤
│  1. Enter story title                                       │
│  2. Enter story prompt                                      │
│  3. SELECT VOICE:                                           │
│     • Empty → Default voice (Piper) ✓ FREE, LOCAL          │
│     • Selected → Cloned voice (ElevenLabs) ✓ PREMIUM        │
│  4. Click "Generate Story"                                  │
│     → API generates story content                           │
│     → Saves to database with selected voice                 │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ VIEWING STORY                                               │
├─────────────────────────────────────────────────────────────┤
│  • Click story card to view full content                    │
│  • See story title and full text                            │
│  • If audio already generated, player shows existing audio  │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ READ ALOUD - NEW VOICE SELECTION                            │
├─────────────────────────────────────────────────────────────┤
│  • User can override voice selection                        │
│  • Choose different voice than generation voice            │
│  • Default: Piper (free)                                   │
│  • Optional: Any cloned voice (ElevenLabs)                 │
│                                                             │
│  Flow Decision:                                             │
│  ├─ IF no voice selected                                    │
│  │  └─→ Use PIPER (free, local TTS)                        │
│  │                                                          │
│  └─ IF voice selected                                      │
│     └─→ Use ELEVENLABS (cloned voice)                      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ AUDIO GENERATION & CACHING                                  │
├─────────────────────────────────────────────────────────────┤
│  • Generate narration using selected TTS service            │
│  • Cache by story_id if story provided                      │
│  • Cache by content hash for general use                    │
│  • Return audio URL                                         │
│  • Auto-play generated audio                                │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ LISTENING                                                   │
├─────────────────────────────────────────────────────────────┤
│  • Audio player displays                                    │
│  • Play/Resume controls available                           │
│  • Continues until end or user pauses                       │
└─────────────────────────────────────────────────────────────┘
```

## Code Changes

### 1. Backend: New Piper Service
**File**: `backend/services/piper_svc.py`

- **Purpose**: Free, local text-to-speech synthesis
- **Features**:
  - Finds Piper executable in system PATH
  - Locates default model files
  - Converts text to WAV audio
  - No API key required (fully local)
  - Suitable for default voice

```python
# Usage
await piper_svc.text_to_speech("Your story text here")
# Returns: bytes of audio data
```

### 2. Backend: Updated Stories API
**File**: `backend/api/stories.py`

#### Import Piper Service
```python
from services.piper_svc import piper_svc
```

#### Updated POST `/stories/read` Endpoint
The endpoint now implements the voice selection logic:

```python
@router.post("/read")
async def read_story_tts(payload: dict, ...):
    """
    CONDITIONAL VOICE FLOW:
    1. No voice_id → Use Piper (default, free)
    2. voice_id provided → Use ElevenLabs (cloned voice)
    """
    text = payload.get("text")
    voice_uuid = payload.get("voice_id")  # Optional
    story_id = payload.get("story_id")    # Optional
    
    # Determine which TTS service to use
    use_piper = not voice_uuid  # No voice = default
    
    if use_piper:
        audio_bytes = await piper_svc.text_to_speech(text)
    else:
        audio_bytes = await elevenlabs_svc.text_to_speech(text, voice_id)
```

**Caching Strategy**:
- If `story_id` provided → Cache in `media/stories/{story_id}.mp3`
- Otherwise → Cache in `media/cache/{content_hash}.mp3`
- Hash includes voice identifier for different voice = different cache

### 3. Frontend: Enhanced Stories Component
**File**: `frontend/src/pages/Stories.tsx`

#### Story Generation Modal
- **Title**: Story title input
- **Prompt**: Story prompt textarea
- **Voice Selection**: 
  - Default: "Default voice (Piper)" - free, local
  - Options: All cloned voices from database
- **Visual Indicator**: Shows which TTS service will be used

#### Story View Modal - "Read Aloud" Section
- **Voice Selector**: Choose voice for THIS reading (can differ from generation voice)
- **Voice Indicator**: Shows "🎙️ Piper" vs "🤖 ElevenLabs"
- **Read Aloud Button**: Triggers API call with selected voice
- **Playback Controls**: Play/Pause/Resume for generated audio

#### State Management
- `selectedVoiceForReading`: Independent from story's original voice
- Users can read same story with different voices
- Caching ensures repeated readings are instant

## API Contract

### POST `/stories/read`
**Request**:
```json
{
  "text": "Your story text here",
  "voice_id": "uuid-or-null",  // null = Piper, uuid = ElevenLabs
  "story_id": "story-uuid"     // optional, for story-level caching
}
```

**Response**:
```json
{
  "url": "/media/stories/{story_id}.mp3"
  // or
  "url": "/media/cache/{hash}.mp3"
}
```

## Decision Logic: Which TTS Service?

| Scenario | Voice ID | Service | Cost | Latency |
|----------|----------|---------|------|---------|
| Default voice | null/empty | Piper | FREE | Fast (local) |
| Cloned voice selected | UUID | ElevenLabs | $ per char | Med (API) |
| Override in read | null/empty | Piper | FREE | Fast |
| Override in read | UUID | ElevenLabs | $ per char | Med |

## Installation Requirements

### Piper Setup
```bash
# Install Piper (example - adapt to your OS)
# macOS
brew install piper-phoneme-tool

# Linux
sudo apt-get install piper

# Or download from: https://github.com/rhasspy/piper/releases
```

### Environment
- No API key needed for Piper
- ElevenLabs API key still required in `.env` for cloned voices
- Both services work independently and in parallel

## Caching Strategy

### Story-level Cache
- **Path**: `media/stories/{story_id}.mp3`
- **Trigger**: When `story_id` provided in request
- **Benefit**: Persistent per story, survives voice changes
- **Use Case**: Fixed narration for story archive

### Content Hash Cache
- **Path**: `media/cache/{sha256_hash}.mp3`
- **Hash Input**: Text + Voice identifier
- **Trigger**: When `story_id` not provided
- **Benefit**: Fast repeated reads, different text = different audio
- **TTL**: No auto-cleanup (manual or scheduled cleanup optional)

## User Experience Flow

1. **Create Story**
   - User enters title, prompt
   - Selects voice (default = Piper)
   - Clicks "Generate"
   - Story appears in grid

2. **View Story**
   - Click story card
   - Modal opens with full text
   - See voice that was used for generation

3. **Read Aloud**
   - In modal, select voice (can be different!)
   - Click "Read Aloud"
   - If Piper: Instant local processing
   - If ElevenLabs: Slightly longer (API call)
   - Audio generated and plays automatically

4. **Playback**
   - Player shows with controls
   - User can pause/resume
   - Can change voice and re-read (new audio cached)

## Testing Checklist

- [ ] Create story without voice → Uses Piper
- [ ] Create story with voice → Uses ElevenLabs
- [ ] Read story with default voice → Piper service
- [ ] Read story with cloned voice → ElevenLabs service
- [ ] Override voice when reading → Uses new voice
- [ ] Cache hit on repeat read → Same audio
- [ ] Audio file generation → File created in media/
- [ ] UI shows correct voice indicator
- [ ] Loading states work correctly
- [ ] Error handling for missing voices
- [ ] Audio playback works in browser

## Future Enhancements

1. **Multiple Voice Models**: Let users choose different Piper models
2. **Audio Quality Settings**: Speed, stability (ElevenLabs)
3. **Auto-narration**: Generate audio when creating story
4. **Batch Processing**: Generate audio for multiple stories
5. **Subtitle Sync**: Show text while audio plays
6. **Voice Analytics**: Track which voices are used
7. **Custom Voices**: Fine-tune ElevenLabs voices
8. **Download Audio**: Save generated audio files
9. **Scheduled Cleanup**: Auto-delete old cache files
10. **Voice Preview**: 5-second sample of voice before reading

## Troubleshooting

### Piper Not Found
```
Error: Piper executable not found
Solution: Install Piper or add to PATH
```

### No Audio Generated
- Check Piper is installed and accessible
- Verify API keys (if using ElevenLabs)
- Check media directory permissions

### Slow Audio Generation
- Piper: Check system resources, local performance
- ElevenLabs: Check API rate limits, network latency

### Audio Quality Issues
- Piper: Model files might be incomplete
- ElevenLabs: Check voice_id and stability settings
