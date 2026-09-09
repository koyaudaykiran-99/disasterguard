export interface EmergencyUpdate {
  id: number;
  clientUpdateId?: string;
  sosId: number;
  incidentId?: number;
  userId?: number;
  updateType: 'INITIAL_SOS' | 'TEXT_UPDATE' | 'LOCATION_UPDATE' | 'SITUATION_UPDATE' | 'MEDICAL_UPDATE' | 'TRAPPED_PERSON_UPDATE' | 'WATER_LEVEL_UPDATE' | 'REPEAT_SOS' | 'CANCEL_REQUEST' | string;
  message?: string;
  latitude?: number;
  longitude?: number;
  accuracy?: number;
  locationTimestamp?: string;
  source: string;
  deliveryStatus: string;
  originalLanguage: string;
  original_language?: string;
  processingStatus: string;
  audioId?: string;
  audio_id?: string;
  audioDuration?: number;
  audioMimeType?: string;
  audioSize?: number;
  audioStorageReference?: string;
  transcriptionProvider?: string;
  transcription_provider?: string;
  transcriptionModel?: string;
  transcriptionConfidence?: number;
  createdAt: string;
  receivedAt: string;
}

export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';

export interface Alert {
  id: string;
  title: string;
  category: 'FLOOD' | 'STORM' | 'LANDSLIDE' | 'CYCLONE' | 'EARTHQUAKE';
  severity: RiskLevel;
  location: string;
  coordinates: [number, number]; // [lat, lng]
  timestamp: string;
  description: string;
  affectedPopulation: number;
  isNew?: boolean;
}

export interface SOSIncident {
  updates?: EmergencyUpdate[];
  id: string;
  sosId?: number;
  title?: string;
  citizenName: string;
  phone: string;
  location: string;
  coordinates: [number, number];
  timestamp: string;
  status: 'DISPATCHED' | 'PENDING' | 'RESCUED';
  emergencyType: 'MEDICAL' | 'TRAPPED' | 'EVACUATION_NEEDED' | 'FOOD_WATER' | string;
  peopleCount: number;
  urgency: RiskLevel;
  // End-to-End Triage & Dispatch fields
  incidentType?: string;
  priorityScore?: number;
  recommendedTeam?: string;
  teamDistanceKm?: number;
  estimatedEtaMinutes?: number;
  recommendedHospital?: string;
  hospitalDistanceKm?: number;
  recommendedShelter?: string;
  shelterDistanceKm?: number;
  riskZoneName?: string;
  assignmentStatus?: string;
  assignmentId?: number;
  notes?: string;
  // Phase 3 Part 2 Rich AI Triage Fields
  triageId?: number;
  triageStatus?: 'PENDING' | 'ANALYZING' | 'COMPLETE' | 'FAILED' | 'FALLBACK';
  confidence?: number;
  confidenceType?: string;
  reasoning?: string[];
  dataSources?: string[];
  facts?: string[] | {
    location?: number[];
    receivedAt?: string;
    message?: string;
    transport?: string;
    accuracyM?: number;
  } | Record<string, any>;
  predictions?: string[] | {
    floodProbability?: number;
    waterDepthM?: number;
    rainfallMm?: number;
    riskZoneName?: string;
    riskZoneLevel?: string;
  } | Record<string, any>;
  aiInterpretation?: string;
  recommendedAction?: string;
  humanConfirmationRequired?: boolean;
  staleDataWarning?: boolean | string;
  // Phase 3 Part 3 Rescue Intelligence Fields
  backendIncidentId?: number;
  rescueTeamId?: number;
  rescueTeamCoordinates?: [number, number];
  dispatchedAt?: string;
  dispatchedBy?: string;
  isOverride?: boolean;
  overrideReason?: string;
  distanceLabel?: string;
  routingLimitations?: string;
}

export interface SafeZone {
  id: string;
  name: string;
  type: 'SHELTER' | 'HOSPITAL' | 'RELIEF_CENTER' | 'ELEVATED_GROUND';
  coordinates: [number, number];
  capacity: number;
  currentOccupancy: number;
  distanceKm: number;
  status: 'OPEN' | 'NEAR_CAPACITY' | 'FULL';
  contact: string;
  supplies: {
    water: number; // percentage
    food: number;
    medical: number;
  };
}

export interface DisasterMarker {
  id: string;
  type: 'DISASTER' | 'EMERGENCY' | 'SAFE_ZONE';
  title: string;
  severity: RiskLevel;
  coordinates: [number, number];
  details: string;
}

export interface AIPredictionResult {
  riskScore: number;
  riskLevel: RiskLevel;
  rainfallPredictionMm: number;
  floodProbabilityPercent: number;
  affectedZoneKm2: number;
  evacuationRecommendation: string;
  confidenceScore: number;
  lastUpdated: string;
  modelName?: string;
  modelVersion?: string;
  dataSource?: string;
  dataSourceType?: 'historical_real' | 'live_weather_db' | 'simulation' | 'synthetic_prototype' | string;
  trainingDataset?: string;
  predictedCategory?: string;
  featureImportance?: Record<string, number>;
  topContributors?: Array<{
    feature: string;
    importance_pct: number;
    observed_value: number;
  }>;
  alertRecommendation?: string;
  topDrivers?: string[];
  disclaimer?: string;
  modelStatus?: 'ACTIVE' | 'CANDIDATE' | 'RETIRED' | string;
  dangerousEventRecall?: number;
}


export interface DashboardStats {
  rainfallMm: number;
  floodRiskPercent: number;
  affectedPopulation: number;
  activeSOSCount: number;
  availableShelters: number;
  rescueTeamsActive: number;
  activeAlerts?: number;
}

export interface UserProfile {
  name: string;
  email: string;
  role: 'DISPATCH_OFFICER' | 'COMMAND_SPECIALIST' | 'FIELD_RESPONDER';
  badgeNumber: string;
  station: string;
  prefersReducedMotion: boolean;
  notificationsEnabled: boolean;
}

export interface SpatialPostGISQuery {
  queryType: 'ST_DWithin' | 'ST_Contains' | 'ST_Buffer' | 'ST_Centroid';
  table: 'disaster_zones' | 'sos_requests' | 'safe_shelters' | 'weather_sensors';
  radiusKm: number;
  centerCoordinates: [number, number];
  returnedRowsCount: number;
  executionTimeMs: number;
}

export interface HistoricalFloodEvent {
  id: number;
  event_name: string;
  event_date: string;
  latitude: number;
  longitude: number;
  severity: string;
  rainfall_total_mm: number;
  duration_hours: number;
  source: string;
  source_type: string;
  description?: string;
  distance_km?: number;
}

export interface SpatialFeatures {
  latitude: number;
  longitude: number;
  elevation: number;
  slope: number;
  relative_elevation: number;
  low_elevation_flag: boolean;
  terrain_risk: number;
  nearest_drainage: string;
  distance_to_drainage_km: number;
  drainage_risk: number;
  historical_event_count: number;
  historical_flood_score: number;
  historical_severity: string;
  spatial_confidence: number;
  provenance: Record<string, any>;
}

export interface FloodIntelligenceResult {
  susceptibility_score: number;
  risk_level: RiskLevel;
  color_code: string;
  estimated_depth_m: number;
  depth_confidence: number;
  depth_type: 'PROXY_ESTIMATE' | 'OBSERVED' | 'MODELLED' | string;
  affected_area_km2: number;
  polygon_coordinates?: [number, number][];
  components: {
    rainfall_component: number;
    terrain_component: number;
    drainage_component: number;
    historical_component: number;
    weights: {
      rainfall: number;
      terrain: number;
      drainage: number;
      historical: number;
    };
  };
  spatial_features: SpatialFeatures;
  explanation: {
    FACT: string[];
    ML_PREDICTION: string[];
    GEOSPATIAL_DERIVATION: string[];
    AI_INTERPRETATION: string[];
    RECOMMENDATION: string[];
  };
  model_version: string;
  data_source_type: string;
  limitations: string[];
  disclaimer: string;
}

export interface InundationZoneFeature {
  id: string | number;
  name: string;
  polygon: [number, number][];
  severity: RiskLevel;
  depthM: number;
  affectedPop?: number;
  depthType?: string;
}



export type ForecastHorizon = '1H' | '3H' | '6H' | '12H' | '24H';

export interface ForecastHorizonData {
  horizon: ForecastHorizon;
  forecast_timestamp: string;
  risk_score: number;
  risk_level: RiskLevel;
  rainfall_estimate_mm: number;
  flood_susceptibility: number;
  proxy_depth_estimate_m: number;
  depth_type: string;
  is_hydraulic_simulation: boolean;
  confidence: number;
  uncertainty: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  uncertainty_summary: string;
  model_version: string;
  data_source: string;
  generated_at: string;
  valid_until?: string;
}

export interface ForecastTrajectory {
  trajectory: 'RAPIDLY_INCREASING' | 'INCREASING' | 'STABLE' | 'DECREASING' | 'RAPIDLY_DECREASING' | 'UNKNOWN';
  current_risk: number;
  peak_risk: number;
  peak_horizon: string;
  delta_6h: number;
  velocity_pts_per_hr: number;
  is_escalating: boolean;
  summary: string;
}

export interface EarlyWarningAlert {
  warning_state: 'NORMAL' | 'WATCH' | 'ADVISORY' | 'WARNING' | 'CRITICAL';
  headline: string;
  triggered_horizon: string;
  trigger_risk_score: number;
  confidence: number;
  uncertainty: number;
  is_inhibited: boolean;
  evidence_categories: {
    FACT: string[];
    ML_PREDICTION: string[];
    GEOSPATIAL_DERIVATION: string[];
    AI_INTERPRETATION: string[];
    RECOMMENDATION: string[];
  };
  actionable_instructions: string[];
}

export interface MultiHorizonForecastResult {
  location: {
    latitude: number;
    longitude: number;
  };
  current: {
    risk_score: number;
    risk_level: RiskLevel;
    rainfall_1h_mm: number;
    rainfall_24h_mm: number;
    elevation_m: number;
    nearest_drainage: string;
    timestamp: string;
  };
  horizons: Record<ForecastHorizon, ForecastHorizonData>;
  trajectory: ForecastTrajectory;
  early_warning: EarlyWarningAlert;
  uncertainty_overview: {
    average_confidence: number;
    average_uncertainty: number;
    confidence_rating: 'HIGH' | 'MEDIUM' | 'LOW';
    horizon_decay_active: boolean;
    scientific_note: string;
  };
  explainability: {
    FACT: string[];
    ML_PREDICTION: string[];
    GEOSPATIAL_DERIVATION: string[];
    AI_INTERPRETATION: string[];
    RECOMMENDATION: string[];
  };
  provenance: {
    model_version: string;
    data_source_type: string;
    data_source: string;
    is_hydraulic_simulation: boolean;
    depth_type: string;
    compliance: string;
  };
  generated_at: string;
}

// Phase 5.4: Adaptive Alert Intelligence Types
export type AlertIntelligenceCategory = 
  | 'WEATHER_ADVISORY'
  | 'HEAVY_RAINFALL_WARNING'
  | 'FLOOD_WATCH'
  | 'FLOOD_WARNING'
  | 'CRITICAL_FLOOD_WARNING'
  | 'EVACUATION_ADVISORY'
  | 'EMERGENCY_SAFETY_ALERT'
  | 'SYSTEM_INFORMATION';

export type AlertSeverityLevel = 'INFO' | 'ADVISORY' | 'WATCH' | 'WARNING' | 'CRITICAL';
export type ApprovalStatusType = 'RECOMMENDED' | 'APPROVED' | 'REJECTED' | 'EXPIRED' | 'CANCELLED';

export interface AlertTargetData {
  id?: number;
  target_type: string;
  location_name: string;
  geometry_wkt?: string;
  user_count_estimate: number;
  created_at?: string;
}

export interface AlertDeliveryData {
  id?: number;
  channel: string;
  status: string;
  attempt_count: number;
  sent_at?: string;
  delivered_at?: string;
  failed_at?: string;
}

export interface AlertAcknowledgementData {
  id?: number;
  alert_id: number;
  user_id?: number;
  client_id?: string;
  channel: string;
  acknowledged_at: string;
}

export interface AdaptiveAlert {
  id: number;
  title: string;
  message: string;
  alert_type: string;
  alert_category: AlertIntelligenceCategory;
  severity: AlertSeverityLevel;
  target_area: string;
  issued_at: string;
  expires_at?: string;
  status: string;
  approval_status: ApprovalStatusType;
  approved_by?: string;
  approved_at?: string;
  forecast_horizon?: string;
  risk_score?: number;
  confidence_score?: number;
  uncertainty_score?: number;
  risk_velocity?: number;
  evidence_categories?: {
    FACT: string[];
    ML_PREDICTION: string[];
    GEOSPATIAL_DERIVATION: string[];
    AI_INTERPRETATION: string[];
    RECOMMENDATION: string[];
  };
  actionable_instructions?: string[];
  targets?: AlertTargetData[];
  deliveries_count?: number;
  acknowledgements_count?: number;
  is_simulation?: boolean;
}

export interface AlertAnalyticsData {
  active_alerts_count: number;
  recommendations_count: number;
  critical_alerts_count: number;
  warning_alerts_count: number;
  total_affected_users_estimate: number;
  total_acknowledgements: number;
  acknowledgement_rate_percent: number;
  delivery_success_rate_percent: number;
  timestamp: string;
}

