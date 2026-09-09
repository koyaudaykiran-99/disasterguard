import React from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { AnimatedCard } from '../components/motion/AnimatedCard';
import { useAuth } from '../context/AuthContext';
import { UserCheck, Shield, Eye, Bell, Database, Key, CheckCircle } from 'lucide-react';
import { UserProfile } from '../types/disaster';

export const ProfilePage: React.FC = () => {
  const { user, toggleReducedMotion, toggleNotifications, updateUserRole } = useAuth();

  return (
    <PageTransition className="p-6 space-y-6">
      {/* Header */}
      <div className="glass-panel p-5 rounded-2xl border border-gray-800">
        <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
          <UserCheck className="w-6 h-6 text-blue-400" />
          Command Specialist Credentials & System Preferences
        </h2>
        <p className="text-xs text-gray-400 font-mono mt-1">
          JWT Authenticated Session & Motion Accessibility Preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Profile Card */}
        <div className="lg:col-span-6 space-y-4">
          <AnimatedCard className="!p-6 space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 text-2xl font-bold font-mono">
                {user.name.charAt(0)}
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-100">{user.name}</h3>
                <p className="text-xs font-mono text-cyan-400">{user.email}</p>
                <div className="mt-1 flex items-center space-x-2">
                  <span className="px-2.5 py-0.5 text-[10px] font-mono font-bold uppercase rounded bg-blue-500/20 text-blue-300 border border-blue-500/40">
                    {user.role}
                  </span>
                  <span className="text-[10px] font-mono text-gray-400">Badge: {user.badgeNumber}</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-800 space-y-2 text-xs font-mono text-gray-300">
              <div className="flex justify-between">
                <span className="text-gray-500">Station Base:</span>
                <span>{user.station}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Clearance Level:</span>
                <span className="text-emerald-400 font-bold">LEVEL 4 - DISPATCH</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">PostgreSQL Auth Protocol:</span>
                <span className="text-cyan-400">JWT + Spatial PostGIS RBAC</span>
              </div>
            </div>

            {/* Role Switcher */}
            <div className="pt-4 border-t border-gray-800 space-y-2">
              <label className="text-xs font-mono text-gray-400 block">Switch Command Role:</label>
              <div className="grid grid-cols-3 gap-2 text-xs font-mono">
                {(['DISPATCH_OFFICER', 'COMMAND_SPECIALIST', 'FIELD_RESPONDER'] as UserProfile['role'][]).map(
                  (role) => (
                    <button
                      key={role}
                      onClick={() => updateUserRole(role)}
                      className={`p-2 rounded-xl border text-center transition-colors ${
                        user.role === role
                          ? 'bg-blue-600/30 border-blue-500 text-blue-300 font-bold'
                          : 'bg-gray-900 border-gray-800 text-gray-400 hover:bg-gray-800'
                      }`}
                    >
                      {role.replace('_', ' ')}
                    </button>
                  )
                )}
              </div>
            </div>
          </AnimatedCard>
        </div>

        {/* Accessibility & Preferences */}
        <div className="lg:col-span-6 space-y-4">
          <AnimatedCard className="!p-6 space-y-5">
            <h3 className="text-sm font-bold font-mono text-gray-200 uppercase tracking-wider flex items-center gap-2">
              <Shield className="w-4 h-4 text-purple-400" />
              Motion & System Accessibility
            </h3>

            {/* Reduced Motion Setting */}
            <div className="flex items-center justify-between p-4 rounded-xl bg-gray-900/80 border border-gray-800">
              <div className="space-y-1">
                <div className="text-sm font-bold text-gray-200 flex items-center gap-2">
                  <Eye className="w-4 h-4 text-purple-400" />
                  Reduced Motion Accessibility
                </div>
                <p className="text-xs text-gray-400">
                  Respects <code className="text-purple-300">prefers-reduced-motion</code>. Disables radar sweeps, continuous pulses, and large translations.
                </p>
              </div>

              <button
                onClick={toggleReducedMotion}
                className={`w-12 h-6 rounded-full transition-colors relative border ${
                  user.prefersReducedMotion ? 'bg-purple-600 border-purple-400' : 'bg-gray-800 border-gray-700'
                }`}
              >
                <span
                  className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
                    user.prefersReducedMotion ? 'translate-x-6' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            {/* Emergency Broadcast Notifications */}
            <div className="flex items-center justify-between p-4 rounded-xl bg-gray-900/80 border border-gray-800">
              <div className="space-y-1">
                <div className="text-sm font-bold text-gray-200 flex items-center gap-2">
                  <Bell className="w-4 h-4 text-cyan-400" />
                  Emergency High-Priority Alerts
                </div>
                <p className="text-xs text-gray-400">
                  Receive immediate audio/visual broadcast notifications for CRITICAL risk score escalations.
                </p>
              </div>

              <button
                onClick={toggleNotifications}
                className={`w-12 h-6 rounded-full transition-colors relative border ${
                  user.notificationsEnabled ? 'bg-cyan-600 border-cyan-400' : 'bg-gray-800 border-gray-700'
                }`}
              >
                <span
                  className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
                    user.notificationsEnabled ? 'translate-x-6' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            <div className="p-3.5 rounded-xl bg-blue-950/20 border border-blue-500/30 text-xs font-mono text-blue-300 flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span>All motion system configurations are saved persistently per session.</span>
            </div>
          </AnimatedCard>
        </div>
      </div>
    </PageTransition>
  );
};
