import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { AlertTriangle, Clock, MapPin, Users, Flame, CloudRain, AlertOctagon, Sparkles } from 'lucide-react';
import { Alert } from '../../types/disaster';

interface AlertCardProps {
  alert: Alert;
  index?: number;
  onSelect?: (alert: Alert) => void;
  onExplainAI?: (alert: Alert) => void;
}

export const AlertCard: React.FC<AlertCardProps> = ({ alert, index = 0, onSelect, onExplainAI }) => {
  const shouldReduceMotion = useReducedMotion();

  const getCategoryIcon = (category: Alert['category']) => {
    switch (category) {
      case 'FLOOD':
        return <CloudRain className="w-5 h-5 text-cyan-400" />;
      case 'STORM':
      case 'CYCLONE':
        return <Flame className="w-5 h-5 text-amber-400" />;
      case 'LANDSLIDE':
      case 'EARTHQUAKE':
        return <AlertTriangle className="w-5 h-5 text-orange-400" />;
      default:
        return <AlertOctagon className="w-5 h-5 text-red-400" />;
    }
  };

  const getSeverityBadge = (severity: Alert['severity']) => {
    switch (severity) {
      case 'LOW':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'MODERATE':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'HIGH':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/30';
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/50';
    }
  };

  const isCritical = alert.severity === 'CRITICAL';

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={
        isCritical && !shouldReduceMotion
          ? {
              opacity: 1,
              y: 0,
              borderColor: [
                'rgba(244, 63, 94, 0.3)',
                'rgba(244, 63, 94, 0.7)',
                'rgba(244, 63, 94, 0.3)',
              ],
              boxShadow: [
                '0 0 10px rgba(244, 63, 94, 0.1)',
                '0 0 20px rgba(244, 63, 94, 0.25)',
                '0 0 10px rgba(244, 63, 94, 0.1)',
              ],
            }
          : { opacity: 1, y: 0 }
      }
      transition={{
        duration: shouldReduceMotion ? 0.05 : isCritical ? 2.4 : 0.3,
        delay: shouldReduceMotion ? 0 : index * 0.05,
        ease: isCritical ? 'easeInOut' : [0.16, 1, 0.3, 1],
        repeat: isCritical && !shouldReduceMotion ? Infinity : 0,
      }}
      whileHover={shouldReduceMotion ? {} : { y: -2 }}
      onClick={() => onSelect?.(alert)}
      className={`relative glass-panel rounded-xl p-5 border cursor-pointer transition-all ${
        isCritical
          ? 'border-rose-500/40 bg-gradient-to-r from-rose-950/20 to-command-card'
          : alert.isNew
          ? 'border-cyan-500/40 bg-command-card ring-1 ring-cyan-500/20'
          : 'border-gray-800 hover:border-gray-700 bg-command-card'
      }`}
    >
      {/* New alert badge */}
      {alert.isNew && (
        <motion.span
          initial={{ scale: 0.8 }}
          animate={{ scale: [0.95, 1.05, 0.95] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute -top-2.5 right-4 bg-cyan-500 text-black font-bold font-mono text-[10px] uppercase px-2.5 py-0.5 rounded-full shadow-lg"
        >
          NEW ALERT
        </motion.span>
      )}

      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-gray-900/80 border border-gray-800">
            {getCategoryIcon(alert.category)}
          </div>
          <div>
            <h4 className="font-semibold text-gray-100 text-base flex items-center gap-2">
              {alert.title}
            </h4>
            <div className="flex items-center text-xs text-gray-400 mt-1 space-x-3">
              <span className="flex items-center">
                <MapPin className="w-3.5 h-3.5 mr-1 text-gray-500" />
                {alert.location}
              </span>
              <span className="flex items-center">
                <Clock className="w-3.5 h-3.5 mr-1 text-gray-500" />
                {alert.timestamp}
              </span>
            </div>
          </div>
        </div>

        <span
          className={`px-3 py-1 text-xs font-mono font-bold tracking-wide uppercase rounded-full border ${getSeverityBadge(
            alert.severity
          )}`}
        >
          {alert.severity}
        </span>
      </div>

      <p className="text-xs text-gray-300 mt-3 leading-relaxed">{alert.description}</p>

      <div className="mt-4 pt-3 border-t border-gray-800/80 flex flex-wrap items-center justify-between gap-2 text-xs text-gray-400 font-mono">
        <span className="flex items-center">
          <Users className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
          Est. Affected: <strong className="text-gray-200 ml-1">{alert.affectedPopulation.toLocaleString()}</strong>
        </span>
        <div className="flex items-center space-x-2">
          {onExplainAI && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onExplainAI(alert);
              }}
              className="px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[11px] font-mono font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Sparkles className="w-3 h-3 text-cyan-400" />
              <span>Explain with AI</span>
            </button>
          )}
          <span className="text-blue-400 hover:text-blue-300 font-sans font-medium flex items-center">
            View Coordinates &rarr;
          </span>
        </div>
      </div>
    </motion.div>
  );
};
