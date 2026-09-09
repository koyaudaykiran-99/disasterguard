import React from 'react';
import { SafetyStatus } from '../../types';
import { getRiskTheme } from '../../lib/theme';
import { RiskScore } from '../motion/RiskScore';
import { DataFreshnessBadge } from '../connectivity/DataFreshnessBadge';
import { useConnectivity } from '../../hooks/useConnectivity';
import { ShieldCheck, AlertCircle } from 'lucide-react';

interface HeroSafetyCardProps {
  status: SafetyStatus;
  timestamp?: string | number;
}

export const HeroSafetyCard: React.FC<HeroSafetyCardProps> = ({
  status,
  timestamp = Date.now(),
}) => {
  const theme = getRiskTheme(status.score);
  const { isOffline } = useConnectivity();

  return (
    <div
      className={`w-full rounded-3xl p-5 border bg-gradient-to-b ${theme.cardGrad} ${theme.borderClass} ${theme.pulseClass} transition-all duration-700 shadow-2xl relative overflow-hidden`}
    >
      {/* Background ambient radial glow */}
      <div
        className="absolute -top-16 -right-16 w-48 h-48 rounded-full blur-3xl pointer-events-none"
        style={{ backgroundColor: theme.bgGlow }}
      />

      {/* Card Header Tag & Freshness Badge */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-mono uppercase tracking-widest text-citizen-text-muted font-bold">
            Your Safety Status
          </span>
          <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: theme.colorHex }} />
        </div>

        <DataFreshnessBadge timestamp={timestamp} />
      </div>

      {/* Core Center Layout: Risk Gauge + Concise Summary */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-5 my-1">
        
        {/* Animated Semicircular Gauge (Springs 0 -> 18) */}
        <div className="shrink-0 flex justify-center">
          <RiskScore score={status.score} size={150} strokeWidth={11} />
        </div>

        {/* Reassuring Context Narrative */}
        <div className="flex flex-col justify-center text-center sm:text-left space-y-1.5">
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center justify-center sm:justify-start gap-1.5">
            <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
            <span>{status.headline}</span>
          </h2>
          <p className="text-xs text-citizen-text-secondary leading-relaxed font-normal max-w-xs">
            {status.message}
          </p>
          <div className="pt-1 flex items-center justify-center sm:justify-start space-x-2 text-[11px] font-mono text-citizen-text-muted">
            <span>AI Model Confidence:</span>
            <span className="text-cyan-400 font-semibold">94.2%</span>
          </div>
        </div>
      </div>

      {/* Offline Stale Data Notice */}
      {isOffline && (
        <div className="mt-3 p-2 rounded-xl bg-amber-950/40 border border-amber-800/40 flex items-center space-x-2 text-[10px] font-mono text-amber-300/90">
          <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>Offline Mode: Displaying last verified regional risk index. Data may be outdated.</span>
        </div>
      )}

      {/* Factor Breakdown Snapshot Row */}
      <div className="mt-4 pt-3.5 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-left">
        {status.factors.slice(0, 2).map((factor, idx) => (
          <div
            key={idx}
            className="p-2 rounded-xl bg-slate-950/40 border border-slate-800/60 font-mono text-[11px]"
          >
            <span className="text-citizen-text-muted block text-[10px] truncate">{factor.name}</span>
            <span className="font-semibold text-citizen-text-primary truncate block mt-0.5">
              {factor.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
