import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  Radio,
  Navigation,
  Check,
  X,
  UserCheck,
  Loader2,
  Info,
} from 'lucide-react';
import {
  BackendRescueRecommendation,
} from '../../services/disasterService';
import { SOSIncident } from '../../types/disaster';

interface RescueDispatchModalProps {
  incident: SOSIncident;
  recommendation: BackendRescueRecommendation | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirmDispatch: (
    incidentId: number,
    rescueTeamId: number,
    notes?: string,
    isOverride?: boolean,
    overrideReason?: string
  ) => Promise<void>;
}

export const RescueDispatchModal: React.FC<RescueDispatchModalProps> = ({
  incident,
  recommendation,
  isOpen,
  onClose,
  onConfirmDispatch,
}) => {
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [overrideReason, setOverrideReason] = useState<string>('');
  const [dispatchNotes, setDispatchNotes] = useState<string>('');
  const [operatorConfirmed, setOperatorConfirmed] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const primaryCandidate = recommendation?.primary_recommendation;

  useEffect(() => {
    if (isOpen && primaryCandidate) {
      setSelectedTeamId(primaryCandidate.team_id);
      setOverrideReason('');
      setDispatchNotes('');
      setOperatorConfirmed(false);
      setErrorMessage(null);
    }
  }, [isOpen, primaryCandidate]);

  if (!isOpen) return null;

  const isOverride =
    Boolean(primaryCandidate) && selectedTeamId !== primaryCandidate?.team_id;

  const selectedCandidate = recommendation?.candidates.find(
    (c) => c.team_id === selectedTeamId
  );

  const rawNum = incident.id.replace('sos-', '').replace('inc-', '');
  const incidentBackendId =
    incident.backendIncidentId ??
    (!isNaN(Number(rawNum)) ? Number(rawNum) : 1);

  const handleDispatch = async () => {
    if (!selectedTeamId) {
      setErrorMessage('Please select a rescue team to dispatch.');
      return;
    }
    if (isOverride && !overrideReason.trim()) {
      setErrorMessage('Please specify an operational reason for operator override.');
      return;
    }
    if (!operatorConfirmed) {
      setErrorMessage('You must check the confirmation barrier to authorize this dispatch.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await onConfirmDispatch(
        incidentBackendId,
        selectedTeamId,
        dispatchNotes.trim() || undefined,
        isOverride,
        isOverride ? overrideReason.trim() : undefined
      );
      onClose();
    } catch (err: any) {
      setErrorMessage(err.message || 'Dispatch transaction failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-command-card border border-gray-700/80 rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between bg-gray-950/70">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              <Radio className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h3 className="text-base font-bold text-gray-100 flex items-center gap-2 font-mono">
                OPERATOR RESCUE TEAM DISPATCH BARRIER
              </h3>
              <p className="text-xs text-gray-400 font-mono">
                Incident #{incidentBackendId} • {incident.incidentType || incident.emergencyType || 'EMERGENCY_DISTRESS'} • Urgency: {incident.urgency}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-200 p-1.5 rounded-lg hover:bg-gray-800/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs font-mono">
          {/* Incident Distress Overview */}
          <div className="bg-gray-950/80 p-3.5 rounded-xl border border-gray-800 space-y-1.5">
            <div className="flex items-center justify-between text-gray-400 text-[11px]">
              <span>Citizen: <strong className="text-gray-200">{incident.citizenName}</strong></span>
              <span>Distress Coordinates: <strong className="text-cyan-400">[{incident.coordinates[0].toFixed(4)}, {incident.coordinates[1].toFixed(4)}]</strong></span>
            </div>
            <p className="text-gray-300 text-xs italic bg-gray-900/60 p-2 rounded border border-gray-800/80">
              "{incident.location}"
            </p>
          </div>

          {/* Candidates Selection List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5">
                <Navigation className="w-4 h-4 text-cyan-400" />
                Ranked Rescue Candidates ({recommendation?.candidates.length || 0})
              </span>
              <span className="text-[10px] text-gray-500">Ranked by Availability, Capabilities & Distance</span>
            </div>

            {recommendation?.candidates.map((cand) => {
              const isSelected = selectedTeamId === cand.team_id;
              const isPrimary = primaryCandidate?.team_id === cand.team_id;

              return (
                <div
                  key={cand.team_id}
                  onClick={() => setSelectedTeamId(cand.team_id)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2.5 ${
                    isSelected
                      ? 'border-indigo-500 bg-indigo-950/30 ring-1 ring-indigo-500/50'
                      : 'border-gray-800 bg-gray-950/40 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2.5">
                      <div
                        className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                          isSelected
                            ? 'border-indigo-400 bg-indigo-600'
                            : 'border-gray-600 bg-gray-800'
                        }`}
                      >
                        {isSelected && <Check className="w-3 h-3 text-white" />}
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-gray-100 font-sans">{cand.team_name}</span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 font-mono">
                            {cand.callsign}
                          </span>
                          {isPrimary && (
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">
                              AI PRIMARY CHOICE
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-gray-400">
                          Status: <strong className={cand.status === 'AVAILABLE' ? 'text-emerald-400' : 'text-amber-400'}>{cand.status}</strong> • Capacity: {cand.capacity} responders
                        </span>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-xs font-bold text-indigo-300 bg-indigo-500/20 px-2 py-0.5 rounded border border-indigo-500/30">
                        Score: {cand.score}/100
                      </div>
                      <div className="text-[10px] text-gray-400 mt-1">
                        Rank #{cand.rank}
                      </div>
                    </div>
                  </div>

                  {/* Capabilities Tags */}
                  <div className="flex flex-wrap gap-1 pt-1">
                    {cand.capabilities.map((cap) => (
                      <span
                        key={cap}
                        className="text-[9px] px-1.5 py-0.5 rounded bg-gray-800/80 text-cyan-300 border border-gray-700"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>

                  {/* Distance & Transparency Warning */}
                  <div className="text-[11px] text-gray-400 flex items-center justify-between border-t border-gray-800/80 pt-2">
                    <span className="flex items-center gap-1 text-cyan-300">
                      <Navigation className="w-3 h-3 text-cyan-400" />
                      {cand.distance_label}: <strong>{cand.distance_km} km</strong>
                    </span>
                    {cand.is_stale_location && (
                      <span className="flex items-center gap-1 text-amber-400 text-[10px] bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/30">
                        <AlertTriangle className="w-3 h-3" />
                        Location &gt;15m stale
                      </span>
                    )}
                  </div>

                  {/* Reasons Breakdown */}
                  <div className="bg-black/30 p-2 rounded-lg space-y-1 text-[10px] text-gray-400">
                    {cand.reasons.map((r, idx) => (
                      <div key={idx} className="flex items-start gap-1.5">
                        <span className="text-indigo-400 mt-0.5">•</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Distance Disclaimer Note */}
          <div className="flex items-start gap-2 p-2.5 rounded-lg bg-blue-950/20 border border-blue-500/20 text-[11px] text-blue-300">
            <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <span>
              <strong>Transparency Notice:</strong> Distances shown are approximate geodesic straight-line spans. Actual road navigation times will fluctuate depending on street-level flood inundation, road barriers, and debris.
            </span>
          </div>

          {/* Operator Override Input (If selecting candidate other than primary) */}
          {isOverride && (
            <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/40 space-y-2.5 animate-fadeIn">
              <div className="flex items-center gap-2 text-amber-300 font-bold">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>OPERATOR OVERRIDE REQUIRED</span>
              </div>
              <p className="text-[11px] text-gray-300">
                You have selected an alternate rescue team ({selectedCandidate?.team_name}) instead of the AI primary recommendation ({primaryCandidate?.team_name}). Please state the operational justification for this override to be logged in the immutable audit trail.
              </p>
              <textarea
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                placeholder="E.g., North bridge submerged, squad Alpha blocked; squad Beta has direct amphibious approach..."
                rows={2}
                className="w-full bg-gray-950 border border-amber-500/40 rounded-lg p-2.5 text-xs font-mono text-gray-100 placeholder-gray-500 focus:outline-none focus:border-amber-400"
              />
            </div>
          )}

          {/* Dispatch Notes (Optional) */}
          <div className="space-y-1.5">
            <label className="text-[11px] text-gray-400 block font-bold">
              Dispatch Instructions / Field Notes (Optional)
            </label>
            <input
              type="text"
              value={dispatchNotes}
              onChange={(e) => setDispatchNotes(e.target.value)}
              placeholder="E.g., Approach from elevated northern embankment, bring life vests for elderly person"
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs font-mono text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Human Confirmation Barrier */}
          <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 space-y-3">
            <div className="flex items-center gap-2 text-rose-300 font-bold text-xs uppercase">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <span>Human Operator Confirmation Barrier</span>
            </div>

            <p className="text-[11px] text-gray-300 leading-relaxed font-sans">
              <strong>CRITICAL SAFETY MANDATE:</strong> AI agents are strictly prohibited from dispatching rescue units autonomously. Only certified human command operators can deploy emergency responders. By checking below, you assume operational responsibility for this dispatch.
            </p>

            <label className="flex items-start gap-2.5 cursor-pointer pt-1">
              <input
                type="checkbox"
                checked={operatorConfirmed}
                onChange={(e) => setOperatorConfirmed(e.target.checked)}
                className="mt-0.5 rounded border-gray-700 bg-gray-900 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-[11px] text-gray-200 select-none">
                I confirm that I am an authorized command operator, have reviewed the situational risks, and officially deploy this rescue team.
              </span>
            </label>
          </div>

          {/* Error Message */}
          {errorMessage && (
            <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/50 text-red-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-gray-800 flex items-center justify-between bg-gray-950/70">
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-xl text-xs font-mono font-semibold bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={handleDispatch}
            disabled={isSubmitting || !operatorConfirmed}
            className={`px-5 py-2 rounded-xl text-xs font-mono font-bold flex items-center gap-2 transition-all ${
              isSubmitting || !operatorConfirmed
                ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-950/40'
            }`}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Authorizing & Dispatching...</span>
              </>
            ) : (
              <>
                <UserCheck className="w-4 h-4" />
                <span>Confirm & Dispatch Unit</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
