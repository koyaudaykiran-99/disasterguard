import React, { useState, useEffect } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { StaggeredList } from '../components/motion/StaggeredList';
import { Badge } from '../components/ui/Badge';
import { OfflineBanner } from '../components/connectivity/OfflineBanner';
import { DataFreshnessBadge } from '../components/connectivity/DataFreshnessBadge';
import { alertRepository } from '../storage/repositories/alertRepository';
import { StoredAlert } from '../storage/storageTypes';
import { mockAlerts } from '../data/mock/alerts';
import { Alert } from '../types';
import { Bell, Clock, MapPin, CheckCircle2, ChevronDown, Database } from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<(Alert | StoredAlert)[]>(mockAlerts);
  const [expandedAlertId, setExpandedAlertId] = useState<string | null>(mockAlerts[0].id);

  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const cached = await alertRepository.getAll();
        if (cached && cached.length > 0) {
          setAlerts(cached);
        }
      } catch (err) {
        console.warn('[AlertsPage] Failed to load alerts from storage:', err);
      }
    };

    loadAlerts();
  }, []);

  return (
    <PageTransition className="space-y-4">
      {/* Offline Connectivity Notification */}
      <OfflineBanner />

      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Bell className="w-5 h-5 text-amber-400" />
            Disaster Alerts & Warnings
          </h2>
          <p className="text-xs text-citizen-text-muted font-mono mt-0.5">
            Real-Time Meteorological & Civil Defense Broadcasts
          </p>
        </div>
      </div>

      {/* Alerts Feed */}
      <StaggeredList className="space-y-3 pt-1">
        {alerts.map((alert) => {
          const isExpanded = expandedAlertId === alert.id;
          const cachedAt = 'cachedAt' in alert ? (alert as StoredAlert).cachedAt : Date.now();

          return (
            <div
              key={alert.id}
              className={`glass-panel rounded-2xl border transition-all duration-200 overflow-hidden ${
                alert.severity === 'HIGH'
                  ? 'border-orange-500/40'
                  : alert.severity === 'MODERATE'
                  ? 'border-amber-500/30'
                  : 'border-slate-800'
              }`}
            >
              {/* Alert Header Trigger */}
              <button
                onClick={() => setExpandedAlertId(isExpanded ? null : alert.id)}
                className="w-full p-4 text-left flex items-start justify-between gap-3 focus:outline-none"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant={alert.severity}>{alert.severity}</Badge>
                    <DataFreshnessBadge timestamp={cachedAt} />
                    <span className="text-[10px] font-mono text-slate-400 flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {alert.timeAgo}
                    </span>
                  </div>

                  <h3 className="font-bold text-sm text-white">{alert.title}</h3>

                  <div className="flex items-center text-xs text-slate-400 font-mono">
                    <MapPin className="w-3.5 h-3.5 mr-1 text-cyan-400" />
                    <span>{alert.location}</span>
                  </div>
                </div>

                <div
                  className={`p-1 rounded-lg text-slate-400 transition-transform duration-200 ${
                    isExpanded ? 'rotate-180 text-cyan-400' : ''
                  }`}
                >
                  <ChevronDown className="w-4 h-4" />
                </div>
              </button>

              {/* Expandable Alert Details & Instructions */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-1 space-y-3 border-t border-slate-800/80 font-mono text-xs animate-fadeIn">
                  <p className="text-slate-300 leading-relaxed font-sans text-xs">
                    {alert.description}
                  </p>

                  <div className="space-y-1.5 bg-slate-950/40 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-cyan-400 block mb-1">
                      Actionable Instructions:
                    </span>
                    <ul className="space-y-1.5">
                      {alert.instructions.map((inst, i) => (
                        <li key={i} className="flex items-start text-slate-300 text-[11px]">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mr-1.5 shrink-0 mt-0.5" />
                          <span>{inst}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {'source' in alert && (
                    <div className="flex items-center text-[10px] text-slate-500 font-mono pt-1">
                      <Database className="w-3 h-3 mr-1 text-slate-600" />
                      <span>Stored locally via IndexedDB • Source: {(alert as StoredAlert).source}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </StaggeredList>
    </PageTransition>
  );
};
