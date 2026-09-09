import React, { useState } from 'react';
import { Waves, Mountain, Compass, History, ShieldAlert, ChevronDown, ChevronUp, Info, AlertTriangle } from 'lucide-react';

interface FloodAdvisoryCardProps {
  score?: number;
  level?: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  elevationMeters?: number;
  slopeDegrees?: number;
  nearestWaterBody?: string;
  waterBodyDistanceKm?: number;
  estimatedWaterDepthM?: number;
  historicalContext?: string;
}

export const FloodAdvisoryCard: React.FC<FloodAdvisoryCardProps> = ({
  score = 64,
  level = 'HIGH',
  elevationMeters = 7.2,
  slopeDegrees = 1.1,
  nearestWaterBody = 'Adyar River Basin',
  waterBodyDistanceKm = 0.85,
  estimatedWaterDepthM = 0.55,
  historicalContext = 'Corresponds with 2015 Adyar / 2023 Michaung lowland inundation sector',
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  const getBadgeStyle = () => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/40';
      case 'MODERATE':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    }
  };

  return (
    <div className="w-full rounded-2xl p-4 border border-cyan-900/40 bg-slate-900/80 backdrop-blur-md shadow-lg space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Waves className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-cyan-400 font-bold block">
              Flood & Inundation Advisory
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              Geospatial Terrain & Drainage Analysis
            </span>
          </div>
        </div>

        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${getBadgeStyle()}`}>
          {level} RISK ({score}/100)
        </span>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/80">
          <div className="flex items-center justify-center space-x-1 text-[10px] font-mono text-slate-400">
            <Mountain className="w-3 h-3 text-cyan-400" />
            <span>Elevation</span>
          </div>
          <div className="text-xs font-mono font-bold text-white mt-1">
            {elevationMeters > 0 ? `+${elevationMeters}m MSL` : `${elevationMeters}m MSL`}
          </div>
        </div>

        <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/80">
          <div className="flex items-center justify-center space-x-1 text-[10px] font-mono text-slate-400">
            <Compass className="w-3 h-3 text-amber-400" />
            <span>Slope</span>
          </div>
          <div className="text-xs font-mono font-bold text-white mt-1">
            {slopeDegrees}° (Flat)
          </div>
        </div>

        <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/80">
          <div className="flex items-center justify-center space-x-1 text-[10px] font-mono text-slate-400">
            <Waves className="w-3 h-3 text-blue-400" />
            <span>Proxy Depth</span>
          </div>
          <div className="text-xs font-mono font-bold text-cyan-300 mt-1">
            ~{estimatedWaterDepthM}m
          </div>
        </div>
      </div>

      {/* Drainage Notice */}
      <div className="p-2.5 rounded-xl bg-blue-950/30 border border-blue-900/40 flex items-start space-x-2 text-[11px] font-mono text-blue-200">
        <ShieldAlert className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-white">{nearestWaterBody}</span>: {waterBodyDistanceKm} km away. Low terrain with high runoff potential.
        </div>
      </div>

      {/* Expand/Collapse Historical Memory & Advice */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between text-[11px] font-mono text-slate-400 hover:text-cyan-300 transition-colors pt-1"
      >
        <span className="flex items-center space-x-1">
          <History className="w-3.5 h-3.5 text-cyan-400" />
          <span>Historical Risk Memory & Safety Checklist</span>
        </span>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isExpanded && (
        <div className="space-y-2 pt-2 border-t border-slate-800 text-[11px] font-mono">
          <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800 text-slate-300">
            <span className="text-amber-400 font-bold block mb-0.5">Historical Memory:</span>
            {historicalContext}
          </div>

          <div className="p-2 rounded-lg bg-amber-950/30 border border-amber-900/40 text-amber-200 space-y-1">
            <span className="font-bold text-amber-300 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5" /> Actionable Safety Advice:
            </span>
            <ul className="list-disc list-inside space-y-0.5 text-[10px] text-slate-300 pl-1">
              <li>Do not attempt to cross submerged roads or underpasses.</li>
              <li>Move essential medications and electronics above ground level.</li>
              <li>Locate the nearest designated elevated shelter in the Shelters tab.</li>
              <li>In an emergency, use the SOS button for priority response.</li>
            </ul>
          </div>

          <div className="text-[9px] text-slate-500 flex items-center space-x-1 pt-1">
            <Info className="w-3 h-3 text-slate-400" />
            <span>* Estimated proxy depth is a susceptibility indicator, not a 2D hydraulic simulation.</span>
          </div>
        </div>
      )}
    </div>
  );
};
