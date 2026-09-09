# AI-DisasterGuard — Phase 5.1 Baseline ML Audit

## Comprehensive Repository Audit of Existing Machine Learning Infrastructure

**Audit Timestamp**: 2026-09-08T20:10:00+00:00  
**Status**: COMPLETE  
**Auditor**: Antigravity AI Engine (Phase 5.1 Preparation)

---

## 1. Executive Summary

This audit catalogs every machine learning component, dataset, preprocessing pipeline, model artifact, prediction service, database table, and live weather integration currently operational in the AI-DisasterGuard repository prior to the full Phase 5.1 enhancement.

The audit confirms that the repository maintains two distinct data pipelines:
1. **Synthetic Prototype Pipeline (v1.0)**: Trained on physically modeled synthetic records (disaster_training_data.csv).
2. **Real Historical Meteorological Pipeline (v2.0)**: Trained on genuine ECMWF ERA5-Land reanalysis observations (historical_weather_chennai_2022_2024.csv).

---

## 2. Dataset Inventory

### 2.1 Synthetic Dataset: ml/datasets/disaster_training_data.csv
- **Dataset Type**: SYNTHETIC_PROTOTYPE
- **Generator**: ml/datasets/generate_dataset.py (Fixed seed 42)
- **Record Count**: 3,500 records
- **Feature Space (9 Features)**:
  - rainfall_intensity_mm_h: 5.0 to 120.0 mm/h
  - cumulative_rainfall_24h: 15.0 to 350.0 mm
  - elevation_m: 1.0 to 65.0 meters
  - slope_deg: 0.1 to 15.0 degrees
  - drainage_proximity_m: 10.0 to 1500.0 meters
  - soil_saturation_pct: 30.0% to 98.0%
  - temperature_c: 22.0 to 38.0 C
  - humidity_pct: 55.0% to 98.0%
  - river_distance_m: 20.0 to 3000.0 meters
- **Target Variables**:
  - risk_level: 4 categories (LOW, MODERATE, HIGH, CRITICAL)
  - water_depth_m: Continuous flood depth (0.0 to 3.8 meters)
  - rainfall_category: 4 categories (LOW, MODERATE, HIGH, EXTREME)
  - predicted_rainfall_mm: Continuous volume (10.0 to 280.0 mm)
- **Operational Role**: Preserved for flood_classifier_v1 and flood_depth_regressor_v1 because open global meteorological reanalysis lacks in-situ physical river streamflow and municipal flood-depth telemetry.

### 2.2 Real Historical Dataset: ml/datasets/historical_weather_chennai_2022_2024.csv
- **Dataset Type**: REAL_HISTORICAL
- **Provider**: Open-Meteo Historical Weather Archive API (https://archive-api.open-meteo.com/v1/archive)
- **Underlying Scientific Model**: ECMWF ERA5 / ERA5-Land Reanalysis
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0) via Copernicus Climate Change Service
- **Geographical Scope**: Chennai Metropolitan Area (13.0827N, 80.2707E), Tamil Nadu, India
- **Temporal Scope**: 2022-01-01T00:00:00Z to 2024-12-31T23:00:00Z (3 full calendar years)
- **Temporal Resolution**: 1-hour consecutive observations
- **Record Count**: 26,304 rows
- **Missing Value Count**: 0 (0.0%)
- **Raw Variables Ingested**:
  - timestamp: ISO-8601 UTC timestamp
  - temperature_c: 18.5 C to 41.8 C
  - humidity_pct: 24.0% to 100.0%
  - precipitation_mm: 0.0 mm to 68.4 mm/h
  - rain_mm: 0.0 mm to 68.4 mm/h
  - surface_pressure_hpa: 991.4 hPa to 1018.6 hPa
  - wind_speed_kmh: 1.8 km/h to 58.2 km/h
  - weather_code: WMO synoptic code (0 to 95)

### 2.3 Engineered Feature Dataset: ml/datasets/engineered_historical_features.csv
- **Record Count**: 26,274 rows (edge-trimmed: initial 24 hours dropped for 24h lag calculation; final 6 hours dropped for forward target window)
- **Engineered Temporal Features (11 Features)**:
  1. rainfall_1h: Lag-1 hour precipitation (mm)
  2. rainfall_3h: Lag-3 hour cumulative precipitation (mm)
  3. rainfall_6h: Lag-6 hour cumulative precipitation (mm)
  4. rainfall_12h: Lag-12 hour cumulative precipitation (mm)
  5. rainfall_24h: Lag-24 hour cumulative precipitation (mm)
  6. temperature: Surface air temperature (C)
  7. humidity: Relative surface humidity (%)
  8. pressure: Surface barometric pressure (hPa)
  9. wind_speed: 10m sustained wind speed (km/h)
  10. pressure_change_3h: 3-hour barometric delta (dP/dt)
  11. humidity_trend_3h: 3-hour relative humidity delta (dH/dt)
- **Forward-Looking Targets**:
  - predicted_rainfall_6h_mm: Cumulative precipitation from hour t to t+6
  - rainfall_category: Classified into LOW (<5mm), MODERATE (5-20mm), HIGH (20-50mm), EXTREME (>=50mm)

---

## 3. Preprocessing Architecture

- **Module**: ml/preprocessing/pipeline.py
  - Encapsulates sklearn.preprocessing.StandardScaler and sklearn.impute.SimpleImputer(strategy='median').
  - Serialized via joblib into ml/models/rainfall_preprocessor_v2.joblib and flood_preprocessor.joblib.
  - Guaranteed idempotency: Fitted strictly on the training partition (first 70%) to avoid any data leakage into validation or test sets.
- **Module**: ml/preprocessing/temporal_features.py
  - Defines FEATURE_COLUMNS schema and chronological splitting (chronological_split).
  - Strict time-series split: 70% Train (18,391 samples), 15% Validation (3,941 samples), 15% Test (3,942 samples).
- **Module**: ml/preprocessing/quality_check.py
  - Checks monotonicity, duplicate timestamps, missing values, domain ranges, and records extreme weather occurrences without naive removal.

---

## 4. Current Models and Artifact Inventory

Located in ml/models/:

- rainfall_classifier_v2.joblib: RandomForestClassifier, v2.0-real-data, ACTIVE
- rainfall_regressor_v2.joblib: GradientBoostingRegressor, v2.0-real-data, ACTIVE
- rainfall_preprocessor_v2.joblib: StandardScaler + Imputer, v2.0-real-data, ACTIVE
- flood_classifier.joblib: RandomForestClassifier, v1.0-prototype, ACTIVE (PROTOTYPE)
- flood_depth_regressor.joblib: RandomForestRegressor, v1.0-prototype, ACTIVE (PROTOTYPE)
- flood_preprocessor.joblib: StandardScaler + Imputer, v1.0-prototype, ACTIVE (PROTOTYPE)
- rainfall_classifier.joblib: RandomForestClassifier, v1.0-prototype, RETIRED
- rainfall_regressor.joblib: RandomForestRegressor, v1.0-prototype, RETIRED
- rainfall_preprocessor.joblib: StandardScaler + Imputer, v1.0-prototype, RETIRED

---

## 5. Inference Services and Runtime Architecture

1. backend/app/ml/prediction_service.py (DisasterMLService):
   - Manages model lifecycle and artifact loading via joblib.
   - Reads active model mappings from ml/models/registry.json.
   - Executes predict_rainfall() with 11-feature input DataFrame and outputs category, continuous mm, confidence (via predict_proba), top 3 feature contributors, and scientific disclaimers.
   - Executes predict_flood() for flood probability and water depth.
   - Provides get_metrics() returning full registry metadata.

2. backend/app/services/prediction_service.py (PredictionService):
   - Sanitizes and validates input features against physical domain boundaries.
   - Queries PostgreSQL table weather_observations for the latest live Open-Meteo observation, automatically augmenting missing input features.
   - Persists predictions into PostgreSQL tables rainfall_predictions and flood_predictions.
   - Calculates composite risk scores via risk_engine, updates risk_zones table, and broadcasts WebSocket domain events.

---

## 6. Live Weather Integration and Provenance Tracking

- Weather provider: backend/app/services/weather_provider.py connects to Open-Meteo API.
- Stores observation in WeatherObservation model in PostgreSQL with coordinates, temperature, humidity, pressure, wind speed, rainfall, and source (open_meteo or mock_weather).
- Inferences generated by prediction_service record data_source:
  - live_weather_db (open_meteo) when live weather exists.
  - historical_real when evaluating historical records.
  - synthetic_prototype when evaluating simulated/synthetic scenarios.

---

## 7. Safety and Confirmation Barrier Compliance

- Invariant verified: Neither prediction_service nor DisasterMLService creates RescueAssignment or dispatches rescue squads.
- AI Emergency Triage (AITriageService) consumes ML predictions solely as advisory inputs (predictions JSON field) and always requires explicit human operator confirmation before any field deployment (human_confirmation_required = True).
