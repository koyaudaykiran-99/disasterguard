import { QueuedSOS } from './emergencyTypes';
import { sosQueueRepository } from '../../storage/repositories/sosQueueRepository';

export const RETRY_SCHEDULE_MS = [0, 5000, 15000, 30000, 60000, 300000];

export class EmergencyQueue {
  public async getNextRetryDelay(retryCount: number): Promise<number> {
    const idx = Math.min(retryCount, RETRY_SCHEDULE_MS.length - 1);
    return RETRY_SCHEDULE_MS[idx];
  }

  public async getPendingRequests(): Promise<QueuedSOS[]> {
    const all = await sosQueueRepository.getAll();
    return all
      .filter((item) => item.status !== 'SENT' && item.status !== 'RECEIVED')
      .sort((a, b) => {
        // Higher priority first, then older first
        if (b.priority !== a.priority) return b.priority - a.priority;
        return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
      });
  }

  public async getActiveSOS(): Promise<QueuedSOS | null> {
    return await sosQueueRepository.getActive();
  }
}

export const emergencyQueue = new EmergencyQueue();
