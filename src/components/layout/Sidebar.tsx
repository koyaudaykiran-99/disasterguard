import React from 'react';
import {
  LayoutDashboard,
  BellRing,
  Map,
  Radio,
  ShieldCheck,
  User,
  Activity,
  Flame,
  Bot,
  Sparkles,
} from 'lucide-react';
import { useDisaster } from '../../context/DisasterContext';

interface SidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPath, onNavigate }) => {
  const { alerts, sosIncidents } = useDisaster();

  const activeSOSCount = sosIncidents.filter((s) => s.status !== 'RESCUED').length;
  const criticalAlertsCount = alerts.filter((a) => a.severity === 'CRITICAL').length;

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/ai-assistant', label: 'AI Assistant', icon: Bot, badgeText: 'LLM' },
    { path: '/alerts', label: 'Alerts', icon: BellRing, badge: criticalAlertsCount },
    { path: '/map', label: 'Command Map', icon: Map },
    { path: '/emergency', label: 'Emergency SOS', icon: Radio, badge: activeSOSCount, badgeDanger: true },
    { path: '/safe-zones', label: 'Safe Zones', icon: ShieldCheck },
    { path: '/profile', label: 'Profile & Auth', icon: User },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-screen flex flex-col justify-between p-4 relative z-30 select-none shadow-sm">
      <div>
        {/* Brand Header */}
        <div className="flex items-center space-x-3 px-2 py-3 mb-6">
          <div className="p-2.5 rounded-2xl bg-blue-50 border border-blue-200 text-blue-600 shadow-sm">
            <Flame className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-900 tracking-wider font-mono uppercase">
              DISASTERGUARD
            </h1>
            <span className="text-[10px] font-mono text-blue-600 font-bold tracking-widest block">
              AI COMMAND SYSTEM
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.path;

            return (
              <button
                key={item.path}
                onClick={() => onNavigate(item.path)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border border-blue-200 shadow-sm font-bold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80 border border-transparent'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>

                {item.badge !== undefined && item.badge > 0 && (
                  <span
                    className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded-full border ${
                      item.badgeDanger
                        ? 'bg-red-100 text-red-700 border-red-300 animate-pulse'
                        : 'bg-amber-100 text-amber-800 border-amber-300'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}

                {item.badgeText && (
                  <span className="px-2 py-0.5 text-[9px] font-mono font-bold rounded-full bg-cyan-100 text-cyan-800 border border-cyan-300 flex items-center gap-1 shadow-sm">
                    <Sparkles className="w-2.5 h-2.5" />
                    {item.badgeText}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Status Footnote */}
      <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 shadow-inner">
        <div className="flex items-center justify-between text-xs text-slate-600">
          <span className="flex items-center font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-ping"></span>
            PostGIS Engine
          </span>
          <span className="text-[10px] font-mono text-emerald-600 font-bold">ONLINE</span>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-600">
          <span className="flex items-center font-medium">
            <Activity className="w-3.5 h-3.5 mr-1.5 text-blue-600" />
            ML Pipeline
          </span>
          <span className="text-[10px] font-mono text-blue-600 font-bold">v4.2 HIGH</span>
        </div>
      </div>
    </aside>
  );
};
