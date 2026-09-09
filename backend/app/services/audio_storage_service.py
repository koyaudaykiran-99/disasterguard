import os
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("disasterguard.audio_storage")

BASE_AUDIO_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "audio"
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_MIME_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/mp4",
    "audio/m4a",
    "audio/mpeg",
    "audio/mp3",
    "audio/aac",
    "application/octet-stream"  # Browser generic fallback
}

class AudioStorageService:
    def __init__(self, base_dir: Path = BASE_AUDIO_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_audio(
        self,
        sos_id: int,
        audio_bytes: bytes,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Securely persist an emergency audio recording to local filesystem storage.
        Validates size, MIME type, generates isolated directory per SOS,
        and returns file storage metadata.
        """
        if not audio_bytes or len(audio_bytes) == 0:
            raise ValueError("Audio recording payload is empty.")

        if len(audio_bytes) > MAX_AUDIO_SIZE_BYTES:
            raise ValueError(f"Audio file size exceeds maximum allowable limit ({MAX_AUDIO_SIZE_BYTES / (1024*1024):.1f} MB).")

        clean_mime = (mime_type or "audio/webm").split(";")[0].strip().lower()
        if clean_mime not in ALLOWED_MIME_TYPES:
            logger.warning(f"Uncommon audio mime type '{clean_mime}', accepting with standard fallback.")
            clean_mime = "audio/webm"

        # Determine safe file extension
        ext = ".webm"
        if "wav" in clean_mime:
            ext = ".wav"
        elif "ogg" in clean_mime:
            ext = ".ogg"
        elif "mp4" in clean_mime or "m4a" in clean_mime:
            ext = ".m4a"
        elif "mpeg" in clean_mime or "mp3" in clean_mime:
            ext = ".mp3"

        audio_id = f"audio_{uuid.uuid4().hex[:16]}"
        safe_filename = f"{audio_id}{ext}"

        # Subdirectory per SOS report
        sos_dir = self.base_dir / str(sos_id)
        sos_dir.mkdir(parents=True, exist_ok=True)

        target_path = (sos_dir / safe_filename).resolve()

        # Prevent directory traversal
        if not str(target_path).startswith(str(self.base_dir.resolve())):
            raise ValueError("Security violation: Invalid storage destination path.")

        with open(target_path, "wb") as f:
            f.write(audio_bytes)

        rel_ref = f"{sos_id}/{safe_filename}"
        logger.info(f"AUDIO_STORED: ID {audio_id} for SOS #{sos_id} ({len(audio_bytes)} bytes, {clean_mime})")

        return {
            "audio_id": audio_id,
            "filename": safe_filename,
            "file_path": str(target_path),
            "storage_reference": rel_ref,
            "audio_size": len(audio_bytes),
            "audio_mime_type": clean_mime
        }

    def get_audio_path(self, sos_id: int, audio_id: str) -> Optional[Path]:
        """
        Locate audio recording by SOS ID and Audio ID with path traversal prevention.
        """
        clean_audio_id = "".join(c for c in audio_id if c.isalnum() or c in ("_", "-"))
        sos_dir = (self.base_dir / str(sos_id)).resolve()

        if not sos_dir.exists() or not str(sos_dir).startswith(str(self.base_dir.resolve())):
            return None

        for file in sos_dir.iterdir():
            if file.stem == clean_audio_id:
                target = file.resolve()
                if str(target).startswith(str(self.base_dir.resolve())) and target.is_file():
                    return target
        return None

audio_storage_service = AudioStorageService()
