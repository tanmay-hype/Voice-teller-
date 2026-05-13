import os
from pathlib import Path
from urllib.parse import quote

import httpx

from core.config import settings


class MediaStorageService:
    def __init__(self):
        self.provider = (settings.AUDIO_STORAGE_PROVIDER or "auto").strip().lower()
        self.supabase_url = settings.SUPABASE_URL.strip().rstrip("/")
        self.supabase_public_url = (settings.SUPABASE_PUBLIC_URL or settings.SUPABASE_URL).strip().rstrip("/")
        self.supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY.strip()
        self.bucket = settings.SUPABASE_STORAGE_BUCKET.strip()

    def _should_use_supabase(self) -> bool:
        has_supabase_config = bool(self.supabase_url and self.supabase_key and self.bucket)
        if self.provider == "supabase":
            return has_supabase_config
        if self.provider == "local":
            return False
        return has_supabase_config

    def _public_url(self, object_path: str) -> str:
        encoded_path = quote(object_path, safe="/")
        return f"{self.supabase_public_url}/storage/v1/object/public/{self.bucket}/{encoded_path}"

    async def _upload_to_supabase(self, object_path: str, audio_bytes: bytes, content_type: str) -> str:
        upload_url = (
            f"{self.supabase_url}/storage/v1/object/{self.bucket}/"
            f"{quote(object_path, safe='/')}?upsert=true"
        )

        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
            "Content-Type": content_type,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(upload_url, content=audio_bytes, headers=headers)
            response.raise_for_status()

        return self._public_url(object_path)

    async def _save_local(self, object_path: str, audio_bytes: bytes) -> str:
        local_path = Path("media") / object_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(audio_bytes)
        return f"/media/{object_path.replace(os.sep, '/')}"

    async def store_audio(
        self,
        *,
        filename: str,
        audio_bytes: bytes,
        folder: str = "stories",
        content_type: str = "audio/mpeg",
    ) -> str:
        object_path = "/".join(part.strip("/") for part in (folder, filename) if part)

        if self._should_use_supabase():
            try:
                print(f"☁️ Uploading audio to Supabase: {object_path}")
                return await self._upload_to_supabase(object_path, audio_bytes, content_type)
            except Exception as exc:
                print(f"⚠️ Supabase audio upload failed, falling back to local media: {exc}")
                if self.provider == "supabase":
                    raise

        return await self._save_local(object_path, audio_bytes)


media_storage_svc = MediaStorageService()