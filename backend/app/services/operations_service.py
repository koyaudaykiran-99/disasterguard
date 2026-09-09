"""
AI-DisasterGuard — Disaster Operations Intelligence Service
Phase 5.5: Multi-Incident Operations, Resource Contention, Bottlenecks, and Response Plans
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models.incident import Incident
from app.database.models.sos import SOSReport
from app.database.models.sos_triage import SOSTriageResult
from app.database.models.rescue import RescueTeam, RescueAssignment, RescueDispatchAuditLog
from app.database.models.shelter import Shelter
from app.database.models.hospital import Hospital
from app.database.models.forecast import ForecastPrediction
from app.database.models.historical_flood import HistoricalFloodEvent
from app.database.models.operations import (
    OperationalRecommendation,
    ResourceContention,
    OperationalBottleneck,
    ResponsePlan,
)
from app.database.models.user import User, UserRole
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType

from ml.operations.incident_priority import calculate_incident_priority
from ml.operations.team_matching import match_rescue_teams
from ml.operations.shelter_matching import match_shelters
from ml.operations.hospital_matching import match_hospitals
from ml.operations.resource_optimizer import optimize_disaster_operations
from ml.operations.bottleneck import detect_operational_bottlenecks
from ml.operations.response_plan import generate_response_plan
from ml.operations.operational_metrics import calculate_operational_metrics
from ml.operations import OperationalStatus, OperationalPriorityLevel

logger = logging.getLogger("disasterguard.operations_service")


class OperationsService:
    @staticmethod
    def get_overview(db: Session) -> Dict[str, Any]:
        """Returns comprehensive operational overview metrics."""
        incidents = db.query(Incident).all()
        teams = db.query(RescueTeam).all()
        shelters = db.query(Shelter).all()
        hospitals = db.query(Hospital).all()
        contentions = db.query(ResourceContention).filter(ResourceContention.is_active == True).all()
        bottlenecks = db.query(OperationalBottleneck).filter(OperationalBottleneck.is_active == True).all()
        audit_logs = db.query(RescueDispatchAuditLog).all()

        metrics = calculate_operational_metrics(
            incidents=incidents,
            teams=teams,
            shelters=shelters,
            hospitals=hospitals,
            contentions=contentions,
            bottlenecks=bottlenecks,
            audit_logs=audit_logs,
        )

        return {
            "active_incidents_count": metrics["active_incidents"],
            "critical_incidents_count": metrics["critical_incidents"],
            "high_priority_incidents_count": metrics["high_priority_incidents"],
            "teams_available_count": metrics["teams_available"],
            "teams_busy_count": metrics["teams_busy"],
            "teams_en_route_count": metrics["teams_en_route"],
            "shelter_available_capacity": metrics["shelter_available_capacity"],
            "hospital_available_beds": metrics["hospital_available_beds"],
            "unassigned_incidents_count": metrics["unassigned_incidents"],
            "contentions_count": metrics["active_contentions_count"],
            "bottlenecks_count": metrics["active_bottlenecks_count"],
            "provenance": {
                "source": "POSTGRESQL_DB",
                "mode": "REAL_TIME_OBSERVATION"
            }
        }

    @staticmethod
    def get_prioritized_incidents(
        db: Session,
        status_filter: Optional[str] = None,
        sort_by: str = "priority",
    ) -> List[Dict[str, Any]]:
        """
        Ranks all active incidents using multi-factor operational priority scoring (0-100).
        Runs resource contention detection across active incidents.
        """
        query = db.query(Incident)
        if status_filter and status_filter.upper() != "ALL":
            query = query.filter(Incident.status == status_filter.upper())
        incidents = query.all()

        teams = db.query(RescueTeam).all()
        shelters = db.query(Shelter).all()
        hospitals = db.query(Hospital).all()

        # Build maps for triage, forecast, flood
        triage_map = {}
        for inc in incidents:
            if inc.sos_id:
                tr = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == inc.sos_id).first()
                if tr:
                    triage_map[inc.id] = tr

        # Run multi-incident coordination and contention detection
        optimization_result = optimize_disaster_operations(
            incidents=incidents,
            teams=teams,
            shelters=shelters,
            hospitals=hospitals,
            triage_map=triage_map,
        )

        # Sync active contentions to DB
        contentions = optimization_result["contentions"]
        now = datetime.now(timezone.utc)
        for c in contentions:
            existing = db.query(ResourceContention).filter(
                ResourceContention.resource_id == c["resource_id"],
                ResourceContention.is_active == True
            ).first()
            if not existing:
                rc = ResourceContention(
                    resource_id=c["resource_id"],
                    resource_name=c["resource_name"],
                    incident_ids_json=json.dumps(c["incident_ids"]),
                    preferred_incident_id=c["preferred_incident_id"],
                    severity=c["severity"],
                    description=c["description"],
                    alternatives_json=json.dumps(c.get("contending_incidents_detail", [])),
                    is_active=True,
                    detected_at=now,
                )
                db.add(rc)
        db.commit()

        # Build prioritized incident response list
        results = []
        for item in optimization_result["prioritized_incidents"]:
            inc = item["incident"]
            p_info = item["priority_info"]
            rec_team = item["team_info"]["recommended_team"]
            contention = item["contention"]

            is_contended = bool(contention and contention.get("is_contended"))
            contention_note = None
            if is_contended:
                if contention.get("status") == "PRIMARY_CLAIM":
                    contention_note = contention.get("note")
                else:
                    contention_note = contention.get("explanation")

            created_str = inc.created_at.isoformat() if inc.created_at else None

            results.append({
                "id": inc.id,
                "title": inc.title,
                "description": inc.description,
                "severity": inc.severity or "LOW",
                "status": inc.status or "PENDING",
                "latitude": float(inc.latitude or 0.0),
                "longitude": float(inc.longitude or 0.0),
                "people_at_risk": p_info["people_at_risk"],
                "priority_score": p_info["priority_score"],
                "priority_level": p_info["priority_level"],
                "created_at": created_str,
                "is_trapped": p_info["is_trapped"],
                "is_medical": p_info["is_medical"],
                "recommended_team_id": rec_team["id"] if rec_team else None,
                "recommended_team_name": rec_team["name"] if rec_team else None,
                "is_contended": is_contended,
                "contention_note": contention_note,
            })

        # Apply sorting
        if sort_by == "age":
            results.sort(key=lambda x: x["created_at"] or "", reverse=False)
        elif sort_by == "people":
            results.sort(key=lambda x: x["people_at_risk"], reverse=True)
        else: # priority
            results.sort(key=lambda x: x["priority_score"], reverse=True)

        return results

    @staticmethod
    def get_incident_priority(db: Session, incident_id: int) -> Dict[str, Any]:
        """Calculates and returns explainable priority score for a specific incident."""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident #{incident_id} not found.")

        triage = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == incident.sos_id).first() if incident.sos_id else None
        forecast = db.query(ForecastPrediction).order_by(desc(ForecastPrediction.id)).first()
        flood = db.query(HistoricalFloodEvent).order_by(desc(HistoricalFloodEvent.id)).first()

        p_info = calculate_incident_priority(incident, triage, forecast, flood)
        p_info["incident_id"] = incident_id
        return p_info

    @staticmethod
    def get_candidate_resources(db: Session, incident_id: int) -> Dict[str, Any]:
        """Evaluates rescue teams, shelters, and hospitals for a specific incident."""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident #{incident_id} not found.")

        teams = db.query(RescueTeam).all()
        shelters = db.query(Shelter).all()
        hospitals = db.query(Hospital).all()

        p_info = OperationsService.get_incident_priority(db, incident_id)

        team_info = match_rescue_teams(incident, teams, p_info)
        shelter_info = match_shelters(incident, shelters)
        hospital_info = match_hospitals(incident, hospitals, p_info)

        return {
            "incident_id": incident_id,
            "priority": p_info,
            "teams": team_info,
            "shelters": shelter_info,
            "hospitals": hospital_info,
        }

    @staticmethod
    def get_response_plan(db: Session, incident_id: int) -> Dict[str, Any]:
        """
        Generates or retrieves the unified explainable Response Plan for an incident.
        INVIOLATE: human_confirmation_required is always True.
        """
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident #{incident_id} not found.")

        # Check existing response plan in DB
        db_plan = db.query(ResponsePlan).filter(ResponsePlan.incident_id == incident_id).first()

        teams = db.query(RescueTeam).all()
        shelters = db.query(Shelter).all()
        hospitals = db.query(Hospital).all()

        p_info = OperationsService.get_incident_priority(db, incident_id)
        team_info = match_rescue_teams(incident, teams, p_info)
        shelter_info = match_shelters(incident, shelters)
        hospital_info = match_hospitals(incident, hospitals, p_info)

        # Check contention
        contention_info = None
        if team_info["recommended_team"]:
            rec_id = team_info["recommended_team"]["id"]
            active_c = db.query(ResourceContention).filter(
                ResourceContention.resource_id == rec_id,
                ResourceContention.is_active == True
            ).first()
            if active_c:
                contention_info = {
                    "is_contended": True,
                    "severity": active_c.severity,
                    "description": active_c.description,
                }

        plan_dict = generate_response_plan(
            incident=incident,
            priority_info=p_info,
            team_matching=team_info,
            shelter_matching=shelter_info,
            hospital_matching=hospital_info,
            contention_info=contention_info,
        )

        # Persist or update response_plan in DB
        now = datetime.now(timezone.utc)
        if not db_plan:
            db_plan = ResponsePlan(
                incident_id=incident_id,
                priority=plan_dict["priority"],
                priority_score=plan_dict["priority_score"],
                recommended_team_id=plan_dict["recommended_team"]["id"] if plan_dict["recommended_team"] else None,
                recommended_team_name=plan_dict["recommended_team"]["name"] if plan_dict["recommended_team"] else None,
                alternative_teams_json=json.dumps(plan_dict["alternative_teams"]),
                recommended_shelter_id=plan_dict["recommended_shelter"]["id"] if plan_dict["recommended_shelter"] else None,
                recommended_shelter_name=plan_dict["recommended_shelter"]["name"] if plan_dict["recommended_shelter"] else None,
                recommended_hospital_id=plan_dict["recommended_hospital"]["id"] if plan_dict["recommended_hospital"] else None,
                recommended_hospital_name=plan_dict["recommended_hospital"]["name"] if plan_dict["recommended_hospital"] else None,
                reasons_json=json.dumps(plan_dict["reasons"]),
                warnings_json=json.dumps(plan_dict["warnings"]),
                confidence=plan_dict["confidence"],
                data_provenance_json=json.dumps(plan_dict["data_provenance"]),
                human_confirmation_required=True,
                status=OperationalStatus.RECOMMENDED.value,
                created_at=now,
                updated_at=now,
            )
            db.add(db_plan)
        else:
            # Update fields if not overridden/confirmed
            if db_plan.status == OperationalStatus.RECOMMENDED.value:
                db_plan.priority = plan_dict["priority"]
                db_plan.priority_score = plan_dict["priority_score"]
                db_plan.recommended_team_id = plan_dict["recommended_team"]["id"] if plan_dict["recommended_team"] else None
                db_plan.recommended_team_name = plan_dict["recommended_team"]["name"] if plan_dict["recommended_team"] else None
                db_plan.alternative_teams_json = json.dumps(plan_dict["alternative_teams"])
                db_plan.recommended_shelter_id = plan_dict["recommended_shelter"]["id"] if plan_dict["recommended_shelter"] else None
                db_plan.recommended_shelter_name = plan_dict["recommended_shelter"]["name"] if plan_dict["recommended_shelter"] else None
                db_plan.recommended_hospital_id = plan_dict["recommended_hospital"]["id"] if plan_dict["recommended_hospital"] else None
                db_plan.recommended_hospital_name = plan_dict["recommended_hospital"]["name"] if plan_dict["recommended_hospital"] else None
                db_plan.reasons_json = json.dumps(plan_dict["reasons"])
                db_plan.warnings_json = json.dumps(plan_dict["warnings"])
                db_plan.confidence = plan_dict["confidence"]
                db_plan.updated_at = now

        db.commit()
        db.refresh(db_plan)

        plan_dict["id"] = db_plan.id
        plan_dict["status"] = db_plan.status
        plan_dict["override_reason"] = db_plan.override_reason
        plan_dict["reviewed_by"] = db_plan.reviewed_by
        plan_dict["reviewed_at"] = db_plan.reviewed_at.isoformat() if db_plan.reviewed_at else None

        return plan_dict

    @staticmethod
    def override_response_plan(
        db: Session,
        incident_id: int,
        operator: User,
        selected_team_id: int,
        override_reason: str,
    ) -> Dict[str, Any]:
        """
        Records an explicit human operator override for the recommended rescue team.
        Does NOT dispatch autonomously; updates plan status to OVERRIDDEN with audit record.
        """
        db_plan = db.query(ResponsePlan).filter(ResponsePlan.incident_id == incident_id).first()
        if not db_plan:
            # Generate plan first
            OperationsService.get_response_plan(db, incident_id)
            db_plan = db.query(ResponsePlan).filter(ResponsePlan.incident_id == incident_id).first()

        selected_team = db.query(RescueTeam).filter(RescueTeam.id == selected_team_id).first()
        if not selected_team:
            raise ValueError(f"Selected rescue team #{selected_team_id} not found.")

        now = datetime.now(timezone.utc)
        original_team_id = db_plan.recommended_team_id
        original_team_name = db_plan.recommended_team_name

        db_plan.recommended_team_id = selected_team.id
        db_plan.recommended_team_name = selected_team.name
        db_plan.status = OperationalStatus.OVERRIDDEN.value
        db_plan.override_reason = override_reason
        db_plan.reviewed_by = operator.email
        db_plan.reviewed_at = now
        db_plan.updated_at = now

        # Add audit record
        audit = RescueDispatchAuditLog(
            operator_id=operator.id,
            operator_name=operator.name or operator.email or "Operator",
            incident_id=incident_id,
            rescue_team_id=selected_team.id,
            action="RESCUE_DISPATCH_OVERRIDE",
            is_override=True,
            override_reason=override_reason,
            details={"original_team_id": original_team_id, "original_team_name": original_team_name},
            timestamp=now,
        )
        db.add(audit)
        db.commit()

        # Emit WebSocket event
        try:
            domain_event = DomainEvent(
                event=EventType.RESPONSE_PLAN_UPDATED,
                entity_id=incident_id,
                entity_type="RESPONSE_PLAN",
                data={
                    "incident_id": incident_id,
                    "status": "OVERRIDDEN",
                    "selected_team_id": selected_team.id,
                    "selected_team_name": selected_team.name,
                    "operator": operator.email,
                    "reason": override_reason,
                }
            )
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(ws_manager.broadcast_event(domain_event))
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Failed to broadcast WebSocket event: {e}")

        return OperationsService.get_response_plan(db, incident_id)

    @staticmethod
    def reject_response_plan(
        db: Session,
        incident_id: int,
        operator: User,
        rejection_reason: str,
    ) -> Dict[str, Any]:
        """Records operator rejection of recommended response plan."""
        db_plan = db.query(ResponsePlan).filter(ResponsePlan.incident_id == incident_id).first()
        if not db_plan:
            OperationsService.get_response_plan(db, incident_id)
            db_plan = db.query(ResponsePlan).filter(ResponsePlan.incident_id == incident_id).first()

        now = datetime.now(timezone.utc)
        db_plan.status = OperationalStatus.REJECTED.value
        db_plan.override_reason = f"REJECTED: {rejection_reason}"
        db_plan.reviewed_by = operator.email
        db_plan.reviewed_at = now
        db_plan.updated_at = now

        audit = RescueDispatchAuditLog(
            operator_id=operator.id,
            operator_name=operator.name or operator.email or "Operator",
            incident_id=incident_id,
            rescue_team_id=db_plan.recommended_team_id or 1,
            action="OPERATOR_REJECTED",
            is_override=False,
            override_reason=rejection_reason,
            details={"status": "REJECTED"},
            timestamp=now,
        )
        db.add(audit)
        db.commit()


        return OperationsService.get_response_plan(db, incident_id)

    @staticmethod
    def get_contentions(db: Session, is_active: bool = True) -> List[Dict[str, Any]]:
        """Returns detected resource contentions."""
        contentions = db.query(ResourceContention).filter(ResourceContention.is_active == is_active).all()
        results = []
        for c in contentions:
            try:
                inc_ids = json.loads(c.incident_ids_json)
            except Exception:
                inc_ids = []
            try:
                alts = json.loads(c.alternatives_json) if c.alternatives_json else None
            except Exception:
                alts = None

            results.append({
                "id": c.id,
                "resource_id": c.resource_id,
                "resource_name": c.resource_name,
                "incident_ids": inc_ids,
                "preferred_incident_id": c.preferred_incident_id,
                "severity": c.severity,
                "description": c.description,
                "alternatives": alts,
                "is_active": c.is_active,
                "detected_at": c.detected_at.isoformat() if c.detected_at else None,
            })
        return results

    @staticmethod
    def get_bottlenecks(db: Session, is_active: bool = True) -> List[Dict[str, Any]]:
        """Scans for and returns operational bottlenecks."""
        incidents = db.query(Incident).all()
        teams = db.query(RescueTeam).all()
        shelters = db.query(Shelter).all()
        hospitals = db.query(Hospital).all()

        detected = detect_operational_bottlenecks(
            incidents=incidents,
            teams=teams,
            shelters=shelters,
            hospitals=hospitals,
            zone="District Operational Area",
        )

        now = datetime.now(timezone.utc)
        # Sync to DB
        for b in detected:
            existing = db.query(OperationalBottleneck).filter(
                OperationalBottleneck.zone == b["zone"],
                OperationalBottleneck.bottleneck_type == b["bottleneck_type"],
                OperationalBottleneck.is_active == True
            ).first()
            if not existing:
                ob = OperationalBottleneck(
                    zone=b["zone"],
                    bottleneck_type=b["bottleneck_type"],
                    severity=b["severity"],
                    description=b["description"],
                    metrics_json=json.dumps(b.get("metrics", {})),
                    guidance=b.get("guidance"),
                    is_active=True,
                    detected_at=now,
                )
                db.add(ob)
        db.commit()

        # Query all active from DB
        db_bottlenecks = db.query(OperationalBottleneck).filter(OperationalBottleneck.is_active == is_active).all()
        results = []
        for b in db_bottlenecks:
            try:
                metrics = json.loads(b.metrics_json) if b.metrics_json else {}
            except Exception:
                metrics = {}
            results.append({
                "id": b.id,
                "zone": b.zone,
                "bottleneck_type": b.bottleneck_type,
                "severity": b.severity,
                "description": b.description,
                "metrics": metrics,
                "guidance": b.guidance,
                "is_active": b.is_active,
                "detected_at": b.detected_at.isoformat() if b.detected_at else None,
            })
        return results

    @staticmethod
    def get_capacity(db: Session) -> Dict[str, Any]:
        """Provides facility capacity breakdown with transparent provenance."""
        teams = db.query(RescueTeam).all()
        shelters = db.query(Shelter).all()
        hospitals = db.query(Hospital).all()

        available_teams = sum(1 for t in teams if str(t.status).upper() == "AVAILABLE")
        busy_teams = sum(1 for t in teams if str(t.status).upper() in ["BUSY", "EN_ROUTE", "ON_SCENE", "DISPATCHED"])

        total_shelter_cap = sum(s.capacity or 0 for s in shelters)
        total_shelter_occ = sum(s.current_occupancy or 0 for s in shelters)
        available_shelter_cap = max(0, total_shelter_cap - total_shelter_occ)

        total_beds = sum(h.available_beds or 0 for h in hospitals)
        saturated_hosp = sum(1 for h in hospitals if str(h.emergency_capacity).upper() == "FULL" or (h.available_beds or 0) == 0)

        return {
            "rescue_teams": {
                "total": len(teams),
                "available": available_teams,
                "busy": busy_teams,
                "utilization_pct": round((busy_teams / max(1, len(teams))) * 100.0, 1),
            },
            "shelters": {
                "total_facilities": len(shelters),
                "total_capacity": total_shelter_cap,
                "current_occupancy": total_shelter_occ,
                "available_capacity": available_shelter_cap,
                "occupancy_pct": round((total_shelter_occ / max(1, total_shelter_cap)) * 100.0, 1) if total_shelter_cap > 0 else 0.0,
            },
            "hospitals": {
                "total_facilities": len(hospitals),
                "available_beds": total_beds,
                "saturated_count": saturated_hosp,
            },
            "provenance": {
                "rescue_teams": "REAL",
                "shelters": "MOCK",
                "hospitals": "MOCK",
            }
        }

    @staticmethod
    def get_coverage(db: Session) -> Dict[str, Any]:
        """Calculates approximate regional coverage."""
        teams = db.query(RescueTeam).all()
        incidents = db.query(Incident).filter(Incident.status.in_(["PENDING", "UNASSIGNED"])).all()

        available_teams = [t for t in teams if str(t.status).upper() == "AVAILABLE"]

        # Honest coverage assessment
        if len(available_teams) >= len(incidents) and len(available_teams) >= 3:
            coverage_status = "GOOD"
        elif len(available_teams) >= 1:
            coverage_status = "MODERATE"
        else:
            coverage_status = "LOW"

        zones = [
            {
                "zone": "District Operational Area",
                "critical_incidents": sum(1 for i in incidents if str(i.severity).upper() == "CRITICAL"),
                "high_incidents": sum(1 for i in incidents if str(i.severity).upper() == "HIGH"),
                "suitable_teams": len(available_teams),
                "coverage": coverage_status,
            }
        ]

        return {
            "zones": zones,
            "overall_coverage": coverage_status,
            "gap_count": max(0, len(incidents) - len(available_teams)),
            "disclaimer": "Resource coverage is an approximation based on straight-line geographic proximity; not a guarantee of road access.",
        }

    @staticmethod
    def get_analytics(db: Session) -> Dict[str, Any]:
        """Calculates system operational analytics strictly from stored database entities."""
        incidents = db.query(Incident).all()
        teams = db.query(RescueTeam).all()
        shelters = db.query(Shelter).all()
        hospitals = db.query(Hospital).all()
        contentions = db.query(ResourceContention).all()
        bottlenecks = db.query(OperationalBottleneck).all()
        audit_logs = db.query(RescueDispatchAuditLog).all()

        return calculate_operational_metrics(
            incidents=incidents,
            teams=teams,
            shelters=shelters,
            hospitals=hospitals,
            contentions=contentions,
            bottlenecks=bottlenecks,
            audit_logs=audit_logs,
        )
