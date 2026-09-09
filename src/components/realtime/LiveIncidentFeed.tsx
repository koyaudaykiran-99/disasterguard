import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  AlertTriangle,
  Radio,
  Droplets,
  Waves,
  Shield,
  LifeBuoy,
  Cpu,
  Clock,
} from 'lucide-react';
import { LiveFeedItem, RealTimeEventType } from '../../types/realtime';

interface LiveIncidentFeedProps {
  items: LiveFeedItem[];
  maxItems?: number;
  className?: string;
}

const getEventIcon = (event: RealTimeEventType) => {
  switch (event) {
    case 'WEATHER_UPDATED':
      return <Droplets className="w-4 h-4 text-cyan-400" />;
    case 'RAIN_PREDICTION_UPDATED':
    case 'FLOOD_PREDICTION_UPDATED':
      return <Cpu className="w-4 h-4 text-indigo-400" />;
    case 'ALERT_CREATED':
    case 'ALERT_UPDATED':
      return <AlertTriangle className="w-4 h-4 text-rose-400" />;
    case 'SOS_CREATED':
    case 'SOS_TRIAGED':
    case 'SOS_UPDATE_CREATED':
    case 'INCIDENT_CREATED':
      return <Radio className="w-4 h-4 text-red-500 animate-pulse" />;
    case 'RESCUE_ASSIGNMENT_CREATED':
    case 'RESCUE_STATUS_UPDATED':
      return <LifeBuoy className="w-4 h-4 text-amber-400" />;
    case 'RISK_ZONE_UPDATED':
      return <Waves className="w-4 h-4 text-orange-400" />;
    case 'SIMULATION_STAGE_CHANGED':
      return <Shield className="w-4 h-4 text-emerald-400" />;
    default:
      return <Activity className="w-4 h-4 text-blue-400" />;
  }
};

const getSeverityBadgeClass = (severity: string) => {
  switch (severity?.toUpperCase()) {
    case 'CRITICAL':
      return 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse';
    case 'HIGH':
      return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    case 'MODERATE':
      return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
    case 'LOW':
    default:
      return 'bg-gray-800/80 text-gray-400 border-gray-700';
  }
};

export const LiveIncidentFeed: React.FC<LiveIncidentFeedProps> = ({
  items,
  maxItems = 12,
  className = '',
}) => {
  const displayItems = items.slice(0, maxItems);

  return (
    <div className={`glass-panel p-5 rounded-2xl border border-gray-800 flex flex-col ${className}`}>
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-gray-800">
        <div className="flex items-center space-x-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
          </span>
          <h3 className="text-sm font-bold text-gray-100 font-mono tracking-wide">
            LIVE COMMAND ACTIVITY FEED
          </h3>
        </div>
        <span className="text-[11px] font-mono text-gray-400 bg-gray-900 px-2 py-0.5 rounded border border-gray-800">
          {items.length} EVENTS
        </span>
      </div>

      <div className="space-y-2.5 overflow-y-auto max-h-[420px] pr-1 scrollbar-thin">
        {displayItems.length === 0 ? (
          <div className="py-10 text-center text-xs font-mono text-gray-500 flex flex-col items-center justify-center space-y-2">
            <Activity className="w-6 h-6 text-gray-600 animate-spin" />
            <span>Listening for real-time disaster command events...</span>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {displayItems.map((item) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: -10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.25 }}
                className="p-3 rounded-xl bg-gray-900/70 border border-gray-800/80 hover:border-gray-700 transition-all"
              >
                <div className="flex items-start justify-between gap-2 mb-1">
                  <div className="flex items-center space-x-2">
                    {getEventIcon(item.event)}
                    <span className="text-xs font-bold text-gray-200">
                      {item.title}
                    </span>
                  </div>
                  <span
                    className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border uppercase ${getSeverityBadgeClass(
                      item.severity
                    )}`}
                  >
                    {item.severity}
                  </span>
                </div>
                <p className="text-xs text-gray-400 pl-6 leading-relaxed line-clamp-2">
                  {item.description}
                </p>
                <div className="flex items-center justify-between mt-1.5 pl-6 text-[10px] font-mono text-gray-500">
                  <span>ID: #{item.entityId || 'SYS'}</span>
                  <span className="flex items-center space-x-1">
                    <Clock className="w-2.5 h-2.5" />
                    <span>{item.timestamp}</span>
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
};
