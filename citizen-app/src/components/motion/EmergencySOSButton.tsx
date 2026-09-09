import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertOctagon, ShieldAlert, X, Info, CheckCircle2, RefreshCw, MapPin, Check, Send, Loader2 } from 'lucide-react';
import { sosBreathingVariants } from '../../lib/animations';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { useEmergencyQueue } from '../../hooks/useEmergencyQueue';
import { useConnectivity } from '../../hooks/useConnectivity';
import { useLocation } from '../../hooks/useLocation';
import { QueuedSOS } from '../../services/emergency/emergencyTypes';

interface EmergencySOSButtonProps {
  className?: string;
}

type ModalStep = 'CONFIRM' | 'SENDING' | 'SUCCESS_RECEIVED' | 'SAVED_LOCALLY' | 'DUPLICATE' | 'ERROR';

export const EmergencySOSButton: React.FC<EmergencySOSButtonProps> = ({ className = '' }) => {
  const reducedMotion = useReducedMotion();
  const { createSOS, activeSOS } = useEmergencyQueue();
  const { isOnline } = useConnectivity();
  const { coords, accuracy, locationName } = useLocation();

  const [modalOpen, setModalOpen] = useState(false);
  const [modalStep, setModalStep] = useState<ModalStep>('CONFIRM');
  const [currentSOS, setCurrentSOS] = useState<QueuedSOS | null>(null);

  const isPending = activeSOS !== null && activeSOS.status !== 'SENT' && activeSOS.status !== 'RECEIVED';

  const handleButtonClick = () => {
    if (activeSOS && activeSOS.status === 'RECEIVED') {
      setCurrentSOS(activeSOS);
      setModalStep('SUCCESS_RECEIVED');
      setModalOpen(true);
      return;
    }

    if (activeSOS && (activeSOS.status === 'WAITING_FOR_TRANSPORT' || activeSOS.status === 'LOCAL_QUEUED')) {
      setCurrentSOS(activeSOS);
      setModalStep('SAVED_LOCALLY');
      setModalOpen(true);
      return;
    }

    // Default: Open confirmation modal
    setModalStep('CONFIRM');
    setModalOpen(true);
  };

  const handleConfirmSend = async () => {
    setModalStep('SENDING');

    const result = await createSOS(
      'Critical flood distress signal. Immediate evacuation or emergency triage required.',
      'CRITICAL'
    );

    setCurrentSOS(result.sos);

    if (result.isDuplicate) {
      setModalStep('DUPLICATE');
    } else if (result.sos.status === 'RECEIVED') {
      setModalStep('SUCCESS_RECEIVED');
    } else {
      setModalStep('SAVED_LOCALLY');
    }
  };

  const formattedTime = currentSOS
    ? new Date(currentSOS.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const refCode = currentSOS?.backendSosId
    ? `#DG-${String(currentSOS.backendSosId).padStart(5, '0')}`
    : currentSOS?.id
    ? `#DG-${currentSOS.id.slice(-5).toUpperCase()}`
    : '#DG-00123';

  return (
    <>
      <div className={`w-full flex justify-center ${className}`}>
        <motion.button
          onClick={handleButtonClick}
          variants={reducedMotion ? undefined : sosBreathingVariants}
          animate={reducedMotion ? undefined : 'idle'}
          whileTap={reducedMotion ? undefined : 'tap'}
          aria-label="SOS Emergency Help Trigger"
          className={`relative w-full max-w-[340px] h-[78px] rounded-2xl p-[1.5px] shadow-sos cursor-pointer group focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 focus:ring-offset-citizen-bg transition-all ${
            isPending
              ? 'bg-gradient-to-r from-amber-600 via-rose-600 to-amber-700'
              : 'bg-gradient-to-r from-rose-600 via-red-600 to-rose-700'
          }`}
        >
          {/* Inner tactile layer with glass highlights */}
          <div className="w-full h-full rounded-[15px] bg-gradient-to-b from-red-600/90 to-rose-950/95 flex items-center justify-between px-6 border-t border-rose-400/40 relative overflow-hidden">
            {/* Ambient inner glow */}
            <div className="absolute inset-0 bg-radial from-rose-500/20 via-transparent to-transparent pointer-events-none" />

            <div className="flex items-center space-x-3.5 z-10">
              <div className="w-12 h-12 rounded-xl bg-rose-500/30 border border-rose-300/40 flex items-center justify-center shadow-inner group-hover:scale-105 transition-transform">
                <AlertOctagon className="w-7 h-7 text-white animate-pulse" />
              </div>
              <div className="text-left">
                <span className="text-xl font-black tracking-wider text-white font-mono flex items-center gap-1.5 leading-none">
                  SOS
                </span>
                <span className="text-xs font-semibold tracking-wide text-rose-200/90 block mt-1">
                  {isPending ? 'REQUEST ACTIVE IN QUEUE' : 'GET EMERGENCY HELP'}
                </span>
              </div>
            </div>

            {/* Tactical emergency badge */}
            <div className="z-10 flex flex-col items-end">
              <span className={`text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                isPending
                  ? 'bg-amber-900/60 text-amber-300 border-amber-500/40 animate-pulse'
                  : 'bg-rose-900/60 text-rose-300 border-rose-500/30'
              }`}>
                {isPending ? 'QUEUED' : '1-TAP'}
              </span>
              <span className="text-[9px] font-mono text-rose-200/70 mt-1">
                {isOnline ? 'Direct' : 'Offline'}
              </span>
            </div>
          </div>
        </motion.button>
      </div>

      {/* Emergency Modal Sequence */}
      <AnimatePresence>
        {modalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="glass-panel w-full max-w-sm rounded-3xl border border-rose-500/40 bg-citizen-surface p-5 shadow-2xl relative font-mono text-xs"
            >
              <button
                onClick={() => setModalOpen(false)}
                className="absolute top-4 right-4 p-1 rounded-lg text-citizen-text-muted hover:text-white transition-colors"
                aria-label="Close dialog"
              >
                <X className="w-5 h-5" />
              </button>

              {/* STEP 1: SOS CONFIRMATION */}
              {modalStep === 'CONFIRM' && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2.5 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-400">
                      <AlertOctagon className="w-6 h-6 animate-pulse" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-white uppercase tracking-wide">EMERGENCY SOS</h3>
                      <p className="text-[10px] text-rose-300">Command Centre Transmission</p>
                    </div>
                  </div>

                  <p className="text-slate-300 leading-relaxed font-sans text-xs">
                    Send your emergency distress signal and precise location to the DisasterGuard Command Centre?
                  </p>

                  <div className="bg-slate-950/70 p-3 rounded-2xl border border-slate-800 space-y-2 text-[11px]">
                    <div className="flex items-center justify-between text-slate-300">
                      <span className="flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                        Location:
                      </span>
                      <span className="text-emerald-400 font-bold flex items-center gap-1">
                        <Check className="w-3.5 h-3.5" />
                        {coords ? `${coords.latitude.toFixed(3)}°, ${coords.longitude.toFixed(3)}°` : 'Available (Default Fix)'}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-slate-300">
                      <span>Accuracy:</span>
                      <span className="text-cyan-300 font-bold">
                        ±{accuracy ? Math.round(accuracy) : 12} m
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-slate-300 border-t border-slate-800/80 pt-1.5">
                      <span>Connectivity:</span>
                      <span className={`font-bold ${isOnline ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {isOnline ? 'Direct HTTPS' : 'Offline (Local Queue)'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pt-1">
                    <button
                      onClick={handleConfirmSend}
                      className="flex-1 py-3 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-sos active:scale-95 transition-all"
                    >
                      <Send className="w-4 h-4" />
                      <span>SEND SOS</span>
                    </button>
                    <button
                      onClick={() => setModalOpen(false)}
                      className="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs transition-colors"
                    >
                      CANCEL
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 2: SENDING / TRANSMITTING */}
              {modalStep === 'SENDING' && (
                <div className="py-6 text-center space-y-3">
                  <Loader2 className="w-10 h-10 text-rose-500 animate-spin mx-auto" />
                  <h3 className="font-bold text-sm text-white">TRANSMITTING DISTRESS SIGNAL</h3>
                  <p className="text-slate-400 text-xs font-sans">
                    Locking satellite GPS telemetry and dispatching to DisasterGuard Command Centre...
                  </p>
                </div>
              )}

              {/* STEP 3: SUCCESS CONFIRMATION (Command Centre Received) */}
              {modalStep === 'SUCCESS_RECEIVED' && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400">
                      <CheckCircle2 className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-white uppercase tracking-wide">SOS RECEIVED</h3>
                      <p className="text-[10px] text-emerald-400">Command Centre Acknowledged</p>
                    </div>
                  </div>

                  <p className="text-slate-300 leading-relaxed font-sans text-xs">
                    The DisasterGuard Command Centre has received your emergency request.
                  </p>

                  <div className="bg-slate-950/70 p-3 rounded-2xl border border-slate-800 space-y-2 text-[11px]">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Reference:</span>
                      <span className="text-cyan-400 font-bold font-mono">{refCode}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Location:</span>
                      <span className="text-emerald-400 font-bold flex items-center gap-1">
                        <Check className="w-3.5 h-3.5" /> Shared
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Time:</span>
                      <span className="text-white font-bold">{formattedTime}</span>
                    </div>
                    <div className="flex items-center justify-between border-t border-slate-800/80 pt-1.5">
                      <span className="text-slate-400">Status:</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">
                        RECEIVED
                      </span>
                    </div>
                  </div>

                  <p className="text-[10px] text-slate-400 font-sans text-center leading-relaxed">
                    Emergency request recorded in Command Centre database. Incident triage and rescue unit matching are underway.
                  </p>

                  <button
                    onClick={() => setModalOpen(false)}
                    className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition-colors"
                  >
                    View Emergency Status
                  </button>
                </div>
              )}

              {/* STEP 4: OFFLINE - STORED IN INDEXEDDB */}
              {modalStep === 'SAVED_LOCALLY' && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2.5 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-400">
                      <AlertOctagon className="w-6 h-6 animate-pulse" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-white uppercase tracking-wide">SOS SAVED LOCALLY</h3>
                      <p className="text-[10px] text-rose-300">IndexedDB Device Queue</p>
                    </div>
                  </div>

                  <div className="bg-rose-950/30 border border-rose-800/40 rounded-xl p-3 space-y-2 text-rose-200">
                    <div className="flex items-start gap-2">
                      <Info className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                      <p className="leading-relaxed font-sans text-xs">
                        Your emergency request is <strong>stored securely on this device</strong>.
                      </p>
                    </div>
                    <p className="text-[11px] text-rose-300/80 leading-relaxed font-sans pl-6">
                      Communication unavailable. It will be transmitted automatically when a supported communication path becomes available.
                    </p>
                  </div>

                  <div className="bg-slate-950/70 p-3 rounded-2xl border border-slate-800 space-y-1.5 text-[11px] text-slate-300">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-cyan-400" /> GPS Telemetry:
                      </span>
                      <span className="text-cyan-400 font-bold">
                        {currentSOS?.latitude ? `${currentSOS.latitude.toFixed(3)}°, ${currentSOS.longitude?.toFixed(3)}°` : 'Stored'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Command Centre:</span>
                      <span className="text-amber-300 font-bold">Not yet received</span>
                    </div>
                  </div>

                  <button
                    onClick={() => setModalOpen(false)}
                    className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition-colors"
                  >
                    Close & Monitor Queue
                  </button>
                </div>
              )}

              {/* STEP 5: DUPLICATE PREVENTION */}
              {modalStep === 'DUPLICATE' && (
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="p-2.5 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-400">
                      <ShieldAlert className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-white">Active SOS Already Exists</h3>
                      <p className="text-[10px] text-amber-400">Duplicate Request Prevented</p>
                    </div>
                  </div>

                  <p className="text-slate-300 leading-relaxed font-sans text-xs">
                    Your previous emergency request is already safely queued and undergoing automatic dispatch attempts.
                  </p>

                  <button
                    onClick={() => setModalOpen(false)}
                    className="w-full mt-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition-colors"
                  >
                    Close
                  </button>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};
