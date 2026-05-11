from pydantic_settings import BaseSettings
import os
import subprocess
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Voice Storytelling"
    APP_VERSION: str = "dev"
    
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "aivoice"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/aivoice"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # Security
    SECRET_KEY: str = "supersecretkey_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # External APIs
    OPENAI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_SENDER: str = "your-email@gmail.com"
    EMAIL_PASSWORD: str = ""
    
    # OTP Settings
    OTP_EXPIRY_MINUTES: int = 15

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Resolve application version: priority -> APP_VERSION env var -> VERSION file -> git commit -> 'dev'
try:
    repo_root = Path(__file__).resolve().parents[2]
except Exception:
    repo_root = Path(os.getcwd())

def _detect_version():
    # 1) Env override
    env_ver = os.environ.get("APP_VERSION")
    if env_ver:
        return env_ver

    # 2) VERSION file at repo root
    ver_file = repo_root / "VERSION"
    if ver_file.exists():
        try:
            return ver_file.read_text().strip()
        except Exception:
            pass

    # 3) Git short commit
    try:
        res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(repo_root), capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass

    return "dev"

# Populate APP_VERSION on settings if not provided by environment
detected = _detect_version()
if not getattr(settings, "APP_VERSION", None):
    try:
        settings.APP_VERSION = detected
    except Exception:
        pass
