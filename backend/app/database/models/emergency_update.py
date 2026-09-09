from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class EmergencyUpdate(Base):
    __tablename__ = "emergency_updates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_update_id = Column(String(100), unique=True, nullable=True, index=True)
    sos_id = Column(Integer, ForeignKey("sos_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    update_type = Column(String(50), nullable=False, default="TEXT_UPDATE", index=True)
    message = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    location_timestamp = Column(DateTime(timezone=True), nullable=True)

    source = Column(String(50), default="CITIZEN_APP", nullable=False)
    delivery_status = Column(String(30), default="RECEIVED", nullable=False)
    original_language = Column(String(10), default="en", nullable=False)
    processing_status = Column(String(30), default="PROCESSED", nullable=False)

    # Audio & Transcription Metadata (Phase 4.2)
    audio_id = Column(String(100), nullable=True, index=True)
    audio_duration = Column(Float, nullable=True)
    audio_mime_type = Column(String(60), nullable=True)
    audio_size = Column(Integer, nullable=True)
    audio_storage_reference = Column(String(255), nullable=True)
    transcription_provider = Column(String(60), nullable=True)
    transcription_model = Column(String(60), nullable=True)
    transcription_confidence = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    sos_report = relationship("SOSReport", back_populates="updates")
    incident = relationship("Incident", back_populates="updates")
