from typing import List, Dict, Any

def create_point_feature(
    id_val: Any,
    latitude: float,
    longitude: float,
    properties: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a GeoJSON Point Feature."""
    return {
        "type": "Feature",
        "id": id_val,
        "geometry": {
            "type": "Point",
            "coordinates": [longitude, latitude] # GeoJSON uses [lng, lat]
        },
        "properties": properties
    }

def create_feature_collection(features: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Wrap features into a GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "features": features
    }

def create_inundation_polygon_feature(
    id_val: Any,
    name: str,
    coordinates_polygon: List[List[float]],
    risk_level: str,
    risk_score: int,
    water_depth: float,
    affected_population: int
) -> Dict[str, Any]:
    """Create GeoJSON Polygon Feature for flood inundation zones."""
    return {
        "type": "Feature",
        "id": id_val,
        "geometry": {
            "type": "Polygon",
            "coordinates": [coordinates_polygon]
        },
        "properties": {
            "name": name,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "water_depth_m": water_depth,
            "affected_population": affected_population
        }
    }
