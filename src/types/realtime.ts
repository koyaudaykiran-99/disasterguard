export type RealTimeEventType =
  | 'WEATHER_UPDATED'
  | 'RAIN_PREDICTION_UPDATED'
  | 'FLOOD_PREDICTION_UPDATED'
  | 'RISK_ZONE_UPDATED'
  | 'ALERT_CREATED'
  | 'ALERT_UPDATED'
  | 'SOS_CREATED'
  | 'SOS_TRIAGED'
  | 'SOS_UPDATE_CREATED'
  | 'INCIDENT_CREATED'
  | 'RESCUE_ASSIGNMENT_CREATED'
  | 'RESCUE_STATUS_UPDATED'
  | 'SHELTER_STATUS_UPDATED'
  | 'HOSPITAL_STATUS_UPDATED'
  | 'SIMULATION_STAGE_CHANGED'
  | 'SYSTEM_STATUS_CHANGED';

export type ConnectionStatus = 'LIVE' | 'RECONNECTING' | 'OFFLINE';

export interface DomainEvent<T = any> {
  event: RealTimeEventType;
  timestamp: string;
  entity_id?: number | string;
  entity_type?: string;
  severity?: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW' | string;
  data: T;
}

export interface LiveFeedItem {
  id: string;
  timestamp: string;
  event: RealTimeEventType;
  severity: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW';
  entityId?: string | number;
  title: string;
  description: string;
}
