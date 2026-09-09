from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime, timezone
from app.database.database import Base

class ForecastPrediction(Base):
    __tablename__ = "forecast_predictions"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), default="Chennai Metro", index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    horizon = Column(String(10), nullable=False, index=True)  # 1H, 3H, 6H, 12H, 24H
    forecast_timestamp = Column(DateTime, nullable=False, index=True)
    risk_score = Column(Integer, nullable=False, default=0, index=True)
    risk_level = Column(String(30), nullable=False, default="LOW", index=True)
    rainfall_estimate_mm = Column(Float, default=0.0)
    flood_susceptibility = Column(Integer, default=0)
    proxy_depth_estimate_m = Column(Float, default=0.0)
    depth_type = Column(String(30), default="PROXY_ESTIMATE")
    confidence = Column(Float, default=0.70)
    uncertainty = Column(Float, default=0.30)
    trajectory = Column(String(30), default="STABLE")
    warning_state = Column(String(30), default="NORMAL")
    model_version = Column(String(50), default="forecast_v1")
    data_source = Column(String(255), default="REAL_WEATHER + REAL_HISTORICAL_ML + GEOSPATIAL_DERIVATION")
    data_source_type = Column(String(50), default="EXPLAINABLE_FORECAST_ENGINE")
    explanation = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    valid_until = Column(DateTime, nullable=True)

    @property
    def score_1h(self) -> float:
        return float(self.risk_score or 0.0)
