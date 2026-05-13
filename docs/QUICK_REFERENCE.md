# Quick Reference: Story Reading Flow

## The Flow (One Picture)

```
┌─────────────────────────────────────────────────────────────────┐
│  USER: Creates Story                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Title: "Dragon's Tale"                                │   │
│  │ • Prompt: "Write a story about..."                       │   │
│  │ • Voice: [Default Piper] ← Can select cloned voice       │   │
│  │ • Click: Generate Story                                  │   │
│  └────────────────┬──────────────────────────────────────┬──┘   │
└─────────────────┼──────────────────────────────────────┼────────┘
                  │                                        │
                  ▼                                        ▼
         ┌──────────────────┐              ┌──────────────────────┐
         │  Backend         │              │  Database            │
         │  Generates Story │              │  Stores Story with   │
         │  (via Gemini)    │              │  selected voice      │
         └──────────────────┘              └──────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND: Story Grid                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [Story Card: "Dragon's Tale"]                           │   │
│  │ Click to view detail...                                  │   │
│  └────────────────────────────┬──────────────────────────┬──┘   │
└─────────────────────────────┼──────────────────────────┼────────┘
                              │
                              ▼
                   ┌────────────────────────┐
                   │ Story Detail Modal     │
                   │ • Full content         │
                   │ • "READ ALOUD" section │
                   └────────────────────────┘
                              │
                   ┌──────────┴──────────┐
                   │                     │
                   ▼                     ▼
            ┌─────────────────────┐  ┌──────────────────────┐
            │ Voice Selector      │  │ Read Aloud Button    │
            │ • Default (Piper)   │  │ (User clicks this)   │
            │ • Cloned voices     │  │                      │
            │   (if available)    │  │                      │
            └─────────────────────┘  └──────┬───────────────┘
                   │                         │
                   └─────────────┬───────────┘
                                 ▼
                    ┌─────────────────────────────┐
                    │ DECISION POINT (Backend)    │
                    └──────────┬──────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
         ┌──────▼──────────┐        ┌────────▼────────────┐
         │ NO VOICE        │        │ VOICE SELECTED      │
         │                 │        │                     │
         │ Use PIPER       │        │ Use ELEVENLABS      │
         │                 │        │                     │
         │ • Local TTS     │        │ • API TTS           │
         │ • FREE          │        │ • Premium Quality   │
         │ • Fast          │        │ • Cloned Voice      │
         └────────┬────────┘        └────────┬────────────┘
                  │                          │
                  └──────────────┬───────────┘
                                 ▼
                      ┌────────────────────────┐
                      │ Generate Audio File    │
                      │ (bytes)                │
                      └────────────┬───────────┘
                                   │
                                   ▼
                      ┌────────────────────────┐
                      │ Cache Audio            │
                      │ media/stories/         │
                      │ {story_id}.mp3         │
                      └────────────┬───────────┘
                                   │
                                   ▼
                      ┌────────────────────────┐
                      │ Return URL to Frontend │
                      └────────────┬───────────┘
                                   │
                                   ▼
                      ┌────────────────────────┐
                      │ Frontend: Audio Player │
                      │ Auto-plays audio       │
                      │ Play/Pause controls    │
                      └────────────────────────┘
```

## Voice Decision Tree

```
   START: "Read Aloud" clicked
           │
           ▼
   ┌───────────────────┐
   │ Voice Selected?   │
   └───────┬───────────┘
           │
    ┌──────┴──────┐
    │             │
 EMPTY/NULL   UUID/SELECTED
    │             │
    ▼             ▼
  PIPER      ELEVENLABS
   FREE      PREMIUM
   LOCAL     API
   FAST      HIGH-QUALITY
```

## What Changed in Your Code

### 1. Backend: New File
**File**: `backend/services/piper_svc.py`
```python
# NEW SERVICE FOR LOCAL TTS
class PiperService:
    async def text_to_speech(text: str) -> bytes
```

### 2. Backend: Updated File
**File**: `backend/api/stories.py`
```python
# ADDED THIS LOGIC TO POST /stories/read

if voice_id is None:
    # Use local TTS
    audio = await piper_svc.text_to_speech(text)
else:
    # Use ElevenLabs API
    audio = await elevenlabs_svc.text_to_speech(text, voice_id)
```

### 3. Frontend: Updated File
**File**: `frontend/src/pages/Stories.tsx`
```typescript
// ADDED VOICE SELECTOR FOR READING
<select onChange={(e) => setSelectedVoiceForReading(e.target.value)}>
  <option>Default (Piper)</option>
  {voices.map(v => <option>{v.name}</option>)}
</select>

// ADDED READ ALOUD SECTION
<button onClick={handleReadAloud}>
  {selectedVoiceForReading ? "ElevenLabs" : "Piper"}
</button>
```

## Usage Flow in 5 Steps

### Step 1: Generate
User creates story and optionally selects voice
```
Title: "My Story"
Prompt: "Write about..."
Voice: [Default / Amy / David / ...]
```

### Step 2: View
Story appears in grid, user clicks it
```
[Story Card] → Click → Detail Modal Opens
```

### Step 3: Select Voice for Reading
User chooses voice (can be different from generation)
```
Voice selector: Default ← (currently selected)
                Amy
                David
                ...
```

### Step 4: Read Aloud
User clicks button, audio generates
```
"Read Aloud" button clicked
↓
Backend decides: Use Piper or ElevenLabs?
↓
Generate audio
↓
Save to cache
↓
Return URL
```

### Step 5: Listen
Audio plays automatically
```
🎵 Audio player with play/pause controls
```

## Installation (One Command)

```bash
# macOS
brew install piper-phoneme-tool

# Linux
sudo apt-get install piper

# Then download model
mkdir -p ~/.local/share/piper/models
wget -O ~/.local/share/piper/models/en_US-amy-medium.onnx \
  https://huggingface.co/rhasspy/piper/releases/download/v1.0.0/en_US-amy-medium.onnx
```

## API Requests (Simplified)

### Create Story with Default Voice
```bash
POST /stories/
{
  "title": "My Story",
  "content": "Write a story...",
  "voice_id": null  # Use Piper
}
```

### Create Story with Cloned Voice
```bash
POST /stories/
{
  "title": "My Story",
  "content": "Write a story...",
  "voice_id": "uuid-of-voice"  # Use ElevenLabs
}
```

### Read Story (Decision Point)
```bash
POST /stories/read
{
  "text": "story content",
  "voice_id": null,  # → PIPER (local, free)
  "story_id": "uuid"
}
```

OR

```bash
POST /stories/read
{
  "text": "story content",
  "voice_id": "uuid",  # → ELEVENLABS (API, premium)
  "story_id": "uuid"
}
```

## Cost Comparison

| Service | Cost | Speed | Quality | Location |
|---------|------|-------|---------|----------|
| Piper | FREE | Fast | Good | Local |
| ElevenLabs | $ | Medium | Premium | API |

## Files to Know

| File | Purpose | Status |
|------|---------|--------|
| `backend/services/piper_svc.py` | New TTS service | ✅ NEW |
| `backend/api/stories.py` | API endpoint | ✅ UPDATED |
| `frontend/src/pages/Stories.tsx` | UI | ✅ UPDATED |
| `STORY_READING_FLOW.md` | Documentation | ✅ NEW |
| `API_USAGE_EXAMPLES.md` | API examples | ✅ NEW |
| `ARCHITECTURE_OVERVIEW.md` | Architecture | ✅ NEW |

## Testing Checklist (5 items)

- [ ] Install Piper: `brew install piper-phoneme-tool`
- [ ] Start backend: `python -m uvicorn backend.main:app`
- [ ] Start frontend: `npm run dev`
- [ ] Create story → "Read Aloud" with default voice (should work)
- [ ] Select cloned voice → "Read Aloud" (should work if ElevenLabs configured)

## Success Criteria

✅ Story generation works
✅ Read Aloud with Piper works (default, free)
✅ Read Aloud with ElevenLabs works (if configured)
✅ Audio caches properly
✅ Voice selector appears in UI
✅ Service indicator shows correct TTS
✅ Audio plays in browser
✅ Can override voice on re-read

## What's Next

1. Install Piper ✅
2. Test the flow locally
3. Deploy with Docker
4. Collect feedback
5. Optimize performance if needed
6. Add more features (voice preview, batch, etc.)

---

**Status**: ✅ Implementation Complete, Ready for Testing

Need help? See the documentation files in the project root.
