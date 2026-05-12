"""
Piper TTS Service - Free, open-source text-to-speech for default voice
"""
import importlib.util
import ntpath
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
            env_parts = env_command.split()
            env_exe = env_parts[0]
            if os.path.exists(env_exe) or shutil.which(env_exe):
                return env_parts
            print(f"   ⚠️  Ignoring PIPER_COMMAND because it does not exist in this runtime: {env_exe}")

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
        
        # Prefer the Python module entry point when available (more reliable)
        if importlib.util.find_spec("piper") is not None:
            return [sys.executable, "-m", "piper"]

        # Try finding a system binary in PATH.
        for candidate in ("piper", "piper.exe"):
            found = shutil.which(candidate)
            if found:
                return [found]
        
        # Default path - will fail with clear message if not found
        return ["piper"]

    def _get_model_path(self) -> str:
        """Get path to default Piper model"""
        # Allow overriding via environment variable (useful for Docker)
        env_model = os.environ.get("PIPER_MODEL_PATH")
        if env_model:
            # If running inside Docker with a Windows path, translate to container mount
            if self._is_linux_piper() and ('\\' in env_model or env_model.startswith('C:')):
                basename = ntpath.basename(env_model)
                return f"/models/{basename}"
            return env_model

        # Common model locations
        common_models = [
            os.path.expanduser("~/.local/share/piper/models/en_US-amy-medium.onnx"),
            os.path.expanduser("~/.local/share/piper/models/en_US-libritts-high.onnx"),
            os.path.join(os.getcwd(), "models", "en_US-amy-medium.onnx"),
            "/models/en_US-amy-medium.onnx",
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
        if env_config:
            # If running inside Docker with a Windows path, translate to container mount
            if self._is_linux_piper() and ('\\' in env_config or env_config.startswith('C:')):
                basename = ntpath.basename(env_config)
                return f"/models/{basename}"
            if os.path.exists(env_config):
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
        if '\\' in host_path or host_path.startswith('C:'):
            return f"/models/{ntpath.basename(host_path)}"
        return f"/models/{os.path.basename(host_path)}"

    def _is_linux_piper(self) -> bool:
        """Check if the detected Piper runner is a Linux binary."""
        if not self.piper_runner:
            return False
        piper_exe = self.piper_runner[0]
        # Check if it's a Unix-style path (not C:\ or C:/)
        return '/' in piper_exe and not piper_exe.startswith('C:')

    def _validate_local_paths(self) -> None:
        """Validate model/config paths before running a local Piper command."""
        if not os.path.exists(self.model_path):
            raise Exception(
                "Piper model file not found at "
                f"{self.model_path}. If API runs in Docker, mount ./models to /models "
                "or set PIPER_USE_DOCKER=1 with a reachable Docker CLI."
            )
        if self.config_path and not os.path.exists(self.config_path):
            raise Exception(f"Piper config file not found at {self.config_path}")

    def _find_espeak_runner(self) -> list[str] | None:
        """Find espeak-ng/espeak as a last-resort local TTS engine."""
        for candidate in ("espeak-ng", "espeak"):
            found = shutil.which(candidate)
            if found:
                return [found]
        return None

    def _generate_espeak_audio(self, text: str, output_path: str) -> bytes:
        """Fallback TTS using espeak-ng when Piper is unavailable."""
        runner = self._find_espeak_runner()
        if not runner:
            raise Exception("Neither Piper nor espeak-ng is available in this runtime")

        cmd = runner + ["-w", output_path, text]
        print(f"   ↪️  Running fallback TTS: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="ignore") if result.stderr is not None else ""
            raise Exception(f"espeak fallback failed: {stderr}")

        if not os.path.exists(output_path):
            raise Exception(f"espeak fallback did not create output file: {output_path}")

        with open(output_path, "rb") as f:
            return f.read()

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
            def _build_local_cmd(output_flag: str) -> list[str]:
                cmd_local = self.piper_runner + [
                    "--model", self.model_path,
                    output_flag, output_path,
                ]
                if self.config_path:
                    cmd_local += ["--config", self.config_path]
                return cmd_local

            # Run Piper command
            cmd = _build_local_cmd("--output-file")
            # If explicitly configured, use Docker container fallback.
            use_docker = False
            docker_container = os.environ.get("PIPER_DOCKER_CONTAINER", "piper")
            if os.environ.get("PIPER_USE_DOCKER", "0") == "1":
                if not shutil.which("docker"):
                    raise Exception("PIPER_USE_DOCKER=1 but Docker CLI is not available in this runtime")
                # Try to detect if docker container exists
                try:
                    inspect = subprocess.run(["docker", "inspect", docker_container], capture_output=True, timeout=10)
                    use_docker = inspect.returncode == 0
                except Exception:
                    use_docker = False

            if use_docker:
                container_model_path = self._to_container_path(self.model_path)
                container_output_path = "/tmp/piper_out.wav"
                docker_cmd = [
                    "docker", "exec", "-i", docker_container,
                    "python", "-m", "piper", "--model", container_model_path, "--output-file", container_output_path
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
                cp_result = subprocess.run(
                    ["docker", "cp", f"{docker_container}:{container_output_path}", output_path],
                    capture_output=True,
                    timeout=20,
                )
                if cp_result.returncode != 0:
                    cp_err = cp_result.stderr.decode("utf-8", errors="ignore") if cp_result.stderr else ""
                    raise Exception(f"Failed to copy Piper output from container: {cp_err}")
            else:
                try:
                    self._validate_local_paths()
                    print(f"   ➡️  Running Piper: {' '.join(cmd)}")
                    # Use stdin to send text (avoid command line length issues)
                    result = subprocess.run(
                        cmd,
                        input=text.encode("utf-8"),
                        capture_output=True,
                        timeout=120
                    )

                    # Some Piper builds use --output_file instead of --output-file.
                    stderr_text = result.stderr.decode("utf-8", errors="ignore") if result.stderr is not None else ""
                    if result.returncode != 0 and ("--output-file" in stderr_text or "unrecognized arguments" in stderr_text):
                        cmd = _build_local_cmd("--output_file")
                        print(f"   ↪️  Retrying Piper with alternate flag: {' '.join(cmd)}")
                        result = subprocess.run(
                            cmd,
                            input=text.encode("utf-8"),
                            capture_output=True,
                            timeout=120
                        )
                except Exception as piper_error:
                    print(f"   ⚠️  Piper unavailable, using espeak fallback: {piper_error}")
                    self._generate_espeak_audio(text, output_path)
                    result = subprocess.CompletedProcess(cmd, 0, b"", b"")
            
            if result.returncode != 0:
                print(f"   ❌ Piper failed!")
                print(f"      Return code: {result.returncode}")
                stderr = result.stderr.decode() if result.stderr is not None else ""
                print(f"      Stderr: {stderr}")
                print("   ⚠️  Falling back to espeak-ng")
                self._generate_espeak_audio(text, output_path)
            
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
