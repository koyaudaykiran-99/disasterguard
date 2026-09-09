import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock
from app.services.weather_provider import (
    NormalizedWeatherData,
    RealWeatherProvider,
    MockWeatherProvider,
    WeatherProviderError,
    get_weather_provider,
    WMO_CODE_MAP
)
from app.services.weather_service import weather_service
from app.database.models.weather import WeatherObservation
from app.services.prediction_service import prediction_service, ACADEMIC_DISCLAIMER

def test_normalized_weather_data_validation():
    """Verify validation and defaults of NormalizedWeatherData."""
    data = NormalizedWeatherData(
        latitude=13.0827,
        longitude=80.2707,
        rainfall_1h=5.2,
        temperature=31.0,
        humidity=75.0,
        wind_speed=14.0,
        pressure=1008.0,
        condition="Thunderstorm",
        source="real"
    )
    assert data.latitude == 13.0827
    assert data.longitude == 80.2707
    assert data.rainfall_1h == 5.2
    assert data.source == "real"
    assert data.is_demo is False
    assert data.condition == "Thunderstorm"

def test_real_weather_provider_coords_validation():
    """Verify latitude and longitude bounds checking."""
    provider = RealWeatherProvider()
    with pytest.raises(ValueError):
        provider._validate_coords(95.0, 80.0)
    with pytest.raises(ValueError):
        provider._validate_coords(-95.0, 80.0)
    with pytest.raises(ValueError):
        provider._validate_coords(13.0, 190.0)
    with pytest.raises(ValueError):
        provider._validate_coords(13.0, -190.0)
    # Valid coords should not raise
    provider._validate_coords(13.0827, 80.2707)

import asyncio

def test_mock_weather_provider():
    """Verify deterministic mock provider output."""
    mock_prov = MockWeatherProvider(base_rain=15.0, condition="Moderate Rain")
    obs = asyncio.run(mock_prov.get_current_weather(13.0827, 80.2707))
    assert obs.source == "mock"
    assert obs.is_demo is True
    assert obs.rainfall_1h == 15.0
    assert obs.condition == "Moderate Rain"
    
    forecast = asyncio.run(mock_prov.get_forecast(13.0827, 80.2707, hours=12))
    assert len(forecast) == 12
    assert forecast[0]["precipitation_mm"] > 0

def test_weather_caching_logic(db_session):
    """Test that fresh DB observations are served from cache and reduce provider queries."""
    # Seed a recent observation
    test_obs = WeatherObservation(
        location="Test Station Alpha",
        latitude=13.0827,
        longitude=80.2707,
        rainfall_1h=12.0,
        rainfall_3h=25.0,
        rainfall_6h=40.0,
        rainfall_24h=65.0,
        temperature=29.0,
        humidity=80.0,
        wind_speed=15.0,
        pressure=1007.0,
        condition="Slight rain showers",
        source="real",
        precipitation_probability=85.0,
        observed_at=datetime.now(timezone.utc)
    )
    db_session.add(test_obs)
    db_session.commit()
    db_session.refresh(test_obs)

    # Fetch weather via weather_service
    res = asyncio.run(weather_service.get_current_weather(db_session, "Test Station Alpha", 13.0827, 80.2707))
    assert res["id"] == test_obs.id
    assert res["source"] in ("real", "cached")
    assert res["rainfall_1h"] == 12.0
    assert res["is_demo"] is False

def test_weather_provider_error_resilience(db_session):
    """Test graceful fallback when external provider raises an exception."""
    with patch("app.services.weather_service.get_weather_provider") as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.get_current_weather.side_effect = WeatherProviderError("API Rate Limited / Network Down")
        mock_factory.return_value = mock_provider

        # Even with provider failure, it must return a valid cached observation and not raise
        res = asyncio.run(weather_service.get_current_weather(db_session, "Fault Tolerance Area", 13.0827, 80.2707))
        assert res is not None
        assert "rainfall_1h" in res
        assert "temperature" in res

def test_api_weather_current_endpoint(client):
    """Test GET /api/v1/weather/current."""
    resp = client.get("/api/v1/weather/current?latitude=13.0827&longitude=80.2707")
    assert resp.status_code == 200
    data = resp.json()
    assert "rainfall_1h" in data
    assert "rainfall_24h" in data
    assert "temperature" in data
    assert "condition" in data
    assert "source" in data

def test_api_weather_history_endpoint(client):
    """Test GET /api/v1/weather/history."""
    resp = client.get("/api/v1/weather/history?limit=5&hours=24")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "observed_at" in data[0]
        assert "source" in data[0]

def test_api_weather_forecast_endpoint(client):
    """Test GET /api/v1/weather/forecast."""
    resp = client.get("/api/v1/weather/forecast?hours=12")
    assert resp.status_code == 200
    data = resp.json()
    assert "predicted_rainfall_mm" in data
    assert "risk_level" in data
    assert data["forecast_horizon_hours"] == 12

def test_ml_prediction_with_live_weather_and_disclaimer(db_session):
    """Test that ML models consume live weather observation and return academic disclaimer."""
    # Seed a high rainfall observation
    test_obs = WeatherObservation(
        location="Chennai Central",
        latitude=13.0827,
        longitude=80.2707,
        rainfall_1h=45.0,
        rainfall_3h=70.0,
        rainfall_6h=95.0,
        rainfall_24h=140.0,
        temperature=25.0,
        humidity=92.0,
        wind_speed=35.0,
        pressure=996.0,
        condition="Heavy rain",
        source="real",
        observed_at=datetime.now(timezone.utc)
    )
    db_session.add(test_obs)
    db_session.commit()

    # Predict rainfall
    r_pred = prediction_service.predict_rainfall(db_session, {"location": "Chennai Central"})
    assert "predicted_rainfall_mm" in r_pred
    assert "live_weather_db" in r_pred["data_source"]
    assert r_pred["disclaimer"] == ACADEMIC_DISCLAIMER

    # Predict flood
    f_pred = prediction_service.predict_flood(db_session, {"location": "Chennai Central"})
    assert "flood_probability" in f_pred
    assert "estimated_water_depth_m" in f_pred
    assert "live_weather_db" in f_pred["data_source"]
    assert f_pred["disclaimer"] is not None and len(f_pred["disclaimer"]) > 0

