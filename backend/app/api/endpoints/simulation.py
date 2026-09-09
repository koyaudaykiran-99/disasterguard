from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.database.database import get_db
from app.database.models.weather import WeatherObservation
from app.database.models.prediction import RainfallPrediction, FloodPrediction
from app.database.models.risk import RiskZone
from app.database.models.alert import Alert
from app.database.models.sos import SOSReport
from app.database.models.incident import Incident
from app.database.models.rescue import RescueTeam, RescueAssignment, RescueDispatchAuditLog
from app.database.models.user import User, UserRole
from app.schemas.rescue import RescueDispatchConfirmRequest
from app.services.prediction_service import prediction_service
from app.services.alert_service import alert_service
from app.schemas.alert import AlertCreate
from app.services.sos_service import sos_service
from app.schemas.sos import SOSCreate
from app.services.rescue_service import rescue_service
from app.services.rescue_intelligence_service import rescue_intelligence_service
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType
from app.core.logging import logger

router = APIRouter()

# Global state memory for simulation state machine
sim_state: Dict[str, Any] = {
    "is_active": False,
    "step": 0,
    "total_steps": 8,
    "stage": "IDLE",
    "title": "Simulation Engine Ready",
    "description": "8-stage backend-driven disaster simulation ready to start.",
    "risk_score": 18,
    "risk_level": "LOW",
    "rainfall_mm": 12.5,
    "flood_prob": 0.05,
    "active_alerts": 0,
    "active_sos": 0,
    "active_incidents": 0,
    "recommended_rescue_team": 0,
    "metrics": {},
    "database_changes": {},
    "simulation_active": False,
    "simulation_complete": False,
    "simulated_record_ids": {
        "weather_observation_id": None,
        "rainfall_prediction_id": None,
        "flood_prediction_id": None,
        "alert_id": None,
        "sos_id": None,
        "incident_id": None,
        "rescue_assignment_id": None,
    }
}


def _clean_simulation_records(db: Session) -> Dict[str, int]:
    """
    Safely delete simulation-created records tagged with [SIMULATION]
    and restore risk zones and rescue teams to baseline.
    Never touches seed or non-simulation records.
    """
    cleaned_counts = {
        "assignments": 0,
        "incidents": 0,
        "sos": 0,
        "alerts": 0,
        "rainfall_predictions": 0,
        "flood_predictions": 0,
        "weather_observations": 0,
        "teams_restored": 0,
        "zones_restored": 0,
    }

    try:
        # 1. Find simulation incidents
        sim_incidents = db.query(Incident).filter(
            (Incident.title.like("%[SIMULATION]%")) | (Incident.description.like("%[SIMULATION]%"))
        ).all()
        sim_incident_ids = [inc.id for inc in sim_incidents]

        # Collect team IDs of simulation assignments to restore only those
        if sim_incident_ids:
            sim_assigns = db.query(RescueAssignment).filter(
                (RescueAssignment.incident_id.in_(sim_incident_ids)) | (RescueAssignment.notes.like("%[SIMULATION]%"))
            ).all()
        else:
            sim_assigns = db.query(RescueAssignment).filter(RescueAssignment.notes.like("%[SIMULATION]%")).all()
        sim_team_ids = {a.rescue_team_id for a in sim_assigns}

        # 2. Delete rescue assignments and audit logs linked to simulation incidents or marked with [SIMULATION]
        if sim_incident_ids:
            db.query(RescueDispatchAuditLog).filter(
                RescueDispatchAuditLog.incident_id.in_(sim_incident_ids)
            ).delete(synchronize_session=False)
            deleted_assignments = db.query(RescueAssignment).filter(
                (RescueAssignment.incident_id.in_(sim_incident_ids)) | (RescueAssignment.notes.like("%[SIMULATION]%"))
            ).delete(synchronize_session=False)
        else:
            deleted_assignments = db.query(RescueAssignment).filter(
                RescueAssignment.notes.like("%[SIMULATION]%")
            ).delete(synchronize_session=False)
        cleaned_counts["assignments"] = deleted_assignments

        # 3. Restore only simulation rescue teams to AVAILABLE if not active on real incidents
        restored = 0
        if sim_team_ids:
            teams = db.query(RescueTeam).filter(RescueTeam.id.in_(sim_team_ids)).all()
            for t in teams:
                other_active = db.query(RescueAssignment).filter(
                    RescueAssignment.rescue_team_id == t.id,
                    RescueAssignment.status.in_(["DISPATCHED", "EN_ROUTE", "ON_SCENE"])
                ).first()
                if not other_active:
                    t.status = "AVAILABLE"
                    restored += 1
        cleaned_counts["teams_restored"] = restored

        # 4. Delete simulation incidents
        if sim_incident_ids:
            deleted_inc = db.query(Incident).filter(Incident.id.in_(sim_incident_ids)).delete(synchronize_session=False)
            cleaned_counts["incidents"] = deleted_inc

        # 5. Delete simulation SOS reports
        deleted_sos = db.query(SOSReport).filter(SOSReport.message.like("%[SIMULATION]%")).delete(synchronize_session=False)
        cleaned_counts["sos"] = deleted_sos

        # 6. Delete simulation alerts
        deleted_alerts = db.query(Alert).filter(
            (Alert.title.like("%[SIMULATION]%")) | (Alert.message.like("%[SIMULATION]%")) | (Alert.is_simulation == True)
        ).delete(synchronize_session=False)
        cleaned_counts["alerts"] = deleted_alerts

        # 7. Delete simulation predictions
        del_rf = db.query(RainfallPrediction).filter(RainfallPrediction.location.like("%[SIMULATION]%")).delete(synchronize_session=False)
        del_fl = db.query(FloodPrediction).filter(FloodPrediction.location.like("%[SIMULATION]%")).delete(synchronize_session=False)
        cleaned_counts["rainfall_predictions"] = del_rf
        cleaned_counts["flood_predictions"] = del_fl

        # 8. Delete simulation weather observations
        del_w = db.query(WeatherObservation).filter(WeatherObservation.location.like("%[SIMULATION]%")).delete(synchronize_session=False)
        cleaned_counts["weather_observations"] = del_w

        # 9. Restore risk zones to baseline
        zones = db.query(RiskZone).all()
        for z in zones:
            z.risk_score = 18
            z.risk_level = "LOW"
            z.updated_at = datetime.now(timezone.utc)
        cleaned_counts["zones_restored"] = len(zones)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error during simulation records cleanup: {e}")
        raise e

    return cleaned_counts


def _get_active_counts(db: Session) -> Dict[str, int]:
    """Retrieve count of active alerts, active SOS, and active incidents from PostgreSQL."""
    alerts_count = db.query(Alert).filter(Alert.status == "ACTIVE").count()
    sos_count = db.query(SOSReport).filter(SOSReport.status != "RESCUED").count()
    inc_count = db.query(Incident).filter(Incident.status != "RESOLVED").count()
    return {
        "alerts": alerts_count,
        "sos": sos_count,
        "incidents": inc_count,
    }


@router.post("/start")
def start_simulation(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Start the 8-Stage Ideathon Emergency Simulation Engine.
    Executes STEP 1 (NORMAL): cleans previous simulation records,
    establishes baseline weather in PostgreSQL, and sets risk zones to LOW (18).
    """
    # Prevent concurrent simulation runs if already running and mid-simulation
    if sim_state["is_active"] and not sim_state["simulation_complete"] and sim_state["step"] > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A simulation is already in progress. Reset the simulation before starting a new run."
        )

    # 1. Clean previous simulation artifacts safely
    _clean_simulation_records(db)

    # 2. Insert baseline weather observation into PostgreSQL
    baseline_obs = WeatherObservation(
        location="[SIMULATION] Baseline Meteorological Station Alpha",
        rainfall_1h=2.5,
        rainfall_3h=5.0,
        rainfall_6h=8.0,
        rainfall_24h=12.5,
        temperature=27.0,
        humidity=58.0,
        wind_speed=14.0,
        pressure=1012.0,
        condition="Partly Cloudy",
        source="simulation",
        observed_at=datetime.now(timezone.utc)
    )
    db.add(baseline_obs)
    db.commit()
    db.refresh(baseline_obs)

    # 3. Set risk zones to baseline score ~18 (LOW)
    zones = db.query(RiskZone).all()
    for z in zones:
        z.risk_score = 18
        z.risk_level = "LOW"
        z.updated_at = datetime.now(timezone.utc)
    db.commit()

    active_counts = _get_active_counts(db)

    sim_state.update({
        "is_active": True,
        "simulation_active": True,
        "simulation_complete": False,
        "step": 1,
        "total_steps": 8,
        "stage": "NORMAL",
        "title": "Normal Conditions",
        "description": "Baseline meteorological and hydrological conditions established across all monitoring sectors.",
        "risk_score": 18,
        "risk_level": "LOW",
        "rainfall_mm": 12.5,
        "flood_prob": 0.08,
        "active_alerts": active_counts["alerts"],
        "active_sos": active_counts["sos"],
        "active_incidents": active_counts["incidents"],
        "recommended_rescue_team": 0,
        "metrics": {
            "rainfall_1h_mm": 2.5,
            "rainfall_24h_mm": 12.5,
            "flood_probability": 0.08,
            "atmospheric_pressure_hpa": 1012.0,
            "inundation_depth_m": 0.0
        },
        "database_changes": {
            "weather_observation_id": baseline_obs.id,
            "risk_zones_reset": len(zones),
            "target_score": 18,
            "risk_level": "LOW"
        },
        "simulated_record_ids": {
            "weather_observation_id": baseline_obs.id,
            "rainfall_prediction_id": None,
            "flood_prediction_id": None,
            "alert_id": None,
            "sos_id": None,
            "incident_id": None,
            "rescue_assignment_id": None,
        }
    })

    try:
        ws_manager.broadcast_event(
            DomainEvent(
                event=EventType.SIMULATION_STAGE_CHANGED,
                timestamp=datetime.now(timezone.utc).isoformat(),
                entity_type="simulation",
                severity=sim_state.get("risk_level", "LOW"),
                data=dict(sim_state)
            )
        )
    except Exception as e:
        pass

    return sim_state


@router.post("/step")
def step_simulation(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Advance the 8-Stage Simulation Engine by 1 step.
    Performs real PostgreSQL 18 database operations corresponding to the target stage.
    """
    if not sim_state["is_active"] or sim_state["step"] == 0:
        return start_simulation(db)

    next_step = min(sim_state["step"] + 1, 8)
    sim_state["step"] = next_step

    # -------------------------------------------------------------------------
    # STEP 2 — HEAVY RAINFALL
    # -------------------------------------------------------------------------
    if next_step == 2:
        heavy_obs = WeatherObservation(
            location="[SIMULATION] Heavy Rainfall Station Beta",
            rainfall_1h=55.0,
            rainfall_3h=85.0,
            rainfall_6h=102.0,
            rainfall_24h=110.0,
            temperature=23.0,
            humidity=95.0,
            wind_speed=48.0,
            pressure=993.0,
            condition="Violent Rain / Storm",
            source="simulation",
            observed_at=datetime.now(timezone.utc)
        )
        db.add(heavy_obs)
        db.commit()
        db.refresh(heavy_obs)
        sim_state["simulated_record_ids"]["weather_observation_id"] = heavy_obs.id

        # Update risk zones moderately
        zones = db.query(RiskZone).all()
        for z in zones:
            z.risk_score = 45
            z.risk_level = "MODERATE"
            z.updated_at = datetime.now(timezone.utc)
        db.commit()

        active_counts = _get_active_counts(db)
        sim_state.update({
            "stage": "HEAVY_RAINFALL",
            "title": "Heavy Rainfall Ingress",
            "description": "Intense precipitation (55 mm/hr) detected. Atmospheric pressure dropped to 993 hPa.",
            "risk_score": 45,
            "risk_level": "MODERATE",
            "rainfall_mm": 110.0,
            "flood_prob": 0.38,
            "active_alerts": active_counts["alerts"],
            "active_sos": active_counts["sos"],
            "active_incidents": active_counts["incidents"],
            "metrics": {
                "rainfall_1h": 55.0,
                "rainfall_24h": 110.0,
                "pressure": 993.0,
                "humidity": 95.0,
                "wind_speed": 48.0
            },
            "database_changes": {
                "weather_observation_id": heavy_obs.id,
                "table": "weather_observations",
                "location": heavy_obs.location,
                "rainfall_1h": 55.0,
                "rainfall_24h": 110.0,
                "pressure": 993.0
            },
            "simulation_complete": False
        })

    # -------------------------------------------------------------------------
    # STEP 3 — AI ANALYSIS
    # -------------------------------------------------------------------------
    elif next_step == 3:
        # Execute actual trained scikit-learn models from Priority 4
        rain_pred = prediction_service.predict_rainfall(db, {
            "location": "[SIMULATION] Central Metro Basin",
            "historical_rainfall_24h": 110.0,
            "rainfall_1h": 55.0,
            "humidity": 95.0,
            "temperature": 23.0,
            "pressure": 993.0,
            "wind_speed": 48.0
        })

        flood_pred = prediction_service.predict_flood(db, {
            "location": "[SIMULATION] Central Metro Basin",
            "rainfall_intensity_mm_h": 55.0,
            "cumulative_rainfall_24h": 110.0,
            "soil_moisture_pct": 88.0,
            "river_discharge_m3_s": 420.0,
            "drainage_capacity_pct": 35.0,
            "elevation_m": 12.0,
            "slope_degrees": 1.5,
            "vegetation_cover_pct": 20.0,
            "urban_density_pct": 75.0,
            "proximity_to_water_m": 80.0,
            "distance_to_drain_m": 45.0
        })

        # Query the newly inserted prediction records
        latest_rain_db = db.query(RainfallPrediction).filter(
            RainfallPrediction.location.like("%[SIMULATION]%")
        ).order_by(RainfallPrediction.id.desc()).first()

        latest_flood_db = db.query(FloodPrediction).filter(
            FloodPrediction.location.like("%[SIMULATION]%")
        ).order_by(FloodPrediction.id.desc()).first()

        rain_id = latest_rain_db.id if latest_rain_db else 0
        flood_id = latest_flood_db.id if latest_flood_db else 0
        sim_state["simulated_record_ids"]["rainfall_prediction_id"] = rain_id
        sim_state["simulated_record_ids"]["flood_prediction_id"] = flood_id

        # Update risk score to ~68 (HIGH)
        zones = db.query(RiskZone).all()
        for z in zones:
            z.risk_score = 68
            z.risk_level = "HIGH"
            z.updated_at = datetime.now(timezone.utc)
        db.commit()

        active_counts = _get_active_counts(db)
        sim_state.update({
            "stage": "AI_ANALYSIS",
            "title": "AI Risk & Inundation Analysis",
            "description": "AI prediction models evaluated hydrological features. Flash flood probability elevated to high.",
            "risk_score": 68,
            "risk_level": "HIGH",
            "rainfall_mm": float(rain_pred.get("predicted_rainfall_mm", 114.8)),
            "flood_prob": float(flood_pred.get("flood_probability", 0.72)),
            "active_alerts": active_counts["alerts"],
            "active_sos": active_counts["sos"],
            "active_incidents": active_counts["incidents"],
            "metrics": {
                "rainfall_prediction_mm": rain_pred.get("predicted_rainfall_mm", 114.8),
                "confidence": rain_pred.get("confidence", 0.88),
                "flood_probability": flood_pred.get("flood_probability", 0.72),
                "estimated_water_depth_m": flood_pred.get("estimated_water_depth_m", 0.95),
                "model_name": rain_pred.get("model_name", "RandomForest"),
                "model_version": rain_pred.get("model_version", "v1.0-scikit-learn")
            },
            "database_changes": {
                "rainfall_prediction_id": rain_id,
                "flood_prediction_id": flood_id,
                "tables": ["rainfall_predictions", "flood_predictions"]
            },
            "simulation_complete": False
        })

    # -------------------------------------------------------------------------
    # STEP 4 — FLOOD RISK INCREASE
    # -------------------------------------------------------------------------
    elif next_step == 4:
        zones = db.query(RiskZone).all()
        previous_scores = [z.risk_score for z in zones]
        for z in zones:
            z.risk_score = 72
            z.risk_level = "HIGH"
            z.updated_at = datetime.now(timezone.utc)
        db.commit()

        active_counts = _get_active_counts(db)
        sim_state.update({
            "stage": "FLOOD_RISK_INCREASE",
            "title": "Flood Risk Escalation",
            "description": "Runoff saturation and river discharge elevated watershed composite risk to HIGH.",
            "risk_score": 72,
            "risk_level": "HIGH",
            "rainfall_mm": 135.0,
            "flood_prob": 0.82,
            "active_alerts": active_counts["alerts"],
            "active_sos": active_counts["sos"],
            "active_incidents": active_counts["incidents"],
            "metrics": {
                "risk_score": 72,
                "risk_level": "HIGH",
                "soil_moisture_pct": 92.0,
                "drainage_saturation_pct": 85.0
            },
            "database_changes": {
                "risk_zones_updated": [z.id for z in zones],
                "previous_scores": previous_scores,
                "new_scores": 72,
                "risk_level": "HIGH",
                "table": "risk_zones"
            },
            "simulation_complete": False
        })

    # -------------------------------------------------------------------------
    # STEP 5 — CRITICAL RISK
    # -------------------------------------------------------------------------
    elif next_step == 5:
        zones = db.query(RiskZone).all()
        previous_scores = [z.risk_score for z in zones]
        for z in zones:
            z.risk_score = 90
            z.risk_level = "CRITICAL"
            z.updated_at = datetime.now(timezone.utc)
        db.commit()

        active_counts = _get_active_counts(db)
        sim_state.update({
            "stage": "CRITICAL_RISK",
            "title": "Critical Flood Threshold Exceeded",
            "description": "Water depth exceeds levee capacity. Riverside lowland sectors elevated to CRITICAL danger.",
            "risk_score": 90,
            "risk_level": "CRITICAL",
            "rainfall_mm": 165.0,
            "flood_prob": 0.94,
            "active_alerts": active_counts["alerts"],
            "active_sos": active_counts["sos"],
            "active_incidents": active_counts["incidents"],
            "metrics": {
                "risk_score": 90,
                "risk_level": "CRITICAL",
                "inundation_depth_m": 1.65,
                "affected_zone_km2": 48.0
            },
            "database_changes": {
                "risk_zones_updated": [z.id for z in zones],
                "previous_scores": previous_scores,
                "new_scores": 90,
                "risk_level": "CRITICAL",
                "table": "risk_zones"
            },
            "simulation_complete": False
        })

    # -------------------------------------------------------------------------
    # STEP 6 — ALERT
    # -------------------------------------------------------------------------
    elif next_step == 6:
        alert = alert_service.create_alert(
            db,
            AlertCreate(
                title="[SIMULATION] CRITICAL FLOOD WARNING",
                message="Severe river overflow and urban inundation in progress. Risk score 90/100. Emergency command mandates immediate high-ground evacuation.",
                alert_type="FLOOD",
                severity="CRITICAL",
                target_area="Downtown Basin & Riverside Lowlands",
                expires_in_hours=6
            )
        )
        sim_state["simulated_record_ids"]["alert_id"] = alert.id

        active_counts = _get_active_counts(db)
        sim_state.update({
            "stage": "ALERT",
            "title": "Emergency Alert Broadcast",
            "description": "CRITICAL flood evacuation warning broadcasted to all citizens and field units.",
            "risk_score": 90,
            "risk_level": "CRITICAL",
            "rainfall_mm": 165.0,
            "flood_prob": 0.94,
            "active_alerts": active_counts["alerts"],
            "active_sos": active_counts["sos"],
            "active_incidents": active_counts["incidents"],
            "metrics": {
                "active_alerts": active_counts["alerts"],
                "alert_severity": "CRITICAL",
                "broadcast_radius_km": 15.0
            },
            "database_changes": {
                "alert_id": alert.id,
                "title": alert.title,
                "severity": alert.severity,
                "target_area": alert.target_area,
                "status": alert.status,
                "table": "alerts"
            },
            "simulation_complete": False
        })

    # -------------------------------------------------------------------------
    # STEP 7 — SOS / INCIDENT
    # -------------------------------------------------------------------------
    elif next_step == 7:
        sos = sos_service.create_sos(
            db,
            SOSCreate(
                latitude=13.0827,
                longitude=80.2707,
                message="[SIMULATION] Water entered my house and an elderly person is trapped.",
                severity="CRITICAL"
            ),
            auto_assign=False
        )
        sim_state["simulated_record_ids"]["sos_id"] = sos.id

        inc = db.query(Incident).filter(Incident.sos_id == sos.id).first()
        inc_id = inc.id if inc else 0
        inc_type = inc.incident_type if inc else "FLOOD_TRAPPED_PERSON"
        inc_severity = inc.severity if inc else "CRITICAL"
        inc_priority = inc.priority_score if inc else 95
        sim_state["simulated_record_ids"]["incident_id"] = inc_id

        active_counts = _get_active_counts(db)
        sim_state.update({
            "stage": "SOS_INCIDENT",
            "title": "Citizen SOS & AI Incident Triage",
            "description": "Citizen trapped by floodwaters submitted emergency SOS. AI triaged incident with Priority 95.",
            "risk_score": 95,
            "risk_level": "CRITICAL",
            "rainfall_mm": 180.0,
            "flood_prob": 0.98,
            "active_alerts": active_counts["alerts"],
            "active_sos": active_counts["sos"],
            "active_incidents": active_counts["incidents"],
            "metrics": {
                "sos_id": sos.id,
                "incident_id": inc_id,
                "incident_type": inc_type,
                "severity": inc_severity,
                "priority_score": inc_priority,
                "status": "PENDING"
            },
            "database_changes": {
                "sos_id": sos.id,
                "incident_id": inc_id,
                "incident_type": inc_type,
                "severity": inc_severity,
                "priority_score": inc_priority,
                "status": "PENDING",
                "tables": ["sos_reports", "incidents"]
            },
            "simulation_complete": False
        })

    # -------------------------------------------------------------------------
    # STEP 8 — AI RESCUE RECOMMENDATION -> OPERATOR CONFIRMATION -> DISPATCH
    # -------------------------------------------------------------------------
    elif next_step == 8:
        inc_id = sim_state["simulated_record_ids"].get("incident_id")
        if not inc_id:
            inc = db.query(Incident).filter(Incident.title.like("%[SIMULATION]%")).order_by(Incident.id.desc()).first()
            inc_id = inc.id if inc else 1

        # 1. AI Recommendation Step (Read-only multi-candidate evaluation)
        rec_result = rescue_intelligence_service.get_recommendations(db, inc_id)
        if rec_result.is_no_team_available or not rec_result.primary_candidate:
            team = db.query(RescueTeam).filter(RescueTeam.status == "AVAILABLE").first()
            if not team:
                team = db.query(RescueTeam).first()
            selected_team_id = team.id if team else 1
            recommended_team_id = selected_team_id
            team_name = team.name if team else "NDRF Alpha Coastal"
            dist_km = 2.5
        else:
            selected_team_id = rec_result.primary_candidate.team_id
            recommended_team_id = rec_result.primary_candidate.team_id
            team_name = rec_result.primary_candidate.team_name
            dist_km = rec_result.primary_candidate.distance_km

        # 2. Operator Confirmation Simulation Step (Simulated Human-in-the-Loop)
        operator_user = db.query(User).filter(User.role.in_([UserRole.OPERATOR, UserRole.ADMIN])).first()
        if not operator_user:
            operator_user = User(
                id=None,
                name="Simulation Duty Operator",
                email="sim_operator@disasterguard.gov",
                role=UserRole.OPERATOR
            )

        confirm_req = RescueDispatchConfirmRequest(
            incident_id=inc_id,
            rescue_team_id=selected_team_id,
            recommended_team_id=recommended_team_id,
            operator_confirmed=True,
            notes="[SIMULATION] Simulated Duty Operator confirmed tactical dispatch after reviewing AI recommendation.",
            is_override=False
        )

        # 3. Official Dispatch via RescueIntelligenceService (Atomic Transaction + Audit Log + Domain Event)
        dispatch_res = rescue_intelligence_service.dispatch_team(db, confirm_req, operator_user)
        assignment_id = dispatch_res.assignment_id

        assign = db.query(RescueAssignment).filter(RescueAssignment.id == assignment_id).first()
        if assign and not assign.notes.startswith("[SIMULATION]"):
            assign.notes = f"[SIMULATION] {assign.notes or ''}"
            db.commit()

        audit = db.query(RescueDispatchAuditLog).filter(RescueDispatchAuditLog.incident_id == inc_id).first()
        if audit and audit.details and isinstance(audit.details, dict):
            details_copy = dict(audit.details)
            details_copy["simulation"] = True
            audit.details = details_copy
            db.commit()

        active_counts = _get_active_counts(db)
        sim_state.update({
            "stage": "RESCUE_RECOMMENDATION",
            "title": "AI Recommendation & Operator-Confirmed Dispatch",
            "description": f"AI recommended '{team_name}'. Duty Operator reviewed candidates and confirmed tactical dispatch.",
            "risk_score": 95,
            "risk_level": "CRITICAL",
            "rainfall_mm": 180.0,
            "flood_prob": 0.98,
            "active_alerts": active_counts["alerts"],
            "active_sos": active_counts["sos"],
            "active_incidents": active_counts["incidents"],
            "recommended_rescue_team": selected_team_id,
            "metrics": {
                "rescue_team_id": selected_team_id,
                "rescue_team_name": team_name,
                "distance_km": dist_km,
                "estimated_response_time": int(dist_km * 3.5 + 4),
                "assignment_id": assignment_id,
                "assignment_status": "DISPATCHED",
                "recommended_hospital": "St. Jude Emergency Medical Center",
                "recommended_shelter": "Central Command Stadium Shelter"
            },
            "database_changes": {
                "assignment_id": assignment_id,
                "rescue_team_id": selected_team_id,
                "rescue_team_name": team_name,
                "distance_km": dist_km,
                "assignment_status": "DISPATCHED",
                "table": "rescue_assignments"
            },
            "simulation_complete": True
        })

    try:
        ws_manager.broadcast_event(
            DomainEvent(
                event=EventType.SIMULATION_STAGE_CHANGED,
                timestamp=datetime.now(timezone.utc).isoformat(),
                entity_type="simulation",
                severity=sim_state.get("risk_level", "LOW"),
                data=dict(sim_state)
            )
        )
    except Exception as e:
        pass

    return sim_state


@router.post("/reset")
def reset_simulation(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Reset simulation engine to initial state.
    Removes all [SIMULATION] records from PostgreSQL, restores risk zones and rescue teams to baseline,
    and resets simulation state to Step 0.
    """
    cleaned_counts = _clean_simulation_records(db)
    active_counts = _get_active_counts(db)

    sim_state.update({
        "is_active": False,
        "simulation_active": False,
        "simulation_complete": False,
        "step": 0,
        "total_steps": 8,
        "stage": "NORMAL",
        "title": "Simulation Engine Ready",
        "description": "Simulation records cleaned and baseline operational state restored in PostgreSQL.",
        "risk_score": 18,
        "risk_level": "LOW",
        "rainfall_mm": 12.5,
        "flood_prob": 0.05,
        "active_alerts": active_counts["alerts"],
        "active_sos": active_counts["sos"],
        "active_incidents": active_counts["incidents"],
        "recommended_rescue_team": 0,
        "metrics": {},
        "database_changes": {
            "records_cleaned": cleaned_counts
        },
        "simulated_record_ids": {
            "weather_observation_id": None,
            "rainfall_prediction_id": None,
            "flood_prediction_id": None,
            "alert_id": None,
            "sos_id": None,
            "incident_id": None,
            "rescue_assignment_id": None,
        }
    })

    try:
        ws_manager.broadcast_event(
            DomainEvent(
                event=EventType.SIMULATION_STAGE_CHANGED,
                timestamp=datetime.now(timezone.utc).isoformat(),
                entity_type="simulation",
                severity="LOW",
                data=dict(sim_state)
            )
        )
    except Exception as e:
        pass

    return sim_state


@router.get("/status")
@router.get("/state")
def get_simulation_status() -> Dict[str, Any]:
    """Retrieve current simulation engine state."""
    return sim_state


# ---------------------------------------------------------
# Phase 6: 17-Stage Command-Centre Coordination Simulation
# ---------------------------------------------------------
from app.services.phase6_simulation import phase6_simulation_service
from pydantic import BaseModel

class Phase6StepRequest(BaseModel):
    step: Optional[int] = None


@router.post("/phase6/start")
def start_phase6_simulation(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Start the 17-stage Phase 6 Command-Centre real-time coordination simulation."""
    return phase6_simulation_service.start(db)


@router.post("/phase6/step")
def step_phase6_simulation(payload: Optional[Phase6StepRequest] = None, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Advance or set specific step in 17-stage Phase 6 simulation."""
    target_step = payload.step if payload else None
    return phase6_simulation_service.step(db, target_step=target_step)


@router.post("/phase6/reset")
def reset_phase6_simulation(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Reset Phase 6 simulation state and clean all [SIMULATION] records from PostgreSQL."""
    return phase6_simulation_service.reset(db)


@router.get("/phase6/state")
def get_phase6_simulation_state() -> Dict[str, Any]:
    """Retrieve current Phase 6 simulation state, active step, and provenance details."""
    return phase6_simulation_service.get_state()

