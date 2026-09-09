from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WeatherObservationSchema(BaseModel):
    id: Optional[int] = None
    location: str
    rainfall_1h: float
    rainfall_3h: float
    rainfall_6h: float
    rainfall_24h: float
    temperature: float
    humidity: float
    wind_speed: float
    pressure: float
    observed_at: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    condition: Optional[str] = "Clear"
    source: Optional[str] = "real"  # "real", "cached", "mock", "simulation"
    precipitation_probability: Optional[float] = None
    is_demo: bool = False

    class Config:
        from_attributes = True

class WeatherForecastSchema(BaseModel):
    location: str
    forecast_horizon_hours: int
    predicted_rainfall_mm: float
    risk_level: str
    temperature: float
    humidity: float
    is_demo: bool = True
