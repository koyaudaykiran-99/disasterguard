from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.ai.tools import DisasterGuardTools

class ContextRouter:
    """Classifies user intent and collects targeted operational context."""

    @staticmethod
    def route_intent(prompt: str) -> str:
        p = prompt.lower()
        if any(w in p for w in ["briefing", "sitrep", "summary of situation", "overview"]):
            return "BRIEFING"
        elif any(w in p for w in ["weather", "rainfall", "precipitation", "radar"]):
            return "WEATHER"
        elif any(w in p for w in ["flood", "inundation", "water depth", "river", "soil"]):
            return "FLOOD_PREDICTION"
        elif any(w in p for w in ["why is", "risk critical", "explain risk", "risk score", "zone critical"]):
            return "RISK_EXPLANATION"
        elif any(w in p for w in ["incident", "trapped", "sos", "distress", "who needs rescue", "critical incident"]):
            return "INCIDENTS_RESCUE"
        elif any(w in p for w in ["shelter", "evacuation center", "safe haven", "where can i go", "safest shelter"]):
            return "SHELTERS"
        elif any(w in p for w in ["hospital", "medical", "ambulance", "trauma", "doctor"]):
            return "HOSPITALS"
        elif any(w in p for w in ["rescue", "team", "boat", "squad", "dispatch"]):
            return "RESCUE_TEAMS"
        return "GENERAL_SITUATION"

class ContextManager:
    """Assembles structured operational context based on routed intent and user role."""

    @staticmethod
    def build_context(
        db: Session,
        prompt: str,
        role: str = "OPERATOR",
        location: Optional[Dict[str, float]] = None,
        incident_id: Optional[int] = None
    ) -> Dict[str, Any]:
        intent = ContextRouter.route_intent(prompt)
        lat = location.get("latitude", 13.0827) if location else 13.0827
        lng = location.get("longitude", 80.2707) if location else 80.2707

        context: Dict[str, Any] = {
            "intent": intent,
            "role": role,
            "sources": []
        }

        # Targeted tool execution based on intent
        if intent in ["BRIEFING", "GENERAL_SITUATION"]:
            context["weather"] = DisasterGuardTools.get_current_weather(db)
            context["rainfall_prediction"] = DisasterGuardTools.get_latest_rainfall_prediction(db)
            context["flood_prediction"] = DisasterGuardTools.get_latest_flood_prediction(db)
            context["risk_zones"] = DisasterGuardTools.get_current_risk_zones(db, limit=5)
            context["active_alerts"] = DisasterGuardTools.get_active_alerts(db, limit=5)
            context["critical_incidents"] = DisasterGuardTools.get_critical_incidents(db, role=role, limit=5)
            context["active_sos"] = DisasterGuardTools.get_active_sos(db, role=role, limit=5)
            context["rescue_teams"] = DisasterGuardTools.get_rescue_team_status(db, role=role, limit=5)
            context["simulation"] = DisasterGuardTools.get_simulation_status()
            context["sources"] = ["Weather API", "Rainfall ML v2.0", "Flood ML v1.0", "Risk Engine", "Incidents", "Alerts"]

        elif intent in ["WEATHER", "FLOOD_PREDICTION", "RISK_EXPLANATION"]:
            context["weather"] = DisasterGuardTools.get_current_weather(db)
            context["rainfall_prediction"] = DisasterGuardTools.get_latest_rainfall_prediction(db)
            context["flood_prediction"] = DisasterGuardTools.get_latest_flood_prediction(db)
            context["risk_zones"] = DisasterGuardTools.get_current_risk_zones(db, limit=5)
            context["active_alerts"] = DisasterGuardTools.get_active_alerts(db, limit=3)
            context["historical_risk"] = DisasterGuardTools.get_historical_risk(db)
            context["sources"] = ["Doppler Weather Observation", "Scikit-Learn Rainfall Model", "Inundation Engine", "Risk Zones"]

        elif intent in ["INCIDENTS_RESCUE", "RESCUE_TEAMS"]:
            context["critical_incidents"] = DisasterGuardTools.get_critical_incidents(db, role=role, limit=8)
            context["active_sos"] = DisasterGuardTools.get_active_sos(db, role=role, limit=8)
            context["rescue_teams"] = DisasterGuardTools.get_rescue_team_status(db, role=role, limit=10)
            context["rescue_assignments"] = DisasterGuardTools.get_rescue_assignments(db, role=role, limit=5)
            context["risk_zones"] = DisasterGuardTools.get_current_risk_zones(db, limit=3)
            context["sources"] = ["Incident Command DB", "SOS Distress Registry", "Rescue Fleet Telemetry", "Risk Engine"]

        elif intent == "SHELTERS":
            context["nearby_shelters"] = DisasterGuardTools.get_nearby_shelters(db, lat=lat, lng=lng, limit=5)
            context["risk_zones"] = DisasterGuardTools.get_current_risk_zones(db, limit=3)
            context["active_alerts"] = DisasterGuardTools.get_active_alerts(db, limit=3)
            context["sources"] = ["PostGIS Shelter Registry", "Spatial Risk Polygons", "Emergency Alerts"]

        elif intent == "HOSPITALS":
            context["nearby_hospitals"] = DisasterGuardTools.get_nearby_hospitals(db, lat=lat, lng=lng, limit=5)
            context["sources"] = ["Hospital Emergency Directory", "Trauma Resource Index"]

        if incident_id:
            context["target_incident"] = DisasterGuardTools.get_incident_details(db, incident_id, role=role)
            context["sources"].append("Target Incident Record")

        return context
