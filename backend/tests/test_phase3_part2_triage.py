import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.database.models.sos import SOSReport
from app.database.models.incident import Incident
from app.database.models.rescue import RescueAssignment
from app.database.models.sos_triage import SOSTriageResult

def test_sos_triage_trapped_person_critical(client: TestClient, db_session: Session):
    payload = {
        "client_id": "sos_triage_test_trapped_001",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "accuracy": 12.0,
        "message": "Water entered ground floor, elderly grandmother trapped and cannot get out",
        "severity": "CRITICAL"
    }
    res = client.post("/api/v1/sos/", json=payload)
    assert res.status_code == 200
    data = res.json()
    sos_id = data["id"]

    # Fetch triage via dedicated endpoint
    triage_res = client.get(f"/api/v1/sos/{sos_id}/triage")
    assert triage_res.status_code == 200
    triage = triage_res.json()

    assert triage["sos_id"] == sos_id
    assert triage["incident_type"] == "TRAPPED_PERSON"
    assert triage["severity"] == "CRITICAL"
    assert triage["priority_score"] >= 85
    assert triage["trapped_person"] is True
    assert triage["confidence"] >= 0.85
    assert len(triage["reasoning"]) >= 2
    assert any("trapped" in r.lower() for r in triage["reasoning"])

def test_sos_triage_medical_emergency(client: TestClient, db_session: Session):
    payload = {
        "client_id": "sos_triage_test_med_002",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "accuracy": 10.0,
        "message": "Resident has deep wound, bleeding and needs immediate medical hospital care",
        "severity": "HIGH"
    }
    res = client.post("/api/v1/sos/", json=payload)
    assert res.status_code == 200
    sos_id = res.json()["id"]

    triage_res = client.get(f"/api/v1/sos/{sos_id}/triage")
    assert triage_res.status_code == 200
    triage = triage_res.json()

    assert triage["incident_type"] == "MEDICAL_EMERGENCY"
    assert triage["medical_emergency"] is True
    assert triage["priority_score"] >= 65

def test_sos_triage_facts_predictions_separation(client: TestClient):
    payload = {
        "client_id": "sos_triage_test_facts_003",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "message": "Rising floodwaters in residential street, basement submerged",
        "severity": "HIGH"
    }
    res = client.post("/api/v1/sos/", json=payload)
    assert res.status_code == 200
    sos_id = res.json()["id"]

    evidence_res = client.get(f"/api/v1/sos/{sos_id}/evidence")
    assert evidence_res.status_code == 200
    evidence = evidence_res.json()

    # Verify Facts
    facts = evidence["facts"]
    assert facts["latitude"] == 13.0827
    assert facts["longitude"] == 80.2707
    assert "rising floodwaters" in facts["reported_message"].lower()

    # Verify Predictions
    preds = evidence["predictions"]
    assert "flood_probability" in preds
    assert "estimated_water_depth_m" in preds
    assert "risk_zone_name" in preds

    # Verify Sources & Interpretation
    assert len(evidence["data_sources"]) >= 3
    assert len(evidence["ai_interpretation"]) > 20
    assert evidence["human_confirmation_required"] is True

def test_sos_triage_idempotency_duplicate_protection(client: TestClient, db_session: Session):
    payload = {
        "client_id": "sos_triage_test_idempotent_004",
        "latitude": 13.0500,
        "longitude": 80.2500,
        "message": "Power cut off and road blocked by fallen trees",
        "severity": "MODERATE"
    }
    res = client.post("/api/v1/sos/", json=payload)
    assert res.status_code == 200
    sos_id = res.json()["id"]

    # Trigger triage multiple times
    t1 = client.post(f"/api/v1/sos/{sos_id}/triage")
    assert t1.status_code == 200
    t2 = client.post(f"/api/v1/sos/{sos_id}/triage")
    assert t2.status_code == 200

    assert t1.json()["id"] == t2.json()["id"]

    # Verify database has exactly 1 row for this sos_id
    rows = db_session.query(SOSTriageResult).filter(SOSTriageResult.sos_id == sos_id).all()
    assert len(rows) == 1

def test_sos_triage_human_in_the_loop_no_autonomous_dispatch(client: TestClient, db_session: Session):
    payload = {
        "client_id": "sos_triage_test_hitl_005",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "message": "Immediate rescue needed, water rising fast",
        "severity": "CRITICAL"
    }
    res = client.post("/api/v1/sos/", json=payload)
    assert res.status_code == 200
    sos_data = res.json()
    sos_id = sos_data["id"]

    # Verify SOS status remains PENDING
    assert sos_data["status"] == "PENDING"

    # Verify linked Incident remains PENDING
    inc = db_session.query(Incident).filter(Incident.sos_id == sos_id).first()
    assert inc is not None
    assert inc.status == "PENDING"

    # Verify NO automatic rescue assignment was created for this incident
    asg = db_session.query(RescueAssignment).filter(RescueAssignment.incident_id == inc.id).first()
    assert asg is None, "Violation: Rescue squad was autonomously assigned without operator confirmation!"

    # Verify triage specifies human confirmation required
    triage = client.get(f"/api/v1/sos/{sos_id}/triage").json()
    assert triage["human_confirmation_required"] is True

def test_sos_triage_vague_message_fallback(client: TestClient):
    payload = {
        "client_id": "sos_triage_test_vague_006",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "message": "Testing situation checking general inquiry",
        "severity": "LOW"
    }
    res = client.post("/api/v1/sos/", json=payload)
    assert res.status_code == 200
    sos_id = res.json()["id"]

    triage = client.get(f"/api/v1/sos/{sos_id}/triage").json()
    assert triage["incident_type"] == "OTHER"
    assert triage["confidence"] <= 0.80
    assert triage["priority_score"] <= 60
    assert triage["triage_status"] == "COMPLETE"

