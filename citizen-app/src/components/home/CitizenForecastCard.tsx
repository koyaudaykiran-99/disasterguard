import { API_BASE_URL } from "../../services/apiConfig";
import React, { useState, useEffect } from 'react';
import { Compass, TrendingUp, AlertTriangle, ShieldCheck, ChevronDown, ChevronUp, Clock, Info } from 'lucide-react';

export const CitizenForecastCard: React.FC = () => {
  const [forecast, setForecast] = useState<any>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/forecast/current?latitude=13.0827&longitude=80.2707`)
      .then((res) => res.json())
      .then((data) => setForecast(data))
      .catch((err) => console.error('Failed to load citizen forecast:', err));
  }, []);

  const currentRisk = forecast?.current?.risk_score ?? 48;
  const currentLevel = forecast?.current?.risk_level ?? 'MODERATE';
  const peakRisk = forecast?.trajectory?.peak_risk ?? 78;
  const peakHorizon = forecast?.trajectory?.peak_horizon ?? '6H';
  const trajectory = forecast?.trajectory?.trajectory ?? 'INCREASING';
  const warningState = forecast?.early_warning?.warning_state ?? 'ADVISORY';
  const headline = forecast?.early_warning?.headline ?? 'Elevated flood risk projected in next 6 hours';
  const confidence = Math.round((forecast?.uncertainty_overview?.average_confidence ?? 0.70) * 100);

  const isElevated = trajectory.includes('INCREASING') || warningState === 'WARNING' || warningState === 'CRITICAL';

  return (
    <div className="mx-4 mb-4 p-4 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 border border-cyan-500/20 shadow-xl text-slate-100">
      {/* Top Title & Indicator */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white tracking-wide">
              EARLY-WARNING RISK FORECAST
            </h4>
            <p className="text-[11px] text-slate-400">
              Chennai Metropolitan Area • Multi-Horizon Predictive Estimate
            </p>
          </div>
        </div>

        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
          isElevated
            ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
            : 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300'
        }`}>
          {trajectory}
        </span>
      </div>

      {/* Main 4 Plain-Language Questions */}
      <div className="space-y-2.5 my-3 text-xs bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
        <div className="flex items-start gap-2">
          <span className="font-bold text-cyan-400 w-16 shrink-0">WHAT:</span>
          <span className="text-slate-200 font-medium">
            Current Risk is <span className="font-bold">{currentLevel} ({currentRisk}/100)</span>. Risk is projected to peak at <span className="text-amber-400 font-bold">{peakRisk}/100</span>.
          </span>
        </div>

        <div className="flex items-start gap-2">
          <span className="font-bold text-cyan-400 w-16 shrink-0">WHEN:</span>
          <span className="text-slate-200">
            Highest anticipated risk window is <span className="font-bold text-amber-300">within the next {peakHorizon}</span>.
          </span>
        </div>

        <div className="flex items-start gap-2">
          <span className="font-bold text-cyan-400 w-16 shrink-0">WHERE:</span>
          <span className="text-slate-200">
            Low-lying residential zones and areas adjacent to primary drainage canals.
          </span>
        </div>

        <div className="flex items-start gap-2">
          <span className="font-bold text-emerald-400 w-16 shrink-0">ACTION:</span>
          <span className="text-emerald-300 font-medium">
            Move essential documents to higher ground. Charge emergency devices. Keep clear of drainage underpasses.
          </span>
        </div>
      </div>

      {/* Details Toggle */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="w-full flex items-center justify-between text-[11px] font-mono text-slate-400 hover:text-cyan-400 pt-1 transition-colors"
      >
        <span>Forecast Confidence: {confidence}% (Horizon Decay Active)</span>
        <div className="flex items-center gap-1">
          <span>{showDetails ? 'Hide technical factors' : 'View technical factors'}</span>
          {showDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {/* Collapsible Details */}
      {showDetails && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] font-mono text-slate-400 space-y-1.5">
          <div className="flex justify-between">
            <span>Forecast Model:</span>
            <span className="text-slate-200 font-semibold">forecast_v1 (Explainable Engine)</span>
          </div>
          <div className="flex justify-between">
            <span>Depth Metric:</span>
            <span className="text-amber-300 font-semibold">PROXY_ESTIMATE (Not 2D Simulation)</span>
          </div>
          <div className="flex justify-between">
            <span>Early Warning State:</span>
            <span className="text-cyan-300 font-semibold">{warningState}</span>
          </div>
          <p className="text-[10px] text-slate-500 pt-1">
            * Predictive risk estimate intended to support preparedness. Official emergency directives remain under government authority.
          </p>
        </div>
      )}
    </div>
  );
};
