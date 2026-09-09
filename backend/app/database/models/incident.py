from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    sos_id = Column(Integer, ForeignKey("sos_reports.id"), nullable=True, index=True)
    title = Column(String(180), nullable=False)
    description = Column(Text, nullable=True)
    incident_type = Column(String(60), default="FLOOD_TRAPPED_PERSON", index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    severity = Column(String(20), default="HIGH", index=True)
    status = Column(String(30), default="PENDING", index=True) # PENDING, DISPATCHED, RESOLVED
    source = Column(String(60), default="CITIZEN_SOS")
    priority_score = Column(Integer, default=50, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    updates = relationship("EmergencyUpdate", back_populates="incident", order_by="EmergencyUpdate.created_at.asc()")

    @property
    def people_at_risk(self) -> int:
        return 1

    @property
    def emergency_type(self) -> str:
        return self.incident_type or "FLOOD"
