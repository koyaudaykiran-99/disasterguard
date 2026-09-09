from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database.database import Base

class RainfallPrediction(Base):
    __tablename__ = "rainfall_predictions"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(120), nullable=False, index=True)
    predicted_rainfall = Column(Float, nullable=False)
    forecast_horizon = Column(Integer, default=6)  # hours
    confidence = Column(Float, default=0.85)
    risk_level = Column(String(20), default="MODERATE", index=True)
    prediction_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class FloodPrediction(Base):
    __tablename__ = "flood_predictions"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(120), nullable=False, index=True)
    flood_probability = Column(Float, nullable=False)
    water_depth = Column(Float, nullable=False)
    risk_level = Column(String(20), default="MODERATE", index=True)
    prediction_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
