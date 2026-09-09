"""
Unified Backend Spatial and Flood Intelligence Service.
Coordinates database PostGIS queries, ML susceptibility calculations, and SOS spatial enrichment.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone

from app.database.models.historical_flood import HistoricalFloodEvent
from app.database.models.inundation import InundationPrediction
from app.database.models.risk import RiskZone
from app.database.models.weather import WeatherObservation
from app.database.models.shelter import Shelter
from app.database.models.hospital import Hospital
from app.database.models.rescue import RescueTeam
from app.gis.spatial_queries import spatial_distance_km, spatial_dwithin
from app.core.logging import logger

import sys
import os
# Ensure ml module is importable
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.geospatial.spatial_features import extract_spatial_features
from ml.geospatial.susceptibility import calculate_flood_susceptibility
from ml.geospatial.inundation import InundationEstimator

class SpatialService:
    """
    Manages geospatial risk zones, historical disaster memory, and SOS contextual enrichment.
    """

    def get_historical_events(self, db: Session, limit: int = 50) -> List[HistoricalFloodEvent]:
        """Fetch all verified historical disaster records."""
        return db.query(HistoricalFloodEvent).order_by(desc(HistoricalFloodEvent.event_date)).limit(limit).all()

    def get_nearby_historical_events(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0
    ) -> List[Dict[str, Any]]:
        """Find historical disaster events within radius_km using spatial distance."""
        all_events = db.query(HistoricalFloodEvent).all()
        results = []
        for ev in all_events:
            d = spatial_distance_km(db, latitude, longitude, ev.latitude, ev.longitude)
            if d <= radius_km:
                results.append({
                    "id": ev.id,
                    "event_name": ev.event_name,
                    "event_date": ev.event_date,
                    "latitude": ev.latitude,
                    "longitude": ev.longitude,
                    "severity": ev.severity,
                    "rainfall_total_mm": ev.rainfall_total_mm,
                    "duration_hours": ev.duration_hours,
                    "source": ev.source,
                    "source_type": ev.source_type,
                    "description": ev.description,
                    "distance_km": d
                })
        results.sort(key=lambda x: x["distance_km"])
        return results

    def get_spatial_features(
        self,
        latitude: float,
        longitude: float,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Extract terrain, drainage, and historical memory features for coordinate."""
        db_events = None
        if db is not None:
            try:
                evs = db.query(HistoricalFloodEvent).all()
                if evs:
                    db_events = [
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
                            "description": e.description
                        }
                        for e in evs
                    ]
            except Exception as ex:
                logger.warning(f"Could not load historical events from DB: {ex}")

        return extract_spatial_features(latitude, longitude, db_events=db_events)

    def calculate_flood_intelligence(
        self,
        latitude: float,
        longitude: float,
        db: Optional[Session] = None,
        rainfall_1h: Optional[float] = None,
        rainfall_24h: Optional[float] = None,
        save_prediction: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate full flood susceptibility and proxy inundation depth for a coordinate.
        Pulls latest meteorological observations if not explicitly provided.
        """
        # Resolve meteorological variables from DB if available
        if (rainfall_1h is None or rainfall_24h is None) and db is not None:
            latest_obs = db.query(WeatherObservation).order_by(desc(WeatherObservation.observed_at)).first()
            if latest_obs:
                rainfall_1h = latest_obs.rainfall_1h if rainfall_1h is None else rainfall_1h
                rainfall_24h = latest_obs.rainfall_24h if rainfall_24h is None else rainfall_24h

        rf_1h = rainfall_1h or 15.0
        rf_3h = rf_1h * 2.2
        rf_6h = rf_1h * 3.5
        rf_12h = rf_1h * 5.0
        rf_24h = rainfall_24h or 65.0

        db_events = None
        if db is not None:
            try:
                evs = db.query(HistoricalFloodEvent).all()
                if evs:
                    db_events = [
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
                            "description": e.description
                        }
                        for e in evs
                    ]
            except Exception:
                pass

        inundation = InundationEstimator.estimate_inundation(
            rainfall_1h=rf_1h,
            rainfall_3h=rf_3h,
            rainfall_6h=rf_6h,
            rainfall_12h=rf_12h,
            rainfall_24h=rf_24h,
            latitude=latitude,
            longitude=longitude,
            db_events=db_events
        )

        if save_prediction and db is not None:
            try:
                pred_rec = InundationPrediction(
                    latitude=latitude,
                    longitude=longitude,
                    risk_level=inundation["risk_level"],
                    susceptibility_score=inundation["susceptibility_score"],
                    estimated_depth_m=inundation["estimated_depth_m"],
                    depth_confidence=inundation["depth_confidence"],
                    depth_type=inundation["depth_type"],
                    affected_area_km2=inundation["affected_area_km2"],
                    data_source_type=inundation["data_source_type"],
                    model_version=inundation["model_version"],
                    explanation=str(inundation["explanation"])
                )
                db.add(pred_rec)
                db.commit()
            except Exception as e:
                logger.error(f"Error saving inundation prediction: {e}")
                db.rollback()

        return inundation

    def enrich_sos_with_flood_context(
        self,
        db: Session,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Enrich citizen SOS coordinates with localized flood risk, nearest shelter, and nearest hospital.
        Advisory information for human command center dispatchers.
        """
        # 1. Flood intelligence at SOS location
        flood_intel = self.calculate_flood_intelligence(latitude, longitude, db=db)

        # 2. Nearest shelter
        shelters = db.query(Shelter).all()
        nearest_shelter = None
        min_shelter_dist = 999.0
        for s in shelters:
            d = spatial_distance_km(db, latitude, longitude, s.latitude, s.longitude)
            if d < min_shelter_dist:
                min_shelter_dist = d
                nearest_shelter = s

        # 3. Nearest hospital
        hospitals = db.query(Hospital).all()
        nearest_hospital = None
        min_hosp_dist = 999.0
        for h in hospitals:
            d = spatial_distance_km(db, latitude, longitude, h.latitude, h.longitude)
            if d < min_hosp_dist:
                min_hosp_dist = d
                nearest_hospital = h

        # 4. Available rescue teams within 10 km
        teams = db.query(RescueTeam).filter(RescueTeam.status == "AVAILABLE").all()
        available_nearby_teams = []
        for t in teams:
            d = spatial_distance_km(db, latitude, longitude, t.latitude, t.longitude)
            if d <= 10.0:
                available_nearby_teams.append({
                    "id": t.id,
                    "name": t.name,
                    "distance_km": d,
                    "vehicle_type": t.vehicle_type
                })
        available_nearby_teams.sort(key=lambda x: x["distance_km"])

        # 5. Multi-Horizon Predictive Risk Context (Phase 5.3 Advisory)
        multi_horizon = None
        try:
            from ml.forecasting.forecast_engine import ForecastEngine
            fc = ForecastEngine.compute_forecast(latitude, longitude)
            horizons = fc.get("horizons", {})
            traj = fc.get("trajectory", {})
            multi_horizon = {
                "1h_risk": horizons.get("1H", {}).get("risk_score"),
                "3h_risk": horizons.get("3H", {}).get("risk_score"),
                "6h_risk": horizons.get("6H", {}).get("risk_score"),
                "12h_risk": horizons.get("12H", {}).get("risk_score"),
                "24h_risk": horizons.get("24H", {}).get("risk_score"),
                "trajectory": traj.get("trajectory", "STABLE"),
                "peak_risk_horizon": traj.get("peak_horizon", "6H"),
                "peak_risk_score": traj.get("peak_risk"),
                "forecast_confidence": fc.get("uncertainty_overview", {}).get("confidence_rating", "MEDIUM"),
                "early_warning_state": fc.get("early_warning", {}).get("warning_state", "NORMAL")
            }
        except Exception as fce:
            logger.warning(f"Could not compute forecast context for SOS: {fce}")

        return {
            "flood_risk_level": flood_intel["risk_level"],
            "flood_susceptibility_score": flood_intel["susceptibility_score"],
            "estimated_water_depth_m": flood_intel["estimated_depth_m"],
            "depth_type": flood_intel["depth_type"],
            "terrain_risk": flood_intel["spatial_features"]["terrain_risk"],
            "elevation_m": flood_intel["spatial_features"]["elevation"],
            "nearest_drainage": flood_intel["spatial_features"]["nearest_drainage"],
            "distance_to_drainage_km": flood_intel["spatial_features"]["distance_to_drainage_km"],
            "historical_exposure": flood_intel["spatial_features"]["historical_severity"],
            "nearest_shelter": {
                "id": nearest_shelter.id if nearest_shelter else None,
                "name": nearest_shelter.name if nearest_shelter else None,
                "distance_km": round(min_shelter_dist, 2) if nearest_shelter else None,
                "status": nearest_shelter.status if nearest_shelter else None
            } if nearest_shelter else None,
            "nearest_hospital": {
                "id": nearest_hospital.id if nearest_hospital else None,
                "name": nearest_hospital.name if nearest_hospital else None,
                "distance_km": round(min_hosp_dist, 2) if nearest_hospital else None,
                "status": nearest_hospital.status if nearest_hospital else None
            } if nearest_hospital else None,
            "available_rescue_teams_count": len(available_nearby_teams),
            "nearby_rescue_teams": available_nearby_teams[:3],
            "multi_horizon_forecast": multi_horizon
        }

    def get_spatial_risk_zones(self, db: Session) -> Dict[str, Any]:
        """
        Generate GeoJSON FeatureCollection of spatial risk zones with multi-factor attributes.
        """
        zones = db.query(RiskZone).all()
        features = []
        for z in zones:
            # Multi-factor intelligence at zone centroid
            intel = self.calculate_flood_intelligence(z.latitude, z.longitude, db=db)
            
            # Use zone geometry if available, or generate bounding box around centroid
            coords = []
            if z.geometry_wkt and "POLYGON" in z.geometry_wkt.upper():
                # Parse polygon from WKT or generate polygon around centroid
                coords = [
                    [z.longitude - 0.015, z.latitude - 0.015],
                    [z.longitude + 0.015, z.latitude - 0.015],
                    [z.longitude + 0.015, z.latitude + 0.015],
                    [z.longitude - 0.015, z.latitude + 0.015],
                    [z.longitude - 0.015, z.latitude - 0.015],
                ]
            else:
                coords = [
                    [z.longitude - 0.01, z.latitude - 0.01],
                    [z.longitude + 0.01, z.latitude - 0.01],
                    [z.longitude + 0.01, z.latitude + 0.01],
                    [z.longitude - 0.01, z.latitude + 0.01],
                    [z.longitude - 0.01, z.latitude - 0.01],
                ]

            features.append({
                "type": "Feature",
                "id": z.id,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                },
                "properties": {
                    "name": z.name,
                    "risk_level": intel["risk_level"],
                    "risk_score": intel["susceptibility_score"],
                    "estimated_depth_m": intel["estimated_depth_m"],
                    "depth_type": intel["depth_type"],
                    "population_estimate": z.population_estimate,
                    "elevation_m": intel["spatial_features"]["elevation"],
                    "slope_deg": intel["spatial_features"]["slope"],
                    "nearest_drainage": intel["spatial_features"]["nearest_drainage"],
                    "historical_severity": intel["spatial_features"]["historical_severity"],
                    "data_source_type": intel["data_source_type"],
                    "model_version": intel["model_version"],
                    "updated_at": z.updated_at.isoformat() if z.updated_at else datetime.now(timezone.utc).isoformat()
                }
            })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    # Method Aliases
    assess_flood_intelligence = calculate_flood_intelligence

    def get_inundation_zones(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """Fetch inundation zones with automatic DB session handling."""
        if db is not None:
            return self.get_spatial_risk_zones(db)
        from app.database.database import SessionLocal
        local_db = SessionLocal()
        try:
            return self.get_spatial_risk_zones(local_db)
        finally:
            local_db.close()

spatial_service = SpatialService()

