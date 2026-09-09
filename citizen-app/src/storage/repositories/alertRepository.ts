import { openDatabase, STORES } from '../db';
import { StoredAlert } from '../storageTypes';
import { Alert } from '../../types';

export const alertRepository = {
  async getAll(): Promise<StoredAlert[]> {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.ALERTS, 'readonly');
      const store = tx.objectStore(STORES.ALERTS);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  },

  async getById(id: string): Promise<StoredAlert | null> {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.ALERTS, 'readonly');
      const store = tx.objectStore(STORES.ALERTS);
      const req = store.get(id);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
  },

  async saveAll(alerts: Alert[], source: 'NETWORK' | 'MANUAL_CACHE' = 'NETWORK'): Promise<void> {
    const db = await openDatabase();
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.ALERTS, 'readwrite');
      const store = tx.objectStore(STORES.ALERTS);
      alerts.forEach((a) => {
        const stored: StoredAlert = { ...a, cachedAt: now, source };
        store.put(stored);
      });
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },
};
