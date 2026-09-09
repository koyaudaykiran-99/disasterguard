import numpy as np
import pandas as pd
import os

def generate_disaster_dataset(num_samples=3500, random_seed=42):
    """
    Generate a physically-grounded synthetic meteorological and hydrological dataset
    for early warning rainfall prediction and flood inundation risk modeling.
    
    DISCLAIMER:
    This dataset is synthetic and designed for prototyping machine learning models.
    It does not represent measured real-world gauge station telemetry.
    """
    np.random.seed(random_seed)
    
    # 1. Atmospheric & Meteorological Features
    # Pressure: baseline 1012 hPa; cyclones/depressions dip to 980-998 hPa
    pressure = np.random.normal(loc=1005.0, scale=8.5, size=num_samples)
    pressure = np.clip(pressure, 978.0, 1022.0)
    
    # Humidity: strongly negative correlated with pressure (low pressure -> saturated air)
    pressure_norm = (1022.0 - pressure) / (1022.0 - 978.0)  # 0 to 1
    humidity = 55.0 + (pressure_norm * 35.0) + np.random.normal(0, 5.0, size=num_samples)
    humidity = np.clip(humidity, 40.0, 99.5)
    
    # Temperature: 22 - 36 C, slightly lower during heavy overcast/rain
    temperature = 33.0 - (pressure_norm * 6.0) + np.random.normal(0, 2.5, size=num_samples)
    temperature = np.clip(temperature, 19.0, 38.0)
    
    # Wind speed: higher when pressure is low (cyclonic gradient)
    wind_speed = 10.0 + (pressure_norm * 45.0) + np.random.exponential(scale=8.0, size=num_samples)
    wind_speed = np.clip(wind_speed, 4.0, 95.0)
    
    # Recent rainfall accumulation
    # Higher baseline if pressure is low and humidity is high
    precip_potential = (pressure_norm * 0.5) + ((humidity - 50.0) / 50.0 * 0.5)
    precip_potential = np.clip(precip_potential, 0.05, 1.0)
    
    rainfall_1h = np.random.exponential(scale=18.0 * precip_potential, size=num_samples)
    rainfall_1h = np.clip(rainfall_1h, 0.0, 75.0)
    
    rainfall_3h = rainfall_1h * (1.8 + np.random.uniform(0.1, 0.9, size=num_samples))
    rainfall_6h = rainfall_3h * (1.4 + np.random.uniform(0.1, 0.8, size=num_samples))
    rainfall_12h = rainfall_6h * (1.3 + np.random.uniform(0.1, 0.7, size=num_samples))
    rainfall_24h = rainfall_12h * (1.2 + np.random.uniform(0.1, 0.6, size=num_samples))
    
    # 2. Geospatial & Hydrological Features
    # Elevation: low-lying coastal basins (1-15m) to elevated ground (15-120m)
    elevation_m = np.random.exponential(scale=18.0, size=num_samples) + 2.0
    elevation_m = np.clip(elevation_m, 1.5, 120.0)
    
    # Slope: degrees
    slope_deg = np.random.exponential(scale=3.5, size=num_samples) + 0.3
    slope_deg = np.clip(slope_deg, 0.2, 28.0)
    
    # Proximity to major river / storm drainage channel (meters)
    drainage_proximity_m = np.random.exponential(scale=380.0, size=num_samples) + 15.0
    drainage_proximity_m = np.clip(drainage_proximity_m, 10.0, 2500.0)
    
    # Soil saturation percentage: influenced by rainfall_24h
    soil_saturation_pct = 35.0 + (np.clip(rainfall_24h, 0, 200) / 200.0 * 55.0) + np.random.normal(0, 5.0, size=num_samples)
    soil_saturation_pct = np.clip(soil_saturation_pct, 20.0, 99.0)
    
    # Historical flood frequency (0-8 events)
    historical_flood_events = np.round((1.0 - np.clip(elevation_m, 0, 50)/50.0) * 5.0 + np.random.poisson(lam=1.0, size=num_samples))
    historical_flood_events = np.clip(historical_flood_events, 0, 8).astype(int)
    
    # 3. Target Formulation (Physically Consistent Ground Truth)
    # Predicted rainfall next 6 hours (continuous mm)
    predicted_rainfall_6h_mm = (
        (pressure_norm * 75.0) +
        ((humidity - 50.0) / 50.0 * 50.0) +
        (rainfall_3h * 0.35) +
        (wind_speed * 0.30) +
        np.random.normal(0, 12.0, size=num_samples)
    )
    predicted_rainfall_6h_mm = np.round(np.clip(predicted_rainfall_6h_mm, 2.0, 260.0), 1)
    
    # Categorical rainfall target
    rainfall_category = []
    for r in predicted_rainfall_6h_mm:
        if r >= 150.0:
            rainfall_category.append("EXTREME")
        elif r >= 90.0:
            rainfall_category.append("HIGH")
        elif r >= 40.0:
            rainfall_category.append("MODERATE")
        else:
            rainfall_category.append("LOW")
    
    # Hydrological runoff index -> Flood Inundation Probability & Depth
    # High rainfall + high soil saturation + low elevation + low slope + close drainage = severe flood
    runoff_score = (
        (predicted_rainfall_6h_mm * 0.30) +
        (rainfall_24h * 0.25) +
        (soil_saturation_pct * 0.25) -
        (elevation_m * 0.60) -
        (slope_deg * 0.80) -
        (drainage_proximity_m * 0.02)
    )
    
    # Sigmoidal calibration to probability [0.05, 0.98]
    flood_prob = 1.0 / (1.0 + np.exp(- (runoff_score - 25.0) / 14.0))
    flood_prob = np.round(np.clip(flood_prob, 0.05, 0.98), 2)
    
    # Inundation depth in meters
    water_depth_m = np.where(
        flood_prob > 0.30,
        np.round(np.clip((flood_prob * 2.2) - (elevation_m * 0.02) + np.random.normal(0, 0.1, size=num_samples), 0.1, 3.4), 2),
        0.0
    )
    
    # Categorical flood risk level
    flood_risk_level = []
    for p, d in zip(flood_prob, water_depth_m):
        if p >= 0.75 or d >= 1.2:
            flood_risk_level.append("CRITICAL")
        elif p >= 0.50 or d >= 0.6:
            flood_risk_level.append("HIGH")
        elif p >= 0.28 or d >= 0.2:
            flood_risk_level.append("MODERATE")
        else:
            flood_risk_level.append("LOW")
            
    df = pd.DataFrame({
        "rainfall_1h": np.round(rainfall_1h, 1),
        "rainfall_3h": np.round(rainfall_3h, 1),
        "rainfall_6h": np.round(rainfall_6h, 1),
        "rainfall_12h": np.round(rainfall_12h, 1),
        "rainfall_24h": np.round(rainfall_24h, 1),
        "temperature": np.round(temperature, 1),
        "humidity": np.round(humidity, 1),
        "pressure": np.round(pressure, 1),
        "wind_speed": np.round(wind_speed, 1),
        "elevation_m": np.round(elevation_m, 1),
        "slope_deg": np.round(slope_deg, 1),
        "drainage_proximity_m": np.round(drainage_proximity_m, 1),
        "soil_saturation_pct": np.round(soil_saturation_pct, 1),
        "historical_flood_events": historical_flood_events,
        "predicted_rainfall_6h_mm": predicted_rainfall_6h_mm,
        "rainfall_category": rainfall_category,
        "flood_probability": flood_prob,
        "water_depth_m": water_depth_m,
        "flood_risk_level": flood_risk_level
    })
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "disaster_training_data.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} samples saved to: {out_path}")
    print("\nTarget Class Distributions:")
    print("Rainfall Category:\n", df['rainfall_category'].value_counts())
    print("\nFlood Risk Level:\n", df['flood_risk_level'].value_counts())

if __name__ == "__main__":
    generate_disaster_dataset()
