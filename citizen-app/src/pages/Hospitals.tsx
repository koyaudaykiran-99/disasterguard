import React, { useState, useEffect } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { AnimatedCard } from '../components/motion/AnimatedCard';
import { StaggeredList } from '../components/motion/StaggeredList';
import { OfflineBanner } from '../components/connectivity/OfflineBanner';
import { DataFreshnessBadge } from '../components/connectivity/DataFreshnessBadge';
import { hospitalRepository } from '../storage/repositories/hospitalRepository';
import { StoredHospital } from '../storage/storageTypes';
import { mockHospitals } from '../data/mock/hospitals';
import { Hospital as HospitalType } from '../types';
import { Hospital, MapPin, Phone, Activity, Database } from 'lucide-react';

export const HospitalsPage: React.FC = () => {
  const [hospitals, setHospitals] = useState<(HospitalType | StoredHospital)[]>(mockHospitals);

  useEffect(() => {
    const loadHospitals = async () => {
      try {
        const cached = await hospitalRepository.getAll();
        if (cached && cached.length > 0) {
          setHospitals(cached);
        }
      } catch (err) {
        console.warn('[HospitalsPage] Failed to load hospitals from storage:', err);
      }
    };

    loadHospitals();
  }, []);

  return (
    <PageTransition className="space-y-4">
      {/* Offline Connectivity Notification */}
      <OfflineBanner />

      {/* Header */}
      <div>
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Hospital className="w-5 h-5 text-rose-400" />
          Emergency Medical Facilities
        </h2>
        <p className="text-xs text-citizen-text-muted font-mono mt-0.5">
          Trauma Centers, Triage Wards & First Aid Clinics
        </p>
      </div>

      {/* Hospitals List */}
      <StaggeredList className="space-y-3.5 pt-1">
        {hospitals.map((hosp) => {
          const cachedAt = 'cachedAt' in hosp ? (hosp as StoredHospital).cachedAt : Date.now();

          return (
            <AnimatedCard key={hosp.id} className="border-slate-800 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded-full border ${
                        hosp.type === 'TRAUMA_CENTER'
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                          : 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                      }`}
                    >
                      {hosp.type.replace('_', ' ')}
                    </span>
                    <DataFreshnessBadge timestamp={cachedAt} />
                    <span className="text-xs text-slate-400 font-mono">{hosp.distanceKm} km away</span>
                  </div>
                  <h3 className="font-bold text-sm text-white mt-1.5">{hosp.name}</h3>
                  <div className="flex items-center text-xs text-slate-400 font-mono mt-0.5">
                    <MapPin className="w-3.5 h-3.5 mr-1 text-slate-500" />
                    <span>{hosp.address}</span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-sm font-bold font-mono text-emerald-400 block">
                    {hosp.availableBeds} Beds
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">Available</span>
                </div>
              </div>

              {/* Department Status Bar */}
              <div className="p-2.5 rounded-xl bg-slate-950/40 border border-slate-800 flex items-center justify-between text-xs font-mono">
                <span className="flex items-center text-slate-300 text-[11px]">
                  <Activity className="w-3.5 h-3.5 text-emerald-400 mr-1.5" />
                  Emergency Department: 24/7 Active
                </span>
                <span className="text-emerald-400 font-bold text-[11px]">Ambulance Intake Ready</span>
              </div>

              {/* Direct Phone Action & Local Cache Note */}
              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                <a
                  href={`tel:${hosp.phone}`}
                  className="flex items-center text-cyan-400 hover:text-cyan-300 font-bold transition-colors"
                >
                  <Phone className="w-3.5 h-3.5 mr-1" />
                  <span>{hosp.phone}</span>
                </a>
                {'source' in hosp ? (
                  <span className="text-[10px] text-slate-500 flex items-center">
                    <Database className="w-3 h-3 mr-1 text-slate-600" />
                    Offline Cached
                  </span>
                ) : (
                  <span className="text-slate-500 text-[11px]">Direct Triage Hotline</span>
                )}
              </div>
            </AnimatedCard>
          );
        })}
      </StaggeredList>
    </PageTransition>
  );
};
