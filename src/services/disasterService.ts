/**
 * DisasterGuard Central API Service Layer
 * Connects Frontend React Client to FastAPI Backend & PostgreSQL + PostGIS Endpoints.
 * Includes timeout handling, automatic retries, and offline data fallbacks.
 */

const getApiBase = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return `${envUrl.replace(/\/$/, '')}/api/v1`;
  }
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'https://ai-disasterguard-backend.onrender.com/api/v1';
  }
  return '/api/v1';
};

export const API_BASE = getApiBase();

/**
 * Fetch wrapper with configurable timeout and retry logic
 */
async function fetchWithRetry<T>(
  url: string,
  options: RequestInit = {},
  retries = 2,
  delayMs = 600,
  timeoutMs = 6000
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...options.headers,
      },
    });
    clearTimeout(timer);

    if (!response.ok) {
      let errDetail = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData?.error?.message) {
          errDetail = errorData.error.message;
        } else if (errorData?.detail) {
          errDetail = errorData.detail;
        }
      } catch (_) {}
      throw new Error(errDetail);
    }

    return await response.json();
  } catch (error: any) {
    clearTimeout(timer);
    if (retries > 0 && options.method !== 'POST') {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
      return fetchWithRetry<T>(url, options, retries - 1, delayMs * 1.5, timeoutMs);
    }
    throw error;
  }
}

// --------------------------------------------------------------------------
// Backend Data Types (Raw API Responses)
// --------------------------------------------------------------------------

export interface BackendDashboardSummary {
  overall_risk_score: number;
  risk_level: string;
  active_alerts: number;
  active_incidents: number;
  active_sos: number;
  affected_population: number;
  rescue_teams_available: number;
  shelters_available: number;
}

export interface BackendAlert {
  id: number;
  title: string;
  message: string;
  alert_type: string;
  severity: string;
  target_area: string;
  issued_at: string;
  expires_at?: string;
  status: string;
}

export interface BackendIncident {
  id: number;
  title: string;
  description?: string;
  incident_type: string;
  latitude: number;
  longitude: number;
  severity: string;
  status: string;
  source: string;
  priority_score: number;
  sos_id?: number;
  created_at: string;
  updated_at?: string;
}

export interface SOSTriageDetail {
  incident_id: number;
  incident_title: string;
  incident_type: string;
  severity: string;
  priority_score: number;
  classification_method: string;
  risk_zone_name?: string;
  risk_zone_level?: string;
  recommended_rescue_team: string;
  rescue_team_id: number;
  distance_km: number;
  estimated_response_minutes: number;
  recommended_hospital: string;
  hospital_distance_km: number;
  recommended_shelter: string;
  shelter_distance_km: number;
  assignment_id: number;
  assignment_status: string;
  // Phase 3 Part 2 Rich AI Triage Fields
  confidence?: number;
  confidence_type?: string;
  reasoning?: string[];
  data_sources?: string[];
  facts?: string[];
  predictions?: string[];
  ai_interpretation?: string;
  recommended_action?: string;
  human_confirmation_required?: boolean;
  stale_data_warning?: string;
}

export interface BackendSOSReport {
  id: number;
  user_id?: number;
  latitude: number;
  longitude: number;
  message?: string;
  severity: string;
  status: string;
  created_at: string;
  resolved_at?: string;
  triage?: SOSTriageDetail;
}

export interface BackendRescueAssignment {
  id: number;
  incident_id: number;
  rescue_team_id: number;
  team_name?: string;
  incident_title?: string;
  incident_type?: string;
  severity?: string;
  priority?: number;
  priority_score?: number;
  estimated_distance?: number;
  eta_minutes?: number;
  recommended_hospital?: string;
  recommended_shelter?: string;
  risk_zone_name?: string;
  status: string;
  assigned_at?: string;
  completed_at?: string;
  notes?: string;
}

export interface BackendShelter {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  capacity: number;
  current_occupancy: number;
  contact?: string;
  status: string;
  distance_km?: number;
  available_capacity?: number;
}

export interface BackendHospital {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  emergency_capacity: number;
  available_beds: number;
  contact?: string;
  status: string;
  distance_km?: number;
}

export interface BackendRescueTeam {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  team_size: number;
  vehicle_type: string;
  equipment?: string;
  status: string;
  contact?: string;
  capabilities?: string[];
  capacity?: number;
  last_updated?: string;
}

export interface BackendRescueCandidate {
  team_id: number;
  team_name: string;
  callsign: string;
  status: string;
  current_latitude: number;
  current_longitude: number;
  capabilities: string[];
  capacity: number;
  distance_km: number;
  distance_label: string;
  routing_limitations: string;
  score: number;
  rank: number;
  reasons: string[];
  is_stale_location: boolean;
  last_updated?: string;
}

export interface BackendRescueRecommendation {
  incident_id: number;
  incident_type: string;
  urgency: string;
  primary_recommendation: BackendRescueCandidate | null;
  candidates: BackendRescueCandidate[];
  is_no_team_available: boolean;
  generated_at: string;
}

export interface BackendRescueDispatchPayload {
  incident_id: number;
  rescue_team_id: number;
  notes?: string;
  is_override?: boolean;
  override_reason?: string;
}

export interface BackendRescueDispatchResponse {
  assignment_id: number;
  incident_id: number;
  rescue_team_id: number;
  team_name: string;
  callsign: string;
  status: string;
  assigned_at: string;
  dispatched_by: string;
  is_override: boolean;
  override_reason?: string;
  distance_km: number;
  distance_label: string;
  routing_limitations: string;
}

export interface BackendRescueDispatchAudit {
  id: number;
  incident_id: number;
  rescue_team_id: number;
  operator_id?: number;
  operator_name: string;
  action: string;
  is_override: boolean;
  override_reason?: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface BackendWeatherObservation {
  id: number;
  location: string;
  rainfall_1h: number;
  rainfall_3h: number;
  rainfall_6h: number;
  rainfall_24h: number;
  temperature: number;
  humidity: number;
  wind_speed: number;
  pressure: number;
  observed_at: string;
  latitude?: number;
  longitude?: number;
  condition?: string;
  source?: 'real' | 'cached' | 'mock' | 'simulation' | string;
  precipitation_probability?: number;
  is_demo?: boolean;
}

export interface TopContributor {
  feature: string;
  importance_pct: number;
  observed_value: number;
}

export interface RiskBreakdown {
  rainfall_weight_pct: number;
  rainfall_score: number;
  flood_weight_pct: number;
  flood_score: number;
  exposure_weight_pct: number;
  exposure_score: number;
}

export interface BackendRainfallPrediction {
  location?: string;
  predicted_rainfall_mm: number;
  confidence: number;
  risk_level: string;
  forecast_horizon_hours: number;
  prediction_time: string;
  model_mode?: string;
  model_name?: string;
  model_version?: string;
  training_dataset?: string;
  data_source_type?: string;
  data_source?: string;
  predicted_category?: string;
  class_probabilities?: Record<string, number>;
  feature_importance?: Record<string, number>;
  top_contributors?: TopContributor[];
  weather_source?: string;
  disclaimer?: string;
}

export interface BackendFloodPrediction {
  location?: string;
  flood_probability: number;
  estimated_water_depth_m: number;
  risk_level: string;
  confidence?: number;
  model_mode?: string;
  model_name?: string;
  model_version?: string;
  training_dataset?: string;
  data_source_type?: string;
  data_source?: string;
  prediction_time: string;
  class_probabilities?: Record<string, number>;
  feature_importance?: Record<string, number>;
  weather_source?: string;
  risk_breakdown?: RiskBreakdown;
  alert_recommendation?: string;
  top_drivers?: string[];
  disclaimer?: string;
  evacuation_advised?: boolean;
}


export interface BackendRiskZone {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  risk_level: string;
  risk_score: number;
  population_estimate: number;
  updated_at: string;
}

export interface BackendSimulationState {
  is_active: boolean;
  step: number;
  total_steps: number;
  stage: string;
  title?: string;
  description?: string;
  risk_score: number;
  risk_level: string;
  rainfall_mm: number;
  flood_prob: number;
  active_alerts: number;
  active_sos: number;
  active_incidents: number;
  recommended_rescue_team: number;
  metrics?: Record<string, any>;
  database_changes?: Record<string, any>;
  simulation_active?: boolean;
  simulation_complete?: boolean;
}

// --------------------------------------------------------------------------
// API Client Methods
// --------------------------------------------------------------------------

export const disasterService = {
  // Health / Status
  checkBackendHealth: async (): Promise<boolean> => {
    try {
      const res = await fetch(`${API_BASE.replace('/api/v1', '')}/health`, {
        signal: AbortSignal.timeout(3000),
      });
      return res.ok;
    } catch {
      return false;
    }
  },

  // Dashboard Summary
  getDashboardSummary: async (): Promise<BackendDashboardSummary> => {
    return fetchWithRetry<BackendDashboardSummary>(`${API_BASE}/dashboard/summary`);
  },

  // Alerts
  getActiveAlerts: async (): Promise<BackendAlert[]> => {
    return fetchWithRetry<BackendAlert[]>(`${API_BASE}/alerts/`);
  },

  createAlert: async (data: {
    title: string;
    message: string;
    alert_type?: string;
    severity?: string;
    target_area: string;
  }): Promise<BackendAlert> => {
    return fetchWithRetry<BackendAlert>(`${API_BASE}/alerts/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Incidents
  getIncidents: async (prioritized = true): Promise<BackendIncident[]> => {
    const url = prioritized
      ? `${API_BASE}/incidents/prioritized`
      : `${API_BASE}/incidents/`;
    return fetchWithRetry<BackendIncident[]>(url);
  },

  createIncident: async (data: {
    title: string;
    description?: string;
    incident_type?: string;
    latitude: number;
    longitude: number;
    severity?: string;
    source?: string;
  }): Promise<BackendIncident> => {
    return fetchWithRetry<BackendIncident>(`${API_BASE}/incidents/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // SOS Reports
  getActiveSOSReports: async (): Promise<BackendSOSReport[]> => {
    return fetchWithRetry<BackendSOSReport[]>(`${API_BASE}/sos/active`);
  },

  createSOSReport: async (data: {
    latitude: number;
    longitude: number;
    message?: string;
    severity?: string;
  }): Promise<BackendSOSReport> => {
    return fetchWithRetry<BackendSOSReport>(`${API_BASE}/sos/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  updateSOSStatus: async (
    sosId: number,
    status: 'PENDING' | 'DISPATCHED' | 'RESCUED'
  ): Promise<BackendSOSReport> => {
    return fetchWithRetry<BackendSOSReport>(`${API_BASE}/sos/${sosId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },

  // Shelters
  getAllShelters: async (): Promise<BackendShelter[]> => {
    return fetchWithRetry<BackendShelter[]>(`${API_BASE}/shelters/`);
  },

  getNearbyShelters: async (
    lat = 13.0827,
    lng = 80.2707,
    radiusKm = 10.0
  ): Promise<BackendShelter[]> => {
    return fetchWithRetry<BackendShelter[]>(
      `${API_BASE}/shelters/nearby?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`
    );
  },

  // Hospitals
  getAllHospitals: async (): Promise<BackendHospital[]> => {
    return fetchWithRetry<BackendHospital[]>(`${API_BASE}/hospitals/`);
  },

  getNearbyHospitals: async (
    lat = 13.0827,
    lng = 80.2707,
    radiusKm = 10.0
  ): Promise<BackendHospital[]> => {
    return fetchWithRetry<BackendHospital[]>(
      `${API_BASE}/hospitals/nearby?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`
    );
  },

  // Rescue Teams & Assignments
  getRescueTeams: async (): Promise<BackendRescueTeam[]> => {
    return fetchWithRetry<BackendRescueTeam[]>(`${API_BASE}/rescue/teams`);
  },

  getRescueAssignments: async (): Promise<BackendRescueAssignment[]> => {
    return fetchWithRetry<BackendRescueAssignment[]>(`${API_BASE}/rescue/assignments`);
  },

  getRescueRecommendation: async (incidentId: number): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/rescue/recommend/${incidentId}`);
  },

  getRescueRecommendations: async (incidentId: number): Promise<BackendRescueRecommendation> => {
    return fetchWithRetry<BackendRescueRecommendation>(
      `${API_BASE}/rescue/recommendations/${incidentId}`
    );
  },

  dispatchRescueTeam: async (
    payload: BackendRescueDispatchPayload,
    token: string = 'demo-operator-token',
    userRole: string = 'OPERATOR'
  ): Promise<BackendRescueDispatchResponse> => {
    return fetchWithRetry<BackendRescueDispatchResponse>(
      `${API_BASE}/rescue/assignments/dispatch`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'X-User-Role': userRole,
        },
        body: JSON.stringify(payload),
      }
    );
  },

  getRescueAuditLogs: async (limit = 50): Promise<BackendRescueDispatchAudit[]> => {
    return fetchWithRetry<BackendRescueDispatchAudit[]>(
      `${API_BASE}/rescue/audit?limit=${limit}`
    );
  },

  // Weather & Predictions
  getCurrentWeather: async (lat?: number, lng?: number): Promise<BackendWeatherObservation> => {
    const query = lat !== undefined && lng !== undefined ? `?latitude=${lat}&longitude=${lng}` : '';
    return fetchWithRetry<BackendWeatherObservation>(`${API_BASE}/weather/current${query}`);
  },

  getWeatherHistory: async (limit = 10, hours = 24): Promise<BackendWeatherObservation[]> => {
    return fetchWithRetry<BackendWeatherObservation[]>(
      `${API_BASE}/weather/history?limit=${limit}&hours=${hours}`
    );
  },

  getLatestRainfallPrediction: async (): Promise<BackendRainfallPrediction> => {
    return fetchWithRetry<BackendRainfallPrediction>(`${API_BASE}/predictions/rainfall/latest`);
  },

  getLatestFloodPrediction: async (): Promise<BackendFloodPrediction> => {
    return fetchWithRetry<BackendFloodPrediction>(`${API_BASE}/predictions/flood/latest`);
  },

  getModelMetrics: async (): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/predictions/models/metrics`);
  },

  getMLModels: async (): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/ml/models`);
  },

  getActiveMLModels: async (): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/ml/models/active`);
  },

  getMLProvenance: async (): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/ml/provenance`);
  },

  getMLExplanation: async (): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/ml/explanation`);
  },

  getRiskZones: async (): Promise<BackendRiskZone[]> => {
    return fetchWithRetry<BackendRiskZone[]>(`${API_BASE}/risk/zones`);
  },

  getMapRiskZonesGeoJSON: async (): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/map/risk-zones`);
  },

  // Simulation Controls
  startSimulation: async (): Promise<BackendSimulationState> => {
    return fetchWithRetry<BackendSimulationState>(`${API_BASE}/simulation/start`, {
      method: 'POST',
    });
  },

  stepSimulation: async (): Promise<BackendSimulationState> => {
    return fetchWithRetry<BackendSimulationState>(`${API_BASE}/simulation/step`, {
      method: 'POST',
    });
  },

  resetSimulation: async (): Promise<BackendSimulationState> => {
    return fetchWithRetry<BackendSimulationState>(`${API_BASE}/simulation/reset`, {
      method: 'POST',
    });
  },

  getSimulationStatus: async (): Promise<BackendSimulationState> => {
    return fetchWithRetry<BackendSimulationState>(`${API_BASE}/simulation/status`);
  },

  // Phase 5.2 Advanced Flood Intelligence & Geospatial APIs
  getFloodIntelligence: async (lat: number = 13.0827, lng: number = 80.2707): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/flood/intelligence?latitude=${lat}&longitude=${lng}`);
  },

  getHistoricalFloodEvents: async (lat?: number, lng?: number, radiusKm: number = 15): Promise<any[]> => {
    const url = (lat !== undefined && lng !== undefined)
      ? `${API_BASE}/flood/historical-events?latitude=${lat}&longitude=${lng}&radius_km=${radiusKm}`
      : `${API_BASE}/flood/historical-events`;
    return fetchWithRetry<any[]>(url);
  },

  getInundationZones: async (lat: number = 13.0827, lng: number = 80.2707): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/flood/inundation?latitude=${lat}&longitude=${lng}`);
  },

  getSpatialFeatures: async (lat: number, lng: number): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/flood/spatial-features?latitude=${lat}&longitude=${lng}`);
  },

  getSpatialRiskZonesGeoJSON: async (): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/flood/zones`);
  },

  // Phase 5.3 Multi-Horizon Risk Forecasting & Early Warning APIs
  getMultiHorizonForecast: async (lat: number = 13.0827, lng: number = 80.2707, refresh: boolean = false): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/forecast/current?latitude=${lat}&longitude=${lng}&refresh=${refresh}`);
  },

  getForecastHorizons: async (lat: number = 13.0827, lng: number = 80.2707): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/forecast/horizons?latitude=${lat}&longitude=${lng}`);
  },

  getForecastHorizonDetail: async (horizon: string, lat: number = 13.0827, lng: number = 80.2707): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/forecast/${horizon}?latitude=${lat}&longitude=${lng}`);
  },

  getRiskTrajectory: async (lat: number = 13.0827, lng: number = 80.2707): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/forecast/meta/trajectory?latitude=${lat}&longitude=${lng}`);
  },

  getForecastUncertainty: async (lat: number = 13.0827, lng: number = 80.2707): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/forecast/meta/uncertainty?latitude=${lat}&longitude=${lng}`);
  },

  getForecastExplanation: async (lat: number = 13.0827, lng: number = 80.2707): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/forecast/meta/explanation?latitude=${lat}&longitude=${lng}`);
  },

  // Phase 5.4: Adaptive Alert Intelligence & Operator Approval APIs
  getActiveApprovedAlerts: async (): Promise<any[]> => {
    return fetchWithRetry<any[]>(`${API_BASE}/alerts/active`);
  },

  getAlertRecommendations: async (): Promise<any[]> => {
    return fetchWithRetry<any[]>(`${API_BASE}/alerts/recommendations`, {
      headers: { 'x-user-role': 'OPERATOR' }
    });
  },

  getAlertAnalytics: async (): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/alerts/analytics`);
  },

  getAlertDetail: async (alertId: number): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/alerts/${alertId}`);
  },

  approveAlert: async (alertId: number, operatorName: string = 'Authorized Operator', editedMessage?: string): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/alerts/${alertId}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-user-role': 'OPERATOR'
      },
      body: JSON.stringify({
        operator_name: operatorName,
        edited_message: editedMessage
      })
    });
  },

  rejectAlert: async (alertId: number, operatorName: string = 'Authorized Operator', notes?: string): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/alerts/${alertId}/reject`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-user-role': 'OPERATOR'
      },
      body: JSON.stringify({
        operator_name: operatorName,
        notes: notes
      })
    });
  },

  acknowledgeAlert: async (alertId: number, clientId?: string, channel: string = 'IN_APP'): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        client_id: clientId,
        channel: channel
      })
    });
  },

  triggerAlertRecommendation: async (lat: number = 13.0827, lng: number = 80.2707, location: string = 'Central Metro Sector', radiusKm: number = 5.0, lang: string = 'en'): Promise<any> => {
    return fetchWithRetry<any>(`${API_BASE}/alerts/recommend?lat=${lat}&lon=${lng}&location=${encodeURIComponent(location)}&radius_km=${radiusKm}&lang=${lang}`, {
      method: 'POST'
    });
  }
};
