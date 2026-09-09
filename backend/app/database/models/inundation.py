from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime, timezone
from app.database.database import Base

class InundationPrediction(Base):
    __tablename__ = "flood_intelligence_predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    risk_level = Column(String(30), default="MODERATE", index=True)
    susceptibility_score = Column(Integer, default=50, index=True)
    estimated_depth_m = Column(Float, default=0.5)
    depth_confidence = Column(Float, default=0.75)
    depth_type = Column(String(30), default="PROXY_ESTIMATE")
    affected_area_km2 = Column(Float, default=1.0)
    data_source_type = Column(String(50), default="DERIVED")
    model_version = Column(String(50), default="v2.1-geospatial")
    explanation = Column(Text, nullable=True)

# Alias for consistent naming
FloodIntelligencePrediction = InundationPrediction

