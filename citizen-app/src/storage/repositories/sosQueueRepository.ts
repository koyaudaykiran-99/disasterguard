import { openDatabase, STORES } from '../db';
import { QueuedSOS } from '../../services/emergency/emergencyTypes';

export const sosQueueRepository = {
  async getAll(): Promise<QueuedSOS[]> {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.SOS_QUEUE, 'readonly');
      const store = tx.objectStore(STORES.SOS_QUEUE);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  },

  async getActive(): Promise<QueuedSOS | null> {
    const all = await this.getAll();
    // Return the latest pending/unsent emergency request
    const pending = all.filter((s) => s.status !== 'SENT' && s.status !== 'RECEIVED');
    if (pending.length === 0) return null;
    return pending.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())[0];
  },

  async enqueue(sos: QueuedSOS): Promise<void> {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.SOS_QUEUE, 'readwrite');
      const store = tx.objectStore(STORES.SOS_QUEUE);
      store.put(sos);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },

  async update(sos: QueuedSOS): Promise<void> {
    return this.enqueue(sos);
  },

  async delete(id: string): Promise<void> {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.SOS_QUEUE, 'readwrite');
      const store = tx.objectStore(STORES.SOS_QUEUE);
      store.delete(id);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },
};
