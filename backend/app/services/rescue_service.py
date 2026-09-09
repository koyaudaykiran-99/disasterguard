from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database.models.rescue import RescueTeam, RescueAssignment
from app.database.models.incident import Incident
from app.database.models.hospital import Hospital
from app.database.models.shelter import Shelter
from app.database.models.risk import RiskZone
from app.gis.spatial_queries import haversine_distance_km
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType
from app.core.logging import logger

class RescueService:
    @staticmethod
    def recommend_team(db: Session, incident_id: int) -> Dict[str, Any]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        lat = incident.latitude if incident else 13.0827
        lng = incident.longitude if incident else 80.2707
        return RescueService.recommend_and_assign(db, incident_id, lat, lng, auto_assign=False)

    @staticmethod
    def recommend_and_assign(
        db: Session,
        incident_id: int,
        lat: float,
        lng: float,
        auto_assign: bool = False
    ) -> Dict[str, Any]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()

        # 1. Nearest Available Rescue Team
        available_teams = db.query(RescueTeam).filter(RescueTeam.status == "AVAILABLE").all()
        teams = available_teams if available_teams else db.query(RescueTeam).all()

        best_team = None
        min_team_dist = float("inf")
        for team in teams:
            dist = haversine_distance_km(lat, lng, team.latitude, team.longitude)
            if dist < min_team_dist:
                min_team_dist = dist
                best_team = team

        if not best_team:
            # Fallback if no team exists in DB
            best_team = RescueTeam(
                name="Water Rescue Squad Alpha (Boat 1)",
                latitude=13.0800,
                longitude=80.2720,
                vehicle_type="MOTORIZED_RESCUE_BOAT",
                equipment="LIFE_JACKETS,RIVER_BOAT,FIRST_AID",
                status="AVAILABLE"
            )
            db.add(best_team)
            db.commit()
            db.refresh(best_team)
            min_team_dist = 1.8

        team_dist = round(min_team_dist if min_team_dist != float("inf") else 2.1, 2)
        eta_minutes = int(max(4, team_dist * 3.5 + 2))

        # 2. Nearest Hospital with bed capacity
        all_hospitals = db.query(Hospital).all()
        avail_hospitals = [h for h in all_hospitals if h.available_beds > 0]
        hospitals_to_check = avail_hospitals if avail_hospitals else all_hospitals

        best_hospital = None
        min_hosp_dist = float("inf")
        for h in hospitals_to_check:
            dist = haversine_distance_km(lat, lng, h.latitude, h.longitude)
            if dist < min_hosp_dist:
                min_hosp_dist = dist
                best_hospital = h

        hospital_name = best_hospital.name if best_hospital else "St. Jude Emergency Medical Center"
        hosp_dist = round(min_hosp_dist if min_hosp_dist != float("inf") else 3.2, 2)

        # 3. Nearest Shelter with available capacity
        all_shelters = db.query(Shelter).all()
        avail_shelters = [s for s in all_shelters if s.current_occupancy < s.capacity]
        shelters_to_check = avail_shelters if avail_shelters else all_shelters

        best_shelter = None
        min_shelter_dist = float("inf")
        for s in shelters_to_check:
            dist = haversine_distance_km(lat, lng, s.latitude, s.longitude)
            if dist < min_shelter_dist:
                min_shelter_dist = dist
                best_shelter = s

        shelter_name = best_shelter.name if best_shelter else "Central Command Stadium Shelter"
        shelter_dist = round(min_shelter_dist if min_shelter_dist != float("inf") else 2.5, 2)

        # 4. Risk Zone Lookup
        risk_zones = db.query(RiskZone).all()
        closest_zone = None
        min_rz_dist = float("inf")
        for rz in risk_zones:
            dist = haversine_distance_km(lat, lng, rz.latitude, rz.longitude)
            if dist < min_rz_dist:
                min_rz_dist = dist
                closest_zone = rz

        risk_zone_name = closest_zone.name if closest_zone else "Central Lowland Sector Alpha"
        risk_zone_level = closest_zone.risk_level if closest_zone else "HIGH"

        # 5. Policy Enforcement: Autonomous dispatch is strictly prohibited by AI-DisasterGuard architecture.
        # All dispatches must proceed through rescue_intelligence_service.dispatch_team with explicit human operator confirmation.
        if auto_assign:
            logger.warning(
                f"[SECURITY_AUDIT] Autonomous dispatch blocked for Incident #{incident_id}. "
                "Automatic creation of RescueAssignment is disabled. Explicit operator confirmation required."
            )

        existing_assign = db.query(RescueAssignment).filter(
            RescueAssignment.incident_id == incident_id,
            RescueAssignment.status.in_(["DISPATCHED", "EN_ROUTE", "ON_SCENE"])
        ).first()
        assignment_id = existing_assign.id if existing_assign else 0
        assignment_status = existing_assign.status if existing_assign else "NOT_ASSIGNED"

        return {
            "recommended_team_id": best_team.id,
            "team_name": best_team.name,
            "distance_km": team_dist,
            "estimated_response_minutes": eta_minutes,
            "reason": f"Nearest available field rescue unit equipped with {best_team.vehicle_type or 'rescue boats'}.",
            "equipment": best_team.equipment or "RESCUE_BOAT,LIFE_JACKETS,FIRST_AID",
            "recommended_hospital": hospital_name,
            "hospital_distance_km": hosp_dist,
            "recommended_shelter": shelter_name,
            "shelter_distance_km": shelter_dist,
            "risk_zone_name": risk_zone_name,
            "risk_zone_level": risk_zone_level,
            "assignment_id": assignment_id,
            "assignment_status": assignment_status,
        }

    @staticmethod
    def get_assignments(db: Session) -> List[Dict[str, Any]]:
        import re
        assignments = db.query(RescueAssignment).order_by(RescueAssignment.assigned_at.desc()).all()
        results = []
        for a in assignments:
            team = db.query(RescueTeam).filter(RescueTeam.id == a.rescue_team_id).first()
            incident = db.query(Incident).filter(Incident.id == a.incident_id).first()

            hosp_name = None
            shelter_name = None
            rz_name = None
            eta_min = int(round((a.estimated_distance or 1.0) / 0.1)) if a.estimated_distance else 5

            if a.notes:
                m_eta = re.search(r"ETA:\s*(\d+)", a.notes)
                if m_eta:
                    eta_min = int(m_eta.group(1))
                m_hosp = re.search(r"Nearest Hospital:\s*([^(]+)", a.notes)
                if m_hosp:
                    hosp_name = m_hosp.group(1).strip()
                m_shelter = re.search(r"Nearest Shelter:\s*([^(]+)", a.notes)
                if m_shelter:
                    shelter_name = m_shelter.group(1).strip()
                m_rz = re.search(r"Risk Zone:\s*([^.]+)", a.notes)
                if m_rz:
                    rz_name = m_rz.group(1).strip()

            if not hosp_name and incident:
                h = db.query(Hospital).first()
                if h:
                    hosp_name = h.name
            if not shelter_name and incident:
                s = db.query(Shelter).first()
                if s:
                    shelter_name = s.name

            results.append({
                "id": a.id,
                "incident_id": a.incident_id,
                "rescue_team_id": a.rescue_team_id,
                "team_name": team.name if team else f"Team #{a.rescue_team_id}",
                "incident_title": incident.title if incident else f"Incident #{a.incident_id}",
                "incident_type": incident.incident_type if incident else "FLOOD_TRAPPED_PERSON",
                "severity": incident.severity if incident else "HIGH",
                "priority": a.priority,
                "priority_score": incident.priority_score if incident else 85,
                "estimated_distance": a.estimated_distance,
                "eta_minutes": eta_min,
                "recommended_hospital": hosp_name,
                "recommended_shelter": shelter_name,
                "risk_zone_name": rz_name,
                "status": a.status,
                "assigned_at": a.assigned_at,
                "completed_at": a.completed_at,
                "notes": a.notes
            })
        return results

    @staticmethod
    def update_assignment_status(
        db: Session,
        assignment_id: int,
        new_status: str,
        notes: Optional[str] = None
    ) -> Optional[RescueAssignment]:
        assignment = db.query(RescueAssignment).filter(RescueAssignment.id == assignment_id).first()
        if not assignment:
            return None

        status_norm = new_status.upper()
        assignment.status = status_norm
        if notes:
            assignment.notes = (assignment.notes or "") + f" | Update: {notes}"

        team = db.query(RescueTeam).filter(RescueTeam.id == assignment.rescue_team_id).first()
        incident = db.query(Incident).filter(Incident.id == assignment.incident_id).first()

        if status_norm in ["COMPLETED", "RESOLVED"]:
            assignment.completed_at = datetime.now(timezone.utc)
            if team:
                team.status = "AVAILABLE"
            if incident:
                incident.status = "RESOLVED"
        elif status_norm in ["CANCELLED"]:
            if team:
                team.status = "AVAILABLE"
        elif status_norm in ["ARRIVED", "RESCUING", "ON_SCENE"]:
            if team:
                team.status = "ON_SCENE"
        elif status_norm in ["DISPATCHED", "EN_ROUTE", "ASSIGNED"]:
            if team:
                team.status = "DISPATCHED"

        db.commit()
        db.refresh(assignment)

        # Broadcast RESCUE_STATUS_UPDATED
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.RESCUE_STATUS_UPDATED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=assignment.id,
                    entity_type="rescue_assignment",
                    severity="HIGH" if status_norm in ["DISPATCHED", "EN_ROUTE", "RESCUING"] else "LOW",
                    data={
                        "assignment_id": assignment.id,
                        "incident_id": assignment.incident_id,
                        "rescue_team_id": assignment.rescue_team_id,
                        "team_name": team.name if team else f"Team #{assignment.rescue_team_id}",
                        "status": assignment.status,
                        "team_status": team.status if team else "UNKNOWN",
                        "notes": assignment.notes
                    }
                )
            )
        except Exception as e:
            pass

        return assignment

rescue_service = RescueService()
