import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PageTransition } from '../components/motion/PageTransition';
import { HeroSafetyCard } from '../components/home/HeroSafetyCard';
import { FloodAdvisoryCard } from '../components/home/FloodAdvisoryCard';
import { CitizenForecastCard } from '../components/home/CitizenForecastCard';
import { CitizenAlertCard } from '../components/home/CitizenAlertCard';
import { EmergencySOSButton } from '../components/motion/EmergencySOSButton';
import { QuickActions } from '../components/home/QuickActions';
import { LatestAlertCard } from '../components/home/LatestAlertCard';
import { CommunicationStatus } from '../components/home/CommunicationStatus';
import { OfflineBanner } from '../components/connectivity/OfflineBanner';
import { LocationBanner } from '../components/location/LocationBanner';
import { ActiveSOSQueueCard } from '../components/emergency/ActiveSOSQueueCard';
import { riskRepository } from '../storage/repositories/riskRepository';
import { alertRepository } from '../storage/repositories/alertRepository';
import { mockSafetyStatus } from '../data/mock/risk';
import { mockAlerts } from '../data/mock/alerts';
import { SafetyStatus, Alert } from '../types';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { openingContainerVariants, openingItemVariants } from '../lib/animations';

export const Home: React.FC = () => {
  const reducedMotion = useReducedMotion();
  const [safetyStatus, setSafetyStatus] = useState<SafetyStatus>(mockSafetyStatus);
  const [latestAlert, setLatestAlert] = useState<Alert>(mockAlerts[0]);
  const [lastSyncTime, setLastSyncTime] = useState<number>(Date.now() - 2 * 60 * 1000);

  useEffect(() => {
    // Load persisted local data from IndexedDB
    const loadCachedData = async () => {
      try {
        const cachedRisk = await riskRepository.getCurrent();
        if (cachedRisk) {
          setSafetyStatus(cachedRisk);
          if (cachedRisk.cachedAt) {
            setLastSyncTime(new Date(cachedRisk.cachedAt).getTime());
          }
        }

        const cachedAlerts = await alertRepository.getAll();
        if (cachedAlerts && cachedAlerts.length > 0) {
          setLatestAlert(cachedAlerts[0]);
        }
      } catch (err) {
        console.warn('[Home] IndexedDB local load warning:', err);
      }
    };

    loadCachedData();
  }, []);

  return (
    <PageTransition>
      <motion.div
        variants={reducedMotion ? undefined : openingContainerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-4 pb-4"
      >
        {/* Step 0: Non-blocking Offline Status Banner */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <OfflineBanner />
        </motion.div>

        {/* Active Offline SOS Queue Notification if pending */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <ActiveSOSQueueCard />
        </motion.div>

        {/* Step 1: GPS Location Acquisition Banner */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <LocationBanner />
        </motion.div>

        {/* Step 2: Hero Safety Status Card (Springs 0 -> 18 with Data Freshness Tag) */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <HeroSafetyCard status={safetyStatus} timestamp={lastSyncTime} />
        </motion.div>

        {/* Phase 5.4: Adaptive Alert Intelligence & Citizen Warning Card */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <CitizenAlertCard />
        </motion.div>

        {/* Phase 5.2: Geospatial Flood Susceptibility & Inundation Advisory */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <CitizenForecastCard />
          <FloodAdvisoryCard />
        </motion.div>

        {/* Step 3: Emergency SOS Button (Breathing Halo + IndexedDB Queue) */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <EmergencySOSButton />
        </motion.div>

        {/* Step 4: Quick Action Cards Grid (Safe Map, Shelters, Hospitals, Alerts) */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <QuickActions />
        </motion.div>

        {/* Step 5: Latest Alert Preview with Freshness Tag */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <LatestAlertCard alert={latestAlert} />
        </motion.div>

        {/* Step 6: Upgraded Multi-Transport Communication Health Status */}
        <motion.div variants={reducedMotion ? undefined : openingItemVariants}>
          <CommunicationStatus />
        </motion.div>
      </motion.div>
    </PageTransition>
  );
};
