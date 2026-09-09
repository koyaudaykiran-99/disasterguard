import React from 'react';
import { useConnectivity } from '../../hooks/useConnectivity';
import { useLocation } from '../../hooks/useLocation';
import { communicationManager } from '../../services/communication/communicationManager';
import { Wifi, WifiOff, Navigation, Radio, Server, Shield } from 'lucide-react';

export const CommunicationStatus: React.FC = () => {
  const { isOnline, backend, lastSync } = useConnectivity();
  const { hasLocation, isLocating } = useLocation();
  const transports = communicationManager.getStatusOverview();

  return (
    <div className="w-full glass-panel p-3.5 rounded-2xl border border-slate-800 space-y-2.5 font-mono text-xs shadow-md">
      <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase font-bold tracking-widest text-citizen-text-muted flex items-center gap-1.5">
          <Radio className="w-3.5 h-3.5 text-cyan-400" />
          Emergency Communication Health
        </span>
        <span className="text-[10px] text-citizen-text-muted">Synced {lastSync}</span>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center pt-0.5">
        
        {/* Internet */}
        <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/80 flex flex-col items-center justify-center">
          {isOnline ? (
            <Wifi className="w-4 h-4 text-emerald-400 mb-1" />
          ) : (
            <WifiOff className="w-4 h-4 text-amber-400 mb-1" />
          )}
          <span className="text-[9px] text-slate-400 uppercase">Internet</span>
          <span className={`text-[10px] font-bold mt-0.5 ${isOnline ? 'text-emerald-400' : 'text-amber-400'}`}>
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </div>

        {/* Backend Reachability */}
        <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/80 flex flex-col items-center justify-center">
          <Server className={`w-4 h-4 mb-1 ${backend === 'REACHABLE' ? 'text-emerald-400' : 'text-amber-400'}`} />
          <span className="text-[9px] text-slate-400 uppercase">Backend</span>
          <span className={`text-[10px] font-bold mt-0.5 ${backend === 'REACHABLE' ? 'text-emerald-400' : 'text-amber-400'}`}>
            {backend}
          </span>
        </div>

        {/* GPS */}
        <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/80 flex flex-col items-center justify-center">
          <Navigation className={`w-4 h-4 mb-1 ${hasLocation ? 'text-cyan-400' : isLocating ? 'text-amber-400 animate-spin' : 'text-slate-500'}`} />
          <span className="text-[9px] text-slate-400 uppercase">GPS</span>
          <span className="text-[10px] font-bold text-cyan-400 mt-0.5">
            {hasLocation ? 'Locked' : isLocating ? 'Locating' : 'Standby'}
          </span>
        </div>

        {/* Emergency Relay / Gateway */}
        <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/80 flex flex-col items-center justify-center">
          <Shield className="w-4 h-4 text-slate-400 mb-1" />
          <span className="text-[9px] text-slate-400 uppercase">Relay</span>
          <span className="text-[10px] font-bold text-slate-400 mt-0.5">
            {transports.RELAY}
          </span>
        </div>

      </div>

      {!isOnline && (
        <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800 text-[10px] text-slate-300 font-sans text-center leading-normal">
          Emergency requests created offline are safely preserved in IndexedDB and queued for auto-dispatch when transport returns.
        </div>
      )}
    </div>
  );
};
