/**
 * Situational Awareness & Operations Intelligence Service Layer
 * Connects frontend React components to Phase 6 Command-Centre APIs.
 */

import {
  SituationalSnapshot,
  OperationalChange,
  RiskHotspot,
  IncidentCluster,
  OperatorAttentionItem,
  OperationalEvent,
  ResourceContention,
  AIBriefing,
} from '../types/situationalAwareness';

const getApiBase = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return `${envUrl.replace(/\/$/, '')}/api/v1`;
  }
  return '/api/v1';
};

const API_BASE = getApiBase();

async function fetchWithTimeout<T>(
  url: string,
  options: RequestInit = {},
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
        if (errorData?.detail) errDetail = errorData.detail;
      } catch (_) {}
      throw new Error(errDetail);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timer);
    throw error;
  }
}

export const situationalAwarenessService = {
  /**
   * Get current real-time situation snapshot
   */
  async getCurrentSituation(): Promise<SituationalSnapshot> {
    const raw = await fetchWithTimeout<any>(`${API_BASE}/situation/current`);
    return {
      id: raw.id,
      riskScore: raw.risk_score,
      riskLevel: raw.risk_level,
      dominantThreat: raw.dominant_threat,
      trend: raw.trend,
      activeEmergencies: raw.active_emergencies,
      criticalEmergencies: raw.critical_emergencies,
      activeAlertsCount: raw.active_alerts_count,
      assignedTeamsCount: raw.assigned_teams_count,
      enRouteTeamsCount: raw.en_route_teams_count,
      resourceContentionsCount: raw.resource_contentions_count,
      operationalBottlenecksCount: raw.operational_bottlenecks_count,
      provenance: raw.provenance,
      confidence: raw.confidence,
      summary: raw.summary,
      delta: raw.delta ? {
        riskScoreDelta: raw.delta.risk_score_delta,
        activeEmergenciesDelta: raw.delta.active_emergencies_delta,
        criticalEmergenciesDelta: raw.delta.critical_emergencies_delta,
        alertsDelta: raw.delta.alerts_delta,
        timeDeltaSeconds: raw.delta.time_delta_seconds,
        direction: raw.delta.direction,
      } : undefined,
      createdAt: raw.created_at,
    };
  },

  /**
   * Get recent detected changes and significant deltas
   */
  async getSituationChanges(minutes = 15): Promise<{ changes: OperationalChange[]; count: number }> {
    const raw = await fetchWithTimeout<any>(`${API_BASE}/situation/changes?minutes=${minutes}`);
    const changes: OperationalChange[] = (raw.recent_changes || []).map((c: any) => ({
      changeType: c.change_type,
      severity: c.severity,
      metric: c.metric,
      previousValue: c.previous_value,
      currentValue: c.current_value,
      delta: c.delta,
      significance: c.significance,
      description: c.description,
      provenance: c.provenance,
      timestamp: c.timestamp,
    }));
    return { changes, count: raw.count ?? changes.length };
  },

  /**
   * Get historical situation snapshots
   */
  async getSituationHistory(limit = 20): Promise<SituationalSnapshot[]> {
    const rawList = await fetchWithTimeout<any[]>(`${API_BASE}/situation/history?limit=${limit}`);
    return rawList.map((raw) => ({
      id: raw.id,
      riskScore: raw.risk_score,
      riskLevel: raw.risk_level,
      dominantThreat: raw.dominant_threat,
      trend: raw.trend,
      activeEmergencies: raw.active_emergencies,
      criticalEmergencies: raw.critical_emergencies,
      activeAlertsCount: raw.active_alerts_count,
      assignedTeamsCount: raw.assigned_teams_count,
      enRouteTeamsCount: raw.en_route_teams_count,
      resourceContentionsCount: raw.resource_contentions_count,
      operationalBottlenecksCount: raw.operational_bottlenecks_count,
      provenance: raw.provenance,
      confidence: raw.confidence,
      summary: raw.summary,
      createdAt: raw.created_at,
    }));
  },

  /**
   * Get geographic risk hotspots
   */
  async getHotspots(): Promise<RiskHotspot[]> {
    const rawList = await fetchWithTimeout<any[]>(`${API_BASE}/hotspots/`);
    return rawList.map((h) => ({
      id: h.id,
      name: h.name,
      latitude: h.latitude,
      longitude: h.longitude,
      radiusMeters: h.radius_meters,
      compositeScore: h.composite_score,
      severity: h.severity,
      contributingSignals: h.contributing_signals || {},
      status: h.status,
      provenance: h.provenance,
      confidence: h.confidence,
      createdAt: h.created_at,
    }));
  },

  /**
   * Get incident clusters
   */
  async getClusters(): Promise<IncidentCluster[]> {
    const rawList = await fetchWithTimeout<any[]>(`${API_BASE}/clusters/`);
    return rawList.map((c) => ({
      id: c.id,
      clusterCode: c.cluster_code,
      centerLat: c.center_lat,
      centerLon: c.center_lon,
      radiusMeters: c.radius_meters,
      incidentCount: c.incident_count,
      criticalCount: c.critical_count,
      compositePriority: c.composite_priority,
      status: c.status,
      incidentIds: c.incident_ids || [],
      recommendedTeams: (c.recommended_teams || []).map((t: any) => ({
        teamId: t.team_id,
        teamName: t.team_name,
        matchScore: t.match_score,
        distanceKm: t.distance_km,
      })),
      provenance: c.provenance,
      confidence: c.confidence,
      createdAt: c.created_at,
    }));
  },

  /**
   * Get paginated operational timeline
   */
  async getOperationalTimeline(limit = 50, offset = 0): Promise<{ events: OperationalEvent[]; total: number }> {
    const raw = await fetchWithTimeout<any>(`${API_BASE}/operations/timeline?limit=${limit}&offset=${offset}`);
    const events: OperationalEvent[] = (raw.events || []).map((e: any) => ({
      id: e.id,
      eventType: e.event_type,
      category: e.category,
      severity: e.severity,
      title: e.title,
      description: e.description,
      provenance: e.provenance,
      actor: e.actor,
      confidence: e.confidence,
      eventMetadata: e.event_metadata,
      createdAt: e.created_at,
    }));
    return { events, total: raw.total ?? events.length };
  },

  /**
   * Get operator attention queue
   */
  async getOperatorAttentionQueue(status = 'PENDING'): Promise<{ items: OperatorAttentionItem[]; pendingCount: number }> {
    const raw = await fetchWithTimeout<any>(`${API_BASE}/operations/attention?status=${status}`);
    const items: OperatorAttentionItem[] = (raw.items || []).map((item: any) => ({
      id: item.id,
      title: item.title,
      summary: item.summary,
      priority: item.priority,
      status: item.status,
      itemType: item.item_type,
      provenance: item.provenance,
      recommendedAction: item.recommended_action,
      actionData: item.action_data,
      acknowledgedAt: item.acknowledged_at,
      acknowledgedBy: item.acknowledged_by,
      createdAt: item.created_at,
    }));
    return { items, pendingCount: raw.pending_count ?? items.length };
  },

  /**
   * Acknowledge operator attention item
   */
  async acknowledgeAttentionItem(id: number, acknowledgedBy = 'OPERATOR_1'): Promise<OperatorAttentionItem> {
    const raw = await fetchWithTimeout<any>(`${API_BASE}/operations/attention/${id}/acknowledge`, {
      method: 'POST',
      body: JSON.stringify({ acknowledged_by: acknowledgedBy }),
    });
    return {
      id: raw.id,
      title: raw.title,
      summary: raw.summary,
      priority: raw.priority,
      status: raw.status,
      itemType: raw.item_type,
      provenance: raw.provenance,
      recommendedAction: raw.recommended_action,
      actionData: raw.action_data,
      acknowledgedAt: raw.acknowledged_at,
      acknowledgedBy: raw.acknowledged_by,
      createdAt: raw.created_at,
    };
  },

  /**
   * Get active resource contentions with Option A vs Option B
   */
  async getResourceConflicts(): Promise<{ contentions: ResourceContention[]; count: number }> {
    const raw = await fetchWithTimeout<any>(`${API_BASE}/operations/conflicts`);
    const contentions: ResourceContention[] = (raw.contentions || []).map((c: any) => ({
      id: String(c.incident_id || c.id || Math.random()),
      incidentId: c.incident_id,
      incidentTitle: c.incident_title,
      incidentSeverity: c.incident_severity,
      location: c.location,
      requestedCapability: c.requested_capability,
      contenders: c.contenders || [],
      optionA: {
        optionId: 'A',
        teamId: c.option_a?.team_id,
        teamName: c.option_a?.team_name,
        teamType: c.option_a?.team_type || 'Rapid Response',
        distanceKm: c.option_a?.distance_km,
        estimatedArrivalMinutes: c.option_a?.estimated_arrival_minutes,
        capabilityMatchScore: c.option_a?.capability_match_score,
        currentWorkload: c.option_a?.current_workload,
        advantages: c.option_a?.advantages || [],
        warnings: c.option_a?.warnings || [],
      },
      optionB: {
        optionId: 'B',
        teamId: c.option_b?.team_id,
        teamName: c.option_b?.team_name,
        teamType: c.option_b?.team_type || 'Support Division',
        distanceKm: c.option_b?.distance_km,
        estimatedArrivalMinutes: c.option_b?.estimated_arrival_minutes,
        capabilityMatchScore: c.option_b?.capability_match_score,
        currentWorkload: c.option_b?.current_workload,
        advantages: c.option_b?.advantages || [],
        warnings: c.option_b?.warnings || [],
      },
      provenance: c.provenance,
      recommendedAction: c.recommended_action,
    }));
    return { contentions, count: raw.count ?? contentions.length };
  },

  /**
   * Get 5-part AI Situational Briefing
   */
  async getAIBriefing(): Promise<AIBriefing> {
    const raw = await fetchWithTimeout<any>(`${API_BASE}/ai/briefing`);
    return {
      executiveSummary: raw.executive_summary,
      evidenceItems: (raw.evidence_items || []).map((item: any) => ({
        type: item.type,
        statement: item.statement,
        confidence: item.confidence,
        source: item.source,
        timestamp: item.timestamp,
      })),
      dominantThreat: raw.dominant_threat,
      recommendedPriorities: raw.recommended_priorities || [],
      generatedAt: raw.generated_at,
      provenance: raw.provenance,
      confidence: raw.confidence,
    };
  },

  /**
   * Phase 6 Simulation Controls
   */
  async startPhase6Simulation(): Promise<any> {
    return fetchWithTimeout<any>(`${API_BASE}/simulation/phase6/start`, { method: 'POST' });
  },

  async stepPhase6Simulation(step?: number): Promise<any> {
    return fetchWithTimeout<any>(`${API_BASE}/simulation/phase6/step`, {
      method: 'POST',
      body: JSON.stringify(step !== undefined ? { step } : {}),
    });
  },

  async resetPhase6Simulation(): Promise<any> {
    return fetchWithTimeout<any>(`${API_BASE}/simulation/phase6/reset`, { method: 'POST' });
  },

  async getPhase6SimulationState(): Promise<any> {
    return fetchWithTimeout<any>(`${API_BASE}/simulation/phase6/state`);
  },
};
