# AI DisasterGuard — Priority 7: Real Historical Data & ML Retraining Documentation

## 1. Executive Summary

Priority 7 upgrades AI DisasterGuard from its synthetic prototype stage to a scientifically grounded, transparent disaster intelligence pipeline. This was accomplished by:
1. Ingesting **26,304 consecutive hourly observations** (3 complete years: 2022-01-01 to 2024-12-31) of authentic ECMWF ERA5-Land reanalysis meteorological data.
2. Performing rigorous quality control, boundary verification, and temporal feature engineering.
3. Implementing strict chronological train/validation/test splitting to eliminate future data leakage.
4. Retraining Model A (Heavy Rainfall Classifier) and Model B (Rainfall Volume Regressor) on genuine historical data (promoted to 2.0-real-data).
5. Establishing a formal **Model Registry** (ml/models/registry.json) with strict 4-tier provenance taxonomy.
6. Upgrading the central Multi-Factor Risk Engine to provide risk decomposition (40% rainfall + 40% flood + 20% urban exposure), internal alert recommendations, and explainable plain-English drivers.
7. Enhancing frontend dashboards with visual provenance badges and top feature contribution breakdowns.
8. Preserving 100% backward compatibility and regression safety for Priorities 1–6.

---

## 2. Authentic Historical Data Ingestion & Quality

- **Reanalysis Provider**: ECMWF ERA5-Land via Open-Meteo Historical Archive API (https://archive-api.open-meteo.com/v1/archive).
- **Geographic Focus**: Chennai Metropolitan Basin (Lat 13.0827°N, Lon 80.2707°E).
- **Time Span**: 2022-01-01T00:00 to 2024-12-31T23:00 (26,304 consecutive hours, 0 missing rows).
- **Quality Checks (ml/datasets/data_quality_report.json)**:
  - Missing value count: 0 cells.
  - Domain violations: 0.
  - Extreme event preservation: 45 hours with rainfall >= 10 mm/h preserved intact without synthetic smoothing.
  - Overall quality rating: EXCELLENT.

---

## 3. 4-Tier Data Provenance Taxonomy

To enforce academic and scientific integrity, all data consumed and produced by DisasterGuard is categorized into four explicit tiers:
1. historical_real: Authentic historical observations/reanalysis (e.g. ECMWF ERA5-Land 2022-2024).
2. live_weather_db: Real-time sensor observations cached in PostgreSQL.
3. simulation: Synthetic disaster scenarios used exclusively by the 8-stage simulation pipeline.
4. synthetic_prototype: Physically modeled synthetic datasets used for hydrological inundation and flood water depth prototypes pending municipal river gauge telemetry.

---

## 4. Leakage-Free Chronological Split & Feature Engineering

- **Split Ratios**: 70% Train (18,391 records), 15% Validation (3,941 records), 15% Test (3,942 records).
- **Time Intervals**:
  - Train: 2022-01-02 00:00 -> 2024-02-07 06:00
  - Validation: 2024-02-07 07:00 -> 2024-07-20 11:00
  - Test: 2024-07-20 12:00 -> 2024-12-31 17:00
- **Feature Vector (11 Features)**:
  - Rolling precipitation: 
ainfall_1h, 
ainfall_3h, 
ainfall_6h, 
ainfall_12h, 
ainfall_24h
  - Atmospheric state: 	emperature, humidity, pressure, wind_speed
  - Dynamics: pressure_change_3h (barometric drop indicator), humidity_trend_3h (moisture surge indicator)

---

## 5. Model Registry & Evaluation

| Model Key | Algorithm | Status | Version | Provenance | Key Metrics |
|---|---|---|---|---|---|
| 
ainfall_classifier_v2 | Balanced RandomForestClassifier | **ACTIVE** | 2.0-real-data | historical_real | Test Accuracy: 86.6%, F1: 0.880, Dangerous Event Recall: 18.8% |
| 
ainfall_regressor_v2 | GradientBoostingRegressor | **ACTIVE** | 2.0-real-data | historical_real | Test MAE: 1.60 mm, RMSE: 4.15 mm, R2: 0.359 |
| 
ainfall_classifier_v1 | RandomForestClassifier | RETIRED | 1.0-prototype | synthetic_prototype | Accuracy: 80.1% |
| 
ainfall_regressor_v1 | RandomForestRegressor | RETIRED | 1.0-prototype | synthetic_prototype | MAE: 9.73 mm |
| lood_classifier_v1 | RandomForestClassifier | **ACTIVE** | 1.0-prototype | synthetic_prototype | Accuracy: 74.9% (Calibrated prototype) |
| lood_depth_regressor_v1| RandomForestRegressor | **ACTIVE** | 1.0-prototype | synthetic_prototype | MAE: 0.18 m (Calibrated prototype) |

---

## 6. Multi-Factor Risk Engine & Alert Recommendations

The updated RiskEngine decomposes composite risk scores (0–100) into three explainable pillars:
- **Rainfall Component (40% weight)**: Scaled against historical basin absorption limits.
- **Flood Inundation Component (40% weight)**: Probability and estimated surface water depth.
- **Urban Exposure Component (20% weight)**: Demographic density and geographic vulnerability.

### Automated Internal Alert Recommendations:
- CRITICAL_WARNING (76–100): Immediate Evacuation & Defense Deployment
- WARNING (51–75): High Inundation Threat, Stage Emergency Crews
- WATCH (26–50): Elevated Inundation Potential, Continuous Monitoring
- MONITOR (0–25): Normal Operational Readiness

---

## 7. Verification Results

- **Backend Pytest Suite**: 22 passed in 5.93s (100% pass rate).
- **Priority 7 Verification Script**: All 7 gates passed.
- **Priority 3 SOS Triage**: Verified auto-dispatch operational.
- **Priority 5 Simulation**: 8-stage simulation pipeline verified operational.
- **Frontend TypeScript Build**: Clean production build (	sc -b && vite build exited with code 0).
