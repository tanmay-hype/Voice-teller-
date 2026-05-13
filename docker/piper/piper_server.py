import json
import os
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


HOST = os.getenv("PIPER_HOST", "0.0.0.0")
PORT = int(os.getenv("PIPER_PORT", "8080"))
MODEL_PATH = os.getenv("PIPER_MODEL_PATH", "/models/en_US-amy-medium.onnx")
CONFIG_PATH = os.getenv("PIPER_CONFIG_PATH", "/models/en_US-amy-medium.onnx.json")


def _speak(text: str, model_path: str | None = None, config_path: str | None = None) -> bytes:
    model = model_path or MODEL_PATH
    config = config_path or CONFIG_PATH

    if not os.path.exists(model):
        raise FileNotFoundError(f"Piper model not found: {model}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_path = tmp.name

    try:
        cmd = ["python", "-m", "piper", "--model", model, "--output-file", output_path]
        if config and os.path.exists(config):
            cmd += ["--config", config]

        result = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=120,
        )

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="ignore") if result.stderr else ""
            alt_cmd = ["python", "-m", "piper", "--model", model, "-f", output_path]
            if config and os.path.exists(config):
                alt_cmd += ["--config", config]
            alt_result = subprocess.run(
                alt_cmd,
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=120,
            )
            if alt_result.returncode != 0:
                alt_stderr = alt_result.stderr.decode("utf-8", errors="ignore") if alt_result.stderr else ""
                raise RuntimeError(stderr or alt_stderr or "Piper synthesis failed")

        return Path(output_path).read_bytes()
    finally:
        try:
            os.remove(output_path)
        except Exception:
            pass


class PiperHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/health"):
            self._send_json(200, {"status": "ok", "service": "piper"})
            return
        self._send_json(404, {"detail": "Not found"})

    def do_POST(self):
        if self.path != "/speak":
            self._send_json(404, {"detail": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8")) if body else {}
            text = (payload.get("text") or "").strip()
            if not text:
                self._send_json(400, {"detail": "Missing text"})
                return

            audio_bytes = _speak(
                text,
                payload.get("model_path"),
                payload.get("config_path"),
            )

            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(audio_bytes)))
            self.end_headers()
            self.wfile.write(audio_bytes)
        except Exception as exc:
            self._send_json(500, {"detail": str(exc)})


def main():
    server = ThreadingHTTPServer((HOST, PORT), PiperHandler)
    print(f"Piper server listening on {HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()