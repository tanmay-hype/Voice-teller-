#!/usr/bin/env bash
set -euo pipefail

# Lightweight installer for Linux/WSL environments
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODELS_DIR="$ROOT_DIR/models"
MEDIA_DIR="$ROOT_DIR/media"
mkdir -p "$MODELS_DIR" "$MEDIA_DIR"

MODEL_NAME="en_US-amy-medium.onnx"
DEST="$MODELS_DIR/$MODEL_NAME"

if [ ! -f "$DEST" ]; then
  echo "Downloading model to $DEST"
  urls=(
    "https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/$MODEL_NAME"
    "https://huggingface.co/rhasspy/piper/resolve/main/voices/$MODEL_NAME"
  )
  success=0
  for u in "${urls[@]}"; do
    if curl -fsSL "$u" -o "$DEST"; then
      success=1
      break
    fi
  done
  if [ "$success" -ne 1 ]; then
    echo "Failed to download model. Please download it manually into $DEST" >&2
    exit 1
  fi
fi

echo "Bringing up Piper container (docker-compose.yml)..."
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found. Please install Docker or run Piper natively." >&2
  exit 1
fi

docker compose -f "$ROOT_DIR/docker-compose.yml" up -d piper --build

echo "Testing Piper by generating a sample..."
docker exec -i piper /bin/sh -c "echo 'Hello from Piper' | python -m piper --model /models/$MODEL_NAME --output-file /tmp/piper_out.wav && cp /tmp/piper_out.wav /media/piper_test.wav" || echo "Warning: sample generation failed"

echo "Done. Sample written to ./media/piper_test.wav if successful. Set PIPER_USE_DOCKER=1 in backend if you want to use Docker mode."
