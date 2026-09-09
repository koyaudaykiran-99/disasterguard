from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.weather_service import weather_service
from app.schemas.weather import WeatherObservationSchema, WeatherForecastSchema
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
    Fetches real observation from Open-Meteo API (or cached in PostgreSQL within TTL).
    """
    return await weather_service.get_current_weather(
        db=db, location=location, latitude=latitude, longitude=longitude
    )

@router.get("/forecast", response_model=WeatherForecastSchema)
async def get_weather_forecast(
    location: str = Query("Central Metro Basin", description="Location name"),
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Latitude"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Longitude"),
    hours: int = Query(6, ge=1, le=48)
):
    """Get AI/meteorological rainfall forecast."""
    return await weather_service.get_forecast(
        location=location, latitude=latitude, longitude=longitude, hours=hours
    )

@router.get("/history", response_model=List[WeatherObservationSchema])
def get_weather_history(
    location: str = Query("Central Metro Basin", description="Location name"),
    limit: int = Query(10, ge=1, le=100, description="Number of recent observations to return"),
    hours: int = Query(24, ge=1, le=168, description="History window in hours"),
    db: Session = Depends(get_db)
):
    """Get historical weather observations stored in PostgreSQL."""
    return weather_service.get_weather_history(db=db, limit=limit, hours=hours)
