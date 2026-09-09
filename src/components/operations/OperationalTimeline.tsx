import React, { useState, useEffect } from 'react';
import {
  Clock,
  Shield,
  Truck,
  AlertTriangle,
  Radio,
  Cpu,
  Flame,
  CheckCircle2,
  Filter,
  RefreshCw
} from 'lucide-react';
import { OperationalEvent } from '../../types/situationalAwareness';
import { situationalAwarenessService } from '../../services/situationalAwarenessService';

interface Props {
  limit?: number;
}

export const OperationalTimeline: React.FC<Props> = ({ limit = 40 }) => {
  const [events, setEvents] = useState<OperationalEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const fetchTimeline = async () => {
    try {
      setLoading(true);
      const res = await situationalAwarenessService.getOperationalTimeline(limit);
      setEvents(res.events);
    } catch (err) {
      console.warn('Failed to load operational timeline:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
    const interval = setInterval(fetchTimeline, 15000);
    return () => clearInterval(interval);
  }, [limit]);

  const filteredEvents = selectedCategory === 'ALL'
    ? events
    : events.filter(e => e.category?.toUpperCase() === selectedCategory);

  const getCategoryIcon = (category: string) => {
    switch (category?.toUpperCase()) {
      case 'DISPATCH':
        return <Truck className="w-4 h-4 text-blue-400" />;
      case 'INCIDENT':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'SIMULATION':
        return <Cpu className="w-4 h-4 text-indigo-400" />;
      case 'ALERT':
        return <Radio className="w-4 h-4 text-purple-400" />;
      default:
        return <Shield className="w-4 h-4 text-slate-400" />;
    }
  };

  const getSeverityGlow = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'border-l-4 border-l-red-500 bg-red-950/10';
      case 'HIGH':
        return 'border-l-4 border-l-orange-500 bg-orange-950/10';
      case 'MODERATE':
        return 'border-l-4 border-l-amber-500 bg-amber-950/10';
      default:
        return 'border-l-4 border-l-blue-500/60 bg-slate-900/40';
    }
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl shadow-xl overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Operational Timeline
            </h3>
            <p className="text-[11px] text-slate-400">
              Database-backed audit trail of all commands and critical transitions
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-lg px-2.5 py-1 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Categories</option>
            <option value="DISPATCH">Dispatches</option>
            <option value="INCIDENT">Incidents</option>
            <option value="ALERT">Alerts</option>
            <option value="SIMULATION">Simulation</option>
            <option value="SYSTEM">System</option>
          </select>

          <button
            onClick={fetchTimeline}
            disabled={loading}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
            title="Refresh Timeline"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Timeline Stream */}
      <div className="p-4 space-y-2.5 overflow-y-auto flex-1 max-h-[380px]">
        {filteredEvents.length === 0 ? (
          <div className="text-center py-10 text-slate-500 text-xs">
            <Clock className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            No operational events logged yet.
          </div>
        ) : (
          filteredEvents.map((event) => (
            <div
              key={event.id}
              className={`p-3 rounded-lg border border-slate-800/80 transition-all ${getSeverityGlow(
                event.severity
              )}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start space-x-2.5">
                  <div className="mt-0.5 p-1 rounded bg-slate-800/80 border border-slate-700/60 flex-shrink-0">
                    {getCategoryIcon(event.category)}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-semibold text-white">
                        {event.title}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                        {event.provenance}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1">
                      {event.description}
                    </p>
                    <div className="flex items-center space-x-3 text-[10px] text-slate-500 mt-1.5">
                      <span>Actor: <strong className="text-slate-400">{event.actor}</strong></span>
                      {event.confidence && (
                        <span>Confidence: <strong className="text-slate-400">{Math.round(event.confidence * 100)}%</strong></span>
                      )}
                    </div>
                  </div>
                </div>

                <span className="text-[10px] text-slate-500 whitespace-nowrap">
                  {new Date(event.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
