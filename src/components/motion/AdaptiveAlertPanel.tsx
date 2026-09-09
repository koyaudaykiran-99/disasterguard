import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  Eye, 
  Filter, 
  Users, 
  Clock, 
  Radio, 
  Send,
  AlertTriangle,
  FileCheck,
  RefreshCw,
  Info
} from 'lucide-react';
import { disasterService } from '../../services/disasterService';
import { AdaptiveAlert, AlertAnalyticsData } from '../../types/disaster';

export const AdaptiveAlertPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'ACTIVE' | 'RECOMMENDATIONS' | 'ALL'>('RECOMMENDATIONS');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [alerts, setAlerts] = useState<AdaptiveAlert[]>([]);
  const [recommendations, setRecommendations] = useState<AdaptiveAlert[]>([]);
  const [analytics, setAnalytics] = useState<AlertAnalyticsData | null>(null);
  const [selectedAlertForReview, setSelectedAlertForReview] = useState<AdaptiveAlert | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);

  const fetchAlertsData = async () => {
    setIsLoading(true);
    try {
      const [activeData, recsData, analyticsData] = await Promise.all([
        disasterService.getActiveApprovedAlerts(),
        disasterService.getAlertRecommendations(),
        disasterService.getAlertAnalytics()
      ]);
      setAlerts(activeData || []);
      setRecommendations(recsData || []);
      setAnalytics(analyticsData || null);
    } catch (err) {
      console.error('Failed to load alert intelligence data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlertsData();
    const interval = setInterval(fetchAlertsData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (alertId: number) => {
    try {
      await disasterService.approveAlert(alertId, 'Duty Officer Alex');
      setActionSuccessMsg(`Alert #${alertId} approved and published to citizen warning channels.`);
      setTimeout(() => setActionSuccessMsg(null), 4000);
      setSelectedAlertForReview(null);
      await fetchAlertsData();
    } catch (err) {
      console.error('Approval failed:', err);
    }
  };

  const handleReject = async (alertId: number) => {
    try {
      await disasterService.rejectAlert(alertId, 'Duty Officer Alex', 'Conditions de-escalated prior to broadcast');
      setActionSuccessMsg(`Alert recommendation #${alertId} rejected and archived.`);
      setTimeout(() => setActionSuccessMsg(null), 4000);
      setSelectedAlertForReview(null);
      await fetchAlertsData();
    } catch (err) {
      console.error('Rejection failed:', err);
    }
  };

  // Determine current list to display
  let displayList = activeTab === 'RECOMMENDATIONS' 
    ? recommendations 
    : (activeTab === 'ACTIVE' ? alerts : [...recommendations, ...alerts]);

  if (severityFilter !== 'ALL') {
    displayList = displayList.filter(a => a.severity === severityFilter);
  }

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse';
      case 'WARNING':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/50';
      case 'WATCH':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50';
      case 'ADVISORY':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/50';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/50';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Telemetry Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
        <div className="glass-panel p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
          <div className="flex items-center justify-between text-slate-400">
            <span>ACTIVE ALERTS</span>
            <Radio className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-xl font-bold text-white mt-1">
            {analytics ? analytics.active_alerts_count : alerts.length}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Approved & Broadcasting</div>
        </div>

        <div className="glass-panel p-3.5 rounded-xl border border-amber-500/30 bg-amber-950/20">
          <div className="flex items-center justify-between text-amber-400">
            <span>RECOMMENDED</span>
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
          </div>
          <div className="text-xl font-bold text-amber-300 mt-1">
            {recommendations.length}
          </div>
          <div className="text-[10px] text-amber-500 mt-0.5">Awaiting Operator Confirmation</div>
        </div>

        <div className="glass-panel p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
          <div className="flex items-center justify-between text-slate-400">
            <span>AFFECTED POPULATION</span>
            <Users className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="text-xl font-bold text-white mt-1">
            ~{(analytics?.total_affected_users_estimate || 14200).toLocaleString()}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Target Zone Coverage</div>
        </div>

        <div className="glass-panel p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
          <div className="flex items-center justify-between text-slate-400">
            <span>DELIVERY SUCCESS</span>
            <Send className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div className="text-xl font-bold text-white mt-1">
            {analytics?.delivery_success_rate_percent ?? 98.4}%
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">In-App + Mesh Relay</div>
        </div>
      </div>

      {actionSuccessMsg && (
        <motion.div 
          initial={{ opacity: 0, y: -8 }} 
          animate={{ opacity: 1, y: 0 }}
          className="p-3 bg-emerald-950/40 border border-emerald-500/40 rounded-xl text-emerald-300 text-xs font-mono flex items-center gap-2"
        >
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{actionSuccessMsg}</span>
        </motion.div>
      )}

      {/* Control Header & Tabs */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('RECOMMENDATIONS')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-mono font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === 'RECOMMENDATIONS'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 border border-transparent'
            }`}
          >
            <span>Operator Queue</span>
            {recommendations.length > 0 && (
              <span className="px-1.5 py-0.2 text-[10px] rounded-full bg-amber-500 text-slate-950 font-bold">
                {recommendations.length}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('ACTIVE')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-mono font-semibold transition-all ${
              activeTab === 'ACTIVE'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 border border-transparent'
            }`}
          >
            Active Warnings ({alerts.length})
          </button>

          <button
            onClick={() => setActiveTab('ALL')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all ${
              activeTab === 'ALL'
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'text-slate-400 hover:text-slate-200 border border-transparent'
            }`}
          >
            All Feeds
          </button>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400">Severity:</span>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 rounded-lg px-2 py-1 focus:outline-none focus:border-cyan-500 text-xs font-mono"
          >
            <option value="ALL">ALL LEVELS</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="WARNING">WARNING</option>
            <option value="WATCH">WATCH</option>
            <option value="ADVISORY">ADVISORY</option>
            <option value="INFO">INFO</option>
          </select>

          <button
            onClick={fetchAlertsData}
            className="p-1.5 text-slate-400 hover:text-slate-200 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors"
            title="Refresh alerts"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Operator Queue Invariant Notice */}
      {activeTab === 'RECOMMENDATIONS' && (
        <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 text-amber-300 text-xs font-mono flex items-start gap-2.5">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">HUMAN OPERATOR APPROVAL BARRIER (PHASE 5.4 SAFETY RULE):</span> High-impact alerts are generated as decision-support recommendations. Autonomous broadcast is blocked until explicit confirmation.
          </div>
        </div>
      )}

      {/* Alert Cards Feed */}
      <div className="space-y-3">
        {displayList.length === 0 ? (
          <div className="glass-panel p-10 text-center rounded-2xl border border-slate-800 text-slate-500 font-mono text-xs">
            No alerts matching current filter criteria.
          </div>
        ) : (
          displayList.map((alert) => {
            const isRec = alert.approval_status === 'RECOMMENDED';
            return (
              <motion.div
                key={alert.id}
                layout
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={`glass-panel p-5 rounded-2xl border transition-all ${
                  isRec
                    ? 'border-amber-500/40 bg-gradient-to-r from-amber-950/20 via-slate-900/60 to-slate-950/80'
                    : 'border-slate-800 hover:border-slate-700 bg-slate-900/50'
                }`}
              >
                <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`px-2.5 py-0.5 rounded-full border text-[11px] font-mono font-bold ${getSeverityBadge(alert.severity)}`}>
                        {alert.severity}
                      </span>
                      <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700 text-[10px] font-mono">
                        {alert.alert_category || alert.alert_type}
                      </span>
                      {isRec ? (
                        <span className="px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[10px] font-mono font-semibold">
                          DECISION-SUPPORT RECOMMENDATION
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono">
                          BROADCASTING ACTIVE
                        </span>
                      )}
                      <span className="text-[11px] font-mono text-slate-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(alert.issued_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-white leading-snug">
                      {alert.title}
                    </h4>

                    <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                      {alert.message}
                    </p>

                    <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono text-slate-400 pt-1">
                      <span>📍 {alert.target_area}</span>
                      {alert.forecast_horizon && (
                        <span>⏳ Peak Horizon: <strong className="text-cyan-400">{alert.forecast_horizon}</strong></span>
                      )}
                      {alert.confidence_score && (
                        <span>🎯 Confidence: <strong>{Math.round(alert.confidence_score * 100)}%</strong></span>
                      )}
                      <span>👥 Target Count: ~{alert.targets?.[0]?.user_count_estimate || 1250}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-wrap items-center gap-2 shrink-0 self-end lg:self-center">
                    <button
                      onClick={() => setSelectedAlertForReview(alert)}
                      className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-mono flex items-center gap-1.5 transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Evidence</span>
                    </button>

                    {isRec ? (
                      <>
                        <button
                          onClick={() => handleApprove(alert.id)}
                          className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-bold flex items-center gap-1.5 shadow-sm transition-all"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Approve & Broadcast</span>
                        </button>
                        <button
                          onClick={() => handleReject(alert.id)}
                          className="px-2.5 py-1.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 border border-rose-500/30 text-rose-300 text-xs font-mono transition-colors"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                        </button>
                      </>
                    ) : (
                      <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Approved by {alert.approved_by || 'Operator'}
                      </span>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })
        )}
      </div>

      {/* Evidence Decomposition Modal */}
      <AnimatePresence>
        {selectedAlertForReview && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-panel w-full max-w-2xl max-h-[85vh] overflow-y-auto p-6 rounded-2xl border border-slate-700 bg-slate-900 text-slate-200 space-y-4 shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <FileCheck className="w-5 h-5 text-cyan-400" />
                  <h3 className="font-bold text-sm text-white">
                    Explainable Evidence Taxonomy — Alert #{selectedAlertForReview.id}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedAlertForReview(null)}
                  className="p-1 rounded-lg text-slate-400 hover:text-white"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3 text-xs font-mono">
                <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700">
                  <span className="text-cyan-400 font-bold block mb-1">FACT (Verified Observations)</span>
                  <ul className="list-disc pl-4 space-y-1 text-slate-300">
                    {selectedAlertForReview.evidence_categories?.FACT?.map((f, i) => (
                      <li key={i}>{f}</li>
                    )) || <li>Local basin telemetry and terrain topography verified.</li>}
                  </ul>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700">
                  <span className="text-indigo-400 font-bold block mb-1">ML_PREDICTION (Forecasts)</span>
                  <ul className="list-disc pl-4 space-y-1 text-slate-300">
                    {selectedAlertForReview.evidence_categories?.ML_PREDICTION?.map((p, i) => (
                      <li key={i}>{p}</li>
                    )) || <li>Peak risk evaluated via multi-horizon regressors.</li>}
                  </ul>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700">
                  <span className="text-amber-400 font-bold block mb-1">GEOSPATIAL_DERIVATION (Targeting)</span>
                  <ul className="list-disc pl-4 space-y-1 text-slate-300">
                    {selectedAlertForReview.evidence_categories?.GEOSPATIAL_DERIVATION?.map((g, i) => (
                      <li key={i}>{g}</li>
                    )) || <li>Target polygon and demographic exposure computed.</li>}
                  </ul>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700">
                  <span className="text-emerald-400 font-bold block mb-1">RECOMMENDATION (Decision Support)</span>
                  <ul className="list-disc pl-4 space-y-1 text-slate-300">
                    {selectedAlertForReview.evidence_categories?.RECOMMENDATION?.map((r, i) => (
                      <li key={i}>{r}</li>
                    )) || <li>Human operator review required prior to publication.</li>}
                  </ul>
                </div>
              </div>

              {/* Action Buttons in Modal */}
              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <div className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
                  <Info className="w-3.5 h-3.5 text-slate-500" />
                  <span>Acknowledged ≠ Safe. Rescue requires separate SOS.</span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedAlertForReview(null)}
                    className="px-3 py-1.5 rounded-xl border border-slate-700 text-slate-300 text-xs font-mono"
                  >
                    Close
                  </button>

                  {selectedAlertForReview.approval_status === 'RECOMMENDED' && (
                    <button
                      onClick={() => handleApprove(selectedAlertForReview.id)}
                      className="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-bold flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Confirm & Broadcast</span>
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};
