export type SOSStatus =
  | 'QUEUED'
  | 'LOCAL_QUEUED'
  | 'SENDING'
  | 'SENT'
  | 'RECEIVED'
  | 'TRIAGED'
  | 'DISPATCHED'
  | 'RESCUED'
  | 'FAILED'
  | 'WAITING_FOR_TRANSPORT';

export type TransportType =
  | 'INTERNET'
  | 'SMS'
  | 'RELAY'
  | 'GATEWAY'
  | 'NONE_AVAILABLE';

export interface EmergencyUpdateItem {
  id: string; // client update UUID
  sosId?: number;
  updateType:
    | 'INITIAL_SOS'
    | 'TEXT_UPDATE'
    | 'LOCATION_UPDATE'
    | 'SITUATION_UPDATE'
    | 'MEDICAL_UPDATE'
    | 'TRAPPED_PERSON_UPDATE'
    | 'WATER_LEVEL_UPDATE'
    | 'REPEAT_SOS'
    | 'CANCEL_REQUEST'
    | string;
  message?: string;
  latitude?: number;
  longitude?: number;
  accuracy?: number | null;
  createdAt: string;
  status: 'LOCAL_QUEUED' | 'SENDING' | 'RECEIVED' | 'FAILED';
  deliveredAt?: string;
  failureReason?: string;
  original_language?: string;
  audioBlob?: Blob;
  audioId?: string;
  audioDuration?: number;
  audioMimeType?: string;
  audioSize?: number;
  audioStorageRef?: string;
  transcriptionProvider?: string;
  transcriptionModel?: string;
  transcriptionConfidence?: number;
}

export interface QueuedSOS {
  id: string;
  createdAt: string;
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  locationName?: string;
  message: string;
  severity: 'CRITICAL' | 'HIGH';
  status: SOSStatus;
  transport: TransportType;
  retryCount: number;
  lastAttemptAt: string | null;
  priority: number; // 100 for critical, 75 for high
  failureReason?: string;
  deliveredAt?: string;
  backendSosId?: number;
  serverAck?: any;
  assignedTeamName?: string;
  dispatchedAt?: string;
  estimatedEtaMinutes?: number;
  updates?: EmergencyUpdateItem[];
  guidance?: any;
}
