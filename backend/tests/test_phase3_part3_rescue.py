import pytest
import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models.rescue import RescueTeam, RescueAssignment, RescueDispatchAuditLog
from app.database.models.incident import Incident
from app.database.models.sos import SOSReport
from app.database.models.sos_triage import SOSTriageResult
from app.database.models.user import User, UserRole
from app.core.security import create_access_token

def get_error_msg(res):
    try:
        body = res.json()
        if "error" in body and isinstance(body["error"], dict):
            return body["error"].get("message", "")
        if "detail" in body:
            return str(body["detail"])
        return str(body)
    except Exception:
        return res.text

@pytest.fixture
def operator_token(db_session: Session):
    user = db_session.query(User).filter(User.email == "test_operator_p3p3@gov.org").first()
    if not user:
        user = User(
            name="Officer Sarah Connor",
            email="test_operator_p3p3@gov.org",
            password_hash="fakehash",
            role=UserRole.OPERATOR
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return create_access_token(user.id)

@pytest.fixture
def test_setup(db_session: Session):
    now = datetime.now(timezone.utc)
    u_id = uuid.uuid4().hex[:8]
    sos = SOSReport(
        client_id=f"sos_p3p3_{u_id}",
        latitude=13.0827,
        longitude=80.2707,
        message="Terrace flooded, 3 people trapped in rising water",
        severity="CRITICAL",
        status="PENDING"
    )
    db_session.add(sos)
    db_session.flush()

    inc = Incident(
        sos_id=sos.id,
        title=f"Flood Trapped Residents #{u_id}",
        incident_type="TRAPPED_PERSON",
        latitude=13.0827,
        longitude=80.2707,
        severity="CRITICAL",
        status="PENDING",
        priority_score=95
    )
    db_session.add(inc)

    triage = SOSTriageResult(
        sos_id=sos.id,
        incident_id=inc.id,
        incident_type="TRAPPED_PERSON",
        severity="CRITICAL",
        priority_score=95,
        people_at_risk=3,
        trapped_person=True,
        flooding=True,
        confidence=0.92,
        recommended_action="Dispatch shallow-draft rescue boat",
        reasoning=["Residents trapped on terrace", "Flood depth exceeds 1.5m"],
        data_sources=["Citizen Beacon", "PostGIS"],
        facts={"latitude": 13.0827, "longitude": 80.2707},
        predictions={"flood_probability": 0.88}
    )
    db_session.add(triage)

    # Teams
    team_a = RescueTeam(
        name=f"Water Rescue Alpha {u_id}",
        latitude=13.0850,
        longitude=80.2720,
        team_size=8,
        capacity=12,
        vehicle_type="MOTORIZED_RESCUE_BOAT",
        equipment="LIFE_JACKETS,RIVER_BOAT,FIRST_AID",
        capabilities="FLOOD_RESCUE,BOAT_RESCUE,FIRST_AID",
        status="AVAILABLE",
        last_updated=now
    )
    team_b = RescueTeam(
        name=f"Urban Evacuation Bravo {u_id}",
        latitude=13.0700,
        longitude=80.2600,
        team_size=6,
        capacity=8,
        vehicle_type="TACTICAL_TRUCK",
        equipment="WINCH,FIRST_AID",
        capabilities="EVACUATION,URBAN_RESCUE",
        status="AVAILABLE",
        last_updated=now
    )
    db_session.add(team_a)
    db_session.add(team_b)
    db_session.commit()
    db_session.refresh(inc)
    db_session.refresh(team_a)
    db_session.refresh(team_b)

    return {"sos": sos, "incident": inc, "team_a": team_a, "team_b": team_b}

def test_rescue_candidate_retrieval_and_ranking(client: TestClient, test_setup):
    inc_id = test_setup["incident"].id
    res = client.get(f"/api/v1/rescue/recommendations/{inc_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["incident_id"] == inc_id
    assert data["incident_type"] == "TRAPPED_PERSON"
    assert data["priority_score"] == 95
    assert data["human_confirmation_required"] is True
    assert len(data["candidates"]) >= 2

    primary = data["primary_candidate"]
    assert primary is not None
    assert primary["is_primary"] is True
    assert "Water Rescue" in primary["team_name"]
    assert primary["score"] >= 80
    assert primary["distance_km"] < 2.0
    assert primary["distance_label"] == "Approx. geographic distance"
    assert len(primary["reasons"]) >= 3
    assert any("AVAILABLE" in r for r in primary["reasons"])
    assert any("Approx. geographic distance only" in w for w in data["warnings"])

def test_rescue_stale_location_detection(client: TestClient, test_setup, db_session: Session):
    team_a = test_setup["team_a"]
    team_a.last_updated = datetime.now(timezone.utc) - timedelta(minutes=35)
    db_session.commit()

    inc_id = test_setup["incident"].id
    res = client.get(f"/api/v1/rescue/recommendations/{inc_id}")
    assert res.status_code == 200
    data = res.json()

    cand_a = next(c for c in data["candidates"] if c["team_id"] == team_a.id)
    assert cand_a["is_stale"] is True
    assert any("stale" in w.lower() for w in cand_a["warnings"])

def test_authorized_operator_dispatch_success(client: TestClient, test_setup, operator_token, db_session: Session):
    inc = test_setup["incident"]
    team = test_setup["team_a"]

    dispatch_payload = {
        "incident_id": inc.id,
        "rescue_team_id": team.id,
        "is_override": False,
        "notes": "Emergency boat deployment authorized by Officer Sarah"
    }

    res = client.post(
        "/api/v1/rescue/assignments/dispatch",
        json=dispatch_payload,
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert res.status_code == 200
    res_data = res.json()

    assert res_data["success"] is True
    assert res_data["incident_id"] == inc.id
    assert res_data["rescue_team_id"] == team.id
    assert res_data["status"] == "DISPATCHED"
    assert res_data["operator_name"] == "Officer Sarah Connor"

    db_session.expire_all()
    db_inc = db_session.query(Incident).filter(Incident.id == inc.id).first()
    assert db_inc.status == "DISPATCHED"

    db_team = db_session.query(RescueTeam).filter(RescueTeam.id == team.id).first()
    assert db_team.status == "DISPATCHED"

    db_sos = db_session.query(SOSReport).filter(SOSReport.id == inc.sos_id).first()
    assert db_sos.status == "DISPATCHED"

    audit = db_session.query(RescueDispatchAuditLog).filter(RescueDispatchAuditLog.id == res_data["audit_id"]).first()
    assert audit is not None
    assert audit.action == "RESCUE_DISPATCH_CONFIRMED"
    assert audit.operator_name == "Officer Sarah Connor"
    assert audit.is_override is False

def test_unauthorized_citizen_dispatch_rejected(client: TestClient, test_setup):
    inc = test_setup["incident"]
    team = test_setup["team_b"]

    dispatch_payload = {
        "incident_id": inc.id,
        "rescue_team_id": team.id
    }

    res = client.post(
        "/api/v1/rescue/assignments/dispatch",
        json=dispatch_payload,
        headers={"X-User-Role": "CITIZEN"}
    )
    assert res.status_code == 403
    assert "Citizen users are not authorized" in get_error_msg(res)

def test_rescue_team_self_assignment_rejected(client: TestClient, test_setup):
    inc = test_setup["incident"]
    team = test_setup["team_b"]

    dispatch_payload = {
        "incident_id": inc.id,
        "rescue_team_id": team.id
    }

    res = client.post(
        "/api/v1/rescue/assignments/dispatch",
        json=dispatch_payload,
        headers={"X-User-Role": "RESCUE_TEAM"}
    )
    assert res.status_code == 403
    assert "Rescue teams cannot assign incidents to themselves" in get_error_msg(res)

def test_unauthenticated_dispatch_rejected(client: TestClient, test_setup):
    inc = test_setup["incident"]
    team = test_setup["team_b"]

    res = client.post(
        "/api/v1/rescue/assignments/dispatch",
        json={"incident_id": inc.id, "rescue_team_id": team.id}
    )
    assert res.status_code == 401

def test_duplicate_dispatch_protection(client: TestClient, test_setup, operator_token):
    inc = test_setup["incident"]
    team = test_setup["team_a"]

    res_first = client.post(
        "/api/v1/rescue/assignments/dispatch",
        json={"incident_id": inc.id, "rescue_team_id": team.id},
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert res_first.status_code == 200

    res_dup = client.post(
        "/api/v1/rescue/assignments/dispatch",
        json={"incident_id": inc.id, "rescue_team_id": team.id},
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert res_dup.status_code == 400
    assert "already has active assignment" in get_error_msg(res_dup)

def test_operator_override_recorded(client: TestClient, test_setup, operator_token, db_session: Session):
    inc = test_setup["incident"]
    team_b = test_setup["team_b"]

    team_b.status = "DISPATCHED"
    db_session.commit()

    res = client.post(
        "/api/v1/rescue/assignments/dispatch",
        json={
            "incident_id": inc.id,
            "rescue_team_id": team_b.id,
            "is_override": True,
            "override_reason": "High ground proximity override by incident commander"
        },
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_override"] is True
    assert data["override_reason"] == "High ground proximity override by incident commander"

    audit = db_session.query(RescueDispatchAuditLog).filter(RescueDispatchAuditLog.id == data["audit_id"]).first()
    assert audit.is_override is True
    assert audit.action == "RESCUE_DISPATCH_OVERRIDE"

def test_ai_tools_cannot_dispatch():
    from app.ai.tools import DisasterGuardTools
    tool_names = [attr for attr in dir(DisasterGuardTools) if not attr.startswith("_")]
    assert "dispatch_rescue_team" not in tool_names
    assert "auto_dispatch" not in tool_names
    assert "confirm_dispatch" not in tool_names
