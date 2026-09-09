import React, { useState } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { mockUserProfile } from '../data/mock/user';
import {
  User,
  Phone,
  MapPin,
  Users,
  CheckCircle2,
  Circle,
  Shield,
} from 'lucide-react';

interface ChecklistItem {
  id: string;
  title: string;
  done: boolean;
}

export const ProfilePage: React.FC = () => {
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

  const completedCount = checklist.filter((i) => i.done).length;
  const progressPercent = Math.round((completedCount / checklist.length) * 100);

  return (
    <PageTransition className="space-y-4">
      {/* Citizen Identity Header Card */}
      <div className="glass-panel p-4 rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900/80 to-slate-950/80 flex items-center space-x-4">
        <div className="w-14 h-14 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 flex items-center justify-center shrink-0">
          <User className="w-7 h-7" />
        </div>
        <div className="space-y-0.5">
          <div className="flex items-center space-x-2">
            <h2 className="text-base font-bold text-white">{mockUserProfile.name}</h2>
            <span className="text-[10px] font-mono font-bold text-rose-400 bg-rose-950/60 px-2 py-0.5 rounded border border-rose-800/40">
              {mockUserProfile.bloodGroup}
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono flex items-center">
            <Phone className="w-3 h-3 mr-1 text-slate-500" />
            {mockUserProfile.phone}
          </p>
          <p className="text-xs text-slate-400 font-mono flex items-center">
            <MapPin className="w-3 h-3 mr-1 text-cyan-400" />
            {mockUserProfile.location}
          </p>
        </div>
      </div>

      {/* Household & Special Needs Card */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 space-y-2 text-xs font-mono">
        <div className="flex items-center justify-between">
          <span className="text-[10px] uppercase font-bold text-slate-400 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-cyan-400" />
            Household Triage Profile
          </span>
          <span className="text-cyan-400 font-bold">{mockUserProfile.householdMembers} Family Members</span>
        </div>
        <div className="p-2.5 rounded-xl bg-slate-950/50 border border-slate-800 text-[11px] text-slate-300">
          <span className="text-amber-400 font-bold block mb-0.5">Triage Vulnerability Flag:</span>
          {mockUserProfile.specialNeeds[0]}
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

      {/* Emergency Contacts List */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 space-y-2.5">
        <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
          Emergency Contacts
        </h3>
        <div className="space-y-2 font-mono text-xs">
          {mockUserProfile.emergencyContacts.map((contact, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-2 rounded-xl bg-slate-950/40 border border-slate-800"
            >
              <div>
                <span className="text-white font-bold block">{contact.name}</span>
                <span className="text-[10px] text-slate-400">{contact.relation}</span>
              </div>
              <a
                href={`tel:${contact.phone}`}
                className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 font-bold transition-colors"
              >
                {contact.phone}
              </a>
            </div>
          ))}
        </div>
      </div>
    </PageTransition>
  );
};
