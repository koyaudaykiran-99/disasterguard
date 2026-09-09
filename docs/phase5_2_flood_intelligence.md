# AI-DisasterGuard — Phase 5.2: Advanced Flood Intelligence & Geospatial Inundation Specification

## 1. Executive Summary & Scientific Honesty

Phase 5.2 transitions the AI-DisasterGuard platform from a linear `Weather -> Rainfall Prediction -> Risk` heuristic into an integrated multi-factor intelligence pipeline:

```text
Weather Observation / Forecast
  -> Multi-Scale Rainfall (1h, 3h, 6h, 12h, 24h)
  -> Topographic Terrain Features (Elevation, Slope, Relative Elevation)
  -> Hydrographic Drainage Network (Proximity & Bottlenecks)
  -> Historical Flood Risk Memory (Verified Disasters 2015–2023)
  -> Geospatial Flood Susceptibility Score Matrix (0–100)
  -> Proxy Inundation Depth & Extents (PROXY_ESTIMATE)
  -> Multi-Layer GIS Command Map + Real-Time Command Dashboard
  -> Citizen App Flood Advisories
  -> Automated SOS Context Enrichment (Read-Only)
  -> Human Operator Confirmation Barrier (Strict Preservation)
```

### Scientific Honesty Principles
1. **Never Claim 2D Hydrodynamic Modeling**: The system does not claim or simulate shallow water equations (Saint-Venant 2D/HEC-RAS).
2. **Explicit Depth Labeling**: All water depths are classified strictly as `PROXY_ESTIMATE` (`is_hydraulic_simulation: false`).
3. **Transparent Provenance**: All geospatial data outputs are accompanied by provenance metadata (`DataSourceType.REAL_GEOSPATIAL`, `DataSourceType.DERIVED`, `DataSourceType.HISTORICAL_EVENT`, `DataSourceType.MOCK`, `DataSourceType.SIMULATION`).
4. **Structured Categorical Explainability**: Susceptibility scores separate outputs into:
   - `FACT`: Observed meteorological & topographic values
   - `ML_PREDICTION`: Scikit-Learn model forward rainfall projections
   - `GEOSPATIAL_DERIVATION`: Spatial distance, slope, bottleneck, and historical decay scores
   - `AI_INTERPRETATION`: Synthesis of composite indicators
   - `RECOMMENDATION`: Actionable operational suggestions for human operators

---

## 2. Geospatial Provider Architecture (`ml/geospatial/`)

### 2.1 Provider Hierarchy & Provenance
* `BaseGeospatialProvider`: Base class enforcing name, mode, and `get_provenance()` returning `GeospatialProvenance`.
* `DataSourceType`: Strict enum distinguishing:
  - `REAL_OBSERVED`: In-situ physical sensor recordings (WMO weather stations)
  - `REAL_REANALYSIS`: High-resolution physical reanalysis (ERA5-Land)
  - `REAL_GEOSPATIAL`: Direct vector or raster GIS datasets
  - `HISTORICAL_EVENT`: Officially documented and verified disaster records
  - `DERIVED`: Computed composite or statistical derivations
  - `SIMULATION`: Test simulation feeds
  - `MOCK`: Geodetic anchor spatial interpolations

### 2.2 Providers
* **`TerrainProvider`**:
  - Modes: `REAL`, `MOCK`, `SIMULATION`.
  - Calculates ground elevation (m ASL), slope (°), relative elevation against coastal base (6.0m ASL), low-elevation flag (< 6.0m), and terrain risk score (0–100).
  - Greater Chennai anchors: Marina Coastal Shore (3.0m), Pallikaranai Marsh (2.2m), Velachery Lowland (4.5m), Saidapet Adyar (5.8m), T. Nagar (8.5m), Central Station (7.2m), St. Thomas Mount Ridge (42.0m).
* **`DrainageProvider`**:
  - Models major Chennai river basins and drainage channels:
    - Adyar River Basin (1200 m³/s capacity)
    - Cooum River Basin (650 m³/s capacity)
    - Buckingham Canal (280 m³/s capacity)
    - Otteri Nullah Storm Drain (180 m³/s capacity)
    - Pallikaranai Wetland Marsh (850 m³/s capacity)
  - Evaluates distance to nearest watercourse and hydraulic bottleneck vulnerability.
* **`HistoricalFloodProvider`**:
  - Seeds and queries verified disaster records:
    1. December 2015 Catastrophic Chennai Flood (Adyar breach, 494mm rainfall)
    2. December 2023 Cyclone Michaung Inundation (220mm rainfall)
    3. November 2021 Severe Urban Waterlogging (205mm rainfall)
    4. December 2016 Cyclone Vardah Storm Inundation (192mm rainfall)
  - Calculates historical exposure score (0–100) using inverse-distance weighting.
* **`InundationEstimator`**:
  - Generates estimated proxy water depths (0.00m to 2.20m) and bounding footprint GeoJSON polygons.
  - Tags depth explicitly as `PROXY_ESTIMATE`.

---

## 3. Database Schema & Migrations

### 3.1 New Tables
1. `historical_flood_events`:
   - `id`, `event_name`, `event_date`, `latitude`, `longitude`, `severity`, `rainfall_total_mm`, `duration_hours`, `source`, `source_type`, `description`, `created_at`.
2. `flood_intelligence_predictions`:
   - `id`, `timestamp`, `latitude`, `longitude`, `risk_level`, `susceptibility_score`, `estimated_depth_m`, `depth_confidence`, `depth_type`, `affected_area_km2`, `data_source_type`, `model_version`, `explanation`.

### 3.2 Alembic Migration
- Version `d4e5f6a7b8c9`: Added `historical_flood_events` and `flood_intelligence_predictions` tables with spatial index compatibility.

---

## 4. Backend Spatial & REST APIs

Mounted on `/api/v1/flood/`:
* `GET /api/v1/flood/intelligence`: Full multi-factor flood susceptibility and proxy depth.
* `GET /api/v1/flood/inundation`: Proxy water depth, bounding polygon GeoJSON, and disclaimer.
* `GET /api/v1/flood/historical-events`: Verified historical disaster footprints.
* `GET /api/v1/flood/spatial-features`: Topography and drainage metrics for a coordinate.
* `GET /api/v1/flood/zones`: Multi-factor risk zones GeoJSON FeatureCollection for map overlays.

---

## 5. UI Integration

1. **Command Centre**:
   - `FloodIntelligencePanel.tsx`: Interactive dashboard panel with risk gauge, terrain metrics, drainage proximity, historical memory, and categorical explanation modal.
   - `DisasterMap.tsx`: Multi-layer GIS canvas supporting PostGIS inundation polygons, historical disaster circles, and HUD toggles.
2. **Citizen Mobile App**:
   - `FloodAdvisoryCard.tsx`: Reassuring, clear advisory card displaying elevation, slope, nearest river distance, and actionable flood safety instructions.

---

## 6. Safety & Human Operator Confirmation Barrier

* **Zero Auto-Dispatch Rule**: No flood intelligence model or AI emergency tool has the capability or authority to dispatch rescue teams.
* **Verification Gate**: `RescueAssignment == 0` for all newly created SOS reports.
