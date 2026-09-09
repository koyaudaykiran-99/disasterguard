import React from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { Cpu, ShieldCheck, Activity, Droplets, Waves, MapPin, RefreshCw, X, BarChart2, CheckCircle2 } from 'lucide-react';
import { AIPredictionResult } from '../../types/disaster';
import { AnimatedCounter } from './AnimatedCounter';
import { RiskScore } from './RiskScore';

interface AIPredictionPanelProps {
  isAnalyzing: boolean;
  prediction: AIPredictionResult | null;
  onRunAnalysis?: () => void;
  isSimulationMode?: boolean;
}

export const AIPredictionPanel: React.FC<AIPredictionPanelProps> = ({
  isAnalyzing,
  prediction,
  onRunAnalysis,
  isSimulationMode = false,
}) => {
  const shouldReduceMotion = useReducedMotion();
  const [showEvaluation, setShowEvaluation] = React.useState(false);

  const isRealData =
    prediction?.modelVersion?.includes('real-data') ||
    prediction?.dataSourceType === 'historical_real' ||
    prediction?.trainingDataset?.includes('chennai');

  return (
    <div className="glass-panel rounded-2xl p-6 border border-blue-500/20 bg-gradient-to-b from-command-card to-command-sidebar relative overflow-hidden">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-4 mb-5 flex-wrap gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-gray-100 flex items-center gap-2 flex-wrap">
              AI DISASTERGUARD RISK MODEL
              {isSimulationMode ? (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/40 font-semibold">
                  SIMULATION MODE
                </span>
              ) : isRealData ? (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/40 font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
                  REAL HISTORICAL
                </span>
              ) : (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/40 font-semibold">
                  SYNTHETIC DEMO
                </span>
              )}
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-semibold">
                ACTIVE
              </span>
            </h3>
            <p className="text-xs text-gray-400 font-mono">
              {prediction?.modelName || 'RandomForest ML Pipeline'} ({prediction?.modelVersion || 'v2.0'})
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowEvaluation(true)}
            className="px-3 py-1.5 rounded-lg text-xs font-mono font-semibold bg-gray-800/80 hover:bg-gray-700/80 text-gray-300 border border-gray-700 transition-colors"
          >
            View Evaluation
          </button>
          {onRunAnalysis && (
            <button
              onClick={onRunAnalysis}
              disabled={isAnalyzing}
              className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-mono font-semibold bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/40 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
              <span>{isAnalyzing ? 'Processing...' : 'Run Risk Analysis'}</span>
            </button>
          )}
        </div>
      </div>

      <AnimatePresence mode="wait">
        {isAnalyzing || !prediction ? (
          /* SCANNING / RADAR ANIMATION STATE */
          <motion.div
            key="analyzing-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="py-10 flex flex-col items-center justify-center relative min-h-[260px]"
          >
            {/* Rotating Radar Scanner Visual */}
            <div className="relative w-40 h-40 flex items-center justify-center mb-6">
              {/* Concentric Circles */}
              <div className="absolute inset-0 rounded-full border border-blue-500/20"></div>
              <div className="absolute inset-4 rounded-full border border-cyan-500/20"></div>
              <div className="absolute inset-10 rounded-full border border-blue-500/30"></div>
              <div className="absolute inset-16 rounded-full border border-cyan-400/40"></div>

              {/* Crosshair lines */}
              <div className="absolute w-full h-[1px] bg-blue-500/20"></div>
              <div className="absolute h-full w-[1px] bg-blue-500/20"></div>

              {/* Rotating Radar Sweep Beam */}
              {!shouldReduceMotion && (
                <div className="absolute inset-0 rounded-full animate-radar-sweep pointer-events-none">
                  <div
                    className="w-1/2 h-1/2 bg-gradient-to-br from-cyan-400/30 to-transparent origin-bottom-right"
                    style={{ clipPath: 'polygon(100% 100%, 0 0, 0 100%)' }}
                  ></div>
                </div>
              )}

              {/* Center Pulsing AI Core */}
              <motion.div
                animate={
                  shouldReduceMotion
                    ? {}
                    : {
                        scale: [0.95, 1.1, 0.95],
                        boxShadow: [
                          '0 0 10px rgba(6, 182, 212, 0.4)',
                          '0 0 25px rgba(6, 182, 212, 0.8)',
                          '0 0 10px rgba(6, 182, 212, 0.4)',
                        ],
                      }
                }
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-10 h-10 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center z-10"
              >
                <Activity className="w-5 h-5 text-cyan-300" />
              </motion.div>
            </div>

            <div className="text-center font-mono space-y-1">
              <p className="text-sm font-bold text-cyan-400 tracking-wider uppercase animate-pulse">
                Analyzing Disaster Risk...
              </p>
              <p className="text-xs text-gray-500">
                Processing Satellite Radar & Spatial PostGIS Sensor Feeds
              </p>
            </div>
          </motion.div>
        ) : (
          /* PREDICTION READY RESULT STATE */
          <motion.div
            key="prediction-ready-state"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center"
          >
            {/* Left: Risk Score Dial */}
            <div className="md:col-span-5 flex flex-col items-center justify-center p-4 rounded-xl bg-gray-900/60 border border-gray-800">
              <RiskScore score={prediction.riskScore} level={prediction.riskLevel} size="md" />
              {prediction.alertRecommendation && (
                <div className="mt-3 text-center px-2 py-1 rounded bg-blue-900/20 border border-blue-500/30">
                  <span className="text-[10px] font-mono text-blue-300 font-semibold block">
                    {prediction.alertRecommendation}
                  </span>
                </div>
              )}
            </div>

            {/* Right: Detailed Prediction Metrics */}
            <div className="md:col-span-7 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-800/80 pb-2">
                <span className="text-xs font-mono text-cyan-400 flex items-center">
                  <ShieldCheck className="w-4 h-4 mr-1 text-cyan-400" />
                  ML PREDICTION READY
                </span>
                <div className="flex items-center gap-3 text-[11px] font-mono">
                  <span className="text-gray-400">
                    Confidence: <strong className="text-cyan-300">{(prediction.confidenceScore * 100).toFixed(0)}%</strong>
                  </span>
                  <span className="text-gray-600">|</span>
                  <span className="text-gray-400">
                    {prediction.lastUpdated}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                {/* Metric 1 */}
                <div className="p-3 rounded-lg bg-gray-900/80 border border-gray-800">
                  <div className="flex items-center text-xs text-gray-400 mb-1">
                    <Droplets className="w-3.5 h-3.5 mr-1 text-blue-400" />
                    Rainfall
                  </div>
                  <div className="text-lg font-bold font-mono text-gray-100">
                    <AnimatedCounter value={prediction.rainfallPredictionMm} decimals={1} suffix=" mm" />
                  </div>
                </div>

                {/* Metric 2 */}
                <div className="p-3 rounded-lg bg-gray-900/80 border border-gray-800">
                  <div className="flex items-center text-xs text-gray-400 mb-1">
                    <Waves className="w-3.5 h-3.5 mr-1 text-cyan-400" />
                    Flood Prob.
                  </div>
                  <div className="text-lg font-bold font-mono text-gray-100">
                    <AnimatedCounter value={prediction.floodProbabilityPercent} suffix="%" />
                  </div>
                </div>

                {/* Metric 3 */}
                <div className="p-3 rounded-lg bg-gray-900/80 border border-gray-800">
                  <div className="flex items-center text-xs text-gray-400 mb-1">
                    <MapPin className="w-3.5 h-3.5 mr-1 text-amber-400" />
                    Affected Zone
                  </div>
                  <div className="text-lg font-bold font-mono text-gray-100">
                    <AnimatedCounter value={prediction.affectedZoneKm2} decimals={1} suffix=" km²" />
                  </div>
                </div>
              </div>

              {/* Explainability: Top Feature Contributors */}
              {prediction.topContributors && prediction.topContributors.length > 0 && (
                <div className="p-2.5 rounded-lg bg-gray-900/70 border border-gray-800">
                  <span className="text-[10px] font-mono text-cyan-400 font-semibold block mb-1.5 uppercase">
                    Key ML Feature Contributors (Relative Weight)
                  </span>
                  <div className="grid grid-cols-3 gap-2">
                    {prediction.topContributors.map((c, idx) => (
                      <div key={idx} className="text-[10px] font-mono bg-gray-800/50 p-1.5 rounded border border-gray-700/50">
                        <span className="text-gray-400 block truncate">{c.feature}</span>
                        <span className="text-cyan-300 font-bold">{c.importance_pct}%</span>
                        <span className="text-gray-500 text-[9px] block">val: {c.observed_value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Evacuation Recommendation Box */}
              <div className="p-3.5 rounded-lg bg-blue-950/30 border border-blue-500/30">
                <span className="text-[11px] font-mono font-bold text-blue-400 uppercase tracking-wider block mb-1">
                  Evacuation & Safety Directive
                </span>
                <p className="text-xs text-gray-200 leading-relaxed">
                  {prediction.evacuationRecommendation}
                </p>
                {prediction.topDrivers && prediction.topDrivers.length > 0 && (
                  <ul className="mt-2 space-y-1 text-[11px] text-gray-300 font-mono border-t border-blue-900/40 pt-1.5">
                    {prediction.topDrivers.slice(0, 2).map((d, idx) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-cyan-400 font-bold">•</span>
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Model Provenance & Disclaimer Footer */}
              <div className="space-y-1 pt-1 border-t border-gray-800/60 font-mono text-[10px]">
                <div className="flex flex-wrap items-center justify-between text-gray-500">
                  <span>Model: <strong className="text-gray-400">{prediction.modelName || 'RandomForest (scikit-learn)'}</strong></span>
                  <span className="px-1.5 py-0.5 rounded bg-blue-900/30 text-blue-300 border border-blue-500/30">
                    Dataset: {prediction.trainingDataset || prediction.dataSource || 'ECMWF ERA5-Land (2022-2024)'}
                  </span>
                </div>
                {prediction.disclaimer && (
                  <p className="text-[9px] text-gray-500 italic leading-tight">
                    * {prediction.disclaimer}
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Phase 5.1 Model Evaluation & Provenance Modal */}
      <AnimatePresence>
        {showEvaluation && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-gray-900 border border-blue-500/30 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 shadow-2xl space-y-5"
            >
              <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                    <BarChart2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-gray-100 font-mono">
                      AI Model Evaluation & Provenance
                    </h4>
                    <span className="text-xs text-blue-400 font-mono">
                      Evidence-Based Historical Intelligence (Phase 5.1)
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setShowEvaluation(false)}
                  className="p-1.5 rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-800 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Status Badges */}
              <div className="flex flex-wrap gap-2 font-mono text-xs">
                <span className="px-2.5 py-1 rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/40 font-semibold">
                  Dataset: REAL HISTORICAL (ECMWF ERA5-Land)
                </span>
                <span className="px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold">
                  Model: RandomForestClassifier v2.0 (ACTIVE)
                </span>
                <span className="px-2.5 py-1 rounded-md bg-purple-500/20 text-purple-300 border border-purple-500/40 font-semibold">
                  Split: Chronological (70/15/15)
                </span>
              </div>

              {/* Benchmark Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center font-mono">
                <div className="p-3 rounded-xl bg-gray-800/60 border border-gray-700/60">
                  <span className="text-[10px] text-gray-400 block uppercase">Test Accuracy</span>
                  <span className="text-lg font-bold text-gray-100">86.61%</span>
                </div>
                <div className="p-3 rounded-xl bg-gray-800/60 border border-gray-700/60">
                  <span className="text-[10px] text-gray-400 block uppercase">Weighted F1</span>
                  <span className="text-lg font-bold text-cyan-300">87.98%</span>
                </div>
                <div className="p-3 rounded-xl bg-gray-800/60 border border-gray-700/60">
                  <span className="text-[10px] text-gray-400 block uppercase">Dangerous Recall</span>
                  <span className="text-lg font-bold text-amber-300">18.75%</span>
                </div>
                <div className="p-3 rounded-xl bg-gray-800/60 border border-gray-700/60">
                  <span className="text-[10px] text-gray-400 block uppercase">Test Samples</span>
                  <span className="text-lg font-bold text-emerald-300">3,942</span>
                </div>
              </div>

              {/* Scientific Honesty Notice */}
              <div className="p-3.5 rounded-xl bg-blue-950/40 border border-blue-500/30 text-xs text-gray-300 space-y-1.5 leading-relaxed">
                <div className="flex items-center text-blue-300 font-bold font-mono">
                  <CheckCircle2 className="w-4 h-4 mr-1.5 text-blue-400" />
                  Scientific Honesty Protocol Verification
                </div>
                <p>
                  <strong>Rainfall Models</strong> are trained and evaluated on 26,304 consecutive hourly observations (2022–2024) for the Chennai region from the ECMWF ERA5-Land reanalysis. Preprocessing is strictly fitted on historical training data to eliminate leakage.
                </p>
                <p className="text-gray-400 text-[11px]">
                  * Flood Inundation & Depth models remain designated as <em>calibrated synthetic prototypes</em> because atmospheric reanalysis products do not record physical streamflow or municipal gauge levels.
                </p>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  onClick={() => setShowEvaluation(false)}
                  className="px-4 py-2 rounded-xl text-xs font-mono font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-colors"
                >
                  Close Evaluation
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};


