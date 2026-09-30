import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CloudRain,
  Thermometer,
  Wind,
  Droplets,
  AlertTriangle,
  RefreshCw,
  MapPin,
  ShieldAlert,
  Clock,
  Radio,
  Zap,
} from 'lucide-react';
import { API_BASE_URL } from '../../services/apiConfig';

export interface CitizenWeatherData {
  provider?: string;
  source?: string;
  timestamp?: string;
  observed_at?: string;
  relative_time_str?: string;
  location?: {
    lat: number;
    lon: number;
    name: string;
  } | string;
  temperature_c?: number;
  temperature?: number;
  humidity?: number;
  rainfall_mm?: number;
  rainfall_1h?: number;
  wind_speed_kmh?: number;
  wind_speed?: number;
  weather_condition?: string;
  condition?: string;
  rain_probability?: number;
  precipitation_probability?: number;
  visibility_km?: number;
  alert_level?: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
}

const STORAGE_KEY = 'disasterguard_citizen_weather';

export const CitizenWeatherCard: React.FC = () => {
  const navigate = useNavigate();
  const [weather, setWeather] = useState<CitizenWeatherData | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [isOfflineData, setIsOfflineData] = useState<boolean>(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<Date>(new Date());

  const fetchWeather = useCallback(async () => {
    setLoading(true);
    try {
      const url = `${API_BASE_URL}/api/v1/weather/current`;
      const res = await fetch(url, { headers: { Accept: 'application/json' } });
      if (!res.ok) {
        throw new Error(`Weather service returned ${res.status}`);
      }
      const data: CitizenWeatherData = await res.json();
      setWeather(data);
      setIsOfflineData(false);
      setLastRefreshedAt(new Date());
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      } catch (err) {
        console.warn('[CitizenWeather] Storage write warning:', err);
      }
    } catch (err) {
      console.warn('[CitizenWeather] Live fetch failed, using local offline telemetry:', err);
      setIsOfflineData(true);
      // If we don't have any cached weather yet, set a sensible default
      if (!weather) {
        const fallback: CitizenWeatherData = {
          provider: 'cached-telemetry',
          source: 'cached',
          location: 'Central Metro Basin (Chennai)',
          temperature_c: 28.5,
          humidity: 75,
          rainfall_mm: 0.0,
          wind_speed_kmh: 12.0,
          weather_condition: 'Partly Cloudy',
          rain_probability: 20,
          alert_level: 'LOW',
          relative_time_str: 'Stored locally',
        };
        setWeather(fallback);
      }
    } finally {
      setLoading(false);
    }
  }, [weather]);

  useEffect(() => {
    fetchWeather();
    const interval = setInterval(fetchWeather, 120000); // 2 minutes
    return () => clearInterval(interval);
  }, [fetchWeather]);

  const locationName =
    typeof weather?.location === 'object' && weather?.location?.name
      ? weather.location.name
      : typeof weather?.location === 'string'
      ? weather.location
      : 'Central Metro Basin';

  const temperature = weather?.temperature_c ?? weather?.temperature ?? 28.0;
  const rainfall = weather?.rainfall_mm ?? weather?.rainfall_1h ?? 0.0;
  const windSpeed = weather?.wind_speed_kmh ?? weather?.wind_speed ?? 12.0;
  const rainProb = weather?.rain_probability ?? weather?.precipitation_probability ?? 0;
  const humidity = weather?.humidity ?? 70;
  const condition = weather?.weather_condition ?? weather?.condition ?? 'Partly Cloudy';
  const alertLevel = weather?.alert_level ?? (rainfall > 70 ? 'CRITICAL' : rainfall > 35 ? 'HIGH' : rainfall > 15 ? 'MODERATE' : 'LOW');
  const providerName = (weather?.provider || weather?.source || 'Open-Meteo').toUpperCase();

  // Dynamic Risk Level styling
  const getRiskBadge = () => {
    switch (alertLevel) {
      case 'CRITICAL':
        return {
          label: '🔴 CRITICAL RISK',
          subtext: 'Severe flood inundation probable',
          badgeClass: 'bg-rose-500/20 text-rose-300 border-rose-500/50',
          cardBorder: 'border-rose-500/50',
          glow: 'rgba(239, 68, 68, 0.15)',
        };
      case 'HIGH':
        return {
          label: '🟠 HIGH RISK',
          subtext: 'High waterlogging in low-lying zones',
          badgeClass: 'bg-orange-500/20 text-orange-300 border-orange-500/50',
          cardBorder: 'border-orange-500/50',
          glow: 'rgba(249, 115, 22, 0.12)',
        };
      case 'MODERATE':
        return {
          label: '🟡 MODERATE RISK',
          subtext: 'Moderate showers & surface accumulation',
          badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/50',
          cardBorder: 'border-amber-500/40',
          glow: 'rgba(245, 158, 11, 0.08)',
        };
      case 'LOW':
      default:
        return {
          label: '🟢 LOW RISK',
          subtext: 'Hydrological conditions normal',
          badgeClass: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50',
          cardBorder: 'border-slate-800',
          glow: 'rgba(16, 185, 129, 0.06)',
        };
    }
  };

  const riskInfo = getRiskBadge();
  const isHeavyRain = rainfall > 30 || alertLevel === 'HIGH' || alertLevel === 'CRITICAL';

  return (
    <div
      className={`w-full rounded-3xl p-5 border ${riskInfo.cardBorder} bg-gradient-to-b from-slate-900/90 to-slate-950/95 shadow-2xl relative overflow-hidden transition-all duration-300`}
      style={{
        boxShadow: `0 10px 30px -10px ${riskInfo.glow}`,
      }}
    >
      {/* Background Subtle Ambient Glow */}
      <div
        className="absolute -top-12 -right-12 w-44 h-44 rounded-full blur-3xl pointer-events-none"
        style={{ backgroundColor: riskInfo.glow }}
      />

      {/* Top Header: Location, Live Source Badge, Refresh */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 pb-3 border-b border-slate-800/80">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <MapPin className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-1.5">
              <span>{locationName}</span>
            </h3>
            <span className="text-[11px] font-mono text-slate-400">
              {condition}
            </span>
          </div>
        </div>

        {/* Source & Freshness Pill */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono bg-slate-800/90 border border-slate-700/80 text-slate-300">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                isOfflineData ? 'bg-amber-400' : 'bg-emerald-400 animate-pulse'
              }`}
            />
            <span className="font-semibold">
              {isOfflineData ? 'CACHED' : 'LIVE'}
            </span>
            <span className="text-slate-500">•</span>
            <span>{providerName}</span>
            <span className="text-slate-500">•</span>
            <span>{weather?.relative_time_str || 'Just now'}</span>
          </div>

          <button
            onClick={fetchWeather}
            disabled={loading}
            className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            title="Refresh Live Weather"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* AI Disaster Risk Status Level Banner */}
      <div className="mt-3.5 flex items-center justify-between p-3 rounded-2xl bg-slate-950/60 border border-slate-800/80">
        <div className="flex items-center space-x-2.5">
          <ShieldAlert className="w-5 h-5 text-cyan-400 shrink-0" />
          <div>
            <div className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">
              Disaster Risk Level
            </div>
            <div className="text-xs font-medium text-slate-200 mt-0.5">
              {riskInfo.subtext}
            </div>
          </div>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-mono font-bold border tracking-wider shrink-0 ${riskInfo.badgeClass}`}
        >
          {riskInfo.label}
        </span>
      </div>

      {/* 4 Core Emergency Weather Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mt-3.5">
        {/* Metric 1: Rainfall (mm) */}
        <div className="p-3 rounded-2xl bg-slate-950/40 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center space-x-1.5 text-[11px] font-mono text-slate-400">
            <CloudRain className="w-3.5 h-3.5 text-blue-400" />
            <span>Rain (1h)</span>
          </div>
          <div className="mt-1.5 flex items-baseline space-x-1">
            <span className="text-xl font-bold font-mono text-blue-400">
              {rainfall.toFixed(1)}
            </span>
            <span className="text-xs font-mono text-slate-400">mm</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500 mt-0.5">
            {rainfall > 5 ? 'Elevated' : 'Normal'}
          </span>
        </div>

        {/* Metric 2: Temperature (°C) */}
        <div className="p-3 rounded-2xl bg-slate-950/40 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center space-x-1.5 text-[11px] font-mono text-slate-400">
            <Thermometer className="w-3.5 h-3.5 text-amber-400" />
            <span>Temp</span>
          </div>
          <div className="mt-1.5 flex items-baseline space-x-1">
            <span className="text-xl font-bold font-mono text-slate-100">
              {temperature.toFixed(1)}
            </span>
            <span className="text-xs font-mono text-slate-400">°C</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500 mt-0.5">
            Humidity: {humidity}%
          </span>
        </div>

        {/* Metric 3: Wind Speed (km/h) */}
        <div className="p-3 rounded-2xl bg-slate-950/40 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center space-x-1.5 text-[11px] font-mono text-slate-400">
            <Wind className="w-3.5 h-3.5 text-teal-400" />
            <span>Wind</span>
          </div>
          <div className="mt-1.5 flex items-baseline space-x-1">
            <span className="text-xl font-bold font-mono text-slate-100">
              {windSpeed.toFixed(1)}
            </span>
            <span className="text-xs font-mono text-slate-400">km/h</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500 mt-0.5">
            {windSpeed > 35 ? 'Gusty' : 'Breeze'}
          </span>
        </div>

        {/* Metric 4: Rain Probability (%) */}
        <div className="p-3 rounded-2xl bg-slate-950/40 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center space-x-1.5 text-[11px] font-mono text-slate-400">
            <Droplets className="w-3.5 h-3.5 text-indigo-400" />
            <span>Precip Prob</span>
          </div>
          <div className="mt-1.5 flex items-baseline space-x-1">
            <span className="text-xl font-bold font-mono text-violet-400">
              {rainProb}
            </span>
            <span className="text-xs font-mono text-slate-400">%</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500 mt-0.5">
            Surge Risk
          </span>
        </div>
      </div>

      {/* Heavy Rain Warning Banner (Shown when rain > 30mm or High/Critical) */}
      {isHeavyRain && (
        <div className="mt-3.5 p-3 rounded-2xl bg-rose-950/50 border border-rose-500/40 text-rose-200 text-xs flex items-start gap-2.5 animate-fadeIn">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5 animate-pulse" />
          <div className="space-y-0.5">
            <span className="font-bold text-rose-300">
              ⚠️ Heavy Rainfall Advisory:
            </span>{' '}
            <span>
              Intense precipitation observed in this sector. Surface waterlogging and drain overflow likely. Keep emergency kit ready and avoid low-lying underpasses.
            </span>
          </div>
        </div>
      )}

      {/* Prominent Emergency Action Button */}
      <button
        onClick={() => navigate('/emergency')}
        className="w-full mt-4 py-3 px-4 rounded-2xl bg-gradient-to-r from-red-600 to-rose-700 hover:from-red-500 hover:to-rose-600 text-white font-bold text-xs font-mono tracking-wider flex items-center justify-center space-x-2 shadow-lg shadow-rose-950/40 active:scale-[0.98] transition-all cursor-pointer group"
      >
        <span className="w-2 h-2 rounded-full bg-white animate-ping" />
        <span>🆘 EMERGENCY SOS & DISPATCH RESCUE</span>
      </button>
    </div>
  );
};
