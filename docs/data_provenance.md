# DisasterGuard — Data Provenance & Scientific Lineage

## Comprehensive Provenance Documentation for Machine Learning Datasets

**Last Updated**: 2026-09-08T20:10:00+00:00  
**Compliance Standard**: AI-DisasterGuard Scientific Honesty Protocol (Phase 5.1)

---

## 1. Real Historical Meteorological Dataset

### 1.1 Dataset Identification
- **Dataset Name**: Chennai Regional Historical Meteorological Dataset (ECMWF ERA5-Land Reanalysis)
- **Dataset File**: `ml/datasets/historical_weather_chennai_2022_2024.csv`
- **Engineered Feature File**: `ml/datasets/engineered_historical_features.csv`
- **Dataset Category**: `REAL_HISTORICAL`

### 1.2 Source & Provenance
- **Source Organization**: European Centre for Medium-Range Weather Forecasts (ECMWF) & Copernicus Climate Change Service (C3S), accessed via Open-Meteo Historical Weather Archive API
- **Source API URL**: `https://archive-api.open-meteo.com/v1/archive`
- **Documentation Reference**: ECMWF ERA5-Land documentation (`https://confluence.ecmwf.int/display/CKB/ERA5-Land`)
- **Access / Ingestion Date**: 2026-09-06T12:00:00Z
- **License / Terms**: Creative Commons Attribution 4.0 International (CC BY 4.0) via Copernicus Climate Change Service & Open-Meteo terms of use.

### 1.3 Geographical Coverage
- **Location**: Chennai Metropolitan Region, Tamil Nadu, South India
- **Coordinates**: Latitude: 13.0827°N, Longitude: 80.2707°E
- **Elevation**: 12.0 meters above mean sea level
- **Spatial Grid**: ERA5-Land ~9 km native grid cell interpolated to metropolitan coordinates.

### 1.4 Temporal Coverage & Resolution
- **Start Timestamp**: `2022-01-01T00:00:00Z`
- **End Timestamp**: `2024-12-31T23:00:00Z`
- **Span**: 3 full consecutive calendar years (1,096 days)
- **Temporal Resolution**: 1-hour consecutive sampling
- **Total Ingested Observations**: 26,304 rows
- **Timezone**: Coordinated Universal Time (UTC)

### 1.5 Variables, Units & Sensor Ranges
| Variable | CSV Column Name | Units | Range in Dataset | Physical Description |
| :--- | :--- | :--- | :--- | :--- |
| Timestamp | `timestamp` | ISO-8601 UTC | 2022-01-01 to 2024-12-31 | Chronological observation time |
| Temperature | `temperature_c` | °C | 18.5 – 41.8 | Ambient air temperature at 2 meters |
| Relative Humidity | `humidity_pct` | % | 24.0 – 100.0 | Surface relative humidity at 2 meters |
| Total Precipitation | `precipitation_mm` | mm/h | 0.0 – 68.4 | Total liquid water equivalent per hour |
| Rain | `rain_mm` | mm/h | 0.0 – 68.4 | Large-scale and convective rainfall |
| Surface Pressure | `surface_pressure_hpa` | hPa | 991.4 – 1018.6 | Barometric pressure at terrain surface |
| Wind Speed | `wind_speed_kmh` | km/h | 1.8 – 58.2 | Sustained wind velocity at 10 meters |
| Weather Code | `weather_code` | WMO code | 0 – 95 | World Meteorological Organization condition code |

### 1.6 Missing Value Behavior & Data Quality
- **Missing Value Percentage**: 0.0% (0 missing values across all 26,304 records).
- **Quality Assurance**: Validated by `ml/preprocessing/quality_check.py`. All temperatures (-10°C to 60°C), pressures (850 to 1080 hPa), humidity (0 to 100%), and precipitation (>= 0.0 mm) fall strictly within physical domain boundaries.
- **Extreme Events Integrity**: Extreme precipitation events (e.g. Cyclone Michaung December 2023 peak of 68.4 mm/h) are verified and preserved without clipping or outlier removal.

### 1.7 Preprocessing & Feature Engineering Performed
- Strictly backward-looking lags: `rainfall_1h`, `rainfall_3h`, `rainfall_6h`, `rainfall_12h`, `rainfall_24h`.
- Atmospheric trend dynamics: `pressure_change_3h` = P(t) - P(t-3), `humidity_trend_3h` = H(t) - H(t-3).
- Forward-looking targets:
  - `predicted_rainfall_6h_mm`: Cumulative precipitation from hour t to t+6.
  - `rainfall_category`: Categorized into `LOW` (<5 mm), `MODERATE` (5-20 mm), `HIGH` (20-50 mm), `EXTREME` (>=50 mm).
- Trimming: First 24 hours dropped (insufficient lag history), final 6 hours dropped (lacking future target). Net engineered records: 26,274.
- Chronological Split: 70% Train (18,391), 15% Validation (3,941), 15% Test (3,942).

### 1.8 Known Scientific Limitations
1. **Atmospheric Scope**: The dataset measures atmospheric precipitation and thermodynamics. It does **not** include localized storm drain clog data, river channel depths, or municipal flood gate discharges.
2. **Reanalysis Inherent Smoothing**: Reanalysis products assimilate ground stations, radar, and satellites, which can slightly underestimate hyper-localized convective micro-burst peaks.
3. **No Direct Flood Inundation Labels**: Flood inundation is a hydrological consequence of rainfall, topography, and drainage, not an atmospheric variable. Therefore, flood depth modeling cannot be claimed to be validated on real ground truth without in-situ gauge records.

---

## 2. Synthetic Prototype Dataset

### 2.1 Dataset Identification
- **Dataset Name**: Physically-Modeled Synthetic Hydrological Prototype Dataset
- **Dataset File**: `ml/datasets/disaster_training_data.csv`
- **Dataset Category**: `SYNTHETIC_PROTOTYPE`
- **Generator**: `ml/datasets/generate_dataset.py` (Fixed seed 42)

### 2.2 Role & Provenance
- **Provider**: Internal deterministic physics simulator (`generate_dataset.py`).
- **Record Count**: 3,500 synthetic scenario vectors.
- **Role in DisasterGuard**:
  - Serves as the prototype baseline for topographical runoff and water-depth modeling (`flood_classifier_v1`, `flood_depth_regressor_v1`).
  - Preserved for disaster simulation drills and comparative benchmarking.
  - Distinctly labeled in all UI panels and model registries with `model_source: "SYNTHETIC"` and `data_source_type: "synthetic_prototype"`.
- **Variables**: 9 physical features including elevation, slope, drainage proximity, soil saturation, and river distance.

### 2.3 Scientific Honesty Disclaimer
> [!WARNING]
> Models trained on `disaster_training_data.csv` represent **calibrated prototypes**, NOT empirically validated ground truth. The Command Centre UI and API responses explicitly disclose this distinction.
