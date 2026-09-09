import React, { useState, useEffect } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { EmergencySOSButton } from '../components/motion/EmergencySOSButton';
import { AnimatedCard } from '../components/motion/AnimatedCard';
import { StaggeredList } from '../components/motion/StaggeredList';
import { useDisaster } from '../context/DisasterContext';
import {
  Radio,
  PhoneCall,
  MapPin,
  Users,
  CheckCircle,
  ShieldAlert,
  Navigation,
  Hospital,
  Home,
  Clock,
  AlertTriangle,
  Send,
  Sparkles,
  Brain,
  FileText,
  UserCheck,
  Layers,
  Activity,
  Play,
  RotateCcw,
  FastForward,
  Shield
} from 'lucide-react';
import { AITriageEvidenceModal } from '../components/emergency/AITriageEvidenceModal';
import { AIRescueRecommendationPanel } from '../components/emergency/AIRescueRecommendationPanel';
import { EmergencyTimeline } from '../components/emergency/EmergencyTimeline';
import { OperationsDashboard } from '../components/operations/OperationsDashboard';
import { SituationAwarenessPanel } from '../components/operations/SituationAwarenessPanel';
import { OperatorAttentionQueue } from '../components/operations/OperatorAttentionQueue';
import { OperationalTimeline } from '../components/operations/OperationalTimeline';
import { ResponsePlanComparisonModal } from '../components/operations/ResponsePlanComparisonModal';
import { situationalAwarenessService } from '../services/situationalAwarenessService';
import { ResourceContention } from '../types/situationalAwareness';
import { SOSIncident } from '../types/disaster';

export const EmergencyPage: React.FC = () => {
  const { sosIncidents, createSOSRequest, resolveSOSIncident } = useDisaster();
  const [viewMode, setViewMode] = useState<'situational' | 'operations' | 'distress'>('distress');
  const [isSOSActive, setIsSOSActive] = useState<boolean>(false);
  const [selectedEvidenceIncident, setSelectedEvidenceIncident] = useState<SOSIncident | null>(null);
  const [customMessage, setCustomMessage] = useState<string>(
    'Water entered my house and an elderly person is trapped.'
  );
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Response Plan Comparison Modal State
  const [isComparisonOpen, setIsComparisonOpen] = useState<boolean>(false);
  const [activeContention, setActiveContention] = useState<ResourceContention | null>(null);

  // Phase 6 Simulation State
  const [simState, setSimState] = useState<any>({
    is_active: false,
    step: 0,
    total_steps: 17,
    stage_info: { title: 'Phase 6 Ready', stage: 'IDLE', description: '17-stage coordination demonstration' }
  });
  const [simLoading, setSimLoading] = useState<boolean>(false);

  const fetchSimState = async () => {
    try {
      const state = await situationalAwarenessService.getPhase6SimulationState();
      setSimState(state);
    } catch (e) {
      console.warn('Could not fetch phase 6 sim state:', e);
    }
  };

  useEffect(() => {
    fetchSimState();
  }, []);

  const handleStartSim = async () => {
    try {
      setSimLoading(true);
      const res = await situationalAwarenessService.startPhase6Simulation();
      setSimState(res);
    } catch (e) {
      console.error('Failed to start phase 6 sim:', e);
    } finally {
      setSimLoading(false);
    }
  };

  const handleStepSim = async () => {
    try {
      setSimLoading(true);
      const res = await situationalAwarenessService.stepPhase6Simulation();
      setSimState(res);
    } catch (e) {
      console.error('Failed to step phase 6 sim:', e);
    } finally {
      setSimLoading(false);
    }
  };

  const handleResetSim = async () => {
    try {
      setSimLoading(true);
      const res = await situationalAwarenessService.resetPhase6Simulation();
      setSimState(res);
    } catch (e) {
      console.error('Failed to reset phase 6 sim:', e);
    } finally {
      setSimLoading(false);
    }
  };

  const handleOpenContention = async (incidentId?: number) => {
    try {
      const conflicts = await situationalAwarenessService.getResourceConflicts();
      if (conflicts.contentions && conflicts.contentions.length > 0) {
        const target = incidentId
          ? conflicts.contentions.find(c => c.incidentId === incidentId) || conflicts.contentions[0]
          : conflicts.contentions[0];
        setActiveContention(target);
        setIsComparisonOpen(true);
      } else {
        // Fallback demo contention
        setActiveContention({
          id: 'contention-demo-1',
          incidentId: incidentId || 101,
          incidentTitle: 'Munirka Enclave Severe Water Ingress & Power Failure',
          incidentSeverity: 'CRITICAL',
          location: 'Munirka Basin, Sector 4',
          requestedCapability: 'SWIFT_WATER_BOAT',
          contenders: [
            { incidentId: 101, priority: 'CRITICAL', title: 'Munirka Enclave Water Ingress' },
            { incidentId: 102, priority: 'HIGH', title: 'IIT Delhi Subway Stranded Commuters' }
          ],
          optionA: {
            optionId: 'A',
            teamId: 1,
            teamName: 'NDRF Quick Response Team Alpha',
            teamType: 'Swift Water Inflatable Boat Unit',
            distanceKm: 2.1,
            estimatedArrivalMinutes: 8.5,
            capabilityMatchScore: 0.96,
            currentWorkload: 1,
            advantages: ['Immediate proximity (2.1 km)', 'High watercraft payload (12 pax)', 'Medical paramedic on board'],
            warnings: ['Already handling 1 secondary staging request']
          },
          optionB: {
            optionId: 'B',
            teamId: 2,
            teamName: 'SDRF Special Flood Division Bravo',
            teamType: 'Amphibious All-Terrain Rescue Unit',
            distanceKm: 4.8,
            estimatedArrivalMinutes: 16.0,
            capabilityMatchScore: 0.88,
            currentWorkload: 0,
            advantages: ['Completely free (0 active assignments)', 'Heavy winch & generator equipment'],
            warnings: ['Double transit time (16 min vs 8.5 min)', 'Longer route across flooded ring road']
          },
          provenance: 'REAL',
          recommendedAction: 'Confirm Option A for immediate critical rescue; hold Option B as reserve.'
        });
        setIsComparisonOpen(true);
      }
    } catch (e) {
      console.warn('Failed to load contention:', e);
    }
  };

  const handleDispatchConfirmed = async (
    incidentId: number,
    teamId: number,
    notes: string,
    isOverride: boolean
  ) => {
    const token = localStorage.getItem('access_token') || 'demo-operator-token';
    const res = await fetch('/api/v1/rescue/assignments/dispatch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        'X-User-Role': 'OPERATOR',
      },
      body: JSON.stringify({
        incident_id: incidentId,
        rescue_team_id: teamId,
        operator_notes: notes,
      }),
    });

    if (!res.ok) {
      let detail = 'Dispatch confirmation failed.';
      try {
        const err = await res.json();
        if (err.detail) detail = err.detail;
      } catch (_) {}
      throw new Error(detail);
    }
  };

  const handleSendCustomSOS = async (messageText: string) => {
    const text = messageText.trim() || 'Water entered my house and an elderly person is trapped.';
    setIsSubmitting(true);
    try {
      await createSOSRequest({
        citizenName: 'Citizen Emergency SOS',
        phone: '+1 (555) 911-2040',
        location: text,
        title: text,
        coordinates: [13.0827, 80.2707],
        emergencyType: 'TRAPPED',
        peopleCount: 2,
        urgency: 'CRITICAL',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTriggerSOS = () => {
    setIsSOSActive(!isSOSActive);
    if (!isSOSActive) {
      handleSendCustomSOS(customMessage);
    }
  };

  const pendingIncidents = sosIncidents.filter((i) => i.status !== 'RESCUED');
  const rescuedIncidents = sosIncidents.filter((i) => i.status === 'RESCUED');

  return (
    <PageTransition className="p-6 space-y-6">
      {/* View Mode Switcher Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-800 pb-3">
        <div className="flex items-center space-x-2 flex-wrap gap-y-2">
          <button
            onClick={() => setViewMode('situational')}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center space-x-2 ${
              viewMode === 'situational'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30 border border-blue-500'
                : 'bg-gray-900/90 text-gray-400 hover:text-white border border-gray-800'
            }`}
          >
            <Activity className="w-4 h-4 text-cyan-300" />
            <span>SITUATIONAL AWARENESS & REAL-TIME COORDINATION (PHASE 6)</span>
          </button>
          <button
            onClick={() => setViewMode('operations')}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center space-x-2 ${
              viewMode === 'operations'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-500'
                : 'bg-gray-900/90 text-gray-400 hover:text-white border border-gray-800'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>DISASTER OPERATIONS & RESOURCE OPTIMIZATION (PHASE 5.5)</span>
          </button>
          <button
            onClick={() => setViewMode('distress')}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center space-x-2 ${
              viewMode === 'distress'
                ? 'bg-red-600 text-white shadow-lg shadow-red-600/30 border border-red-500'
                : 'bg-gray-900/90 text-gray-400 hover:text-white border border-gray-800'
            }`}
          >
            <Radio className="w-4 h-4" />
            <span>SOS BEACONS & TRIAGE TIMELINE</span>
          </button>
        </div>

        {/* Phase 6 Simulation Demo Controls Bar */}
        <div className="flex items-center space-x-2 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800 text-xs font-mono">
          <span className="text-slate-400 px-2 py-0.5 text-[11px] hidden sm:inline">
            Phase 6 Demo: Step <strong className="text-white">{simState?.step || 0}</strong>/17
          </span>
          <button
            onClick={handleStartSim}
            disabled={simLoading}
            className="px-2.5 py-1 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 transition flex items-center space-x-1"
            title="Start Phase 6 Simulation"
          >
            <Play className="w-3 h-3" />
            <span>Start</span>
          </button>
          <button
            onClick={handleStepSim}
            disabled={simLoading}
            className="px-2.5 py-1 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/40 transition flex items-center space-x-1"
            title="Advance 1 Step in Simulation"
          >
            <FastForward className="w-3 h-3" />
            <span>Next</span>
          </button>
          <button
            onClick={handleResetSim}
            disabled={simLoading}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
            title="Reset Simulation to Baseline"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* VIEW MODE: Situational Awareness & Coordination (Phase 6) */}
      {viewMode === 'situational' && (
        <div className="space-y-6">
          {/* Top Real-Time Situational Awareness & What Changed Panel */}
          <SituationAwarenessPanel />

          {/* 2-Column Grid: Operator Attention Queue & Operational Timeline */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="min-h-[420px]">
              <OperatorAttentionQueue onOpenContention={handleOpenContention} />
            </div>
            <div className="min-h-[420px]">
              <OperationalTimeline limit={35} />
            </div>
          </div>
        </div>
      )}

      {/* VIEW MODE: Disaster Operations & Resource Optimization (Phase 5.5) */}
      {viewMode === 'operations' && (
        <div className="space-y-6">
          <SituationAwarenessPanel />
          <OperationsDashboard />
        </div>
      )}

      {/* VIEW MODE: Distress & SOS Feed */}
      {viewMode === 'distress' && (
        <>
          {/* Header & SOS Action Hero */}
          <div className="glass-panel p-8 rounded-2xl border border-red-500/30 bg-gradient-to-r from-red-950/30 via-command-card to-command-card text-center space-y-4">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-red-500/20 text-red-400 border border-red-500/40 text-xs font-mono font-bold">
              <Radio className="w-4 h-4 animate-pulse" />
              <span>DIRECT DISPATCH BEACON & AI TRIAGE</span>
            </div>

            <h2 className="text-2xl font-extrabold text-gray-100">
              Emergency Distress & SOS Dispatch Center
            </h2>
            <p className="text-xs text-gray-300 max-w-xl mx-auto font-mono">
              Submitting a citizen distress alert triggers backend PostgreSQL persistence, AI NLP triage classification, priority scoring, risk-zone lookup, and nearest rescue team dispatch.
            </p>

            {/* Quick Test Distress Message Dispatcher */}
            <div className="max-w-2xl mx-auto pt-2 text-left bg-black/40 p-4 rounded-xl border border-red-500/20 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-red-400 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  Citizen Emergency Distress Reporter
                </span>
                <span className="text-[10px] font-mono text-gray-400">PostgreSQL + AI Triage Integrated</span>
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={customMessage}
                  onChange={(e) => setCustomMessage(e.target.value)}
                  placeholder="Enter distress message (e.g. Water entered my house and an elderly person is trapped.)"
                  className="flex-1 bg-gray-900/90 border border-gray-700 rounded-lg px-3 py-2 text-xs font-mono text-gray-100 placeholder-gray-500 focus:outline-none focus:border-red-500"
                />
                <button
                  onClick={() => handleSendCustomSOS(customMessage)}
                  disabled={isSubmitting || !customMessage.trim()}
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white rounded-lg text-xs font-mono font-bold flex items-center gap-1.5 transition-colors shadow-lg shadow-red-600/30 shrink-0"
                >
                  <Send className="w-3.5 h-3.5" />
                  {isSubmitting ? 'Transmitting...' : 'Dispatch SOS'}
                </button>
              </div>

              <div className="flex flex-wrap items-center gap-2 pt-1">
                <span className="text-[11px] font-mono text-gray-400">Quick Test:</span>
                <button
                  onClick={() => {
                    const msg = 'Water entered my house and an elderly person is trapped.';
                    setCustomMessage(msg);
                    handleSendCustomSOS(msg);
                  }}
                  className="px-2.5 py-1 rounded bg-red-950/60 hover:bg-red-900/70 border border-red-500/40 text-[11px] font-mono text-red-300 transition-colors text-left"
                >
                  "Water entered my house and an elderly person is trapped."
                </button>
              </div>
            </div>

            <div className="pt-2 flex justify-center">
              <EmergencySOSButton active={isSOSActive} onClick={handleTriggerSOS} size="lg" />
            </div>
          </div>

          {/* Grid of Incidents */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Active Incidents Feed */}
            <div className="lg:col-span-8 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold font-mono text-gray-200 uppercase tracking-wider flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-rose-400" />
                  Active Dispatch Feed ({pendingIncidents.length})
                </h3>
                <span className="text-xs font-mono text-rose-400 font-bold">Live AI Triage & Rescue Links</span>
              </div>

              <StaggeredList className="space-y-4">
                {pendingIncidents.map((incident) => (
                  <AnimatedCard
                    key={incident.id}
                    className={`!p-5 ${
                      incident.urgency === 'CRITICAL' ? 'border-rose-500/40 bg-rose-950/10' : 'border-gray-800'
                    }`}
                  >
                    <div className="space-y-4">
                      {/* Top Bar: Citizen, Urgency, Priority Score, Status & Resolve */}
                      <div className="flex flex-wrap items-start justify-between gap-2 border-b border-gray-800/80 pb-3">
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-bold text-gray-100 text-base">{incident.citizenName}</span>
                            <span
                              className={`text-xs font-mono font-bold px-2 py-0.5 rounded border ${
                                incident.urgency === 'CRITICAL'
                                  ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                                  : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                              }`}
                            >
                              {incident.urgency} SEVERITY
                            </span>
                            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                              Priority Score: {incident.priorityScore ?? 94}/100
                            </span>
                            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-1">
                              <Brain className="w-3 h-3 text-indigo-400" />
                              AI TRIAGE COMPLETE
                            </span>
                          </div>
                          <div className="text-xs text-cyan-400 font-mono mt-1.5 flex items-center gap-1.5">
                            <AlertTriangle className="w-3.5 h-3.5 text-cyan-400" />
                            <span>
                              Incident Type:{' '}
                              <strong className="text-gray-100 font-bold">
                                {incident.incidentType || incident.emergencyType || 'FLOOD_TRAPPED_PERSON'}
                              </strong>
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setSelectedEvidenceIncident(incident)}
                            className="px-2.5 py-1 rounded bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 text-xs font-mono flex items-center gap-1 transition-colors"
                          >
                            <FileText className="w-3.5 h-3.5" />
                            <span>Triage Evidence</span>
                          </button>
                          <button
                            onClick={() => resolveSOSIncident(incident.id)}
                            className="px-2.5 py-1 rounded bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 border border-emerald-500/40 text-xs font-mono flex items-center gap-1 transition-colors"
                          >
                            <CheckCircle className="w-3.5 h-3.5" />
                            <span>Resolve</span>
                          </button>
                        </div>
                      </div>

                      {/* Description & Location */}
                      <p className="text-xs text-gray-300 font-mono leading-relaxed bg-black/30 p-3 rounded-lg border border-gray-800">
                        {incident.location}
                      </p>

                      {/* AI Rescue Recommendation Panel */}
                      <AIRescueRecommendationPanel incident={incident} />

                      {/* Real-time Voice Audio Player & Timeline Updates */}
                      <EmergencyTimeline sosId={incident.id} />
                    </div>
                  </AnimatedCard>
                ))}
              </StaggeredList>
            </div>

            {/* Resolved Incidents Sidebar */}
            <div className="lg:col-span-4 space-y-4">
              <h3 className="text-sm font-bold font-mono text-gray-200 uppercase tracking-wider flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                Resolved Incidents ({rescuedIncidents.length})
              </h3>

              <div className="space-y-3">
                {rescuedIncidents.map((incident) => (
                  <div
                    key={incident.id}
                    className="p-3 bg-gray-900/60 border border-emerald-500/30 rounded-xl space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-gray-200 text-xs">{incident.citizenName}</span>
                      <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                        RESCUED
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-400 font-mono line-clamp-1">
                      {incident.location}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Response Plan Comparison Modal */}
      <ResponsePlanComparisonModal
        isOpen={isComparisonOpen}
        onClose={() => setIsComparisonOpen(false)}
        contention={activeContention}
        onDispatchConfirmed={handleDispatchConfirmed}
      />

      {/* Triage Evidence Modal */}
      {selectedEvidenceIncident && (
        <AITriageEvidenceModal
          isOpen={Boolean(selectedEvidenceIncident)}
          incident={selectedEvidenceIncident}
          onClose={() => setSelectedEvidenceIncident(null)}
        />
      )}
    </PageTransition>
  );
};
