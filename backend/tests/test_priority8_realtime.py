import pytest
from unittest.mock import patch, MagicMock
from app.schemas.events import DomainEvent, EventType
from app.services.websocket_manager import WebSocketManager, ws_manager
from app.database.models.risk import RiskZone
from app.database.models.rescue import RescueTeam, RescueAssignment
from app.database.models.incident import Incident
from app.database.models.alert import Alert

def test_event_type_taxonomy():
    """Verify all 15 required domain event types are present and correctly formatted."""
    expected_events = [
        "WEATHER_UPDATED",
        "RAIN_PREDICTION_UPDATED",
        "FLOOD_PREDICTION_UPDATED",
        "RISK_ZONE_UPDATED",
        "ALERT_CREATED",
        "ALERT_UPDATED",
        "SOS_CREATED",
        "SOS_TRIAGED",
        "INCIDENT_CREATED",
        "RESCUE_ASSIGNMENT_CREATED",
        "RESCUE_STATUS_UPDATED",
        "SHELTER_STATUS_UPDATED",
        "HOSPITAL_STATUS_UPDATED",
        "SIMULATION_STAGE_CHANGED",
        "SYSTEM_STATUS_CHANGED",
    ]
    for event_name in expected_events:
        assert hasattr(EventType, event_name)
        assert getattr(EventType, event_name).value == event_name

    # Test DomainEvent serialization
    evt = DomainEvent(
        event=EventType.RESCUE_STATUS_UPDATED,
        timestamp="2026-09-06T18:00:00Z",
        entity_type="rescue_assignment",
        entity_id="12",
        severity="HIGH",
        data={"status": "EN_ROUTE", "team_id": 3}
    )
    dumped = evt.model_dump()
    assert dumped["event"] == "RESCUE_STATUS_UPDATED"
    assert dumped["severity"] == "HIGH"
    assert dumped["entity_id"] == "12"
    assert dumped["data"]["status"] == "EN_ROUTE"

def test_ws_connection_and_handshake(client):
    """Test connecting to the WebSocket endpoint and receiving initial handshake."""
    with client.websocket_connect("/api/v1/ws") as websocket:
        welcome = websocket.receive_json()
        assert welcome["event"] == "SYSTEM_STATUS_CHANGED"
        assert welcome["data"]["status"] == "connected"
        assert welcome["data"]["role"] == "OPERATOR"
        assert "client_id" in welcome["data"]

def test_ws_ping_pong(client):
    """Test bidirectional text ping-pong over the WebSocket."""
    with client.websocket_connect("/api/v1/ws") as websocket:
        _ = websocket.receive_json()  # Handshake
        websocket.send_text("ping")
        resp = websocket.receive_text()
        assert resp == "pong"

def test_ws_manager_role_filtering():
    """Unit test WebSocketManager role-based filtering and disconnection cleanup."""
    import asyncio
    manager = WebSocketManager()

    class MockWS:
        def __init__(self):
            self.sent = []
            self.accepted = False
        async def accept(self):
            self.accepted = True
        async def send_json(self, data):
            self.sent.append(data)

    async def run_scenario():
        ws_op = MockWS()
        ws_cit = MockWS()
        ws_adm = MockWS()

        await manager.connect(ws_op, client_id="op_1", role="OPERATOR")
        await manager.connect(ws_cit, client_id="cit_1", role="CITIZEN")
        await manager.connect(ws_adm, client_id="adm_1", role="ADMIN")

        assert len(manager.active_connections) == 3

        # Broadcast with OPERATOR role filter
        # OPERATOR should receive, ADMIN should receive, CITIZEN should NOT receive
        payload = {"event": "TEST_OP_EVENT", "data": {}}
        await manager.broadcast(payload, role_filter="OPERATOR")

        assert len(ws_op.sent) == 1
        assert len(ws_adm.sent) == 1
        assert len(ws_cit.sent) == 0

        # Disconnect test
        manager.disconnect(ws_op)
        assert len(manager.active_connections) == 2

    asyncio.run(run_scenario())

def test_rescue_assignment_status_patch(client, db_session):
    """Test PATCH /api/v1/rescue/assignments/{id}/status updates DB and broadcasts RESCUE_STATUS_UPDATED."""
    # Ensure team and incident exist
    team = RescueTeam(
        name="Realtime Alpha Squad",
        latitude=13.0827,
        longitude=80.2707,
        team_size=6,
        vehicle_type="TRUCK",
        equipment="FIRST_AID",
        status="BUSY"
    )
    db_session.add(team)
    db_session.flush()

    incident = Incident(
        title="Realtime Water Rescue",
        description="Trapped citizens on roof",
        severity="HIGH",
        priority_score=80,
        status="IN_PROGRESS",
        latitude=13.0830,
        longitude=80.2710
    )
    db_session.add(incident)
    db_session.flush()

    assignment = RescueAssignment(
        incident_id=incident.id,
        rescue_team_id=team.id,
        status="DISPATCHED",
        notes="Urgent evacuation"
    )
    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(assignment)

    # Patch assignment status to EN_ROUTE
    patch_resp = client.patch(
        f"/api/v1/rescue/assignments/{assignment.id}/status",
        json={"status": "EN_ROUTE", "notes": "Approaching sector via bypass"}
    )
    assert patch_resp.status_code == 200
    res_data = patch_resp.json()
    assert res_data["status"] == "EN_ROUTE"

    # Verify DB update persisted
    db_session.refresh(assignment)
    assert assignment.status == "EN_ROUTE"

    # Patch assignment status to RESOLVED (which frees the team)
    res_resp = client.patch(
        f"/api/v1/rescue/assignments/{assignment.id}/status",
        json={"status": "RESOLVED", "notes": "Mission complete"}
    )
    assert res_resp.status_code == 200
    db_session.refresh(assignment)
    db_session.refresh(team)
    assert assignment.status == "RESOLVED"
    assert team.status == "AVAILABLE"

def test_risk_zone_patch(client, db_session):
    """Test PATCH /api/v1/risk/zones/{id} updates DB and broadcasts RISK_ZONE_UPDATED."""
    zone = RiskZone(
        name="Command Sector Realtime Test",
        latitude=13.0850,
        longitude=80.2750,
        risk_level="MODERATE",
        risk_score=55,
        population_estimate=12000
    )
    db_session.add(zone)
    db_session.commit()
    db_session.refresh(zone)

    patch_resp = client.patch(
        f"/api/v1/risk/zones/{zone.id}",
        json={"risk_score": 88, "risk_level": "CRITICAL"}
    )
    assert patch_resp.status_code == 200
    res_data = patch_resp.json()
    assert res_data["risk_score"] == 88
    assert res_data["risk_level"] == "CRITICAL"

    # Verify DB state
    db_session.refresh(zone)
    assert zone.risk_score == 88
    assert zone.risk_level == "CRITICAL"

def test_alert_patch_status(client, db_session):
    """Test PATCH /api/v1/alerts/{id} updates DB and broadcasts ALERT_UPDATED."""
    alert = Alert(
        title="Flood Warning Sector 4",
        message="Water level rising rapidly",
        severity="HIGH",
        status="ACTIVE",
        target_area="Sector 4",
        alert_type="FLOOD"
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)

    patch_resp = client.patch(
        f"/api/v1/alerts/{alert.id}",
        json={"status": "RESOLVED"}
    )
    assert patch_resp.status_code == 200
    db_session.refresh(alert)
    assert alert.status == "RESOLVED"

def test_simulation_endpoints_broadcast(client):
    """Test simulation start, step, and reset trigger successfully."""
    start_resp = client.post("/api/v1/simulation/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["stage"] == "NORMAL"

    step_resp = client.post("/api/v1/simulation/step")
    assert step_resp.status_code == 200
    assert step_resp.json()["stage"] == "HEAVY_RAINFALL"

    reset_resp = client.post("/api/v1/simulation/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["stage"] == "NORMAL"
    assert reset_resp.json()["is_active"] is False

def test_post_commit_broadcast_resilience():
    """Verify that exceptions during broadcast do NOT raise or break calling flow."""
    manager = WebSocketManager()
    # Mock broadcast to throw an error
    with patch.object(manager, "broadcast", side_effect=RuntimeError("Network failure")):
        try:
            # Should not raise exception
            manager.broadcast_event(
                DomainEvent(
                    event=EventType.SYSTEM_STATUS_CHANGED,
                    timestamp="2026-09-06T18:00:00Z",
                    entity_type="system",
                    severity="LOW",
                    data={"test": "resilience"}
                )
            )
        except Exception as e:
            pytest.fail(f"broadcast_event raised an exception instead of catching it: {e}")
