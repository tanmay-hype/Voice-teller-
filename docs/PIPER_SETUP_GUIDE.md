# Setup Guide: Piper + Story Reading Flow

## Quick Start

Your story reading flow is now implemented! Follow these steps to get it working:

## Step 1: Install Piper

### Option A: Native install (Linux/macOS)

If you are on Linux or macOS and prefer a native install, use your package manager or follow the platform instructions below. On Windows, Docker mode (Option C) is recommended — see the Windows section further down.

**macOS (Homebrew)**
```bash
# If you have a mac-native build of Piper available via Homebrew tap (varies by distro), install it. If not, prefer Docker method on macOS.
brew install piper-phoneme-tool || true

# Models directory (local)
mkdir -p ~/.local/share/piper/models
cd ~/.local/share/piper/models
wget https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/en_US-amy-medium.onnx
```

**Ubuntu/Debian**
```bash
sudo apt-get update
sudo apt-get install -y piper || true

# Download model
mkdir -p ~/.local/share/piper/models
cd ~/.local/share/piper/models
wget https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/en_US-amy-medium.onnx
```

**Fedora/RHEL**
```bash
sudo dnf install -y piper || true

# Download model
mkdir -p ~/.local/share/piper/models
cd ~/.local/share/piper/models
wget https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/en_US-amy-medium.onnx
```

### Option B: Docker (Recommended on Windows and easy on all platforms)

This repository includes a `piper` service in `docker-compose.yml` and helper scripts to run Piper inside a container. This is the most reliable approach on Windows where native Piper binaries may not be available.

1. Download the model and start the Piper container (Windows PowerShell):

```powershell
.\scripts\setup_piper_windows.ps1
```

2. Or on WSL / Linux:

```bash
./scripts/setup_piper_wsl.sh
```

3. The script will create `./models` and `./media`, download the ONNX model, run the `piper` container, and generate a test sample `./media/piper_test.wav`.

If you prefer to run your own compose file, `docker-compose.yml` defines a `piper` service that mounts `./models` and `./media`.

### Option C: Native from source (advanced)

If you need a native Piper binary, build or download releases for your platform from the project's releases and add the executable to your PATH. For Windows native builds may not be available — prefer Docker on Windows.

```bash
# Example (Linux):
wget https://github.com/rhasspy/piper/releases/download/v1.0.0/piper_linux_x86_64.tar.gz
tar xzf piper_linux_x86_64.tar.gz
# copy the `piper` binary to /usr/local/bin or similar
sudo cp piper /usr/local/bin/
```

## Step 2: Verify Installation

```bash
# Check if piper is in PATH
which piper

# Test Piper
echo "Hello world" | piper --model ~/.local/share/piper/models/en_US-amy-medium.onnx --output-file /tmp/test.wav

# Check output
ls -lh /tmp/test.wav
```

## Step 3: Update Backend Configuration (Optional)

If Piper is not in default PATH, update `backend/services/piper_svc.py`:

```python
def _find_piper(self) -> str:
    """Find Piper executable"""
    # Add your custom path here
    custom_paths = [
        "/path/to/your/piper",
        # ...existing paths...
    ]
    # ... rest of method
```

If you are running Piper inside Docker (recommended on Windows), set these environment variables for the backend (example using a `.env` file or your process manager):

```bash
PIPER_USE_DOCKER=1
PIPER_DOCKER_CONTAINER=piper
PIPER_MODEL_PATH=/models/en_US-amy-medium.onnx
```

These tell `piper_svc` to call `docker exec <container> piper ...` and where the model lives inside the container.

## Step 4: Test the Flow

### Create Story with Default Voice
1. Go to Stories page
2. Click "New Story"
3. Enter title: "Test Story"
4. Enter prompt: "Write a short fairy tale about a dragon"
5. Leave voice selector on "Default voice (Piper)" ✓
6. Click "Generate Story"
7. Wait for story generation

### Read with Piper
1. Click on generated story
2. See "Read Aloud" section
3. Voice selector shows "Default voice (Piper - Free)"
4. Click "Read Aloud"
5. Audio generates locally and plays
6. Listen to narration

### Read with ElevenLabs (Optional - if you have cloned voices)
1. Click on story again
2. Change voice selector to a cloned voice
3. Click "Read Aloud"
4. Audio generates via ElevenLabs and plays
5. Compare quality between services

## Step 5: Production Deployment

### Docker Setup

Update `docker-compose.yml`:

```yaml
services:
  backend:
    build: ./backend
    environment:
      - PIPER_PATH=/usr/bin/piper
      - PIPER_MODEL=/models/en_US-amy-medium.onnx
    volumes:
      - ./media:/app/media
      - ./models:/models

  # Optional: Separate Piper service for scaling
  piper:
    image: debian:bookworm-slim
    entrypoint: >
      bash -c "apt-get update && apt-get install -y piper &&
               mkdir -p /models &&
               wget -O /models/en_US-amy-medium.onnx
               https://huggingface.co/rhasspy/piper/releases/download/v1.0.0/en_US-amy-medium.onnx &&
               tail -f /dev/null"
    volumes:
      - ./models:/models
```

### Environment Variables

Add to `.env`:
```bash
# Piper Configuration
PIPER_EXECUTABLE=/usr/bin/piper
PIPER_MODEL_PATH=/root/.local/share/piper/models/en_US-amy-medium.onnx

# ElevenLabs (existing)
ELEVENLABS_API_KEY=your_key_here
```

## Troubleshooting

### "Piper executable not found"
```bash
# Check PATH
echo $PATH

# Install Piper properly
which piper

# Add to PATH if needed
export PATH=$PATH:/path/to/piper
```

### "Model file not found"
```bash
# Verify model exists
ls -lh ~/.local/share/piper/models/

# Download if missing
mkdir -p ~/.local/share/piper/models
wget -O ~/.local/share/piper/models/en_US-amy-medium.onnx \
  https://huggingface.co/rhasspy/piper/releases/download/v1.0.0/en_US-amy-medium.onnx
```

### "Audio generation timeout"
- Increase timeout in `piper_svc.py` (currently 60s)
- Check system resources
- Verify model is not corrupted

### "No audio output"
- Check media directory permissions: `chmod 755 media/`
- Verify WAV file is being created: `ls -la media/cache/`
- Test Piper manually: `echo "test" | piper --model ... --output-file test.wav`

### "ElevenLabs still being used for default"
- Check `voice_id` is not being passed in request
- Verify `selectedVoiceForReading` is null/empty
- Check browser console for API request

## Performance Tips

### Speed Up Generation
1. Use smaller model: `en_US-amy-small.onnx` (faster, lower quality)
2. Run Piper in parallel service
3. Cache aggressively (already implemented)

### Reduce Latency
1. Pre-generate audio for common stories
2. Use lighter models for real-time use
3. Consider batch processing

### Optimize Storage
1. Use MP3 compression instead of WAV
2. Implement cache cleanup (script included below)
3. Archive old audio files

### Cache Cleanup Script

Create `cleanup_audio_cache.py`:

```python
import os
import time
from pathlib import Path

CACHE_DIR = Path("media/cache")
MAX_AGE_DAYS = 7  # Delete files older than 7 days

def cleanup_cache():
    cutoff_time = time.time() - (MAX_AGE_DAYS * 86400)
    
    for file in CACHE_DIR.glob("*.mp3"):
        if file.stat().st_mtime < cutoff_time:
            file.unlink()
            print(f"Deleted: {file}")

if __name__ == "__main__":
    cleanup_cache()
```

Run periodically:
```bash
# Linux/Mac cron
0 2 * * * cd /app && python cleanup_audio_cache.py

# Or as scheduled task in Python
from schedule import every
every().day.at("02:00").do(cleanup_cache)
```

## Testing Checklist

After setup, verify:

- [ ] `which piper` returns a path
- [ ] Piper processes test text: `echo "test" | piper ...`
- [ ] Backend imports piper_svc without errors
- [ ] Story generation works
- [ ] Read aloud works with Piper (show logs)
- [ ] Read aloud works with ElevenLabs (if available)
- [ ] Audio caching works (file created in media/)
- [ ] Audio plays in browser
- [ ] Voice selector changes TTS service
- [ ] Different voices produce different audio

## Next Steps

1. Install Piper using guide above
2. Test story generation and reading
3. Compare Piper (free, local) vs ElevenLabs (cloned voices)
4. Deploy to production with Docker
5. Monitor performance and cache usage
6. Add cleanup jobs for cache management

## Support

For Piper issues: https://github.com/rhasspy/piper/issues
For ElevenLabs issues: https://github.com/elevenlabs/elevenlabs-python/issues

Your implementation is complete and ready to use!
