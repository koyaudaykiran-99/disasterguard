import os
import io
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("disasterguard.stt")

@dataclass
class TranscriptionResult:
    text: str
    original_language: str
    confidence: float
    provider: str
    model: str
    duration_seconds: float = 0.0
    is_mock: bool = True

class SpeechToTextProvider(ABC):
    @abstractmethod
    def transcribe(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
        mime_type: str = "audio/webm",
        duration_seconds: Optional[float] = None
    ) -> TranscriptionResult:
        pass

class MockSTTProvider(SpeechToTextProvider):
    """
    Mock speech-to-text provider that produces realistic regional emergency distress transcripts
    for Telugu, Hindi, and English without requiring third-party cloud API credentials.
    """
    TRANSCRIPTS = {
        "te": "మా ఇంట్లోకి నీళ్లు వచ్చాయి, మా నాన్న చిక్కుకున్నారు",
        "hi": "घर में पानी भर गया है और पिताजी फंसे हुए हैं, हमें तुरंत मदद चाहिए",
        "en": "Water has entered the ground floor and an elderly family member is trapped, please send boat rescue."
    }

    def transcribe(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
        mime_type: str = "audio/webm",
        duration_seconds: Optional[float] = None
    ) -> TranscriptionResult:
        lang = (language or "en").lower().strip()
        if lang in ("te", "telugu", "te-in"):
            chosen_lang = "te"
            transcript = self.TRANSCRIPTS["te"]
        elif lang in ("hi", "hindi", "hi-in"):
            chosen_lang = "hi"
            transcript = self.TRANSCRIPTS["hi"]
        else:
            chosen_lang = "en"
            transcript = self.TRANSCRIPTS["en"]

        dur = duration_seconds if duration_seconds is not None else 6.5

        logger.info(
            f"MOCK_STT_TRANSCRIBED: {chosen_lang} ({len(audio_bytes)} bytes) -> '{transcript[:30]}...'"
        )

        return TranscriptionResult(
            text=transcript,
            original_language=chosen_lang,
            confidence=0.95,
            provider="mock-stt",
            model="mock-regional-v1",
            duration_seconds=dur,
            is_mock=True
        )

class WhisperSTTProvider(SpeechToTextProvider):
    """
    Real cloud speech-to-text integration using OpenAI Whisper API.
    Used when STT_MODE=REAL and OPENAI_API_KEY/STT_API_KEY is available.
    """
    def __init__(self, api_key: str, model: str = "whisper-1", timeout: int = 15):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def transcribe(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
        mime_type: str = "audio/webm",
        duration_seconds: Optional[float] = None
    ) -> TranscriptionResult:
        import httpx

        headers = {"Authorization": f"Bearer {self.api_key}"}
        ext = "webm"
        if "wav" in mime_type:
            ext = "wav"
        elif "ogg" in mime_type:
            ext = "ogg"
        elif "mp4" in mime_type or "m4a" in mime_type:
            ext = "m4a"
        elif "mpeg" in mime_type or "mp3" in mime_type:
            ext = "mp3"

        files = {"file": (f"audio.{ext}", io.BytesIO(audio_bytes), mime_type)}
        data = {"model": self.model}
        if language and language.lower() in ("te", "hi", "en"):
            data["language"] = language.lower()

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data
                )
                if res.status_code == 200:
                    payload = res.json()
                    text = payload.get("text", "").strip()
                    logger.info(f"WHISPER_REAL_TRANSCRIBED: {language} -> '{text[:40]}...'")
                    return TranscriptionResult(
                        text=text,
                        original_language=language or "en",
                        confidence=0.92,
                        provider="openai-whisper",
                        model=self.model,
                        duration_seconds=duration_seconds or 0.0,
                        is_mock=False
                    )
                else:
                    logger.error(f"Whisper API error: {res.status_code} - {res.text}")
                    raise RuntimeError(f"Whisper STT error: HTTP {res.status_code}")
        except Exception as e:
            logger.error(f"Whisper request exception: {e}")
            raise e

class STTService:
    def __init__(self):
        self.mode = os.getenv("STT_MODE", "MOCK").upper()
        self.provider_name = os.getenv("STT_PROVIDER", "mock").lower()
        self.api_key = os.getenv("STT_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("STT_MODEL", "whisper-1")

        if self.mode == "REAL" and self.api_key:
            logger.info(f"STTService initialized with REAL provider ({self.provider_name}, model {self.model})")
            self._provider: SpeechToTextProvider = WhisperSTTProvider(api_key=self.api_key, model=self.model)
        else:
            logger.info("STTService initialized with MockSTTProvider (demo/mock mode).")
            self._provider = MockSTTProvider()

    @property
    def provider(self) -> SpeechToTextProvider:
        return self._provider

    def set_provider(self, provider: SpeechToTextProvider):
        """Allows test suites or runtime to switch provider dynamically."""
        self._provider = provider

    def transcribe_audio(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
        mime_type: str = "audio/webm",
        duration_seconds: Optional[float] = None
    ) -> TranscriptionResult:
        """
        Transcribe emergency audio recording with fallback handling.
        """
        try:
            return self._provider.transcribe(
                audio_bytes=audio_bytes,
                language=language,
                mime_type=mime_type,
                duration_seconds=duration_seconds
            )
        except Exception as e:
            logger.warning(f"Primary STT provider failed: {e}. Falling back to MockSTTProvider.")
            mock = MockSTTProvider()
            return mock.transcribe(
                audio_bytes=audio_bytes,
                language=language,
                mime_type=mime_type,
                duration_seconds=duration_seconds
            )

stt_service = STTService()
