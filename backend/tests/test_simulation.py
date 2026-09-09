from app.database.models.weather import WeatherObservation
from app.database.models.prediction import RainfallPrediction, FloodPrediction
from app.database.models.risk import RiskZone
from app.database.models.alert import Alert
from app.database.models.sos import SOSReport
from app.database.models.incident import Incident
from app.database.models.rescue import RescueAssignment, RescueTeam

def test_simulation_8_stages_and_database(client, db_session):
    # Ensure baseline rescue teams and risk zones exist in test db
    if db_session.query(RescueTeam).count() == 0:
        team = RescueTeam(
            name="Water Rescue Squad Alpha (Boat 1)",
            latitude=13.0800,
            longitude=80.2720,
            team_size=8,
            vehicle_type="MOTORIZED_RESCUE_BOAT",
            equipment="LIFE_JACKETS,RIVER_BOAT,FIRST_AID",
            status="AVAILABLE"
        )
        db_session.add(team)
        db_session.commit()

    if db_session.query(RiskZone).count() == 0:
        zone = RiskZone(
            name="Riverside Lowland Sector Alpha",
            latitude=13.0827,
            longitude=80.2707,
            risk_level="LOW",
            risk_score=18,
            population_estimate=18500
        )
        db_session.add(zone)
        db_session.commit()

    # -------------------------------------------------------------------------
    # STEP 1: NORMAL
    # -------------------------------------------------------------------------
    start_resp = client.post("/api/v1/simulation/start")
    assert start_resp.status_code == 200
    start_data = start_resp.json()
    assert start_data["is_active"] is True
    assert start_data["step"] == 1
    assert start_data["stage"] == "NORMAL"
    assert start_data["risk_score"] == 18
    assert start_data["risk_level"] == "LOW"

    # DB Verification: Step 1
    base_obs = db_session.query(WeatherObservation).filter(
        WeatherObservation.location.like("%[SIMULATION]%")
    ).first()
    assert base_obs is not None
    assert base_obs.rainfall_24h == 12.5

    # -------------------------------------------------------------------------
    # STEP 2: HEAVY RAINFALL
    # -------------------------------------------------------------------------
    step2_resp = client.post("/api/v1/simulation/step")
    assert step2_resp.status_code == 200
    step2_data = step2_resp.json()
    assert step2_data["step"] == 2
    assert step2_data["stage"] == "HEAVY_RAINFALL"
    assert step2_data["risk_score"] == 45
    assert step2_data["metrics"]["rainfall_1h"] == 55.0
    assert step2_data["metrics"]["rainfall_24h"] == 110.0
    assert step2_data["metrics"]["pressure"] == 993.0

    # DB Verification: Step 2
    heavy_obs = db_session.query(WeatherObservation).filter(
        WeatherObservation.rainfall_1h == 55.0
    ).first()
    assert heavy_obs is not None
    assert heavy_obs.pressure == 993.0

    # -------------------------------------------------------------------------
    # STEP 3: AI ANALYSIS
    # -------------------------------------------------------------------------
    step3_resp = client.post("/api/v1/simulation/step")
    assert step3_resp.status_code == 200
    step3_data = step3_resp.json()
    assert step3_data["step"] == 3
    assert step3_data["stage"] == "AI_ANALYSIS"
    assert step3_data["risk_score"] == 68
    assert step3_data["risk_level"] == "HIGH"

    # DB Verification: Step 3
    rain_pred = db_session.query(RainfallPrediction).filter(
        RainfallPrediction.location.like("%[SIMULATION]%")
    ).first()
    assert rain_pred is not None
    flood_pred = db_session.query(FloodPrediction).filter(
        FloodPrediction.location.like("%[SIMULATION]%")
    ).first()
    assert flood_pred is not None

    # -------------------------------------------------------------------------
    # STEP 4: FLOOD RISK INCREASE
    # -------------------------------------------------------------------------
    step4_resp = client.post("/api/v1/simulation/step")
    assert step4_resp.status_code == 200
    step4_data = step4_resp.json()
    assert step4_data["step"] == 4
    assert step4_data["stage"] == "FLOOD_RISK_INCREASE"
    assert step4_data["risk_score"] == 72
    assert step4_data["risk_level"] == "HIGH"

    # DB Verification: Step 4
    zone_step4 = db_session.query(RiskZone).first()
    assert zone_step4.risk_score == 72

    # -------------------------------------------------------------------------
    # STEP 5: CRITICAL RISK
    # -------------------------------------------------------------------------
    step5_resp = client.post("/api/v1/simulation/step")
    assert step5_resp.status_code == 200
    step5_data = step5_resp.json()
    assert step5_data["step"] == 5
    assert step5_data["stage"] == "CRITICAL_RISK"
    assert step5_data["risk_score"] == 90
    assert step5_data["risk_level"] == "CRITICAL"

    # DB Verification: Step 5
    zone_step5 = db_session.query(RiskZone).first()
    assert zone_step5.risk_score == 90
    assert zone_step5.risk_level == "CRITICAL"

    # -------------------------------------------------------------------------
    # STEP 6: ALERT
    # -------------------------------------------------------------------------
    step6_resp = client.post("/api/v1/simulation/step")
    assert step6_resp.status_code == 200
    step6_data = step6_resp.json()
    assert step6_data["step"] == 6
    assert step6_data["stage"] == "ALERT"

    # DB Verification: Step 6
    sim_alert = db_session.query(Alert).filter(
        Alert.title.like("%[SIMULATION]%")
    ).first()
    assert sim_alert is not None
    assert sim_alert.severity == "CRITICAL"
    assert sim_alert.status == "ACTIVE"

    # -------------------------------------------------------------------------
    # STEP 7: SOS / INCIDENT
    # -------------------------------------------------------------------------
    step7_resp = client.post("/api/v1/simulation/step")
    assert step7_resp.status_code == 200
    step7_data = step7_resp.json()
    assert step7_data["step"] == 7
    assert step7_data["stage"] == "SOS_INCIDENT"

    # DB Verification: Step 7
    sim_sos = db_session.query(SOSReport).filter(
        SOSReport.message.like("%[SIMULATION]%")
    ).first()
    assert sim_sos is not None
    assert sim_sos.severity == "CRITICAL"

    sim_inc = db_session.query(Incident).filter(
        Incident.sos_id == sim_sos.id
    ).first()
    assert sim_inc is not None
    assert sim_inc.severity == "CRITICAL"
    assert sim_inc.priority_score >= 90

    # -------------------------------------------------------------------------
    # STEP 8: RESCUE RECOMMENDATION
    # -------------------------------------------------------------------------
    step8_resp = client.post("/api/v1/simulation/step")
    assert step8_resp.status_code == 200
    step8_data = step8_resp.json()
    assert step8_data["step"] == 8
    assert step8_data["stage"] == "RESCUE_RECOMMENDATION"
    assert step8_data["simulation_complete"] is True

    # DB Verification: Step 8
    sim_assign = db_session.query(RescueAssignment).filter(
        RescueAssignment.incident_id == sim_inc.id
    ).first()
    assert sim_assign is not None
    assert sim_assign.status == "DISPATCHED"

    # Check status endpoint
    status_resp = client.get("/api/v1/simulation/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["step"] == 8
    assert status_resp.json()["simulation_complete"] is True

    # -------------------------------------------------------------------------
    # RESET
    # -------------------------------------------------------------------------
    reset_resp = client.post("/api/v1/simulation/reset")
    assert reset_resp.status_code == 200
    reset_data = reset_resp.json()
    assert reset_data["is_active"] is False
    assert reset_data["step"] == 0
    assert reset_data["simulation_complete"] is False

    # DB Verification: Reset cleanup
    assert db_session.query(Alert).filter(Alert.title.like("%[SIMULATION]%")).count() == 0
    assert db_session.query(SOSReport).filter(SOSReport.message.like("%[SIMULATION]%")).count() == 0
    assert db_session.query(Incident).filter(Incident.title.like("%[SIMULATION]%")).count() == 0
    assert db_session.query(RescueAssignment).filter(RescueAssignment.notes.like("%[SIMULATION]%")).count() == 0
    assert db_session.query(WeatherObservation).filter(WeatherObservation.location.like("%[SIMULATION]%")).count() == 0
    assert db_session.query(RainfallPrediction).filter(RainfallPrediction.location.like("%[SIMULATION]%")).count() == 0
    assert db_session.query(FloodPrediction).filter(FloodPrediction.location.like("%[SIMULATION]%")).count() == 0
