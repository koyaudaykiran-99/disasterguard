import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageTransition } from '../components/motion/PageTransition';
import { useAuth } from '../context/AuthContext';
import {
  User,
  Phone,
  Mail,
  Users,
  CheckCircle2,
  Circle,
  Shield,
  LogOut,
  ShieldCheck,
} from 'lucide-react';

interface ChecklistItem {
  id: string;
  title: string;
  done: boolean;
}

export const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, safetyProfile, logout } = useAuth();

  const [checklist, setChecklist] = useState<ChecklistItem[]>([
    { id: 'c1', title: 'Drinking Water (3 Liters / Person / 3 Days)', done: true },
    { id: 'c2', title: 'Essential Family Medications & Prescriptions', done: true },
    { id: 'c3', title: 'Waterproof Bag for IDs, Passports & Land Deeds', done: true },
    { id: 'c4', title: 'Battery Power Bank & Multi-Charging Cables', done: true },
    { id: 'c5', title: 'High-Lumen LED Torch with Extra Cells', done: true },
    { id: 'c6', title: 'Emergency Whistle & High-Vis Reflective Band', done: false },
    { id: 'c7', title: 'First Aid Kit (Bandages, Antiseptic, Gauze)', done: false },
  ]);

  const toggleItem = (id: string) => {
    setChecklist((prev) =>
      prev.map((item) => (item.id === id ? { ...item, done: !item.done } : item))
    );
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const completedCount = checklist.filter((i) => i.done).length;
  const progressPercent = Math.round((completedCount / checklist.length) * 100);

  const displayName = user?.name || 'Citizen User';
  const displayEmail = user?.email || 'citizen@disasterguard.gov';
  const displayPhone = user?.phone || safetyProfile?.emergencyContactPhone || 'Not provided';
  const emergencyContact = safetyProfile?.emergencyContactName || 'Local Civil Defense Helpline (1077)';
  const emergencyPhone = safetyProfile?.emergencyContactPhone || '1077';

  return (
    <PageTransition className="space-y-4">
      {/* Citizen Identity Header Card */}
      <div className="glass-panel p-4 rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900/80 to-slate-950/80 flex items-center justify-between">
        <div className="flex items-center space-x-3.5">
          <div className="w-13 h-13 rounded-2xl bg-red-600/20 border border-red-500/30 text-red-500 flex items-center justify-center shrink-0">
            <User className="w-6 h-6" />
          </div>
          <div className="space-y-0.5">
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-white tracking-tight">{displayName}</h2>
              <span className="text-[9px] font-mono font-bold text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/40 flex items-center gap-1">
                <ShieldCheck className="w-2.5 h-2.5" />
                PROTECTED
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono flex items-center">
              <Mail className="w-3 h-3 mr-1 text-slate-500 shrink-0" />
              <span className="truncate max-w-[180px]">{displayEmail}</span>
            </p>
            {displayPhone && (
              <p className="text-xs text-slate-400 font-mono flex items-center">
                <Phone className="w-3 h-3 mr-1 text-slate-500 shrink-0" />
                <span>{displayPhone}</span>
              </p>
            )}
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          title="Sign Out of Emergency Account"
          className="p-2.5 rounded-xl bg-slate-900 hover:bg-red-950/50 text-slate-400 hover:text-red-400 border border-slate-800 hover:border-red-800/50 transition-colors shrink-0 focus:outline-none"
          aria-label="Sign out"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>

      {/* Household & Special Needs Card */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 space-y-2 text-xs font-mono">
        <div className="flex items-center justify-between">
          <span className="text-[10px] uppercase font-bold text-slate-400 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-red-400" />
            Safety & Emergency Contacts
          </span>
          <span className="text-slate-300 font-bold text-[11px]">Active Profile</span>
        </div>
        <div className="p-2.5 rounded-xl bg-slate-950/50 border border-slate-800 text-[11px] text-slate-300 flex items-center justify-between">
          <div>
            <span className="text-slate-400 block text-[10px]">Designated Next of Kin:</span>
            <strong className="text-white">{emergencyContact}</strong>
          </div>
          <a
            href={`tel:${emergencyPhone}`}
            className="px-2.5 py-1 rounded-lg bg-red-600/20 border border-red-500/30 hover:bg-red-600/30 text-red-400 font-bold text-xs transition-colors flex items-center gap-1"
          >
            <Phone className="w-3 h-3" />
            <span>{emergencyPhone}</span>
          </a>
        </div>
      </div>

      {/* Emergency Go-Bag Readiness Checklist */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              72-Hour Evacuation Go-Bag
            </h3>
          </div>
          <span className="text-xs font-mono font-bold text-emerald-400">
            {completedCount} / {checklist.length} ({progressPercent}%)
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
          <div
            className="h-full bg-emerald-500 rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Interactive Items */}
        <div className="space-y-2 pt-1">
          {checklist.map((item) => (
            <button
              key={item.id}
              onClick={() => toggleItem(item.id)}
              className="w-full flex items-center justify-between p-2.5 rounded-xl bg-slate-950/40 border border-slate-800/80 hover:border-slate-700 text-left transition-colors focus:outline-none"
            >
              <span
                className={`text-xs ${
                  item.done ? 'text-slate-400 line-through' : 'text-slate-200'
                }`}
              >
                {item.title}
              </span>
              {item.done ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 ml-2" />
              ) : (
                <Circle className="w-4 h-4 text-slate-600 shrink-0 ml-2" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Sign Out Action Card */}
      <div className="pt-2">
        <button
          onClick={handleLogout}
          className="w-full py-3 px-4 rounded-xl bg-slate-900/80 hover:bg-red-950/30 text-slate-400 hover:text-red-400 border border-slate-800 hover:border-red-900/50 text-xs font-bold transition-all flex items-center justify-center gap-2"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out of Emergency Protection Session</span>
        </button>
      </div>
    </PageTransition>
  );
};
