# AI-DisasterGuard — Phase 5.2 Baseline Audit

## 1. Existing Flood-Related Functionality
* **Database Models**:
  * `FloodPrediction` (`backend/app/database/models/prediction.py`): Contains `location`, `flood_probability`, `water_depth`, `risk_level`, `prediction_time`.
  * `RiskZone` (`backend/app/database/models/risk.py`): Contains `name`, `latitude`, `longitude`, `risk_level`, `risk_score`, `population_estimate`, `geometry_wkt` (WKT string representation).
* **ML / Risk Engines**:
  * `RiskEngine` (`backend/app/ml/risk_engine.py`): Heuristic 0–100 score matrix combining rainfall (40%), flood inundation (40%), and urban exposure (20%).
  * `DisasterMLService` (`backend/app/ml/prediction_service.py`): Manages `rainfall_classifier_v2` and `rainfall_regressor_v2` (Phase 5.1 real historical models) alongside `flood_classifier_v1` and `flood_depth_regressor_v1` (`SYNTHETIC_PROTOTYPE` fallback).
* **Endpoints**:
  * `/api/v1/predictions/flood`: Ingestion and retrieval of prototype flood predictions.
  * `/api/v1/risk/zones`: Retrieval of active risk zones.
  * `/api/v1/risk/calculate`: Calculation of multi-factor risk score.

---

## 2. Existing Spatial Data
* **Repository Datasets**:
  * No raw raster DEMs (e.g., GeoTIFF), vector shapefiles, or hydrographic flowline datasets exist in `ml/datasets/`.
  * `RiskZone` seed data in `seed.py` defines 3 static WKT multipolygons around Central Chennai, Northern Slopes, and Eastern Elevated Plateau.
  * `DisasterMap.tsx` currently hardcodes two polygon arrays for `INUNDATION_ZONES` (Downtown Riverside Basin and Northern Highway Slopes).
  * Safe shelters and hospitals have point coordinates (`latitude`, `longitude`) in PostgreSQL.

---

## 3. Existing PostGIS Capabilities
* **Local Environment Status**:
  * The local PostgreSQL 18 instance does not have the PostGIS compiled extension library installed (`pg_available_extensions` returns empty for PostGIS).
  * `database.py` catches this during startup and logs: `PostGIS extension initialization warning: extension "postgis" is not available`.
  * Python environment possesses `geoalchemy2` (v0.17.1) and `shapely` (v2.0.7).
  * `backend/app/gis/spatial_queries.py` currently executes spherical Haversine math in Python (`haversine_distance_km`, `is_point_within_radius`).
* **Requirement**:
  * The system must implement PostGIS SQL queries (`ST_DWithin`, `ST_Distance`, `ST_Intersects`, `ST_Contains`) using GeoAlchemy2/PostGIS where the database extension is enabled, with a robust GeoAlchemy2/Shapely spatial fallback when running in vanilla PostgreSQL environments.

---

## 4. Existing Synthetic Flood Logic
* **Models**: `flood_classifier_v1.joblib` and `flood_depth_regressor_v1.joblib` trained on uniform random variables (`disaster_training_data.csv`).
* **Formulas**: In `ml/synthetic/generator.py`, water depth was generated using synthetic heuristic formulas.
* **Preservation**: Retained in `ml/models/registry.json` under `SYNTHETIC_PROTOTYPE` for simulation and air-gapped fallback.

---

## 5. Existing Real-Data ML
* **Completed in Phase 5.1**:
  * ECMWF ERA5-Land reanalysis dataset (`historical_weather_chennai_2022_2024.csv`, 26,304 hourly observations).
  * 11 temporal features (`rainfall_1h`, `rainfall_3h`, `rainfall_6h`, `rainfall_12h`, `rainfall_24h`, `temperature`, `humidity`, `pressure`, `wind_speed`, `pressure_change_3h`, `humidity_trend_3h`).
  * Chronological 70/15/15 split with zero future leakage.
  * Models: `rainfall_classifier_v2.joblib` (Balanced Random Forest) and `rainfall_regressor_v2.joblib` (Random Forest).
  * Provenance API, manifest, and read-only AI agent tools.

---

## 6. What Can Be Reused
* Real historical ERA5-Land weather data ingestion and temporal feature engineering.
* `rainfall_classifier_v2` and `rainfall_regressor_v2` for quantitative precipitation forecasting.
* PostgreSQL database connection pool, Alembic migration framework, and seed data.
* WebSocket broadcast infrastructure for real-time GIS state synchronization.
* Command Centre Leaflet map canvas and layer toggle HUD.
* Citizen App offline queue and persistent SOS architecture.
* Human Operator Confirmation Barrier (`RescueAssignment == 0` without confirmation).

---

## 7. What Must Be Improved
* **Geospatial Provider Abstraction**: Modular architecture for Terrain, Drainage, and Historical Flood intelligence with clear source classification (`REAL_GEOSPATIAL`, `HISTORICAL_EVENT`, `DERIVED`, `SIMULATION`, `MOCK`).
* **Topographic & Terrain Proxy**: Terrain elevation, slope, and accumulation proxies with explicit provider modes (`REAL`, `MOCK`, `SIMULATION`).
* **Historical Flood Memory**: Verified database layer (`HistoricalFloodEvent`) tracking historical disaster events (e.g. 2015 Chennai Floods, 2023 Cyclone Michaung, 2021 Waterlogging).
* **Explainable Geospatial Susceptibility**: Physics-aligned multi-factor index combining multi-scale rainfall accumulation, elevation, slope, and historical vulnerability.
* **Inundation Intelligence**: `InundationPrediction` exposing `PROXY_ESTIMATE` depth, confidence, and plain-English explainability drivers.
* **Spatial Risk Zones**: Dynamic PostGIS/GeoAlchemy2 risk zone updates with geometry, risk score, and contextual metrics.
* **Command Centre UI**: Flood Intelligence Panel with risk gauge, terrain metrics, and provenance badges.
* **Interactive Map**: Multi-layer Leaflet GIS supporting Inundation Proxies, Historical Flood Events, Shelters, Hospitals, and SOS Distress Markers.
* **AI Emergency Agent**: 4 read-only flood intelligence tools with strict dispatch and model mutation barriers.

---

## 8. Dataset Limitations
* **No Real-Time Hydrodynamic Telemetry**: The repository lacks river gauge telemetry, storm-water drain IoT sensors, and high-resolution LiDAR DEMs.
* **Reanalysis vs Inundation**: ERA5-Land provides atmospheric precipitation reanalysis, not ground-truth street-level water depths.
* **Historical Event Coverage**: Only major documented Chennai meteorological flood disasters have verified historical data.

---

## 9. Scientific Limitations
* Models produce **geospatial flood susceptibility and risk proxies**, NOT hydrodynamic flood inundations (such as 2D Saint-Venant hydraulic simulations).
* Estimated water depth is classified as **`PROXY_ESTIMATE`**; no claim of centimeter-level physical accuracy is made.
* Predictions indicate relative risk prioritization to assist human command center operators.

---

## 10. Implementation Plan Overview
1. Create `ml/geospatial/` and `backend/app/services/geospatial/` provider architecture (`TerrainProvider`, `DrainageProvider`, `HistoricalFloodProvider`, `SpatialRiskEngine`).
2. Add database model `HistoricalFloodEvent` and `InundationPrediction` (with Alembic migration). Seed verified Chennai historical floods.
3. Integrate spatial feature extraction with PostGIS queries and GeoAlchemy2/Shapely fallback.
4. Extend `DisasterMLService` with advanced flood intelligence and explainability drivers.
5. Upgrade Command Centre UI (`FloodIntelligencePanel.tsx`, `DisasterMap.tsx` multi-layer GIS with historical events).
6. Integrate flood context into SOS triage and citizen alerts.
7. Add 4 read-only AI agent tools in `tools.py`.
8. Implement verification suite (`scratch/verify_phase5_2_flood_intelligence.py`) covering all 34+ gates.
9. Execute full regression testing (Phase 3.5, 4.1, 4.2, 5.1, pytest 79+ tests, frontend Vite builds).
10. Generate documentation and completion report.
