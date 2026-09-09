from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class SOSReport(Base):
    __tablename__ = "sos_reports"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(100), unique=True, nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    accuracy = Column(Float, nullable=True)
    message = Column(Text, nullable=True)
    severity = Column(String(20), default="CRITICAL", index=True)
    status = Column(String(30), default="PENDING", index=True) # PENDING, DISPATCHED, RESCUED
    transport = Column(String(50), default="INTERNET", nullable=True)
    device_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    updates = relationship("EmergencyUpdate", back_populates="sos_report", order_by="EmergencyUpdate.created_at.asc()", cascade="all, delete-orphan")

    @property
    def sos_id(self) -> int:
        return self.id

    @property
    def received_at(self):
        return self.created_at
