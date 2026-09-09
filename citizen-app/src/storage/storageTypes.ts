import { Alert, Shelter, Hospital, SafetyStatus } from '../types';

export interface StoredAlert extends Alert {
  cachedAt: string;
  source: 'NETWORK' | 'INITIAL_SEED' | 'MANUAL_CACHE';
}

export interface StoredShelter extends Shelter {
  cachedAt: string;
  source: 'NETWORK' | 'INITIAL_SEED' | 'MANUAL_CACHE';
}

export interface StoredHospital extends Hospital {
  cachedAt: string;
  source: 'NETWORK' | 'INITIAL_SEED' | 'MANUAL_CACHE';
}

export interface StoredRisk extends SafetyStatus {
  id: string; // 'current_risk'
  cachedAt: string;
  source: 'NETWORK' | 'INITIAL_SEED' | 'MANUAL_CACHE';
}

export interface AppMetadata {
  key: string;
  value: any;
  updatedAt: string;
}
