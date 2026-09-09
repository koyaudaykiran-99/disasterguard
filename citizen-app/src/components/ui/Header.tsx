import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Shield, User, Zap, WifiOff, Wifi } from 'lucide-react';
import { useConnectivity } from '../../hooks/useConnectivity';
import { useLocation } from '../../hooks/useLocation';

interface HeaderProps {
  locationName?: string;
}

export const Header: React.FC<HeaderProps> = ({
  locationName = 'Guntur, Andhra Pradesh',
}) => {
  const navigate = useNavigate();
  const { isOnline, isDemoOffline, toggleDemoOffline } = useConnectivity();
  const { coords, accuracy, hasLocation } = useLocation();

  return (
    <header className="w-full pt-safe pt-3.5 pb-2.5 px-4 border-b border-slate-800/80 bg-citizen-bg/95 backdrop-blur-md sticky top-0 z-40">
      <div className="flex items-center justify-between">
        
        {/* Brand & Tagline */}
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 p-[1.5px] shadow-lg shadow-cyan-950/30 shrink-0">
            <div className="w-full h-full rounded-[10px] bg-slate-950 flex items-center justify-center">
              <Shield className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-base font-extrabold tracking-tight text-white font-mono">
                AI-DisasterGuard
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            </div>
            <p className="text-[10px] text-citizen-text-muted font-medium tracking-wide">
              Predict Early. Warn Faster. Respond Smarter.
            </p>
          </div>
        </div>

        {/* Right Header Actions: Demo Toggle & Profile Avatar */}
        <div className="flex items-center space-x-2">
          {/* Quick Demo Offline Simulation Toggle */}
          <button
            onClick={() => toggleDemoOffline()}
            title="Toggle between Online and Simulated Offline Network Blackout"
            className={`px-2 py-1 rounded-xl text-[10px] font-mono font-bold border transition-colors flex items-center gap-1 ${
              isDemoOffline
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
            }`}
          >
            <Zap className="w-3 h-3" />
            <span>{isDemoOffline ? 'Demo: Offline' : 'Simulate Offline'}</span>
          </button>

          {/* Profile Avatar */}
          <button
            onClick={() => navigate('/profile')}
            className="relative w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-citizen-text-secondary hover:text-white hover:border-cyan-400/50 transition-all focus:outline-none"
            aria-label="View citizen profile"
          >
            <User className="w-4 h-4" />
            <span
              className={`absolute top-0 right-0 w-2 h-2 rounded-full border-2 border-citizen-bg ${
                isOnline ? 'bg-emerald-500' : 'bg-amber-500'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Sub-bar: GPS Location & Network State */}
      <div className="mt-2 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center text-citizen-text-secondary truncate max-w-[210px]">
          <MapPin className="w-3.5 h-3.5 text-cyan-400 mr-1 shrink-0" />
          <span className="truncate text-[11px] font-medium">
            {locationName} {hasLocation && accuracy ? `(±${accuracy}m)` : ''}
          </span>
        </div>

        <div
          className={`flex items-center space-x-1.5 px-2 py-0.5 rounded-full border text-[10px] ${
            isOnline
              ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/40'
              : 'bg-amber-950/40 text-amber-300 border-amber-800/40'
          }`}
        >
          {isOnline ? (
            <Wifi className="w-3 h-3 text-emerald-400" />
          ) : (
            <WifiOff className="w-3 h-3 text-amber-400" />
          )}
          <span>{isOnline ? 'Online' : 'Offline Mode'}</span>
        </div>
      </div>
    </header>
  );
};
