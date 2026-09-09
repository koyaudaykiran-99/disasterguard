import React from 'react';
import { useConnectivity } from '../../hooks/useConnectivity';
import { Clock, ShieldCheck, Database } from 'lucide-react';

interface DataFreshnessBadgeProps {
  timestamp: string | number;
  className?: string;
}

export const DataFreshnessBadge: React.FC<DataFreshnessBadgeProps> = ({
  timestamp,
  className = '',
}) => {
  const { getFreshness } = useConnectivity();
  const { freshness, label } = getFreshness(timestamp);

  const styleMap = {
    LIVE: 'text-emerald-400 bg-emerald-500/15 border-emerald-500/30',
    RECENT: 'text-cyan-300 bg-cyan-500/15 border-cyan-500/30',
    CACHED: 'text-amber-300 bg-amber-500/15 border-amber-500/30',
    STALE: 'text-rose-300 bg-rose-500/20 border-rose-500/40',
    OFFLINE: 'text-amber-300 bg-amber-500/15 border-amber-500/30',
  }[freshness];

  const Icon = freshness === 'LIVE' ? ShieldCheck : freshness === 'CACHED' ? Database : Clock;

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider uppercase border ${styleMap} ${className}`}
    >
      <Icon className="w-3 h-3 mr-1 shrink-0" />
      <span>{label}</span>
    </span>
  );
};
