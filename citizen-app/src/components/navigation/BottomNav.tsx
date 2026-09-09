import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Home, Map, Bell, AlertOctagon, User } from 'lucide-react';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface NavItem {
  id: string;
  label: string;
  path: string;
  icon: React.ElementType;
  isEmergency?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'home', label: 'Home', path: '/', icon: Home },
  { id: 'map', label: 'Map', path: '/map', icon: Map },
  { id: 'emergency', label: 'Emergency', path: '/emergency', icon: AlertOctagon, isEmergency: true },
  { id: 'alerts', label: 'Alerts', path: '/alerts', icon: Bell },
  { id: 'profile', label: 'Profile', path: '/profile', icon: User },
];

export const BottomNav: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 pointer-events-none pb-safe"
      aria-label="Citizen bottom navigation"
    >
      <div className="max-w-md mx-auto px-4 pb-2">
        <div className="glass-panel-elevated rounded-3xl p-1.5 border border-slate-700/80 shadow-2xl pointer-events-auto flex items-center justify-around">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                className={`relative flex flex-col items-center justify-center py-2 px-3 rounded-2xl min-h-[48px] min-w-[54px] transition-all focus:outline-none ${
                  isActive
                    ? item.isEmergency
                      ? 'text-rose-400'
                      : 'text-cyan-400 font-bold'
                    : 'text-citizen-text-muted hover:text-citizen-text-secondary'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                {/* Active Pill Indicator with spring physics */}
                {isActive && (
                  <motion.div
                    layoutId={reducedMotion ? undefined : 'activeNavIndicator'}
                    className={`absolute inset-0 rounded-2xl ${
                      item.isEmergency ? 'bg-rose-500/20 border border-rose-500/40' : 'bg-cyan-500/15 border border-cyan-500/30'
                    }`}
                    transition={{
                      type: 'spring',
                      stiffness: 350,
                      damping: 30,
                    }}
                  />
                )}

                <div className="relative z-10 flex flex-col items-center">
                  <Icon
                    className={`w-5 h-5 transition-transform ${
                      isActive ? 'scale-110' : 'scale-100'
                    } ${item.isEmergency && !isActive ? 'text-rose-400/80' : ''}`}
                  />
                  <span className="text-[10px] font-mono tracking-tight mt-1 font-medium">
                    {item.label}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};
