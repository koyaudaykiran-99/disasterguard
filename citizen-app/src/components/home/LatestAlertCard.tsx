import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert } from '../../types';
import { CloudRain, ArrowRight, Clock } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface LatestAlertCardProps {
  alert: Alert;
}

export const LatestAlertCard: React.FC<LatestAlertCardProps> = ({ alert }) => {
  const navigate = useNavigate();

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between px-1">
        <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-citizen-text-muted">
          Latest Alert
        </h3>
        <span className="text-[10px] font-mono text-amber-400 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
          Active Warning
        </span>
      </div>

      <div
        onClick={() => navigate('/alerts')}
        className="glass-panel p-4 rounded-2xl border border-amber-500/30 bg-gradient-to-r from-amber-950/20 via-slate-900/60 to-slate-950/80 hover:border-amber-500/50 cursor-pointer transition-all duration-200 group relative overflow-hidden"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start space-x-3">
            <div className="p-2.5 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-400 shrink-0 mt-0.5">
              <CloudRain className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <Badge variant={alert.severity}>{alert.category}</Badge>
                <span className="text-[11px] font-mono text-citizen-text-muted flex items-center">
                  <Clock className="w-3 h-3 mr-1 text-slate-500" />
                  {alert.timeAgo}
                </span>
              </div>

              <h4 className="font-bold text-sm text-white mt-1.5 group-hover:text-amber-300 transition-colors">
                {alert.title}
              </h4>
              <p className="text-xs text-citizen-text-secondary line-clamp-2 mt-1 leading-relaxed">
                {alert.description}
              </p>
            </div>
          </div>
        </div>

        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
          <span className="text-citizen-text-muted text-[11px] truncate max-w-[200px]">
            📍 {alert.location}
          </span>
          <span className="text-amber-400 font-semibold group-hover:translate-x-1 transition-transform flex items-center gap-1 text-[11px]">
            <span>View full alert</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </span>
        </div>
      </div>
    </div>
  );
};
