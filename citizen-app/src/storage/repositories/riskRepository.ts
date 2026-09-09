import { openDatabase, STORES } from '../db';
import { StoredRisk } from '../storageTypes';
import { SafetyStatus } from '../../types';

export const riskRepository = {
  async getCurrent(): Promise<StoredRisk | null> {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.RISK, 'readonly');
      const store = tx.objectStore(STORES.RISK);
      const req = store.get('current_risk');
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
  },

  async save(risk: SafetyStatus, source: 'NETWORK' | 'MANUAL_CACHE' = 'NETWORK'): Promise<void> {
    const db = await openDatabase();
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.RISK, 'readwrite');
      const store = tx.objectStore(STORES.RISK);
      const stored: StoredRisk = {
        ...risk,
        id: 'current_risk',
        cachedAt: now,
        source,
      };
      store.put(stored);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },
};
