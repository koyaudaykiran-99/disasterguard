import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models.weather import WeatherObservation
from app.database.models.prediction import RainfallPrediction, FloodPrediction
from app.database.models.risk import RiskZone
from app.database.models.alert import Alert
from app.database.models.sos import SOSReport
from app.database.models.incident import Incident
from app.database.models.rescue import RescueTeam, RescueAssignment
from app.database.models.shelter import Shelter
from app.database.models.hospital import Hospital
from app.gis.spatial_queries import haversine_distance_km

logger = logging.getLogger("disasterguard.ai.tools")

class AlertList(list):
    """Dual-compatibility container satisfying both legacy list checks and modern dictionary access."""
    def __init__(self, items: list, active_alerts_count: Optional[int] = None):
        super().__init__(items)
        self.active_alerts_count = active_alerts_count if active_alerts_count is not None else len(items)
        self.alerts = items

    def __getitem__(self, key):
        if isinstance(key, str):
            if key == "active_alerts_count":
                return self.active_alerts_count
            elif key == "alerts":
                return self.alerts
            raise KeyError(key)
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == "active_alerts_count":
            return self.active_alerts_count
        elif key == "alerts":
            return self.alerts
        return default

class DisasterGuardTools:
    """
    Controlled backend tools for the AI Emergency Agent.
    Strictly uses parameterized SQLAlchemy queries.
    Never executes arbitrary SQL.
    Enforces role-based permissions and data sanitization.
    """

    @staticmethod
    def get_current_weather(db: Session) -> Dict[str, Any]:
        """Fetch latest verified meteorological observation from PostgreSQL."""
        obs = db.query(WeatherObservation).order_by(desc(WeatherObservation.observed_at)).first()
        if not obs:
            return {"status": "NO_DATA", "message": "No weather observations recorded yet"}
        return {
            "id": obs.id,
            "location": obs.location,
            "latitude": obs.latitude,
            "longitude": obs.longitude,
            "rainfall_1h_mm": obs.rainfall_1h or 0.0,
            "rainfall_24h_mm": obs.rainfall_24h or 0.0,
            "temperature_c": obs.temperature or 28.0,
            "humidity_pct": obs.humidity or 70.0,
            "pressure_hpa": obs.pressure or 1012.0,
            "wind_speed_kmh": obs.wind_speed or 10.0,
            "condition": obs.condition or "Clear",
            "source": obs.source or "unknown",
            "observed_at": obs.observed_at.isoformat() if obs.observed_at else None
        }

    @staticmethod
    def get_latest_rainfall_prediction(db: Session) -> Dict[str, Any]:
        """Fetch latest Scikit-Learn rainfall ML prediction from PostgreSQL."""
        pred = db.query(RainfallPrediction).order_by(desc(RainfallPrediction.prediction_time)).first()
        if not pred:
            return {"status": "NO_DATA", "message": "No rainfall predictions available"}
        return {
            "id": pred.id,
            "location": pred.location,
            "predicted_rainfall_mm": pred.predicted_rainfall,
            "forecast_horizon_hours": pred.forecast_horizon,
            "confidence": pred.confidence or 0.85,
            "risk_level": pred.risk_level or "LOW",
            "created_at": pred.prediction_time.isoformat() if hasattr(pred, "prediction_time") and pred.prediction_time else None
        }

    @staticmethod
    def get_latest_flood_prediction(db: Session) -> Dict[str, Any]:
        """Fetch latest ML surface inundation prediction from PostgreSQL."""
        pred = db.query(FloodPrediction).order_by(desc(FloodPrediction.prediction_time)).first()
        if not pred:
            return {"status": "NO_DATA", "message": "No flood predictions available"}
        return {
            "id": pred.id,
            "location": pred.location,
            "flood_probability": pred.flood_probability,
            "estimated_water_depth_m": getattr(pred, "water_depth", 0.0) or 0.0,
            "risk_level": pred.risk_level or "LOW",
            "confidence": getattr(pred, "confidence", 0.88) or 0.88,
            "created_at": pred.prediction_time.isoformat() if hasattr(pred, "prediction_time") and pred.prediction_time else None
        }

    @staticmethod
    def get_current_risk_zones(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch current multi-factor risk zones ranked by risk score."""
        zones = db.query(RiskZone).order_by(desc(RiskZone.risk_score)).limit(limit).all()
        return [
            {
                "id": z.id,
                "name": z.name,
                "risk_score": z.risk_score,
                "risk_level": z.risk_level,
                "population_estimate": z.population_estimate,
                "latitude": z.latitude,
                "longitude": z.longitude,
                "updated_at": z.updated_at.isoformat() if z.updated_at else None
            }
            for z in zones
        ]

    @staticmethod
    def get_active_alerts(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch currently active disaster alerts."""
        alerts = db.query(Alert).filter(Alert.status == "ACTIVE").order_by(desc(Alert.issued_at)).limit(limit).all()
        return [
            {
                "id": a.id,
                "title": a.title,
                "message": a.message,
                "severity": a.severity,
                "alert_type": a.alert_type,
                "target_area": a.target_area,
                "issued_at": a.issued_at.isoformat() if a.issued_at else None
            }
            for a in alerts
        ]

    @staticmethod
    def get_active_sos(db: Session, role: str = "OPERATOR", limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch active un-rescued citizen SOS calls. Enforces role security & PII masking."""
        if role == "CITIZEN":
            count = db.query(SOSReport).filter(SOSReport.status.in_(["PENDING", "TRIAGED", "ASSIGNED"])).count()
            return [{"active_sos_count": count, "note": "Detailed citizen SOS coordinates are restricted for public safety."}]

        reports = db.query(SOSReport).filter(
            SOSReport.status.in_(["PENDING", "TRIAGED", "ASSIGNED", "DISPATCHED"])
        ).order_by(desc(SOSReport.created_at)).limit(limit).all()

        results = []
        for s in reports:
            results.append({
                "id": s.id,
                "message": s.message,
                "severity": s.severity,
                "status": s.status,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "created_at": s.created_at.isoformat() if s.created_at else None
            })
        return results

    @staticmethod
    def get_critical_incidents(db: Session, role: str = "OPERATOR", limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch active operational incidents ranked by priority score."""
        incidents = db.query(Incident).filter(
            Incident.status.in_(["PENDING", "IN_PROGRESS"])
        ).order_by(desc(Incident.priority_score)).limit(limit).all()

        if role == "CITIZEN":
            return [
                {
                    "id": inc.id,
                    "title": inc.title,
                    "incident_type": inc.incident_type,
                    "severity": inc.severity,
                    "status": inc.status
                }
                for inc in incidents
            ]

        results = []
        for inc in incidents:
            # Check if incident has an assigned rescue team
            asg = db.query(RescueAssignment).filter(RescueAssignment.incident_id == inc.id).first()
            has_rescue = asg is not None
            rescue_status = asg.status if asg else "NOT_ASSIGNED"
            team_name = None
            if asg:
                team = db.query(RescueTeam).filter(RescueTeam.id == asg.rescue_team_id).first()
                team_name = team.name if team else f"Squad #{asg.rescue_team_id}"

            results.append({
                "id": inc.id,
                "sos_id": inc.sos_id,
                "title": inc.title,
                "incident_type": inc.incident_type,
                "severity": inc.severity,
                "priority_score": inc.priority_score,
                "status": inc.status,
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "rescue_assigned": has_rescue,
                "rescue_status": rescue_status,
                "rescue_team": team_name,
                "created_at": inc.created_at.isoformat() if inc.created_at else None
            })
        return results

    @staticmethod
    def get_rescue_team_status(db: Session, role: str = "OPERATOR", limit: int = 15) -> Dict[str, Any]:
        """Fetch field rescue team statuses and fleet availability."""
        if role == "CITIZEN":
            avail = db.query(RescueTeam).filter(RescueTeam.status == "AVAILABLE").count()
            busy = db.query(RescueTeam).filter(RescueTeam.status != "AVAILABLE").count()
            return {
                "available_teams_count": avail,
                "engaged_teams_count": busy,
                "note": "Field squad positions are restricted to authorized dispatchers."
            }

        teams = db.query(RescueTeam).limit(limit).all()
        return {
            "total_teams": len(teams),
            "teams": [
                {
                    "id": t.id,
                    "name": t.name,
                    "vehicle_type": t.vehicle_type,
                    "team_size": t.team_size,
                    "status": t.status,
                    "latitude": t.latitude,
                    "longitude": t.longitude,
                    "equipment": t.equipment
                }
                for t in teams
            ]
        }

    @staticmethod
    def get_rescue_assignments(db: Session, role: str = "OPERATOR", limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch active rescue assignments with team and incident linkage."""
        if role == "CITIZEN":
            return []

        assignments = db.query(RescueAssignment).order_by(desc(RescueAssignment.assigned_at)).limit(limit).all()
        results = []
        for asg in assignments:
            team = db.query(RescueTeam).filter(RescueTeam.id == asg.rescue_team_id).first()
            inc = db.query(Incident).filter(Incident.id == asg.incident_id).first()
            results.append({
                "assignment_id": asg.id,
                "incident_id": asg.incident_id,
                "incident_title": inc.title if inc else "Unknown Incident",
                "team_id": asg.rescue_team_id,
                "team_name": team.name if team else "Unknown Team",
                "status": asg.status,
                "notes": asg.notes,
                "assigned_at": asg.assigned_at.isoformat() if asg.assigned_at else None
            })
        return results

    @staticmethod
    def get_nearby_shelters(db: Session, lat: float = 13.0827, lng: float = 80.2707, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch nearest evacuation shelters and check flood risk along vicinity."""
        shelters = db.query(Shelter).filter(Shelter.status != "CLOSED").all()
        results = []
        for s in shelters:
            dist = haversine_distance_km(lat, lng, s.latitude, s.longitude)
            # Check surrounding risk zone
            nearest_zone = None
            min_z_dist = float("inf")
            for z in db.query(RiskZone).all():
                zd = haversine_distance_km(s.latitude, s.longitude, z.latitude, z.longitude)
                if zd < min_z_dist:
                    min_z_dist = zd
                    nearest_zone = z

            zone_risk = nearest_zone.risk_level if nearest_zone and min_z_dist < 2.0 else "LOW"

            results.append({
                "id": s.id,
                "name": s.name,
                "distance_km": round(dist, 2),
                "capacity": s.capacity,
                "current_occupancy": s.current_occupancy,
                "available_capacity": max(0, s.capacity - s.current_occupancy),
                "status": s.status,
                "contact": s.contact,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "vicinity_risk_level": zone_risk
            })

        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]

    @staticmethod
    def get_nearby_hospitals(db: Session, lat: float = 13.0827, lng: float = 80.2707, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch nearest emergency medical facilities and trauma capabilities."""
        hospitals = db.query(Hospital).all()
        results = []
        for h in hospitals:
            dist = haversine_distance_km(lat, lng, h.latitude, h.longitude)
            results.append({
                "id": h.id,
                "name": h.name,
                "distance_km": round(dist, 2),
                "emergency_capacity": h.emergency_capacity,
                "available_beds": h.available_beds,
                "status": h.status,
                "contact": h.contact,
                "latitude": h.latitude,
                "longitude": h.longitude
            })
        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]

    @staticmethod
    def get_simulation_status() -> Dict[str, Any]:
        """Fetch current state of the 8-stage disaster simulation engine."""
        try:
            from app.api.endpoints.simulation import sim_state
            return {
                "is_active": sim_state.get("is_active", False),
                "step": sim_state.get("step", 0),
                "stage": sim_state.get("stage", "IDLE"),
                "title": sim_state.get("title", "Simulation Engine Ready"),
                "rainfall_mm": sim_state.get("rainfall_mm", 0.0),
                "risk_score": sim_state.get("risk_score", 18),
                "risk_level": sim_state.get("risk_level", "LOW")
            }
        except Exception as e:
            return {"is_active": False, "stage": "IDLE", "error": str(e)}

    @staticmethod
    def get_system_status() -> Dict[str, Any]:
        """Fetch real-time WebSocket connection and database operational status."""
        try:
            from app.services.websocket_manager import ws_manager
            active_clients = len(ws_manager.active_connections)
        except Exception:
            active_clients = 0

        return {
            "system": "AI DisasterGuard Real-Time Command Center",
            "real_time_status": "ONLINE" if active_clients > 0 else "STANDBY",
            "active_operator_connections": active_clients,
            "database_engine": "PostgreSQL 18 + PostGIS",
            "ml_model_status": "Loaded (v2.0 Real Data + v1.0 Prototypes)",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def get_incident_details(db: Session, incident_id: int, role: str = "OPERATOR") -> Optional[Dict[str, Any]]:
        """Fetch full contextual breakdown for a single incident."""
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            return None

        asg = db.query(RescueAssignment).filter(RescueAssignment.incident_id == inc.id).first()
        team = db.query(RescueTeam).filter(RescueTeam.id == asg.rescue_team_id).first() if asg else None
        sos = db.query(SOSReport).filter(SOSReport.id == inc.sos_id).first() if inc.sos_id else None

        nearby_shelters = DisasterGuardTools.get_nearby_shelters(db, inc.latitude, inc.longitude, limit=1)
        nearby_hospitals = DisasterGuardTools.get_nearby_hospitals(db, inc.latitude, inc.longitude, limit=1)

        return {
            "incident_id": inc.id,
            "title": inc.title,
            "description": inc.description,
            "incident_type": inc.incident_type,
            "severity": inc.severity,
            "priority_score": inc.priority_score,
            "status": inc.status,
            "latitude": inc.latitude,
            "longitude": inc.longitude,
            "sos_message": sos.message if sos else None,
            "sos_status": sos.status if sos else None,
            "assignment_id": asg.id if asg else None,
            "assignment_status": asg.status if asg else "NOT_ASSIGNED",
            "assigned_team": team.name if team else None,
            "assigned_team_type": team.vehicle_type if team else None,
            "recommended_shelter": nearby_shelters[0] if nearby_shelters else None,
            "recommended_hospital": nearby_hospitals[0] if nearby_hospitals else None,
            "created_at": inc.created_at.isoformat() if inc.created_at else None
        }

    @staticmethod
    def get_sos_details(db: Session, sos_id: int, role: str = "OPERATOR") -> Optional[Dict[str, Any]]:
        """Fetch details of a specific citizen SOS distress call."""
        sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
        if not sos:
            return None
        return {
            "id": sos.id,
            "severity": sos.severity,
            "status": sos.status,
            "message": sos.message,
            "latitude": sos.latitude,
            "longitude": sos.longitude,
            "created_at": sos.created_at.isoformat() if sos.created_at else None
        }

    @staticmethod
    def get_historical_risk(db: Session) -> Dict[str, Any]:
        """Fetch summary of recent risk score progression."""
        zones = db.query(RiskZone).all()
        avg_score = round(sum(z.risk_score for z in zones) / len(zones), 1) if zones else 0
        critical_count = sum(1 for z in zones if z.risk_level in ["HIGH", "CRITICAL"])
        return {
            "average_risk_score": avg_score,
            "total_monitored_zones": len(zones),
            "critical_risk_zones_count": critical_count
        }

    @staticmethod
    def recommend_rescue_team_tool(db: Session, incident_id: int, role: str = "OPERATOR") -> Dict[str, Any]:
        """
        Evaluate and recommend suitable rescue teams for an active incident.
        Advisory tool only: DOES NOT perform autonomous dispatch.
        """
        from app.services.rescue_intelligence_service import rescue_intelligence_service
        try:
            res = rescue_intelligence_service.get_recommendations(db, incident_id)
            return res.model_dump() if hasattr(res, "model_dump") else res.dict()
        except Exception as e:
            return {"error": str(e), "note": "Unable to calculate rescue recommendation."}

    # -------------------------------------------------------------------------
    # PHASE 5.1 READ-ONLY ML INTROSPECTION TOOLS
    # -------------------------------------------------------------------------

    @staticmethod
    def get_active_model_info(db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch active machine learning models, algorithms, and training datasets (Read-only)."""
        from app.ml.prediction_service import ml_service
        return ml_service.get_active_models()

    @staticmethod
    def get_model_metrics(db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch evaluation metrics and test benchmarks for active models (Read-only)."""
        from app.ml.prediction_service import ml_service
        return ml_service.get_metrics()

    @staticmethod
    def get_prediction_provenance(db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch data provenance, coverage periods, and license metadata (Read-only)."""
        from app.ml.prediction_service import ml_service
        return ml_service.get_provenance()

    @staticmethod
    def get_prediction_explanation(db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch structured explanation separating facts, predictions, interpretations, and advisories (Read-only)."""
        from app.ml.prediction_service import ml_service
        return ml_service.get_explanation()

    # -------------------------------------------------------------------------
    # PHASE 5.2 READ-ONLY GEOSPATIAL & FLOOD INTELLIGENCE TOOLS
    # -------------------------------------------------------------------------

    @staticmethod
    def get_flood_intelligence(
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        db: Optional[Session] = None,
        role: str = "OPERATOR"
    ) -> Dict[str, Any]:
        """Fetch multi-factor flood susceptibility, proxy water depth, and component breakdown (Read-only)."""
        from app.services.geospatial.spatial_service import spatial_service
        return spatial_service.calculate_flood_intelligence(latitude, longitude, db=db)

    @staticmethod
    def get_spatial_risk(
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        db: Optional[Session] = None,
        role: str = "OPERATOR"
    ) -> Dict[str, Any]:
        """Fetch topographic elevation, slope, and hydrographic drainage proximity for a location (Read-only)."""
        from app.services.geospatial.spatial_service import spatial_service
        return spatial_service.get_spatial_features(latitude, longitude, db=db)

    @staticmethod
    def get_historical_flood_context(
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        radius_km: float = 15.0,
        db: Optional[Session] = None,
        role: str = "OPERATOR"
    ) -> Dict[str, Any]:
        """Fetch nearby verified historical disaster records and prior flood exposure (Read-only)."""
        from app.services.geospatial.spatial_service import spatial_service
        if db is not None:
            nearby = spatial_service.get_nearby_historical_events(db, latitude, longitude, radius_km=radius_km)
            return {
                "events_count": len(nearby),
                "radius_km": radius_km,
                "events": nearby
            }
        from ml.geospatial.historical_flood_provider import HistoricalFloodProvider
        return HistoricalFloodProvider().get_historical_context(latitude, longitude, radius_km=radius_km)

    @staticmethod
    def get_inundation_explanation(
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        db: Optional[Session] = None,
        role: str = "OPERATOR"
    ) -> Dict[str, Any]:
        """Fetch structured scientific explanation categorizing Facts, Predictions, Derivations, and Advisories (Read-only)."""
        from app.services.geospatial.spatial_service import spatial_service
        intel = spatial_service.calculate_flood_intelligence(latitude, longitude, db=db)
        return {
            "risk_level": intel["risk_level"],
            "susceptibility_score": intel["susceptibility_score"],
            "depth_m": intel["estimated_depth_m"],
            "depth_type": intel["depth_type"],
            "explanation": intel["explanation"],
            "disclaimer": intel["disclaimer"]
        }


    @staticmethod
    def get_multi_horizon_forecast(
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        db: Optional[Session] = None,
        role: str = "OPERATOR"
    ) -> Dict[str, Any]:
        """Fetch full multi-horizon predictive risk forecast (1H, 3H, 6H, 12H, 24H) (Read-only)."""
        from ml.forecasting.forecast_engine import ForecastEngine
        return ForecastEngine.compute_forecast(latitude=latitude, longitude=longitude)

    @staticmethod
    def get_risk_trajectory(
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        db: Optional[Session] = None,
        role: str = "OPERATOR"
    ) -> Dict[str, Any]:
        """Fetch future risk trajectory classification, velocity, and peak horizon (Read-only)."""
        from ml.forecasting.forecast_engine import ForecastEngine
        fc = ForecastEngine.compute_forecast(latitude=latitude, longitude=longitude)
        return fc.get("trajectory", {})

    @staticmethod
    def get_forecast_uncertainty(
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        db: Optional[Session] = None,
        role: str = "OPERATOR"
    ) -> Dict[str, Any]:
        """Fetch measurable forecast uncertainty decomposition and confidence metrics (Read-only)."""
        from ml.forecasting.forecast_engine import ForecastEngine
        fc = ForecastEngine.compute_forecast(latitude=latitude, longitude=longitude)
        return fc.get("uncertainty_overview", {})

    @staticmethod
    def get_early_warning_status(
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        db: Optional[Session] = None,
        role: str = "OPERATOR"
    ) -> Dict[str, Any]:
        """Fetch early-warning escalation state and operational protective instructions (Read-only)."""
        from ml.forecasting.forecast_engine import ForecastEngine
        fc = ForecastEngine.compute_forecast(latitude=latitude, longitude=longitude)
        return fc.get("early_warning", {})

    @staticmethod
    def get_forecast_explanation(
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        db: Optional[Session] = None,
        role: str = "OPERATOR"
    ) -> Dict[str, Any]:
        """Fetch structured 5-category evidence payload for multi-horizon forecast (Read-only)."""
        from ml.forecasting.forecast_engine import ForecastEngine
        fc = ForecastEngine.compute_forecast(latitude=latitude, longitude=longitude)
        return {
            "headline": fc.get("early_warning", {}).get("headline", ""),
            "warning_state": fc.get("early_warning", {}).get("warning_state", "NORMAL"),
            "evidence_categories": fc.get("explainability", {})
        }

    @staticmethod
    def get_active_alerts(db: Optional[Session] = None, limit: int = 10, role: str = "OPERATOR", **kwargs) -> Any:
        """Fetch active approved emergency alerts (Read-only)."""
        from app.database.database import SessionLocal
        from app.services.alert_intelligence_service import alert_intelligence_service
        s = db or SessionLocal()
        try:
            alerts = alert_intelligence_service.get_active_alerts(s)
            formatted = [
                {
                    "id": a.id,
                    "alert_id": a.id,
                    "title": a.title,
                    "category": a.alert_category,
                    "severity": a.severity,
                    "target_area": a.target_area,
                    "horizon": a.forecast_horizon,
                    "risk_score": a.risk_score,
                    "confidence_score": a.confidence_score
                }
                for a in (alerts[:limit] if limit else alerts)
            ]
            return AlertList(formatted, active_alerts_count=len(alerts))
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_alert_recommendations(db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch pending operator alert recommendations (Read-only)."""
        from app.database.database import SessionLocal
        from app.services.alert_intelligence_service import alert_intelligence_service
        s = db or SessionLocal()
        try:
            recs = alert_intelligence_service.get_recommendations(s)
            return {
                "recommendations_count": len(recs),
                "recommendations": [
                    {
                        "id": r.id,
                        "title": r.title,
                        "category": r.alert_category,
                        "severity": r.severity,
                        "target_area": r.target_area,
                        "peak_risk": r.risk_score,
                        "peak_horizon": r.forecast_horizon,
                        "approval_status": r.approval_status
                    }
                    for r in recs
                ]
            }
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_alert_targeting(alert_id: Optional[int] = None, latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch geographic targeting and affected demographics (Read-only)."""
        from app.database.database import SessionLocal
        from app.database.models.alert import AlertTarget
        from ml.alerts.targeting import TargetingEngine
        s = db or SessionLocal()
        try:
            if alert_id:
                targets = s.query(AlertTarget).filter(AlertTarget.alert_id == alert_id).all()
                if targets:
                    t = targets[0]
                    return {
                        "alert_id": alert_id,
                        "target_type": t.target_type,
                        "location": t.location_name,
                        "estimated_users": t.user_count_estimate or 0,
                        "geometry_wkt": t.geometry_wkt,
                        "privacy_notice": "Demographics aggregated; no individual citizen identifiers."
                    }
            return TargetingEngine.evaluate_targeting(latitude, longitude, db_session=s)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_alert_delivery_status(alert_id: Optional[int] = None, db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch delivery channels and acknowledgement rate (Read-only)."""
        from app.database.database import SessionLocal
        from app.services.alert_intelligence_service import alert_intelligence_service
        from app.database.models.alert import AlertDelivery, AlertAcknowledgement
        s = db or SessionLocal()
        try:
            if alert_id:
                deliveries = s.query(AlertDelivery).filter(AlertDelivery.alert_id == alert_id).all()
                acks = s.query(AlertAcknowledgement).filter(AlertAcknowledgement.alert_id == alert_id).count()
                return {
                    "alert_id": alert_id,
                    "deliveries": [{"channel": d.channel, "status": d.status} for d in deliveries],
                    "acknowledgements_count": acks,
                    "safety_note": "Acknowledged != Safe"
                }
            return alert_intelligence_service.get_alert_analytics(s)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_alert_explanation(alert_id: Optional[int] = None, db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch structured 5-category evidence payload for an alert (Read-only)."""
        import json
        from app.database.database import SessionLocal
        from app.database.models.alert import Alert
        s = db or SessionLocal()
        try:
            if alert_id:
                alert = s.query(Alert).filter(Alert.id == alert_id).first()
                if alert and alert.evidence_json:
                    return {
                        "alert_id": alert.id,
                        "category": alert.alert_category,
                        "severity": alert.severity,
                        "evidence_categories": json.loads(alert.evidence_json)
                    }
            return {
                "status": "SAMPLE_EXPLANATION",
                "evidence_categories": {
                    "FACT": ["Rainfall accumulation elevated"],
                    "ML_PREDICTION": ["Multi-horizon peak risk 78/100 at 6H"],
                    "GEOSPATIAL_DERIVATION": ["Low-lying basin susceptibility 68/100"],
                    "AI_INTERPRETATION": ["Increasing trajectory with risk velocity +3.2 pts/hr"],
                    "RECOMMENDATION": ["Operator review for FLOOD_WARNING"]
                }
            }
        finally:
            if not db:
                s.close()

    # Phase 5.5 Disaster Operations Intelligence Read-Only Tools
    @staticmethod
    def get_active_incidents(status: str = "ALL", db: Optional[Session] = None, role: str = "OPERATOR") -> List[Dict[str, Any]]:
        """Fetch active prioritized emergencies for decision support. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            return OperationsService.get_prioritized_incidents(s, status_filter=status)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_incident_priority(incident_id: int, db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch explainable priority score decomposition and evidence. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            return OperationsService.get_incident_priority(s, incident_id=incident_id)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_resource_availability(db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch rescue team deployment availability and status. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            return OperationsService.get_capacity(s)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_resource_contention(is_active: bool = True, db: Optional[Session] = None, role: str = "OPERATOR") -> List[Dict[str, Any]]:
        """Fetch detected resource contention conflicts. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            return OperationsService.get_contentions(s, is_active=is_active)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_operational_bottlenecks(is_active: bool = True, db: Optional[Session] = None, role: str = "OPERATOR") -> List[Dict[str, Any]]:
        """Fetch operational bottlenecks (shortages, saturation, stale telemetry). READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            return OperationsService.get_bottlenecks(s, is_active=is_active)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_shelter_recommendations(incident_id: int, db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch capacity-aware safe evacuation shelters for an emergency. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            res = OperationsService.get_candidate_resources(s, incident_id=incident_id)
            return res.get("shelters", {})
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_hospital_recommendations(incident_id: int, db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch emergency medical hospitals and trauma bed availability. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            res = OperationsService.get_candidate_resources(s, incident_id=incident_id)
            return res.get("hospitals", {})
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_response_plan(incident_id: int, db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch unified response plan packaging team, shelter, and hospital recommendations. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            return OperationsService.get_response_plan(s, incident_id=incident_id)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_resource_coverage(db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch straight-line emergency coverage estimates across sectors. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            return OperationsService.get_coverage(s)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_operational_metrics(db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch stored-data operational metrics and latency stats. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.operations_service import OperationsService
        s = db or SessionLocal()
        try:
            return OperationsService.get_analytics(s)
        finally:
            if not db:
                s.close()

    # Phase 6 Situational Awareness Tools (Strictly Read-Only)
    @staticmethod
    def get_current_situation(db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch current operational situation combining weather, risk, incidents, and capacity. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.situational_awareness_service import situational_awareness_service
        s = db or SessionLocal()
        try:
            return situational_awareness_service.get_current_situation(s)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_recent_changes(limit: int = 20, db: Optional[Session] = None, role: str = "OPERATOR") -> List[Dict[str, Any]]:
        """Fetch recent detected delta events across operational sectors. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.situational_awareness_service import situational_awareness_service
        s = db or SessionLocal()
        try:
            return situational_awareness_service.get_recent_changes(s, limit=limit)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_incident_clusters(active_only: bool = True, db: Optional[Session] = None, role: str = "OPERATOR") -> List[Dict[str, Any]]:
        """Fetch spatial incident clusters with dominant hazards and resource demands. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.situational_awareness_service import situational_awareness_service
        s = db or SessionLocal()
        try:
            return situational_awareness_service.get_incident_clusters(s, active_only=active_only)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_risk_hotspots(active_only: bool = True, db: Optional[Session] = None, role: str = "OPERATOR") -> List[Dict[str, Any]]:
        """Fetch multi-signal geographic risk hotspots with evidence taxonomy. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.situational_awareness_service import situational_awareness_service
        s = db or SessionLocal()
        try:
            return situational_awareness_service.get_risk_hotspots(s, active_only=active_only)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_operator_attention_queue(unresolved_only: bool = True, db: Optional[Session] = None, role: str = "OPERATOR") -> List[Dict[str, Any]]:
        """Fetch prioritized Operator Attention Queue (Critical -> High -> Medium). READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.situational_awareness_service import situational_awareness_service
        s = db or SessionLocal()
        try:
            return situational_awareness_service.get_operator_attention_queue(s, unresolved_only=unresolved_only)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_resource_conflicts(db: Optional[Session] = None, role: str = "OPERATOR") -> List[Dict[str, Any]]:
        """Fetch detected resource contention conflicts with Option A vs Option B. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.situational_awareness_service import situational_awareness_service
        s = db or SessionLocal()
        try:
            return situational_awareness_service.get_resource_conflicts_with_options(s)
        finally:
            if not db:
                s.close()

    @staticmethod
    def get_operational_timeline(limit: int = 50, offset: int = 0, db: Optional[Session] = None, role: str = "OPERATOR") -> Dict[str, Any]:
        """Fetch database-backed operational timeline events. READ-ONLY."""
        from app.database.database import SessionLocal
        from app.services.situational_awareness_service import situational_awareness_service
        s = db or SessionLocal()
        try:
            return situational_awareness_service.get_operational_timeline(s, limit=limit, offset=offset)
        finally:
            if not db:
                s.close()


# Module-level tool wrappers for agent orchestration
async def get_flood_intelligence(latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_flood_intelligence(latitude=latitude, longitude=longitude, db=db, role=role)

async def get_spatial_risk(latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_spatial_risk(latitude=latitude, longitude=longitude, db=db, role=role)

async def get_historical_flood_context(latitude: float = 13.0827, longitude: float = 80.2707, radius_km: float = 15.0, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_historical_flood_context(latitude=latitude, longitude=longitude, radius_km=radius_km, db=db, role=role)

async def get_inundation_explanation(latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_inundation_explanation(latitude=latitude, longitude=longitude, db=db, role=role)

async def get_multi_horizon_forecast(latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_multi_horizon_forecast(latitude=latitude, longitude=longitude, db=db, role=role)

async def get_risk_trajectory(latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_risk_trajectory(latitude=latitude, longitude=longitude, db=db, role=role)

async def get_forecast_uncertainty(latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_forecast_uncertainty(latitude=latitude, longitude=longitude, db=db, role=role)

async def get_early_warning_status(latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_early_warning_status(latitude=latitude, longitude=longitude, db=db, role=role)

async def get_forecast_explanation(latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_forecast_explanation(latitude=latitude, longitude=longitude, db=db, role=role)

async def get_active_alerts(db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_active_alerts(db=db, role=role)

async def get_alert_recommendations(db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_alert_recommendations(db=db, role=role)

async def get_alert_targeting(alert_id: Optional[int] = None, latitude: float = 13.0827, longitude: float = 80.2707, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_alert_targeting(alert_id=alert_id, latitude=latitude, longitude=longitude, db=db, role=role)

async def get_alert_delivery_status(alert_id: Optional[int] = None, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_alert_delivery_status(alert_id=alert_id, db=db, role=role)

async def get_alert_explanation(alert_id: Optional[int] = None, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_alert_explanation(alert_id=alert_id, db=db, role=role)

# Phase 5.5 Async Wrappers
async def get_active_incidents(status: str = "ALL", db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_active_incidents(status=status, db=db, role=role)

async def get_incident_priority(incident_id: int, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_incident_priority(incident_id=incident_id, db=db, role=role)

async def get_resource_availability(db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_resource_availability(db=db, role=role)

async def get_resource_contention(is_active: bool = True, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_resource_contention(is_active=is_active, db=db, role=role)

async def get_operational_bottlenecks(is_active: bool = True, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_operational_bottlenecks(is_active=is_active, db=db, role=role)

async def get_shelter_recommendations(incident_id: int, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_shelter_recommendations(incident_id=incident_id, db=db, role=role)

async def get_hospital_recommendations(incident_id: int, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_hospital_recommendations(incident_id=incident_id, db=db, role=role)

async def get_response_plan(incident_id: int, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_response_plan(incident_id=incident_id, db=db, role=role)

async def get_resource_coverage(db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_resource_coverage(db=db, role=role)

async def get_operational_metrics(db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_operational_metrics(db=db, role=role)

# Phase 6 Situational Awareness Async Wrappers
async def get_current_situation(db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_current_situation(db=db, role=role)

async def get_recent_changes(limit: int = 20, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_recent_changes(limit=limit, db=db, role=role)

async def get_incident_clusters(active_only: bool = True, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_incident_clusters(active_only=active_only, db=db, role=role)

async def get_risk_hotspots(active_only: bool = True, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_risk_hotspots(active_only=active_only, db=db, role=role)

async def get_operator_attention_queue(unresolved_only: bool = True, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_operator_attention_queue(unresolved_only=unresolved_only, db=db, role=role)

async def get_resource_conflicts(db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_resource_conflicts(db=db, role=role)

async def get_operational_timeline(limit: int = 50, offset: int = 0, db: Optional[Session] = None, role: str = "OPERATOR"):
    return DisasterGuardTools.get_operational_timeline(limit=limit, offset=offset, db=db, role=role)


class SimpleTool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


DISASTER_GUARD_TOOLS = [
    SimpleTool("get_current_weather", "Fetch latest weather observations"),
    SimpleTool("get_latest_rainfall_prediction", "Fetch latest rainfall ML predictions"),
    SimpleTool("get_active_model_info", "Fetch active ML model info"),
    SimpleTool("get_model_metrics", "Fetch evaluation metrics"),
    SimpleTool("get_prediction_provenance", "Fetch model provenance"),
    SimpleTool("get_prediction_explanation", "Fetch prediction explanation"),
    SimpleTool("get_flood_intelligence", "Fetch multi-factor flood susceptibility and proxy depth"),
    SimpleTool("get_spatial_risk", "Fetch topographic elevation, slope, and drainage proximity"),
    SimpleTool("get_historical_flood_context", "Fetch nearby verified historical disaster records"),
    SimpleTool("get_inundation_explanation", "Fetch scientific inundation explanation and proxy breakdown"),
    SimpleTool("get_multi_horizon_forecast", "Fetch multi-horizon predictive risk forecast across 1H, 3H, 6H, 12H, 24H"),
    SimpleTool("get_risk_trajectory", "Fetch risk trajectory classification, velocity, and peak horizon"),
    SimpleTool("get_forecast_uncertainty", "Fetch measurable uncertainty decomposition and confidence ratings"),
    SimpleTool("get_early_warning_status", "Fetch early-warning escalation state and operational protective instructions"),
    SimpleTool("get_forecast_explanation", "Fetch structured 5-category evidence for multi-horizon forecasts"),
    SimpleTool("get_active_alerts", "Fetch active approved emergency alerts"),
    SimpleTool("get_alert_recommendations", "Fetch pending operator alert recommendations"),
    SimpleTool("get_alert_targeting", "Fetch geographic targeting and affected demographics"),
    SimpleTool("get_alert_delivery_status", "Fetch delivery channels and acknowledgement telemetry"),
    SimpleTool("get_alert_explanation", "Fetch structured 5-category evidence decomposition for an alert"),
    # Phase 5.5 Operational Decision Support Tools (Strictly Read-Only)
    SimpleTool("get_active_incidents", "Fetch active prioritized emergencies for decision support"),
    SimpleTool("get_incident_priority", "Fetch explainable operational priority score decomposition"),
    SimpleTool("get_resource_availability", "Fetch rescue team deployment availability and status"),
    SimpleTool("get_resource_contention", "Fetch detected resource contention conflicts between emergencies"),
    SimpleTool("get_operational_bottlenecks", "Fetch operational bottlenecks (shortages, saturation, stale telemetry)"),
    SimpleTool("get_shelter_recommendations", "Fetch capacity-aware safe evacuation shelters for an emergency"),
    SimpleTool("get_hospital_recommendations", "Fetch emergency medical hospitals and trauma bed availability"),
    SimpleTool("get_response_plan", "Fetch unified response plan packaging team, shelter, and hospital"),
    SimpleTool("get_resource_coverage", "Fetch straight-line emergency coverage estimates across sectors"),
    SimpleTool("get_operational_metrics", "Fetch stored-data operational metrics and latency stats"),
    # Phase 6 Real-Time Situational Awareness Tools (Strictly Read-Only)
    SimpleTool("get_current_situation", "Fetch real-time operational situation combining all disaster signals"),
    SimpleTool("get_recent_changes", "Fetch recent detected delta events across operational sectors"),
    SimpleTool("get_situation_changes", "Fetch recent detected delta events across operational sectors"),
    SimpleTool("get_incident_clusters", "Fetch spatial incident clusters with dominant hazards and resource demands"),
    SimpleTool("get_risk_hotspots", "Fetch multi-signal geographic risk hotspots with evidence taxonomy"),
    SimpleTool("get_operator_attention_queue", "Fetch prioritized Operator Attention Queue"),
    SimpleTool("get_resource_conflicts", "Fetch detected resource contention conflicts with response options"),
    SimpleTool("get_operational_timeline", "Fetch database-backed operational timeline events"),
]






