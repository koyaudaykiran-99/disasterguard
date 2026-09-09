import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.ml.rainfall_model import rainfall_predictor
from app.ml.flood_model import flood_predictor
from app.ml.risk_engine import risk_engine
from app.database.models.prediction import RainfallPrediction, FloodPrediction
from app.database.models.weather import WeatherObservation
from app.database.models.risk import RiskZone
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType

logger = logging.getLogger("disasterguard.prediction")

RAINFALL_DISCLAIMER = (
    "Trained and evaluated on genuine ECMWF ERA5-Land historical meteorological data (2022-2024)."
)

FLOOD_DISCLAIMER = (
    "Current flood-depth model remains a synthetic-data prototype pending historical hydrological streamflow/gauge labels."
)

ACADEMIC_DISCLAIMER = RAINFALL_DISCLAIMER


class PredictionService:

    @staticmethod
    def _validate_weather_features(features: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and validate input meteorological feature ranges."""
        validated = dict(features)
        
        # Clamp humidity 0-100%
        if "humidity" in validated:
            try:
                val = float(validated["humidity"])
                validated["humidity"] = max(0.0, min(100.0, val))
            except (ValueError, TypeError):
                validated["humidity"] = 75.0

        # Validate non-negative rainfall
        for rain_key in ["rainfall_1h", "rainfall_3h", "rainfall_6h", "rainfall_12h", "historical_rainfall_24h", "cumulative_rainfall_24h", "rainfall_intensity_mm_h"]:
            if rain_key in validated:
                try:
                    val = float(validated[rain_key])
                    validated[rain_key] = max(0.0, val)
                except (ValueError, TypeError):
                    validated[rain_key] = 0.0

        # Validate temperature
        if "temperature" in validated:
            try:
                val = float(validated["temperature"])
                validated["temperature"] = max(-50.0, min(65.0, val))
            except (ValueError, TypeError):
                validated["temperature"] = 28.0

        # Validate pressure
        if "pressure" in validated:
            try:
                val = float(validated["pressure"])
                validated["pressure"] = max(800.0, min(1100.0, val))
            except (ValueError, TypeError):
                validated["pressure"] = 1012.0

        # Validate wind speed
        if "wind_speed" in validated:
            try:
                val = float(validated["wind_speed"])
                validated["wind_speed"] = max(0.0, val)
            except (ValueError, TypeError):
                validated["wind_speed"] = 10.0

        return validated

    @staticmethod
    def predict_rainfall(db: Session, features: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = PredictionService._validate_weather_features(features)
        
        # Augment with live PostgreSQL weather observation if available
        latest_weather = db.query(WeatherObservation).order_by(WeatherObservation.observed_at.desc()).first()
        data_source = "synthetic_features"
        weather_source = "none"

        if latest_weather:
            weather_source = latest_weather.source or "unknown"
            data_source = f"live_weather_db ({weather_source})"
            
            if sanitized.get("historical_rainfall_24h") == 120.0 and (latest_weather.rainfall_24h or 0) > 0:
                sanitized["historical_rainfall_24h"] = latest_weather.rainfall_24h
            if "rainfall_1h" not in sanitized:
                sanitized["rainfall_1h"] = latest_weather.rainfall_1h
            if "rainfall_3h" not in sanitized:
                sanitized["rainfall_3h"] = latest_weather.rainfall_3h
            if "rainfall_6h" not in sanitized:
                sanitized["rainfall_6h"] = latest_weather.rainfall_6h
            if "humidity" not in sanitized:
                sanitized["humidity"] = latest_weather.humidity or 85.0
            if "temperature" not in sanitized:
                sanitized["temperature"] = latest_weather.temperature or 26.0
            if "pressure" not in sanitized:
                sanitized["pressure"] = latest_weather.pressure or 1002.0
            if "wind_speed" not in sanitized:
                sanitized["wind_speed"] = latest_weather.wind_speed or 28.0

        result = rainfall_predictor.predict(sanitized)
        if weather_source != "none":
            result["data_source"] = data_source
        result["weather_source"] = weather_source
        if not result.get("disclaimer"):
            result["disclaimer"] = RAINFALL_DISCLAIMER
        
        # Save genuine ML prediction record to PostgreSQL
        db_rec = RainfallPrediction(
            location=sanitized.get("location", "Central Metro Basin"),
            predicted_rainfall=result["predicted_rainfall_mm"],
            forecast_horizon=result["forecast_horizon_hours"],
            confidence=result["confidence"],
            risk_level=result["risk_level"]
        )
        db.add(db_rec)
        db.commit()
        db.refresh(db_rec)

        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.RAIN_PREDICTION_UPDATED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=db_rec.id,
                    entity_type="rainfall_prediction",
                    severity=result.get("risk_level", "LOW"),
                    data=result
                )
            )
        except Exception as b_err:
            logger.warning(f"Could not broadcast RAIN_PREDICTION_UPDATED: {b_err}")
        
        return result

    @staticmethod
    def predict_flood(db: Session, features: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = PredictionService._validate_weather_features(features)
        
        # Augment with live PostgreSQL weather observation if available
        latest_weather = db.query(WeatherObservation).order_by(WeatherObservation.observed_at.desc()).first()
        data_source = "synthetic_features"
        weather_source = "none"

        if latest_weather:
            weather_source = latest_weather.source or "unknown"
            data_source = f"live_weather_db ({weather_source})"

            if sanitized.get("rainfall_intensity_mm_h") == 45.0 and (latest_weather.rainfall_1h or 0) > 0:
                sanitized["rainfall_intensity_mm_h"] = latest_weather.rainfall_1h
            if sanitized.get("cumulative_rainfall_24h") == 180.0 and (latest_weather.rainfall_24h or 0) > 0:
                sanitized["cumulative_rainfall_24h"] = latest_weather.rainfall_24h

        result = flood_predictor.predict(sanitized)
        if weather_source != "none":
            result["data_source"] = data_source
        result["weather_source"] = weather_source
        if not result.get("disclaimer"):
            result["disclaimer"] = FLOOD_DISCLAIMER
        
        # Save genuine ML prediction record to PostgreSQL
        db_rec = FloodPrediction(
            location=sanitized.get("location", "Central Metro Basin"),
            flood_probability=result["flood_probability"],
            water_depth=result["estimated_water_depth_m"],
            risk_level=result["risk_level"]
        )
        db.add(db_rec)
        db.commit()
        db.refresh(db_rec)
        
        # Update active RiskZones with fresh ML risk score and alert recommendation
        try:
            risk_calc = risk_engine.calculate_risk_score(
                rainfall_mm=float(sanitized.get("cumulative_rainfall_24h", 145.0)),
                flood_prob=result["flood_probability"],
                water_depth_m=result["estimated_water_depth_m"],
                population_density=12000
            )
            result["risk_breakdown"] = risk_calc.get("breakdown")
            result["alert_recommendation"] = risk_calc.get("alert_recommendation")
            result["top_drivers"] = risk_calc.get("top_drivers")

            zones = db.query(RiskZone).all()
            for z in zones:
                z.risk_level = risk_calc["risk_level"]
                z.risk_score = risk_calc["risk_score"]
                z.updated_at = datetime.now(timezone.utc)
            db.commit()

            # Broadcast updated risk zone event
            for z in zones:
                ws_manager.broadcast_event(
                    DomainEvent(
                        event=EventType.RISK_ZONE_UPDATED,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        entity_id=z.id,
                        entity_type="risk_zone",
                        severity=z.risk_level,
                        data={
                            "id": z.id,
                            "name": z.name,
                            "risk_level": z.risk_level,
                            "risk_score": z.risk_score,
                            "population_estimate": z.population_estimate
                        }
                    )
                )
        except Exception as e:
            logger.warning(f"Error updating risk zones from ML flood prediction: {e}")
            db.rollback()

        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.FLOOD_PREDICTION_UPDATED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=db_rec.id,
                    entity_type="flood_prediction",
                    severity=result.get("risk_level", "LOW"),
                    data=result
                )
            )
        except Exception as b_err:
            logger.warning(f"Could not broadcast FLOOD_PREDICTION_UPDATED: {b_err}")

        return result

prediction_service = PredictionService()
