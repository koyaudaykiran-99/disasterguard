import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.config import settings
from app.database.models.weather import WeatherObservation
from app.services.weather_provider import (
    weather_provider_manager,
    NormalizedWeatherData,
    WeatherProviderError,
    calculate_alert_level,
    MockWeatherProvider
)
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType

logger = logging.getLogger("disasterguard.weather")


class WeatherService:
    """
    Unified Real-Time Weather & Hydrological Service.
    Powers both Citizen App and Command Center with identical, cached, normalized weather.
    """

    async def get_current_weather(
        self,
        db: Session,
        location: str = "Central Metro Basin",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fetch current weather observation with caching.
        1. Checks PostgreSQL cache (valid for WEATHER_CACHE_MINUTES).
        2. If stale or absent, queries external weather provider cascade (IMD -> OpenWeather -> Open-Meteo).
        3. Persists observation to database.
        4. Broadcasts WebSocket event to connected dashboards.
        5. On provider failure, gracefully falls back to latest cached record without crashing.
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
            sim_cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
            sim_time = latest_sim.observed_at
            if sim_time.tzinfo is None:
                sim_time = sim_time.replace(tzinfo=timezone.utc)
            if sim_time >= sim_cutoff:
                return self._to_dict(latest_sim, source="simulation", is_cached=True)

        # 2. Check for fresh cached observation within WEATHER_CACHE_MINUTES
        cache_minutes = getattr(settings, "WEATHER_CACHE_MINUTES", 3)
        cache_cutoff = datetime.now(timezone.utc) - timedelta(minutes=cache_minutes)
        cached_obs = (
            db.query(WeatherObservation)
            .filter(
                WeatherObservation.observed_at >= cache_cutoff,
                WeatherObservation.source.in_(["real", "cached", "imd", "openweather", "open-meteo"])
            )
            .order_by(desc(WeatherObservation.observed_at))
            .first()
        )

        if cached_obs:
            logger.info(f"Serving cached weather observation id={cached_obs.id} (source={cached_obs.source})")
            return self._to_dict(cached_obs, source=cached_obs.source or "cached", is_cached=True)

        # 3. Cache miss: Fetch from Multi-Source Weather Manager (IMD -> OpenWeather -> Open-Meteo)
        try:
            normalized: NormalizedWeatherData = await weather_provider_manager.get_current_weather(
                latitude=lat, longitude=lng, location_name=location
            )

            # Persist observation to PostgreSQL
            db_obs = WeatherObservation(
                location=normalized.location_name or location,
                latitude=normalized.latitude,
                longitude=normalized.longitude,
                rainfall_1h=normalized.rainfall_1h,
                rainfall_3h=normalized.rainfall_3h,
                rainfall_6h=normalized.rainfall_6h,
                rainfall_24h=normalized.rainfall_24h,
                temperature=normalized.temperature_c,
                humidity=normalized.humidity,
                wind_speed=normalized.wind_speed_kmh,
                pressure=normalized.pressure_hpa,
                condition=normalized.weather_condition,
                source=normalized.provider,
                precipitation_probability=normalized.precipitation_probability,
                observed_at=datetime.now(timezone.utc)
            )
            db.add(db_obs)
            db.commit()
            db.refresh(db_obs)

            obs_dict = self._to_dict(db_obs, source=normalized.provider, is_cached=False)
            obs_dict["provider"] = normalized.provider
            obs_dict["rain_probability"] = normalized.rain_probability
            obs_dict["visibility_km"] = normalized.visibility_km
            obs_dict["alert_level"] = normalized.alert_level
            obs_dict["alerts"] = normalized.alerts
            obs_dict["official_warnings"] = normalized.official_warnings
            obs_dict["data_freshness"] = "Updated just now"

            # Broadcast real-time update over WebSocket
            try:
                ws_manager.broadcast_event(
                    DomainEvent(
                        event=EventType.WEATHER_UPDATED,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        entity_id=db_obs.id,
                        entity_type="weather_observation",
                        severity=normalized.alert_level,
                        data=obs_dict
                    )
                )
            except Exception as b_err:
                logger.warning(f"Could not broadcast WEATHER_UPDATED: {b_err}")

            logger.info(f"Persisted new real weather observation id={db_obs.id} from provider={normalized.provider}")
            return obs_dict

        except Exception as exc:
            logger.warning(
                f"External weather providers failed: {exc}. Falling back to PostgreSQL cache or mock."
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
                return self._to_dict(fallback_obs, source="cached", is_cached=True)

            # Fallback B: Deterministic mock provider
            mock_provider = MockWeatherProvider()
            mock_data = await mock_provider.get_current_weather(latitude=lat, longitude=lng, location_name=location)
            res = mock_data.model_dump()
            res["data_freshness"] = "Offline Fallback Sensor"
            return res

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
            records = (
                db.query(WeatherObservation)
                .order_by(desc(WeatherObservation.observed_at))
                .limit(limit)
                .all()
            )
        return [self._to_dict(rec, source=rec.source or "cached", is_cached=True) for rec in records]

    async def get_forecast(
        self,
        location: str = "Central Metro Basin",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Generate multi-hour rainfall & temperature trajectory forecast."""
        lat = latitude if latitude is not None else settings.WEATHER_LATITUDE
        lng = longitude if longitude is not None else settings.WEATHER_LONGITUDE

        forecast_items = await weather_provider_manager.get_forecast(latitude=lat, longitude=lng, hours=hours)
        predicted_rainfall = sum(item.get("precipitation_mm", 0.0) for item in forecast_items) if forecast_items else 24.5
        risk_level = "CRITICAL" if predicted_rainfall > 60 else ("HIGH" if predicted_rainfall > 30 else ("MODERATE" if predicted_rainfall > 10 else "LOW"))

        return {
            "provider": weather_provider_manager.active_provider_name,
            "location": {"lat": lat, "lon": lng, "city": location},
            "location_name": location,
            "forecast_horizon_hours": hours,
            "predicted_rainfall_mm": round(predicted_rainfall, 2),
            "risk_level": risk_level,
            "temperature_c": forecast_items[0].get("temperature_c", 28.0) if forecast_items else 28.0,
            "humidity": 78.0,
            "hourly_timeline": forecast_items,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_demo": weather_provider_manager.active_provider_name == "mock",
        }

    async def get_alerts(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location: str = "Central Metro Basin",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Retrieve active meteorological warnings & severe weather alerts."""
        lat = latitude if latitude is not None else settings.WEATHER_LATITUDE
        lng = longitude if longitude is not None else settings.WEATHER_LONGITUDE

        provider_alerts = await weather_provider_manager.get_alerts(lat, lng)

        # Check latest weather observation for high rainfall condition
        heavy_rain_detected = False
        current_rainfall = 0.0
        if db:
            latest = db.query(WeatherObservation).order_by(desc(WeatherObservation.observed_at)).first()
            if latest:
                current_rainfall = float(latest.rainfall_1h or 0.0)
                if current_rainfall >= 20.0:
                    heavy_rain_detected = True

        alerts_list = []
        if heavy_rain_detected:
            alerts_list.append({
                "source": "AI-DisasterGuard Weather Monitor",
                "severity": "CRITICAL" if current_rainfall >= 40 else "HIGH",
                "headline": "Heavy rainfall detected in your area.",
                "instruction": "Flood risk is HIGH. Move to a safe/high-ground area if instructed by authorities.",
                "rainfall_mm": current_rainfall
            })

        for pa in provider_alerts:
            alerts_list.append(pa)

        return {
            "provider": weather_provider_manager.active_provider_name,
            "location": {"lat": lat, "lon": lng, "city": location},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_alerts": len(alerts_list),
            "alerts": alerts_list
        }

    async def get_rainfall_summary(
        self,
        db: Session,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """Detailed rainfall metrics: 1h, 3h, 6h, 12h, 24h accumulation & intensity."""
        current = await self.get_current_weather(db=db, latitude=latitude, longitude=longitude)
        r1h = current.get("rainfall_1h", 0.0)
        r3h = current.get("rainfall_3h", r1h * 2.8)
        r6h = current.get("rainfall_6h", r1h * 5.2)
        r24h = current.get("rainfall_24h", r1h * 14.0)

        intensity_label = (
            "Violent Downpour" if r1h >= 50 else
            "Heavy Rain" if r1h >= 25 else
            "Moderate Rain" if r1h >= 7.5 else
            "Light Rain" if r1h > 0.5 else "Dry / Trace"
        )

        return {
            "provider": current.get("provider", "open-meteo"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": current.get("location", {}),
            "rainfall_current_mm": r1h,
            "rainfall_1h_mm": r1h,
            "rainfall_3h_mm": r3h,
            "rainfall_6h_mm": r6h,
            "rainfall_24h_mm": r24h,
            "intensity_mm_h": r1h,
            "intensity_category": intensity_label,
            "rain_probability": current.get("rain_probability", 0.0),
            "alert_level": current.get("alert_level", "LOW")
        }

    def get_status(self) -> Dict[str, Any]:
        """Provider status monitor for ideathon demo and system diagnostics."""
        has_ow = bool(getattr(settings, "OPENWEATHER_API_KEY", "") or getattr(settings, "WEATHER_API_KEY", ""))
        has_imd = bool(getattr(settings, "IMD_API_KEY", ""))

        return {
            "status": "operational",
            "active_provider": weather_provider_manager.active_provider_name,
            "available_providers": ["imd", "openweather", "open-meteo", "cached", "mock"],
            "configured_keys": {
                "openweather": "configured" if has_ow else "not_configured (cascades to Open-Meteo)",
                "imd": "configured" if has_imd else "public_gateway / fallback"
            },
            "cache_ttl_minutes": getattr(settings, "WEATHER_CACHE_MINUTES", 3),
            "radar_provider": getattr(settings, "RADAR_TILE_PROVIDER", "rainviewer"),
            "coordinates": {
                "latitude": settings.WEATHER_LATITUDE,
                "longitude": settings.WEATHER_LONGITUDE
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _to_dict(self, obs: WeatherObservation, source: Optional[str] = None, is_cached: bool = False) -> Dict[str, Any]:
        actual_source = source or obs.source or "real"
        now = datetime.now(timezone.utc)
        obs_time = obs.observed_at
        if obs_time and obs_time.tzinfo is None:
            obs_time = obs_time.replace(tzinfo=timezone.utc)

        age_seconds = (now - obs_time).total_seconds() if obs_time else 0
        age_minutes = int(age_seconds // 60)

        data_freshness = "Updated just now" if age_minutes < 1 else f"Updated {age_minutes} min ago"
        if is_cached and actual_source == "cached":
            data_freshness = f"Cached {age_minutes} min ago"

        r1h = round(obs.rainfall_1h or 0.0, 2)
        r24h = round(obs.rainfall_24h or (r1h * 14.0), 2)
        temp = round(obs.temperature, 1) if obs.temperature is not None else 28.0
        hum = round(obs.humidity, 1) if obs.humidity is not None else 65.0
        wind = round(obs.wind_speed, 1) if obs.wind_speed is not None else 10.0
        press = round(obs.pressure, 1) if obs.pressure is not None else 1012.0
        cond = obs.condition or "Partly Cloudy"

        prob_raw = float(obs.precipitation_probability or 0.0)
        prob_ratio = round(prob_raw / 100.0, 2) if prob_raw > 1.0 else round(prob_raw, 2)

        alert_lvl = calculate_alert_level(r1h, prob_ratio)

        # Normalize provider name
        provider_name = actual_source
        if provider_name in ("real", "live_weather_db (real)"):
            provider_name = "open-meteo"

        return {
            "id": obs.id,
            "provider": provider_name,
            "timestamp": obs_time.isoformat() if obs_time else now.isoformat(),
            "location": {
                "lat": obs.latitude or settings.WEATHER_LATITUDE,
                "lon": obs.longitude or settings.WEATHER_LONGITUDE,
                "city": obs.location or "Central Metro Basin"
            },
            "location_name": obs.location or "Central Metro Basin",
            "latitude": obs.latitude or settings.WEATHER_LATITUDE,
            "longitude": obs.longitude or settings.WEATHER_LONGITUDE,
            "temperature_c": temp,
            "temperature": temp,
            "humidity": hum,
            "rainfall_mm": r1h,
            "rainfall_intensity_mm_h": r1h,
            "rainfall_1h": r1h,
            "rainfall_3h": round(obs.rainfall_3h or (r1h * 2.8), 2),
            "rainfall_6h": round(obs.rainfall_6h or (r1h * 5.2), 2),
            "rainfall_24h": r24h,
            "wind_speed_kmh": wind,
            "wind_speed": wind,
            "pressure_hpa": press,
            "pressure": press,
            "weather_condition": cond,
            "condition": cond,
            "rain_probability": prob_ratio,
            "precipitation_probability": round(prob_ratio * 100.0, 1),
            "visibility_km": 10.0,
            "alert_level": alert_lvl,
            "source": actual_source,
            "observed_at": obs.observed_at,
            "is_demo": actual_source in ("mock", "simulation"),
            "is_cached": is_cached,
            "cached_at": obs_time.isoformat() if is_cached and obs_time else None,
            "data_freshness": data_freshness,
            "alerts": [f"Alert: High rainfall ({r1h} mm/h) in {obs.location}"] if r1h >= 20.0 else [],
            "official_warnings": []
        }


weather_service = WeatherService()
