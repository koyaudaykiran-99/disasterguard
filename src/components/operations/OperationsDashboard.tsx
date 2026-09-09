import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle,
  Clock,
  Users,
  Hospital,
  Home,
  Truck,
  RefreshCw,
  AlertCircle,
  X,
  Layers,
  ArrowRight,
  Sparkles,
  Info,
  ChevronDown
} from 'lucide-react';

interface OperationalOverview {
  active_incidents_count: number;
  critical_incidents_count: number;
  high_priority_incidents_count: number;
  teams_available_count: number;
  teams_busy_count: number;
  teams_en_route_count: number;
  shelter_available_capacity: number;
  hospital_available_beds: number;
  unassigned_incidents_count: number;
  contentions_count: number;
  bottlenecks_count: number;
  provenance: Record<string, string>;
}

interface PrioritizedIncident {
  id: number;
  title: string;
  description: string;
  severity: string;
  status: string;
  latitude: number;
  longitude: number;
  people_at_risk: number;
  priority_score: number;
  priority_level: string;
  created_at: string | null;
  is_trapped: boolean;
  is_medical: boolean;
  recommended_team_id: number | null;
  recommended_team_name: string | null;
  is_contended: boolean;
  contention_note: string | null;
}

interface ResourceContention {
  id: number;
  resource_id: number;
  resource_name: string;
  incident_ids: number[];
  preferred_incident_id: number;
  severity: string;
  description: string;
}

interface OperationalBottleneck {
  id: number;
  zone: string;
  bottleneck_type: string;
  severity: string;
  description: string;
  guidance?: string;
}

interface CandidateTeam {
  id: number;
  name: string;
  score: number;
  status: string;
  distance_km: number;
  distance_label: string;
  capabilities: string[];
  telemetry_age_minutes: number;
  data_provenance: string;
  reasons: string[];
  warnings: string[];
}

interface ResponsePlan {
  id?: number;
  incident_id: number;
  priority: string;
  priority_score: number;
  recommended_team: CandidateTeam | null;
  alternative_teams: CandidateTeam[];
  recommended_shelter: {
    id: number;
    name: string;
    score: number;
    distance_label: string;
    available_capacity: number;
    occupancy_pct: number;
    data_provenance: string;
  } | null;
  recommended_hospital: {
    id: number;
    name: string;
    score: number;
    distance_label: string;
    emergency_capacity: string;
    available_beds: number;
    data_provenance: string;
  } | null;
  contention?: {
    is_contended: boolean;
    explanation?: string;
  } | null;
  reasons: string[];
  warnings: string[];
  confidence: string;
  data_provenance: Record<string, string>;
  human_confirmation_required: boolean;
  status: string;
}

export const OperationsDashboard: React.FC = () => {
  const [overview, setOverview] = useState<OperationalOverview | null>(null);
  const [incidents, setIncidents] = useState<PrioritizedIncident[]>([]);
  const [contentions, setContentions] = useState<ResourceContention[]>([]);
  const [bottlenecks, setBottlenecks] = useState<OperationalBottleneck[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<string>('priority');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Modal states
  const [selectedPlanIncidentId, setSelectedPlanIncidentId] = useState<number | null>(null);
  const [activePlan, setActivePlan] = useState<ResponsePlan | null>(null);
  const [isPlanLoading, setIsPlanLoading] = useState<boolean>(false);
  const [isOverrideModalOpen, setIsOverrideModalOpen] = useState<boolean>(false);
  const [overrideTeamId, setOverrideTeamId] = useState<number | null>(null);
  const [overrideReason, setOverrideReason] = useState<string>('');
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);

  const fetchOperationsData = async () => {
    try {
      const [ovRes, incRes, conRes, botRes] = await Promise.all([
        fetch('/api/v1/operations/overview'),
        fetch(`/api/v1/operations/incidents?status=${statusFilter}&sort_by=${sortBy}`),
        fetch('/api/v1/operations/contentions'),
        fetch('/api/v1/operations/bottlenecks'),
      ]);

      if (ovRes.ok) setOverview(await ovRes.json());
      if (incRes.ok) setIncidents(await incRes.json());
      if (conRes.ok) setContentions(await conRes.json());
      if (botRes.ok) setBottlenecks(await botRes.json());
    } catch (err) {
      console.error('Failed to load operational intelligence:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchOperationsData();
    const interval = setInterval(fetchOperationsData, 10000);
    return () => clearInterval(interval);
  }, [statusFilter, sortBy]);

  const handleOpenPlan = async (incId: number) => {
    setSelectedPlanIncidentId(incId);
    setIsPlanLoading(true);
    setActionSuccessMessage(null);
    try {
      const res = await fetch(`/api/v1/operations/incidents/${incId}/response-plan`);
      if (res.ok) {
        const plan = await res.json();
        setActivePlan(plan);
        if (plan.alternative_teams && plan.alternative_teams.length > 0) {
          setOverrideTeamId(plan.alternative_teams[0].id);
        }
      }
    } catch (err) {
      console.error('Error fetching response plan:', err);
    } finally {
      setIsPlanLoading(false);
    }
  };

  const handleConfirmDispatch = async () => {
    if (!activePlan || !activePlan.recommended_team) return;
    try {
      const token = localStorage.getItem('access_token') || 'demo-operator-token';
      const res = await fetch('/api/v1/rescue/assignments/dispatch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-User-Role': 'OPERATOR',
        },
        body: JSON.stringify({
          incident_id: activePlan.incident_id,
          rescue_team_id: activePlan.recommended_team.id,
          operator_notes: 'Confirmed via Operations Dashboard Response Plan Review',
        }),
      });

      if (res.ok) {
        setActionSuccessMessage(`Rescue squad ${activePlan.recommended_team.name} successfully dispatched by Operator confirmation!`);
        fetchOperationsData();
        setTimeout(() => {
          setSelectedPlanIncidentId(null);
          setActivePlan(null);
        }, 1800);
      } else {
        const err = await res.json();
        alert(`Dispatch failed: ${err.detail || 'Unauthorized'}`);
      }
    } catch (err) {
      alert(`Network error dispatching unit: ${err}`);
    }
  };

  const handleOverrideSubmit = async () => {
    if (!activePlan || !overrideTeamId || !overrideReason.trim()) {
      alert('Please select an alternative team and enter an override rationale.');
      return;
    }
    try {
      const token = localStorage.getItem('access_token') || 'demo-operator-token';
      const res = await fetch(`/api/v1/operations/incidents/${activePlan.incident_id}/response-plan/override`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-User-Role': 'OPERATOR',
        },
        body: JSON.stringify({
          selected_team_id: overrideTeamId,
          override_reason: overrideReason,
        }),
      });

      if (res.ok) {
        const updated = await res.json();
        setActivePlan(updated);
        setIsOverrideModalOpen(false);
        setActionSuccessMessage('Operator override recorded in audit logs. Team updated.');
        fetchOperationsData();
      }
    } catch (err) {
      alert(`Error submitting override: ${err}`);
    }
  };

  const getPriorityColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/40';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
      case 'MEDIUM':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Section: Overview Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-3.5 rounded-xl bg-gray-900/80 border border-red-500/30 font-mono">
          <div className="flex items-center justify-between text-gray-400 text-xs uppercase">
            <span>Critical</span>
            <AlertTriangle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-red-400 mt-1">
            {overview?.critical_incidents_count ?? 0}
          </div>
          <div className="text-[10px] text-gray-500 mt-0.5">Priority 90-100</div>
        </div>

        <div className="p-3.5 rounded-xl bg-gray-900/80 border border-orange-500/30 font-mono">
          <div className="flex items-center justify-between text-gray-400 text-xs uppercase">
            <span>Active SOS</span>
            <ShieldAlert className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-2xl font-bold text-orange-400 mt-1">
            {overview?.active_incidents_count ?? 0}
          </div>
          <div className="text-[10px] text-gray-500 mt-0.5">Unresolved</div>
        </div>

        <div className="p-3.5 rounded-xl bg-gray-900/80 border border-emerald-500/30 font-mono">
          <div className="flex items-center justify-between text-gray-400 text-xs uppercase">
            <span>Teams Avail</span>
            <Truck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {overview?.teams_available_count ?? 0}
          </div>
          <div className="text-[10px] text-gray-500 mt-0.5">{overview?.teams_busy_count ?? 0} busy / deployed</div>
        </div>

        <div className="p-3.5 rounded-xl bg-gray-900/80 border border-cyan-500/30 font-mono">
          <div className="flex items-center justify-between text-gray-400 text-xs uppercase">
            <span>Shelter Cap</span>
            <Home className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-400 mt-1">
            {overview?.shelter_available_capacity ?? 0}
          </div>
          <div className="text-[10px] text-cyan-500/70 mt-0.5">Available (MOCK)</div>
        </div>

        <div className="p-3.5 rounded-xl bg-gray-900/80 border border-purple-500/30 font-mono">
          <div className="flex items-center justify-between text-gray-400 text-xs uppercase">
            <span>Trauma Beds</span>
            <Hospital className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-purple-400 mt-1">
            {overview?.hospital_available_beds ?? 0}
          </div>
          <div className="text-[10px] text-purple-500/70 mt-0.5">Available (MOCK)</div>
        </div>

        <div className="p-3.5 rounded-xl bg-gray-900/80 border border-amber-500/30 font-mono">
          <div className="flex items-center justify-between text-gray-400 text-xs uppercase">
            <span>Bottlenecks</span>
            <Layers className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {overview?.bottlenecks_count ?? 0}
          </div>
          <div className="text-[10px] text-amber-500/70 mt-0.5">{overview?.contentions_count ?? 0} contentions</div>
        </div>
      </div>

      {/* Resource Contention Banner (if any contention detected) */}
      {contentions.length > 0 && (
        <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/50 space-y-2 font-mono">
          <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
            <AlertCircle className="w-4 h-4 animate-pulse text-amber-400" />
            <span>OPERATIONAL RESOURCE CONTENTION DETECTED ({contentions.length})</span>
          </div>
          {contentions.map((c) => (
            <div key={c.id} className="text-xs text-amber-200/90 pl-6 border-l-2 border-amber-500/40 space-y-1">
              <div className="font-semibold text-white">{c.description}</div>
              <div className="text-[11px] text-amber-400/80">
                AI Advisory: Higher priority incident given primary claim. Operators may review alternatives in the queue.
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Operational Bottlenecks Ribbon */}
      {bottlenecks.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {bottlenecks.map((b) => (
            <div
              key={b.id}
              className="p-3 rounded-lg bg-gray-900/60 border border-gray-800 text-xs font-mono space-y-1"
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-gray-300 uppercase flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  {b.bottleneck_type.replace('_', ' ')}
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {b.severity}
                </span>
              </div>
              <p className="text-gray-400 text-[11px]">{b.description}</p>
              {b.guidance && <p className="text-indigo-400 text-[10px] font-semibold">&rarr; {b.guidance}</p>}
            </div>
          ))}
        </div>
      )}

      {/* Main Prioritized Incident Queue */}
      <div className="space-y-3 font-mono">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-gray-200 uppercase">
              Operational Priority Queue ({incidents.length})
            </span>
            <span className="text-[11px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Decision Support
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-gray-900 border border-gray-700 rounded-lg px-2.5 py-1 text-gray-200 text-xs focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="PENDING">Pending (Unassigned)</option>
              <option value="DISPATCHED">Dispatched</option>
              <option value="RESOLVED">Resolved</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-gray-900 border border-gray-700 rounded-lg px-2.5 py-1 text-gray-200 text-xs focus:outline-none focus:border-indigo-500"
            >
              <option value="priority">Sort: Priority Score (0-100)</option>
              <option value="people">Sort: People at Risk</option>
              <option value="age">Sort: Oldest First</option>
            </select>

            <button
              onClick={fetchOperationsData}
              className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition"
              title="Refresh operational queue"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-gray-500 text-xs font-mono animate-pulse">
            Analyzing multi-hazard telemetry and evaluating candidate assignments...
          </div>
        ) : incidents.length === 0 ? (
          <div className="p-8 text-center text-gray-500 text-xs font-mono bg-gray-900/40 rounded-xl border border-gray-800">
            No active emergencies matching filter. Regional operations stable.
          </div>
        ) : (
          <div className="space-y-2.5">
            {incidents.map((inc) => (
              <div
                key={inc.id}
                className="p-4 rounded-xl bg-gray-900/70 border border-gray-800 hover:border-indigo-500/50 transition space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getPriorityColor(inc.priority_level)}`}>
                        {inc.priority_level} &bull; {inc.priority_score}/100
                      </span>
                      <span className="text-xs font-bold text-white uppercase tracking-wide">
                        Incident #{inc.id}: {inc.title}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 line-clamp-1">{inc.description}</p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => handleOpenPlan(inc.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition shadow-lg shadow-indigo-600/20"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Review Plan</span>
                    </button>
                  </div>
                </div>

                {/* Sub-pills: Tags, Team Candidate, Contention */}
                <div className="flex flex-wrap items-center gap-2 text-[11px] pt-2 border-t border-gray-800/80">
                  {inc.is_trapped && (
                    <span className="px-2 py-0.5 rounded bg-red-950/60 border border-red-500/40 text-red-300 font-semibold">
                      TRAPPED PERSON
                    </span>
                  )}
                  {inc.is_medical && (
                    <span className="px-2 py-0.5 rounded bg-rose-950/60 border border-rose-500/40 text-rose-300 font-semibold">
                      MEDICAL URGENCY
                    </span>
                  )}
                  <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 flex items-center gap-1">
                    <Users className="w-3 h-3 text-gray-400" />
                    {inc.people_at_risk} at risk
                  </span>

                  {inc.recommended_team_name && (
                    <span className="px-2 py-0.5 rounded bg-blue-950/40 border border-blue-500/30 text-blue-300 flex items-center gap-1">
                      <Truck className="w-3 h-3 text-blue-400" />
                      Candidate: {inc.recommended_team_name}
                    </span>
                  )}

                  {inc.is_contended && (
                    <span className="px-2 py-0.5 rounded bg-amber-950/60 border border-amber-500/40 text-amber-300 font-bold flex items-center gap-1">
                      <AlertCircle className="w-3 h-3 text-amber-400" />
                      Contended Resource
                    </span>
                  )}

                  <span className="ml-auto text-[10px] text-gray-500">
                    Status: <strong className="text-gray-300">{inc.status}</strong>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Response Plan Review Modal */}
      {selectedPlanIncidentId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm font-mono animate-in fade-in">
          <div className="w-full max-w-2xl bg-gray-900 border border-gray-700 rounded-2xl p-6 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
                  <ShieldAlert className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                    Operational Response Plan — Incident #{selectedPlanIncidentId}
                  </h3>
                  <div className="text-[11px] text-gray-400">
                    Decision Support Object &bull; Inviolate Human Confirmation Required
                  </div>
                </div>
              </div>
              <button
                onClick={() => {
                  setSelectedPlanIncidentId(null);
                  setActivePlan(null);
                }}
                className="p-1 rounded-lg text-gray-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {isPlanLoading || !activePlan ? (
              <div className="p-8 text-center text-gray-400 text-xs animate-pulse">
                Synthesizing multi-resource candidate ranking and evaluating facility safety...
              </div>
            ) : (
              <div className="space-y-4 text-xs">
                {/* Priority & Status Bar */}
                <div className="flex items-center justify-between p-3 rounded-xl bg-gray-950/60 border border-gray-800">
                  <div>
                    <div className="text-gray-400 text-[10px] uppercase">Operational Priority Score</div>
                    <div className="text-lg font-bold text-white">
                      {activePlan.priority_score} / 100 ({activePlan.priority})
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-gray-400 text-[10px] uppercase">Plan Status</div>
                    <div className="text-sm font-bold text-indigo-400">{activePlan.status}</div>
                  </div>
                </div>

                {/* Primary Recommended Team */}
                {activePlan.recommended_team && (
                  <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-500/30 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-blue-300 text-xs uppercase flex items-center gap-1.5">
                        <Truck className="w-4 h-4 text-blue-400" />
                        Recommended Rescue Squad: {activePlan.recommended_team.name}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-200 border border-blue-500/30 font-bold">
                        Score: {activePlan.recommended_team.score}/100
                      </span>
                    </div>
                    <div className="text-[11px] text-gray-300">
                      Distance: <strong className="text-blue-200">{activePlan.recommended_team.distance_label}</strong>
                    </div>
                    <div className="text-[11px] text-gray-400">
                      Capabilities: {activePlan.recommended_team.capabilities.join(', ')}
                    </div>
                    <div className="text-[10px] text-gray-500">
                      Telemetry: {activePlan.recommended_team.telemetry_age_minutes} min old (Provenance: {activePlan.recommended_team.data_provenance})
                    </div>
                  </div>
                )}

                {/* Recommended Shelter & Hospital (2 cols) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {/* Shelter */}
                  <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-1">
                    <div className="flex items-center gap-1 text-emerald-300 font-bold text-xs uppercase">
                      <Home className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Shelter: {activePlan.recommended_shelter?.name || 'Central Facility'}</span>
                    </div>
                    <div className="text-[11px] text-gray-300">
                      Available Capacity: <strong className="text-emerald-300">{activePlan.recommended_shelter?.available_capacity ?? 120}</strong>
                    </div>
                    <div className="text-[10px] text-gray-500">
                      {activePlan.recommended_shelter?.distance_label} &bull; Provenance: {activePlan.recommended_shelter?.data_provenance}
                    </div>
                  </div>

                  {/* Hospital */}
                  <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-1">
                    <div className="flex items-center gap-1 text-rose-300 font-bold text-xs uppercase">
                      <Hospital className="w-3.5 h-3.5 text-rose-400" />
                      <span>Hospital: {activePlan.recommended_hospital?.name || 'Regional Medical'}</span>
                    </div>
                    <div className="text-[11px] text-gray-300">
                      Available Beds: <strong className="text-rose-300">{activePlan.recommended_hospital?.available_beds ?? 12}</strong> ({activePlan.recommended_hospital?.emergency_capacity})
                    </div>
                    <div className="text-[10px] text-gray-500">
                      {activePlan.recommended_hospital?.distance_label} &bull; Provenance: {activePlan.recommended_hospital?.data_provenance}
                    </div>
                  </div>
                </div>

                {/* Reasons List */}
                <div className="p-3 rounded-lg bg-black/40 border border-gray-800 space-y-1">
                  <div className="text-[10px] uppercase font-bold text-gray-400">Optimization Reasons:</div>
                  <ul className="space-y-0.5 text-gray-300 text-[11px]">
                    {activePlan.reasons.map((r, i) => (
                      <li key={i} className="flex items-center gap-1.5">
                        <CheckCircle className="w-3 h-3 text-emerald-400 shrink-0" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Warnings List (if any) */}
                {activePlan.warnings.length > 0 && (
                  <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/30 space-y-1">
                    <div className="text-[10px] uppercase font-bold text-amber-400">Operational Warnings:</div>
                    <ul className="space-y-0.5 text-amber-200/90 text-[11px]">
                      {activePlan.warnings.map((w, i) => (
                        <li key={i} className="flex items-center gap-1.5">
                          <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
                          <span>{w}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Inviolate Human Confirmation Barrier Banner */}
                <div className="p-3 rounded-lg bg-indigo-950/30 border border-indigo-500/40 text-[11px] text-indigo-200 flex items-start gap-2">
                  <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-white">Human Confirmation Barrier:</strong> Automated engines produce recommendations only. Only explicit confirmation by an authorized Command Centre operator dispatches personnel.
                  </div>
                </div>

                {actionSuccessMessage && (
                  <div className="p-3 rounded-lg bg-emerald-900/40 border border-emerald-500 text-emerald-200 text-xs font-bold text-center animate-in fade-in">
                    {actionSuccessMessage}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex flex-wrap items-center justify-end gap-3 pt-3 border-t border-gray-800">
                  <button
                    onClick={() => setIsOverrideModalOpen(true)}
                    className="px-3.5 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-bold transition"
                  >
                    Override Team...
                  </button>

                  <button
                    onClick={handleConfirmDispatch}
                    className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow-lg shadow-emerald-600/20 flex items-center gap-1.5"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>CONFIRM DISPATCH</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Override Sub-Modal */}
      {isOverrideModalOpen && activePlan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm font-mono animate-in fade-in">
          <div className="w-full max-w-md bg-gray-900 border border-gray-700 rounded-xl p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-gray-800 pb-2">
              <span className="font-bold text-sm text-white uppercase">Operator Override</span>
              <button onClick={() => setIsOverrideModalOpen(false)} className="text-gray-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <label className="text-gray-400 text-[11px] block">Select Alternative Squad:</label>
              <select
                value={overrideTeamId || ''}
                onChange={(e) => setOverrideTeamId(Number(e.target.value))}
                className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-gray-200"
              >
                {activePlan.alternative_teams.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name} (Score: {t.score}/100, Dist: {t.distance_km} km)
                  </option>
                ))}
              </select>

              <label className="text-gray-400 text-[11px] block pt-2">Override Rationale (Required for Audit Trail):</label>
              <textarea
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                placeholder="e.g., Team Alpha handling secondary life-safety emergency in North Sector"
                className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-gray-200 text-xs h-20"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-800 text-xs">
              <button
                onClick={() => setIsOverrideModalOpen(false)}
                className="px-3 py-1.5 rounded-lg bg-gray-800 text-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={handleOverrideSubmit}
                className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold"
              >
                Save Override
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
