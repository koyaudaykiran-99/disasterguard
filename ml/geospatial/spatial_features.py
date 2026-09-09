"""
Unified Spatial Feature Extraction Engine.
Aggregates terrain, drainage, and historical memory features for any geographic coordinate.
"""

from typing import Dict, Any, Optional
from .terrain_provider import TerrainProvider
from .drainage_provider import DrainageProvider
from .historical_flood_provider import HistoricalFloodProvider
from .provider import DataSourceType

_terrain_provider = TerrainProvider()
_drainage_provider = DrainageProvider()
_historical_provider = HistoricalFloodProvider()

def extract_spatial_features(
    latitude: float,
    longitude: float,
    db_events: Optional[list] = None
) -> Dict[str, Any]:
    """
    Extract comprehensive topographic, drainage, and historical spatial features for a coordinate.
    """
    terrain = _terrain_provider.get_terrain_features(latitude, longitude)
    drainage = _drainage_provider.get_drainage_features(latitude, longitude)
    historical = _historical_provider.get_historical_context(latitude, longitude, db_events=db_events)

    # Average spatial confidence across providers
    avg_confidence = round(
        (terrain["confidence"] + drainage["confidence"] + historical["confidence"]) / 3.0,
        2
    )

    return {
        "latitude": round(latitude, 5),
        "longitude": round(longitude, 5),
        "elevation": terrain["elevation"],
        "elevation_m": terrain["elevation"],
        "slope": terrain["slope"],
        "slope_deg": terrain["slope"],
        "relative_elevation": terrain["relative_elevation"],
        "low_elevation_flag": terrain["low_elevation_flag"],
        "terrain_risk": terrain["terrain_risk_score"],
        "nearest_drainage": drainage["nearest_drainage"],
        "nearest_water_body": drainage["nearest_drainage"],
        "distance_to_drainage_km": drainage["distance_to_drainage_km"],
        "distance_to_water_km": drainage["distance_to_drainage_km"],
        "drainage_risk": drainage["drainage_risk_score"],
        "historical_event_count": historical["historical_event_count"],
        "historical_flood_score": historical["historical_risk_score"],
        "historical_severity": historical["historical_severity"],
        "spatial_confidence": avg_confidence,
        "provenance": {
            "terrain": terrain["provenance"],
            "drainage": drainage["provenance"],
            "historical": historical["provenance"]
        }
    }
