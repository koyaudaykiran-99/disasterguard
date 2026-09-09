export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';

export interface RiskFactor {
  name: string;
  value: string;
  status: 'SAFE' | 'WARNING' | 'ALERT';
}

export interface SafetyStatus {
  score: number; // 0 - 100
  level: RiskLevel;
  headline: string;
  message: string;
  locationName: string;
  updatedAt: string;
  factors: RiskFactor[];
}

export interface Alert {
  id: string;
  backendAlertId?: number;
  title: string;
  severity: RiskLevel;
  category: 'RAINFALL' | 'FLOOD' | 'CYCLONE' | 'EVACUATION' | 'INFRASTRUCTURE' | string;
  location: string;
  description: string;
  timestamp: string;
  timeAgo: string;
  instructions: string[];
  horizon?: string;
  confidence?: string;
  why?: string;
  acknowledged?: boolean;
  acknowledgedAt?: string;
}

export interface AdaptiveCitizenAlert {
  id: number;
  title: string;
  headline: string;
  message: string;
  category: string;
  severity: 'INFO' | 'ADVISORY' | 'WATCH' | 'WARNING' | 'CRITICAL' | RiskLevel | string;
  location: string;
  horizon: string;
  confidence: string;
  why: string;
  what_to_do: string[];
  acknowledged: boolean;
  acknowledgedAt?: string;
  issuedAt: string;
}

export interface Shelter {
  id: string;
  name: string;
  distanceKm: number;
  latitude?: number;
  longitude?: number;
  capacity: number;
  currentOccupancy: number;
  status: 'OPEN' | 'NEAR_CAPACITY' | 'FULL';
  address: string;
  phone: string;
  supplies: {
    water: number; // percentage
    food: number;
    medical: number;
  };
  isElevated: boolean;
}

export interface Hospital {
  id: string;
  name: string;
  distanceKm: number;
  latitude?: number;
  longitude?: number;
  type: 'TRAUMA_CENTER' | 'GENERAL' | 'PRIMARY_HEALTH';
  availableBeds: number;
  phone: string;
  address: string;
  emergencyDepartmentOpen: boolean;
}

export interface CommunicationState {
  internet: 'ONLINE' | 'OFFLINE';
  gps: 'GPS AVAILABLE' | 'GPS UNAVAILABLE';
  relay: 'RELAY READY' | 'RELAY UNAVAILABLE';
  lastSync: string;
}

export interface EmergencyContact {
  name: string;
  relation: string;
  phone: string;
}

export interface UserProfile {
  name: string;
  phone: string;
  bloodGroup: string;
  location: string;
  householdMembers: number;
  specialNeeds: string[];
  emergencyContacts: EmergencyContact[];
  checklistCompleted: number;
  checklistTotal: number;
}
