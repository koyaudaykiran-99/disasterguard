import React, { useState } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { AlertCard } from '../components/motion/AlertCard';
import { StaggeredList } from '../components/motion/StaggeredList';
import { useDisaster } from '../context/DisasterContext';
import { BellRing, Filter, AlertTriangle, ShieldAlert } from 'lucide-react';
import { RiskLevel, Alert } from '../types/disaster';
import { AlertExplanationModal } from '../components/ai/AlertExplanationModal';
import { AdaptiveAlertPanel } from '../components/motion/AdaptiveAlertPanel';

export const AlertsPage: React.FC = () => {
  const { alerts } = useDisaster();
  const [selectedSeverity, setSelectedSeverity] = useState<RiskLevel | 'ALL'>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [alertForAI, setAlertForAI] = useState<Alert | null>(null);

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSeverity = selectedSeverity === 'ALL' || alert.severity === selectedSeverity;
    const matchesCategory = selectedCategory === 'ALL' || alert.category === selectedCategory;
    return matchesSeverity && matchesCategory;
  });

  return (
    <PageTransition className="p-6 space-y-6">
      {/* Header & Filter Controls */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-gray-800">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <BellRing className="w-6 h-6 text-rose-400" />
            Disaster Alert & Incident Center
          </h2>
          <p className="text-xs text-gray-400 font-mono mt-1">
            Real-Time Geo-Targeted Warning Feeds & Escalation Log
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 bg-gray-900 px-3 py-1.5 rounded-xl border border-gray-800 text-xs font-mono">
            <Filter className="w-3.5 h-3.5 text-gray-400" />
            <span className="text-gray-400">Severity:</span>
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value as any)}
              className="bg-transparent text-gray-200 focus:outline-none cursor-pointer"
            >
              <option value="ALL" className="bg-gray-900">ALL SEVERITIES</option>
              <option value="CRITICAL" className="bg-gray-900 text-rose-400">CRITICAL</option>
              <option value="HIGH" className="bg-gray-900 text-orange-400">HIGH</option>
              <option value="MODERATE" className="bg-gray-900 text-amber-400">MODERATE</option>
              <option value="LOW" className="bg-gray-900 text-emerald-400">LOW</option>
            </select>
          </div>

          <div className="flex items-center space-x-2 bg-gray-900 px-3 py-1.5 rounded-xl border border-gray-800 text-xs font-mono">
            <span className="text-gray-400">Type:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-transparent text-gray-200 focus:outline-none cursor-pointer"
            >
              <option value="ALL" className="bg-gray-900">ALL DISASTERS</option>
              <option value="FLOOD" className="bg-gray-900">FLOOD</option>
              <option value="STORM" className="bg-gray-900">STORM</option>
              <option value="LANDSLIDE" className="bg-gray-900">LANDSLIDE</option>
              <option value="CYCLONE" className="bg-gray-900">CYCLONE</option>
            </select>
          </div>
        </div>
      </div>

      {/* Phase 5.4: Adaptive Alert Intelligence & Operator Approval Panel */}
      <AdaptiveAlertPanel />

      {/* Alert Feed Summary */}
      <div className="flex items-center justify-between text-xs font-mono text-gray-400">
        <span>Showing {filteredAlerts.length} of {alerts.length} active alerts</span>
        <span className="flex items-center text-cyan-400">
          <ShieldAlert className="w-3.5 h-3.5 mr-1" />
          Broadcast to 142,000 Citizens via Emergency Cell Broadcast
        </span>
      </div>

      {/* Staggered Alert Cards List */}
      {filteredAlerts.length > 0 ? (
        <StaggeredList className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredAlerts.map((alert, idx) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              index={idx}
              onExplainAI={(a) => setAlertForAI(a)}
            />
          ))}
        </StaggeredList>
      ) : (
        <div className="glass-panel p-12 text-center rounded-2xl border border-gray-800 space-y-3">
          <AlertTriangle className="w-10 h-10 text-gray-600 mx-auto" />
          <h4 className="text-gray-300 font-bold">No Alerts Match Selected Filter</h4>
          <p className="text-xs text-gray-500 font-mono">Try clearing filter criteria to view all active warnings.</p>
        </div>
      )}

      {/* AI Alert Explanation Modal */}
      <AlertExplanationModal
        alert={alertForAI}
        isOpen={Boolean(alertForAI)}
        onClose={() => setAlertForAI(null)}
        onNavigateToAssistant={() => {
          setAlertForAI(null);
          window.location.hash = '/ai-assistant';
        }}
      />
    </PageTransition>
  );
};
