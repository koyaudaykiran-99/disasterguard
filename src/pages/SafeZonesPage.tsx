import React, { useState } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { AnimatedCard } from '../components/motion/AnimatedCard';
import { AnimatedCounter } from '../components/motion/AnimatedCounter';
import { StaggeredList } from '../components/motion/StaggeredList';
import { useDisaster } from '../context/DisasterContext';
import { ShieldCheck, MapPin, Phone, Hospital, Home, HeartPulse, Navigation } from 'lucide-react';
import { SafeZone } from '../types/disaster';
import { SafeZoneDirectionsModal } from '../components/safezones/SafeZoneDirectionsModal';

export const SafeZonesPage: React.FC = () => {
  const { safeZones } = useDisaster();
  const [selectedSafeZoneForDirections, setSelectedSafeZoneForDirections] = useState<SafeZone | null>(null);
  const [isDirectionsModalOpen, setIsDirectionsModalOpen] = useState<boolean>(false);

  const handleOpenDirections = (sz: SafeZone) => {
    setSelectedSafeZoneForDirections(sz);
    setIsDirectionsModalOpen(true);
  };

  const getSafeZoneIcon = (type: string) => {
    switch (type) {
      case 'HOSPITAL':
        return <Hospital className="w-5 h-5 text-rose-400" />;
      case 'SHELTER':
        return <Home className="w-5 h-5 text-emerald-400" />;
      default:
        return <HeartPulse className="w-5 h-5 text-cyan-400" />;
    }
  };

  return (
    <PageTransition className="p-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-gray-800">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            Verified Safe Shelters & Relief Centers
          </h2>
          <p className="text-xs text-gray-400 font-mono mt-1">
            Real-Time Occupancy & Supply Inventory System
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono text-gray-300 bg-gray-900 px-4 py-2 rounded-xl border border-gray-800">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>3 Shelters Open in 5km Radius</span>
        </div>
      </div>

      {/* Grid List of Safe Zones */}
      <StaggeredList className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {safeZones.map((sz) => {
          const occupancyPercent = Math.round((sz.currentOccupancy / sz.capacity) * 100);

          return (
            <AnimatedCard key={sz.id} className="!p-6 space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2.5 rounded-xl bg-gray-900 border border-gray-800">
                    {getSafeZoneIcon(sz.type)}
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-100 text-base">{sz.name}</h3>
                    <div className="flex items-center text-xs text-gray-400 mt-0.5">
                      <MapPin className="w-3.5 h-3.5 mr-1 text-gray-500" />
                      {sz.distanceKm} km away
                    </div>
                  </div>
                </div>

                <span
                  className={`px-2.5 py-0.5 text-[10px] font-mono font-bold uppercase rounded-full border ${
                    sz.status === 'OPEN'
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                      : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  }`}
                >
                  {sz.status}
                </span>
              </div>

              {/* Occupancy Progress Bar */}
              <div className="space-y-1.5 font-mono">
                <div className="flex justify-between text-xs text-gray-300">
                  <span>Capacity Occupancy</span>
                  <span className="font-bold">
                    <AnimatedCounter value={sz.currentOccupancy} /> / {sz.capacity} ({occupancyPercent}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-gray-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-1000 ${
                      occupancyPercent > 85 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${occupancyPercent}%` }}
                  ></div>
                </div>
              </div>

              {/* Inventory Supplies Breakdown */}
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-800/80 text-center font-mono text-xs">
                <div className="p-2 rounded-lg bg-gray-900/60 border border-gray-800">
                  <span className="text-[10px] text-gray-500 block">Water</span>
                  <span className="font-bold text-cyan-400">{sz.supplies.water}%</span>
                </div>
                <div className="p-2 rounded-lg bg-gray-900/60 border border-gray-800">
                  <span className="text-[10px] text-gray-500 block">Food</span>
                  <span className="font-bold text-amber-400">{sz.supplies.food}%</span>
                </div>
                <div className="p-2 rounded-lg bg-gray-900/60 border border-gray-800">
                  <span className="text-[10px] text-gray-500 block">Medical</span>
                  <span className="font-bold text-emerald-400">{sz.supplies.medical}%</span>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-between text-xs text-gray-400 font-mono">
                <span className="flex items-center">
                  <Phone className="w-3.5 h-3.5 mr-1 text-gray-500" />
                  {sz.contact}
                </span>
                <button
                  onClick={() => handleOpenDirections(sz)}
                  className="text-blue-400 hover:text-blue-300 font-sans font-semibold flex items-center gap-1.5 px-2.5 py-1 rounded-lg hover:bg-blue-900/30 transition-all cursor-pointer border border-transparent hover:border-blue-500/30"
                  title={`Get directions and evacuation route to ${sz.name}`}
                >
                  <Navigation className="w-3.5 h-3.5 text-blue-400" />
                  <span>Get Directions &rarr;</span>
                </button>
              </div>
            </AnimatedCard>
          );
        })}
      </StaggeredList>

      {/* Emergency Safe Zone Navigation & Evacuation Directions Modal */}
      <SafeZoneDirectionsModal
        safeZone={selectedSafeZoneForDirections}
        isOpen={isDirectionsModalOpen}
        onClose={() => setIsDirectionsModalOpen(false)}
      />
    </PageTransition>
  );
};
