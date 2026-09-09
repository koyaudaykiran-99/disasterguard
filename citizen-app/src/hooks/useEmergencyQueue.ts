import { useState, useEffect, useCallback } from 'react';
import { emergencyManager } from '../services/emergency/emergencyManager';
import { QueuedSOS } from '../services/emergency/emergencyTypes';

export function useEmergencyQueue() {
  const [activeSOS, setActiveSOS] = useState<QueuedSOS | null>(emergencyManager.getActiveSOS());
  const [allSOS, setAllSOS] = useState<QueuedSOS[]>([]);

  useEffect(() => {
    const unsubscribe = emergencyManager.subscribe((active, all) => {
      setActiveSOS(active);
      setAllSOS(all);
    });
    return unsubscribe;
  }, []);

  const createSOS = useCallback(
    async (message?: string, severity?: 'CRITICAL' | 'HIGH') => {
      return await emergencyManager.createSOS(message, severity);
    },
    []
  );

  const retryNow = useCallback(async () => {
    await emergencyManager.retryPendingRequests();
  }, []);

  const cancelActiveSOS = useCallback(async () => {
    await emergencyManager.cancelActiveSOS();
  }, []);

  return {
    activeSOS,
    allSOS,
    isQueued: activeSOS !== null && activeSOS.status !== 'SENT',
    createSOS,
    retryNow,
    cancelActiveSOS,
  };
}
