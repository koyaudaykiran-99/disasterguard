from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentClassificationResponse

class IncidentService:
    @staticmethod
    def classify_incident(description: str) -> IncidentClassificationResponse:
        desc_lower = (description or "").lower()

        is_trapped = any(w in desc_lower for w in ["trapped", "stranded", "stuck", "surrounded", "cannot get out", "roof", "rooftop"])
        is_vulnerable = any(w in desc_lower for w in ["elderly", "infant", "baby", "child", "children", "pregnant", "disabled", "wheelchair", "senior"])
        is_water_inundated = any(w in desc_lower for w in ["water entered", "rising water", "flooded house", "flooded basement", "submerged", "waist deep", "chest deep", "rushing water"])
        is_medical = any(w in desc_lower for w in ["medical", "injured", "injury", "bleeding", "unconscious", "heart", "oxygen", "hospital", "asthma"])
        is_supplies = any(w in desc_lower for w in ["food", "drinking water", "starving", "rations", "supplies", "dry clothes"])

        if is_trapped and is_vulnerable:
            return IncidentClassificationResponse(
                incident_type="FLOOD_TRAPPED_PERSON",
                severity="CRITICAL",
                priority_score=98,
                recommended_action="IMMEDIATE_RESCUE_BOAT_DISPATCH"
            )
        elif is_trapped or (is_water_inundated and is_vulnerable):
            return IncidentClassificationResponse(
                incident_type="FLOOD_TRAPPED_PERSON",
                severity="CRITICAL",
                priority_score=95,
                recommended_action="IMMEDIATE_RESCUE_BOAT_DISPATCH"
            )
        elif is_medical:
            return IncidentClassificationResponse(
                incident_type="MEDICAL_EMERGENCY",
                severity="HIGH",
                priority_score=88,
                recommended_action="AMBULANCE_AIR_RESCUE_DISPATCH"
            )
        elif is_water_inundated:
            return IncidentClassificationResponse(
                incident_type="GENERAL_FLOOD_EVACUATION",
                severity="HIGH",
                priority_score=75,
                recommended_action="EVACUATION_ASSISTANCE_DISPATCH"
            )
        elif is_supplies:
            return IncidentClassificationResponse(
                incident_type="RELIEF_SUPPLIES_NEEDED",
                severity="MODERATE",
                priority_score=58,
                recommended_action="SHELTER_RELIEF_AIRDROP"
            )
        else:
            return IncidentClassificationResponse(
                incident_type="GENERAL_FLOOD_EVACUATION",
                severity="MODERATE",
                priority_score=50,
                recommended_action="COMMUNITY_EVACUATION_ADVISORY"
            )

    @staticmethod
    def get_prioritized_incidents(db: Session) -> List[Incident]:
        return db.query(Incident).order_by(Incident.priority_score.desc(), Incident.created_at.desc()).all()

    @staticmethod
    def create_incident(db: Session, inc_in: IncidentCreate) -> Incident:
        classified = IncidentService.classify_incident(inc_in.description or inc_in.title)
        
        inc = Incident(
            title=inc_in.title,
            description=inc_in.description,
            incident_type=classified.incident_type,
            latitude=inc_in.latitude,
            longitude=inc_in.longitude,
            severity=classified.severity,
            status="PENDING",
            source=inc_in.source,
            priority_score=classified.priority_score
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        return inc

incident_service = IncidentService()
