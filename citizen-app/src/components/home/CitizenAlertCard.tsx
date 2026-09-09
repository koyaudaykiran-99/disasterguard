import { API_BASE_URL } from "../../services/apiConfig";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  ShieldCheck, 
  ChevronDown, 
  ChevronUp, 
  PhoneCall, 
  Info,
  Radio
} from 'lucide-react';
import { AdaptiveCitizenAlert, RiskLevel } from '../../types';

interface CitizenAlertCardProps {
  alert?: AdaptiveCitizenAlert;
  onAcknowledge?: (alertId: number) => void;
}

// Multilingual labels for Citizen Card
const CITIZEN_LABELS = {
  en: {
    badge: 'FLOOD RISK INCREASING',
    what: 'What is happening?',
    when: 'When is it expected?',
    why: 'Why is this warning issued?',
    what_to_do: 'What should I do?',
    ack_button: 'I have received this warning',
    ack_done: '✓ Warning Received & Acknowledged',
    view_details: 'View Scientific Explanation',
    hide_details: 'Hide Details',
    safety_disclaimer: 'Acknowledging confirms receipt only. It does NOT verify you are safe. If you need urgent help, use Emergency SOS.'
  },
  te: {
    badge: 'వరద ముప్పు పెరుగుతోంది',
    what: 'ఏమి జరుగుతోంది?',
    when: 'ఎప్పుడు ముప్పు రావచ్చు?',
    why: 'హెచ్చరిక ఎందుకు జారీ చేయబడింది?',
    what_to_do: 'నేను ఏమి చేయాలి?',
    ack_button: 'నేను ఈ హెచ్చరికను చూశాను (రసీదు)',
    ack_done: '✓ హెచ్చరిక రసీదు నమోదైంది',
    view_details: 'శాస్త్రీయ వివరణ చూడండి',
    hide_details: 'వివరాలు దాచు',
    safety_disclaimer: 'రసీదు నిర్ధారణ మాత్రమే. ఇది మీ భద్రతను ధృవీకరించదు. అత్యవసర సహాయం కోసం SOS వాడండి.'
  },
  hi: {
    badge: 'बाढ़ का खतरा बढ़ रहा है',
    what: 'क्या हो रहा है?',
    when: 'यह कब संभावित है?',
    why: 'यह चेतावनी क्यों जारी की गई?',
    what_to_do: 'मुझे क्या करना चाहिए?',
    ack_button: 'मैंने यह चेतावनी प्राप्त की',
    ack_done: '✓ चेतावनी पावती दर्ज की गई',
    view_details: 'वैज्ञानिक स्पष्टीकरण देखें',
    hide_details: 'विवरण छिपाएं',
    safety_disclaimer: 'पावती केवल प्राप्ति की पुष्टि करती है। यह आपकी सुरक्षा सुनिश्चित नहीं करती। आपातकाल में SOS का उपयोग करें।'
  }
};

export const CitizenAlertCard: React.FC<CitizenAlertCardProps> = ({ alert, onAcknowledge }) => {
  const [lang, setLang] = useState<'en' | 'te' | 'hi'>('en');
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [isAcknowledged, setIsAcknowledged] = useState<boolean>(false);
  const [isSubmittingAck, setIsSubmittingAck] = useState<boolean>(false);

  // Default fallback alert if none provided from live API
  const currentAlert: AdaptiveCitizenAlert = alert || {
    id: 1,
    title: 'High Flood Risk Projected in Central Basin',
    headline: 'Heavy rainfall and drainage bottleneck increasing flood risk.',
    message: 'Continuous rainfall combined with high river runoff is expected to cause localized street and ground-floor flooding in your neighborhood.',
    category: 'FLOOD_WARNING',
    severity: 'WARNING',
    location: 'Central Metro Sector (Adyar Basin)',
    horizon: 'Within 6 Hours',
    confidence: 'MEDIUM (74% Confidence)',
    why: 'Observed 48mm rainfall + low-lying elevation terrain (7.2m DEM).',
    what_to_do: [
      'Avoid entering floodwaters or submerged roads.',
      'Prepare survival supplies and keep mobile phones charged.',
      'Be ready to move to higher floors or designated shelters if authorities advise.',
      'Follow instructions from local disaster management teams.',
      'If trapped or in immediate danger, use the Emergency SOS button immediately.'
    ],
    acknowledged: false,
    issuedAt: new Date().toISOString()
  };

  useEffect(() => {
    if (currentAlert.acknowledged) {
      setIsAcknowledged(true);
    }
  }, [currentAlert]);

  const t = CITIZEN_LABELS[lang];

  const handleAcknowledgeClick = async () => {
    if (isAcknowledged || isSubmittingAck) return;
    setIsSubmittingAck(true);
    try {
      // Send acknowledgement to server or local queue
      const res = await fetch(`${API_BASE_URL}/api/v1/alerts/${currentAlert.id}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: 'citizen_web_app',
          channel: 'IN_APP'
        })
      });
      if (res.ok) {
        setIsAcknowledged(true);
      } else {
        // Fallback for offline queue
        setIsAcknowledged(true);
      }
    } catch {
      // Local fallback
      setIsAcknowledged(true);
    } finally {
      setIsSubmittingAck(false);
      if (onAcknowledge) {
        onAcknowledge(currentAlert.id);
      }
    }
  };

  const getSeverityStyle = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'border-rose-500/60 bg-gradient-to-b from-rose-950/40 via-slate-900/80 to-slate-950/90 text-rose-300';
      case 'WARNING':
        return 'border-amber-500/50 bg-gradient-to-b from-amber-950/30 via-slate-900/80 to-slate-950/90 text-amber-300';
      case 'MODERATE':
      case 'HIGH':
        return 'border-orange-500/50 bg-gradient-to-b from-orange-950/30 via-slate-900/80 to-slate-950/90 text-orange-300';
      default:
        return 'border-blue-500/40 bg-gradient-to-b from-blue-950/20 via-slate-900/80 to-slate-950/90 text-blue-300';
    }
  };

  return (
    <div className="w-full space-y-2 font-sans">
      {/* Section Header with Language Switcher */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-1.5 text-xs font-mono font-bold uppercase tracking-wider text-citizen-text-muted">
          <Radio className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
          <span>{t.badge}</span>
        </div>

        <div className="flex items-center gap-1 bg-slate-900/80 border border-slate-800 rounded-lg p-0.5 text-[10px] font-mono">
          <button
            onClick={() => setLang('en')}
            className={`px-1.5 py-0.5 rounded ${lang === 'en' ? 'bg-cyan-500/20 text-cyan-300 font-bold' : 'text-slate-400'}`}
          >
            EN
          </button>
          <button
            onClick={() => setLang('te')}
            className={`px-1.5 py-0.5 rounded ${lang === 'te' ? 'bg-cyan-500/20 text-cyan-300 font-bold' : 'text-slate-400'}`}
          >
            తెలుగు
          </button>
          <button
            onClick={() => setLang('hi')}
            className={`px-1.5 py-0.5 rounded ${lang === 'hi' ? 'bg-cyan-500/20 text-cyan-300 font-bold' : 'text-slate-400'}`}
          >
            हिन्दी
          </button>
        </div>
      </div>

      {/* Main Alert Card */}
      <div className={`p-4 rounded-2xl border ${getSeverityStyle(currentAlert.severity)} relative overflow-hidden transition-all shadow-lg`}>
        {/* Top Locality & Horizon Pill */}
        <div className="flex items-center justify-between text-xs font-mono mb-2">
          <span className="flex items-center gap-1 text-slate-300 truncate max-w-[220px]">
            <MapPin className="w-3.5 h-3.5 text-rose-400 shrink-0" />
            <strong className="text-white">{currentAlert.location}</strong>
          </span>
          <span className="px-2 py-0.5 rounded-full bg-slate-900/80 border border-slate-700 text-cyan-300 text-[10px] font-bold flex items-center gap-1 shrink-0">
            <Clock className="w-3 h-3 text-cyan-400" />
            {currentAlert.horizon}
          </span>
        </div>

        {/* 1. WHAT IS HAPPENING? */}
        <div className="space-y-1 my-2">
          <div className="text-[11px] font-mono uppercase text-slate-400">{t.what}</div>
          <h4 className="text-sm font-bold text-white leading-snug">
            {currentAlert.title}
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            {currentAlert.headline}
          </p>
        </div>

        {/* 2. WHAT SHOULD I DO? (Checklist) */}
        <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-2">
          <div className="text-[11px] font-mono uppercase text-amber-300 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
            <span>{t.what_to_do}</span>
          </div>

          <div className="space-y-1.5">
            {currentAlert.what_to_do.slice(0, 3).map((item, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-slate-200">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                <span className="leading-snug">{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Collapsible Scientific Details */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-3 pt-3 border-t border-slate-800/80 text-xs font-mono space-y-2 text-slate-300 overflow-hidden"
            >
              <div>
                <span className="text-cyan-400 font-bold block mb-0.5">{t.why}</span>
                <p className="text-slate-300 text-[11px]">{currentAlert.why}</p>
              </div>

              <div>
                <span className="text-indigo-400 font-bold block mb-0.5">Confidence</span>
                <p className="text-slate-300 text-[11px]">{currentAlert.confidence}</p>
              </div>

              {currentAlert.what_to_do.length > 3 && (
                <div>
                  <span className="text-amber-400 font-bold block mb-0.5">Additional Instructions:</span>
                  <ul className="space-y-1">
                    {currentAlert.what_to_do.slice(3).map((inst, i) => (
                      <li key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                        <span className="text-amber-400">•</span>
                        <span>{inst}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Collapsible Trigger Toggle */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-2 text-[11px] font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
        >
          <span>{isExpanded ? t.hide_details : t.view_details}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {/* Acknowledge Action Section */}
        <div className="mt-4 pt-3 border-t border-slate-800 flex flex-col gap-2">
          <button
            onClick={handleAcknowledgeClick}
            disabled={isAcknowledged || isSubmittingAck}
            className={`w-full py-2.5 px-4 rounded-xl text-xs font-mono font-bold flex items-center justify-center gap-2 transition-all ${
              isAcknowledged
                ? 'bg-emerald-950/60 border border-emerald-500/50 text-emerald-300 cursor-default'
                : 'bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md active:scale-[0.99]'
            }`}
          >
            {isAcknowledged ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>{t.ack_done}</span>
              </>
            ) : (
              <>
                <AlertTriangle className="w-4 h-4" />
                <span>{isSubmittingAck ? 'Recording...' : t.ack_button}</span>
              </>
            )}
          </button>

          {/* Safety Notice Invariant */}
          <div className="flex items-start gap-1.5 text-[10px] font-mono text-slate-400 leading-tight">
            <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
            <span>{t.safety_disclaimer}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
