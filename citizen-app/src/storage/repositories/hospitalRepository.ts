import { openDatabase, STORES } from '../db';
import { StoredHospital } from '../storageTypes';
import { Hospital } from '../../types';

export const hospitalRepository = {
  async getAll(): Promise<StoredHospital[]> {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.HOSPITALS, 'readonly');
      const store = tx.objectStore(STORES.HOSPITALS);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  },

  async saveAll(hospitals: Hospital[], source: 'NETWORK' | 'MANUAL_CACHE' = 'NETWORK'): Promise<void> {
    const db = await openDatabase();
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.HOSPITALS, 'readwrite');
      const store = tx.objectStore(STORES.HOSPITALS);
      hospitals.forEach((h) => {
        const stored: StoredHospital = { ...h, cachedAt: now, source };
        store.put(stored);
      });
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },
};
