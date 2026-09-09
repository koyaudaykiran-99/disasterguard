import React, { useState, useEffect } from 'react';
import {
  Bell,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowRight,
  Shield,
  Filter,
  Check,
  Zap,
  ChevronRight
} from 'lucide-react';
import { OperatorAttentionItem } from '../../types/situationalAwareness';
import { situationalAwarenessService } from '../../services/situationalAwarenessService';

interface Props {
  onInspectItem?: (item: OperatorAttentionItem) => void;
  onOpenContention?: (incidentId?: number) => void;
}

export const OperatorAttentionQueue: React.FC<Props> = ({ onInspectItem, onOpenContention }) => {
  const [items, setItems] = useState<OperatorAttentionItem[]>([]);
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [statusFilter, setStatusFilter] = useState<'PENDING' | 'ALL'>('PENDING');
  const [acknowledgingId, setAcknowledgingId] = useState<number | null>(null);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const res = await situationalAwarenessService.getOperatorAttentionQueue(
        statusFilter === 'ALL' ? undefined : 'PENDING'
      );
      setItems(res.items);
      setPendingCount(res.pendingCount);
    } catch (err) {
      console.warn('Failed to load attention items:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
    const interval = setInterval(fetchItems, 12000);
    return () => clearInterval(interval);
  }, [statusFilter]);

  const handleAcknowledge = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      setAcknowledgingId(id);
      await situationalAwarenessService.acknowledgeAttentionItem(id, 'OPERATOR_1');
      await fetchItems();
    } catch (err) {
      console.error('Failed to acknowledge attention item:', err);
    } finally {
      setAcknowledgingId(null);
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
      case 'MODERATE':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      default:
        return 'bg-slate-700 text-slate-300 border-slate-600';
    }
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl shadow-xl overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Operator Attention Queue
              </h3>
              {pendingCount > 0 && (
                <span className="px-2 py-0.2 rounded-full text-[10px] font-black bg-red-500 text-white shadow-sm shadow-red-500/50">
                  {pendingCount} ACTION REQUIRED
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400">
              High-priority events demanding human review or decision
            </p>
          </div>
        </div>

        {/* Filter */}
        <div className="flex items-center space-x-1.5 bg-slate-800/80 p-0.5 rounded-lg border border-slate-700/60 text-xs">
          <button
            onClick={() => setStatusFilter('PENDING')}
            className={`px-2.5 py-1 rounded font-medium transition ${
              statusFilter === 'PENDING'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setStatusFilter('ALL')}
            className={`px-2.5 py-1 rounded font-medium transition ${
              statusFilter === 'ALL'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All
          </button>
        </div>
      </div>

      {/* Queue items */}
      <div className="p-4 space-y-3 overflow-y-auto flex-1 max-h-[380px]">
        {items.length === 0 ? (
          <div className="text-center py-10 text-slate-500 text-xs">
            <CheckCircle className="w-8 h-8 text-emerald-500/60 mx-auto mb-2" />
            <p className="font-semibold text-slate-400">Attention Queue Clear</p>
            <p className="mt-1">All high-priority operational items have been addressed or acknowledged.</p>
          </div>
        ) : (
          items.map((item) => {
            const isPending = item.status === 'PENDING';
            return (
              <div
                key={item.id}
                className={`border rounded-lg p-3 transition-all ${
                  isPending
                    ? 'bg-slate-950/70 border-slate-700/80 hover:border-blue-500/60 shadow-md'
                    : 'bg-slate-950/30 border-slate-800/60 opacity-70'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1 flex-1">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className={`text-[10px] font-black px-2 py-0.5 rounded border ${getPriorityBadge(item.priority)}`}>
                        {item.priority}
                      </span>
                      <span className="text-xs font-bold text-white tracking-wide">
                        {item.title}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">
                        {item.provenance}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 line-clamp-2">
                      {item.summary}
                    </p>

                    {item.recommendedAction && (
                      <div className="text-[11px] text-amber-300/90 font-medium bg-amber-500/10 border border-amber-500/20 px-2 py-1 rounded mt-1.5 flex items-center space-x-1.5">
                        <Zap className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                        <span>Rec: {item.recommendedAction}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col items-end space-y-2 flex-shrink-0">
                    <span className="text-[10px] text-slate-500">
                      {new Date(item.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>

                    {isPending ? (
                      <div className="flex items-center space-x-1.5">
                        {item.title.toLowerCase().includes('contention') && onOpenContention && (
                          <button
                            onClick={() => onOpenContention(item.actionData?.incident_id)}
                            className="px-2 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-semibold transition"
                          >
                            Resolve
                          </button>
                        )}
                        <button
                          onClick={(e) => handleAcknowledge(item.id, e)}
                          disabled={acknowledgingId === item.id}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 text-[11px] font-medium transition flex items-center space-x-1"
                        >
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span>Ack</span>
                        </button>
                      </div>
                    ) : (
                      <span className="text-[10px] text-emerald-400 flex items-center space-x-1">
                        <CheckCircle className="w-3 h-3" />
                        <span>Acknowledged</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
