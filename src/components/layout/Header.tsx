import React from 'react';
import { motion } from 'framer-motion';
import { Play, ShieldAlert, User, Eye, EyeOff, Sparkles, RotateCcw } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useDisaster } from '../../context/DisasterContext';
import { RealTimeStatusBadge } from '../realtime/RealTimeStatusBadge';

const STAGE_LABELS: Record<number, string> = {
  1: 'NORMAL',
  2: 'HEAVY RAINFALL',
  3: 'AI ANALYSIS',
  4: 'FLOOD RISK INCREASE',
  5: 'CRITICAL RISK',
  6: 'ALERT',
  7: 'SOS / INCIDENT',
  8: 'RESCUE RECOMMENDATION',
};

export const Header: React.FC = () => {
  const { user, toggleReducedMotion } = useAuth();
  const {
    isSimulationActive,
    runDisasterSimulation,
    resetDisasterSimulation,
    simulationStep,
    simulationStage,
    isSimulationComplete,
    connectionStatus,
    reconnectWebSocket,
  } = useDisaster();

  const stageLabel = STAGE_LABELS[simulationStep] || simulationStage || 'NORMAL';

  return (
    <header className="bg-white/95 border-b border-slate-200/90 px-6 py-3.5 flex items-center justify-between sticky top-0 z-20 backdrop-blur-md shadow-sm">
      {/* Left Title & Status Ticker */}
      <div className="flex items-center space-x-4">
        {/* Real-Time WebSocket Connection Badge */}
        <RealTimeStatusBadge status={connectionStatus} onReconnect={reconnectWebSocket} />

        <div className="hidden md:flex items-center space-x-2 px-3 py-1 rounded-xl bg-slate-100/90 border border-slate-200 text-[11px] font-mono text-slate-600 shadow-inner">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>Spatial PostGIS ST_DWithin Active</span>
        </div>

        {(isSimulationActive || isSimulationComplete) && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`flex items-center space-x-2 px-3 py-1 rounded-md border font-mono text-xs font-bold ${
              isSimulationComplete
                ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                : 'bg-amber-500/20 border-amber-500/40 text-amber-300'
            }`}
          >
            <ShieldAlert className={`w-4 h-4 ${isSimulationComplete ? 'text-emerald-400' : 'text-amber-400 animate-bounce'}`} />
            <span>
              {isSimulationComplete
                ? `SIMULATION COMPLETE (Step 8/8: ${STAGE_LABELS[8]})`
                : `Step ${simulationStep || 1}/8: ${stageLabel}`}
            </span>
          </motion.div>
        )}
      </div>

      {/* Right Controls & Actions */}
      <div className="flex items-center space-x-4">
        {/* Reset Simulation Button */}
        {(isSimulationActive || isSimulationComplete) && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.96 }}
            onClick={resetDisasterSimulation}
            aria-label="Reset Simulation and Restore Database Baseline"
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-mono font-bold tracking-wider uppercase border border-rose-500/40 bg-rose-950/40 hover:bg-rose-900/50 text-rose-300 transition-all shadow-lg"
            title="Reset Simulation & Restore Database"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>RESET</span>
          </motion.button>
        )}

        {/* RUN DISASTER SIMULATION BUTTON */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.96 }}
          onClick={runDisasterSimulation}
          disabled={isSimulationActive}
          aria-label="Run Backend-Driven Disaster Simulation"
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-mono font-bold tracking-wider uppercase border transition-all shadow-lg ${
            isSimulationActive
              ? 'bg-amber-600/30 text-amber-300 border-amber-500/50 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white border-blue-400/40 shadow-blue-500/20'
          }`}
        >
          <Play className={`w-3.5 h-3.5 ${isSimulationActive ? 'animate-spin' : ''}`} />
          <span>
            {isSimulationActive
              ? 'SIMULATION IN PROGRESS...'
              : isSimulationComplete
              ? 'RERUN SIMULATION'
              : 'RUN DISASTER SIMULATION'}
          </span>
        </motion.button>

        {/* Reduced Motion Toggle */}
        <button
          onClick={toggleReducedMotion}
          aria-label={user.prefersReducedMotion ? 'Enable standard motion' : 'Enable reduced motion'}
          title={user.prefersReducedMotion ? 'Enable standard motion' : 'Enable reduced motion'}
          className={`p-2 rounded-xl border text-xs flex items-center space-x-1.5 transition-colors ${
            user.prefersReducedMotion
              ? 'bg-purple-100 border-purple-300 text-purple-700'
              : 'bg-slate-100 border-slate-200 text-slate-600 hover:text-slate-900 shadow-sm'
          }`}
        >
          {user.prefersReducedMotion ? (
            <>
              <EyeOff className="w-4 h-4 text-purple-600" />
              <span className="hidden lg:inline font-mono text-[11px]">Reduced Motion</span>
            </>
          ) : (
            <>
              <Eye className="w-4 h-4" />
              <span className="hidden lg:inline font-mono text-[11px]">Full Motion</span>
            </>
          )}
        </button>

        {/* User Badge */}
        <div className="flex items-center space-x-2.5 pl-3 border-l border-slate-200">
          <div className="w-8 h-8 rounded-xl bg-blue-100 border border-blue-200 flex items-center justify-center text-blue-600 font-bold text-xs shadow-sm">
            <User className="w-4 h-4" />
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-semibold text-slate-900">{user.name}</div>
            <div className="text-[10px] font-mono text-slate-500">{user.role}</div>
          </div>
        </div>
      </div>
    </header>
  );
};
