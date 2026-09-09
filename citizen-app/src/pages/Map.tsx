import React, { useState, useEffect } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { AnimatedCard } from '../components/motion/AnimatedCard';
import { StaggeredList } from '../components/motion/StaggeredList';
import { OfflineBanner } from '../components/connectivity/OfflineBanner';
import { DataFreshnessBadge } from '../components/connectivity/DataFreshnessBadge';
import { CitizenMap } from '../components/map/CitizenMap';
import { LanguageSelector } from '../components/common/LanguageSelector';
import { useLanguage } from '../context/LanguageContext';
import { useLocation } from '../hooks/useLocation';
import { shelterRepository } from '../storage/repositories/shelterRepository';
import { hospitalRepository } from '../storage/repositories/hospitalRepository';
import { StoredShelter, StoredHospital } from '../storage/storageTypes';
import { mockShelters } from '../data/mock/shelters';
import { mockHospitals } from '../data/mock/hospitals';
import { Shelter, Hospital } from '../types';
import {
  Compass,
  MapPin,
  Navigation,
  Crosshair,
  ShieldCheck,
  Hospital as HospitalIcon,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';

export const MapPage: React.FC = () => {
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'SHELTER' | 'HOSPITAL'>('ALL');
  const [shelters, setShelters] = useState<(Shelter | StoredShelter)[]>(mockShelters);
  const [hospitals, setHospitals] = useState<(Hospital | StoredHospital)[]>(mockHospitals);
  const [selectedFacility, setSelectedFacility] = useState<Shelter | Hospital | null>(null);

  const { coords, status: locStatus, locationName, requestLocation, isLocating } = useLocation();
  const { language } = useLanguage();

  useEffect(() => {
    const loadCachedPoints = async () => {
      try {
        const [cachedShelters, cachedHospitals] = await Promise.all([
          shelterRepository.getAll(),
          hospitalRepository.getAll(),
        ]);
        if (cachedShelters && cachedShelters.length > 0) setShelters(cachedShelters);
        if (cachedHospitals && cachedHospitals.length > 0) setHospitals(cachedHospitals);
      } catch (err) {
        console.warn('[MapPage] Error loading cached facilities:', err);
      }
    };

    loadCachedPoints();
  }, []);

  return (
    <PageTransition className="space-y-4">
      <OfflineBanner />

      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-red-600" />
            <span>
              {language === 'te' ? 'సురక్షిత మార్గాలు & మ్యాప్' : language === 'hi' ? 'सुरक्षित मार्ग और नक्शा' : 'Safe Routes & GIS Map'}
            </span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-mono mt-0.5">
            {language === 'te'
              ? 'ధృవీకరించబడిన సురక్షిత ప్రాంతాలు & ప్రమాద స్థలాలు'
              : 'Verified Safe High-Ground & Live Inundation Corridors'}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <LanguageSelector />
        </div>
      </div>

      <CitizenMap
        shelters={shelters}
        hospitals={hospitals}
        selectedFacility={selectedFacility}
        onSelectFacility={(f) => setSelectedFacility(f)}
        className="h-[380px]"
      />

      <div className="p-3.5 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-transparent border border-emerald-500/30 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold text-emerald-800 dark:text-emerald-300">
            {language === 'te'
              ? 'సురక్షిత తరలింపు మార్గదర్శకాలు (Safe Evacuation Guidance)'
              : language === 'hi'
              ? 'सुरक्षित निकासी मार्गदर्शन'
              : 'Safe Evacuation Guidance'}
          </h4>
          <p className="text-xs text-slate-700 dark:text-slate-200 mt-1 font-medium">
            {language === 'te'
              ? 'వరద పరిస్థితి ఉంది. వెంటనే ఎత్తైన మరియు సురక్షితమైన ప్రదేశానికి వెళ్లండి. నీటిలో నడవకండి. సహాయ శిబిరానికి తరలి వెళ్ళండి.'
              : language === 'hi'
              ? 'बाढ़ की स्थिति है। तुरंत ऊंचे और सुरक्षित स्थान पर जाएं। बहते पानी में न चलें। सुरक्षित राहत शिविर में जाएं।'
              : 'Severe flood situation active. Immediately move towards elevated safe ground. Do not walk or drive through flowing water.'}
          </p>
          <div className="mt-1.5 text-[11px] font-mono text-emerald-700 dark:text-emerald-400">
            {language === 'te'
              ? 'గమనిక: దూరాలు ఉజ్జాయింపు భౌగోళిక దూరం (Approx. geographic distance) మాత్రమే.'
              : 'Note: Distances are approximate geographic direct distance.'}
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-2 pt-1">
        {(['ALL', 'SHELTER', 'HOSPITAL'] as const).map((filter) => (
          <button
            key={filter}
            onClick={() => setActiveFilter(filter)}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
              activeFilter === filter
                ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-bold shadow-md'
                : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-800'
            }`}
          >
            {filter === 'ALL' ? (language === 'te' ? 'అన్ని కేంద్రాలు' : 'All Points') :
             filter === 'SHELTER' ? (language === 'te' ? 'సహాయ శిబిరాలు' : 'Safe Shelters') :
             (language === 'te' ? 'ఆసుపత్రులు' : 'Hospitals')}
          </button>
        ))}
      </div>

      <StaggeredList className="space-y-3 pt-1">
        {(activeFilter === 'ALL' || activeFilter === 'SHELTER') &&
          shelters.map((sz) => {
            const cachedAt = 'cachedAt' in sz ? (sz as StoredShelter).cachedAt : Date.now();
            const isSelected = selectedFacility?.id === sz.id;
            return (
              <AnimatedCard
                key={sz.id}
                className={`cursor-pointer transition-all border ${
                  isSelected
                    ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/30 shadow-md ring-2 ring-emerald-500/30'
                    : 'border-slate-200 dark:border-slate-800 hover:border-emerald-500/50'
                }`}
              >
                <div
                  className="flex items-start justify-between"
                  onClick={() => setSelectedFacility(sz as Shelter)}
                >
                  <div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-mono font-bold uppercase text-emerald-700 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/30">
                        {language === 'te' ? 'సహాయ శిబిరం' : 'SHELTER'}
                      </span>
                      <DataFreshnessBadge timestamp={cachedAt} />
                      <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                        ~{sz.distanceKm} km (Approx. geographic distance)
                      </span>
                    </div>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white mt-1">{sz.name}</h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{sz.address}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400">
                      {sz.capacity - sz.currentOccupancy} free
                    </span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 block font-mono">
                      {Math.round((sz.currentOccupancy / sz.capacity) * 100)}% occupied
                    </span>
                  </div>
                </div>
              </AnimatedCard>
            );
          })}

        {(activeFilter === 'ALL' || activeFilter === 'HOSPITAL') &&
          hospitals.map((hosp) => {
            const cachedAt = 'cachedAt' in hosp ? (hosp as StoredHospital).cachedAt : Date.now();
            const isSelected = selectedFacility?.id === hosp.id;
            return (
              <AnimatedCard
                key={hosp.id}
                className={`cursor-pointer transition-all border ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-950/30 shadow-md ring-2 ring-blue-500/30'
                    : 'border-slate-200 dark:border-slate-800 hover:border-blue-500/50'
                }`}
              >
                <div
                  className="flex items-start justify-between"
                  onClick={() => setSelectedFacility(hosp as Hospital)}
                >
                  <div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-mono font-bold uppercase text-blue-700 dark:text-blue-400 bg-blue-100 dark:bg-blue-500/20 px-2 py-0.5 rounded border border-blue-500/30">
                        {language === 'te' ? 'ఆసుపత్రి' : 'HOSPITAL'}
                      </span>
                      <DataFreshnessBadge timestamp={cachedAt} />
                      <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                        ~{hosp.distanceKm} km (Approx. geographic distance)
                      </span>
                    </div>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white mt-1">{hosp.name}</h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{hosp.address}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-mono font-bold text-blue-600 dark:text-blue-400">
                      {hosp.availableBeds} beds
                    </span>
                    <span className="text-[10px] text-emerald-600 dark:text-emerald-400 block font-mono">ER Open</span>
                  </div>
                </div>
              </AnimatedCard>
            );
          })}
      </StaggeredList>
    </PageTransition>
  );
};
