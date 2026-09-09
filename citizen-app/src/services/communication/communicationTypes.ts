import { QueuedSOS, TransportType } from '../emergency/emergencyTypes';

export type TransportStatus = 'AVAILABLE' | 'UNAVAILABLE' | 'STANDBY' | 'NOT_IMPLEMENTED';

export interface TransportResult {
  success: boolean;
  transport: TransportType;
  messageId?: string;
  backendSosId?: number;
  serverAck?: any;
  timestamp: string;
  error?: string;
}

export interface CommunicationTransport {
  type: TransportType;
  name: string;
  description: string;
  isAvailable(): Promise<boolean>;
  getStatus(): TransportStatus;
  sendEmergencyMessage(sos: QueuedSOS): Promise<TransportResult>;
}
