"""
AI-DisasterGuard — Geospatial Alert Targeting Engine
Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication
"""

import math
from typing import Dict, Any, List, Optional
from shapely.geometry import Point, Polygon
from shapely import wkt
from ml.alerts import TargetType

class TargetingEngine:
    """
    Computes location-aware target zones, bounding geometries, and privacy-conscious
    affected population estimates for emergency warnings.
    """

    @staticmethod
    def generate_bounding_polygon_wkt(lat: float, lon: float, radius_km: float = 5.0, num_points: int = 16) -> str:
        """
        Generates a circular polygon approximation around (lat, lon) in WKT format.
        """
        points = []
        # Approximate 1 deg latitude ~ 111 km, 1 deg longitude ~ 111 * cos(lat) km
        lat_rad = math.radians(lat)
        deg_lat = radius_km / 111.0
        deg_lon = radius_km / (111.0 * max(0.01, math.cos(lat_rad)))

        for i in range(num_points):
            angle = 2.0 * math.pi * i / num_points
            p_lat = lat + deg_lat * math.sin(angle)
            p_lon = lon + deg_lon * math.cos(angle)
            points.append((round(p_lon, 6), round(p_lat, 6)))
        points.append(points[0]) # Close polygon ring

        poly = Polygon(points)
        return poly.wkt

    @staticmethod
    def evaluate_targeting(
        latitude: float,
        longitude: float,
        location_name: str = "Central Metro Sector",
        radius_km: float = 5.0,
        db_session: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Evaluate geographic targeting, identifying affected zones, shelters, and
        privacy-safe population estimates without exposing individual personal data.
        """
        poly_wkt = TargetingEngine.generate_bounding_polygon_wkt(latitude, longitude, radius_km)
        area_sq_km = round(math.pi * (radius_km ** 2), 1)

        # Baseline urban density estimate: ~1,200 people per sq km in metro zones
        estimated_population = int(area_sq_km * 1200)
        intersecting_zones: List[str] = [location_name]
        nearby_shelters_count = 0
        nearby_hospitals_count = 0
        nearby_rescue_teams_count = 0

        # If DB session is provided, query actual database entities
        if db_session is not None:
            try:
                from app.database.models.risk import RiskZone
                from app.database.models.shelter import Shelter
                from app.database.models.hospital import Hospital
                from app.database.models.rescue import RescueTeam
                from app.gis.spatial_queries import haversine_distance_km

                # Find RiskZones within radius
                zones = db_session.query(RiskZone).all()
                zone_names = []
                total_zone_pop = 0
                for z in zones:
                    d = haversine_distance_km(latitude, longitude, z.latitude, z.longitude)
                    if d <= radius_km * 1.5:
                        zone_names.append(z.name)
                        total_zone_pop += (z.population_estimate or 1500)
                if zone_names:
                    intersecting_zones = list(set(zone_names))
                    if total_zone_pop > 0:
                        estimated_population = total_zone_pop

                # Shelters in zone
                shelters = db_session.query(Shelter).all()
                for s in shelters:
                    if haversine_distance_km(latitude, longitude, s.latitude, s.longitude) <= radius_km:
                        nearby_shelters_count += 1

                # Hospitals in zone
                hospitals = db_session.query(Hospital).all()
                for h in hospitals:
                    if haversine_distance_km(latitude, longitude, h.latitude, h.longitude) <= radius_km:
                        nearby_hospitals_count += 1

                # Rescue teams in zone
                teams = db_session.query(RescueTeam).all()
                for t in teams:
                    if t.latitude and t.longitude:
                        if haversine_distance_km(latitude, longitude, t.latitude, t.longitude) <= radius_km:
                            nearby_rescue_teams_count += 1

            except Exception:
                pass

        target_summary = {
            "target_type": TargetType.GEO_ZONE.value,
            "location_name": location_name,
            "center": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius_km,
            "affected_area_sq_km": area_sq_km,
            "estimated_users": estimated_population,
            "is_estimate_approximate": True,
            "geometry_wkt": poly_wkt,
            "intersecting_zones": intersecting_zones,
            "critical_facilities": {
                "shelters_count": nearby_shelters_count,
                "hospitals_count": nearby_hospitals_count,
                "rescue_teams_count": nearby_rescue_teams_count
            },
            "privacy_notice": "Individual citizen identifiers are aggregated; no personal data exposed."
        }
        return target_summary
