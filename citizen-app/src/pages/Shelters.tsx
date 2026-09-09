import React, { useState, useEffect } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { AnimatedCard } from '../components/motion/AnimatedCard';
import { StaggeredList } from '../components/motion/StaggeredList';
import { OfflineBanner } from '../components/connectivity/OfflineBanner';
import { DataFreshnessBadge } from '../components/connectivity/DataFreshnessBadge';
import { shelterRepository } from '../storage/repositories/shelterRepository';
import { StoredShelter } from '../storage/storageTypes';
import { mockShelters } from '../data/mock/shelters';
import { Shelter } from '../types';
import { Home, MapPin, Phone, Database } from 'lucide-react';

export const SheltersPage: React.FC = () => {
  const [shelters, setShelters] = useState<(Shelter | StoredShelter)[]>(mockShelters);

  useEffect(() => {
    const loadShelters = async () => {
      try {
        const cached = await shelterRepository.getAll();
        if (cached && cached.length > 0) {
          setShelters(cached);
        }
      } catch (err) {
        console.warn('[SheltersPage] Failed to load shelters from storage:', err);
      }
    };

    loadShelters();
  }, []);

  return (
    <PageTransition className="space-y-4">
      {/* Offline Connectivity Notification */}
      <OfflineBanner />

      {/* Header */}
      <div>
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Home className="w-5 h-5 text-emerald-400" />
          Verified Emergency Shelters
        </h2>
        <p className="text-xs text-citizen-text-muted font-mono mt-0.5">
          High Ground Sanctuaries & Community Safe Centers
        </p>
      </div>

      {/* Shelters List */}
      <StaggeredList className="space-y-3.5 pt-1">
        {shelters.map((sz) => {
          const occupancyPercent = Math.round((sz.currentOccupancy / sz.capacity) * 100);
          const cachedAt = 'cachedAt' in sz ? (sz as StoredShelter).cachedAt : Date.now();

          return (
            <AnimatedCard key={sz.id} className="border-slate-800 space-y-3">
              {/* Header Info */}
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded-full border ${
                        sz.status === 'OPEN'
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                      }`}
                    >
                      {sz.status}
                    </span>
                    {sz.isElevated && (
                      <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                        High Ground
                      </span>
                    )}
                    <DataFreshnessBadge timestamp={cachedAt} />
                  </div>
                  <h3 className="font-bold text-sm text-white mt-1.5">{sz.name}</h3>
                  <div className="flex items-center text-xs text-slate-400 font-mono mt-0.5">
                    <MapPin className="w-3.5 h-3.5 mr-1 text-slate-500" />
                    <span>{sz.distanceKm} km away • {sz.address}</span>
                  </div>
                </div>
              </div>

              {/* Occupancy Progress Bar */}
              <div className="space-y-1 font-mono text-xs">
                <div className="flex justify-between text-slate-300 text-[11px]">
                  <span>Occupancy</span>
                  <span className="font-bold">
                    {sz.currentOccupancy} / {sz.capacity} ({occupancyPercent}%)
                  </span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      occupancyPercent > 80 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${occupancyPercent}%` }}
                  />
                </div>
              </div>

              {/* Supplies Pill Grid */}
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/80 text-center font-mono text-xs">
                <div className="p-1.5 rounded-xl bg-slate-950/40 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">Water</span>
                  <span className="font-bold text-cyan-400">{sz.supplies.water}%</span>
                </div>
                <div className="p-1.5 rounded-xl bg-slate-950/40 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">Food</span>
                  <span className="font-bold text-amber-400">{sz.supplies.food}%</span>
                </div>
                <div className="p-1.5 rounded-xl bg-slate-950/40 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">Medical</span>
                  <span className="font-bold text-emerald-400">{sz.supplies.medical}%</span>
                </div>
              </div>

              {/* Action Hotline & Local Cache Note */}
              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                <a
                  href={`tel:${sz.phone}`}
                  className="flex items-center text-cyan-400 hover:text-cyan-300 font-bold transition-colors"
                >
                  <Phone className="w-3.5 h-3.5 mr-1" />
                  <span>{sz.phone}</span>
                </a>
                {'source' in sz ? (
                  <span className="text-[10px] text-slate-500 flex items-center">
                    <Database className="w-3 h-3 mr-1 text-slate-600" />
                    Offline Cached
                  </span>
                ) : (
                  <span className="text-slate-500 text-[11px]">Free Intake</span>
                )}
              </div>
            </AnimatedCard>
          );
        })}
      </StaggeredList>
    </PageTransition>
  );
};
