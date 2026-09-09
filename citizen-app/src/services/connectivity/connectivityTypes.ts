export type InternetStatus = 'ONLINE' | 'OFFLINE' | 'RECONNECTING';
export type BackendStatus = 'REACHABLE' | 'UNREACHABLE' | 'UNKNOWN';
export type DataFreshness = 'LIVE' | 'RECENT' | 'CACHED' | 'STALE' | 'OFFLINE';

export interface ConnectivityState {
  internet: InternetStatus;
  backend: BackendStatus;
  isDemoOffline: boolean;
  lastSync: string;
  lastSyncTimestamp: number;
}
