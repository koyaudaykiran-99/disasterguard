import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Clock,
  Radio,
  AlertTriangle,
  Waves,
  HeartPulse,
  MapPin,
  RefreshCw,
  XCircle,
  MessageSquare,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Mic,
  Volume2,
} from 'lucide-react';
import { EmergencyUpdate } from '../../types/disaster';
import { API_BASE } from '../../services/disasterService';

interface EmergencyTimelineProps {
  sosId?: number | string;
  initialUpdates?: EmergencyUpdate[];
  className?: string;
}

export const EmergencyTimeline: React.FC<EmergencyTimelineProps> = ({
  sosId,
  initialUpdates,
  className = '',
}) => {
  const [updates, setUpdates] = useState<EmergencyUpdate[]>(initialUpdates || []);
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  // Poll or fetch updates if sosId is provided
  useEffect(() => {
    if (!sosId) return;
    const numericId = typeof sosId === 'string' ? parseInt(sosId.replace(/\D/g, ''), 10) : sosId;
    if (isNaN(numericId) || numericId <= 0) return;

    let isMounted = true;
    const fetchUpdates = async () => {
      try {
        const res = await fetch(`${API_BASE}/sos/${numericId}/updates`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted && Array.isArray(data) && data.length > 0) {
            setUpdates(data);
          }
        }
      } catch (e) {
        // Fallback or offline
      }
    };

    fetchUpdates();
    const interval = setInterval(fetchUpdates, 8000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [sosId]);

  // Sync if initialUpdates prop changes
  useEffect(() => {
    if (initialUpdates && initialUpdates.length > 0) {
      setUpdates(initialUpdates);
    }
  }, [initialUpdates]);

  const getUpdateMeta = (type: string) => {
    switch (type) {
      case 'INITIAL_SOS':
        return {
          icon: <Radio className="w-3.5 h-3.5 text-rose-400" />,
          label: 'Initial SOS Transmitted',
          badgeClass: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
        };
      case 'TRAPPED_PERSON_UPDATE':
        return {
          icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />,
          label: 'Person Trapped Escalation',
          badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
        };
      case 'WATER_LEVEL_UPDATE':
        return {
          icon: <Waves className="w-3.5 h-3.5 text-cyan-400" />,
          label: 'Rising Floodwaters',
          badgeClass: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
        };
      case 'MEDICAL_UPDATE':
        return {
          icon: <HeartPulse className="w-3.5 h-3.5 text-rose-400" />,
          label: 'Medical Emergency',
          badgeClass: 'bg-rose-600/20 text-rose-200 border-rose-600/40',
        };
      case 'LOCATION_UPDATE':
        return {
          icon: <MapPin className="w-3.5 h-3.5 text-emerald-400" />,
          label: 'GPS Coordinate Shift',
          badgeClass: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
        };
      case 'REPEAT_SOS':
        return {
          icon: <RefreshCw className="w-3.5 h-3.5 text-purple-400" />,
          label: 'Repeat SOS Beacon',
          badgeClass: 'bg-purple-500/20 text-purple-300 border-purple-500/40',
        };
      case 'CANCEL_REQUEST':
        return {
          icon: <XCircle className="w-3.5 h-3.5 text-slate-400" />,
          label: 'Cancel Request',
          badgeClass: 'bg-slate-500/20 text-slate-300 border-slate-500/40',
        };
      case 'SITUATION_UPDATE':
        return {
          icon: <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />,
          label: 'Situation Escalation',
          badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
        };
      case 'VOICE_UPDATE':
        return {
          icon: <Mic className="w-3.5 h-3.5 text-pink-400 animate-pulse" />,
          label: 'Voice Emergency Update',
          badgeClass: 'bg-pink-500/20 text-pink-300 border-pink-500/40',
        };
      default:
        return {
          icon: <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />,
          label: 'Distress Update',
          badgeClass: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
        };
    }
  };

  const formatTime = (ts?: string) => {
    if (!ts) return 'Just now';
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return ts;
    }
  };

  const displayList = updates.length > 0 ? updates : [
    {
      id: 0,
      sosId: typeof sosId === 'number' ? sosId : 0,
      updateType: 'INITIAL_SOS',
      message: 'Citizen distress beacon initialized with location telemetry.',
      source: 'CITIZEN_APP',
      deliveryStatus: 'RECEIVED',
      originalLanguage: 'en',
      processingStatus: 'PROCESSED',
      createdAt: new Date().toISOString(),
      receivedAt: new Date().toISOString(),
    } as EmergencyUpdate
  ];

  return (
    <div className={`rounded-xl border border-gray-800/80 bg-gray-950/70 p-3 space-y-2.5 font-mono text-xs ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800/60 pb-2">
        <div className="flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
          <span className="font-bold text-gray-200 uppercase tracking-wider text-[11px]">
            Emergency Timeline ({displayList.length} {displayList.length === 1 ? 'event' : 'events'})
          </span>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-gray-400 hover:text-gray-200 p-1 rounded transition-colors flex items-center gap-1 text-[10px]"
        >
          <span>{isExpanded ? 'Collapse' : 'Expand'}</span>
          {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {/* Timeline Items */}
      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.2 }}
          className="relative pl-4 space-y-3 before:absolute before:left-1.5 before:top-2 before:bottom-2 before:w-[2px] before:bg-gray-800"
        >
          {displayList.map((item, idx) => {
            const meta = getUpdateMeta(item.updateType);
            return (
              <motion.div
                key={item.id || idx}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: idx * 0.05 }}
                className="relative group space-y-1"
              >
                {/* Timeline Dot */}
                <div className="absolute -left-4 top-1 w-2.5 h-2.5 rounded-full bg-gray-900 border-2 border-indigo-400 group-hover:scale-125 transition-transform" />

                {/* Event Top Bar */}
                <div className="flex flex-wrap items-center justify-between gap-1.5">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {meta.icon}
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${meta.badgeClass}`}>
                      {meta.label}
                    </span>

                    {/* Multilingual Voice Badges */}
                    {(item.updateType === 'VOICE_UPDATE' || item.audio_id || item.audioId) && (
                      <>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${
                          (item.original_language || item.originalLanguage) === 'te'
                            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                            : (item.original_language || item.originalLanguage) === 'hi'
                            ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                            : 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                        }`}>
                          {(item.original_language || item.originalLanguage) === 'te'
                            ? 'TELUGU'
                            : (item.original_language || item.originalLanguage) === 'hi'
                            ? 'HINDI'
                            : 'ENGLISH'}
                        </span>

                        {(item.transcription_provider || item.transcriptionProvider) && (
                          <span className={`text-[9px] px-1.5 py-0.5 rounded border font-mono ${
                            (item.transcription_provider || item.transcriptionProvider)?.includes('mock')
                              ? 'bg-amber-950/40 text-amber-400 border-amber-500/40'
                              : 'bg-cyan-950/40 text-cyan-300 border-cyan-500/40'
                          }`}>
                            {(item.transcription_provider || item.transcriptionProvider)?.includes('mock')
                              ? 'DEMO / MOCK TRANSCRIPTION'
                              : 'AI WHISPER'}
                          </span>
                        )}
                      </>
                    )}
                  </div>
                  <span className="text-[10px] text-gray-400">
                    {formatTime(item.createdAt)}
                  </span>
                </div>

                {/* Message Content & Original Transcript */}
                {item.message && (
                  <div className="pl-5 space-y-1">
                    {(item.updateType === 'VOICE_UPDATE' || item.audio_id || item.audioId) && (
                      <span className="text-[10px] text-pink-300 font-semibold block">
                        Original Spoken Transcript:
                      </span>
                    )}
                    <p className={`leading-relaxed p-2 rounded border text-xs ${
                      item.updateType === 'VOICE_UPDATE' || item.audio_id || item.audioId
                        ? 'text-pink-100 bg-pink-950/20 border-pink-500/30 font-medium'
                        : 'text-gray-300 bg-black/20 border-gray-800/40 text-[11px]'
                    }`}>
                      "{item.message}"
                    </p>
                  </div>
                )}

                {/* Voice Audio Playback Player */}
                {(item.audio_id || item.audioId) && (
                  <div className="pl-5 pt-1">
                    <div className="bg-black/40 p-1.5 rounded-lg border border-pink-500/30 flex items-center gap-2 max-w-sm">
                      <Volume2 className="w-3.5 h-3.5 text-pink-400 shrink-0" />
                      <audio
                        controls
                        preload="none"
                        src={`${API_BASE}/sos/${item.sosId || (typeof sosId === 'number' ? sosId : parseInt(String(sosId || '').replace(/\D/g, ''), 10) || 1)}/voice/${item.audio_id || item.audioId}`}
                        className="w-full h-6"
                      />
                    </div>
                  </div>
                )}

                {/* GPS Coordinates Shift if available */}
                {item.latitude != null && item.longitude != null && (
                  <div className="text-[10px] text-emerald-400 pl-5 flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    <span>
                      Coords: [{item.latitude.toFixed(4)}, {item.longitude.toFixed(4)}]
                      {item.accuracy ? ` (±${item.accuracy.toFixed(0)}m)` : ''}
                    </span>
                  </div>
                )}
              </motion.div>
            );
          })}
        </motion.div>
      )}
    </div>
  );
};
