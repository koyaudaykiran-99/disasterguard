"""
REST API Endpoints for Advanced Flood Intelligence, Geospatial Inundation, and Historical Memory.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.geospatial.spatial_service import spatial_service
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType
from datetime import datetime, timezone

router = APIRouter()

@router.get("/intelligence")
def get_flood_intelligence(
    latitude: float = Query(13.0827, description="Target latitude (e.g. 13.0827 for Chennai)"),
    longitude: float = Query(80.2707, description="Target longitude (e.g. 80.2707 for Chennai)"),
    rainfall_1h: Optional[float] = Query(None, description="Current 1h rainfall (mm)"),
    rainfall_24h: Optional[float] = Query(None, description="24h accumulated rainfall (mm)"),
    save: bool = Query(False, description="Save prediction to database"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate explainable geospatial flood susceptibility and proxy inundation risk.
    """
    intel = spatial_service.calculate_flood_intelligence(
        latitude=latitude,
        longitude=longitude,
        db=db,
        rainfall_1h=rainfall_1h,
        rainfall_24h=rainfall_24h,
        save_prediction=save
    )
    return intel

@router.get("/inundation")
def get_inundation_zones(
    latitude: float = Query(13.0827, description="Center latitude"),
    longitude: float = Query(80.2707, description="Center longitude"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieve active flood inundation zones with proxy water depth and GeoJSON polygon boundaries.
    """
    intel = spatial_service.calculate_flood_intelligence(
        latitude=latitude,
        longitude=longitude,
        db=db
    )

    # Return structured inundation response for Command Map
    return {
        "center": [latitude, longitude],
        "risk_level": intel["risk_level"],
        "susceptibility_score": intel["susceptibility_score"],
        "estimated_depth_m": intel["estimated_depth_m"],
        "depth_type": intel["depth_type"],
        "depth_confidence": intel["depth_confidence"],
        "affected_area_km2": intel["affected_area_km2"],
        "polygon_coordinates": intel["polygon_coordinates"],
        "spatial_features": intel["spatial_features"],
        "explanation": intel["explanation"],
        "disclaimer": intel["disclaimer"]
    }

@router.get("/historical-events")
def get_historical_flood_events(
    latitude: Optional[float] = Query(None, description="Optional center latitude for proximity filter"),
    longitude: Optional[float] = Query(None, description="Optional center longitude for proximity filter"),
    radius_km: float = Query(15.0, description="Search radius in kilometers"),
    limit: int = Query(50, description="Max records to return"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Retrieve verified historical flood and cyclone disaster events with provenance citations.
    """
    if latitude is not None and longitude is not None:
        return spatial_service.get_nearby_historical_events(
            db=db,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
    
    events = spatial_service.get_historical_events(db=db, limit=limit)
    return [
        {
            "id": e.id,
            "event_name": e.event_name,
            "event_date": e.event_date,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "severity": e.severity,
            "rainfall_total_mm": e.rainfall_total_mm,
            "duration_hours": e.duration_hours,
            "source": e.source,
            "source_type": e.source_type,
            "description": e.description
        }
        for e in events
    ]

@router.get("/spatial-features")
def get_spatial_features_endpoint(
    latitude: float = Query(..., description="Target latitude"),
    longitude: float = Query(..., description="Target longitude"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Extract topographic, hydrographic drainage, and historical exposure features for a coordinate.
    """
    return spatial_service.get_spatial_features(latitude, longitude, db=db)

@router.get("/zones")
def get_spatial_risk_zones_geojson(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieve GeoJSON FeatureCollection of spatial risk zones with multi-factor attributes.
    """
    return spatial_service.get_spatial_risk_zones(db)
