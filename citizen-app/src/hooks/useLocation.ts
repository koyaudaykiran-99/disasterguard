import { useState, useEffect, useCallback } from 'react';
import { locationService } from '../services/location/locationService';
import { LocationState } from '../services/location/locationTypes';

export function useLocation() {
  const [location, setLocation] = useState<LocationState>(locationService.getState());

  useEffect(() => {
    const unsubscribe = locationService.subscribe((state) => {
      setLocation(state);
    });
    return unsubscribe;
  }, []);

  const requestLocation = useCallback(() => {
    return locationService.requestLocation();
  }, []);

  return {
    location,
    requestLocation,
    coords: location.coords,
    status: location.status,
    locationName: location.locationName,
    accuracy: location.coords?.accuracy ?? null,
    isLocating: location.status === 'LOCATING',
    hasLocation: location.status === 'LOCATION_AVAILABLE' && location.coords !== null,
    isDenied: location.status === 'PERMISSION_DENIED',
  };
}
