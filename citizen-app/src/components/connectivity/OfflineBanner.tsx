import React from 'react';
import { useConnectivity } from '../../hooks/useConnectivity';
import { WifiOff, AlertCircle } from 'lucide-react';

export const OfflineBanner: React.FC = () => {
  const { isOffline, isDemoOffline, lastSync } = useConnectivity();

  if (!isOffline) return null;

  return (
    <div className="w-full bg-amber-950/40 border border-amber-500/40 rounded-2xl p-3 flex items-start space-x-3 text-xs font-mono text-amber-200 animate-fadeIn shadow-lg">
      <div className="p-1.5 rounded-lg bg-amber-500/20 text-amber-400 shrink-0 mt-0.5">
        <WifiOff className="w-4 h-4" />
      </div>
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <span className="font-bold text-amber-300 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            {isDemoOffline ? 'Demo Simulation: Offline Blackout' : 'Offline Safety Mode Active'}
          </span>
          <span className="text-[10px] text-amber-400/80">Cached</span>
        </div>
        <p className="text-[11px] text-amber-200/90 mt-0.5 leading-relaxed font-sans">
          Using latest locally persisted safety data from IndexedDB. Last synchronized {lastSync}.
        </p>
      </div>
    </div>
  );
};
