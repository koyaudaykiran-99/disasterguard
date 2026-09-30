from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.weather_service import weather_service
from app.schemas.weather import (
    WeatherObservationSchema,
    WeatherForecastSchema,
    WeatherAlertsSchema,
    WeatherRainfallSchema,
    WeatherStatusSchema
)
from typing import Dict, Any, List, Optional

router = APIRouter()

@router.get("/current", response_model=WeatherObservationSchema)
async def get_current_weather(
    location: str = Query("Central Metro Basin", description="Location name"),
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Latitude (-90 to 90)"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Longitude (-180 to 180)"),
    db: Session = Depends(get_db)
):
    """
    Get current weather & hydrological observation.
    Queries multi-tier provider cascade (IMD -> OpenWeather -> Open-Meteo) with PostgreSQL cache.
    Clearly indicates provider used ('imd', 'openweather', 'open-meteo', 'cached').
    """
    return await weather_service.get_current_weather(
        db=db, location=location, latitude=latitude, longitude=longitude
    )

@router.get("/forecast", response_model=WeatherForecastSchema)
async def get_weather_forecast(
    location: str = Query("Central Metro Basin", description="Location name"),
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Latitude"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Longitude"),
    hours: int = Query(24, ge=1, le=72, description="Forecast horizon in hours")
):
    """
    Get meteorological rainfall trajectory & temperature forecast.
    """
    return await weather_service.get_forecast(
        location=location, latitude=latitude, longitude=longitude, hours=hours
    )

@router.get("/alerts", response_model=WeatherAlertsSchema)
async def get_weather_alerts(
    location: str = Query("Central Metro Basin", description="Location name"),
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Latitude"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Longitude"),
    db: Session = Depends(get_db)
):
    """
    Get active meteorological alerts and severe rainfall warnings.
    """
    return await weather_service.get_alerts(
        latitude=latitude, longitude=longitude, location=location, db=db
    )

@router.get("/rainfall", response_model=WeatherRainfallSchema)
async def get_rainfall_data(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Latitude"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Longitude"),
    db: Session = Depends(get_db)
):
    """
    Get granular rainfall telemetry (intensity, 1h, 3h, 6h, 24h accumulation, and risk category).
    """
    return await weather_service.get_rainfall_summary(
        db=db, latitude=latitude, longitude=longitude
    )

@router.get("/status", response_model=WeatherStatusSchema)
def get_weather_status():
    """
    Diagnostic status of weather providers, API keys, cache TTL, and radar layer.
    """
    return weather_service.get_status()

@router.get("/history", response_model=List[WeatherObservationSchema])
def get_weather_history(
    location: str = Query("Central Metro Basin", description="Location name"),
    limit: int = Query(10, ge=1, le=100, description="Number of recent observations to return"),
    hours: int = Query(24, ge=1, le=168, description="History window in hours"),
    db: Session = Depends(get_db)
):
    """Get historical weather observations stored in PostgreSQL."""
    return weather_service.get_weather_history(db=db, limit=limit, hours=hours)
