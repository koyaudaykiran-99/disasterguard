import { useState, useEffect, useCallback } from 'react';
import { connectivityService } from '../services/connectivity/connectivityService';
import { ConnectivityState, DataFreshness } from '../services/connectivity/connectivityTypes';

export function useConnectivity() {
  const [state, setState] = useState<ConnectivityState>(connectivityService.getState());

  useEffect(() => {
    const unsubscribe = connectivityService.subscribe((next) => {
      setState(next);
    });
    return unsubscribe;
  }, []);

  const toggleDemoOffline = useCallback((override?: boolean) => {
    connectivityService.toggleDemoOffline(override);
  }, []);

  const getFreshness = useCallback((timestamp: number | string) => {
    return connectivityService.computeFreshness(timestamp);
  }, []);

  return {
    ...state,
    isOnline: state.internet === 'ONLINE',
    isOffline: state.internet === 'OFFLINE',
    isBackendReachable: state.backend === 'REACHABLE',
    toggleDemoOffline,
    getFreshness,
  };
}
