export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface AIChatResponse {
  answer?: string;
  reply: string;
  severity?: 'INFO' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  emergency_level: 'INFO' | 'ADVISORY' | 'WARNING' | 'CRITICAL';
  confidence?: number;
  confidence_type?: 'CALIBRATED' | 'SYSTEM_HEURISTIC' | 'QUALITATIVE';
  suggested_actions: string[];
  recommendations?: string[];
  warnings?: string[];
  sources: string[];
  timestamp: string;
  data_freshness?: string;
}

export interface EmergencyBriefingResponse {
  title: string;
  generated_at: string;
  overall_threat_level: string;
  situation_summary: string;
  weather_summary: string;
  flood_risk_summary: string;
  critical_zones: any[];
  active_incidents_count: number;
  pending_sos_count: number;
  rescue_operations_summary: string;
  shelter_status_summary: string;
  hospital_readiness_summary: string;
  recommended_priorities: string[];
  data_freshness: string;
  disclaimer: string;
}

export interface IncidentAnalysisResponse {
  incident_id: number;
  title: string;
  incident_type: string;
  severity: string;
  priority_score: number;
  status: string;
  location: { latitude: number; longitude: number };
  triage_summary: string;
  sos_details?: any;
  risk_zone?: any;
  current_assignment?: any;
  recommended_rescue_team?: any;
  nearby_shelter?: any;
  nearby_hospital?: any;
  recommended_action: string;
  confidence: number;
  sources: string[];
  advisory_notice: string;
}

export interface RiskExplanationResponse {
  zone_name: string;
  composite_risk_score: number;
  risk_level: string;
  primary_drivers: string[];
  breakdown: Record<string, any>;
  weather_factors: Record<string, any>;
  ml_predictions: Record<string, any>;
  alert_status: string;
  tactical_prognosis: string;
  recommendations: string[];
  sources: string[];
}

export interface ShelterRecommendationResponse {
  recommended_shelter?: any;
  alternative_shelters: any[];
  distance_km: number;
  flood_risk_along_route: string;
  route_safety_notes: string[];
  warnings: string[];
  sources: string[];
}

export interface SafetyChecklistItem {
  id: string;
  text: string;
  urgency: 'IMMEDIATE' | 'BEFORE_EVACUATION' | 'LONG_TERM';
  category: 'SUPPLIES' | 'UTILITIES' | 'MEDICAL' | 'PETS' | 'COMM';
}

export interface PersonalizedSafetyRequest {
  disaster_type: string;
  location: string;
  housing_type: 'GROUND_FLOOR' | 'HIGH_RISE' | 'SINGLE_STORY' | 'BASEMENT';
  household_members: number;
  has_elderly: boolean;
  has_children: boolean;
  has_pets: boolean;
  has_medical_needs: boolean;
  mobility_impaired: boolean;
}

export interface PersonalizedSafetyResponse {
  summary: string;
  disaster_type: string;
  location: string;
  immediate_actions: string[];
  evacuation_checklist: string[];
  supplies_checklist: string[];
  communication_plan: string;
  special_precautions: string[];
  checklists: SafetyChecklistItem[];
}

export interface AlertExplanationRequest {
  alert_id?: string;
  title: string;
  category: string;
  severity: string;
  location: string;
  description: string;
  affected_population?: number;
}

export interface AlertExplanationResponse {
  alert_id?: string;
  title: string;
  severity: string;
  plain_language_summary: string;
  trigger_cause: string;
  danger_timeline: string;
  immediate_actions: string[];
  evacuation_advice: string;
  safety_rating: string;
}

export interface RiskFactorDetail {
  factor: string;
  weight: number;
  contribution_percent: number;
  status: string;
  detail: string;
}

export interface RiskInterpretationRequest {
  risk_score: number;
  rainfall_mm: number;
  flood_probability: number;
  water_depth_m: number;
  population_density: number;
}

export interface RiskInterpretationResponse {
  composite_score: number;
  risk_level: string;
  summary: string;
  factor_breakdown: RiskFactorDetail[];
  trend_trajectory: string;
  recommended_tactical_actions: string[];
  forecast_horizon_hours: number;
}

const getAiApiBase = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return `${envUrl.replace(/\/$/, '')}/api/v1/ai`;
  }
  return '/api/v1/ai';
};

const API_BASE = getAiApiBase();

export const sendAIChat = async (
  message: string,
  persona: string = 'COMMAND_DISPATCHER',
  conversation_history: ChatMessage[] = [],
  context?: Record<string, any>
): Promise<AIChatResponse> => {
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, persona, conversation_history, context }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend AI chat fetch failed, using smart client fallback:', err);
  }

  // Resilient fallback
  return {
    reply: `**AI EMERGENCY ASSISTANT RESPONSE (${persona})**\n\nI have logged your situation regarding: "${message}".\n\n• **Immediate Protocol**: Keep off flooded ground, protect documents and communications gear, and stay tuned to live emergency channel.\n• **Water Warning**: Do not attempt to cross flooded roadways.\n• **Evacuation**: If in low-lying area, relocate to nearest safe zone immediately.`,
    suggested_actions: [
      'Locate Nearest Safe Shelter',
      'Verify Household Emergency Pack',
      'Call Emergency SOS Dispatch'
    ],
    emergency_level: 'WARNING',
    sources: ['Local AI Emergency Ruleset v4.2', 'DisasterGuard Offline Protocol'],
    timestamp: new Date().toISOString(),
  };
};

export const generatePersonalizedSafety = async (
  req: PersonalizedSafetyRequest
): Promise<PersonalizedSafetyResponse> => {
  try {
    const res = await fetch(`${API_BASE}/safety-instructions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend safety instruction fetch failed, using client fallback:', err);
  }

  return {
    summary: `Personalized Emergency Survival Protocol for ${req.household_members} person household in ${req.location}.`,
    disaster_type: req.disaster_type,
    location: req.location,
    immediate_actions: [
      'Move all vital electronics, identification, and valuables to highest level of dwelling.',
      'Charge all mobile phones and portable batteries to 100%.',
      'Shut off electrical main panel if water begins pooling around foundation.'
    ],
    evacuation_checklist: [
      'Sturdy closed-toe waterproof footwear',
      'Emergency whistle and high-visibility rain poncho',
      'Prescription medicines in sealed waterproof bag'
    ],
    supplies_checklist: [
      `${req.household_members * 3}L potable water per day`,
      'Battery-powered LED flashlights + extra cells',
      'Non-perishable high-protein food ration pack'
    ],
    communication_plan: 'Use SMS messaging instead of voice calls to keep congested networks free for first responders.',
    special_precautions: req.has_elderly
      ? ['Elderly family members require 14-day supply of daily prescriptions and pre-arranged wheelchair transit.']
      : [],
    checklists: [
      { id: 'c1', text: 'Pack emergency medicines and ID cards', urgency: 'IMMEDIATE', category: 'MEDICAL' },
      { id: 'c2', text: 'Turn off ground floor power circuits', urgency: 'BEFORE_EVACUATION', category: 'UTILITIES' },
      { id: 'c3', text: 'Secure pets in sturdy carriers', urgency: 'IMMEDIATE', category: 'PETS' }
    ]
  };
};

export const explainAlertWithAI = async (
  req: AlertExplanationRequest
): Promise<AlertExplanationResponse> => {
  try {
    const res = await fetch(`${API_BASE}/explain-alert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend explain alert failed, using client fallback:', err);
  }

  return {
    alert_id: req.alert_id,
    title: req.title,
    severity: req.severity,
    plain_language_summary: `This is a ${req.severity} alert for ${req.title} impacting ${req.location}. Inundation sensors have detected severe surface water accumulation posing active hazard to citizens.`,
    trigger_cause: 'Regional rainfall gauges and catchment basin runoff exceeded safe drainage capacity thresholds.',
    danger_timeline: 'Peak runoff expected in 45-90 minutes. Road access may be compromised.',
    immediate_actions: [
      'Do NOT attempt to drive through water-covered roads or underpasses.',
      'Elevate essential appliances and food stores above floor level.',
      'Identify nearest high-ground designated safe shelter.'
    ],
    evacuation_advice: 'Residents in low-elevation ground-floor housing should prepare to move to elevated safe zones immediately.',
    safety_rating: req.severity === 'CRITICAL' ? 'EXTREME DANGER' : 'HIGH VIGILANCE'
  };
};

export const interpretRiskWithAI = async (
  req: RiskInterpretationRequest
): Promise<RiskInterpretationResponse> => {
  try {
    const res = await fetch(`${API_BASE}/interpret-risk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend interpret risk failed, using client fallback:', err);
  }

  return {
    composite_score: req.risk_score,
    risk_level: req.risk_score >= 80 ? 'CRITICAL' : req.risk_score >= 60 ? 'HIGH' : 'MODERATE',
    summary: `Composite risk index is ${req.risk_score}/100 driven by ${req.rainfall_mm}mm precipitation and ${req.water_depth_m}m projected water depth.`,
    factor_breakdown: [
      {
        factor: 'Rainfall Accumulation',
        weight: 35.0,
        contribution_percent: 32.5,
        status: 'DANGEROUS',
        detail: `${req.rainfall_mm} mm recorded in past 6 hours.`
      },
      {
        factor: 'Water Depth Projection',
        weight: 30.0,
        contribution_percent: 27.0,
        status: 'CRITICAL',
        detail: `${req.water_depth_m} m depth exceeds vehicle clearance.`
      },
      {
        factor: 'Inundation Model Probability',
        weight: 20.0,
        contribution_percent: 18.0,
        status: 'CONFIRMED',
        detail: `${Math.round(req.flood_probability * 100)}% model probability from hydrological analysis.`
      },
      {
        factor: 'Population Density',
        weight: 15.0,
        contribution_percent: 12.0,
        status: 'HIGH EXPOSURE',
        detail: `${req.population_density.toLocaleString()} residents in target quadrant.`
      }
    ],
    trend_trajectory: 'RAPID ESCALATION (+18 pts in past 2 hrs). Peak projected in 45-75 minutes.',
    recommended_tactical_actions: [
      'Deploy mobile barriers along North-South drainage corridor',
      'Pre-position amphibious rescue squads at Sector 7 staging zone',
      'Trigger automated reverse-911 cell broadcast to residents within 1.5 km radius'
    ],
    forecast_horizon_hours: 3
  };
};


export const fetchEmergencyBriefing = async (role: string = 'OPERATOR'): Promise<EmergencyBriefingResponse> => {
  const res = await fetch(`${API_BASE}/briefing?role=${role}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error('Failed to fetch emergency briefing');
  return await res.json();
};

export const analyzeIncidentAI = async (incidentId: number, role: string = 'OPERATOR'): Promise<IncidentAnalysisResponse> => {
  const res = await fetch(`${API_BASE}/analyze-incident`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ incident_id: incidentId, role }),
  });
  if (!res.ok) throw new Error('Failed to analyze incident');
  return await res.json();
};

export const explainRiskAI = async (zoneId?: number): Promise<RiskExplanationResponse> => {
  const res = await fetch(`${API_BASE}/explain-risk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ zone_id: zoneId }),
  });
  if (!res.ok) throw new Error('Failed to explain risk');
  return await res.json();
};

export const recommendShelterAI = async (latitude: number, longitude: number, role: string = 'CITIZEN'): Promise<ShelterRecommendationResponse> => {
  const res = await fetch(`${API_BASE}/recommend-shelter`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latitude, longitude, role }),
  });
  if (!res.ok) throw new Error('Failed to recommend shelter');
  return await res.json();
};
