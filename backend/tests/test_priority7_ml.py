import os
import json
import pytest
from app.ml.prediction_service import ml_service
from app.ml.risk_engine import risk_engine

def test_model_registry_loaded():
    assert ml_service.is_loaded is True
    assert ml_service.registry.get('registry_version') == '2.0'
    active = ml_service.registry.get('active_models', {})
    assert active.get('rainfall_classifier') == 'rainfall_classifier_v2'
    assert active.get('rainfall_regressor') == 'rainfall_regressor_v2'
    assert active.get('flood_classifier') == 'flood_classifier_v1'
    assert active.get('flood_depth_regressor') == 'flood_depth_regressor_v1'

def test_model_provenance_separation():
    models = ml_service.registry.get('models', {})
    r_clf = models.get('rainfall_classifier_v2', {})
    assert r_clf.get('data_source_type') == 'historical_real'
    assert r_clf.get('version') == 'v2.0-real-data'
    assert 'ECMWF ERA5-Land' in r_clf.get('scientific_disclaimer', '')
    assert 'dangerous_event_recall' in r_clf.get('metrics', {})
    f_clf = models.get('flood_classifier_v1', {})
    assert f_clf.get('data_source_type') == 'synthetic_prototype'
    assert f_clf.get('version') == 'v1.0-prototype'
    assert 'prototype' in f_clf.get('scientific_disclaimer', '').lower()

def test_risk_engine_decomposition_and_alerts():
    crit = risk_engine.calculate_risk_score(
        rainfall_mm=220.0,
        flood_prob=0.92,
        water_depth_m=1.8,
        population_density=18000
    )
    assert crit['risk_score'] >= 76
    assert crit['risk_level'] == 'CRITICAL'
    assert crit['alert_level'] == 'CRITICAL_WARNING'
    assert 'CRITICAL WARNING' in crit['alert_recommendation']
    assert len(crit['top_drivers']) == 3
    assert crit['breakdown']['rainfall_weight_pct'] == 40
    assert crit['breakdown']['flood_weight_pct'] == 40
    assert crit['breakdown']['exposure_weight_pct'] == 20

    low = risk_engine.calculate_risk_score(
        rainfall_mm=8.0,
        flood_prob=0.04,
        water_depth_m=0.0,
        population_density=1200
    )
    assert low['risk_score'] <= 25
    assert low['risk_level'] == 'LOW'
    assert low['alert_level'] == 'MONITOR'

def test_rainfall_prediction_api(client):
    payload = {
        'location': 'North Basin Coastal',
        'historical_rainfall_24h': 140.0,
        'humidity': 90.0,
        'temperature': 25.0,
        'pressure': 994.0,
        'wind_speed': 42.0,
        'forecast_horizon_hours': 6
    }
    response = client.post('/api/v1/predictions/rainfall', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['predicted_rainfall_mm'] >= 0.0
    assert 0.0 <= data['confidence'] <= 1.0
    assert data['risk_level'] in ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']
    assert data['model_version'] == 'v2.0-real-data'
    assert data['data_source_type'] == 'historical_real'
    assert data['training_dataset'] == 'historical_weather_chennai_2022_2024.csv'
    assert len(data['top_contributors']) == 3
    assert 'feature' in data['top_contributors'][0]
    assert 'importance_pct' in data['top_contributors'][0]

def test_flood_prediction_api(client):
    payload = {
        'location': 'Riverside Lowland',
        'rainfall_intensity_mm_h': 48.0,
        'cumulative_rainfall_24h': 190.0,
        'elevation_m': 8.0,
        'slope_deg': 1.2,
        'drainage_proximity_m': 80.0,
        'soil_saturation_pct': 85.0
    }
    response = client.post('/api/v1/predictions/flood', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data['flood_probability'] <= 1.0
    assert data['estimated_water_depth_m'] >= 0.0
    assert data['model_version'] == 'v1.0-prototype'
    assert data['data_source_type'] == 'synthetic_prototype'
    assert data['risk_breakdown'] is not None
    assert data['alert_recommendation'] is not None
    assert len(data['top_drivers']) >= 2
    assert 'prototype' in data['disclaimer'].lower()

def test_models_metrics_api(client):
    response = client.get('/api/v1/predictions/models/metrics')
    assert response.status_code == 200
    data = response.json()
    assert data['registry_version'] == '2.0'
    assert 'active_models' in data
    assert 'rainfall_classifier_v2' in data['models']
    assert 'flood_classifier_v1' in data['models']
