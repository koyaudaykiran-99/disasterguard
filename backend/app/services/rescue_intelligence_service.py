import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models.rescue import RescueTeam, RescueAssignment, RescueDispatchAuditLog
from app.database.models.incident import Incident
from app.database.models.sos import SOSReport
from app.database.models.sos_triage import SOSTriageResult
from app.database.models.user import User, UserRole
from app.gis.spatial_queries import haversine_distance_km
from app.schemas.rescue import (
    RescueCandidate,
    RescueRecommendationResult,
    RescueDispatchConfirmRequest,
    RescueDispatchResponse
)
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType

logger = logging.getLogger("disasterguard.rescue_intelligence")

# Required capabilities map per incident taxonomy
INCIDENT_CAPABILITY_MAP: Dict[str, List[str]] = {
    "FLOODING": ["FLOOD_RESCUE", "BOAT_RESCUE"],
    "TRAPPED_PERSON": ["FLOOD_RESCUE", "BOAT_RESCUE", "SEARCH_AND_RESCUE"],
    "MEDICAL_EMERGENCY": ["MEDICAL", "FIRST_AID", "TRAUMA_CARE"],
    "EVACUATION_REQUIRED": ["EVACUATION", "HIGH_WATER", "URBAN_RESCUE"],
    "INFRASTRUCTURE_DAMAGE": ["URBAN_RESCUE", "HEAVY_EQUIPMENT"],
    "LANDSLIDE": ["SEARCH_AND_RESCUE", "URBAN_RESCUE"],
    "ROAD_BLOCKAGE": ["HIGH_WATER", "URBAN_RESCUE"],
    "POWER_OUTAGE": ["FIRST_AID", "EVACUATION"],
    "MISSING_PERSON": ["SEARCH_AND_RESCUE", "WINCH_EXTRACTION"],
    "WEATHER_THREAT": ["FLOOD_RESCUE", "EVACUATION"],
    "OTHER": ["FIRST_AID", "FLOOD_RESCUE"],
}

class RescueIntelligenceService:
    @staticmethod
    def get_recommendations(db: Session, incident_id: int) -> RescueRecommendationResult:
        """
        Evaluate and rank all candidate rescue teams for an incident.
        Strictly advisory: DOES NOT autonomously dispatch.
        """
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident #{incident_id} not found.")

        sos = db.query(SOSReport).filter(SOSReport.id == incident.sos_id).first() if incident.sos_id else None
        triage = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == incident.sos_id).first() if incident.sos_id else None

        inc_type = (triage.incident_type if triage else incident.incident_type or "FLOODING").upper()
        severity = (incident.severity or "HIGH").upper()
        p_score = triage.priority_score if triage else incident.priority_score or 75
        people_count = triage.people_at_risk if triage else 1

        required_caps = set(INCIDENT_CAPABILITY_MAP.get(inc_type, ["FLOOD_RESCUE", "FIRST_AID"]))

        all_teams = db.query(RescueTeam).all()
        candidates: List[RescueCandidate] = []
        global_warnings: List[str] = [
            "Approx. geographic distance only (road network routing unavailable)"
        ]

        now = datetime.now(timezone.utc)

        for team in all_teams:
            # 1. Capabilities
            team_caps_list = [c.strip().upper() for c in (team.capabilities or "FLOOD_RESCUE,FIRST_AID").split(",") if c.strip()]
            team_caps_set = set(team_caps_list)

            # Include vehicle type in capability assessment
            v_type = (team.vehicle_type or "").upper()
            if "BOAT" in v_type:
                team_caps_set.add("BOAT_RESCUE")
                team_caps_set.add("FLOOD_RESCUE")
            if "HELICOPTER" in v_type:
                team_caps_set.add("WINCH_EXTRACTION")
                team_caps_set.add("SEARCH_AND_RESCUE")
            if "AMBULANCE" in v_type:
                team_caps_set.add("MEDICAL")
                team_caps_set.add("FIRST_AID")

            matched_caps = team_caps_set.intersection(required_caps)
            if len(matched_caps) == len(required_caps):
                cap_match_level = "EXACT"
                cap_score = 30
            elif len(matched_caps) > 0:
                cap_match_level = "HIGH" if len(matched_caps) >= len(required_caps) / 2 else "PARTIAL"
                cap_score = 20 if cap_match_level == "HIGH" else 10
            else:
                cap_match_level = "MINIMAL"
                cap_score = 0

            # 2. Distance
            dist_km = haversine_distance_km(incident.latitude, incident.longitude, team.latitude, team.longitude)
            if dist_km < 2.0:
                dist_score = 25
            elif dist_km < 5.0:
                dist_score = 20
            elif dist_km < 10.0:
                dist_score = 15
            elif dist_km < 20.0:
                dist_score = 10
            else:
                dist_score = 5

            eta_min = int(max(3, dist_km * 3.5 + 2))

            # 3. Availability
            t_status = (team.status or "AVAILABLE").upper()
            if t_status == "AVAILABLE":
                avail_score = 25
            elif t_status in ["BUSY", "EN_ROUTE", "DISPATCHED", "ON_SCENE"]:
                avail_score = -20
            else: # OFFLINE, UNAVAILABLE
                avail_score = -50

            # 4. Freshness
            is_stale = False
            team_updated = team.last_updated
            if team_updated:
                # Ensure timezone-aware
                if team_updated.tzinfo is None:
                    team_updated = team_updated.replace(tzinfo=timezone.utc)
                age_min = (now - team_updated).total_seconds() / 60.0
                if age_min > 15.0:
                    is_stale = True
                    fresh_score = -15
                else:
                    fresh_score = 5
            else:
                fresh_score = 0

            # 5. Capacity
            cap_limit = team.capacity or 10
            capacity_score = 5 if cap_limit >= people_count else 0

            # Total score (clamped 0-100)
            raw_score = 25 + avail_score + dist_score + cap_score + fresh_score + capacity_score
            final_score = int(max(0, min(100, raw_score)))

            # Reasons
            reasons: List[str] = []
            if t_status == "AVAILABLE":
                reasons.append("Team is currently AVAILABLE for immediate deployment")
            else:
                reasons.append(f"Team status is {t_status}")

            if cap_match_level in ["EXACT", "HIGH"]:
                reasons.append(f"Equipped with {', '.join(sorted(matched_caps))} matching {inc_type}")
            elif team.vehicle_type:
                reasons.append(f"Field vehicle ({team.vehicle_type.replace('_', ' ')}) ready for deployment")

            reasons.append(f"Geographic proximity: {dist_km} km (estimated response ~{eta_min} min)")

            if cap_limit >= people_count:
                reasons.append(f"Unit capacity ({cap_limit} personnel) adequate for {people_count} reported victim(s)")

            # Candidate warnings
            team_warnings: List[str] = []
            if is_stale:
                team_warnings.append(f"Team location updated {int(age_min)} min ago (potential stale GPS)")
            if t_status != "AVAILABLE":
                team_warnings.append(f"Team is currently {t_status}; dispatching requires operator override")
            if cap_match_level == "MINIMAL":
                team_warnings.append(f"Team lacks primary specialized capabilities for {inc_type}")

            candidates.append(RescueCandidate(
                team_id=team.id,
                team_name=team.name,
                score=final_score,
                distance_km=dist_km,
                distance_label="Approx. geographic distance",
                routing_limitations="Straight-line geographic distance. Actual road travel times may vary depending on flood inundation and road closures.",
                estimated_response_minutes=eta_min,
                capabilities=team_caps_list,
                vehicle_type=team.vehicle_type or "RESCUE_BOAT",
                equipment=team.equipment or "BASIC_FIRST_AID",
                status=t_status,
                capacity=cap_limit,
                is_stale=is_stale,
                is_stale_location=is_stale,
                last_updated=team_updated,
                reasons=reasons,
                warnings=team_warnings,
                is_primary=False,
                capability_match=cap_match_level
            ))

        # Sort candidates descending by score
        candidates.sort(key=lambda c: c.score, reverse=True)

        # Select primary candidate: highest-scoring available team within operational range (<= 100 km)
        primary_candidate = None
        for c in candidates:
            if c.status == "AVAILABLE" and c.distance_km <= 100.0:
                c.is_primary = True
                primary_candidate = c
                break

        result_status = "RECOMMENDATION_AVAILABLE"
        if not primary_candidate:
            result_status = "NO_SUITABLE_TEAM_FOUND"
            global_warnings.append("No active rescue teams available within operational jurisdiction (< 100 km)")

        is_none_avail = (primary_candidate is None) or (result_status == "NO_SUITABLE_TEAM_FOUND")
        return RescueRecommendationResult(
            incident_id=incident.id,
            sos_id=incident.sos_id,
            incident_type=inc_type,
            severity=severity,
            priority_score=p_score,
            primary_candidate=primary_candidate,
            primary_recommendation=primary_candidate,
            is_no_team_available=is_none_avail,
            candidates=candidates,
            warnings=global_warnings,
            status=result_status,
            human_confirmation_required=True,
            created_at=now
        )

    @staticmethod
    def dispatch_team(
        db: Session,
        request: RescueDispatchConfirmRequest,
        operator: User
    ) -> RescueDispatchResponse:
        """
        Execute atomic operator-confirmed rescue dispatch.
        Enforces strict RBAC and transactional consistency.
        """
        # 1. RBAC Check: ADMIN or OPERATOR required
        role_val = operator.role.value if hasattr(operator.role, "value") else str(operator.role).upper()
        if role_val == "CITIZEN":
            raise PermissionError("Citizen users are not authorized to confirm rescue dispatch.")
        elif role_val == "RESCUE_TEAM":
            raise PermissionError("Rescue teams cannot assign incidents to themselves.")
        elif role_val not in ["ADMIN", "OPERATOR"]:
            raise PermissionError("User role is not authorized for rescue dispatch operations.")

        # 2. Retrieve and lock incident & team
        incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
        if not incident:
            raise ValueError(f"Incident #{request.incident_id} does not exist.")

        team = db.query(RescueTeam).filter(RescueTeam.id == request.rescue_team_id).first()
        if not team:
            raise ValueError(f"Rescue team #{request.rescue_team_id} does not exist.")

        # Check for active existing assignment
        existing_assignment = db.query(RescueAssignment).filter(
            RescueAssignment.incident_id == incident.id,
            RescueAssignment.status.in_(["DISPATCHED", "EN_ROUTE", "ON_SCENE"])
        ).first()

        if existing_assignment:
            # Duplicate confirmation protection: same team already assigned
            if existing_assignment.rescue_team_id == team.id:
                raise ValueError(
                    f"Incident #{incident.id} already has active assignment #{existing_assignment.id} "
                    f"to team #{existing_assignment.rescue_team_id} ('{team.name}'). Duplicate dispatch rejected."
                )
            # Reassignment to different team requires explicit operator override
            if not request.is_override:
                raise ValueError(
                    f"Incident #{incident.id} already has active assignment #{existing_assignment.id} "
                    f"to team #{existing_assignment.rescue_team_id}. Override flag required to reassign."
                )

        # Check team availability
        if team.status != "AVAILABLE" and not request.is_override:
            raise ValueError(
                f"Team '{team.name}' is currently {team.status}. "
                "Operator explicit override is required to dispatch a busy unit."
            )

        now = datetime.now(timezone.utc)
        dist_km = haversine_distance_km(incident.latitude, incident.longitude, team.latitude, team.longitude)

        try:
            # Cancel superseded prior assignment if reassigning
            if existing_assignment:
                existing_assignment.status = "CANCELLED"
                existing_assignment.notes = (existing_assignment.notes or "") + f" | Cancelled & Superseded (Reassigned to '{team.name}')"
                old_team = db.query(RescueTeam).filter(RescueTeam.id == existing_assignment.rescue_team_id).first()
                if old_team and old_team.id != team.id:
                    old_team.status = "AVAILABLE"

            # 3. Create Rescue Assignment
            assignment = RescueAssignment(
                incident_id=incident.id,
                rescue_team_id=team.id,
                priority=1 if incident.severity == "CRITICAL" else 2,
                estimated_distance=dist_km,
                status="DISPATCHED",
                assigned_at=now,
                notes=request.notes or (
                    f"Operator '{operator.name}' confirmed dispatch of '{team.name}'. "
                    f"Override: {request.is_override} (Reason: {request.override_reason or 'None'})."
                )
            )
            db.add(assignment)
            db.flush() # obtain assignment.id

            # 4. Update Team Status
            team.status = "DISPATCHED"
            team.last_updated = now

            # 5. Update Incident Status
            incident.status = "DISPATCHED"

            # 6. Update linked SOS report if present
            if incident.sos_id:
                sos = db.query(SOSReport).filter(SOSReport.id == incident.sos_id).first()
                if sos:
                    sos.status = "DISPATCHED"

            # 7. Record Immutable Audit Log
            audit_action = "RESCUE_DISPATCH_OVERRIDE" if request.is_override else "RESCUE_DISPATCH_CONFIRMED"
            op_id = operator.id
            if op_id is not None:
                if not db.query(User).filter(User.id == op_id).first():
                    op_id = None

            audit_entry = RescueDispatchAuditLog(
                operator_id=op_id,
                operator_name=operator.name,
                incident_id=incident.id,
                rescue_team_id=team.id,
                action=audit_action,
                is_override=bool(request.is_override),
                override_reason=request.override_reason,
                details={
                    "assignment_id": assignment.id,
                    "distance_km": dist_km,
                    "incident_type": incident.incident_type,
                    "severity": incident.severity,
                    "priority_score": incident.priority_score,
                    "team_name": team.name,
                    "operator_role": operator.role.value
                },
                timestamp=now
            )
            db.add(audit_entry)
            db.flush()

            db.commit()
            db.refresh(assignment)

            logger.info(
                f"DISPATCH_COMMITTED: Assignment #{assignment.id} | Team '{team.name}' (ID #{team.id}) -> "
                f"Incident #{incident.id} by Operator '{operator.name}' (Override: {request.is_override})"
            )

        except Exception as e:
            db.rollback()
            logger.error(f"DISPATCH_ROLLBACK: Failed to commit dispatch transaction: {str(e)}")
            raise

        # 8. Emit WebSocket Domain Events
        try:
            ws_manager.broadcast_event(DomainEvent(
                event=EventType.RESCUE_ASSIGNMENT_CREATED,
                data={
                    "assignment_id": assignment.id,
                    "incident_id": incident.id,
                    "sos_id": incident.sos_id,
                    "rescue_team_id": team.id,
                    "team_name": team.name,
                    "status": "DISPATCHED",
                    "distance_km": dist_km,
                    "operator_name": operator.name,
                    "dispatched_by": operator.name,
                    "is_override": bool(request.is_override),
                    "assigned_at": now.isoformat()
                }
            ))
            ws_manager.broadcast_event(DomainEvent(
                event=EventType.RESCUE_STATUS_UPDATED,
                data={
                    "assignment_id": assignment.id,
                    "rescue_team_id": team.id,
                    "incident_id": incident.id,
                    "new_status": "DISPATCHED"
                }
            ))
        except Exception as ws_err:
            logger.warning(f"WebSocket broadcast non-fatal warning: {str(ws_err)}")

        return RescueDispatchResponse(
            success=True,
            assignment_id=assignment.id,
            incident_id=incident.id,
            rescue_team_id=team.id,
            team_name=team.name,
            incident_title=incident.title,
            status="DISPATCHED",
            assigned_at=now,
            operator_name=operator.name,
            dispatched_by=operator.name,
            is_override=bool(request.is_override),
            override_reason=request.override_reason,
            audit_id=audit_entry.id
        )

rescue_intelligence_service = RescueIntelligenceService()
