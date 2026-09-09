import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEmergencyQueue } from '../../hooks/useEmergencyQueue';
import { useConnectivity } from '../../hooks/useConnectivity';
import { useLanguage } from '../../context/LanguageContext';
import { emergencyManager } from '../../services/emergency/emergencyManager';
import { locationService } from '../../services/location/locationService';
import { emergencyGuidanceService, EmergencySituationType } from '../../services/guidance/emergencyGuidanceService';
import { LanguageSelector } from '../common/LanguageSelector';
import {
  AlertOctagon,
  ShieldCheck,
  Clock,
  Radio,
  RefreshCw,
  XCircle,
  MapPin,
  Check,
  CircleDot,
  Navigation,
  Send,
  Waves,
  HeartPulse,
  Users,
  Home,
  AlertTriangle,
  Brain,
  Truck,
  CheckCircle2,
  ShieldAlert,
  Hospital as HospitalIcon,
  Compass
} from 'lucide-react';
import { VoiceSOSRecorder } from './VoiceSOSRecorder';

const QUICK_UPDATES = [
  { type: 'WATER_LEVEL_UPDATE', label: '🌊 Water is rising', text: 'Water level is rising rapidly inside the premises.' },
  { type: 'TRAPPED_PERSON_UPDATE', label: '👤 Someone is trapped', text: 'A person is trapped and cannot evacuate safely.' },
  { type: 'MEDICAL_UPDATE', label: '❤️ Someone is injured', text: 'Urgent medical assistance required for injured resident.' },
  { type: 'SITUATION_UPDATE', label: '🏠 House is flooded', text: 'Water entered living areas, moving to elevated structure.' },
  { type: 'SITUATION_UPDATE', label: '🚨 Situation is worse', text: 'Emergency situation is getting significantly worse.' },
];

const LIFECYCLE_STAGES = [
  'UNDER REVIEW',
  'AI TRIAGE COMPLETED',
  'RESCUE TEAM ASSIGNED',
  'RESCUE SQUAD EN ROUTE',
  'ON SCENE',
  'RESOLVED'
];

export const ActiveSOSQueueCard: React.FC = () => {
  const { activeSOS, cancelActiveSOS } = useEmergencyQueue();
  const { isOnline } = useConnectivity();
  const { language } = useLanguage();
  const navigate = useNavigate();
  const [customUpdate, setCustomUpdate] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);
  const [showUpdatesList, setShowUpdatesList] = useState<boolean>(false);

  if (!activeSOS || activeSOS.status === 'SENT') return null;

  const refCode = activeSOS.backendSosId
    ? `#DG-${String(activeSOS.backendSosId).padStart(5, '0')}`
    : `#DG-${activeSOS.id.slice(-5).toUpperCase()}`;

  const timeFormatted = new Date(activeSOS.createdAt).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  const getStatusInfo = (status: string) => {
    const norm = (status || '').toUpperCase();
    switch (norm) {
      case 'ON_SCENE':
        return {
          currentStageIdx: 4,
          stageTitle: 'ON SCENE',
          label: 'Rescue Squad On Scene',
          subtext: `Rescue personnel have arrived at the distress location (${refCode})`,
          color: 'text-emerald-400',
          badgeBg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
          dotColor: 'bg-emerald-400',
          icon: <ShieldCheck className="w-4 h-4 text-emerald-400" />
        };
      case 'EN_ROUTE':
      case 'DISPATCHED':
        return {
          currentStageIdx: 3,
          stageTitle: 'RESCUE SQUAD EN ROUTE',
          label: activeSOS.assignedTeamName
            ? `Dispatched: ${activeSOS.assignedTeamName} En Route`
            : 'Rescue Squad Dispatched & En Route',
          subtext: `Command-confirmed rescue squad en route • Note: Live telemetry shown only when field GPS is active (${refCode})`,
          color: 'text-cyan-400',
          badgeBg: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40',
          dotColor: 'bg-cyan-400 animate-ping',
          icon: <Navigation className="w-4 h-4 text-cyan-400 animate-pulse" />
        };
      case 'ASSIGNED':
        return {
          currentStageIdx: 2,
          stageTitle: 'RESCUE TEAM ASSIGNED',
          label: activeSOS.assignedTeamName
            ? `Assigned: ${activeSOS.assignedTeamName}`
            : 'Rescue Squad Assigned',
          subtext: `Rescue unit assigned by Command Center • Preparing departure (${refCode})`,
          color: 'text-blue-400',
          badgeBg: 'bg-blue-500/20 text-blue-400 border-blue-500/40',
          dotColor: 'bg-blue-400',
          icon: <Truck className="w-4 h-4 text-blue-400" />
        };
      case 'TRIAGED':
      case 'AI_TRIAGE_COMPLETED':
        return {
          currentStageIdx: 1,
          stageTitle: 'AI TRIAGE COMPLETED',
          label: 'AI Emergency Triage Completed',
          subtext: `NLP triage & priority scoring completed • Awaiting human operator dispatch authorization (${refCode})`,
          color: 'text-purple-400',
          badgeBg: 'bg-purple-500/20 text-purple-400 border-purple-500/40',
          dotColor: 'bg-purple-400',
          icon: <Brain className="w-4 h-4 text-purple-400" />
        };
      case 'RECEIVED':
      case 'UNDER_REVIEW':
        return {
          currentStageIdx: 0,
          stageTitle: 'UNDER REVIEW',
          label: 'Emergency Under Operator Review',
          subtext: `SOS received by Central Command • Processing emergency triage (${refCode})`,
          color: 'text-amber-400',
          badgeBg: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
          dotColor: 'bg-amber-400',
          icon: <Clock className="w-4 h-4 text-amber-400" />
        };
      case 'RESOLVED':
      case 'RESCUED':
        return {
          currentStageIdx: 5,
          stageTitle: 'RESOLVED',
          label: 'Emergency Incident Resolved',
          subtext: `Citizen reported safe and incident closed by emergency responders (${refCode})`,
          color: 'text-emerald-400',
          badgeBg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
          dotColor: 'bg-emerald-400',
          icon: <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        };
      default:
        return {
          currentStageIdx: 0,
          stageTitle: isOnline ? 'TRANSMITTING' : 'SAVED LOCALLY',
          label: isOnline ? 'Transmitting Emergency SOS...' : 'Saved locally • waiting for communication',
          subtext: isOnline
            ? `Establishing link with Central Command (${refCode})`
            : 'Emergency message stored locally in IndexedDB • Will synchronize automatically when connectivity resumes.',
          color: 'text-rose-400',
          badgeBg: 'bg-rose-500/20 text-rose-400 border-rose-500/40',
          dotColor: 'bg-rose-400 animate-ping',
          icon: <AlertOctagon className="w-4 h-4 text-rose-400 animate-pulse" />
        };
    }
  };

  const statusInfo = getStatusInfo(activeSOS.status);

  // Situation determination for contextual Telugu instructions
  const determineSituation = (): EmergencySituationType => {
    const text = (activeSOS.message || '').toLowerCase();
    const triage = (activeSOS as any).guidance?.triage_summary;
    if (text.includes('trap') || triage?.incident_type === 'TRAPPED' || triage?.incident_type === 'STRUCTURE_COLLAPSE') {
      return 'TRAPPED';
    }
    if (text.includes('injur') || text.includes('medic') || triage?.incident_type === 'MEDICAL') {
      return 'MEDICAL';
    }
    if (text.includes('rain') || text.includes('wind')) {
      return 'HEAVY_RAIN';
    }
    if (text.includes('evacuat') || activeSOS.status === 'DISPATCHED') {
      return 'EVACUATION';
    }
    return 'FLOOD';
  };

  const situation = determineSituation();
  const situationGuidance = emergencyGuidanceService.getGuidanceForSituation(situation, language);
  const guidanceData = (activeSOS as any).guidance;

  const handleSendUpdate = async (type: string, text: string) => {
    if (!text.trim()) return;
    setIsSending(true);
    try {
      await emergencyManager.sendEmergencyUpdate(type, text.trim());
      setCustomUpdate('');
    } finally {
      setIsSending(false);
    }
  };

  const handleUpdateLocation = async () => {
    setIsSending(true);
    try {
      const loc = locationService.getState();
      const coords = loc.coords ? {
        latitude: loc.coords.latitude,
        longitude: loc.coords.longitude,
        accuracy: loc.coords.accuracy ?? undefined
      } : undefined;
      await emergencyManager.sendEmergencyUpdate(
        'LOCATION_UPDATE',
        'Updated GPS beacon telemetry from device sensor.',
        coords
      );
    } finally {
      setIsSending(false);
    }
  };

  const updates = activeSOS.updates || [];

  return (
    <div
      className={`w-full glass-panel-elevated p-4 rounded-3xl border shadow-glow-critical space-y-4 font-mono text-xs animate-fadeIn ${
        statusInfo.currentStageIdx >= 3
          ? 'border-cyan-500/60 bg-gradient-to-b from-cyan-950/40 via-slate-900/80 to-slate-950/90 shadow-cyan-950/40'
          : statusInfo.currentStageIdx >= 1
          ? 'border-indigo-500/50 bg-gradient-to-b from-indigo-950/30 via-slate-900/80 to-slate-950/90'
          : 'border-rose-500/50 bg-gradient-to-b from-rose-950/40 via-slate-900/80 to-slate-950/90'
      }`}
    >
      {/* Header Badge & Language Toggle */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center space-x-2">
          <div className={`p-1.5 rounded-lg ${statusInfo.badgeBg}`}>
            {statusInfo.icon}
          </div>
          <div>
            <span className="font-bold text-white text-xs uppercase tracking-wider block">
              {statusInfo.label}
            </span>
            <span className={`text-[10px] flex items-center gap-1.5 mt-0.5 ${statusInfo.color}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${statusInfo.dotColor}`} />
              <span>{statusInfo.subtext}</span>
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <LanguageSelector />
          <span className="text-[10px] text-slate-400">{timeFormatted}</span>
          <button
            onClick={cancelActiveSOS}
            className="p-1 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition-colors"
            title="Cancel Emergency SOS"
          >
            <XCircle className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 6-Stage Operational Progress Track */}
      <div className="bg-black/40 p-2.5 rounded-xl border border-slate-800/80 space-y-2">
        <div className="flex items-center justify-between text-[10px] text-slate-400">
          <span className="uppercase font-bold tracking-wider text-slate-300">Response Lifecycle</span>
          <span className="font-semibold text-cyan-400">Stage {statusInfo.currentStageIdx + 1} of 6</span>
        </div>
        <div className="grid grid-cols-6 gap-1">
          {LIFECYCLE_STAGES.map((stageName, idx) => {
            const isCompleted = idx < statusInfo.currentStageIdx;
            const isCurrent = idx === statusInfo.currentStageIdx;
            return (
              <div key={idx} className="flex flex-col items-center">
                <div
                  className={`h-1.5 w-full rounded-full transition-all ${
                    isCompleted
                      ? 'bg-emerald-500'
                      : isCurrent
                      ? 'bg-cyan-400 animate-pulse'
                      : 'bg-slate-800'
                  }`}
                />
                <span
                  className={`text-[8px] mt-1 text-center font-mono leading-tight truncate w-full ${
                    isCurrent
                      ? 'text-white font-bold'
                      : isCompleted
                      ? 'text-emerald-400'
                      : 'text-slate-600'
                  }`}
                >
                  {stageName.split(' ')[0]}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Context-Aware Telugu Emergency Guidance Box */}
      <div className="p-3 bg-red-950/40 rounded-2xl border border-red-500/40 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-red-400 shrink-0" />
            <span className="text-xs font-bold text-red-300">
              {situationGuidance.title[language] || situationGuidance.title.te}
            </span>
          </div>
          <span className="text-[10px] uppercase px-2 py-0.5 rounded-full bg-red-500/20 text-red-300 font-bold border border-red-500/30">
            {situation}
          </span>
        </div>
        <p className="text-xs text-red-100 font-medium leading-relaxed">
          {situationGuidance.message[language] || situationGuidance.message.te}
        </p>
        <div className="text-[11px] text-red-200/90 pt-1 border-t border-red-500/20 flex items-start gap-1.5">
          <span className="font-bold">సూచన:</span>
          <span>{situationGuidance.recommendedAction[language] || situationGuidance.recommendedAction.te}</span>
        </div>
      </div>

      {/* Recommended Facilities & Safe Direction Guidance */}
      {guidanceData && (guidanceData.recommended_shelter || guidanceData.recommended_hospital) && (
        <div className="p-3 bg-black/40 rounded-2xl border border-emerald-500/40 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              {language === 'te' ? 'సిఫార్సు చేయబడిన సురక్షిత కేంద్రాలు' : 'Recommended Safe Havens'}
            </span>
            <button
              onClick={() => navigate('/map')}
              className="text-[11px] text-cyan-400 hover:text-cyan-300 font-bold flex items-center gap-1 underline"
            >
              <Compass className="w-3.5 h-3.5" />
              <span>{language === 'te' ? 'మ్యాప్‌లో చూడండి' : 'Open GIS Map'}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {/* Shelter Recommendation */}
            {guidanceData.recommended_shelter && (
              <div className="p-2.5 rounded-xl bg-slate-900/90 border border-emerald-500/30 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-emerald-400 uppercase">
                    🛡️ {language === 'te' ? 'పునరావాస శిబిరం' : 'Safe Shelter'}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    ~{guidanceData.recommended_shelter.distance_km} km
                  </span>
                </div>
                <h5 className="text-xs font-bold text-white truncate">
                  {guidanceData.recommended_shelter.name}
                </h5>
                <p className="text-[10px] text-slate-400">
                  {guidanceData.recommended_shelter.distance_label} • {guidanceData.recommended_shelter.capacity_or_beds || 'Safe High Ground'}
                </p>
              </div>
            )}

            {/* Hospital Recommendation */}
            {guidanceData.recommended_hospital && (
              <div className="p-2.5 rounded-xl bg-slate-900/90 border border-blue-500/30 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-blue-400 uppercase">
                    🏥 {language === 'te' ? 'ఆసుపత్రి' : 'Hospital'}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    ~{guidanceData.recommended_hospital.distance_km} km
                  </span>
                </div>
                <h5 className="text-xs font-bold text-white truncate">
                  {guidanceData.recommended_hospital.name}
                </h5>
                <p className="text-[10px] text-slate-400">
                  {guidanceData.recommended_hospital.distance_label} • {guidanceData.recommended_hospital.capacity_or_beds || 'Emergency Medical'}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Distress Summary */}
      <div className="p-3 bg-black/30 rounded-xl border border-slate-800 space-y-2">
        <div className="flex items-center justify-between text-[11px]">
          <span className="text-slate-400">Emergency ID:</span>
          <span className="text-white font-bold">{refCode}</span>
        </div>
        <div className="text-slate-300 text-xs">
          "{activeSOS.message}"
        </div>
        {activeSOS.latitude && activeSOS.longitude && (
          <div className="flex items-center gap-1 text-[10px] text-emerald-400">
            <MapPin className="w-3 h-3" />
            <span>GPS: [{activeSOS.latitude.toFixed(4)}, {activeSOS.longitude.toFixed(4)}]</span>
          </div>
        )}
      </div>

      {/* Continuous Emergency Updates Section */}
      <div className="space-y-2 pt-1 border-t border-slate-800/80">
        <div className="flex items-center justify-between">
          <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
            <Radio className="w-3 h-3 text-rose-400 animate-pulse" />
            {language === 'te' ? 'అత్యవసర సమాచారం పంపండి:' : 'Send Emergency Update:'}
          </span>
          <button
            onClick={() => setShowUpdatesList(!showUpdatesList)}
            className="text-[10px] text-indigo-400 hover:text-indigo-300 underline"
          >
            {updates.length} {updates.length === 1 ? 'update' : 'updates'} ({showUpdatesList ? 'hide' : 'view'})
          </button>
        </div>

        {/* Multilingual Voice Update Recorder */}
        <VoiceSOSRecorder />

        {/* Quick Update Buttons */}
        <div className="grid grid-cols-2 gap-1.5">
          {QUICK_UPDATES.map((btn, idx) => (
            <button
              key={idx}
              onClick={() => handleSendUpdate(btn.type, btn.text)}
              disabled={isSending}
              className="text-left px-2 py-1.5 rounded-lg bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 text-[10px] text-slate-200 transition-colors flex items-center justify-between disabled:opacity-50"
            >
              <span className="truncate">{btn.label}</span>
            </button>
          ))}
          <button
            onClick={handleUpdateLocation}
            disabled={isSending}
            className="text-left px-2 py-1.5 rounded-lg bg-emerald-950/40 hover:bg-emerald-900/50 border border-emerald-500/40 text-[10px] text-emerald-300 transition-colors flex items-center justify-between disabled:opacity-50"
          >
            <span>📍 Update my location</span>
          </button>
        </div>

        {/* Custom Text Update Input */}
        <div className="flex gap-1.5 pt-1">
          <input
            type="text"
            value={customUpdate}
            onChange={(e) => setCustomUpdate(e.target.value)}
            placeholder={language === 'te' ? 'పరిస్థితి వివరాలు టైప్ చేయండి...' : 'Type situation update...'}
            className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSendUpdate('TEXT_UPDATE', customUpdate);
            }}
          />
          <button
            onClick={() => handleSendUpdate('TEXT_UPDATE', customUpdate)}
            disabled={isSending || !customUpdate.trim()}
            className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold transition-colors shrink-0 flex items-center gap-1"
          >
            <Send className="w-3 h-3" />
            <span>Update</span>
          </button>
        </div>

        {/* Updates History List (when expanded) */}
        {showUpdatesList && updates.length > 0 && (
          <div className="space-y-1.5 pt-2 max-h-40 overflow-y-auto">
            {updates.map((u, i) => (
              <div key={u.id || i} className="p-2 bg-slate-900/90 rounded-lg border border-slate-800 text-[11px] space-y-0.5">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-slate-300 uppercase">{u.updateType}</span>
                  <span className={u.status === 'RECEIVED' ? 'text-emerald-400' : 'text-amber-400'}>
                    {u.status === 'RECEIVED' ? '✓ Received' : '🟡 Saved locally • waiting for communication'}
                  </span>
                </div>
                {u.message && <p className="text-slate-200">"{u.message}"</p>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Offline sync note */}
      {!isOnline && (
        <div className="p-2 rounded-lg bg-amber-950/30 border border-amber-500/40 text-[10px] text-amber-300 flex items-center gap-1.5">
          <CircleDot className="w-3 h-3 animate-pulse text-amber-400 shrink-0" />
          <span>Offline mode: Saved locally • waiting for communication. Synchronizes automatically when connection resumes.</span>
        </div>
      )}
    </div>
  );
};
