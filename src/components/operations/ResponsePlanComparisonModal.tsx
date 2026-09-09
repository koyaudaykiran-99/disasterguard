import React, { useState } from 'react';
import {
  X,
  Shield,
  Truck,
  CheckCircle,
  AlertTriangle,
  Clock,
  MapPin,
  Award,
  Zap,
  Lock,
  ArrowRight
} from 'lucide-react';
import { ResourceContention, ResponseOption } from '../../types/situationalAwareness';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  contention: ResourceContention | null;
  onDispatchConfirmed: (incidentId: number, teamId: number, notes: string, isOverride: boolean) => Promise<void>;
}

export const ResponsePlanComparisonModal: React.FC<Props> = ({
  isOpen,
  onClose,
  contention,
  onDispatchConfirmed
}) => {
  const [selectedOption, setSelectedOption] = useState<'A' | 'B'>('A');
  const [overrideReason, setOverrideReason] = useState<string>('');
  const [operatorNotes, setOperatorNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen || !contention) return null;

  const isOverride = selectedOption === 'B';

  const handleConfirm = async () => {
    if (isOverride && !overrideReason.trim()) {
      setErrorMsg('Mandatory override reason required when selecting alternative Option B.');
      return;
    }

    const team = selectedOption === 'A' ? contention.optionA : contention.optionB;
    if (!team.teamId) {
      setErrorMsg('Selected team has invalid identifier.');
      return;
    }

    try {
      setSubmitting(true);
      setErrorMsg(null);
      const fullNotes = isOverride
        ? `[OPERATOR_OVERRIDE]: ${overrideReason} | ${operatorNotes}`
        : `[OPERATOR_CONFIRMED]: ${operatorNotes || 'Confirmed recommended Option A'}`;

      await onDispatchConfirmed(contention.incidentId, team.teamId, fullNotes, isOverride);
      onClose();
    } catch (err: any) {
      setErrorMsg(err?.message || 'Dispatch confirmation failed.');
    } finally {
      setSubmitting(false);
    }
  };

  const renderOptionCard = (option: ResponseOption, type: 'A' | 'B') => {
    const isSelected = selectedOption === type;
    const isRecommended = type === 'A';

    return (
      <div
        onClick={() => setSelectedOption(type)}
        className={`cursor-pointer rounded-xl border p-5 transition-all relative ${
          isSelected
            ? 'bg-slate-900 border-blue-500 shadow-lg shadow-blue-500/10 ring-2 ring-blue-500/40'
            : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 opacity-80'
        }`}
      >
        {isRecommended && (
          <div className="absolute -top-3 left-4 bg-emerald-500 text-slate-950 font-black text-[10px] uppercase tracking-wider px-2.5 py-0.5 rounded-full shadow">
            Primary Recommended
          </div>
        )}
        {!isRecommended && (
          <div className="absolute -top-3 left-4 bg-indigo-500 text-white font-bold text-[10px] uppercase tracking-wider px-2.5 py-0.5 rounded-full shadow">
            Alternative Strategic Option
          </div>
        )}

        <div className="flex items-start justify-between mt-1">
          <div>
            <h4 className="text-base font-bold text-white flex items-center space-x-2">
              <span>Option {type}:</span>
              <span className="text-blue-400">{option.teamName || 'Squad Team'}</span>
            </h4>
            <p className="text-xs text-slate-400 mt-0.5">
              Type: {option.teamType}
            </p>
          </div>
          <div className="text-right">
            <span className="text-2xl font-black font-mono text-white">
              {Math.round(option.capabilityMatchScore * 100)}%
            </span>
            <div className="text-[10px] text-slate-400 uppercase">Match Score</div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-3 gap-2 mt-4 bg-slate-950/80 p-3 rounded-lg border border-slate-800/80 text-center">
          <div>
            <span className="text-slate-400 text-[10px] block uppercase">Distance</span>
            <span className="text-sm font-bold text-slate-200 font-mono">
              {option.distanceKm.toFixed(1)} km
            </span>
          </div>
          <div>
            <span className="text-slate-400 text-[10px] block uppercase">Est. Arrival</span>
            <span className="text-sm font-bold text-amber-400 font-mono">
              {Math.round(option.estimatedArrivalMinutes)} min
            </span>
          </div>
          <div>
            <span className="text-slate-400 text-[10px] block uppercase">Workload</span>
            <span className="text-sm font-bold text-slate-200 font-mono">
              {option.currentWorkload} active
            </span>
          </div>
        </div>

        {/* Advantages */}
        <div className="mt-3">
          <span className="text-[11px] font-semibold text-emerald-400 flex items-center space-x-1">
            <Award className="w-3.5 h-3.5" />
            <span>Operational Advantages:</span>
          </span>
          <ul className="text-xs text-slate-300 list-disc list-inside mt-1 space-y-0.5">
            {option.advantages?.length > 0 ? (
              option.advantages.map((adv, i) => <li key={i}>{adv}</li>)
            ) : (
              <li>Optimized response metrics</li>
            )}
          </ul>
        </div>

        {/* Warnings */}
        {option.warnings && option.warnings.length > 0 && (
          <div className="mt-2.5 bg-amber-500/10 border border-amber-500/20 rounded p-2 text-xs text-amber-300">
            <div className="flex items-center space-x-1 font-semibold text-[11px] text-amber-400">
              <AlertTriangle className="w-3 h-3" />
              <span>Operational Advisory:</span>
            </div>
            <ul className="list-disc list-inside mt-0.5 text-[11px] space-y-0.5">
              {option.warnings.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <Truck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white uppercase tracking-wider">
                  Resource Contention & Response Plan Review
                </h3>
                <span className="px-2 py-0.5 text-xs font-mono font-semibold rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  DECISION REQUIRED
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Target: <strong className="text-slate-200">{contention.incidentTitle}</strong> ({contention.location})
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Inviolate Safety Barrier Notice */}
        <div className="bg-emerald-950/30 border-b border-emerald-500/20 px-6 py-2.5 flex items-center space-x-2.5 text-xs text-emerald-300">
          <Shield className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>
            <strong>Safety Invariant Enforced:</strong> Automated engines only formulate recommendations. No unit is dispatched without explicit human operator confirmation.
          </span>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Contenders summary */}
          {contention.contenders && contention.contenders.length > 1 && (
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3.5">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Competing Incident Claims ({contention.contenders.length} emergencies requested this capability)
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                {contention.contenders.map((c, i) => (
                  <div key={i} className="text-xs p-2 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-200">{c.title}</span>
                    <span className="text-red-400 font-bold font-mono">{c.priority}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Option Cards Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {renderOptionCard(contention.optionA, 'A')}
            {renderOptionCard(contention.optionB, 'B')}
          </div>

          {/* Operator Decision Section */}
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-3">
            <h5 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
              <Lock className="w-3.5 h-3.5 text-blue-400" />
              <span>Operator Authorization & Audit Log</span>
            </h5>

            {isOverride && (
              <div>
                <label className="block text-xs font-semibold text-amber-400 mb-1">
                  Override Justification * (Mandatory for Option B selection)
                </label>
                <input
                  type="text"
                  placeholder="e.g., Tactical terrain constraint / Local road blockage along Option A route"
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  className="w-full bg-slate-900 border border-amber-500/50 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">
                Operator Tactical Notes (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g., Coordinate with Sector 4 liaison upon arrival"
                value={operatorNotes}
                onChange={(e) => setOperatorNotes(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            {errorMsg && (
              <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 p-2.5 rounded">
                {errorMsg}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-semibold transition"
          >
            Cancel / Defer
          </button>

          <div className="flex items-center space-x-3">
            <button
              type="button"
              onClick={handleConfirm}
              disabled={submitting}
              className={`px-5 py-2.5 rounded-lg text-xs font-bold flex items-center space-x-2 shadow-lg transition ${
                isOverride
                  ? 'bg-amber-600 hover:bg-amber-500 text-white shadow-amber-900/30'
                  : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/30'
              }`}
            >
              <CheckCircle className="w-4 h-4" />
              <span>
                {submitting
                  ? 'Verifying & Dispatching...'
                  : isOverride
                  ? 'Override & Dispatch Option B'
                  : 'Confirm & Dispatch Option A'}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
