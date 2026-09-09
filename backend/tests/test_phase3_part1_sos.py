import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.database.models.sos import SOSReport

def test_submit_valid_citizen_sos(client: TestClient, db_session: Session):
    payload = {
        "client_id": "sos_test_valid_001",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "accuracy": 14.5,
        "message": "Water reached 1st floor level, urgent assistance required",
        "severity": "CRITICAL",
        "transport": "INTERNET"
    }
    response = client.post("/api/v1/sos/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["client_id"] == "sos_test_valid_001"
    assert data["latitude"] == 13.0827
    assert data["longitude"] == 80.2707
    assert data["accuracy"] == 14.5
    assert data["transport"] == "INTERNET"
    assert data["status"] in ["PENDING", "DISPATCHED"]
    assert "id" in data
    assert data["sos_id"] == data["id"]
    assert "created_at" in data

    # Verify database persistence
    db_sos = db_session.query(SOSReport).filter(SOSReport.client_id == "sos_test_valid_001").first()
    assert db_sos is not None
    assert db_sos.id == data["id"]
    assert db_sos.accuracy == 14.5

def test_submit_sos_invalid_coordinates(client: TestClient):
    # Latitude > 90
    bad_lat = {
        "latitude": 95.5,
        "longitude": 80.2707,
        "message": "Test invalid latitude"
    }
    res1 = client.post("/api/v1/sos/", json=bad_lat)
    assert res1.status_code == 422

    # Longitude < -180
    bad_lng = {
        "latitude": 13.0827,
        "longitude": -185.0,
        "message": "Test invalid longitude"
    }
    res2 = client.post("/api/v1/sos/", json=bad_lng)
    assert res2.status_code == 422

def test_submit_sos_invalid_severity(client: TestClient):
    payload = {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "message": "Test invalid severity",
        "severity": "CATASTROPHIC_ULTRA"
    }
    res = client.post("/api/v1/sos/", json=payload)
    assert res.status_code == 422

def test_submit_sos_empty_message(client: TestClient):
    payload = {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "message": "   "
    }
    res = client.post("/api/v1/sos/", json=payload)
    assert res.status_code == 422

def test_sos_idempotency_duplicate_client_id(client: TestClient, db_session: Session):
    client_id = "sos_test_idempotency_unique_999"
    payload = {
        "client_id": client_id,
        "latitude": 13.0450,
        "longitude": 80.2400,
        "accuracy": 8.0,
        "message": "House submerged, family on second floor",
        "severity": "HIGH",
        "transport": "INTERNET"
    }

    # First submission
    res1 = client.post("/api/v1/sos/", json=payload)
    assert res1.status_code == 200
    sos1 = res1.json()

    # Second submission (simulating retry / reconnect)
    res2 = client.post("/api/v1/sos/", json=payload)
    assert res2.status_code == 200
    sos2 = res2.json()

    # Must resolve to the exact same SOS record
    assert sos1["id"] == sos2["id"]
    assert sos1["client_id"] == sos2["client_id"]

    # Verify only ONE database record exists
    matches = db_session.query(SOSReport).filter(SOSReport.client_id == client_id).all()
    assert len(matches) == 1

def test_sos_server_authority_disregards_client_overrides(client: TestClient):
    payload = {
        "client_id": "sos_test_authority_002",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "message": "Citizen reporting flooding",
        "severity": "CRITICAL",
        # Client tries to claim status or priority
        "status": "RESCUED",
        "priority": 1,
        "role": "admin"
    }
    res = client.post("/api/v1/sos/", json=payload)
    assert res.status_code == 200
    data = res.json()
    # Server decides status (starts at PENDING or DISPATCHED, never RESCUED)
    assert data["status"] in ["PENDING", "DISPATCHED"]
    assert data["status"] != "RESCUED"
