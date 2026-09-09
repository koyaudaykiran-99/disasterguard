import React from 'react';
import { useLocation } from '../../hooks/useLocation';
import { MapPin, Navigation, AlertCircle, RefreshCw } from 'lucide-react';

export const LocationBanner: React.FC = () => {
  const { location, requestLocation, hasLocation, isLocating, isDenied, accuracy } = useLocation();

  if (hasLocation) {
    return (
      <div className="w-full glass-panel p-3.5 rounded-2xl border border-cyan-500/30 bg-gradient-to-r from-cyan-950/20 via-slate-900/60 to-slate-950/80 flex items-center justify-between font-mono text-xs shadow-md">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/15 border border-cyan-500/40 text-cyan-400 shrink-0">
            <Navigation className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white text-xs">{location.locationName}</span>
              <span className="text-[10px] text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                GPS Locked
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Lat: {location.coords?.latitude}°, Lng: {location.coords?.longitude}° (Accuracy ±{accuracy}m)
            </p>
          </div>
        </div>

        <button
          onClick={requestLocation}
          className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-800 transition-colors"
          title="Refresh GPS location"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLocating ? 'animate-spin text-cyan-400' : ''}`} />
        </button>
      </div>
    );
  }

  if (isDenied) {
    return (
      <div className="w-full glass-panel p-3.5 rounded-2xl border border-amber-500/30 bg-amber-950/20 flex items-center justify-between font-mono text-xs">
        <div className="flex items-center space-x-2.5">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
          <div>
            <span className="font-bold text-amber-300 block text-xs">Location Disabled</span>
            <span className="text-[10px] text-slate-400 font-sans block">
              Using cached regional safety data for Guntur, AP.
            </span>
          </div>
        </div>
        <button
          onClick={requestLocation}
          className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-300 text-xs font-bold border border-slate-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="w-full glass-panel p-3.5 rounded-2xl border border-slate-800 flex items-center justify-between font-mono text-xs">
      <div className="flex items-center space-x-2.5">
        <MapPin className="w-4 h-4 text-cyan-400 shrink-0" />
        <div>
          <span className="font-bold text-white block text-xs">Acquire GPS Accuracy</span>
          <span className="text-[10px] text-slate-400 font-sans block">
            Helps calculate safe evacuation routes to nearby shelters.
          </span>
        </div>
      </div>

      <button
        onClick={requestLocation}
        disabled={isLocating}
        className="px-3 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold font-mono transition-colors shadow-sm disabled:opacity-50 shrink-0 flex items-center gap-1.5"
      >
        <Navigation className={`w-3.5 h-3.5 ${isLocating ? 'animate-spin' : ''}`} />
        <span>{isLocating ? 'Locating...' : 'Enable Location'}</span>
      </button>
    </div>
  );
};
