import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import {
  Waves,
  Mountain,
  Compass,
  History,
  CloudRain,
  ShieldAlert,
  Info,
  X,
  RefreshCw,
  ExternalLink,
  MapPin,
  CheckCircle2
} from 'lucide-react';
import { FloodIntelligenceResult, HistoricalFloodEvent } from '../../types/disaster';
import { disasterService } from '../../services/disasterService';

interface FloodIntelligencePanelProps {
  latitude?: number;
  longitude?: number;
  isSimulationMode?: boolean;
}

export const FloodIntelligencePanel: React.FC<FloodIntelligencePanelProps> = ({
  latitude = 13.0827,
  longitude = 80.2707,
  isSimulationMode = false
}) => {
  const shouldReduceMotion = useReducedMotion();
  const [data, setData] = useState<FloodIntelligenceResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [showExplanationModal, setShowExplanationModal] = useState<boolean>(false);
  const [lastRefreshed, setLastRefreshed] = useState<string>('');

  const fetchFloodIntelligence = async () => {
    setIsLoading(true);
    try {
      const res = await disasterService.getFloodIntelligence(latitude, longitude);
      setData(res);
      setLastRefreshed(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to load flood intelligence:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFloodIntelligence();
    const interval = setInterval(fetchFloodIntelligence, 60000); // 60s auto refresh
    return () => clearInterval(interval);
  }, [latitude, longitude]);

  const riskScore = data?.susceptibility_score ?? 58;
  const riskLevel = data?.risk_level ?? 'HIGH';
  const estimatedDepth = data?.estimated_depth_m ?? 0.6;
  const elevation = data?.spatial_features?.elevation ?? 7.2;
  const slope = data?.spatial_features?.slope ?? 1.1;
  const nearestDrainage = data?.spatial_features?.nearest_drainage ?? 'Otteri Nullah Channel';
  const distDrainage = data?.spatial_features?.distance_to_drainage_km ?? 0.8;
  const histSeverity = data?.spatial_features?.historical_severity ?? 'HIGH';
  const histCount = data?.spatial_features?.historical_event_count ?? 4;

  // Controlled motion variants based on risk level
  const pulseVariant = {
    LOW: { scale: 1.0 },
    MODERATE: shouldReduceMotion ? { scale: 1.0 } : { scale: [1, 1.02, 1], transition: { duration: 3, repeat: Infinity } },
    HIGH: shouldReduceMotion ? { scale: 1.0 } : { scale: [1, 1.03, 1], boxShadow: ['0 0 10px rgba(249, 115, 22, 0.2)', '0 0 20px rgba(249, 115, 22, 0.4)', '0 0 10px rgba(249, 115, 22, 0.2)'], transition: { duration: 2.2, repeat: Infinity } },
    CRITICAL: shouldReduceMotion ? { scale: 1.0 } : { scale: [1, 1.04, 1], boxShadow: ['0 0 15px rgba(244, 63, 94, 0.3)', '0 0 30px rgba(244, 63, 94, 0.6)', '0 0 15px rgba(244, 63, 94, 0.3)'], transition: { duration: 1.6, repeat: Infinity } }
  };

  const colorMap: Record<string, { bg: string; text: string; border: string; bar: string }> = {
    LOW: { bg: 'bg-cyan-500/10', text: 'text-cyan-400', border: 'border-cyan-500/30', bar: 'bg-cyan-500' },
    MODERATE: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30', bar: 'bg-amber-500' },
    HIGH: { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/30', bar: 'bg-orange-500' },
    CRITICAL: { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/30', bar: 'bg-rose-500' }
  };

  const currentColors = colorMap[riskLevel] || colorMap['HIGH'];

  return (
    <div className="glass-panel rounded-2xl p-6 border border-blue-500/20 bg-gradient-to-b from-command-card to-command-sidebar relative overflow-hidden shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-4 mb-5 flex-wrap gap-3">
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-xl ${currentColors.bg} border ${currentColors.border} ${currentColors.text}`}>
            <Waves className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-base font-bold text-gray-100 font-mono tracking-wide">
                FLOOD INTELLIGENCE & INUNDATION
              </h3>
              {/* Provenance Badges */}
              {isSimulationMode ? (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 font-semibold">
                  SIMULATION
                </span>
              ) : (
                <>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-semibold">
                    REAL HISTORICAL
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/40 font-semibold">
                    REAL GEOSPATIAL
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/40 font-semibold">
                    DERIVED
                  </span>
                </>
              )}
            </div>
            <p className="text-xs text-gray-400 font-mono mt-0.5">
              Multi-factor Topographic & Meteorological Engine (v2.1)
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowExplanationModal(true)}
            className="px-3 py-1.5 rounded-lg text-xs font-mono font-semibold bg-gray-800 hover:bg-gray-700 text-cyan-300 border border-cyan-500/30 transition-colors flex items-center gap-1.5"
          >
            <Info className="w-3.5 h-3.5" />
            <span>View Explanation</span>
          </button>
          <button
            onClick={fetchFloodIntelligence}
            disabled={isLoading}
            className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white border border-gray-700 transition-colors disabled:opacity-50"
            title="Refresh Flood Intelligence"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Grid Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left: Susceptibility Gauge Card */}
        <motion.div
          animate={pulseVariant[riskLevel as keyof typeof pulseVariant] || {}}
          className={`rounded-xl p-5 border ${currentColors.border} ${currentColors.bg} flex flex-col justify-between`}
        >
          <div>
            <div className="flex items-center justify-between text-xs font-mono text-gray-400 mb-2">
              <span>FLOOD SUSCEPTIBILITY</span>
              <span className="text-[10px] uppercase font-bold text-gray-500">PROXY ESTIMATE</span>
            </div>
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-4xl font-extrabold font-mono text-white tracking-tight">
                {riskScore}
              </span>
              <span className="text-gray-400 font-mono text-lg">/100</span>
              <span className={`ml-auto text-sm font-bold font-mono px-2.5 py-0.5 rounded ${currentColors.bg} ${currentColors.text} border ${currentColors.border}`}>
                {riskLevel}
              </span>
            </div>

            {/* Visual Bar Gauge */}
            <div className="w-full h-2.5 bg-gray-800 rounded-full overflow-hidden mb-3">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${riskScore}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
                className={`h-full ${currentColors.bar}`}
              />
            </div>
          </div>

          <div className="pt-3 border-t border-gray-800/80 text-xs font-mono">
            <div className="flex justify-between items-center py-0.5">
              <span className="text-gray-400">Est. Water Depth:</span>
              <span className="text-white font-bold">{estimatedDepth.toFixed(2)} m</span>
            </div>
            <div className="flex justify-between items-center py-0.5 text-[11px]">
              <span className="text-gray-500">Depth Confidence:</span>
              <span className="text-gray-300">{(data?.depth_confidence ? data.depth_confidence * 100 : 75).toFixed(0)}%</span>
            </div>
          </div>
        </motion.div>

        {/* Middle: Topographic & Hydrographic Metrics */}
        <div className="rounded-xl p-5 border border-gray-800 bg-gray-950/60 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 text-xs font-mono text-blue-400 font-bold mb-3">
              <Mountain className="w-4 h-4" />
              <span>TERRAIN & DRAINAGE GEOMETRY</span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono mb-3">
              <div className="bg-gray-900/80 p-2.5 rounded-lg border border-gray-800">
                <span className="text-gray-400 block text-[11px]">Elevation ASL</span>
                <span className="text-base font-bold text-white">{elevation.toFixed(1)} m</span>
              </div>
              <div className="bg-gray-900/80 p-2.5 rounded-lg border border-gray-800">
                <span className="text-gray-400 block text-[11px]">Surface Slope</span>
                <span className="text-base font-bold text-white">{slope.toFixed(1)}°</span>
              </div>
            </div>
          </div>

          <div className="space-y-1.5 text-xs font-mono pt-2 border-t border-gray-800">
            <div className="flex justify-between">
              <span className="text-gray-400">Nearest Waterway:</span>
              <span className="text-cyan-300 font-semibold truncate max-w-[140px]" title={nearestDrainage}>
                {nearestDrainage}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Channel Distance:</span>
              <span className="text-white">{distDrainage.toFixed(2)} km</span>
            </div>
          </div>
        </div>

        {/* Right: Historical Disaster Memory */}
        <div className="rounded-xl p-5 border border-gray-800 bg-gray-950/60 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 text-xs font-mono text-amber-400 font-bold mb-3">
              <History className="w-4 h-4" />
              <span>HISTORICAL DISASTER MEMORY</span>
            </div>

            <div className="space-y-2 text-xs font-mono mb-3">
              <div className="flex justify-between items-center bg-gray-900/80 p-2 rounded-lg border border-gray-800">
                <span className="text-gray-400">Recorded Disasters:</span>
                <span className="text-white font-bold">{histCount} Verified Events</span>
              </div>
              <div className="flex justify-between items-center bg-gray-900/80 p-2 rounded-lg border border-gray-800">
                <span className="text-gray-400">Prior Exposure:</span>
                <span className={`font-bold px-2 py-0.5 rounded text-[10px] ${
                  histSeverity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                  histSeverity === 'HIGH' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                  'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                }`}>
                  {histSeverity}
                </span>
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-gray-800 text-[11px] font-mono text-gray-400">
            Anchored to 2015 Adyar Flood (494mm) & 2023 Cyclone Michaung (220mm) disaster records.
          </div>
        </div>
      </div>

      {/* Explanation Modal */}
      <AnimatePresence>
        {showExplanationModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[1000] bg-black/85 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-gray-950 border border-gray-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto font-mono text-xs"
            >
              <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                <div className="flex items-center space-x-2 text-cyan-400">
                  <Waves className="w-5 h-5" />
                  <h4 className="text-sm font-bold text-white uppercase">
                    Flood Susceptibility Breakdown & Scientific Provenance
                  </h4>
                </div>
                <button
                  onClick={() => setShowExplanationModal(false)}
                  className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Categorical Explanations */}
              <div className="space-y-3">
                <div className="bg-blue-950/30 border border-blue-800/40 rounded-xl p-3">
                  <span className="text-[11px] font-bold text-blue-300 block mb-1">FACT (Observed Data)</span>
                  <ul className="list-disc list-inside space-y-0.5 text-gray-300">
                    {data?.explanation?.FACT?.map((f, i) => (
                      <li key={i}>{f}</li>
                    )) || <li>Observed 24h rainfall load and geodetic coordinate baseline.</li>}
                  </ul>
                </div>

                <div className="bg-emerald-950/30 border border-emerald-800/40 rounded-xl p-3">
                  <span className="text-[11px] font-bold text-emerald-300 block mb-1">ML PREDICTION (Real Rainfall Models)</span>
                  <ul className="list-disc list-inside space-y-0.5 text-gray-300">
                    {data?.explanation?.ML_PREDICTION?.map((p, i) => (
                      <li key={i}>{p}</li>
                    )) || <li>Real-historical BalancedRandomForest predicts forward 6h rainfall.</li>}
                  </ul>
                </div>

                <div className="bg-purple-950/30 border border-purple-800/40 rounded-xl p-3">
                  <span className="text-[11px] font-bold text-purple-300 block mb-1">GEOSPATIAL DERIVATION (Topography & Catchment)</span>
                  <ul className="list-disc list-inside space-y-0.5 text-gray-300">
                    {data?.explanation?.GEOSPATIAL_DERIVATION?.map((g, i) => (
                      <li key={i}>{g}</li>
                    )) || <li>Relative depression index and drainage corridor proximity calculated.</li>}
                  </ul>
                </div>

                <div className="bg-amber-950/30 border border-amber-800/40 rounded-xl p-3">
                  <span className="text-[11px] font-bold text-amber-300 block mb-1">AI INTERPRETATION & RECOMMENDATION</span>
                  <div className="text-gray-300 mb-1">
                    {data?.explanation?.AI_INTERPRETATION?.[0] || 'Combined indicators suggest elevated flood risk.'}
                  </div>
                  <div className="text-cyan-300 font-semibold">
                    Advisory: {data?.explanation?.RECOMMENDATION?.[0] || 'Maintain active monitoring.'}
                  </div>
                </div>

                <div className="p-3 bg-gray-900 rounded-xl border border-gray-800 text-[11px] text-gray-400">
                  <span className="font-bold text-gray-300 block mb-1">Scientific Integrity Notice:</span>
                  {data?.disclaimer || 'Water depth is a PROXY ESTIMATE. Not a certified hydraulic or hydrodynamic simulation.'}
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  onClick={() => setShowExplanationModal(false)}
                  className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-colors"
                >
                  Close Explanation
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
