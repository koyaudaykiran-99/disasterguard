import { API_BASE_URL } from "../apiConfig";
import { ConnectivityState, DataFreshness } from './connectivityTypes';

type ConnectivityListener = (state: ConnectivityState) => void;

class ConnectivityService {
  private state: ConnectivityState = {
    internet: typeof navigator !== 'undefined' && navigator.onLine ? 'ONLINE' : 'OFFLINE',
    backend: 'UNKNOWN',
    isDemoOffline: false,
    lastSync: '2 min ago',
    lastSyncTimestamp: Date.now() - 2 * 60 * 1000,
  };

  private listeners: Set<ConnectivityListener> = new Set();
  private healthCheckInterval: any = null;

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('online', this.handleOnline);
      window.addEventListener('offline', this.handleOffline);
      this.checkBackendReachability();
      // Periodically verify backend reachability every 30s
      this.healthCheckInterval = setInterval(() => this.checkBackendReachability(), 30000);
    }
  }

  private handleOnline = () => {
    if (this.state.isDemoOffline) return;
    this.state = {
      ...this.state,
      internet: 'ONLINE',
      lastSync: 'Just now',
      lastSyncTimestamp: Date.now(),
    };
    this.notify();
    this.checkBackendReachability();
  };

  private handleOffline = () => {
    this.state = {
      ...this.state,
      internet: 'OFFLINE',
      backend: 'UNREACHABLE',
    };
    this.notify();
  };

  public async checkBackendReachability(): Promise<boolean> {
    if (this.state.isDemoOffline || (typeof navigator !== 'undefined' && !navigator.onLine)) {
      this.state.backend = 'UNREACHABLE';
      this.notify();
      return false;
    }

    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 3500);

      const res = await fetch(`${API_BASE_URL}/api/v1/health`, {
        method: 'GET',
        signal: controller.signal,
      });
      clearTimeout(timer);

      const isReachable = res.ok;
      this.state = {
        ...this.state,
        backend: isReachable ? 'REACHABLE' : 'UNREACHABLE',
        lastSync: 'Just now',
        lastSyncTimestamp: Date.now(),
      };
      this.notify();
      return isReachable;
    } catch {
      this.state = {
        ...this.state,
        backend: 'UNREACHABLE',
      };
      this.notify();
      return false;
    }
  }

  public toggleDemoOffline(forceOffline?: boolean): void {
    const nextDemoState = forceOffline !== undefined ? forceOffline : !this.state.isDemoOffline;
    
    if (nextDemoState) {
      this.state = {
        ...this.state,
        isDemoOffline: true,
        internet: 'OFFLINE',
        backend: 'UNREACHABLE',
      };
    } else {
      const realOnline = typeof navigator !== 'undefined' ? navigator.onLine : true;
      this.state = {
        ...this.state,
        isDemoOffline: false,
        internet: realOnline ? 'ONLINE' : 'OFFLINE',
        lastSync: 'Just now',
        lastSyncTimestamp: Date.now(),
      };
      this.checkBackendReachability();
    }
    this.notify();
  }

  public getState(): ConnectivityState {
    return this.state;
  }

  public subscribe(listener: ConnectivityListener): () => void {
    this.listeners.add(listener);
    listener(this.state);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    this.listeners.forEach((l) => l(this.state));
  }

  public computeFreshness(timestamp: number | string): { freshness: DataFreshness; label: string } {
    const timeMs = typeof timestamp === 'string' ? new Date(timestamp).getTime() : timestamp;
    const diffMin = Math.max(0, Math.floor((Date.now() - timeMs) / (1000 * 60)));

    if (this.state.internet === 'OFFLINE') {
      if (diffMin > 180) return { freshness: 'STALE', label: `STALE • ${Math.floor(diffMin / 60)} hours ago (Offline)` };
      if (diffMin > 60) return { freshness: 'CACHED', label: `CACHED • ${Math.floor(diffMin / 60)} hr ago (Offline)` };
      return { freshness: 'CACHED', label: `CACHED • ${diffMin} min ago (Offline)` };
    }

    if (diffMin < 5) return { freshness: 'LIVE', label: 'LIVE • Updated just now' };
    if (diffMin < 60) return { freshness: 'RECENT', label: `RECENT • ${diffMin} min ago` };
    return { freshness: 'STALE', label: `STALE • ${Math.floor(diffMin / 60)} hours ago` };
  }
}

export const connectivityService = new ConnectivityService();
