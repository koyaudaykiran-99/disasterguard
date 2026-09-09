import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.config import settings
from app.database.models.weather import WeatherObservation
from app.services.weather_provider import (
    get_weather_provider,
    MockWeatherProvider,
    NormalizedWeatherData,
    WeatherProviderError
)
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType

logger = logging.getLogger("disasterguard.weather")

class WeatherService:
    async def get_current_weather(
        self,
        db: Session,
        location: str = "Central Metro Basin",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fetch current weather observation with caching.
        Checks PostgreSQL cache first (valid for WEATHER_CACHE_MINUTES).
        If stale or absent, queries external weather provider, persists, and returns.
        On network/provider failure, gracefully falls back to latest cached record.
        """
        lat = latitude if latitude is not None else settings.WEATHER_LATITUDE
        lng = longitude if longitude is not None else settings.WEATHER_LONGITUDE

        # 1. Check if the latest observation in DB is a recent simulation event
        latest_sim = (
            db.query(WeatherObservation)
            .filter(WeatherObservation.source == "simulation")
            .order_by(desc(WeatherObservation.observed_at))
            .first()
        )
        if latest_sim:
            # Check if simulation event occurred in the last 15 minutes
            sim_cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
            # Safe tz-aware comparison
            sim_time = latest_sim.observed_at
            if sim_time.tzinfo is None:
                sim_time = sim_time.replace(tzinfo=timezone.utc)
            if sim_time >= sim_cutoff:
                return self._to_dict(latest_sim, source="simulation")

        # 2. Check for fresh cached observation within WEATHER_CACHE_MINUTES
        cache_cutoff = datetime.now(timezone.utc) - timedelta(minutes=settings.WEATHER_CACHE_MINUTES)
        cached_obs = (
            db.query(WeatherObservation)
            .filter(
                WeatherObservation.observed_at >= cache_cutoff,
                WeatherObservation.source.in_(["real", "cached"])
            )
            .order_by(desc(WeatherObservation.observed_at))
            .first()
        )

        if cached_obs:
            logger.info(f"Serving cached weather observation id={cached_obs.id} (source={cached_obs.source})")
            return self._to_dict(cached_obs, source="cached")

        # 3. Cache miss: Fetch from configured weather provider
        provider = get_weather_provider()
        try:
            normalized: NormalizedWeatherData = await provider.get_current_weather(
                latitude=lat, longitude=lng, location_name=location
            )
            
            # Persist observation to PostgreSQL
            db_obs = WeatherObservation(
                location=normalized.location,
                latitude=normalized.latitude,
                longitude=normalized.longitude,
                rainfall_1h=normalized.rainfall_1h,
                rainfall_3h=normalized.rainfall_3h,
                rainfall_6h=normalized.rainfall_6h,
                rainfall_24h=normalized.rainfall_24h,
                temperature=normalized.temperature,
                humidity=normalized.humidity,
                wind_speed=normalized.wind_speed,
                pressure=normalized.pressure,
                condition=normalized.condition,
                source=normalized.source,
                precipitation_probability=normalized.precipitation_probability,
                observed_at=normalized.observed_at
            )
            db.add(db_obs)
            db.commit()
            db.refresh(db_obs)

            obs_dict = self._to_dict(db_obs, source=normalized.source)
            try:
                ws_manager.broadcast_event(
                    DomainEvent(
                        event=EventType.WEATHER_UPDATED,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        entity_id=db_obs.id,
                        entity_type="weather_observation",
                        severity="CRITICAL" if (db_obs.rainfall_1h or 0) >= 25 else "HIGH" if (db_obs.rainfall_1h or 0) >= 10 else "LOW",
                        data=obs_dict
                    )
                )
            except Exception as b_err:
                logger.warning(f"Could not broadcast WEATHER_UPDATED: {b_err}")

            logger.info(f"Persisted new real weather observation id={db_obs.id} from {normalized.source}")
            return obs_dict

        except Exception as exc:
            logger.warning(
                f"External weather provider failed: {exc}. Falling back to PostgreSQL cache or mock."
            )
            db.rollback()
            
            # Fallback A: Any existing observation in PostgreSQL
            fallback_obs = (
                db.query(WeatherObservation)
                .order_by(desc(WeatherObservation.observed_at))
                .first()
            )
            if fallback_obs:
                logger.info(f"Using fallback historical observation id={fallback_obs.id}")
                return self._to_dict(fallback_obs, source="cached")

            # Fallback B: Deterministic mock provider
            mock_provider = MockWeatherProvider()
            mock_data = await mock_provider.get_current_weather(latitude=lat, longitude=lng, location_name=location)
            return mock_data.model_dump()

    def get_weather_history(
        self, db: Session, limit: int = 10, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Retrieve recent historical weather observations from PostgreSQL."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        records = (
            db.query(WeatherObservation)
            .filter(WeatherObservation.observed_at >= cutoff)
            .order_by(desc(WeatherObservation.observed_at))
            .limit(limit)
            .all()
        )
        if not records:
            # Fall back to latest records regardless of time window
            records = (
                db.query(WeatherObservation)
                .order_by(desc(WeatherObservation.observed_at))
                .limit(limit)
                .all()
            )
        return [self._to_dict(rec, source=rec.source or "cached") for rec in records]

    async def get_forecast(
        self,
        location: str = "Central Metro Basin",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        hours: int = 6
    ) -> Dict[str, Any]:
        """Generate forecast for location using weather provider."""
        lat = latitude if latitude is not None else settings.WEATHER_LATITUDE
        lng = longitude if longitude is not None else settings.WEATHER_LONGITUDE
        provider = get_weather_provider()
        forecast_items = await provider.get_forecast(latitude=lat, longitude=lng, hours=hours)
        
        predicted_rainfall = sum(item.get("precipitation_mm", 0.0) for item in forecast_items) if forecast_items else 24.5
        risk_level = "HIGH" if predicted_rainfall > 50 else ("MEDIUM" if predicted_rainfall > 20 else "LOW")

        return {
            "location": location,
            "forecast_horizon_hours": hours,
            "predicted_rainfall_mm": round(predicted_rainfall, 2),
            "risk_level": risk_level,
            "temperature": forecast_items[0].get("temperature_c", 28.0) if forecast_items else 28.0,
            "humidity": 78.0,
            "is_demo": settings.WEATHER_PROVIDER != "real",
        }

    def _to_dict(self, obs: WeatherObservation, source: Optional[str] = None) -> Dict[str, Any]:
        actual_source = source or obs.source or "real"
        return {
            "id": obs.id,
            "location": obs.location,
            "latitude": obs.latitude,
            "longitude": obs.longitude,
            "rainfall_1h": round(obs.rainfall_1h or 0.0, 2),
            "rainfall_3h": round(obs.rainfall_3h or 0.0, 2),
            "rainfall_6h": round(obs.rainfall_6h or 0.0, 2),
            "rainfall_24h": round(obs.rainfall_24h or 0.0, 2),
            "temperature": round(obs.temperature, 1) if obs.temperature is not None else 28.0,
            "humidity": round(obs.humidity, 1) if obs.humidity is not None else 65.0,
            "wind_speed": round(obs.wind_speed, 1) if obs.wind_speed is not None else 10.0,
            "pressure": round(obs.pressure, 1) if obs.pressure is not None else 1012.0,
            "condition": obs.condition or "Clear",
            "source": actual_source,
            "precipitation_probability": round(obs.precipitation_probability, 1) if obs.precipitation_probability is not None else 0.0,
            "observed_at": obs.observed_at,
            "is_demo": actual_source not in ("real", "cached")
        }

weather_service = WeatherService()
