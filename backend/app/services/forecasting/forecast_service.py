"""
Unified Backend Multi-Horizon Risk Forecasting Service.
Coordinates weather provider series, historical flood memory, ML susceptibility engine,
PostgreSQL persistence, and real-time WebSocket broadcasts.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import json
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models.forecast import ForecastPrediction
from app.database.models.historical_flood import HistoricalFloodEvent
from app.services.weather_provider import get_weather_provider
from app.services.websocket_manager import ws_manager
from app.schemas.events import EventType, DomainEvent
from app.core.logging import logger

import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.forecasting.forecast_engine import ForecastEngine
from ml.forecasting.horizon_engine import ForecastHorizon
from ml.forecasting.escalation import WarningState

class ForecastService:
    """
    Singleton service handling multi-horizon forecasting, persistence, and event broadcasts.
    """
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_ttl_seconds: int = 60

    def __init__(self):
        self.weather_provider = get_weather_provider()

    async def get_or_calculate_forecast(
        self,
        latitude: float,
        longitude: float,
        db: Optional[Session] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate or retrieve cached multi-horizon risk forecast.
        """
        cache_key = f"{round(latitude, 4)}_{round(longitude, 4)}"
        now = datetime.now(timezone.utc)

        # Check in-memory cache
        if not force_refresh and cache_key in self._cache:
            cached_item = self._cache[cache_key]
            cached_time = cached_item.get("_cached_at")
            if cached_time and (now - cached_time).total_seconds() < self._cache_ttl_seconds:
                return cached_item["data"]

        # Fetch live/mock weather observation
        weather_dict = {}
        forecast_series = []
        try:
            current_w = await self.weather_provider.get_current_weather(latitude, longitude)
            weather_dict = current_w.model_dump() if hasattr(current_w, "model_dump") else current_w.dict()
            forecast_series = await self.weather_provider.get_forecast(latitude, longitude, hours=24)
        except Exception as e:
            logger.warning(f"Error fetching live weather for forecast: {e}. Falling back to default baseline.")
            weather_dict = {
                "rainfall_1h": 10.0,
                "rainfall_24h": 40.0,
                "temperature": 28.0,
                "humidity": 75.0,
                "pressure": 1008.0,
                "wind_speed": 14.0,
                "condition": "Cloudy",
                "source": "fallback"
            }

        # Query historical events from DB if available
        db_events = None
        if db is not None:
            try:
                evs = db.query(HistoricalFloodEvent).all()
                if evs:
                    db_events = [
                        {
                            "id": e.id,
                            "event_name": e.event_name,
                            "latitude": e.latitude,
                            "longitude": e.longitude,
                            "severity": e.severity,
                            "rainfall_total_mm": e.rainfall_total_mm,
                            "description": e.description
                        }
                        for e in evs
                    ]
            except Exception as e:
                logger.warning(f"Could not load historical events from db: {e}")

        # Compute multi-horizon forecast
        forecast_result = ForecastEngine.compute_forecast(
            latitude=latitude,
            longitude=longitude,
            weather_data=weather_dict,
            forecast_series=forecast_series,
            db_events=db_events
        )

        # Persist to database if db session provided
        if db is not None:
            try:
                self._persist_forecast_records(db, latitude, longitude, forecast_result)
            except Exception as ex:
                logger.error(f"Failed to persist forecast records: {ex}", exc_info=True)

        # Update cache
        self._cache[cache_key] = {
            "_cached_at": now,
            "data": forecast_result
        }

        # Broadcast WebSocket event
        try:
            traj_data = forecast_result.get("trajectory", {})
            early_w = forecast_result.get("early_warning", {})
            event_payload = {
                "event": EventType.FORECAST_UPDATED,
                "timestamp": now.isoformat(),
                "data": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current_risk": forecast_result.get("current", {}).get("risk_score", 50),
                    "trajectory": traj_data.get("trajectory", "STABLE"),
                    "peak_risk": traj_data.get("peak_risk", 50),
                    "peak_horizon": traj_data.get("peak_horizon", "6H"),
                    "warning_state": early_w.get("warning_state", "NORMAL"),
                    "headline": early_w.get("headline", "")
                }
            }
            # Trigger asynchronous non-blocking broadcast
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(ws_manager.broadcast(event_payload))
                if early_w.get("warning_state") in ["WARNING", "CRITICAL"]:
                    asyncio.create_task(ws_manager.broadcast({
                        "event": EventType.EARLY_WARNING_ESCALATED,
                        "timestamp": now.isoformat(),
                        "data": early_w
                    }))
        except Exception as ws_ex:
            logger.warning(f"WebSocket broadcast error for forecast: {ws_ex}")

        return forecast_result

    def _persist_forecast_records(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        forecast_result: Dict[str, Any]
    ) -> None:
        """
        Persist each horizon prediction as a record in PostgreSQL forecast_predictions table.
        """
        horizons = forecast_result.get("horizons", {})
        traj = forecast_result.get("trajectory", {}).get("trajectory", "STABLE")
        w_state = forecast_result.get("early_warning", {}).get("warning_state", "NORMAL")
        expl_json = json.dumps(forecast_result.get("explainability", {}))

        for h, data in horizons.items():
            dt_str = data.get("forecast_timestamp")
            fc_dt = datetime.fromisoformat(dt_str) if dt_str else datetime.now(timezone.utc)
            val_until_str = data.get("valid_until")
            val_until_dt = datetime.fromisoformat(val_until_str) if val_until_str else None

            pred_record = ForecastPrediction(
                location="Chennai Metro",
                latitude=latitude,
                longitude=longitude,
                horizon=h,
                forecast_timestamp=fc_dt,
                risk_score=data.get("risk_score", 0),
                risk_level=data.get("risk_level", "LOW"),
                rainfall_estimate_mm=data.get("rainfall_estimate_mm", 0.0),
                flood_susceptibility=data.get("flood_susceptibility", 0),
                proxy_depth_estimate_m=data.get("proxy_depth_estimate_m", 0.0),
                depth_type="PROXY_ESTIMATE",
                confidence=data.get("confidence", 0.70),
                uncertainty=data.get("uncertainty", 0.30),
                trajectory=traj,
                warning_state=w_state,
                model_version="forecast_v1",
                data_source="REAL_WEATHER + REAL_HISTORICAL_ML + GEOSPATIAL_DERIVATION",
                data_source_type="EXPLAINABLE_FORECAST_ENGINE",
                explanation=expl_json,
                generated_at=datetime.now(timezone.utc),
                valid_until=val_until_dt
            )
            db.add(pred_record)
        db.commit()

# Singleton instance
forecast_service = ForecastService()
