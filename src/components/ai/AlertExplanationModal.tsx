import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  X,
  Sparkles,
  AlertTriangle,
  Clock,
  MapPin,
  Users,
  Compass,
  CheckCircle2,
  ArrowRight,
  Bot,
  Activity,
} from 'lucide-react';
import { Alert } from '../../types/disaster';
import { explainAlertWithAI, AlertExplanationResponse } from '../../services/aiService';

interface AlertExplanationModalProps {
  alert: Alert | null;
  isOpen: boolean;
  onClose: () => void;
  onNavigateToAssistant?: () => void;
}

export const AlertExplanationModal: React.FC<AlertExplanationModalProps> = ({
  alert,
  isOpen,
  onClose,
  onNavigateToAssistant,
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [explanation, setExplanation] = useState<AlertExplanationResponse | null>(null);

  useEffect(() => {
    if (isOpen && alert) {
      setLoading(true);
      explainAlertWithAI({
        alert_id: alert.id,
        title: alert.title,
        category: alert.category,
        severity: alert.severity,
        location: alert.location,
        description: alert.description,
        affected_population: alert.affectedPopulation,
      })
        .then((res) => setExplanation(res))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    } else {
      setExplanation(null);
    }
  }, [isOpen, alert]);

  if (!isOpen || !alert) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-2xl max-h-[85vh] rounded-3xl border border-gray-700 bg-command-card flex flex-col overflow-hidden shadow-2xl">
        {/* Modal Header */}
        <div className="p-5 border-b border-gray-800 bg-gray-900/90 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 text-white shadow-lg">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-gray-100 flex items-center gap-2 font-mono">
                AI ALERT INTERPRETATION & EXPLANATION
              </h3>
              <p className="text-xs text-gray-400 font-mono">
                Translating Technical Sensor Telemetry into Plain Human Language
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-gray-400 hover:text-gray-100 hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Target Alert Meta Card */}
          <div className="p-4 rounded-2xl bg-gray-950 border border-gray-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-cyan-400 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                {alert.title}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                {alert.severity}
              </span>
            </div>
            <div className="flex items-center text-xs text-gray-400 space-x-4 font-mono">
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-gray-500" /> {alert.location}
              </span>
              <span className="flex items-center gap-1">
                <Users className="w-3.5 h-3.5 text-gray-500" /> {alert.affectedPopulation.toLocaleString()} affected
              </span>
            </div>
          </div>

          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-3 text-gray-400 text-xs font-mono">
              <Sparkles className="w-6 h-6 text-cyan-400 animate-spin" />
              <span>Analyzing hydrological models and generating clear instructions...</span>
            </div>
          ) : (
            explanation && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                {/* Plain English Summary */}
                <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-500/30 text-xs md:text-sm text-blue-200 leading-relaxed font-sans">
                  <strong className="text-cyan-300 font-mono text-xs block mb-1">
                    WHAT THIS MEANS FOR YOU:
                  </strong>
                  {explanation.plain_language_summary}
                </div>

                {/* Sensor Trigger Cause */}
                <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 space-y-1.5">
                  <div className="flex items-center space-x-2 text-xs font-mono font-semibold text-gray-300">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    <span>WHY THIS ALERT WAS TRIGGERED:</span>
                  </div>
                  <p className="text-xs text-gray-400 leading-relaxed pl-6">
                    {explanation.trigger_cause}
                  </p>
                </div>

                {/* Timeline */}
                <div className="p-4 rounded-xl bg-gray-900 border border-gray-800 space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-mono font-semibold text-gray-300">
                    <Clock className="w-4 h-4 text-amber-400" />
                    <span>PROJECTED ESCALATION TIMELINE:</span>
                  </div>
                  <div className="text-xs text-gray-300 font-mono whitespace-pre-line pl-6 leading-relaxed">
                    {explanation.danger_timeline}
                  </div>
                </div>

                {/* Immediate Actions */}
                <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-2.5">
                  <strong className="text-xs font-mono font-bold text-rose-300 block uppercase">
                    IMMEDIATE ACTIONS YOU SHOULD TAKE:
                  </strong>
                  <div className="space-y-1.5 pl-1">
                    {explanation.immediate_actions.map((act, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs text-gray-200">
                        <CheckCircle2 className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                        <span>{act}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Evacuation Advice */}
                <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-200">
                  <strong className="font-mono text-[11px] block text-amber-400 mb-1">
                    EVACUATION PROTOCOL:
                  </strong>
                  {explanation.evacuation_advice}
                </div>
              </motion.div>
            )
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-gray-800 bg-gray-900/60 flex items-center justify-between text-xs font-mono">
          <span className="text-gray-500 flex items-center gap-1">
            <Compass className="w-3.5 h-3.5 text-cyan-400" />
            Verified with GIS Spatial Polygons
          </span>

          {onNavigateToAssistant && (
            <button
              onClick={() => {
                onClose();
                onNavigateToAssistant();
              }}
              className="px-3 py-1.5 rounded-xl bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 border border-blue-500/40 flex items-center gap-1.5 transition-colors"
            >
              <Bot className="w-3.5 h-3.5" />
              <span>Ask AI Follow-up</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
