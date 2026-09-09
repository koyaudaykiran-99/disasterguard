# DisasterGuard Machine Learning Datasets & Provenance

This directory maintains the training datasets and metadata for DisasterGuard machine learning models, strictly distinguishing between authentic historical observations and synthetic/prototype training data.

---

## 1. Dataset Provenance Inventory

| Dataset Identifier | File Name | Type | Records | Time Window | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_real_era5` | `historical_weather_chennai_2022_2024.csv` | **REAL HISTORICAL METEOROLOGICAL** | 26,304 | 2022-01-01 to 2024-12-31 | ECMWF ERA5-Land via Open-Meteo Archive API |
| `synthetic_prototype` | `disaster_training_data.csv` | **PHYSICALLY-MODELED SYNTHETIC** | 3,500 | N/A (Physically Simulated) | `generate_dataset.py` (Fixed seed 42) |

---

## 2. REAL HISTORICAL DATASET: `historical_weather_chennai_2022_2024.csv`

### 2.1 Metadata & Origin
- **Dataset Name**: Chennai Regional Historical Meteorological Dataset
- **Provider**: Open-Meteo Historical Weather Archive API (`https://archive-api.open-meteo.com/v1/archive`)
- **Underlying Scientific Model**: European Centre for Medium-Range Weather Forecasts (ECMWF) ERA5 / ERA5-Land Reanalysis
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0) via Copernicus Climate Change Service & Open-Meteo
- **Geographic Coverage**:
  - Region: Chennai Metropolitan Area, Tamil Nadu, India
  - Latitude: 13.0827°N, Longitude: 80.2707°E
- **Temporal Coverage**: 2022-01-01T00:00 to 2024-12-31T23:00 (3 full years, 1-hour temporal resolution)
- **Total Records**: 26,304 consecutive hourly observations
- **Missing Values**: 0.0% (Reanalysis quality verified)

### 2.2 Ingested Meteorological Variables
| Variable | Unit | Range in Dataset | Description |
| :--- | :--- | :--- | :--- |
| `timestamp` | ISO-8601 | 2022-01-01 to 2024-12-31 | Observation UTC timestamp |
| `temperature_c` | °C | 18.5 – 41.8 | Surface air temperature at 2m above ground |
| `humidity_pct` | % | 24.0 – 100.0 | Relative surface humidity at 2m |
| `precipitation_mm` | mm | 0.0 – 68.4 | Total precipitation in the preceding hour |
| `rain_mm` | mm | 0.0 – 68.4 | Large-scale and convective rainfall |
| `surface_pressure_hpa` | hPa | 991.4 – 1018.6 | Atmospheric pressure at surface level |
| `wind_speed_kmh` | km/h | 1.8 – 58.2 | Sustained wind speed at 10m above ground |
| `weather_code` | WMO code | 0 – 95 | World Meteorological Organization synoptic code |

### 2.3 Scientific Use in DisasterGuard
- Used to train **Model A (Heavy Rainfall Classifier v2.0)** and **Model B (Rainfall Volume Regressor v2.0)**.
- Ingested via strict **chronological splitting** (70% Train, 15% Validation, 15% Test) to eliminate future data leakage.

---

## 3. SYNTHETIC PROTOTYPE DATASET: `disaster_training_data.csv`

### 3.1 Role & Boundary
- **Records**: 3,500 physically simulated vectors.
- **Role**: Prototyping topographical runoff, slope drainage, and flood-depth estimation.
- **Scientific Honesty Boundary**: Retained for **Model C (Flood Inundation Classifier)** and **Model D (Water Depth Regressor)** because open global meteorological archives do not provide physical river streamflow or municipal gauge depth telemetry. These models are explicitly tagged as `v1.0-prototype` and `training_data="synthetic_prototype"`.

---

## 4. Strict Data Taxonomy Rules

DisasterGuard enforces an explicit 4-tier data taxonomy:

1. **REAL HISTORICAL DATA (`historical_real`)**:
   Authentic meteorological time series used for model training, offline validation, and retrospective verification.
2. **LIVE WEATHER DATA (`live_weather_db`)**:
   Real-time telemetry and current API observations from Open-Meteo ingested into PostgreSQL with a 15-minute cache TTL.
3. **SIMULATION DATA (`simulation`)**:
   Controlled, isolated multi-stage synthetic disaster states used for operator readiness drills. Tagged with `[SIMULATION]`.
4. **SYNTHETIC DATA (`synthetic_prototype`)**:
   Engineered physical scenarios for prototype modeling where live physical gauges do not yet exist.

> [!CAUTION]
> Under no circumstances may synthetic data be labeled as real historical data, nor may simulation events overwrite live historical records.
