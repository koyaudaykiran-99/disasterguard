from app.ml.risk_engine import risk_engine

def test_risk_score_critical():
    res = risk_engine.calculate_risk_score(
        rainfall_mm=210.0,
        flood_prob=0.95,
        water_depth_m=1.8,
        population_density=18000,
        historical_vulnerability=0.9
    )
    assert res["risk_score"] >= 76
    assert res["risk_level"] == "CRITICAL"

def test_risk_score_high():
    res = risk_engine.calculate_risk_score(
        rainfall_mm=130.0,
        flood_prob=0.65,
        water_depth_m=0.8,
        population_density=10000,
        historical_vulnerability=0.6
    )
    assert 51 <= res["risk_score"] <= 75
    assert res["risk_level"] == "HIGH"

def test_risk_score_moderate():
    res = risk_engine.calculate_risk_score(
        rainfall_mm=60.0,
        flood_prob=0.35,
        water_depth_m=0.3,
        population_density=5000,
        historical_vulnerability=0.4
    )
    assert 26 <= res["risk_score"] <= 50
    assert res["risk_level"] == "MODERATE"

def test_risk_score_low():
    res = risk_engine.calculate_risk_score(
        rainfall_mm=10.0,
        flood_prob=0.05,
        water_depth_m=0.0,
        population_density=1000,
        historical_vulnerability=0.1
    )
    assert res["risk_score"] <= 25
    assert res["risk_level"] == "LOW"
