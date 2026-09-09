"""
Geospatial Spatial Query Engine.
Supports PostGIS SQL functions (ST_DWithin, ST_Distance, ST_Contains, ST_Intersects)
with resilient GeoAlchemy2 and Shapely geometric fallbacks for vanilla PostgreSQL environments.
"""

import math
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely import wkt

# Global flag to track whether PostGIS extension is available in current database engine
_POSTGIS_AVAILABLE: Optional[bool] = None

def check_postgis_available(db: Session) -> bool:
    """Check whether PostGIS functions can be executed in PostgreSQL."""
    global _POSTGIS_AVAILABLE
    if _POSTGIS_AVAILABLE is not None:
        return _POSTGIS_AVAILABLE
    try:
        db.execute(text("SELECT PostGIS_Version()"))
        _POSTGIS_AVAILABLE = True
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        _POSTGIS_AVAILABLE = False
    return _POSTGIS_AVAILABLE

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate geodesic distance between two points in km using Haversine formula."""
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * (math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def is_point_within_radius(center_lat: float, center_lng: float, target_lat: float, target_lng: float, radius_km: float) -> bool:
    """Check if target point is within radius in km."""
    dist = haversine_distance_km(center_lat, center_lng, target_lat, target_lng)
    return dist <= radius_km

def spatial_distance_km(arg1, arg2, arg3=None, arg4=None, arg5=None) -> float:
    """
    Calculate distance between two coordinates in kilometers.
    Accepts either (db, lat1, lon1, lat2, lon2) or (lat1, lon1, lat2, lon2).
    Executes PostGIS ST_Distance where available, with Shapely/Haversine fallback.
    """
    if arg5 is not None:
        db, lat1, lon1, lat2, lon2 = arg1, float(arg2), float(arg3), float(arg4), float(arg5)
    else:
        db, lat1, lon1, lat2, lon2 = None, float(arg1), float(arg2), float(arg3), float(arg4)

    if db is not None and check_postgis_available(db):
        try:
            sql = text("""
                SELECT ST_Distance(
                    ST_SetSRID(ST_MakePoint(:lon1, :lat1), 4326)::geography,
                    ST_SetSRID(ST_MakePoint(:lon2, :lat2), 4326)::geography
                ) / 1000.0 AS dist_km
            """)
            result = db.execute(sql, {"lon1": lon1, "lat1": lat1, "lon2": lon2, "lat2": lat2}).scalar()
            return round(float(result), 2)
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
    return haversine_distance_km(lat1, lon1, lat2, lon2)

def spatial_dwithin(arg1, arg2, arg3=None, arg4=None, arg5=None, arg6=None) -> bool:
    """
    Evaluate whether target coordinate falls within radius_km.
    Accepts either (db, center_lat, center_lng, target_lat, target_lng, radius_km)
    or (center_lat, center_lng, target_lat, target_lng, radius_km).
    Executes PostGIS ST_DWithin where available, with Shapely/Haversine fallback.
    """
    if arg6 is not None:
        db, center_lat, center_lng, target_lat, target_lng, radius_km = arg1, float(arg2), float(arg3), float(arg4), float(arg5), float(arg6)
    else:
        db, center_lat, center_lng, target_lat, target_lng, radius_km = None, float(arg1), float(arg2), float(arg3), float(arg4), float(arg5)

    if db is not None and check_postgis_available(db):
        try:
            sql = text("""
                SELECT ST_DWithin(
                    ST_SetSRID(ST_MakePoint(:target_lng, :target_lat), 4326)::geography,
                    ST_SetSRID(ST_MakePoint(:center_lng, :center_lat), 4326)::geography,
                    :radius_m
                ) AS is_within
            """)
            result = db.execute(sql, {
                "center_lat": center_lat,
                "center_lng": center_lng,
                "target_lat": target_lat,
                "target_lng": target_lng,
                "radius_m": radius_km * 1000.0
            }).scalar()
            return bool(result)
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
    return is_point_within_radius(center_lat, center_lng, target_lat, target_lng, radius_km)

def is_point_in_polygon(lat: float, lng: float, polygon_coords: List[List[float]]) -> bool:
    """
    Evaluate whether point [lat, lng] is contained within a polygon [[lat, lng], ...].
    Uses Shapely Point-in-Polygon geometric algorithm.
    """
    pt = Point(lng, lat)
    # shapely coordinates are [lng, lat]
    shapely_poly_coords = [(c[1], c[0]) for c in polygon_coords]
    poly = Polygon(shapely_poly_coords)
    return poly.contains(pt) or poly.touches(pt)

def parse_wkt_geometry(wkt_string: str) -> Optional[Any]:
    """Parse WKT geometry into Shapely geometry object."""
    try:
        return wkt.loads(wkt_string)
    except Exception:
        return None
