import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, ArrowRight, Radio, MapPin, HeartPulse } from 'lucide-react';

interface StepProtectedSuccessProps {
  onEnterDashboard: () => void;
  userName: string;
}

export const StepProtectedSuccess: React.FC<StepProtectedSuccessProps> = ({
  onEnterDashboard,
  userName,
}) => {
  // Automatically redirect after 3 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      onEnterDashboard();
    }, 3000);
    return () => clearTimeout(timer);
  }, [onEnterDashboard]);

  return (
    <div className="text-center py-4 space-y-6">
      {/* Animated Protection Emblem */}
      <div className="relative flex items-center justify-center w-24 h-24 mx-auto">
        <motion.div
          className="absolute inset-0 rounded-full bg-red-500/10"
          animate={{ scale: [1, 1.35, 1], opacity: [0.6, 0.1, 0.6] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 260, damping: 20 }}
          className="w-20 h-20 rounded-full bg-gradient-to-b from-red-500 to-red-600 text-white flex items-center justify-center shadow-xl shadow-red-600/30 relative z-10"
        >
          <ShieldCheck className="w-10 h-10 stroke-[2.2]" />
        </motion.div>
      </div>

      <div className="space-y-1">
        <motion.h2
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="text-2xl font-black text-slate-900 tracking-tight"
        >
          You're Protected
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="text-xs text-slate-600 max-w-xs mx-auto"
        >
          Welcome, {userName || 'Citizen'}. AI-DisasterGuard is ready to help keep you safe.
        </motion.p>
      </div>

      {/* Armed Capabilities Verification List */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
        className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-left space-y-2 text-xs"
      >
        <div className="flex items-center gap-2.5 text-slate-700">
          <div className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
            <Radio className="w-3.5 h-3.5" />
          </div>
          <span className="font-semibold text-[11px]">Real-Time Disaster Feeds & Alerts Armed</span>
        </div>

        <div className="flex items-center gap-2.5 text-slate-700">
          <div className="w-6 h-6 rounded-lg bg-red-100 text-red-600 flex items-center justify-center shrink-0">
            <HeartPulse className="w-3.5 h-3.5" />
          </div>
          <span className="font-semibold text-[11px]">Instant Offline SOS & Rescue Priority Active</span>
        </div>

        <div className="flex items-center gap-2.5 text-slate-700">
          <div className="w-6 h-6 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center shrink-0">
            <MapPin className="w-3.5 h-3.5" />
          </div>
          <span className="font-semibold text-[11px]">Safe Evacuation Corridor & Shelter Radar Live</span>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.45 }}
      >
        <button
          onClick={onEnterDashboard}
          className="w-full py-3 px-4 rounded-xl bg-slate-900 hover:bg-black text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md transition-all"
        >
          <span>Enter Safety Dashboard</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </motion.div>
    </div>
  );
};
