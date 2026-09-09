export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
export type DominantThreat = 'FLOOD' | 'STORM' | 'LANDSLIDE' | 'CYCLONE' | 'EARTHQUAKE' | 'URBAN_WATERLOGGING';
export type SituationalTrend = 'ESCALATING' | 'STABLE' | 'DE_ESCALATING' | 'RAPIDLY_ESCALATING';

export type ProvenanceType = 
  | 'REAL' 
  | 'CACHED' 
  | 'MOCK' 
  | 'SIMULATION' 
  | 'DERIVED' 
  | 'ML_PREDICTION' 
  | 'AI_INTERPRETATION' 
  | 'RECOMMENDATION';

export interface SituationalSnapshot {
  id?: number;
  riskScore: number;
  riskLevel: RiskLevel;
  dominantThreat: DominantThreat | string;
  trend: SituationalTrend | string;
  activeEmergencies: number;
  criticalEmergencies: number;
  activeAlertsCount: number;
  assignedTeamsCount: number;
  enRouteTeamsCount: number;
  resourceContentionsCount: number;
  operationalBottlenecksCount: number;
  provenance: ProvenanceType;
  confidence: number;
  summary: string;
  delta?: {
    riskScoreDelta: number;
    activeEmergenciesDelta: number;
    criticalEmergenciesDelta: number;
    alertsDelta: number;
    timeDeltaSeconds: number;
    direction: 'INCREASED' | 'DECREASED' | 'UNCHANGED';
  };
  createdAt: string;
}

export interface OperationalChange {
  changeType: string;
  severity: RiskLevel;
  metric: string;
  previousValue: number | string;
  currentValue: number | string;
  delta: number;
  significance: 'MINOR' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  description: string;
  provenance: ProvenanceType;
  timestamp: string;
}

export interface RiskHotspot {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  radiusMeters: number;
  compositeScore: number;
  severity: RiskLevel;
  contributingSignals: {
    rainfall?: number;
    floodProb?: number;
    drainage?: number;
    sosDensity?: number;
    elevation?: number;
    [key: string]: any;
  };
  status: 'ACTIVE' | 'RESOLVING' | 'INACTIVE';
  provenance: ProvenanceType;
  confidence: number;
  createdAt: string;
}

export interface IncidentCluster {
  id: number;
  clusterCode: string;
  centerLat: number;
  centerLon: number;
  radiusMeters: number;
  incidentCount: number;
  criticalCount: number;
  compositePriority: number;
  status: 'ACTIVE' | 'RESOLVED' | 'MERGED';
  incidentIds: number[];
  recommendedTeams: Array<{
    teamId: number;
    teamName: string;
    matchScore: number;
    distanceKm?: number;
  }>;
  provenance: ProvenanceType;
  confidence: number;
  createdAt: string;
}

export interface OperatorAttentionItem {
  id: number;
  title: string;
  summary: string;
  priority: RiskLevel;
  status: 'PENDING' | 'ACKNOWLEDGED' | 'RESOLVED';
  itemType: string;
  provenance: ProvenanceType;
  recommendedAction: string;
  actionData?: Record<string, any>;
  acknowledgedAt?: string;
  acknowledgedBy?: string;
  createdAt: string;
}

export interface OperationalEvent {
  id: number;
  eventType: string;
  category: string;
  severity: RiskLevel;
  title: string;
  description: string;
  provenance: ProvenanceType;
  actor: string;
  confidence: number;
  eventMetadata?: Record<string, any>;
  createdAt: string;
}

export interface ResponseOption {
  optionId: 'A' | 'B';
  teamId: number;
  teamName: string;
  teamType: string;
  distanceKm: number;
  estimatedArrivalMinutes: number;
  capabilityMatchScore: number;
  currentWorkload: number;
  advantages: string[];
  warnings: string[];
}

export interface ResourceContention {
  id: string;
  incidentId: number;
  incidentTitle: string;
  incidentSeverity: RiskLevel;
  location: string;
  requestedCapability: string;
  contenders: Array<{ incidentId: number; priority: RiskLevel; title: string }>;
  optionA: ResponseOption;
  optionB: ResponseOption;
  provenance: ProvenanceType;
  recommendedAction: string;
}

export interface EvidenceItem {
  type: 'FACT' | 'ML_PREDICTION' | 'GEOSPATIAL_DERIVATION' | 'AI_INTERPRETATION' | 'RECOMMENDATION';
  statement: string;
  confidence: number;
  source: string;
  timestamp: string;
}

export interface AIBriefing {
  executiveSummary: string;
  evidenceItems: EvidenceItem[];
  dominantThreat: string;
  recommendedPriorities: string[];
  generatedAt: string;
  provenance: ProvenanceType;
  confidence: number;
}
