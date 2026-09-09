# AI-DisasterGuard — ML Model Evaluation Report

## Real Historical Retraining Benchmarks (Phase 5.1)

**Generated**: 2026-09-08T14:43:35.296147+00:00  
**Dataset**: `historical_weather_chennai_2022_2024.csv` (ECMWF ERA5-Land Reanalysis)  
**Dataset Type**: `REAL_HISTORICAL`  
**Temporal Splits**:
- **Train (70%)**: 2022-01-02T00:00 to 2024-02-07T06:00 (18391 records)
- **Validation (15%)**: 2024-02-07T07:00 to 2024-07-20T11:00 (3941 records)
- **Test (15%)**: 2024-07-20T12:00 to 2024-12-31T17:00 (3942 records)

---

## 1. Model Comparison Matrix

| Task | Model | Type | Accuracy | F1 Score | Dangerous Event Recall | MAE | RMSE | R² |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Rainfall Classification | Dummy (Most Frequent) | BASELINE | 0.9112 | 0.8689 | 0.0% | - | - | - |
| Rainfall Classification | Logistic Regression | BASELINE | 0.9178 | 0.8971 | 10.4% | - | - | - |
| Rainfall Classification | Gradient Boosting | CANDIDATE | 0.9066 | 0.8941 | 18.8% | - | - | - |
| Rainfall Classification | Balanced Random Forest | **SELECTED** | **0.8661** | **0.8798** | **18.8%** | - | - | - |
| Rainfall Volume (6h) | Dummy (Mean) | BASELINE | - | - | - | 1.99 mm | 5.23 mm | -0.0186 |
| Rainfall Volume (6h) | Ridge Regression | BASELINE | - | - | - | 1.68 mm | 4.15 mm | 0.3579 |
| Rainfall Volume (6h) | Gradient Boosting | **SELECTED** | - | - | - | **1.6 mm** | **4.15 mm** | **0.3593** |
| Rainfall Volume (6h) | Random Forest Regressor | CANDIDATE | - | - | - | 1.59 mm | 3.99 mm | 0.4079 |

---

## 2. False Negative Analysis for Severe Events

For disaster risk operations, a false negative (failing to alert for a severe storm) carries severe humanitarian risk.
- **Total Test Dangerous Events (HIGH/EXTREME)**: 48 events
- **Missed Dangerous Events**: 39 events
- **Dangerous Event Recall**: 18.75%

---

## 3. Top Model Feature Contributors

### Heavy Rainfall Classifier
[
  [
    "rainfall_24h",
    0.1761
  ],
  [
    "wind_speed",
    0.1556
  ],
  [
    "pressure",
    0.1556
  ],
  [
    "rainfall_12h",
    0.1182
  ],
  [
    "rainfall_6h",
    0.0869
  ]
]

### Rainfall Volume Regressor
[
  [
    "wind_speed",
    0.4425
  ],
  [
    "rainfall_1h",
    0.1241
  ],
  [
    "pressure",
    0.0946
  ],
  [
    "rainfall_24h",
    0.087
  ],
  [
    "temperature",
    0.0672
  ]
]

---

## 4. Scientific Honesty & Boundaries
Flood Inundation & Water Depth models (`flood_classifier_v1`, `flood_depth_regressor_v1`) are retained as **calibrated synthetic prototypes** because open atmospheric reanalysis does not include physical river streamflow or municipal gauge depth measurements.
