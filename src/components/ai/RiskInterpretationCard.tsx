import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles,
  TrendingUp,
  Activity,
  Layers,
  ShieldAlert,
  Droplets,
  Waves,
  Users,
  CheckCircle2,
  RefreshCw,
  Sliders,
} from 'lucide-react';
import { useDisaster } from '../../context/DisasterContext';
import { interpretRiskWithAI, RiskInterpretationResponse } from '../../services/aiService';

interface RiskInterpretationCardProps {
  onOpenAssistant?: () => void;
}

export const RiskInterpretationCard: React.FC<RiskInterpretationCardProps> = ({
  onOpenAssistant,
}) => {
  const { dashboardStats, aiPrediction } = useDisaster();
  const [loading, setLoading] = useState<boolean>(false);
  const [interpretation, setInterpretation] = useState<RiskInterpretationResponse | null>(null);

  const fetchInterpretation = () => {
    setLoading(true);
    interpretRiskWithAI({
      risk_score: aiPrediction?.riskScore ?? 84.0,
      rainfall_mm: dashboardStats.rainfallMm || 145.2,
      flood_probability: (dashboardStats.floodRiskPercent || 88) / 100,
      water_depth_m: 1.2,
      population_density: dashboardStats.affectedPopulation || 12000,
    })
      .then((res) => setInterpretation(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchInterpretation();
  }, [dashboardStats.rainfallMm, dashboardStats.floodRiskPercent]);

  return (
    <div className="glass-panel rounded-2xl p-6 border border-indigo-500/20 bg-gradient-to-br from-command-card via-gray-900 to-command-sidebar shadow-xl relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute -right-16 -top-16 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>

      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-4 mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-gray-100 font-mono flex items-center gap-2">
              AI RISK INTERPRETATION & PROGNOSIS
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-bold">
                0-100 COMPOSITE MODEL
              </span>
            </h3>
            <p className="text-xs text-gray-400 font-mono">
              Multi-Factor Hydrological Weighting & Real-Time Trajectory Analysis
            </p>
          </div>
        </div>

        <button
          onClick={fetchInterpretation}
          disabled={loading}
          className="p-2 rounded-xl bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-400 hover:text-indigo-300 transition-colors"
          title="Re-run AI Risk Interpretation"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading && !interpretation ? (
        <div className="py-8 flex flex-col items-center justify-center text-xs font-mono text-gray-400 space-y-2">
          <Sparkles className="w-5 h-5 text-indigo-400 animate-spin" />
          <span>Synthesizing multi-variate hydrological risk vectors...</span>
        </div>
      ) : (
        interpretation && (
          <div className="space-y-5">
            {/* Top Trajectory Banner */}
            <div className="p-3.5 rounded-xl bg-gradient-to-r from-rose-950/30 via-gray-900 to-indigo-950/20 border border-rose-500/30 flex items-start space-x-3">
              <TrendingUp className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <span className="text-[11px] font-mono font-bold text-rose-300 uppercase block tracking-wider">
                  2-HOUR TRAJECTORY PROGNOSIS:
                </span>
                <p className="text-xs text-gray-200 font-sans leading-relaxed">
                  {interpretation.trend_trajectory}
                </p>
              </div>
            </div>

            {/* AI Summary */}
            <p className="text-xs text-gray-300 leading-relaxed font-sans bg-gray-950/60 p-3.5 rounded-xl border border-gray-800">
              <strong className="text-indigo-300 font-mono block mb-1">AI Executive Diagnosis:</strong>
              {interpretation.summary}
            </p>

            {/* 4 Factor Breakdown Grid */}
            <div>
              <h4 className="text-xs font-mono font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-indigo-400" />
                Contributing Factor Weights:
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {interpretation.factor_breakdown.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-gray-900/80 border border-gray-800 space-y-2 hover:border-gray-700 transition-colors"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-gray-200">{item.factor}</span>
                      <span
                        className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                          item.status === 'CRITICAL' || item.status === 'DANGEROUS'
                            ? 'bg-rose-500/20 text-rose-400'
                            : 'bg-indigo-500/20 text-indigo-300'
                        }`}
                      >
                        {item.status}
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-gray-950 h-2 rounded-full overflow-hidden border border-gray-800">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500"
                        style={{ width: `${(item.contribution_percent / item.weight) * 100}%` }}
                      ></div>
                    </div>

                    <div className="flex items-center justify-between text-[11px] font-mono text-gray-400">
                      <span>Weight: {item.weight}%</span>
                      <span className="text-indigo-400 font-bold">
                        Contribution: {item.contribution_percent}%
                      </span>
                    </div>

                    <p className="text-[11px] text-gray-400 leading-normal">{item.detail}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Tactical Actions for Responders */}
            <div className="p-4 rounded-xl bg-gray-950 border border-gray-800 space-y-2">
              <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider block flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
                AI Recommended Tactical Response Actions:
              </span>
              <div className="space-y-1.5 pl-1">
                {interpretation.recommended_tactical_actions.map((act, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-gray-300">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{act}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Actions */}
            {onOpenAssistant && (
              <div className="pt-2 flex justify-end">
                <button
                  onClick={onOpenAssistant}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-mono text-xs font-bold flex items-center gap-2 shadow-lg transition-all"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Consult Emergency AI Assistant</span>
                </button>
              </div>
            )}
          </div>
        )
      )}
    </div>
  );
};
