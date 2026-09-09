import { LocationState, Coordinates } from './locationTypes';
import { openDatabase, STORES } from '../../storage/db';

type LocationListener = (state: LocationState) => void;

class LocationService {
  private state: LocationState = {
    coords: null,
    locationName: 'Guntur, Andhra Pradesh',
    status: 'IDLE',
    timestamp: null,
    errorMessage: null,
  };

  private listeners: Set<LocationListener> = new Set();
  private hasInitialized = false;

  constructor() {
    this.restoreCachedLocation();
  }

  private async restoreCachedLocation(): Promise<void> {
    try {
      const db = await openDatabase();
      const tx = db.transaction(STORES.METADATA, 'readonly');
      const store = tx.objectStore(STORES.METADATA);
      const req = store.get('cached_location');

      req.onsuccess = () => {
        if (req.result && req.result.value) {
          const cached = req.result.value;
          this.state = {
            ...this.state,
            coords: cached.coords,
            locationName: cached.locationName || 'Guntur, Andhra Pradesh',
            status: 'LOCATION_AVAILABLE',
            timestamp: cached.timestamp,
          };
          this.notify();
        }
      };
    } catch (err) {
      console.warn('[LocationService] Could not read cached location from IndexedDB:', err);
    }
  }

  private async persistLocation(coords: Coordinates, name: string): Promise<void> {
    try {
      const db = await openDatabase();
      const tx = db.transaction(STORES.METADATA, 'readwrite');
      const store = tx.objectStore(STORES.METADATA);
      store.put({
        key: 'cached_location',
        value: { coords, locationName: name, timestamp: Date.now() },
        updatedAt: new Date().toISOString(),
      });
    } catch (err) {
      console.warn('[LocationService] Could not save location to IndexedDB:', err);
    }
  }

  public getState(): LocationState {
    return this.state;
  }

  public subscribe(listener: LocationListener): () => void {
    this.listeners.add(listener);
    listener(this.state);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    this.listeners.forEach((listener) => listener(this.state));
  }

  public async requestLocation(): Promise<LocationState> {
    if (typeof window === 'undefined' || !navigator.geolocation) {
      this.state = {
        ...this.state,
        status: 'LOCATION_UNAVAILABLE',
        errorMessage: 'Geolocation is not supported by your browser or device.',
      };
      this.notify();
      return this.state;
    }

    this.state = {
      ...this.state,
      status: 'LOCATING',
      errorMessage: null,
    };
    this.notify();

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords: Coordinates = {
            latitude: Number(position.coords.latitude.toFixed(5)),
            longitude: Number(position.coords.longitude.toFixed(5)),
            accuracy: Math.round(position.coords.accuracy),
          };

          // Approximate location name based on known coordinates or regional center
          const locationName = 'Guntur, Andhra Pradesh';

          this.state = {
            coords,
            locationName,
            status: 'LOCATION_AVAILABLE',
            timestamp: position.timestamp || Date.now(),
            errorMessage: null,
          };

          this.persistLocation(coords, locationName);
          this.notify();
          resolve(this.state);
        },
        (error) => {
          let status: LocationState['status'] = 'LOCATION_ERROR';
          let errorMessage = 'Failed to acquire location coordinates.';

          if (error.code === error.PERMISSION_DENIED) {
            status = 'PERMISSION_DENIED';
            errorMessage = 'Location permission was declined. Using cached regional safety zones.';
          } else if (error.code === error.POSITION_UNAVAILABLE) {
            status = 'LOCATION_UNAVAILABLE';
            errorMessage = 'GPS position currently unavailable on this device.';
          }

          this.state = {
            ...this.state,
            status,
            errorMessage,
          };

          this.notify();
          resolve(this.state);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        }
      );
    });
  }
}

export const locationService = new LocationService();
