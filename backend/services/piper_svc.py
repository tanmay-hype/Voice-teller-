"""
Piper TTS Service - Free, open-source text-to-speech for default voice
"""
import importlib.util
import subprocess
import os
import shutil
import sys
from pathlib import Path
from core.config import settings


class PiperService:
    """Local Piper TTS service for default voice synthesis"""

    def __init__(self):
        self.piper_runner = self._find_piper_runner()
        self.model_path = self._get_model_path()
        self.config_path = self._get_config_path()
        print(f"🔧 PiperService initialized")
        print(f"   Piper runner: {' '.join(self.piper_runner)}")
        print(f"   Model path: {self.model_path}")
        print(f"   Config path: {self.config_path or 'auto-detect'}")

    def _find_piper_runner(self) -> list[str]:
        """Find a runnable Piper command on the local machine."""
        env_command = os.environ.get("PIPER_COMMAND")
        if env_command:
            return env_command.split()

        # Try common installation paths first.
        common_paths = [
            "/usr/bin/piper",
            "/usr/local/bin/piper",
            "C:\\Program Files\\piper\\piper.exe",
            "C:\\piper\\piper.exe",
            "/opt/piper/piper",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return [path]
        
        # Try finding in PATH.
        for candidate in ("piper", "piper.exe"):
            found = shutil.which(candidate)
            if found:
                return [found]

        # If the Python package is installed, use the module entry point.
        if importlib.util.find_spec("piper") is not None:
            return [sys.executable, "-m", "piper"]
        
        # Default path - will fail with clear message if not found
        return ["piper"]

    def _get_model_path(self) -> str:
        """Get path to default Piper model"""
        # Allow overriding via environment variable (useful for Docker)
        env_model = os.environ.get("PIPER_MODEL_PATH")
        if env_model:
            return env_model

        # Common model locations
        common_models = [
            os.path.expanduser("~/.local/share/piper/models/en_US-amy-medium.onnx"),
            os.path.expanduser("~/.local/share/piper/models/en_US-libritts-high.onnx"),
            os.path.join(os.getcwd(), "models", "en_US-amy-medium.onnx"),
            "/usr/share/piper/models/en_US-amy-medium.onnx",
        ]

        for model in common_models:
            if os.path.exists(model):
                return model

        # Return default even if not found (will fail clearly)
        return os.path.join(os.path.expanduser("~/.local/share/piper/models"), "en_US-amy-medium.onnx")

    def _get_config_path(self) -> str | None:
        """Find a matching Piper config JSON if one is available."""
        env_config = os.environ.get("PIPER_CONFIG_PATH")
        if env_config and os.path.exists(env_config):
            return env_config

        model_dir = os.path.dirname(self.model_path)
        base_name = os.path.basename(self.model_path)
        candidate_names = [
            f"{base_name}.json",
            f"{os.path.splitext(base_name)[0]}.json",
        ]

        for candidate_name in candidate_names:
            candidate_path = os.path.join(model_dir, candidate_name)
            if os.path.exists(candidate_path):
                return candidate_path

        return None

    def _to_container_path(self, host_path: str) -> str:
        """Translate a host model path into the mounted container path."""
        return f"/models/{os.path.basename(host_path)}"

    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech using Piper
        Returns: Audio bytes in MP3 format
        """
        print(f"\n{'='*50}")
        print(f"🎙️  Piper text_to_speech START")
        print(f"   Text length: {len(text)} chars")
        print(f"   Model: {self.model_path}")

        # Create temporary output file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name

        try:
            # Run Piper command
            cmd = self.piper_runner + [
                "--model", self.model_path,
                "--output-file", output_path,
            ]
            if self.config_path:
                cmd += ["--config", self.config_path]
            # If explicitly configured, use Docker container fallback.
            use_docker = False
            docker_container = os.environ.get("PIPER_DOCKER_CONTAINER", "piper")
            if os.environ.get("PIPER_USE_DOCKER", "0") == "1":
                # Try to detect if docker container exists
                try:
                    subprocess.run(["docker", "inspect", docker_container], capture_output=True, timeout=10)
                    use_docker = True
                except Exception:
                    use_docker = False

            if use_docker:
                container_model_path = self._to_container_path(self.model_path)
                docker_cmd = [
                    "docker", "exec", "-i", docker_container,
                    "python", "-m", "piper", "--model", container_model_path, "--output-file", "/tmp/piper_out.wav"
                ]
                if self.config_path:
                    docker_cmd += ["--config", self._to_container_path(self.config_path)]
                print(f"   ➡️  Running Piper in Docker: {' '.join(docker_cmd)}")
                result = subprocess.run(
                    docker_cmd,
                    input=text.encode("utf-8"),
                    capture_output=True,
                    timeout=120
                )
                # copy out the file from container to host output_path
                try:
                    subprocess.run(["docker", "cp", f"{docker_container}:/tmp/piper_out.wav", output_path], check=True, timeout=20)
                except Exception:
                    # if docker cp failed, proceed to check output inside container
                    pass
            else:
                print(f"   ➡️  Running Piper: {' '.join(cmd)}")
                # Use stdin to send text (avoid command line length issues)
                result = subprocess.run(
                    cmd,
                    input=text.encode("utf-8"),
                    capture_output=True,
                    timeout=60
                )
            
            if result.returncode != 0:
                print(f"   ❌ Piper failed!")
                print(f"      Return code: {result.returncode}")
                stderr = result.stderr.decode() if result.stderr is not None else ""
                print(f"      Stderr: {stderr}")
                raise Exception(f"Piper TTS failed: {stderr}")
            
            # Read the output WAV file
            if not os.path.exists(output_path):
                raise Exception(f"Piper did not create output file: {output_path}")
            
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            print(f"   ✅ Piper TTS completed!")
            print(f"      Audio size: {len(audio_bytes)} bytes")
            print(f"{'='*50}\n")
            
            return audio_bytes

        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Piper request timed out")
            print(f"{'='*50}\n")
            raise Exception("Piper TTS request timed out")
        
        finally:
            # Clean up temp file
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception:
                pass


# Singleton instance
piper_svc = PiperService()
