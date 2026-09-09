from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database.database import Base

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(120), nullable=False, index=True)
    rainfall_1h = Column(Float, default=0.0)
    rainfall_3h = Column(Float, default=0.0)
    rainfall_6h = Column(Float, default=0.0)
    rainfall_24h = Column(Float, default=0.0)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    condition = Column(String(60), default="Clear", nullable=True)
    source = Column(String(30), default="real", index=True)
    precipitation_probability = Column(Float, nullable=True)
    observed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    @property
    def rainfall_mm(self) -> float:
        return float(self.rainfall_1h or 0.0)
