import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import httpx
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger("disasterguard.weather")

WMO_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

class NormalizedWeatherData(BaseModel):
    location: str = "Regional Monitoring Center"
    latitude: float
    longitude: float
    rainfall_1h: float = Field(default=0.0, ge=0.0)
    rainfall_3h: float = Field(default=0.0, ge=0.0)
    rainfall_6h: float = Field(default=0.0, ge=0.0)
    rainfall_24h: float = Field(default=0.0, ge=0.0)
    temperature: float = Field(default=28.0)
    humidity: float = Field(default=60.0, ge=0.0, le=100.0)
    wind_speed: float = Field(default=10.0, ge=0.0)
    pressure: float = Field(default=1012.0)
    condition: str = "Clear"
    precipitation_probability: Optional[float] = 0.0
    source: str = "real"  # "real", "cached", "mock", "simulation"
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_demo: bool = False

    class Config:
        from_attributes = True

class WeatherProviderError(Exception):
    """Base exception for weather provider issues."""
    pass

class WeatherProvider(ABC):
    """Abstract Base Class for weather data providers."""

    @abstractmethod
    async def get_current_weather(
        self, latitude: float, longitude: float, location_name: Optional[str] = None
    ) -> NormalizedWeatherData:
        """Fetch current weather observation for specified coordinates."""
        pass

    @abstractmethod
    async def get_forecast(
        self, latitude: float, longitude: float, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Fetch weather forecast for specified coordinates."""
        pass

class RealWeatherProvider(WeatherProvider):
    """
    Real-world meteorological provider.
    Primary: Open-Meteo API (zero-key academic/prototype friendly).
    Secondary: OpenWeatherMap (if WEATHER_API_KEY is configured).
    """

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def _validate_coords(self, latitude: float, longitude: float) -> None:
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")

    async def get_current_weather(
        self, latitude: float, longitude: float, location_name: Optional[str] = None
    ) -> NormalizedWeatherData:
        self._validate_coords(latitude, longitude)
        
        # Check if user has an OpenWeatherMap key configured
        if settings.WEATHER_API_KEY and "openweather" in settings.WEATHER_API_BASE_URL.lower():
            return await self._fetch_openweather(latitude, longitude, location_name)
        
        return await self._fetch_open_meteo(latitude, longitude, location_name)

    async def _fetch_open_meteo(
        self, latitude: float, longitude: float, location_name: Optional[str] = None
    ) -> NormalizedWeatherData:
        endpoint = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": round(latitude, 4),
            "longitude": round(longitude, 4),
            "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,surface_pressure,wind_speed_10m",
            "hourly": "precipitation,precipitation_probability",
            "forecast_days": 2,
            "timezone": "auto"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(endpoint, params=params)
                if resp.status_code != 200:
                    raise WeatherProviderError(f"Open-Meteo returned status {resp.status_code}: {resp.text}")
                data = resp.json()
        except httpx.RequestError as exc:
            logger.warning(f"Open-Meteo network error for coords ({latitude}, {longitude}): {exc}")
            raise WeatherProviderError(f"Network error contacting weather API: {exc}")

        current = data.get("current", {})
        hourly = data.get("hourly", {})

        # Cumulative rainfall calculation from hourly series
        hourly_precip = hourly.get("precipitation", [])
        precip_prob = hourly.get("precipitation_probability", [])
        
        rain_1h = float(current.get("rain") or current.get("precipitation") or 0.0)
        
        # Sum 3h, 6h, 24h precipitation from hourly series if available
        rain_3h = float(sum(hourly_precip[:3])) if len(hourly_precip) >= 3 else rain_1h * 3
        rain_6h = float(sum(hourly_precip[:6])) if len(hourly_precip) >= 6 else rain_1h * 6
        rain_24h = float(sum(hourly_precip[:24])) if len(hourly_precip) >= 24 else rain_1h * 24

        weather_code = current.get("weather_code", 0)
        condition_str = WMO_CODE_MAP.get(weather_code, "Partly cloudy")

        current_prob = float(precip_prob[0]) if precip_prob else 0.0

        loc_label = location_name or f"Coords ({round(latitude, 2)}, {round(longitude, 2)})"

        return NormalizedWeatherData(
            location=loc_label,
            latitude=latitude,
            longitude=longitude,
            rainfall_1h=round(max(0.0, rain_1h), 2),
            rainfall_3h=round(max(0.0, rain_3h), 2),
            rainfall_6h=round(max(0.0, rain_6h), 2),
            rainfall_24h=round(max(0.0, rain_24h), 2),
            temperature=float(current.get("temperature_2m", 28.0)),
            humidity=float(current.get("relative_humidity_2m", 65.0)),
            wind_speed=float(current.get("wind_speed_10m", 12.0)),
            pressure=float(current.get("surface_pressure", 1010.0)),
            condition=condition_str,
            precipitation_probability=current_prob,
            source="real",
            observed_at=datetime.now(timezone.utc),
            is_demo=False
        )

    async def _fetch_openweather(
        self, latitude: float, longitude: float, location_name: Optional[str] = None
    ) -> NormalizedWeatherData:
        endpoint = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": settings.WEATHER_API_KEY,
            "units": "metric"
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(endpoint, params=params)
                if resp.status_code != 200:
                    raise WeatherProviderError(f"OpenWeatherMap returned {resp.status_code}")
                data = resp.json()
        except httpx.RequestError as exc:
            raise WeatherProviderError(f"OpenWeatherMap network error: {exc}")

        main = data.get("main", {})
        wind = data.get("wind", {})
        rain = data.get("rain", {})
        weather_list = data.get("weather", [{}])
        cond = weather_list[0].get("main", "Clear") if weather_list else "Clear"

        rain_1h = float(rain.get("1h", 0.0))

        return NormalizedWeatherData(
            location=location_name or data.get("name", f"Coords ({latitude}, {longitude})"),
            latitude=latitude,
            longitude=longitude,
            rainfall_1h=rain_1h,
            rainfall_3h=rain_1h * 2.5,
            rainfall_6h=rain_1h * 4.5,
            rainfall_24h=rain_1h * 12.0,
            temperature=float(main.get("temp", 28.0)),
            humidity=float(main.get("humidity", 65.0)),
            wind_speed=float(wind.get("speed", 10.0) * 3.6), # m/s to km/h
            pressure=float(main.get("pressure", 1012.0)),
            condition=cond,
            precipitation_probability=float(rain_1h > 0) * 80.0,
            source="real",
            observed_at=datetime.now(timezone.utc),
            is_demo=False
        )

    async def get_forecast(
        self, latitude: float, longitude: float, hours: int = 24
    ) -> List[Dict[str, Any]]:
        self._validate_coords(latitude, longitude)
        endpoint = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": round(latitude, 4),
            "longitude": round(longitude, 4),
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
            "forecast_days": 2,
            "timezone": "auto"
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(endpoint, params=params)
                if resp.status_code == 200:
                    data = resp.json().get("hourly", {})
                    times = data.get("time", [])[:hours]
                    precips = data.get("precipitation", [])[:hours]
                    temps = data.get("temperature_2m", [])[:hours]
                    codes = data.get("weather_code", [])[:hours]
                    return [
                        {
                            "time": times[i],
                            "precipitation_mm": precips[i] if i < len(precips) else 0.0,
                            "temperature_c": temps[i] if i < len(temps) else 25.0,
                            "condition": WMO_CODE_MAP.get(codes[i], "Clear") if i < len(codes) else "Clear"
                        }
                        for i in range(len(times))
                    ]
        except Exception as e:
            logger.warning(f"Error fetching forecast: {e}")
        return []

class MockWeatherProvider(WeatherProvider):
    """Deterministic mock provider for offline testing and synthetic environments."""

    def __init__(self, base_rain: float = 12.5, condition: str = "Scattered Showers"):
        self.base_rain = base_rain
        self.condition = condition

    async def get_current_weather(
        self, latitude: float, longitude: float, location_name: Optional[str] = None
    ) -> NormalizedWeatherData:
        return NormalizedWeatherData(
            location=location_name or "Chennai Metropolitan Area (Synthetic Sensor)",
            latitude=latitude,
            longitude=longitude,
            rainfall_1h=self.base_rain,
            rainfall_3h=self.base_rain * 2.8,
            rainfall_6h=self.base_rain * 5.2,
            rainfall_24h=self.base_rain * 14.5,
            temperature=27.5,
            humidity=82.0,
            wind_speed=18.5,
            pressure=1008.0,
            condition=self.condition,
            precipitation_probability=75.0,
            source="mock",
            observed_at=datetime.now(timezone.utc),
            is_demo=True
        )

    async def get_forecast(
        self, latitude: float, longitude: float, hours: int = 24
    ) -> List[Dict[str, Any]]:
        return [
            {
                "hour_offset": i,
                "precipitation_mm": max(0.0, self.base_rain * (1.0 - 0.03 * i)),
                "temperature_c": 27.0 + (i % 5),
                "condition": self.condition
            }
            for i in range(hours)
        ]

def get_weather_provider() -> WeatherProvider:
    """Factory returning configured weather provider."""
    provider_type = settings.WEATHER_PROVIDER.strip().lower()
    if provider_type == "real":
        return RealWeatherProvider()
    return MockWeatherProvider()
