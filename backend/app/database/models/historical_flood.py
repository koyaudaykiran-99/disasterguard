from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime, timezone
from app.database.database import Base

class HistoricalFloodEvent(Base):
    __tablename__ = "historical_flood_events"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(150), nullable=False, index=True)
    event_date = Column(String(30), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(String(30), default="HIGH", index=True)
    rainfall_total_mm = Column(Float, nullable=False)
    duration_hours = Column(Integer, default=24)
    source = Column(String(255), nullable=False)
    source_type = Column(String(50), default="HISTORICAL_EVENT")
    description = Column(Text, nullable=True)
    geometry_wkt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
