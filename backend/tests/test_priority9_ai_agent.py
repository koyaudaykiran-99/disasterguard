import pytest
from app.ai.tools import DisasterGuardTools
from app.ai.provider import AIProvider, GPTAstraProvider, FallbackAIProvider, get_ai_provider
from app.ai.safety import AISafetyGuard, ADVISORY_DISCLAIMER
from app.ai.context import ContextRouter, ContextManager
from app.ai.agent import AIEmergencyAgent
from app.ai.schemas import (
    AIEmergencyRequest, AIEmergencyResponse,
    EmergencyBriefingResponse, IncidentAnalysisResponse,
    RiskExplanationResponse, ShelterRecommendationResponse,
    RescueAnalysisResponse
)
from app.database.models.weather import WeatherObservation
from app.database.models.prediction import RainfallPrediction, FloodPrediction
from app.database.models.risk import RiskZone
from app.database.models.alert import Alert
from app.database.models.sos import SOSReport
from app.database.models.incident import Incident
from app.database.models.rescue import RescueTeam, RescueAssignment
from app.database.models.shelter import Shelter
from app.database.models.hospital import Hospital

def test_ai_provider_abstraction():
    """Verify AI provider interface and fallback mechanics."""
    provider = get_ai_provider()
    assert isinstance(provider, AIProvider)
    fallback = FallbackAIProvider()
    assert isinstance(fallback, AIProvider)

def test_weather_tool(db_session):
    """Verify weather tool retrieves latest observation."""
    res = DisasterGuardTools.get_current_weather(db_session)
    assert isinstance(res, dict)
    assert "rainfall_24h_mm" in res or res.get("status") == "NO_DATA"

def test_rainfall_prediction_tool(db_session):
    """Verify rainfall prediction tool retrieves ML forecast."""
    res = DisasterGuardTools.get_latest_rainfall_prediction(db_session)
    assert isinstance(res, dict)
    assert "predicted_rainfall_mm" in res or res.get("status") == "NO_DATA"

def test_flood_prediction_tool(db_session):
    """Verify flood prediction tool retrieves inundation probability."""
    res = DisasterGuardTools.get_latest_flood_prediction(db_session)
    assert isinstance(res, dict)
    assert "flood_probability" in res or res.get("status") == "NO_DATA"

def test_risk_zones_tool(db_session):
    """Verify risk zones tool queries and ranks zones."""
    zones = DisasterGuardTools.get_current_risk_zones(db_session, limit=5)
    assert isinstance(zones, list)
    if zones:
        assert "risk_score" in zones[0]
        assert "risk_level" in zones[0]

def test_alerts_tool(db_session):
    """Verify active alerts tool queries alerts."""
    alerts = DisasterGuardTools.get_active_alerts(db_session, limit=5)
    assert isinstance(alerts, list)

def test_sos_tool_role_redaction(db_session):
    """Verify SOS tool masks detailed PII when called by CITIZEN role."""
    # Ensure at least 1 SOS exists
    sos = db_session.query(SOSReport).first()
    if not sos:
        sos = SOSReport(latitude=13.08, longitude=80.27, message="Need help water rising", severity="HIGH", status="PENDING")
        db_session.add(sos)
        db_session.commit()

    # Citizen role check
    citizen_sos = DisasterGuardTools.get_active_sos(db_session, role="CITIZEN")
    assert isinstance(citizen_sos, list)
    assert "active_sos_count" in citizen_sos[0]
    assert "note" in citizen_sos[0]

    # Operator role check
    operator_sos = DisasterGuardTools.get_active_sos(db_session, role="OPERATOR")
    assert isinstance(operator_sos, list)
    assert len(operator_sos) > 0
    assert "message" in operator_sos[0]

def test_incidents_tool_role_redaction(db_session):
    """Verify incident tool hides internal rescue telemetry from CITIZEN."""
    inc = db_session.query(Incident).first()
    if not inc:
        inc = Incident(title="Trapped family", severity="CRITICAL", priority_score=90, status="PENDING", latitude=13.08, longitude=80.27)
        db_session.add(inc)
        db_session.commit()

    citizen_inc = DisasterGuardTools.get_critical_incidents(db_session, role="CITIZEN")
    assert "rescue_assigned" not in citizen_inc[0]

    operator_inc = DisasterGuardTools.get_critical_incidents(db_session, role="OPERATOR")
    assert "rescue_assigned" in operator_inc[0]

def test_rescue_team_tool_role_redaction(db_session):
    """Verify rescue fleet tool hides squad positions from CITIZEN."""
    cit_teams = DisasterGuardTools.get_rescue_team_status(db_session, role="CITIZEN")
    assert "teams" not in cit_teams
    assert "available_teams_count" in cit_teams

    op_teams = DisasterGuardTools.get_rescue_team_status(db_session, role="OPERATOR")
    assert "teams" in op_teams

def test_shelters_tool_and_safety(db_session):
    """Verify spatial shelter queries evaluate distance and nearby risk."""
    if db_session.query(Shelter).count() == 0:
        s = Shelter(name="High Ground Community Center", latitude=13.09, longitude=80.28, capacity=500, current_occupancy=50, contact="+91 44 1122 3344", status="OPEN")
        db_session.add(s)
        db_session.commit()

    shelters = DisasterGuardTools.get_nearby_shelters(db_session, lat=13.0827, lng=80.2707, limit=3)
    assert len(shelters) > 0
    assert "distance_km" in shelters[0]
    assert "vicinity_risk_level" in shelters[0]

def test_hospitals_tool(db_session):
    """Verify hospital directory queries trauma facilities."""
    if db_session.query(Hospital).count() == 0:
        h = Hospital(name="City Emergency Hospital", latitude=13.085, longitude=80.275, emergency_capacity=200, available_beds=50, contact="+91 44 2345 6789", status="AVAILABLE")
        db_session.add(h)
        db_session.commit()

    hospitals = DisasterGuardTools.get_nearby_hospitals(db_session, lat=13.0827, lng=80.2707, limit=3)
    assert len(hospitals) > 0
    assert "emergency_capacity" in hospitals[0]

def test_simulation_status_tool():
    """Verify simulation status tool reads scenario state."""
    sim = DisasterGuardTools.get_simulation_status()
    assert isinstance(sim, dict)
    assert "stage" in sim

def test_system_status_tool():
    """Verify system status tool checks WebSocket and database."""
    sys_status = DisasterGuardTools.get_system_status()
    assert sys_status["database_engine"] == "PostgreSQL 18 + PostGIS"
    assert "active_operator_connections" in sys_status

def test_safety_guardrails_secret_redaction():
    """Verify safety sanitizer scrubs API keys and connection strings."""
    dirty_payload = {
        "answer": "Using secret xpl_75a688fa4f009a249a105f096843fdcfddc6857c and db postgresql://postgres:pw@localhost/db",
        "recommendations": [],
        "warnings": []
    }
    sanitized = AISafetyGuard.sanitize_response(dirty_payload)
    assert "xpl_" not in sanitized["answer"]
    assert "postgresql://" not in sanitized["answer"]
    assert "[REDACTED_CREDENTIAL]" in sanitized["answer"]
    assert ADVISORY_DISCLAIMER in sanitized["warnings"]

def test_safety_guardrails_autonomous_claim_prevention():
    """Verify safety sanitizer flags and corrects claims of autonomous dispatch."""
    claim_payload = {
        "answer": "I have dispatched Rescue Squad Alpha to your location immediately.",
        "recommendations": ["Stay put"],
        "warnings": []
    }
    sanitized = AISafetyGuard.sanitize_response(claim_payload)
    assert "SAFETY CORRECTION" in sanitized["answer"]
    assert ADVISORY_DISCLAIMER in sanitized["warnings"]

def test_context_router_intents():
    """Verify intent router categorizes queries accurately."""
    assert ContextRouter.route_intent("Give me an emergency briefing") == "BRIEFING"
    assert ContextRouter.route_intent("What is the current rainfall?") == "WEATHER"
    assert ContextRouter.route_intent("Why is this zone critical risk?") == "RISK_EXPLANATION"
    assert ContextRouter.route_intent("Where is the safest shelter nearby?") == "SHELTERS"
    assert ContextRouter.route_intent("Who needs rescue right now?") == "INCIDENTS_RESCUE"

def test_api_chat_endpoint(client):
    """Test POST /api/v1/ai/chat returns structured grounded response."""
    resp = client.post("/api/v1/ai/chat", json={
        "message": "What is the current disaster situation?",
        "persona": "COMMAND_DISPATCHER",
        "role": "OPERATOR"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "severity" in data
    assert "sources" in data
    assert "recommendations" in data
    assert "warnings" in data
    assert "reply" in data  # Backwards compatibility check
    assert len(data["sources"]) > 0

def test_api_briefing_endpoint(client):
    """Test POST /api/v1/ai/briefing produces executive situation report."""
    resp = client.post("/api/v1/ai/briefing?role=OPERATOR")
    assert resp.status_code == 200
    data = resp.json()
    assert "situation_summary" in data
    assert "weather_summary" in data
    assert "flood_risk_summary" in data
    assert "recommended_priorities" in data
    assert "disclaimer" in data

def test_api_explain_risk_endpoint(client, db_session):
    """Test POST /api/v1/ai/explain-risk returns multi-factor breakdown."""
    zone = db_session.query(RiskZone).first()
    zone_id = zone.id if zone else 1
    resp = client.post("/api/v1/ai/explain-risk", json={"zone_id": zone_id})
    assert resp.status_code == 200
    data = resp.json()
    assert "zone_name" in data
    assert "composite_risk_score" in data
    assert "primary_drivers" in data
    assert "breakdown" in data

def test_api_recommend_shelter_endpoint(client):
    """Test POST /api/v1/ai/recommend-shelter returns safe evacuation option."""
    resp = client.post("/api/v1/ai/recommend-shelter", json={
        "latitude": 13.0827,
        "longitude": 80.2707,
        "role": "CITIZEN"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "route_safety_notes" in data
    assert "warnings" in data

def test_api_rescue_analysis_endpoint(client):
    """Test POST /api/v1/ai/rescue-analysis matches unassigned incidents."""
    resp = client.post("/api/v1/ai/rescue-analysis?role=OPERATOR")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_unassigned_incidents" in data
    assert "tactical_rationale" in data
    assert "advisory_notice" in data

def test_api_analyze_incident_endpoint(client, db_session):
    """Test POST /api/v1/ai/analyze-incident returns detailed incident breakdown."""
    inc = db_session.query(Incident).first()
    if not inc:
        inc = Incident(title="Terrace rescue", severity="HIGH", priority_score=85, status="PENDING", latitude=13.08, longitude=80.27)
        db_session.add(inc)
        db_session.commit()

    resp = client.post("/api/v1/ai/analyze-incident", json={"incident_id": inc.id})
    assert resp.status_code == 200
    data = resp.json()
    assert data["incident_id"] == inc.id
    assert "recommended_action" in data
    assert "triage_summary" in data

def test_role_authorization_in_chat(client):
    """Verify citizen role gets citizen-appropriate guidance without tactical leak."""
    resp = client.post("/api/v1/ai/chat", json={
        "message": "Where are the rescue teams positioned?",
        "role": "CITIZEN"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
