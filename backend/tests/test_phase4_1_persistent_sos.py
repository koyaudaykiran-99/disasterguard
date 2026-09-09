import pytest
import uuid
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models.sos import SOSReport
from app.database.models.incident import Incident
from app.database.models.sos_triage import SOSTriageResult
from app.database.models.emergency_update import EmergencyUpdate
from app.database.models.rescue import RescueAssignment

def test_persistent_sos_lifecycle(client: TestClient, db_session: Session):
    u_id = uuid.uuid4().hex[:8]
    client_id = f"test_persist_{u_id}"

    # 1. Initial SOS submission
    payload_sos = {
        "client_id": client_id,
        "latitude": 13.0827,
        "longitude": 80.2707,
        "accuracy": 8.0,
        "message": "Water entered street and driveway",
        "severity": "HIGH",
        "transport": "INTERNET"
    }
    res = client.post("/api/v1/sos/", json=payload_sos)
    assert res.status_code == 200
    sos_data = res.json()
    sos_id = sos_data["id"]
    assert sos_data["status"] == "PENDING"

    # Verify initial update exists
    initial_update = db_session.query(EmergencyUpdate).filter(
        EmergencyUpdate.sos_id == sos_id,
        EmergencyUpdate.update_type == "INITIAL_SOS"
    ).first()
    assert initial_update is not None
    assert initial_update.update_type == "INITIAL_SOS"

    # 2. Repeated SOS with same client_id (idempotent / returns same SOS)
    res_repeat = client.post("/api/v1/sos/", json=payload_sos)
    assert res_repeat.status_code == 200
    assert res_repeat.json()["id"] == sos_id

    # 3. Add text emergency update
    up1 = {
        "client_update_id": f"up_{u_id}_1",
        "update_type": "TEXT_UPDATE",
        "message": "Water entered house, currently 1 foot deep",
        "source": "CITIZEN_APP"
    }
    res_up1 = client.post(f"/api/v1/sos/{sos_id}/updates", json=up1)
    assert res_up1.status_code == 200
    assert res_up1.json()["update_type"] == "TEXT_UPDATE"

    # 4. Add GPS location update
    up_gps = {
        "client_update_id": f"up_{u_id}_gps",
        "update_type": "LOCATION_UPDATE",
        "message": "Moved to elevated terrace",
        "latitude": 13.0855,
        "longitude": 80.2735,
        "accuracy": 5.0
    }
    res_gps = client.post(f"/api/v1/sos/{sos_id}/updates", json=up_gps)
    assert res_gps.status_code == 200
    db_session.expire_all()
    updated_sos = db_session.query(SOSReport).filter(SOSReport.id == sos_id).first()
    assert abs(updated_sos.latitude - 13.0855) < 1e-4

    # 5. Add critical trapped person update triggering AI re-triage
    up_crit = {
        "client_update_id": f"up_{u_id}_crit",
        "update_type": "TRAPPED_PERSON_UPDATE",
        "message": "Father is trapped on ground floor, water is rising rapidly",
        "source": "CITIZEN_APP"
    }
    res_crit = client.post(f"/api/v1/sos/{sos_id}/updates", json=up_crit)
    assert res_crit.status_code == 200

    # 6. Verify AI re-triage escalated priority and severity
    db_session.expire_all()
    triage = db_session.query(SOSTriageResult).filter(SOSTriageResult.sos_id == sos_id).first()
    assert triage is not None
    assert triage.trapped_person is True
    assert triage.priority_score >= 85
    assert triage.severity == "CRITICAL"
    assert triage.human_confirmation_required is True

    # 7. Verify NO automatic dispatch occurred (Human barrier)
    linked_inc = db_session.query(Incident).filter(Incident.sos_id == sos_id).first()
    assert linked_inc is not None
    assert linked_inc.status == "PENDING"
    assignments = db_session.query(RescueAssignment).filter(RescueAssignment.incident_id == linked_inc.id).count()
    assert assignments == 0

    # 8. Verify timeline retrieval
    res_timeline = client.get(f"/api/v1/sos/{sos_id}/updates")
    assert res_timeline.status_code == 200
    updates_list = res_timeline.json()
    assert len(updates_list) >= 4

    # 9. Verify update idempotency
    res_dup = client.post(f"/api/v1/sos/{sos_id}/updates", json=up_crit)
    assert res_dup.status_code == 200
    assert res_dup.json()["id"] == res_crit.json()["id"]
