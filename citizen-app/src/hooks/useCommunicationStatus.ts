import { useState, useEffect } from 'react';
import { CommunicationState } from '../types';

export function useCommunicationStatus(): CommunicationState {
  const [isOnline, setIsOnline] = useState<boolean>(() => {
    return typeof navigator !== 'undefined' ? navigator.onLine : true;
  });

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return {
    internet: isOnline ? 'ONLINE' : 'OFFLINE',
    gps: 'GPS AVAILABLE',
    relay: isOnline ? 'RELAY READY' : 'RELAY UNAVAILABLE',
    lastSync: 'Just now',
  };
}
