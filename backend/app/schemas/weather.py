from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class WeatherObservationSchema(BaseModel):
    id: Optional[int] = None
    provider: Optional[str] = "open-meteo"
    timestamp: Optional[str] = None
    location: Union[Dict[str, Any], str] = "Central Metro Basin"
    location_name: Optional[str] = "Central Metro Basin"
    
    # User's normalized specification
    temperature_c: Optional[float] = 28.0
    humidity: float = 65.0
    rainfall_mm: Optional[float] = 0.0
    rainfall_intensity_mm_h: Optional[float] = 0.0
    wind_speed_kmh: Optional[float] = 10.0
    pressure_hpa: Optional[float] = 1012.0
    weather_condition: Optional[str] = "Partly Cloudy"
    rain_probability: Optional[float] = 0.0
    visibility_km: Optional[float] = 10.0
    alert_level: Optional[str] = "LOW"
    
    # Backward compatibility with existing DB & ML models
    rainfall_1h: float = 0.0
    rainfall_3h: float = 0.0
    rainfall_6h: float = 0.0
    rainfall_24h: float = 0.0
    temperature: Optional[float] = 28.0
    wind_speed: Optional[float] = 10.0
    pressure: Optional[float] = 1012.0
    observed_at: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    condition: Optional[str] = "Partly Cloudy"
    source: Optional[str] = "real"  # "real", "cached", "mock", "simulation", "imd", "openweather", "open-meteo"
    precipitation_probability: Optional[float] = None
    is_demo: bool = False
    is_cached: bool = False
    cached_at: Optional[str] = None
    data_freshness: Optional[str] = "Updated just now"
    alerts: Optional[List[str]] = Field(default_factory=list)
    official_warnings: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    class Config:
        from_attributes = True

class WeatherForecastSchema(BaseModel):
    provider: Optional[str] = "open-meteo"
    location: Union[Dict[str, Any], str] = "Central Metro Basin"
    location_name: Optional[str] = "Central Metro Basin"
    forecast_horizon_hours: int = 24
    predicted_rainfall_mm: float = 0.0
    risk_level: str = "LOW"
    temperature_c: Optional[float] = 28.0
    temperature: Optional[float] = 28.0
    humidity: float = 78.0
    hourly_timeline: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    timestamp: Optional[str] = None
    is_demo: bool = False

class WeatherAlertsSchema(BaseModel):
    provider: Optional[str] = "open-meteo"
    location: Union[Dict[str, Any], str] = "Central Metro Basin"
    timestamp: str
    total_alerts: int = 0
    alerts: List[Dict[str, Any]] = Field(default_factory=list)

class WeatherRainfallSchema(BaseModel):
    provider: Optional[str] = "open-meteo"
    timestamp: str
    location: Union[Dict[str, Any], str] = "Central Metro Basin"
    rainfall_current_mm: float = 0.0
    rainfall_1h_mm: float = 0.0
    rainfall_3h_mm: float = 0.0
    rainfall_6h_mm: float = 0.0
    rainfall_24h_mm: float = 0.0
    intensity_mm_h: float = 0.0
    intensity_category: str = "Light Rain"
    rain_probability: float = 0.0
    alert_level: str = "LOW"

class WeatherStatusSchema(BaseModel):
    status: str = "operational"
    active_provider: str = "open-meteo"
    available_providers: List[str] = ["imd", "openweather", "open-meteo", "cached", "mock"]
    configured_keys: Dict[str, str]
    cache_ttl_minutes: int = 3
    radar_provider: str = "rainviewer"
    coordinates: Dict[str, float]
    timestamp: str
