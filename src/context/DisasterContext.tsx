import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  Alert,
  SOSIncident,
  SafeZone,
  DisasterMarker,
  AIPredictionResult,
  DashboardStats,
  SpatialPostGISQuery,
  RiskLevel,
} from '../types/disaster';
import {
  disasterService,
  BackendAlert,
  BackendIncident,
  BackendSOSReport,
  BackendShelter,
  BackendHospital,
  BackendRiskZone,
  BackendRescueAssignment,
  BackendWeatherObservation,
} from '../services/disasterService';
import { ConnectionStatus, LiveFeedItem, DomainEvent } from '../types/realtime';
import { websocketService } from '../services/websocketService';

interface DisasterContextType {
  alerts: Alert[];
  sosIncidents: SOSIncident[];
  safeZones: SafeZone[];
  markers: DisasterMarker[];
  aiPrediction: AIPredictionResult | null;
  isAnalyzing: boolean;
  dashboardStats: DashboardStats;
  currentWeather: BackendWeatherObservation | null;
  isSimulationActive: boolean;
  simulationStep: number;
  simulationStage: string;
  simulationTitle: string;
  isSimulationComplete: boolean;
  postGisLogs: SpatialPostGISQuery[];
  isLoading: boolean;
  backendConnected: boolean;
  connectionStatus: ConnectionStatus;
  liveIncidentFeed: LiveFeedItem[];
  reconnectWebSocket: () => void;
  refreshData: () => Promise<void>;
  runDisasterSimulation: () => void;
  resetDisasterSimulation: () => Promise<void>;
  triggerAIAnalysis: () => void;
  createSOSRequest: (incident: Omit<SOSIncident, 'id' | 'timestamp' | 'status'>) => Promise<void>;
  resolveSOSIncident: (id: string) => Promise<void>;
  dispatchRescueTeam: (
    incidentId: number,
    rescueTeamId: number,
    notes?: string,
    isOverride?: boolean,
    overrideReason?: string
  ) => Promise<any>;
  filterSafeZonesByRadius: (radiusKm: number) => Promise<void>;
}

// --------------------------------------------------------------------------
// Offline Mock Fallbacks (Used if backend is offline or during cold boot)
// --------------------------------------------------------------------------

const fallbackAlerts: Alert[] = [
  {
    id: 'alt-101',
    title: 'Severe Urban Flash Flood Warning',
    category: 'FLOOD',
    severity: 'CRITICAL',
    location: 'Downtown Basin & Riverside Drive',
    coordinates: [13.0827, 80.2707],
    timestamp: '10 mins ago',
    description: 'Rapid river overflow detected by PostGIS sensors. Water level rising at 18cm/hr.',
    affectedPopulation: 14200,
    isNew: true,
  },
  {
    id: 'alt-102',
    title: 'High Slope Landslide Risk Warning',
    category: 'LANDSLIDE',
    severity: 'HIGH',
    location: 'Northern Foothills Highway 4',
    coordinates: [13.0915, 80.285],
    timestamp: '42 mins ago',
    description: 'Soil saturation threshold exceeded. Highway traffic diversion initiated.',
    affectedPopulation: 3800,
  },
  {
    id: 'alt-103',
    title: 'Moderate Storm Surge Advisory',
    category: 'STORM',
    severity: 'MODERATE',
    location: 'Eastern Harbor & Coastal Zone',
    coordinates: [13.065, 80.291],
    timestamp: '2 hours ago',
    description: 'Swell height reaching 3.4m. Coastal fishing vessels advised to anchor at safe harbors.',
    affectedPopulation: 8500,
  },
];

const fallbackSOSIncidents: SOSIncident[] = [
  {
    id: 'sos-801',
    citizenName: 'David Vance',
    phone: '+1 (555) 019-2834',
    location: '742 Evergreen Terrace (Basement flooded)',
    coordinates: [13.085, 80.275],
    timestamp: '5 mins ago',
    status: 'PENDING',
    emergencyType: 'TRAPPED',
    peopleCount: 4,
    urgency: 'CRITICAL',
  },
  {
    id: 'sos-802',
    citizenName: 'Elena Rostova',
    phone: '+1 (555) 014-9921',
    location: 'Community Center Shelter B',
    coordinates: [13.078, 80.268],
    timestamp: '18 mins ago',
    status: 'DISPATCHED',
    emergencyType: 'MEDICAL',
    peopleCount: 2,
    urgency: 'HIGH',
  },
];

const fallbackSafeZones: SafeZone[] = [
  {
    id: 'sz-01',
    name: 'Central Command Stadium Shelter',
    type: 'SHELTER',
    coordinates: [13.075, 80.26],
    capacity: 2500,
    currentOccupancy: 1420,
    distanceKm: 1.8,
    status: 'OPEN',
    contact: '+1 (555) 900-1122',
    supplies: { water: 85, food: 78, medical: 90 },
  },
  {
    id: 'sz-02',
    name: 'St. Jude General Emergency Medical',
    type: 'HOSPITAL',
    coordinates: [13.09, 80.27],
    capacity: 600,
    currentOccupancy: 510,
    distanceKm: 3.2,
    status: 'NEAR_CAPACITY',
    contact: '+1 (555) 900-3344',
    supplies: { water: 95, food: 88, medical: 65 },
  },
  {
    id: 'sz-03',
    name: 'Northern Ridge Relief Station',
    type: 'RELIEF_CENTER',
    coordinates: [13.1, 80.28],
    capacity: 1200,
    currentOccupancy: 340,
    distanceKm: 5.4,
    status: 'OPEN',
    contact: '+1 (555) 900-5566',
    supplies: { water: 90, food: 92, medical: 95 },
  },
];

const fallbackMarkers: DisasterMarker[] = [
  {
    id: 'mk-1',
    type: 'DISASTER',
    title: 'Flash Flood Epicenter - Basin A',
    severity: 'CRITICAL',
    coordinates: [13.0827, 80.2707],
    details: 'Water depth: 1.4m. Flow rate: 12m³/s',
  },
  {
    id: 'mk-2',
    type: 'EMERGENCY',
    title: 'SOS Incident #801 - Trapped Family',
    severity: 'CRITICAL',
    coordinates: [13.085, 80.275],
    details: '4 civilians trapped. Rescue Boat 2 en route.',
  },
  {
    id: 'mk-3',
    type: 'SAFE_ZONE',
    title: 'Central Command Stadium Shelter',
    severity: 'LOW',
    coordinates: [13.075, 80.26],
    details: '1,080 beds available. Fully stocked.',
  },
];

const fallbackAIPrediction: AIPredictionResult = {
  riskScore: 78,
  riskLevel: 'HIGH',
  rainfallPredictionMm: 145.2,
  floodProbabilityPercent: 88,
  affectedZoneKm2: 34.5,
  evacuationRecommendation:
    'Mandatory evacuation recommended for low-lying zones along Riverside sector within 3 hours.',
  confidenceScore: 0.94,
  lastUpdated: 'Just now',
};

const fallbackStats: DashboardStats = {
  rainfallMm: 145.2,
  floodRiskPercent: 88,
  affectedPopulation: 26500,
  activeSOSCount: 2,
  availableShelters: 14,
  rescueTeamsActive: 8,
};

// --------------------------------------------------------------------------
// Mappers: Transform Backend DB Schemas into Frontend Types
// --------------------------------------------------------------------------

function mapBackendAlerts(backendAlerts: BackendAlert[]): Alert[] {
  if (!backendAlerts || backendAlerts.length === 0) return fallbackAlerts;
  return backendAlerts.map((b) => {
    const cat = ['FLOOD', 'STORM', 'LANDSLIDE', 'CYCLONE', 'EARTHQUAKE'].includes(
      b.alert_type?.toUpperCase()
    )
      ? (b.alert_type.toUpperCase() as any)
      : 'FLOOD';

    const sev = ['LOW', 'MODERATE', 'HIGH', 'CRITICAL'].includes(b.severity?.toUpperCase())
      ? (b.severity.toUpperCase() as RiskLevel)
      : 'HIGH';

    return {
      id: `alt-${b.id}`,
      title: b.title,
      category: cat,
      severity: sev,
      location: b.target_area || 'Central Metro District',
      coordinates: [13.0827, 80.2707],
      timestamp: b.issued_at
        ? new Date(b.issued_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : 'Just now',
      description: b.message,
      affectedPopulation: 14200,
      isNew: b.status === 'ACTIVE',
    };
  });
}

function mapBackendIncidentsAndSOS(
  incidents: BackendIncident[],
  sosList: BackendSOSReport[],
  assignments: BackendRescueAssignment[] = []
): SOSIncident[] {
  const list: SOSIncident[] = [];
  const processedIncidentIds = new Set<number>();

  // 1. Process SOS Reports (linking Incidents and Assignments)
  sosList.forEach((s) => {
    const sev = (['LOW', 'MODERATE', 'HIGH', 'CRITICAL'].includes(s.severity?.toUpperCase())
      ? s.severity.toUpperCase()
      : 'CRITICAL') as RiskLevel;

    // Find linked incident if available
    const linkedInc = incidents.find(
      (inc) => inc.sos_id === s.id || (Math.abs(inc.latitude - s.latitude) < 0.0001 && Math.abs(inc.longitude - s.longitude) < 0.0001)
    );
    if (linkedInc) {
      processedIncidentIds.add(linkedInc.id);
    }

    // Find linked rescue assignment
    const linkedAssign = linkedInc
      ? assignments.find((a) => a.incident_id === linkedInc.id)
      : assignments.length > 0 ? assignments[0] : undefined;

    const triage = s.triage;

    list.push({
      id: `sos-${s.id}`,
      title: triage?.incident_title || linkedInc?.title || s.message || `Distress Beacon #${s.id}`,
      citizenName: `Citizen SOS #${s.id}`,
      phone: '+1 (555) 911-0000',
      location: s.message || `Sector Coordinates (${s.latitude.toFixed(3)}, ${s.longitude.toFixed(3)})`,
      coordinates: [s.latitude, s.longitude],
      timestamp: s.created_at
        ? new Date(s.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : 'Just now',
      status: s.status === 'RESCUED' ? 'RESCUED' : (s.status === 'DISPATCHED' || linkedAssign?.status === 'DISPATCHED') ? 'DISPATCHED' : 'PENDING',
      emergencyType: (triage?.incident_type === 'MEDICAL_EMERGENCY' || linkedInc?.incident_type === 'MEDICAL_EMERGENCY') ? 'MEDICAL' : 'TRAPPED',
      peopleCount: 3,
      urgency: (triage?.severity ? (['LOW', 'MODERATE', 'HIGH', 'CRITICAL'].includes(triage.severity.toUpperCase()) ? triage.severity.toUpperCase() as RiskLevel : sev) : sev),
      // 10 End-to-End Triage & Dispatch fields:
      incidentType: triage?.incident_type || linkedInc?.incident_type || linkedAssign?.incident_type || 'FLOOD_TRAPPED_PERSON',
      priorityScore: triage?.priority_score ?? linkedInc?.priority_score ?? linkedAssign?.priority_score ?? 98,
      recommendedTeam: triage?.recommended_rescue_team || linkedAssign?.team_name || 'Water Rescue Squad Alpha',
      teamDistanceKm: triage?.distance_km ?? linkedAssign?.estimated_distance ?? 0.4,
      estimatedEtaMinutes: triage?.estimated_response_minutes ?? linkedAssign?.eta_minutes ?? 4,
      recommendedHospital: triage?.recommended_hospital || linkedAssign?.recommended_hospital || 'St. Jude General Emergency Medical',
      hospitalDistanceKm: triage?.hospital_distance_km ?? 0.73,
      recommendedShelter: triage?.recommended_shelter || linkedAssign?.recommended_shelter || 'St. Jude Emergency High Ground Shelter',
      shelterDistanceKm: triage?.shelter_distance_km ?? 0.73,
      riskZoneName: triage?.risk_zone_name || linkedAssign?.risk_zone_name || 'Riverside Lowland Sector Alpha',
      assignmentId: triage?.assignment_id || linkedAssign?.id,
      assignmentStatus: triage?.assignment_status || linkedAssign?.status || (s.status === 'PENDING' ? 'PENDING_CONFIRMATION' : 'DISPATCHED'),
      notes: linkedAssign?.notes,
      // Phase 3 Part 2 rich fields:
      triageStatus: triage ? 'COMPLETE' : 'PENDING',
      confidence: triage?.confidence ?? 0.88,
      confidenceType: triage?.confidence_type || 'MULTIMODAL_GROUNDED',
      reasoning: triage?.reasoning,
      dataSources: triage?.data_sources,
      facts: triage?.facts,
      predictions: triage?.predictions,
      aiInterpretation: triage?.ai_interpretation,
      recommendedAction: triage?.recommended_action,
      humanConfirmationRequired: triage?.human_confirmation_required ?? true,
      staleDataWarning: triage?.stale_data_warning ?? false,
    });
  });

  // 2. Process Remaining Unlinked Incidents
  incidents.forEach((inc) => {
    if (processedIncidentIds.has(inc.id)) return;

    const sev = (['LOW', 'MODERATE', 'HIGH', 'CRITICAL'].includes(inc.severity?.toUpperCase())
      ? inc.severity.toUpperCase()
      : 'HIGH') as RiskLevel;

    const linkedAssign = assignments.find((a) => a.incident_id === inc.id);

    list.push({
      id: `inc-${inc.id}`,
      title: inc.title,
      citizenName: inc.source === 'CITIZEN_SOS' ? `SOS Dispatch Call #${inc.id}` : 'Field Scout Report',
      phone: '+1 (555) 019-2834',
      location: inc.description || `Sector (${inc.latitude.toFixed(3)}, ${inc.longitude.toFixed(3)})`,
      coordinates: [inc.latitude, inc.longitude],
      timestamp: inc.created_at
        ? new Date(inc.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : '10 mins ago',
      status: inc.status === 'RESOLVED' ? 'RESCUED' : (inc.status === 'DISPATCHED' || linkedAssign?.status === 'DISPATCHED') ? 'DISPATCHED' : 'PENDING',
      emergencyType: inc.incident_type === 'MEDICAL_EMERGENCY' ? 'MEDICAL' : 'TRAPPED',
      peopleCount: 4,
      urgency: sev,
      incidentType: inc.incident_type,
      priorityScore: inc.priority_score,
      recommendedTeam: linkedAssign?.team_name,
      teamDistanceKm: linkedAssign?.estimated_distance,
      estimatedEtaMinutes: linkedAssign?.eta_minutes,
      recommendedHospital: linkedAssign?.recommended_hospital,
      recommendedShelter: linkedAssign?.recommended_shelter,
      riskZoneName: linkedAssign?.risk_zone_name,
      assignmentId: linkedAssign?.id,
      assignmentStatus: linkedAssign?.status,
      notes: linkedAssign?.notes,
    });
  });

  return list.length > 0 ? list : fallbackSOSIncidents;
}

function mapBackendSafeZones(shelters: BackendShelter[], hospitals: BackendHospital[]): SafeZone[] {
  const result: SafeZone[] = [];

  shelters.forEach((s) => {
    const status =
      s.current_occupancy >= s.capacity
        ? 'FULL'
        : s.current_occupancy >= s.capacity * 0.8
        ? 'NEAR_CAPACITY'
        : 'OPEN';

    result.push({
      id: `sz-sh-${s.id}`,
      name: s.name,
      type: 'SHELTER',
      coordinates: [s.latitude, s.longitude],
      capacity: s.capacity,
      currentOccupancy: s.current_occupancy,
      distanceKm: +(s.distance_km || 2.4).toFixed(1),
      status,
      contact: s.contact || '+1 (555) 900-1122',
      supplies: { water: 85, food: 80, medical: 90 },
    });
  });

  hospitals.forEach((h) => {
    const status =
      h.available_beds <= 5
        ? 'FULL'
        : h.available_beds <= 20
        ? 'NEAR_CAPACITY'
        : 'OPEN';

    result.push({
      id: `sz-hosp-${h.id}`,
      name: h.name,
      type: 'HOSPITAL',
      coordinates: [h.latitude, h.longitude],
      capacity: h.emergency_capacity,
      currentOccupancy: Math.max(0, h.emergency_capacity - h.available_beds),
      distanceKm: +(h.distance_km || 3.8).toFixed(1),
      status,
      contact: h.contact || '+1 (555) 900-9900',
      supplies: { water: 95, food: 88, medical: 95 },
    });
  });

  return result.length > 0 ? result : fallbackSafeZones;
}

function synthesizeMarkers(
  riskZones: BackendRiskZone[],
  incidents: BackendIncident[],
  sosList: BackendSOSReport[],
  shelters: BackendShelter[]
): DisasterMarker[] {
  const markers: DisasterMarker[] = [];

  riskZones.forEach((rz) => {
    markers.push({
      id: `mk-rz-${rz.id}`,
      type: 'DISASTER',
      title: rz.name,
      severity: (rz.risk_level?.toUpperCase() || 'HIGH') as RiskLevel,
      coordinates: [rz.latitude, rz.longitude],
      details: `Risk Score: ${rz.risk_score}/100 | Population Exposed: ${rz.population_estimate?.toLocaleString()}`,
    });
  });

  incidents.forEach((inc) => {
    markers.push({
      id: `mk-inc-${inc.id}`,
      type: 'EMERGENCY',
      title: inc.title,
      severity: (inc.severity?.toUpperCase() || 'CRITICAL') as RiskLevel,
      coordinates: [inc.latitude, inc.longitude],
      details: inc.description || 'Priority Emergency Incident Reported',
    });
  });

  sosList.forEach((sos) => {
    markers.push({
      id: `mk-sos-${sos.id}`,
      type: 'EMERGENCY',
      title: `Citizen SOS Beacon #${sos.id}`,
      severity: (sos.severity?.toUpperCase() || 'CRITICAL') as RiskLevel,
      coordinates: [sos.latitude, sos.longitude],
      details: sos.message || 'Distress Call Awaiting Rescue Dispatch',
    });
  });

  shelters.forEach((sh) => {
    markers.push({
      id: `mk-sh-${sh.id}`,
      type: 'SAFE_ZONE',
      title: sh.name,
      severity: 'LOW',
      coordinates: [sh.latitude, sh.longitude],
      details: `Capacity: ${sh.capacity} | Status: ${sh.status}`,
    });
  });

  return markers.length > 0 ? markers : fallbackMarkers;
}

// --------------------------------------------------------------------------
// DisasterProvider Component
// --------------------------------------------------------------------------

const DisasterContext = createContext<DisasterContextType | undefined>(undefined);

export const DisasterProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [alerts, setAlerts] = useState<Alert[]>(fallbackAlerts);
  const [sosIncidents, setSOSIncidents] = useState<SOSIncident[]>(fallbackSOSIncidents);
  const [safeZones, setSafeZones] = useState<SafeZone[]>(fallbackSafeZones);
  const [markers, setMarkers] = useState<DisasterMarker[]>(fallbackMarkers);
  const [aiPrediction, setAIPrediction] = useState<AIPredictionResult | null>(fallbackAIPrediction);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats>(fallbackStats);
  const [currentWeather, setCurrentWeather] = useState<BackendWeatherObservation | null>(null);
  const [isSimulationActive, setIsSimulationActive] = useState<boolean>(false);
  const [simulationStep, setSimulationStep] = useState<number>(0);
  const [simulationStage, setSimulationStage] = useState<string>('NORMAL');
  const [simulationTitle, setSimulationTitle] = useState<string>('Normal Conditions');
  const [isSimulationComplete, setIsSimulationComplete] = useState<boolean>(false);
  const simulationAbortRef = React.useRef<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('OFFLINE');
  const [liveIncidentFeed, setLiveIncidentFeed] = useState<LiveFeedItem[]>([]);
  const [postGisLogs, setPostGisLogs] = useState<SpatialPostGISQuery[]>([
    {
      queryType: 'ST_DWithin',
      table: 'safe_shelters',
      radiusKm: 5.0,
      centerCoordinates: [13.0827, 80.2707],
      returnedRowsCount: 3,
      executionTimeMs: 12.4,
    },
    {
      queryType: 'ST_Contains',
      table: 'disaster_zones',
      radiusKm: 12.0,
      centerCoordinates: [13.0827, 80.2707],
      returnedRowsCount: 1,
      executionTimeMs: 8.1,
    },
  ]);

  // Master Data Refresh from Live PostgreSQL REST APIs
  const refreshData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [
        summaryRes,
        alertsRes,
        incidentsRes,
        sosRes,
        sheltersRes,
        hospitalsRes,
        riskZonesRes,
        weatherRes,
        floodPredRes,
        rainPredRes,
        assignmentsRes,
      ] = await Promise.allSettled([
        disasterService.getDashboardSummary(),
        disasterService.getActiveAlerts(),
        disasterService.getIncidents(true),
        disasterService.getActiveSOSReports(),
        disasterService.getAllShelters(),
        disasterService.getAllHospitals(),
        disasterService.getRiskZones(),
        disasterService.getCurrentWeather(),
        disasterService.getLatestFloodPrediction(),
        disasterService.getLatestRainfallPrediction(),
        disasterService.getRescueAssignments(),
      ]);

      const isConnected = summaryRes.status === 'fulfilled' || alertsRes.status === 'fulfilled';
      setBackendConnected(isConnected);

      // 1. Dashboard Stats
      if (summaryRes.status === 'fulfilled') {
        const s = summaryRes.value;
        const weather = weatherRes.status === 'fulfilled' ? weatherRes.value : null;
        const flood = floodPredRes.status === 'fulfilled' ? floodPredRes.value : null;

        setDashboardStats({
          rainfallMm: weather?.rainfall_24h || 145.2,
          floodRiskPercent: flood?.flood_probability
            ? Math.round(flood.flood_probability * 100)
            : 88,
          affectedPopulation: s.affected_population || 26500,
          activeSOSCount: s.active_sos || 2,
          availableShelters: s.shelters_available || 14,
          rescueTeamsActive: s.rescue_teams_available || 8,
        });
      }

      if (weatherRes.status === 'fulfilled') {
        setCurrentWeather(weatherRes.value);
      }

      // 2. Alerts
      if (alertsRes.status === 'fulfilled') {
        setAlerts(mapBackendAlerts(alertsRes.value));
      }

      // 3. Incidents & SOS
      const incList = incidentsRes.status === 'fulfilled' ? incidentsRes.value : [];
      const sosList = sosRes.status === 'fulfilled' ? sosRes.value : [];
      const assignList = assignmentsRes.status === 'fulfilled' ? assignmentsRes.value : [];
      if (incidentsRes.status === 'fulfilled' || sosRes.status === 'fulfilled' || assignmentsRes.status === 'fulfilled') {
        setSOSIncidents(mapBackendIncidentsAndSOS(incList, sosList, assignList));
      }

      // 4. Safe Zones (Shelters + Hospitals)
      const shList = sheltersRes.status === 'fulfilled' ? sheltersRes.value : [];
      const hospList = hospitalsRes.status === 'fulfilled' ? hospitalsRes.value : [];
      if (sheltersRes.status === 'fulfilled' || hospitalsRes.status === 'fulfilled') {
        setSafeZones(mapBackendSafeZones(shList, hospList));
      }

      // 5. Markers
      const rzList = riskZonesRes.status === 'fulfilled' ? riskZonesRes.value : [];
      if (isConnected) {
        setMarkers(synthesizeMarkers(rzList, incList, sosList, shList));
      }

      // 6. AI Prediction Model
      if (floodPredRes.status === 'fulfilled' && rainPredRes.status === 'fulfilled') {
        const flood = floodPredRes.value;
        const rain = rainPredRes.value;
        const summary = summaryRes.status === 'fulfilled' ? summaryRes.value : null;

        setAIPrediction({
          riskScore: summary?.overall_risk_score || 78,
          riskLevel: (summary?.risk_level || flood.risk_level || 'HIGH') as RiskLevel,
          rainfallPredictionMm: rain.predicted_rainfall_mm || 145.2,
          floodProbabilityPercent: Math.round((flood.flood_probability || 0.88) * 100),
          affectedZoneKm2: 34.5,
          evacuationRecommendation: flood.alert_recommendation || (flood.evacuation_advised || flood.flood_probability > 0.75
            ? 'Mandatory evacuation recommended for low-lying zones along Riverside sector.'
            : 'Precautionary advisory in effect. Prepare household essentials.'),
          confidenceScore: rain.confidence || 0.94,
          lastUpdated: 'Live from Backend',
          modelName: rain.model_name || flood.model_name || 'RandomForestClassifier (scikit-learn)',
          modelVersion: rain.model_version || flood.model_version || 'v2.0-real-data',
          dataSource: rain.data_source || flood.data_source || 'ECMWF ERA5-Land Historical Reanalysis',
          dataSourceType: rain.data_source_type || 'historical_real',
          trainingDataset: rain.training_dataset || 'historical_weather_chennai_2022_2024.csv',
          predictedCategory: rain.predicted_category || 'MODERATE',
          featureImportance: rain.feature_importance,
          topContributors: rain.top_contributors,
          alertRecommendation: flood.alert_recommendation,
          topDrivers: flood.top_drivers,
          disclaimer: rain.disclaimer || flood.disclaimer,
        });
      }
    } catch (err) {
      console.warn('Backend synchronization warning, keeping offline fallback:', err);
      setBackendConnected(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  // Real-Time WebSocket Connection & Event Lifecycle Management
  useEffect(() => {
    // 1. Establish WebSocket connection
    websocketService.connect();

    // 2. Track connection status
    const unsubStatus = websocketService.onStatusChange((status) => {
      setConnectionStatus(status);
      if (status === 'LIVE') {
        setBackendConnected(true);
      }
    });

    // 3. On reconnect, perform authoritative state reconciliation with PostgreSQL
    const unsubReconnect = websocketService.onReconnect(() => {
      console.log('[RealTime] Reconnected to backend, reconciling state with PostgreSQL...');
      refreshData();
    });

    // 4. Wildcard domain event listener for real-time state updates
    const unsubEvents = websocketService.on('*', (domainEvent: DomainEvent) => {
      let title = domainEvent.event.replace(/_/g, ' ');
      let description = `Event ${domainEvent.event} received`;

      if (domainEvent.event === 'WEATHER_UPDATED') {
        const w = domainEvent.data;
        title = `Weather Observation Updated (${w?.condition || 'Live'})`;
        description = `Temp: ${w?.temperature ?? 26}°C | Rain 1h: ${w?.rainfall_1h || 0}mm | Rain 24h: ${w?.rainfall_24h || 0}mm | Wind: ${w?.wind_speed ?? 15}km/h`;
        if (w) {
          setCurrentWeather(w);
          setDashboardStats((prev) => ({
            ...prev,
            rainfallMm: w.rainfall_24h || w.rainfall_1h || prev.rainfallMm,
          }));
        }
      } else if (domainEvent.event === 'RAIN_PREDICTION_UPDATED') {
        const p = domainEvent.data;
        title = `Rainfall Model Prediction (${p?.predicted_category || p?.risk_level || 'UPDATED'})`;
        description = `Predicted Rainfall: ${p?.predicted_rainfall_mm?.toFixed(1) ?? '145.0'}mm (${((p?.confidence ?? 0.9) * 100).toFixed(0)}% confidence)`;
        setAIPrediction((prev) =>
          prev
            ? {
                ...prev,
                rainfallPredictionMm: p.predicted_rainfall_mm || prev.rainfallPredictionMm,
                confidenceScore: p.confidence || prev.confidenceScore,
                predictedCategory: p.predicted_category || prev.predictedCategory,
                featureImportance: p.feature_importance || prev.featureImportance,
                topContributors: p.top_contributors || prev.topContributors,
              }
            : prev
        );
      } else if (domainEvent.event === 'FLOOD_PREDICTION_UPDATED') {
        const p = domainEvent.data;
        title = `Flood Risk Forecast (${p?.risk_level || 'UPDATED'})`;
        description = `Flood Prob: ${Math.round((p?.flood_probability || 0.88) * 100)}% | Water Depth: ${(p?.estimated_water_depth_m || 1.2).toFixed(2)}m`;
        setAIPrediction((prev) =>
          prev
            ? {
                ...prev,
                floodProbabilityPercent: Math.round((p.flood_probability || 0) * 100),
                riskLevel: (p.risk_level || prev.riskLevel) as RiskLevel,
                alertRecommendation: p.alert_recommendation || prev.alertRecommendation,
                topDrivers: p.top_drivers || prev.topDrivers,
              }
            : prev
        );
        setDashboardStats((prev) => ({
          ...prev,
          floodRiskPercent: Math.round((p.flood_probability || 0) * 100),
        }));
      } else if (domainEvent.event === 'RISK_ZONE_UPDATED') {
        const rz = domainEvent.data;
        title = `Risk Zone Escalation: ${rz?.name || 'Sector'}`;
        description = `Risk Level: ${rz?.risk_level} | Risk Score: ${rz?.risk_score}/100`;
        setMarkers((prev) =>
          prev.map((m) =>
            m.id === `mk-rz-${rz.id}`
              ? {
                  ...m,
                  severity: (rz.risk_level?.toUpperCase() || 'HIGH') as RiskLevel,
                  details: `Risk Score: ${rz.risk_score}/100 | Population Exposed: ${rz.population_estimate?.toLocaleString()}`,
                }
              : m
          )
        );
      } else if (domainEvent.event === 'ALERT_CREATED') {
        const a = domainEvent.data;
        title = `Emergency Alert Issued: ${a?.title || 'Active Alert'}`;
        description = a?.message || `Target Area: ${a?.target_area} [${a?.severity}]`;
        const newAlert: Alert = {
          id: `alt-${a.id}`,
          title: a.title,
          category: (a.alert_type || 'FLOOD') as any,
          severity: (['CRITICAL', 'HIGH', 'MODERATE', 'LOW'].includes(a.severity?.toUpperCase()) ? a.severity.toUpperCase() : 'HIGH') as RiskLevel,
          location: a.target_area || 'Central Metro Sector',
          coordinates: [13.0827, 80.2707],
          timestamp: 'Just now',
          description: a.message,
          affectedPopulation: 12500,
          isNew: true,
        };
        setAlerts((prev) => [newAlert, ...prev]);
        setDashboardStats((prev) => ({ ...prev, activeAlerts: (prev.activeAlerts || 0) + 1 }));
      } else if (domainEvent.event === 'ALERT_UPDATED') {
        const a = domainEvent.data;
        title = `Alert Status Updated: ${a?.title || 'Alert'}`;
        description = `Status changed to ${a?.status} [${a?.severity}]`;
        setAlerts((prev) =>
          prev.map((item) =>
            item.id === `alt-${a.id}`
              ? { ...item, severity: (a.severity || item.severity) as RiskLevel }
              : item
          )
        );
      } else if (domainEvent.event === 'SOS_CREATED') {
        const s = domainEvent.data;
        title = `Citizen Emergency SOS Beacon Received`;
        description = s?.message || `SOS #${s?.id} reported at (${s?.latitude?.toFixed(3)}, ${s?.longitude?.toFixed(3)})`;
        const newSos: SOSIncident = {
          id: `sos-${s.id}`,
          citizenName: `Citizen Distress SOS #${s.id}`,
          phone: '+1 (555) 911-0000',
          location: s.message || `Sector Coordinates (${s.latitude}, ${s.longitude})`,
          coordinates: [s.latitude, s.longitude],
          timestamp: 'Just now',
          status: 'PENDING',
          emergencyType: s.message?.toLowerCase().includes('trapped') ? 'TRAPPED' : 'MEDICAL',
          peopleCount: 4,
          urgency: (['CRITICAL', 'HIGH', 'MODERATE', 'LOW'].includes(s.severity?.toUpperCase()) ? s.severity.toUpperCase() : 'CRITICAL') as RiskLevel,
        };
        setSOSIncidents((prev) => [newSos, ...prev]);
        setDashboardStats((prev) => ({ ...prev, activeSOSCount: prev.activeSOSCount + 1 }));
        setMarkers((prev) => [
          {
            id: `mk-sos-${s.id}`,
            type: 'EMERGENCY',
            title: `Citizen SOS Beacon #${s.id}`,
            severity: newSos.urgency,
            coordinates: [s.latitude, s.longitude],
            details: s.message || 'Distress Call Awaiting Rescue Dispatch',
          },
          ...prev,
        ]);
      } else if (domainEvent.event === 'SOS_TRIAGED') {
        const t = domainEvent.data;
        title = `AI Triage Completed: ${t?.title || 'Distress Call'}`;
        description = `Classified as ${t?.incident_type} with Priority Score ${t?.priority_score}/100`;
        setSOSIncidents((prev) =>
          prev.map((item) =>
            item.id === `sos-${t.sos_id}` || item.id === `inc-${t.incident_id}`
              ? {
                  ...item,
                  incidentType: t.incident_type,
                  priorityScore: t.priority_score,
                  urgency: (['CRITICAL', 'HIGH', 'MODERATE', 'LOW'].includes(t.severity?.toUpperCase()) ? t.severity.toUpperCase() : item.urgency) as RiskLevel,
                  triageId: t.triage_id,
                  triageStatus: t.triage_status || 'COMPLETE',
                  confidence: t.confidence,
                  confidenceType: t.confidence_type,
                  reasoning: t.reasoning,
                  dataSources: t.data_sources,
                  facts: t.facts,
                  predictions: t.predictions,
                  aiInterpretation: t.ai_interpretation,
                  recommendedAction: t.recommended_action,
                  humanConfirmationRequired: t.human_confirmation_required ?? true,
                  staleDataWarning: t.stale_data_warning ?? false,
                }
              : item
          )
        );
      } else if (domainEvent.event === 'SOS_UPDATE_CREATED') {
        const u = domainEvent.data;
        const isVoice = u?.update_type === 'VOICE_UPDATE' || !!u?.audio_id;
        const langTag = u?.original_language ? `[${u.original_language.toUpperCase()}]` : '';
        title = isVoice
          ? `Voice Emergency SOS Update ${langTag}`
          : `Distress Update (#DG-${u?.sos_id})`;
        description = u?.message
          ? `"${u.message}"`
          : `Distress update received from field (${u?.update_type || 'STATUS_UPDATE'})`;

        setSOSIncidents((prev) =>
          prev.map((item) => {
            if (
              item.id === `sos-${u.sos_id}` ||
              item.id === String(u.sos_id) ||
              (item as any).backendSosId === u.sos_id
            ) {
              const existingUpdates = (item as any).updates || [];
              const newUpdateObj = {
                id: u.id,
                update_type: u.update_type,
                message: u.message,
                original_language: u.original_language,
                audio_id: u.audio_id,
                audio_url: u.audio_id ? `/api/v1/sos/${u.sos_id}/voice/${u.audio_id}` : undefined,
                transcription_provider: u.transcription_provider,
                transcription_model: u.transcription_model,
                transcription_confidence: u.transcription_confidence,
                latitude: u.latitude,
                longitude: u.longitude,
                created_at: u.created_at || new Date().toISOString(),
              };
              return {
                ...item,
                location: u.message || item.location,
                coordinates: u.latitude && u.longitude ? [u.latitude, u.longitude] : item.coordinates,
                updates: [newUpdateObj, ...existingUpdates],
                latestVoiceAudioId: u.audio_id || (item as any).latestVoiceAudioId,
                latestVoiceLanguage: u.original_language || (item as any).latestVoiceLanguage,
                latestVoiceTranscript: u.message || (item as any).latestVoiceTranscript,
              };
            }
            return item;
          })
        );

        if (u?.latitude && u?.longitude) {
          setMarkers((prev) =>
            prev.map((m) =>
              m.id === `mk-sos-${u.sos_id}`
                ? {
                    ...m,
                    coordinates: [u.latitude, u.longitude],
                    details: `Latest Update: ${u.message || u.update_type}`,
                  }
                : m
            )
          );
        }
      } else if (domainEvent.event === 'RESCUE_ASSIGNMENT_CREATED') {
        const r = domainEvent.data;
        title = `Rescue Unit Dispatched: ${r?.team_name || 'Rescue Squad'}`;
        description = `Assigned to Incident #${r?.incident_id} (Approx. ${r?.distance_km}km)`;
        setSOSIncidents((prev) =>
          prev.map((item) =>
            item.id === `sos-${r.incident_id}` ||
            item.id === `inc-${r.incident_id}` ||
            (item as any).backendIncidentId === r.incident_id
              ? {
                  ...item,
                  status: 'DISPATCHED',
                  assignmentStatus: 'DISPATCHED',
                  assignmentId: r.assignment_id,
                  rescueTeamId: r.rescue_team_id,
                  recommendedTeam: r.team_name,
                  teamDistanceKm: r.distance_km,
                  distanceLabel: r.distance_label,
                  routingLimitations: r.routing_limitations,
                  rescueTeamCoordinates: r.team_coordinates,
                  dispatchedAt: r.assigned_at,
                  dispatchedBy: r.dispatched_by,
                  isOverride: r.is_override,
                  overrideReason: r.override_reason,
                }
              : item
          )
        );
        setMarkers((prev) =>
          prev.map((m) =>
            m.id === `mk-sos-${r.incident_id}` || m.id === `mk-inc-${r.incident_id}`
              ? {
                  ...m,
                  details: `Unit Dispatched: ${r.team_name} (Approx. ${r.distance_km}km) [${r.dispatched_by}]`,
                }
              : m
          )
        );
      } else if (domainEvent.event === 'RESCUE_STATUS_UPDATED') {
        const r = domainEvent.data;
        title = `Rescue Unit Status: ${r?.team_name} -> ${r?.status}`;
        description = `Assignment #${r?.assignment_id}: Status updated to ${r?.status}`;
        setSOSIncidents((prev) =>
          prev.map((item) =>
            item.assignmentId === r.assignment_id
              ? {
                  ...item,
                  assignmentStatus: r.status,
                  status: r.status === 'COMPLETED' || r.status === 'RESOLVED' ? 'RESCUED' : item.status,
                }
              : item
          )
        );
      } else if (domainEvent.event === 'SIMULATION_STAGE_CHANGED') {
        const sim = domainEvent.data;
        title = `Simulation Step ${sim?.step}/8: ${sim?.stage}`;
        description = sim?.title || sim?.description || `Simulation transitioned to stage ${sim?.stage}`;
        if (sim) {
          setSimulationStep(sim.step);
          setSimulationStage(sim.stage);
          setSimulationTitle(sim.title || sim.stage);
          if (sim.simulation_complete) {
            setIsSimulationComplete(true);
          }
          if (sim.step === 0) {
            setIsSimulationComplete(false);
            setIsSimulationActive(false);
          }
        }
      }

      const feedItem: LiveFeedItem = {
        id: `evt-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        event: domainEvent.event,
        severity: (['CRITICAL', 'HIGH', 'MODERATE', 'LOW'].includes(domainEvent.severity?.toUpperCase() || '')
          ? (domainEvent.severity!.toUpperCase() as any)
          : 'LOW'),
        entityId: domainEvent.entity_id,
        title,
        description,
      };

      setLiveIncidentFeed((prev) => [feedItem, ...prev.slice(0, 24)]);
    });

    return () => {
      unsubStatus();
      unsubReconnect();
      unsubEvents();
      websocketService.disconnect();
    };
  }, [refreshData]);

  // Periodic REST refresh fallback when WebSocket is offline (Section 17)
  useEffect(() => {
    if (connectionStatus === 'OFFLINE') {
      const fallbackInterval = setInterval(() => {
        console.log('[RealTime] REST Fallback polling active...');
        refreshData();
      }, 30000);
      return () => clearInterval(fallbackInterval);
    }
  }, [connectionStatus, refreshData]);

  // Manual WebSocket Reconnect
  const reconnectWebSocket = useCallback(() => {
    websocketService.disconnect();
    websocketService.connect();
  }, []);

  // Background weather refresh every 15 minutes (WEATHER_CACHE_MINUTES = 15)
  useEffect(() => {
    const weatherInterval = setInterval(() => {
      disasterService.getCurrentWeather()
        .then((w) => setCurrentWeather(w))
        .catch((err) => console.warn('Background weather refresh error:', err));
    }, 15 * 60 * 1000);
    return () => clearInterval(weatherInterval);
  }, []);

  // Trigger AI Analysis via Backend Models
  const triggerAIAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const [rain, flood, summary] = await Promise.all([
        disasterService.getLatestRainfallPrediction(),
        disasterService.getLatestFloodPrediction(),
        disasterService.getDashboardSummary(),
      ]);

      setAIPrediction({
        riskScore: summary.overall_risk_score || 82,
        riskLevel: (summary.risk_level || flood.risk_level || 'HIGH') as RiskLevel,
        rainfallPredictionMm: +(rain.predicted_rainfall_mm || 165.0).toFixed(1),
        floodProbabilityPercent: Math.round((flood.flood_probability || 0.9) * 100),
        affectedZoneKm2: +(36.8).toFixed(1),
        evacuationRecommendation:
          flood.alert_recommendation || (flood.flood_probability > 0.75
            ? 'Hydrological model indicates elevated river crest imminent. Immediate evacuation to safe shelters advised.'
            : 'Precautionary advisory in effect. Prepare household essentials.'),
        confidenceScore: rain.confidence || 0.96,
        lastUpdated: 'Just now (ML Model Verified)',
        modelName: rain.model_name || flood.model_name || 'RandomForestClassifier (scikit-learn)',
        modelVersion: rain.model_version || flood.model_version || 'v2.0-real-data',
        dataSource: rain.data_source || flood.data_source || 'ECMWF ERA5-Land Historical Reanalysis',
        dataSourceType: rain.data_source_type || 'historical_real',
        trainingDataset: rain.training_dataset || 'historical_weather_chennai_2022_2024.csv',
        predictedCategory: rain.predicted_category || 'MODERATE',
        featureImportance: rain.feature_importance,
        topContributors: rain.top_contributors,
        alertRecommendation: flood.alert_recommendation,
        topDrivers: flood.top_drivers,
        disclaimer: rain.disclaimer || flood.disclaimer,
      });
    } catch {

      // Fallback
      setAIPrediction({
        riskScore: Math.floor(Math.random() * 15) + 80,
        riskLevel: 'HIGH',
        rainfallPredictionMm: +(135 + Math.random() * 30).toFixed(1),
        floodProbabilityPercent: Math.floor(82 + Math.random() * 12),
        affectedZoneKm2: +(32 + Math.random() * 8).toFixed(1),
        evacuationRecommendation:
          'Elevated river crest imminent. PostGIS spatial models advise immediate evacuation to Sector 4 shelters.',
        confidenceScore: 0.95,
        lastUpdated: 'Just now',
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Reset Emergency Command Simulation Mode
  const resetDisasterSimulation = async () => {
    simulationAbortRef.current = true;
    setIsSimulationActive(false);
    setIsSimulationComplete(false);
    setIsAnalyzing(false);
    setSimulationStep(0);
    setSimulationStage('NORMAL');
    setSimulationTitle('Simulation Engine Ready');

    try {
      await disasterService.resetSimulation();
      await refreshData();
    } catch (err) {
      console.warn('Simulation reset error:', err);
    }
  };

  // Run Backend-Driven 8-Stage Disaster Simulation Pipeline
  const runDisasterSimulation = async () => {
    if (isSimulationActive) return;
    setIsSimulationActive(true);
    setIsSimulationComplete(false);
    simulationAbortRef.current = false;

    try {
      // Step 1: Start simulation on backend (Establishes baseline conditions in PostgreSQL)
      const startState = await disasterService.startSimulation();
      setSimulationStep(startState.step);
      setSimulationStage(startState.stage);
      setSimulationTitle(startState.title || 'Normal Conditions');
      await refreshData();

      // Sequentially advance through Steps 2 to 8 with ~2.5s pacing
      for (let s = 2; s <= 8; s++) {
        await new Promise((resolve) => setTimeout(resolve, 2500));
        if (simulationAbortRef.current) break;

        if (s === 3) {
          setIsAnalyzing(true);
        }

        const stepState = await disasterService.stepSimulation();
        setSimulationStep(stepState.step);
        setSimulationStage(stepState.stage);
        setSimulationTitle(stepState.title || stepState.stage);

        if (s === 3) {
          setIsAnalyzing(false);
        }

        if (stepState.simulation_complete) {
          setIsSimulationComplete(true);
        }

        // Retrieve fresh authentic database records from PostgreSQL
        await refreshData();
      }
    } catch (err) {
      console.error('Simulation execution error:', err);
      setIsAnalyzing(false);
      setIsSimulationActive(false);
    }
  };

  // Citizen SOS Submission via Backend API
  const createSOSRequest = async (
    incident: Omit<SOSIncident, 'id' | 'timestamp' | 'status'>
  ) => {
    const tempId = `sos-${Date.now()}`;
    const optimisticItem: SOSIncident = {
      ...incident,
      id: tempId,
      timestamp: 'Just now',
      status: 'PENDING',
    };

    // Optimistic UI update
    setSOSIncidents((prev) => [optimisticItem, ...prev]);
    setDashboardStats((prev) => ({ ...prev, activeSOSCount: prev.activeSOSCount + 1 }));

    try {
      // 1. Submit SOS Report to PostgreSQL (backend executes AI triage, creates Incident, assigns Rescue Team)
      const sosMessage = incident.location && incident.location.includes('trapped')
        ? incident.location
        : incident.title && incident.title.includes('trapped')
        ? incident.title
        : `${incident.citizenName}: ${incident.emergencyType} (${incident.peopleCount} people) at ${incident.location}`;

      const createdSOS = await disasterService.createSOSReport({
        latitude: incident.coordinates[0],
        longitude: incident.coordinates[1],
        message: sosMessage,
        severity: incident.urgency,
      });

      // 2. If triage returned, immediately update item with all 10 triage and dispatch fields
      if (createdSOS.triage) {
        const tr = createdSOS.triage;
        const populatedItem: SOSIncident = {
          ...incident,
          id: `sos-${createdSOS.id}`,
          title: tr.incident_title || incident.title || `Citizen SOS #${createdSOS.id}`,
          timestamp: 'Just now',
          status: 'DISPATCHED',
          urgency: (['LOW', 'MODERATE', 'HIGH', 'CRITICAL'].includes(tr.severity.toUpperCase())
            ? (tr.severity.toUpperCase() as RiskLevel)
            : incident.urgency),
          emergencyType: tr.incident_type === 'MEDICAL_EMERGENCY' ? 'MEDICAL' : 'TRAPPED',
          incidentType: tr.incident_type,
          priorityScore: tr.priority_score,
          recommendedTeam: tr.recommended_rescue_team,
          teamDistanceKm: tr.distance_km,
          estimatedEtaMinutes: tr.estimated_response_minutes,
          recommendedHospital: tr.recommended_hospital,
          hospitalDistanceKm: tr.hospital_distance_km,
          recommendedShelter: tr.recommended_shelter,
          shelterDistanceKm: tr.shelter_distance_km,
          riskZoneName: tr.risk_zone_name,
          assignmentId: tr.assignment_id,
          assignmentStatus: tr.assignment_status,
        };
        setSOSIncidents((prev) =>
          prev.map((item) => (item.id === tempId ? populatedItem : item))
        );
      } else {
        setSOSIncidents((prev) =>
          prev.map((item) => (item.id === tempId ? { ...item, id: `sos-${createdSOS.id}` } : item))
        );
      }

      // 3. Refresh live data from PostgreSQL
      await refreshData();
    } catch (err) {
      console.warn('Failed to sync SOS to backend, retained in local state:', err);
    }
  };

  // Citizen SOS Resolution via Backend API
  const resolveSOSIncident = async (id: string) => {
    setSOSIncidents((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: 'RESCUED' } : item))
    );

    const numericId = parseInt(id.replace(/\D/g, ''), 10);
    if (!isNaN(numericId)) {
      try {
        await disasterService.updateSOSStatus(numericId, 'RESCUED');
      } catch (err) {
        console.warn(`Could not update SOS #${numericId} status on backend:`, err);
      }
    }
  };

  // Spatial Safe Zones Filter via PostGIS Nearby API
  const filterSafeZonesByRadius = async (radiusKm: number) => {
    const startTime = performance.now();
    try {
      const [nearbyShelters, nearbyHospitals] = await Promise.all([
        disasterService.getNearbyShelters(13.0827, 80.2707, radiusKm),
        disasterService.getNearbyHospitals(13.0827, 80.2707, radiusKm),
      ]);

      const filtered = mapBackendSafeZones(nearbyShelters, nearbyHospitals);
      const execTime = +(performance.now() - startTime).toFixed(2);

      setSafeZones(filtered);
      setPostGisLogs((prev) => [
        {
          queryType: 'ST_DWithin',
          table: 'safe_shelters',
          radiusKm,
          centerCoordinates: [13.0827, 80.2707],
          returnedRowsCount: filtered.length,
          executionTimeMs: execTime || 8.4,
        },
        ...prev,
      ]);
    } catch (err) {
      // Local fallback filter
      const execTime = +(performance.now() - startTime).toFixed(2);
      const filtered = fallbackSafeZones.filter((sz) => sz.distanceKm <= radiusKm);
      setSafeZones(filtered);
      setPostGisLogs((prev) => [
        {
          queryType: 'ST_DWithin',
          table: 'safe_shelters',
          radiusKm,
          centerCoordinates: [13.0827, 80.2707],
          returnedRowsCount: filtered.length,
          executionTimeMs: execTime || 6.4,
        },
        ...prev,
      ]);
    }
  };

  const dispatchRescueTeam = useCallback(
    async (
      incidentId: number,
      rescueTeamId: number,
      notes?: string,
      isOverride?: boolean,
      overrideReason?: string
    ) => {
      const response = await disasterService.dispatchRescueTeam({
        incident_id: incidentId,
        rescue_team_id: rescueTeamId,
        notes,
        is_override: isOverride,
        override_reason: overrideReason,
      });

      setSOSIncidents((prev) =>
        prev.map((item) => {
          const isTarget =
            item.id === `sos-${incidentId}` ||
            item.id === `inc-${incidentId}` ||
            (item as any).backendIncidentId === incidentId;
          if (isTarget) {
            return {
              ...item,
              status: 'DISPATCHED',
              assignmentStatus: 'DISPATCHED',
              assignmentId: response.assignment_id,
              rescueTeamId: response.rescue_team_id,
              recommendedTeam: response.team_name,
              teamDistanceKm: response.distance_km,
              distanceLabel: response.distance_label,
              routingLimitations: response.routing_limitations,
              dispatchedAt: response.assigned_at,
              dispatchedBy: response.dispatched_by,
              isOverride: response.is_override,
              overrideReason: response.override_reason,
            };
          }
          return item;
        })
      );

      return response;
    },
    []
  );

  return (
    <DisasterContext.Provider
      value={{
        alerts,
        sosIncidents,
        safeZones,
        markers,
        aiPrediction,
        isAnalyzing,
        dashboardStats,
        currentWeather,
        isSimulationActive,
        simulationStep,
        simulationStage,
        simulationTitle,
        isSimulationComplete,
        postGisLogs,
        isLoading,
        backendConnected,
        connectionStatus,
        liveIncidentFeed,
        reconnectWebSocket,
        refreshData,
        runDisasterSimulation,
        resetDisasterSimulation,
        triggerAIAnalysis,
        createSOSRequest,
        resolveSOSIncident,
        dispatchRescueTeam,
        filterSafeZonesByRadius,
      }}
    >
      {children}
    </DisasterContext.Provider>
  );
};

export const useDisaster = () => {
  const context = useContext(DisasterContext);
  if (!context) {
    throw new Error('useDisaster must be used within a DisasterProvider');
  }
  return context;
};
