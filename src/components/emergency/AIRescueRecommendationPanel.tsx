import React, { useState, useEffect, useCallback } from 'react';
import {
  Navigation,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  Clock,
  Layers,
  CheckCircle,
  ExternalLink,
  Loader2,
  ChevronRight,
  Info,
} from 'lucide-react';
import {
  disasterService,
  BackendRescueRecommendation,
} from '../../services/disasterService';
import { SOSIncident } from '../../types/disaster';
import { RescueDispatchModal } from './RescueDispatchModal';

interface AIRescueRecommendationPanelProps {
  incident: SOSIncident;
  onDispatchSuccess?: (assignment: any) => void;
}

export const AIRescueRecommendationPanel: React.FC<AIRescueRecommendationPanelProps> = ({
  incident,
  onDispatchSuccess,
}) => {
  const [recommendation, setRecommendation] = useState<BackendRescueRecommendation | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const rawNum = incident.id.replace('sos-', '').replace('inc-', '');
  const incidentBackendId =
    incident.backendIncidentId ??
    (!isNaN(Number(rawNum)) ? Number(rawNum) : 1);

  const isDispatched =
    incident.status === 'DISPATCHED' ||
    incident.assignmentStatus === 'DISPATCHED';

  const fetchRecommendation = useCallback(async () => {
    if (isDispatched) return;
    setLoading(true);
    setError(null);
    try {
      const data = await disasterService.getRescueRecommendations(incidentBackendId);
      setRecommendation(data);
    } catch (err: any) {
      console.warn('[AIRescueRecommendationPanel] Error loading recommendation:', err);
      setError('Unable to load real-time rescue recommendation.');
    } finally {
      setLoading(false);
    }
  }, [incidentBackendId, isDispatched]);

  useEffect(() => {
    fetchRecommendation();
  }, [fetchRecommendation]);

  const handleConfirmDispatch = async (
    incId: number,
    rescueTeamId: number,
    notes?: string,
    isOverride?: boolean,
    overrideReason?: string
  ) => {
    const res = await disasterService.dispatchRescueTeam(
      {
        incident_id: incId,
        rescue_team_id: rescueTeamId,
        notes,
        is_override: isOverride,
        override_reason: overrideReason,
      },
      'demo-operator-token',
      'OPERATOR'
    );
    if (onDispatchSuccess) {
      onDispatchSuccess(res);
    }
  };

  // Case 1: Incident is already officially dispatched
  if (isDispatched) {
    return (
      <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/40 text-xs font-mono space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-emerald-300 font-bold text-[11px] uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Rescue Unit Dispatched • Human Confirmed</span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">
            EN ROUTE
          </span>
        </div>

        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="text-gray-100 font-bold text-sm">
              {incident.recommendedTeam || 'Assigned Rescue Squad'}
            </div>
            <div className="text-[11px] text-gray-400 mt-0.5">
              Approx. geographic distance: <strong className="text-gray-200">{incident.teamDistanceKm ?? 0.4} km</strong>
            </div>
          </div>
          {incident.dispatchedBy && (
            <div className="text-right text-[10px] text-gray-400">
              <span>Authorized by:</span>
              <div className="text-gray-200 font-bold">{incident.dispatchedBy}</div>
            </div>
          )}
        </div>

        {incident.isOverride && (
          <div className="p-2 rounded bg-amber-950/30 border border-amber-500/30 text-[10px] text-amber-300">
            <strong>Operator Override:</strong> {incident.overrideReason || 'Direct route choice'}
          </div>
        )}

        <div className="text-[10px] text-gray-500 border-t border-emerald-500/20 pt-1 flex items-center justify-between">
          <span>Straight-line distance. Road travel depends on flood depths.</span>
          <span className="text-emerald-400 font-bold">Live Tracking Active</span>
        </div>
      </div>
    );
  }

  // Case 2: Loading State
  if (loading) {
    return (
      <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 text-xs font-mono flex items-center justify-center space-x-2 text-indigo-300">
        <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
        <span>Evaluating Candidate Rescue Units...</span>
      </div>
    );
  }

  // Case 3: Error State
  if (error || !recommendation) {
    return (
      <div className="p-3.5 rounded-xl bg-indigo-950/20 border border-indigo-500/30 text-xs font-mono space-y-2">
        <div className="flex items-center justify-between text-indigo-300 text-[11px] font-bold">
          <span className="flex items-center gap-1.5 uppercase">
            <Navigation className="w-3.5 h-3.5" />
            Assigned Rescue Team
          </span>
          <button
            onClick={fetchRecommendation}
            className="text-[10px] text-indigo-400 hover:text-indigo-200 underline"
          >
            Retry AI Recommendation
          </button>
        </div>
        <div className="text-gray-100 font-bold text-sm">
          {incident.recommendedTeam || 'Water Rescue Squad Alpha'}
        </div>
        <div className="flex items-center justify-between text-[11px] text-gray-400">
          <span>Distance: Approx. {incident.teamDistanceKm ?? 0.4} km</span>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-2.5 py-1 rounded bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 text-[10px] font-bold"
          >
            Dispatch Barrier &rarr;
          </button>
        </div>
      </div>
    );
  }

  const primary = recommendation.primary_recommendation;

  // Case 4: No suitable team available
  if (recommendation.is_no_team_available || !primary) {
    return (
      <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/40 text-xs font-mono space-y-2">
        <div className="flex items-center gap-1.5 text-amber-300 font-bold text-[11px] uppercase">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span>No Suitable Rescue Unit Available</span>
        </div>
        <p className="text-[11px] text-gray-300">
          All rescue units with required capabilities are currently dispatched or out of range.
        </p>
        <button
          onClick={() => setIsModalOpen(true)}
          className="w-full py-1.5 px-3 rounded-lg bg-amber-600/30 hover:bg-amber-600/50 text-amber-200 border border-amber-500/40 text-[11px] font-bold flex items-center justify-center gap-1"
        >
          <span>Review All Teams & Manual Override</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
        <RescueDispatchModal
          incident={incident}
          recommendation={recommendation}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onConfirmDispatch={handleConfirmDispatch}
        />
      </div>
    );
  }

  // Case 5: AI Recommendation available — Operator Confirmation Required
  return (
    <div className="p-3.5 rounded-xl bg-indigo-950/25 border border-indigo-500/40 text-xs font-mono space-y-2.5 relative overflow-hidden">
      {/* Top Banner */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-indigo-300 font-bold text-[11px] uppercase">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>AI Rescue Recommendation</span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">
          {primary.score}/100 MATCH
        </span>
      </div>

      {/* Primary Candidate Summary */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="text-gray-100 font-bold text-sm flex items-center gap-2">
            <span>{primary.team_name}</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-gray-800 text-gray-400 font-normal">
              {primary.callsign}
            </span>
          </div>
          <div className="text-[11px] text-cyan-300 mt-0.5 flex items-center gap-1">
            <Navigation className="w-3 h-3 text-cyan-400" />
            <span>{primary.distance_label}: <strong>{primary.distance_km} km</strong></span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
            {primary.status}
          </span>
          <div className="text-[10px] text-gray-400 mt-1">
            Cap: {primary.capacity}
          </div>
        </div>
      </div>

      {/* Capabilities Badges */}
      <div className="flex flex-wrap gap-1">
        {primary.capabilities.slice(0, 3).map((cap) => (
          <span
            key={cap}
            className="text-[9px] px-1.5 py-0.5 rounded bg-gray-900 text-gray-300 border border-gray-800"
          >
            {cap}
          </span>
        ))}
      </div>

      {/* Top Reason */}
      {primary.reasons && primary.reasons.length > 0 && (
        <div className="text-[10px] text-gray-300 bg-black/30 p-1.5 rounded border border-gray-800/80 italic">
          "{primary.reasons[0]}"
        </div>
      )}

      {/* Action Buttons: Operator Confirmation Required */}
      <div className="flex items-center gap-2 pt-1 border-t border-indigo-500/20">
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex-1 py-1.5 px-2 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 text-[11px] font-bold flex items-center justify-center gap-1 transition-colors"
        >
          <span>Review Candidates ({recommendation.candidates.length})</span>
        </button>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex-1 py-1.5 px-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-[11px] flex items-center justify-center gap-1 shadow-md shadow-emerald-950/40 transition-colors"
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Confirm Dispatch</span>
        </button>
      </div>

      {/* Modal */}
      <RescueDispatchModal
        incident={incident}
        recommendation={recommendation}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirmDispatch={handleConfirmDispatch}
      />
    </div>
  );
};
