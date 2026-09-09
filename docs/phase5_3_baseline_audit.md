# AI-DisasterGuard — Phase 5.3 Baseline Audit

## Multi-Horizon Predictive Risk + Uncertainty-Aware Early Warning Intelligence

### 1. Executive Summary & Audit Purpose
This baseline audit establishes the technical foundation for **Phase 5.3: Multi-Horizon Predictive Risk + Uncertainty-Aware Early Warning Intelligence**.
The objective of Phase 5.3 is to advance AI-DisasterGuard from a point-in-time flood susceptibility assessment (Phase 5.2) and single-window forward rainfall prediction (Phase 5.1) into a multi-horizon risk evolution engine answering:
1. What is current disaster risk?
2. How is risk projected to evolve over 1H, 3H, 6H, 12H, and 24H horizons?
3. How confident is the forecast, and what is its measurable uncertainty?
4. What is the risk trajectory (increasing, stable, decreasing)?
5. When should warnings escalate, and what structured evidence triggered the escalation?

Before implementing Phase 5.3, this audit inspects all active components, establishes verified baseline test passes, documents existing limitations, and sets strict scientific honesty boundaries.

---

## 2. Baseline Test & Build Verification
The complete existing platform was verified prior to any Phase 5.3 changes:

| Verification Suite | Target | Result | Status |
| :--- | :---: | :---: | :---: |
| **Backend Pytest Suite** | 79 Unit/Integration Tests | 79 / 79 Passed (17.59s) | **PASS (100%)** |
| **Phase 3.5 Auto-Dispatch Audit** | 11 Safety Gates | 11 / 11 Passed | **PASS (100%)** |
| **Phase 4.1 Persistent SOS Suite** | 17 Gates | 17 / 17 Passed | **PASS (100%)** |
| **Phase 4.2 Multilingual Voice Suite** | 25 Gates | 25 / 25 Passed | **PASS (100%)** |
| **Phase 5.1 Real ML Retraining Suite** | 34 Gates | 34 / 34 Passed | **PASS (100%)** |
| **Phase 5.2 Flood Intelligence Suite** | 35 Gates | 35 / 35 Passed | **PASS (100%)** |
| **Command Centre Frontend Build** | `tsc -b && vite build` | 0 Errors (12.29s) | **PASS (100%)** |
| **Citizen Mobile App Build** | `tsc -b && vite build` | 0 Errors (9.45s) | **PASS (100%)** |

All baseline suites pass at 100%. The system is completely stable and healthy.

---

## 3. Existing Forecasting & Weather Capabilities
1. **Weather Providers (`backend/app/services/weather_provider.py`)**:
   - `RealWeatherProvider`: Interfaces with Open-Meteo API (or OpenWeatherMap when API key is set).
   - Ingests: temperature, humidity, surface pressure, wind speed, WMO weather code, 1h precipitation, and hourly forecast arrays (`hourly.precipitation`, `hourly.precipitation_probability`, `hourly.temperature_2m`).
   - `get_forecast(latitude, longitude, hours=24)`: Retrieves hourly meteorological forecasts up to 24 hours.
   - `MockWeatherProvider`: Deterministic synthetic provider for offline, air-gapped, or demonstration environments.
   - Caching: Weather observations cached in PostgreSQL `weather_observations` table to avoid redundant external network round-trips.

2. **Current Limitations in Weather Forecasting**:
   - Meteorological forecasts provide raw atmospheric precipitation projections, not compound flood risk or terrain-inundation projections.
   - Forecast series does not compute compound risk indices across standard operational intervals (1H, 3H, 6H, 12H, 24H).
   - No dynamic trajectory classification or uncertainty modeling exists in the weather layer.

---

## 4. Existing ML Models & Capabilities
1. **Real Historical Reanalysis Models (Phase 5.1)**:
   - Dataset: ECMWF ERA5-Land for Greater Chennai Metro (2022-01-01 to 2024-12-31, 26,304 hourly observations, CC BY 4.0).
   - `rainfall_classifier_v2.joblib`: Balanced Random Forest Classifier predicting rainfall severity (`LOW`, `MODERATE`, `HIGH`, `EXTREME`).
   - `rainfall_regressor_v2.joblib`: Random Forest Regressor predicting quantitative 6h rainfall accumulation (mm).
   - Preprocessing: `rainfall_preprocessor_v2.joblib` (StandardScaler + SimpleImputer across 11 temporal lag and trend features).
   - Horizon handling: Regressor predicts 6h volume directly. For other horizons, a crude heuristic power-law scaling (`pred_mm * (horizon / 6.0) ** 0.6`) was used.

2. **Synthetic Prototype Models (Phase 4)**:
   - `flood_classifier_v1.joblib` and `flood_depth_regressor_v1.joblib` trained on synthetic 3,500 sample dataset (`disaster_training_data.csv`).
   - Retained as `SYNTHETIC_PROTOTYPE` for offline fallback.

3. **Known Model Limitations**:
   - Model trained on single forward 6h window. It does not output discrete horizon forecasts (1H, 3H, 12H, 24H) natively.
   - Dangerous-event recall in ERA5-Land classifier is 18.8% (due to class imbalance: extreme monsoon downpours are rare in hourly reanalysis).
   - ML output represents atmospheric precipitation, NOT street-level water depth.

---

## 5. Existing Flood Intelligence & Spatial Calculations (Phase 5.2)
1. **Geospatial Provider Architecture (`ml/geospatial/`)**:
   - `TerrainProvider`: IDW interpolation against Chennai geodetic benchmarks (Marina, Pallikaranai, Velachery, Saidapet, T. Nagar, Central Station, St. Thomas Mount). Computes ground elevation (m ASL), slope angle (°), relative elevation to 6m ASL base.
   - `DrainageProvider`: Models 5 major drainage basins (Adyar River, Cooum River, Buckingham Canal, Otteri Nullah, Pallikaranai Wetland), computing distance-to-watercourse and bottleneck exposure.
   - `HistoricalFloodProvider`: Stores 4 verified historical Chennai flood disasters (2015 Adyar flood, 2023 Cyclone Michaung, 2021 waterlogging, 2016 Cyclone Vardah) and computes distance-decayed historical risk scores.
   - `susceptibility.py`: Normalized 0–100 composite score combining Rainfall load (40%), Topographic terrain (25%), Drainage proximity (20%), and Historical memory (15%).
   - `inundation.py`: Generates estimated proxy water depths (0.00m to 2.20m) and bounding footprint GeoJSON polygons, strictly labeled `PROXY_ESTIMATE` (`is_hydraulic_simulation: false`).

2. **Limitations in Current Flood Intelligence**:
   - Evaluates current point-in-time snapshot. It cannot answer how flood susceptibility will evolve 3, 6, 12, or 24 hours into the future.
   - Does not track risk trajectory (whether vulnerability is surging or abating).
   - Lacks an evidence-based escalation engine to generate proactive early warnings before disaster thresholds are reached.

---

## 6. Existing Risk Calculations & Alert Systems
1. **Risk Engine (`backend/app/ml/risk_engine.py`)**:
   - Calculates heuristic risk scores (0–100) for static predefined zones using fixed weightings.
2. **Alert Endpoints (`backend/app/api/endpoints/alerts.py`)**:
   - Manages CRUD for operational alerts. Does not currently integrate predictive multi-horizon forecasting or trajectory-based escalation triggers.

---

## 7. What Phase 5.3 Will Add
1. **Multi-Horizon Forecasting Architecture (`ml/forecasting/`)**:
   - `forecast_engine.py`: Unified multi-horizon risk forecasting engine synthesizing weather forecast series, real ML rainfall projection, terrain, drainage, and historical memory.
   - `horizon_engine.py`: Standardized forecast generation for **1H, 3H, 6H, 12H, and 24H**.
   - `uncertainty.py`: Explicit, measurable uncertainty estimation (horizon temporal decay, data staleness, model confidence, signal conflict, geospatial variance).
   - `trajectory.py`: Risk trajectory classification (`RAPIDLY_INCREASING`, `INCREASING`, `STABLE`, `DECREASING`, `RAPIDLY_DECREASING`, `UNKNOWN`).
   - `escalation.py`: Early-warning escalation engine with transparent states (`NORMAL`, `WATCH`, `ADVISORY`, `WARNING`, `CRITICAL`), threshold dampening on low confidence, and deduplication/cooldown.
   - `forecast_features.py`: Feature extraction across multi-horizon temporal windows.
   - `forecast_registry.py`: Governance, metadata, and provenance tracking for forecasting engines.

2. **Database Persistence & Alembic Migration**:
   - `forecast_predictions` table in PostgreSQL 18 storing location, horizon, timestamp, risk score, risk level, rainfall estimate, flood susceptibility, proxy depth, confidence, uncertainty, trajectory, provenance, and explanation JSON.
   - Alembic migration and spatial query compatibility.

3. **FastAPI Endpoints (`/api/v1/forecast/`)**:
   - `GET /api/v1/forecast/current`
   - `GET /api/v1/forecast/horizons`
   - `GET /api/v1/forecast/{horizon}`
   - `GET /api/v1/forecast/trajectory`
   - `GET /api/v1/forecast/explanation`
   - `GET /api/v1/forecast/uncertainty`

4. **WebSocket Real-Time Events**:
   - `FORECAST_UPDATED`
   - `FORECAST_TRAJECTORY_UPDATED`
   - `EARLY_WARNING_ESCALATED`
   - `EARLY_WARNING_DEESCALATED`
   - `FORECAST_CONFIDENCE_CHANGED`
   - Broadcast strictly after database commit.

5. **Command Centre Tactical UI**:
   - `MultiHorizonForecastPanel.tsx`: Interactive multi-horizon risk card with 1H/3H/6H/12H/24H timeline, risk vs time chart, trajectory badge, confidence gauge, and early warning escalation banner.
   - Multi-layer Map integration: Forecast risk layers (1H, 3H, 6H, 12H, 24H) selectable on `DisasterMap.tsx`.
   - Categorical Explainability Modal (`FACT`, `ML_PREDICTION`, `GEOSPATIAL_DERIVATION`, `AI_INTERPRETATION`, `RECOMMENDATION`).

6. **Citizen Mobile App**:
   - `CitizenForecastCard.tsx` on `Home.tsx`: Simplified, reassuring, action-oriented warning card (What, When, Where, What Should I Do).

7. **Emergency SOS Enrichment**:
   - Enrich new SOS reports with multi-horizon risk context (current, 1H, 3H, 6H, 12H, 24H), trajectory, and confidence to support AI retriage and operator dispatch decisions.

8. **AI Emergency Agent Integration**:
   - 5 read-only tools: `get_multi_horizon_forecast`, `get_risk_trajectory`, `get_forecast_uncertainty`, `get_early_warning_status`, `get_forecast_explanation`.
   - Strict zero-mutation and zero-dispatch enforcement.

9. **Historical Forecast Memory & Evaluation**:
   - `ml/evaluation/forecast_evaluation.py`: Framework to store forecasts and compare against future observed conditions (MAE, RMSE, accuracy, false-negative analysis).

---

## 8. What Phase 5.3 Will Explicitly NOT Claim (Mandatory Scientific Honesty)
To preserve scientific honesty and technical credibility, AI-DisasterGuard explicitly adheres to the following principles:

1. **NO Guaranteed Flood Prediction**: The platform produces predictive risk estimates and susceptibility proxies; it does NOT claim deterministic knowledge of disaster occurrence.
2. **NO Exact Future Flood Depth**: Future water depths are labeled strictly as `PROXY_ESTIMATE`; no centimeter-level physical precision is claimed.
3. **NO Real-Time Hydrodynamic Simulation**: AI-DisasterGuard explicitly does NOT solve 2D shallow water Saint-Venant equations or run hydraulic physics simulations (e.g. HEC-RAS / TUFLOW).
4. **NO Certified Meteorological Forecasting Authority**: The system is a decision-support prototype, not a government-certified weather forecasting or civil protection agency.
5. **NO Autonomous Emergency Decisions or Dispatches**: The platform strictly enforces the **Human Operator Confirmation Barrier** (`RescueAssignment == 0` for all automated events). Rescue dispatches require explicit human commander confirmation.
6. **NO Unjustified Deep Learning Claims**: The forecasting engine uses a transparent, explainable synthesis of real historical ML, atmospheric reanalysis trends, topographic benchmarks, and historical disaster memory, labeled as `EXPLAINABLE_FORECAST_ENGINE`. It will not falsely rebrand mathematical heuristics as "deep learning" or "Transformers".
7. **Uncertainty Increases With Horizon**: Confidence is explicitly modeled to decay as the forecast horizon extends (1H > 3H > 6H > 12H > 24H).

---

## 9. Baseline Audit Sign-Off
- **Status**: AUDIT COMPLETE — BASELINE CONFIRMED STABLE.
- **Ready for Implementation**: Phase 5.3 architecture, forecasting modules, database models, APIs, and UI components.
