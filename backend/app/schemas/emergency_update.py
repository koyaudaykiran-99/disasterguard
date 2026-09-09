from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

VALID_UPDATE_TYPES = {
    "INITIAL_SOS",
    "TEXT_UPDATE",
    "LOCATION_UPDATE",
    "SITUATION_UPDATE",
    "MEDICAL_UPDATE",
    "TRAPPED_PERSON_UPDATE",
    "WATER_LEVEL_UPDATE",
    "REPEAT_SOS",
    "CANCEL_REQUEST",
    "VOICE_UPDATE"
}

class EmergencyUpdateCreate(BaseModel):
    client_update_id: Optional[str] = Field(None, max_length=100, description="Unique client-generated idempotency key")
    update_type: str = Field("TEXT_UPDATE", description="Type of emergency update")
    message: Optional[str] = Field(None, max_length=1000, description="Distress message or update description")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Updated latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Updated longitude")
    accuracy: Optional[float] = Field(None, ge=0.0, description="GPS accuracy in meters")
    location_timestamp: Optional[datetime] = None
    source: Optional[str] = Field("CITIZEN_APP", max_length=50)
    original_language: Optional[str] = Field("en", max_length=10, description="Spoken language ISO code (en, te, hi)")
    audio_id: Optional[str] = Field(None, max_length=100)
    audio_duration: Optional[float] = None
    audio_mime_type: Optional[str] = Field(None, max_length=60)
    audio_size: Optional[int] = None
    audio_storage_reference: Optional[str] = Field(None, max_length=255)
    transcription_provider: Optional[str] = Field(None, max_length=60)
    transcription_model: Optional[str] = Field(None, max_length=60)
    transcription_confidence: Optional[float] = None

    @field_validator("update_type")
    @classmethod
    def validate_update_type(cls, v: str) -> str:
        if not v:
            return "TEXT_UPDATE"
        clean = v.strip().upper()
        if clean not in VALID_UPDATE_TYPES:
            raise ValueError(f"Invalid update_type '{v}'. Must be one of: {', '.join(sorted(VALID_UPDATE_TYPES))}")
        return clean

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        if not clean:
            return None
        if len(clean) > 1000:
            raise ValueError("Emergency update message exceeds maximum allowable length (1000 chars).")
        return clean

    @field_validator("client_update_id")
    @classmethod
    def validate_client_update_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        return clean if clean else None

class EmergencyUpdateResponse(BaseModel):
    id: int
    client_update_id: Optional[str] = None
    sos_id: int
    incident_id: Optional[int] = None
    user_id: Optional[int] = None
    update_type: str
    message: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    location_timestamp: Optional[datetime] = None
    source: str
    delivery_status: str
    original_language: str
    processing_status: str
    audio_id: Optional[str] = None
    audio_duration: Optional[float] = None
    audio_mime_type: Optional[str] = None
    audio_size: Optional[int] = None
    audio_storage_reference: Optional[str] = None
    transcription_provider: Optional[str] = None
    transcription_model: Optional[str] = None
    transcription_confidence: Optional[float] = None
    created_at: datetime
    received_at: datetime

    class Config:
        from_attributes = True
