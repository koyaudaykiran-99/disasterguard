import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  Clock,
  Shield,
  Activity,
  Layers,
  ChevronRight,
  Flame,
  Zap,
  Info
} from 'lucide-react';
import { SituationalSnapshot, OperationalChange } from '../../types/situationalAwareness';
import { situationalAwarenessService } from '../../services/situationalAwarenessService';

interface Props {
  onSelectHotspot?: (hotspotId: number) => void;
  onSelectCluster?: (clusterId: number) => void;
}

export const SituationAwarenessPanel: React.FC<Props> = () => {
  const [snapshot, setSnapshot] = useState<SituationalSnapshot | null>(null);
  const [changes, setChanges] = useState<OperationalChange[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const [activeTab, setActiveTab] = useState<'CURRENT' | 'CHANGES'>('CURRENT');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [snap, changeData] = await Promise.all([
        situationalAwarenessService.getCurrentSituation(),
        situationalAwarenessService.getSituationChanges(30),
      ]);
      setSnapshot(snap);
      setChanges(changeData.changes);
      setLastRefreshed(new Date());
    } catch (err) {
      console.warn('Failed to load situational awareness data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000); // 15s refresh
    return () => clearInterval(interval);
  }, []);

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/40 shadow-red-900/30';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/40 shadow-orange-900/30';
      case 'MODERATE':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40 shadow-amber-900/30';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 shadow-emerald-900/30';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'RAPIDLY_ESCALATING':
      case 'ESCALATING':
        return <TrendingUp className="w-4 h-4 text-red-400" />;
      case 'DE_ESCALATING':
        return <TrendingDown className="w-4 h-4 text-emerald-400" />;
      default:
        return <Minus className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl shadow-xl overflow-hidden mb-6">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between px-6 py-4 border-b border-slate-800/80 bg-slate-950/40 gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Activity className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-white tracking-wide uppercase">
                Disaster Situational Intelligence
              </h2>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
                PHASE 6
              </span>
              {snapshot?.provenance && (
                <span className="px-1.5 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {snapshot.provenance}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Live multi-source synthesis • Change tracking • Threat evaluation
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Navigation tabs */}
          <div className="flex bg-slate-800/80 p-1 rounded-lg border border-slate-700/60 text-xs">
            <button
              onClick={() => setActiveTab('CURRENT')}
              className={`px-3 py-1 rounded-md font-medium transition-all ${
                activeTab === 'CURRENT'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Current Situation
            </button>
            <button
              onClick={() => setActiveTab('CHANGES')}
              className={`px-3 py-1 rounded-md font-medium transition-all flex items-center space-x-1.5 ${
                activeTab === 'CHANGES'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>What Changed</span>
              {changes.length > 0 && (
                <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-red-500 text-white font-bold">
                  {changes.length}
                </span>
              )}
            </button>
          </div>

          <button
            onClick={fetchData}
            disabled={loading}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
            title="Refresh Situational Picture"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Body */}
      {activeTab === 'CURRENT' ? (
        <div className="p-6">
          {/* Metrics summary row */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-5">
            {/* Risk Score */}
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 flex flex-col justify-between">
              <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                Risk Score
              </span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className="text-2xl font-black text-white font-mono">
                  {snapshot ? Math.round(snapshot.riskScore) : '--'}
                </span>
                <span className="text-xs text-slate-400 font-mono">/100</span>
              </div>
              <div className="flex items-center space-x-1.5 mt-2">
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getRiskBadgeColor(
                    snapshot?.riskLevel || 'LOW'
                  )}`}
                >
                  {snapshot?.riskLevel || 'LOW'}
                </span>
              </div>
            </div>

            {/* Trend */}
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 flex flex-col justify-between">
              <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                Trajectory
              </span>
              <div className="flex items-center space-x-2 mt-1">
                {getTrendIcon(snapshot?.trend || 'STABLE')}
                <span className="text-sm font-bold text-white uppercase tracking-tight">
                  {(snapshot?.trend || 'STABLE').replace(/_/g, ' ')}
                </span>
              </div>
              <span className="text-[10px] text-slate-500 mt-2 font-mono">
                Threat: {snapshot?.dominantThreat || 'FLOOD'}
              </span>
            </div>

            {/* Critical Emergencies */}
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 flex flex-col justify-between">
              <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                Critical SOS
              </span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className={`text-2xl font-black font-mono ${
                  (snapshot?.criticalEmergencies ?? 0) > 0 ? 'text-red-400' : 'text-slate-300'
                }`}>
                  {snapshot?.criticalEmergencies ?? 0}
                </span>
                <span className="text-xs text-slate-500">
                  / {snapshot?.activeEmergencies ?? 0} total
                </span>
              </div>
              <span className="text-[10px] text-slate-500 mt-2">
                Active in queue
              </span>
            </div>

            {/* Active Alerts */}
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 flex flex-col justify-between">
              <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                Active Alerts
              </span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className="text-2xl font-black text-amber-400 font-mono">
                  {snapshot?.activeAlertsCount ?? 0}
                </span>
              </div>
              <span className="text-[10px] text-slate-500 mt-2">
                Broadcasted
              </span>
            </div>

            {/* Assigned & En Route */}
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 flex flex-col justify-between">
              <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                Squad Deployments
              </span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className="text-2xl font-black text-blue-400 font-mono">
                  {(snapshot?.assignedTeamsCount ?? 0) + (snapshot?.enRouteTeamsCount ?? 0)}
                </span>
              </div>
              <span className="text-[10px] text-slate-500 mt-2">
                {snapshot?.enRouteTeamsCount ?? 0} en route
              </span>
            </div>

            {/* Resource Contentions */}
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 flex flex-col justify-between">
              <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                Contentions
              </span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className={`text-2xl font-black font-mono ${
                  (snapshot?.resourceContentionsCount ?? 0) > 0 ? 'text-amber-400' : 'text-slate-400'
                }`}>
                  {snapshot?.resourceContentionsCount ?? 0}
                </span>
              </div>
              <span className="text-[10px] text-slate-500 mt-2">
                Competing claims
              </span>
            </div>

            {/* Bottlenecks */}
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 flex flex-col justify-between">
              <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                Bottlenecks
              </span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className={`text-2xl font-black font-mono ${
                  (snapshot?.operationalBottlenecksCount ?? 0) > 0 ? 'text-orange-400' : 'text-slate-400'
                }`}>
                  {snapshot?.operationalBottlenecksCount ?? 0}
                </span>
              </div>
              <span className="text-[10px] text-slate-500 mt-2">
                Logistical chokepoints
              </span>
            </div>
          </div>

          {/* Situation Summary & Confidence Footer */}
          <div className="bg-slate-950/40 border border-slate-800 rounded-lg p-3 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
            <div className="flex items-center space-x-2 text-slate-300">
              <Info className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span className="italic">
                "{snapshot?.summary || 'Synthesizing multi-horizon forecast and operational sensor data...'}"
              </span>
            </div>
            <div className="flex items-center space-x-4 text-slate-500 text-[11px] flex-shrink-0">
              <span>Confidence: {snapshot ? Math.round(snapshot.confidence * 100) : 0}%</span>
              <span>Updated: {lastRefreshed.toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      ) : (
        /* What Changed Feed */
        <div className="p-6">
          {changes.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-sm">
              <Clock className="w-8 h-8 mx-auto mb-2 text-slate-600" />
              No significant situational deviations detected in the last observation window.
            </div>
          ) : (
            <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
              {changes.map((change, idx) => (
                <div
                  key={idx}
                  className="bg-slate-950/60 border border-slate-800 rounded-lg p-3.5 flex items-start justify-between hover:border-slate-700 transition"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${getRiskBadgeColor(change.severity)}`}>
                        {change.severity}
                      </span>
                      <span className="text-xs font-semibold text-white">
                        {change.changeType.replace(/_/g, ' ')}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500 bg-slate-900 px-1.5 py-0.5 rounded">
                        {change.provenance}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300">
                      {change.description}
                    </p>
                    <div className="text-[11px] text-slate-500 font-mono">
                      Delta: <span className={change.delta > 0 ? 'text-red-400' : 'text-emerald-400'}>
                        {change.delta > 0 ? `+${change.delta}` : change.delta}
                      </span> ({change.previousValue} → {change.currentValue})
                    </div>
                  </div>
                  <span className="text-[10px] text-slate-500 whitespace-nowrap ml-4">
                    {new Date(change.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
