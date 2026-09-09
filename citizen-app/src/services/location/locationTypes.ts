export type LocationStatus =
  | 'IDLE'
  | 'LOCATING'
  | 'LOCATION_AVAILABLE'
  | 'PERMISSION_DENIED'
  | 'LOCATION_UNAVAILABLE'
  | 'LOCATION_ERROR';

export interface Coordinates {
  latitude: number;
  longitude: number;
  accuracy: number; // in meters
}

export interface LocationState {
  coords: Coordinates | null;
  locationName: string;
  status: LocationStatus;
  timestamp: number | null;
  errorMessage: string | null;
}
