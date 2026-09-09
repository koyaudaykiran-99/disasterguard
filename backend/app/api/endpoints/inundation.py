from fastapi import APIRouter
from app.services.inundation_service import inundation_service
from typing import Dict, Any

router = APIRouter()

@router.get("/geojson")
@router.get("/zones")
def get_inundation_geojson() -> Dict[str, Any]:
    """Get Leaflet-compatible GeoJSON FeatureCollection of flood inundation zones."""
    return inundation_service.get_inundation_geojson()
