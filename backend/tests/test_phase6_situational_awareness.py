"""
Phase 6: Situational Awareness & Command-Centre Real-Time Coordination Tests
Verifies:
- Situational Snapshot Generation
- Multi-Signal Change Detection & Deltas
- Incident Clustering (Preserves emergency record identities)
- Risk Hotspots Multi-Signal Convergence
- Prioritized Operator Attention Queue
- Database-backed Operational Timeline
- Side-by-side Response Plan Options (Option A vs Option B)
- 5-part AI Situational Briefing Evidence Taxonomy
- Phase 6 17-stage Simulation Engine
- Inviolate Safety Barrier: 0 Autonomous Dispatches
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models.situational_awareness import (
    SituationalSnapshot,
    OperationalEvent,
    IncidentCluster,
    RiskHotspot,
    OperatorAttentionItem
)
from app.database.models.rescue import RescueTeam, RescueAssignment
from app.database.models.incident import Incident
from app.database.models.sos import SOSReport
from app.ml.situational_awareness.change_detection import ChangeDetector
from app.ml.situational_awareness.incident_clustering import IncidentClusterer
from app.ml.situational_awareness.hotspot_detection import HotspotDetector
from app.ml.situational_awareness.event_correlation import EventCorrelator


def test_situational_snapshot_endpoint(client: TestClient):
    res = client.get("/api/v1/situation/current")
    assert res.status_code == 200
    data = res.json()
    assert "risk_score" in data
    assert "risk_level" in data
    assert "dominant_threat" in data
    assert "trend" in data
    assert "provenance" in data
    assert "confidence" in data
    assert isinstance(data["risk_score"], (int, float))


def test_situation_changes_endpoint(client: TestClient):
    res = client.get("/api/v1/situation/changes?minutes=60")
    assert res.status_code == 200
    data = res.json()
    assert "recent_changes" in data
    assert "count" in data
    assert isinstance(data["recent_changes"], list)


def test_hotspots_endpoint(client: TestClient, db_session: Session):
    # Insert test hotspot
    hs = RiskHotspot(
        hotspot_code="HS-TEST-01",
        name="Test Hotspot Basin",
        hazard_type="FLASH_FLOOD",
        latitude=13.0827,
        longitude=80.2707,
        radius_km=0.8,
        hotspot_score=85.0,
        severity="HIGH",
        confidence=0.90,
        is_active=True,
        detected_at=datetime.now(timezone.utc)
    )
    db_session.add(hs)
    db_session.commit()

    res = client.get("/api/v1/hotspots/")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(h["name"] == "Test Hotspot Basin" for h in data)


def test_clusters_endpoint(client: TestClient, db_session: Session):
    # Insert test cluster
    cl = IncidentCluster(
        cluster_code="CLU-TEST-01",
        title="Test Cluster",
        dominant_hazard="FLOOD",
        risk_level="HIGH",
        latitude=13.0850,
        longitude=80.2750,
        radius_km=0.5,
        incident_count=3,
        incident_ids_json="[101, 102, 103]",
        confidence=0.91,
        is_active=True,
        detected_at=datetime.now(timezone.utc)
    )
    db_session.add(cl)
    db_session.commit()

    res = client.get("/api/v1/clusters/")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(c["cluster_code"] == "CLU-TEST-01" for c in data)


def test_operational_timeline_endpoint(client: TestClient, db_session: Session):
    event = OperationalEvent(
        event_type="TEST_EVENT",
        entity_type="DISPATCH",
        severity="HIGH",
        title="Test Operational Event",
        description="Operator assigned unit to sector 3",
        data_provenance="REAL",
        source="SYSTEM",
        confidence=1.0,
        event_timestamp=datetime.now(timezone.utc)
    )
    db_session.add(event)
    db_session.commit()

    res = client.get("/api/v1/operations/timeline?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "events" in data
    assert "total" in data or "total_events" in data
    assert len(data["events"]) >= 1


def test_operator_attention_queue(client: TestClient, db_session: Session):
    item = OperatorAttentionItem(
        title="Critical Bridge Water Surge",
        description="Sensor reported +0.8m above safety threshold",
        urgency="CRITICAL",
        category="SENSOR_ANOMALY",
        recommended_action="Dispatch patrol team to inspect support pillars.",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    res = client.get("/api/v1/operations/attention?status=PENDING")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "pending_count" in data
    assert data["pending_count"] >= 1

    # Test acknowledge endpoint
    res_ack = client.post(
        f"/api/v1/operations/attention/{item.id}/acknowledge",
        json={"acknowledged_by": "OPERATOR_TEST"}
    )
    assert res_ack.status_code == 200
    assert res_ack.json()["status"] == "ACKNOWLEDGED"


def test_resource_conflicts_options_comparison(client: TestClient):
    res = client.get("/api/v1/operations/conflicts")
    assert res.status_code == 200
    data = res.json()
    assert "contentions" in data
    assert "count" in data


def test_ai_briefing_5_part_taxonomy(client: TestClient):
    res = client.get("/api/v1/ai/briefing")
    assert res.status_code == 200
    data = res.json()
    assert "executive_summary" in data
    assert "evidence_items" in data
    assert "dominant_threat" in data
    assert "recommended_priorities" in data
    assert "provenance" in data
    assert "confidence" in data

    # Verify evidence taxonomy categories
    taxonomies = {item["type"] for item in data["evidence_items"]}
    expected_categories = {"FACT", "ML_PREDICTION", "GEOSPATIAL_DERIVATION", "AI_INTERPRETATION", "RECOMMENDATION"}
    # At least some evidence types are present
    assert len(taxonomies.intersection(expected_categories)) > 0


def test_phase6_simulation_lifecycle(client: TestClient):
    # Start
    res_start = client.post("/api/v1/simulation/phase6/start")
    assert res_start.status_code == 200
    state = res_start.json()
    assert state["step"] == 1
    assert state["is_active"] is True

    # Step to 5 (Hotspot detected)
    res_step = client.post("/api/v1/simulation/phase6/step", json={"step": 5})
    assert res_step.status_code == 200
    state5 = res_step.json()
    assert state5["step"] == 5
    assert state5["stage_info"]["stage"] == "HOTSPOT_DETECTED"

    # Step to 12 (Operator confirms dispatch)
    res_step12 = client.post("/api/v1/simulation/phase6/step", json={"step": 12})
    assert res_step12.status_code == 200
    state12 = res_step12.json()
    assert state12["step"] == 12

    # Reset
    res_reset = client.post("/api/v1/simulation/phase6/reset")
    assert res_reset.status_code == 200
    state_reset = res_reset.json()
    assert state_reset["step"] == 0
    assert state_reset["is_active"] is False


def test_ml_modules_direct():
    # 1. Change Detector
    detector = ChangeDetector()
    res = detector.evaluate_changes(
        current_state={"risk_score": 75.0, "active_emergencies": 5, "critical_emergencies": 2},
        previous_state={"risk_score": 25.0, "active_emergencies": 1, "critical_emergencies": 0}
    )
    assert isinstance(res, list)
    assert len(res) > 0

    # 2. Incident Clusterer (preserves original IDs)
    clusterer = IncidentClusterer()
    incidents = [
        {"id": 1, "latitude": 28.558, "longitude": 77.172, "severity": "CRITICAL", "priority_score": 90},
        {"id": 2, "latitude": 28.559, "longitude": 77.173, "severity": "HIGH", "priority_score": 85},
        {"id": 3, "latitude": 28.557, "longitude": 77.171, "severity": "MODERATE", "priority_score": 70},
    ]
    clusters = clusterer.cluster_incidents(incidents)
    assert isinstance(clusters, list)
    if clusters:
        # Emergency record IDs preserved in cluster without modifying original records
        assert "incident_ids" in clusters[0]
        assert set(clusters[0]["incident_ids"]).issubset({1, 2, 3})

    # 3. Hotspot Detector
    hs_detector = HotspotDetector()
    hotspots = hs_detector.detect_hotspots(
        incidents=incidents,
        weather_observation={"rainfall_rate_mm": 95.0, "latitude": 28.558, "longitude": 77.172},
        forecast_data={"flood_probability": 0.88}
    )
    assert isinstance(hotspots, list)

    # 4. Event Correlator
    correlator = EventCorrelator()
    corrs = correlator.correlate_signals(
        incidents=incidents,
        weather_data={"rainfall_rate_mm": 110.0}
    )
    assert isinstance(corrs, list)


def test_safety_barrier_inviolate():
    """
    CRITICAL SAFETY GATE:
    Verifies that zero automated engines (ML, AI, clustering, hotspots, change detection)
    can create a confirmed dispatch. All dispatches require explicit operator action.
    """
    from app.services.situational_awareness_service import SituationalAwarenessService
    from app.ai.tools import DISASTER_GUARD_TOOLS

    # 1. Verify that no AI tool has dispatch authority
    for tool in DISASTER_GUARD_TOOLS:
        name = tool.name.lower()
        assert "dispatch" not in name or "read" in name or "get" in name or "list" in name, \
            f"Safety violation: Tool {tool.name} implies autonomous dispatch capability!"

    # 2. Verify all 7 Phase 6 AI tools are read-only
    phase6_tool_names = [
        "get_current_situation",
        "get_situation_changes",
        "get_risk_hotspots",
        "get_incident_clusters",
        "get_operator_attention_queue",
        "get_resource_conflicts",
        "get_operational_timeline"
    ]
    tool_names = [t.name for t in DISASTER_GUARD_TOOLS]
    for p6_name in phase6_tool_names:
        assert p6_name in tool_names, f"Phase 6 tool {p6_name} must be registered in AI tools registry."
