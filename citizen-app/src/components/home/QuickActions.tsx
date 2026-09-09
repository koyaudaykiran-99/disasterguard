import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Map, Home, Hospital, Bell, ChevronRight } from 'lucide-react';
import { cardInteractiveVariants } from '../../lib/animations';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface QuickActionItem {
  id: string;
  title: string;
  description: string;
  route: string;
  icon: React.ElementType;
  iconColor: string;
  bgGlow: string;
  borderColor: string;
}

const QUICK_ACTIONS: QuickActionItem[] = [
  {
    id: 'map',
    title: 'Safe Map',
    description: 'Find safe routes & risk zones',
    route: '/map',
    icon: Map,
    iconColor: 'text-cyan-400',
    bgGlow: 'bg-cyan-500/10',
    borderColor: 'group-hover:border-cyan-500/40',
  },
  {
    id: 'shelters',
    title: 'Shelters',
    description: 'Nearby emergency shelters',
    route: '/shelters',
    icon: Home,
    iconColor: 'text-emerald-400',
    bgGlow: 'bg-emerald-500/10',
    borderColor: 'group-hover:border-emerald-500/40',
  },
  {
    id: 'hospitals',
    title: 'Hospitals',
    description: 'Find nearby medical support',
    route: '/hospitals',
    icon: Hospital,
    iconColor: 'text-rose-400',
    bgGlow: 'bg-rose-500/10',
    borderColor: 'group-hover:border-rose-500/40',
  },
  {
    id: 'alerts',
    title: 'Alerts',
    description: 'Current disaster warnings',
    route: '/alerts',
    icon: Bell,
    iconColor: 'text-amber-400',
    bgGlow: 'bg-amber-500/10',
    borderColor: 'group-hover:border-amber-500/40',
  },
];

export const QuickActions: React.FC = () => {
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  return (
    <div className="w-full space-y-2.5">
      <div className="flex items-center justify-between px-1">
        <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-citizen-text-muted">
          Quick Actions
        </h3>
        <span className="text-[10px] font-mono text-cyan-400">Emergency Services</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {QUICK_ACTIONS.map((action) => {
          const Icon = action.icon;

          return (
            <motion.button
              key={action.id}
              onClick={() => navigate(action.route)}
              variants={!reducedMotion ? cardInteractiveVariants : undefined}
              initial="rest"
              whileHover={!reducedMotion ? 'hover' : undefined}
              whileTap={!reducedMotion ? 'tap' : undefined}
              className={`glass-panel p-3.5 rounded-2xl border border-slate-800 text-left flex flex-col justify-between h-[106px] group transition-all duration-200 focus:outline-none focus:ring-1 focus:ring-cyan-400/40 ${action.borderColor}`}
            >
              <div className="flex items-center justify-between w-full">
                <div className={`p-2 rounded-xl ${action.bgGlow} border border-slate-700/60`}>
                  <Icon className={`w-5 h-5 ${action.iconColor}`} />
                </div>
                <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-citizen-text-secondary group-hover:translate-x-0.5 transition-all" />
              </div>

              <div>
                <span className="font-bold text-sm text-white block group-hover:text-cyan-300 transition-colors">
                  {action.title}
                </span>
                <span className="text-[11px] text-citizen-text-muted leading-tight block mt-0.5 line-clamp-1">
                  {action.description}
                </span>
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
};
