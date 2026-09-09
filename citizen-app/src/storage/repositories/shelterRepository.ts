import { openDatabase, STORES } from '../db';
import { StoredShelter } from '../storageTypes';
import { Shelter } from '../../types';

export const shelterRepository = {
  async getAll(): Promise<StoredShelter[]> {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.SHELTERS, 'readonly');
      const store = tx.objectStore(STORES.SHELTERS);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  },

  async saveAll(shelters: Shelter[], source: 'NETWORK' | 'MANUAL_CACHE' = 'NETWORK'): Promise<void> {
    const db = await openDatabase();
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.SHELTERS, 'readwrite');
      const store = tx.objectStore(STORES.SHELTERS);
      shelters.forEach((s) => {
        const stored: StoredShelter = { ...s, cachedAt: now, source };
        store.put(stored);
      });
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },
};
