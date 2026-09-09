# Priority 7 — Machine Learning Architecture Audit

**Project**: AI DisasterGuard  
**Audit Date**: September 2026  
**Auditor**: Antigravity AI Engineering  
**Scope**: Machine Learning Subsystem (`ml/`, `backend/app/ml/`, `backend/app/services/`, database schemas, and endpoints)

---

## 1. Executive Summary

AI DisasterGuard currently operates with a **Priority 4 Scikit-Learn prototype** for heavy rainfall prediction and flood inundation risk estimation. While the software architecture, REST endpoints, database schemas, and PostGIS risk-zone updates are integrated and working, the models were trained on a **synthetic, physically-modeled dataset** (`ml/datasets/disaster_training_data.csv`).

Priority 7 upgrades this system to ingest **authentic real-world historical meteorological observations** from official sources (ECMWF ERA5-Land via Open-Meteo Historical Archive API), implements temporal feature engineering without future leakage, introduces a formal **Model Registry** (`ml/models/registry.json`), and provides explainable risk scoring while maintaining scientific honesty regarding available hydrological features.

---

## 2. Current ML Pipeline Inventory

### 2.1 Training Dataset
- **Location**: `ml/datasets/disaster_training_data.csv`
- **Volume**: 3,500 samples
- **Generator**: `ml/datasets/generate_dataset.py` (fixed random seed: 42)
- **Data Provenance**: Physically-modeled synthetic dataset simulating atmospheric pressure depressions, relative humidity saturation, multi-interval rainfall accumulation, and topographical runoff.

### 2.2 Feature Columns

#### A. Heavy Rainfall Prediction Models
| Feature | Type | Units | Description |
| :--- | :--- | :--- | :--- |
| `rainfall_1h` | Float | mm | Preceding 1-hour rainfall accumulation |
| `rainfall_3h` | Float | mm | Preceding 3-hour rainfall accumulation |
| `rainfall_6h` | Float | mm | Preceding 6-hour rainfall accumulation |
| `rainfall_12h` | Float | mm | Preceding 12-hour rainfall accumulation |
| `rainfall_24h` | Float | mm | Preceding 24-hour rainfall accumulation |
| `temperature` | Float | °C | Surface ambient temperature |
| `humidity` | Float | % | Relative surface humidity |
| `pressure` | Float | hPa | Atmospheric barometric surface pressure |
| `wind_speed` | Float | km/h | Sustained surface wind speed |

#### B. Flood Inundation Models
| Feature | Type | Units | Description |
| :--- | :--- | :--- | :--- |
| `rainfall_intensity_mm_h` | Float | mm/h | Real-time rainfall intensity rate |
| `cumulative_rainfall_24h` | Float | mm | 24-hour cumulative precipitation |
| `elevation_m` | Float | meters | Topographical elevation above sea level |
| `slope_deg` | Float | degrees | Terrain slope angle |
| `drainage_proximity_m` | Float | meters | Distance to primary storm canal/river |
| `soil_saturation_pct` | Float | % | Topsoil moisture saturation index |

### 2.3 Target Variables
1. **Model 1A (Heavy Rainfall Classifier)**: `rainfall_category` (`LOW` <40mm, `MODERATE` 40–90mm, `HIGH` 90–150mm, `EXTREME` ≥150mm).
2. **Model 1B (Rainfall Continuous Regressor)**: `predicted_rainfall_6h_mm` (Continuous millimeters in 6-hour forecast).
3. **Model 2A (Flood Risk Classifier)**: `flood_risk_level` (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
4. **Model 2B (Flood Depth Continuous Regressor)**: `water_depth_m` (Continuous flood depth 0.0 to 3.4m).

### 2.4 Preprocessing Pipeline
- **Implementation**: `ml/preprocessing/pipeline.py`
- **Steps**:
  1. `SimpleImputer(strategy="median")`
  2. `StandardScaler()`
- **Persistence**: Serialized with `joblib` into `ml/models/rainfall_preprocessor.joblib` and `ml/models/flood_preprocessor.joblib`.

### 2.5 Trained Artifacts & Versioning
- `ml/models/rainfall_classifier.joblib` (RandomForestClassifier, n=100, max_depth=12)
- `ml/models/rainfall_regressor.joblib` (RandomForestRegressor, n=100, max_depth=12)
- `ml/models/rainfall_preprocessor.joblib` (PreprocessingPipeline)
- `ml/models/flood_classifier.joblib` (RandomForestClassifier, n=100, max_depth=12)
- `ml/models/flood_depth_regressor.joblib` (RandomForestRegressor, n=100, max_depth=12)
- `ml/models/flood_preprocessor.joblib` (PreprocessingPipeline)
- `ml/models/model_metrics.json` (Static validation metrics)

### 2.6 Baseline Performance Comparison (Synthetic Test Set)
- **Rainfall Classifier**:
  - Primary RF: Accuracy 80.14%, F1 79.97%
  - Baseline LogisticRegression: Accuracy 81.43%
- **Rainfall Regressor**:
  - Primary RF: MAE 9.73 mm, RMSE 12.18 mm, R² 0.8198
- **Flood Classifier**:
  - Primary RF: Accuracy 74.86%, F1 74.20%
  - Baseline GradientBoosting: Accuracy 74.71%
- **Flood Depth Regressor**:
  - Primary RF: MAE 0.18 m, RMSE 0.26 m, R² 0.8673

---

## 3. Serving & Inference Architecture

### 3.1 Inference Engine: `DisasterMLService`
- **File**: `backend/app/ml/prediction_service.py`
- **Loading**: Singleton initialized at app startup; loads all 6 `.joblib` artifacts once into RAM.
- **Methods**:
  - `predict_rainfall(features)`: Scaled features → RF Predictor → probability distribution & continuous mm.
  - `predict_flood(features)`: Scaled features → RF Predictor → flood probability & depth estimate.
  - `get_metrics()`: Exposes `model_metrics.json`.

### 3.2 Service Layer & Database Synchronization: `PredictionService`
- **File**: `backend/app/services/prediction_service.py`
- **Live Ingestion**: Ingests the latest `WeatherObservation` from PostgreSQL if live observations exist.
- **Persistence**: Writes inference rows to PostgreSQL tables `rainfall_predictions` and `flood_predictions`.
- **Spatial Feedback**: Calls `risk_engine.calculate_risk_score(...)` and updates all active `RiskZone` records in PostGIS/PostgreSQL.

---

## 4. Gaps Identified for Priority 7

1. **Training Data Authenticity**: Models are trained on synthetic data. Real historical weather data from official reanalysis (ERA5-Land via Open-Meteo) must be ingested for genuine training.
2. **Hydrological Ground Truth Boundaries**: While atmospheric parameters (rainfall, pressure, temperature, wind, humidity) are available in real historical meteorological records, streamflow and flood-depth gauge records are not universally available in open API archives without localized telemetry. We must strictly preserve academic honesty:
   - **Model A & B (Rainfall)**: Trained on **Real Historical Data**.
   - **Model C & D (Flood Risk & Depth)**: Maintained as **Physics-Modeled Prototype** until certified telemetry gauges are connected.
3. **Temporal Data Leakage Prevention**: Currently uses random `train_test_split`. Time series data must use **chronological splitting** (e.g. 70% past training, 15% validation, 15% test).
4. **Model Registry & Versioning**: Currently loads hardcoded paths with no versioning, candidate promotion, or provenance tracking. A formal `ml/models/registry.json` must be established.
5. **Explainable Risk Scoring**: Current risk engine provides an aggregate score without feature attribution or reasons for the elevated score.
6. **Internal Alert Recommendation**: Alerts should follow a tiered internal recommendation system (`MONITOR`, `WATCH`, `WARNING`, `CRITICAL WARNING`) without broadcasting public alerts.

---

## 5. Non-Regression Constraints

- **Priority 1–4**: Core database tables, Alembic migrations, and existing endpoints remain stable.
- **Priority 5 Simulation**: Simulation mode must remain 100% deterministic and independent of external training data.
- **Priority 6 Real Weather**: Ingestion of live Open-Meteo weather and 15-minute PostgreSQL caching must feed the new active models directly.
