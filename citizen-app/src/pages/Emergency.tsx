import React from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { EmergencySOSButton } from '../components/motion/EmergencySOSButton';
import { VoiceSOSRecorder } from '../components/emergency/VoiceSOSRecorder';
import { ActiveSOSQueueCard } from '../components/emergency/ActiveSOSQueueCard';
import { OfflineBanner } from '../components/connectivity/OfflineBanner';
import { AnimatedCard } from '../components/motion/AnimatedCard';
import { StaggeredList } from '../components/motion/StaggeredList';
import {
  AlertOctagon,
  PhoneCall,
  Flame,
  Waves,
} from 'lucide-react';

const EMERGENCY_SERVICES = [
  { name: 'National Emergency Helpline', number: '112', desc: 'Police, Fire, Ambulance', color: 'text-rose-400' },
  { name: 'Disaster Management Helpline', number: '1077', desc: 'District Collector Control Room', color: 'text-amber-400' },
  { name: 'Medical Emergency Ambulance', number: '108', desc: 'Trauma & Patient Transport', color: 'text-emerald-400' },
];

export const EmergencyPage: React.FC = () => {
  return (
    <PageTransition className="space-y-5">
      {/* Offline Connectivity Notification */}
      <OfflineBanner />

      {/* Header */}
      <div>
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <AlertOctagon className="w-5 h-5 text-rose-500" />
          Emergency Assistance
        </h2>
        <p className="text-xs text-citizen-text-muted font-mono mt-0.5">
          Distress Triggers & Direct Helplines
        </p>
      </div>

      {/* Real-time Emergency Queue Status (Shows queued offline & delivery states) */}
      <ActiveSOSQueueCard />

      {/* Prominent SOS Trigger */}
      <EmergencySOSButton />

      {/* Multilingual Voice SOS Trigger */}
      <VoiceSOSRecorder isInitialSOS={true} />

      {/* Direct Emergency Dials */}
      <div className="space-y-2.5">
        <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-citizen-text-muted px-1">
          Direct Helplines
        </h3>

        <div className="grid grid-cols-1 gap-2.5">
          {EMERGENCY_SERVICES.map((srv, idx) => (
            <a
              key={idx}
              href={`tel:${srv.number}`}
              className="glass-panel p-3.5 rounded-2xl border border-slate-800 hover:border-slate-700 flex items-center justify-between transition-colors group"
            >
              <div className="flex items-center space-x-3">
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-cyan-400 group-hover:scale-105 transition-transform">
                  <PhoneCall className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-white">{srv.name}</h4>
                  <p className="text-xs text-slate-400 font-mono">{srv.desc}</p>
                </div>
              </div>
              <span className={`text-lg font-black font-mono tracking-wider ${srv.color}`}>
                {srv.number}
              </span>
            </a>
          ))}
        </div>
      </div>

      {/* Immediate Survival Rules */}
      <div className="space-y-2.5">
        <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-citizen-text-muted px-1">
          Immediate Safety Guidelines
        </h3>

        <StaggeredList className="space-y-2 font-sans text-xs">
          <AnimatedCard className="border-cyan-500/20 space-y-1">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold font-mono">
              <Waves className="w-4 h-4" />
              <span>Flood Ground Rule</span>
            </div>
            <p className="text-slate-300 leading-relaxed">
              Never attempt to drive or walk through moving floodwaters. Just 15cm of flowing water can knock an adult off their feet.
            </p>
          </AnimatedCard>

          <AnimatedCard className="border-amber-500/20 space-y-1">
            <div className="flex items-center space-x-2 text-amber-400 font-bold font-mono">
              <Flame className="w-4 h-4" />
              <span>Electrical Isolation</span>
            </div>
            <p className="text-slate-300 leading-relaxed">
              Shut down main domestic electrical breakers before water enters dwelling ground levels to eliminate electrocution hazard.
            </p>
          </AnimatedCard>
        </StaggeredList>
      </div>
    </PageTransition>
  );
};
