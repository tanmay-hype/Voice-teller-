# Story Reading Flow - Architecture & Visual Reference

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Story Generation Flow:                                                    │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │ 1. New Story Modal                                          │           │
│  │    • Title input                                            │           │
│  │    • Prompt textarea                                        │           │
│  │    • Voice selector (Default Piper / Cloned voices)         │           │
│  │    • Submit → POST /stories/                                │           │
│  └────────────────────────┬────────────────────────────────────┘           │
│                           │                                                 │
│  Story View & Reading:                                                    │
│  ┌────────────────────────▼────────────────────────────────────┐           │
│  │ 2. Story Detail Modal                                       │           │
│  │    ┌──────────────────────────────────────────────────┐     │           │
│  │    │ Story Title & Content Display                    │     │           │
│  │    └──────────────────────────────────────────────────┘     │           │
│  │                                                             │           │
│  │    ┌──────────────────────────────────────────────────┐     │           │
│  │    │ READ ALOUD SECTION                               │     │           │
│  │    │ • Voice selector (can override generation)       │     │           │
│  │    │ • Service indicator (Piper/ElevenLabs)           │     │           │
│  │    │ • \"Read Aloud\" button → POST /stories/read      │     │           │
│  │    └────────────────────┬─────────────────────────────┘     │           │
│  │                         │                                    │           │
│  │    ┌────────────────────▼─────────────────────────────┐     │           │
│  │    │ Audio Playback                                   │     │           │
│  │    │ • HTML5 Audio Player                             │     │           │
│  │    │ • Play/Pause/Resume controls                     │     │           │
│  │    └──────────────────────────────────────────────────┘     │           │
│  └──────────────────────────────────────────────────────────┘   │           │
│                                                                 │           │
└─────────────────────────────────────────────────────────────────┼───────────┘
                                                                  │ HTTP
                        ┌─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  API Router: api/stories.py                                               │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │ POST /stories/                                               │          │
│  │ • Receive: {title, content, voice_id?}                      │          │
│  │ • Call: gemini_svc.generate_story()                         │          │
│  │ • Save: Story record to DB                                  │          │
│  │ • Return: Story with ID                                     │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │ POST /stories/read  🔥 NEW CONDITIONAL LOGIC                │          │
│  │                                                              │          │
│  │ • Receive: {text, voice_id?, story_id?}                    │          │
│  │                                                              │          │
│  │ • Decision Point:                                           │          │
│  │   if voice_id is None/Empty:                                │          │
│  │     └─→ USE PIPER (default)                                │          │
│  │   else:                                                      │          │
│  │     └─→ USE ELEVENLABS (cloned voice)                      │          │
│  │                                                              │          │
│  │ • Caching:                                                   │          │
│  │   if story_id provided:                                      │          │
│  │     └─→ media/stories/{story_id}.mp3                        │          │
│  │   else:                                                      │          │
│  │     └─→ media/cache/{hash}.mp3                              │          │
│  │                                                              │          │
│  │ • Return: {url}                                             │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                             │
└─────────────────┬────────────────────────┬────────────────────────┬───────────┘
                  │                        │                        │
                  ▼                        ▼                        ▼
    ┌──────────────────────┐  ┌──────────────────────┐  ┌─────────────────────┐
    │  PIPER SERVICE       │  │  ELEVENLABS SERVICE  │  │   DATABASE          │
    │  (Local TTS)         │  │  (Cloned Voices)     │  │   (Story Records)   │
    │                      │  │                      │  │                     │
    │ • No API key         │  │ • API key required   │  │ • story.id          │
    │ • Fast (local)       │  │ • Premium quality    │  │ • story.content     │
    │ • Free               │  │ • API latency        │  │ • story.voice_id    │
    │ • Returns WAV bytes  │  │ • Returns MP3 bytes  │  │ • story.audio_url   │
    │                      │  │                      │  │ • story.user_id     │
    │ text_to_speech()     │  │ text_to_speech()     │  │                     │
    │ → bytes              │  │ → bytes              │  │                     │
    └──────────┬───────────┘  └──────────┬───────────┘  └─────────────────────┘
               │                         │
               └────────────┬────────────┘
                            ▼
              ┌────────────────────────────┐
              │   FILE STORAGE (media/)    │
              │                            │
              │ /media/stories/            │
              │   {story_id}.mp3           │
              │ /media/cache/              │
              │   {hash}.mp3               │
              └────────────────────────────┘
```

## Request/Response Flow Diagram

```
FRONTEND REQUEST TO BACKEND
═════════════════════════════

Case 1: Generate Story (Default Voice)
─────────────────────────────────────

POST /api/stories/
{
  "title": "Dragon's Tale",
  "content": "Write a story...",
  "voice_id": null
}
                    │
                    ▼
            Database: Store Story
            voice_id = null
                    │
                    ▼
            Response: Story object
            {
              "id": "uuid-123",
              "content": "generated...",
              "voice_id": null
            }
                    │
                    ▼
            Frontend: Story appears in grid
            Voice used will be: PIPER (default)


Case 2: Read Story (Conditional Voice Selection)
──────────────────────────────────────────────────

POST /api/stories/read
{
  "text": "story content...",
  "voice_id": null,           ← User selected "Default Voice"
  "story_id": "uuid-123"
}
                    │
                    ▼
            Decision: voice_id is null?
                    │
       ┌────────────┴────────────┐
       │ YES                      │ NO
       ▼                          ▼
    USE PIPER               USE ELEVENLABS
    text → bytes            text + voice_uuid → bytes
    (local, fast)           (API, slower)
       │                          │
       └────────────┬─────────────┘
                    ▼
            Save to media/stories/{id}.mp3
            Update story.audio_url
                    │
                    ▼
            Response: {url: "/media/stories/uuid-123.mp3"}
                    │
                    ▼
            Frontend: Set audio.src = url
            Audio auto-plays
```

## Voice Selection Decision Tree

```
User clicks "Read Aloud"
        │
        ▼
┌─────────────────────────────┐
│ Voice Selector State?       │
└──────────────┬──────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
   Empty/Null      UUID/Selected
   (Default)       (Cloned)
      │                 │
      ▼                 ▼
┌─────────────┐   ┌──────────────────┐
│   PIPER     │   │   ELEVENLABS     │
├─────────────┤   ├──────────────────┤
│ Cost: FREE  │   │ Cost: $ per char │
│ Speed: FAST │   │ Speed: MEDIUM    │
│ Location:   │   │ Location: API    │
│ LOCAL       │   │                  │
│             │   │ Quality: HIGH    │
│ Quality:    │   │                  │
│ GOOD        │   │ Cloned voice     │
│             │   │ personality      │
└──────┬──────┘   └────────┬─────────┘
       │                   │
       └───────────┬───────┘
                   ▼
          Generate Audio Bytes
                   │
                   ▼
          Save to media/{path}
                   │
                   ▼
          Return URL to Frontend
                   │
                   ▼
          Audio plays in browser
```

## Data Flow: Story Creation to Reading

```
1. USER ACTION
   ┌──────────────────────────┐
   │ Click "New Story"        │
   │ Fill form:               │
   │ • Title: "My Tale"       │
   │ • Prompt: "..."          │
   │ • Voice: [Default/Amy]   │
   │ Click Generate           │
   └────────────┬─────────────┘
                │
                ▼
2. FRONTEND SENDS
   POST /stories/
   {
     title: "My Tale",
     content: "...",
     voice_id: null or "uuid"
   }
                │
                ▼
3. BACKEND PROCESSES
   • Generate story via Gemini
   • Create Story record
   • Save voice_id if provided
   • Return story object
                │
                ▼
4. FRONTEND STATE UPDATE
   • Add story to stories array
   • Story appears in grid
   • Close modal
   • Display in grid
                │
                ▼
5. USER ACTION
   Click story card
   Story detail modal opens
                │
                ▼
6. READ ALOUD SECTION SHOWS
   • Voice selector (can change!)
   • "Read Aloud" button
   • Service indicator
                │
                ▼
7. USER ACTION
   Select voice (or keep default)
   Click "Read Aloud"
                │
                ▼
8. FRONTEND SENDS
   POST /stories/read
   {
     text: story.content,
     voice_id: selectedVoiceForReading,
     story_id: story.id
   }
                │
                ▼
9. BACKEND DECISION
   ┌─ if voice_id is null
   │  └─ Use Piper
   └─ else
      └─ Use ElevenLabs
                │
                ▼
10. TTS SERVICE GENERATES
    Piper: text → bytes (local)
    OR
    ElevenLabs: text + voice_id → bytes (API)
                │
                ▼
11. BACKEND SAVES & RETURNS
    Save bytes to media/stories/{id}.mp3
    Return {url: "/media/stories/{id}.mp3"}
                │
                ▼
12. FRONTEND PLAYS
    new Audio(url).play()
    Display player with controls
    Show play/pause buttons
                │
                ▼
13. USER LISTENS
    Hears story narration
    Can pause/resume
    Can close and reopen
    (cache prevents re-generation)
```

## Technology Stack Summary

| Component | Technology | Role |
|-----------|-----------|------|
| Frontend | React + TypeScript | UI, voice selection, audio playback |
| Backend | FastAPI (Python) | API, routing, TTS orchestration |
| TTS #1 | Piper | Default voice (local, free) |
| TTS #2 | ElevenLabs | Cloned voice (API, premium) |
| Database | PostgreSQL | Story records, voice metadata |
| AI | Google Gemini | Story generation |
| Storage | File system | Audio files in media/ |
| Caching | File system + Hash | Fast re-reads, no re-generation |

## Performance Metrics

| Operation | Piper | ElevenLabs |
|-----------|-------|-----------|
| Cold Generate | ~5-10s | ~2-5s |
| Cache Hit | Instant | Instant |
| Text Length | Scales linearly | Scales linearly |
| Concurrent | Can parallelize | Rate limited |
| Model Size | ~100MB | N/A (cloud) |
| Storage | WAV files | MP3 files |

## File Structure Changes

```
backend/
  services/
    piper_svc.py          ← NEW: Piper TTS service
    elevenlabs_svc.py     (unchanged)
    gemini_svc.py         (unchanged)
  api/
    stories.py            ← UPDATED: New conditional logic
    
frontend/
  src/pages/
    Stories.tsx           ← UPDATED: Enhanced UI

media/                    ← Gets created at runtime
  stories/
    {story-id}.mp3        ← Story-specific audio
  cache/
    {hash}.mp3            ← Temporary cached audio

Documentation/
  STORY_READING_FLOW.md   ← NEW: Flow documentation
  PIPER_SETUP_GUIDE.md    ← NEW: Installation guide
  API_USAGE_EXAMPLES.md   ← NEW: API examples
```

## Environment Variables

```bash
# Required - Existing
ELEVENLABS_API_KEY=your_key_here

# Optional - Piper paths (auto-detected if in PATH)
PIPER_EXECUTABLE=/usr/bin/piper
PIPER_MODEL_PATH=/root/.local/share/piper/models/en_US-amy-medium.onnx
```

---

This architecture provides:
- ✅ Flexibility: Two TTS services for different use cases
- ✅ Cost efficiency: Free default voice (Piper)
- ✅ Quality: Premium option (ElevenLabs)
- ✅ Performance: Smart caching eliminates re-generation
- ✅ User control: Voice selection at read time
- ✅ Scalability: Independent services can be replaced/upgraded
