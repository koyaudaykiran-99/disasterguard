import { mockAlerts } from '../data/mock/alerts';
import { mockShelters } from '../data/mock/shelters';
import { mockHospitals } from '../data/mock/hospitals';
import { mockSafetyStatus } from '../data/mock/risk';
import { StoredAlert, StoredShelter, StoredHospital, StoredRisk } from './storageTypes';

const DB_NAME = 'DisasterGuardCitizenDB';
const DB_VERSION = 1;

export const STORES = {
  ALERTS: 'alerts',
  SHELTERS: 'shelters',
  HOSPITALS: 'hospitals',
  RISK: 'risk',
  SOS_QUEUE: 'sos_queue',
  METADATA: 'metadata',
} as const;

let dbPromise: Promise<IDBDatabase> | null = null;

export function openDatabase(): Promise<IDBDatabase> {
  if (dbPromise) return dbPromise;

  dbPromise = new Promise((resolve, reject) => {
    if (typeof window === 'undefined' || !window.indexedDB) {
      reject(new Error('IndexedDB is not supported in this environment.'));
      return;
    }

    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;

      // 1. Alerts store
      if (!db.objectStoreNames.contains(STORES.ALERTS)) {
        const store = db.createObjectStore(STORES.ALERTS, { keyPath: 'id' });
        store.createIndex('severity', 'severity', { unique: false });
        store.createIndex('updatedAt', 'timestamp', { unique: false });
      }

      // 2. Shelters store
      if (!db.objectStoreNames.contains(STORES.SHELTERS)) {
        const store = db.createObjectStore(STORES.SHELTERS, { keyPath: 'id' });
        store.createIndex('distanceKm', 'distanceKm', { unique: false });
      }

      // 3. Hospitals store
      if (!db.objectStoreNames.contains(STORES.HOSPITALS)) {
        const store = db.createObjectStore(STORES.HOSPITALS, { keyPath: 'id' });
        store.createIndex('distanceKm', 'distanceKm', { unique: false });
      }

      // 4. Risk assessment store
      if (!db.objectStoreNames.contains(STORES.RISK)) {
        db.createObjectStore(STORES.RISK, { keyPath: 'id' });
      }

      // 5. Offline Emergency SOS Queue store
      if (!db.objectStoreNames.contains(STORES.SOS_QUEUE)) {
        const store = db.createObjectStore(STORES.SOS_QUEUE, { keyPath: 'id' });
        store.createIndex('status', 'status', { unique: false });
        store.createIndex('createdAt', 'createdAt', { unique: false });
        store.createIndex('priority', 'priority', { unique: false });
      }

      // 6. Metadata store (sync timestamps, cached user GPS, etc.)
      if (!db.objectStoreNames.contains(STORES.METADATA)) {
        db.createObjectStore(STORES.METADATA, { keyPath: 'key' });
      }
    };

    request.onsuccess = async () => {
      const db = request.result;
      try {
        await seedInitialDataIfEmpty(db);
      } catch (err) {
        console.warn('[IndexedDB] Initial seeding warning:', err);
      }
      resolve(db);
    };

    request.onerror = () => {
      reject(request.error);
    };
  });

  return dbPromise;
}

// Seed initial safety data so the application is completely populated offline
async function seedInitialDataIfEmpty(db: IDBDatabase): Promise<void> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction([STORES.ALERTS, STORES.SHELTERS, STORES.HOSPITALS, STORES.RISK, STORES.METADATA], 'readwrite');
    const alertStore = tx.objectStore(STORES.ALERTS);
    const countReq = alertStore.count();

    countReq.onsuccess = () => {
      if (countReq.result === 0) {
        const now = new Date().toISOString();

        // Seed alerts
        mockAlerts.forEach((alert) => {
          const storedAlert: StoredAlert = { ...alert, cachedAt: now, source: 'INITIAL_SEED' };
          alertStore.put(storedAlert);
        });

        // Seed shelters
        const shelterStore = tx.objectStore(STORES.SHELTERS);
        mockShelters.forEach((shelter) => {
          const storedShelter: StoredShelter = { ...shelter, cachedAt: now, source: 'INITIAL_SEED' };
          shelterStore.put(storedShelter);
        });

        // Seed hospitals
        const hospitalStore = tx.objectStore(STORES.HOSPITALS);
        mockHospitals.forEach((hosp) => {
          const storedHosp: StoredHospital = { ...hosp, cachedAt: now, source: 'INITIAL_SEED' };
          hospitalStore.put(storedHosp);
        });

        // Seed risk
        const riskStore = tx.objectStore(STORES.RISK);
        const storedRisk: StoredRisk = {
          ...mockSafetyStatus,
          id: 'current_risk',
          cachedAt: now,
          source: 'INITIAL_SEED',
        };
        riskStore.put(storedRisk);

        // Seed metadata
        const metaStore = tx.objectStore(STORES.METADATA);
        metaStore.put({ key: 'last_sync', value: now, updatedAt: now });
        metaStore.put({ key: 'default_location', value: 'Guntur, Andhra Pradesh', updatedAt: now });

        console.log('[IndexedDB] Successfully seeded initial offline emergency dataset.');
      }
      resolve();
    };

    tx.onerror = () => reject(tx.error);
  });
}
