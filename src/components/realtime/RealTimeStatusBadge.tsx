import React from 'react';
import { RefreshCw, WifiOff } from 'lucide-react';
import { ConnectionStatus } from '../../types/realtime';

interface RealTimeStatusBadgeProps {
  status: ConnectionStatus;
  onReconnect?: () => void;
  className?: string;
}

export const RealTimeStatusBadge: React.FC<RealTimeStatusBadgeProps> = ({
  status,
  onReconnect,
  className = '',
}) => {
  if (status === 'LIVE') {
    return (
      <div
        className={`flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 text-xs font-mono font-medium shadow-sm shadow-emerald-950 ${className}`}
        title="Real-Time WebSocket stream active with backend"
      >
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
        </span>
        <span className="font-bold tracking-wider">LIVE</span>
      </div>
    );
  }

  if (status === 'RECONNECTING') {
    return (
      <div
        className={`flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-950/60 border border-amber-500/40 text-amber-300 text-xs font-mono font-medium ${className}`}
        title="Attempting automatic reconnection with exponential backoff"
      >
        <RefreshCw className="w-3 h-3 animate-spin text-amber-400" />
        <span className="font-semibold tracking-wider">RECONNECTING...</span>
      </div>
    );
  }

  return (
    <div
      className={`flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-500/40 text-rose-400 text-xs font-mono font-medium ${className}`}
      title="WebSocket disconnected. Operating in automatic 30s REST fallback polling mode."
    >
      <WifiOff className="w-3 h-3 text-rose-400" />
      <span className="font-semibold tracking-wider">OFFLINE (REST FALLBACK)</span>
      {onReconnect && (
        <button
          onClick={onReconnect}
          className="ml-1 text-[10px] underline hover:text-white transition-colors"
          title="Force reconnect now"
        >
          Retry
        </button>
      )}
    </div>
  );
};
