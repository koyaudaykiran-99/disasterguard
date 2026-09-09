import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  ShieldCheck,
  Users,
  Baby,
  HeartPulse,
  Accessibility,
  Dog,
  Home,
  MapPin,
  Sparkles,
  CheckSquare,
  Square,
  AlertTriangle,
  Flame,
  Printer,
  Compass,
} from 'lucide-react';
import {
  generatePersonalizedSafety,
  PersonalizedSafetyRequest,
  PersonalizedSafetyResponse,
} from '../../services/aiService';

interface PersonalizedSafetyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PersonalizedSafetyModal: React.FC<PersonalizedSafetyModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [formData, setFormData] = useState<PersonalizedSafetyRequest>({
    disaster_type: 'FLOOD',
    location: 'Downtown Basin & Riverside',
    housing_type: 'GROUND_FLOOR',
    household_members: 3,
    has_elderly: true,
    has_children: false,
    has_pets: true,
    has_medical_needs: false,
    mobility_impaired: false,
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PersonalizedSafetyResponse | null>(null);
  const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>({});

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await generatePersonalizedSafety(formData);
      setResult(res);
      setCheckedItems({});
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleCheck = (id: string) => {
    setCheckedItems((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-3xl max-h-[90vh] rounded-3xl border border-gray-700/80 bg-command-card flex flex-col overflow-hidden shadow-2xl">
        {/* Modal Header */}
        <div className="p-5 border-b border-gray-800 bg-gray-900/80 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-amber-600 to-orange-500 text-white shadow-lg">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-gray-100 flex items-center gap-2">
                PERSONALIZED SAFETY INSTRUCTIONS
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                  AI CUSTOMIZED
                </span>
              </h3>
              <p className="text-xs text-gray-400 font-mono">
                Tailored Survival Protocols Based on Your Household Vulnerability Factors
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-gray-400 hover:text-gray-100 hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Demographic Inputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono text-gray-300 mb-1.5 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-cyan-400" /> Current Location / Sector:
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full bg-gray-950 border border-gray-800 rounded-xl px-3.5 py-2 text-xs text-gray-100 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-gray-300 mb-1.5 flex items-center gap-1.5">
                <Home className="w-3.5 h-3.5 text-cyan-400" /> Building & Dwelling Type:
              </label>
              <select
                value={formData.housing_type}
                onChange={(e) => setFormData({ ...formData, housing_type: e.target.value as any })}
                className="w-full bg-gray-950 border border-gray-800 rounded-xl px-3.5 py-2 text-xs text-gray-100 focus:outline-none focus:border-cyan-500"
              >
                <option value="GROUND_FLOOR">Ground Floor Flat / Duplex (High Risk)</option>
                <option value="BASEMENT">Basement Living Unit (Extreme Risk)</option>
                <option value="SINGLE_STORY">Single-Story Detached Bungalow</option>
                <option value="HIGH_RISE">High-Rise Apartment (Floor 3+)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-gray-300 mb-2 flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-blue-400" /> Household Members ({formData.household_members} People):
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.household_members}
              onChange={(e) => setFormData({ ...formData, household_members: parseInt(e.target.value) })}
              className="w-full accent-cyan-400 cursor-pointer"
            />
          </div>

          {/* Household Demographic Toggle Chips */}
          <div>
            <span className="block text-xs font-mono text-gray-300 mb-2">
              Select Specific Vulnerability Considerations:
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, has_elderly: !formData.has_elderly })}
                className={`p-3 rounded-xl border text-left flex items-center space-x-2.5 text-xs font-mono transition-all ${
                  formData.has_elderly
                    ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                    : 'bg-gray-950 border-gray-800 text-gray-400 hover:border-gray-700'
                }`}
              >
                <Users className="w-4 h-4 text-amber-400" />
                <span>Elderly (65+)</span>
              </button>

              <button
                type="button"
                onClick={() => setFormData({ ...formData, has_children: !formData.has_children })}
                className={`p-3 rounded-xl border text-left flex items-center space-x-2.5 text-xs font-mono transition-all ${
                  formData.has_children
                    ? 'bg-blue-500/20 border-blue-500/50 text-blue-300'
                    : 'bg-gray-950 border-gray-800 text-gray-400 hover:border-gray-700'
                }`}
              >
                <Baby className="w-4 h-4 text-blue-400" />
                <span>Infants / Children</span>
              </button>

              <button
                type="button"
                onClick={() => setFormData({ ...formData, has_pets: !formData.has_pets })}
                className={`p-3 rounded-xl border text-left flex items-center space-x-2.5 text-xs font-mono transition-all ${
                  formData.has_pets
                    ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                    : 'bg-gray-950 border-gray-800 text-gray-400 hover:border-gray-700'
                }`}
              >
                <Dog className="w-4 h-4 text-emerald-400" />
                <span>Pets / Animals</span>
              </button>

              <button
                type="button"
                onClick={() => setFormData({ ...formData, has_medical_needs: !formData.has_medical_needs })}
                className={`p-3 rounded-xl border text-left flex items-center space-x-2.5 text-xs font-mono transition-all ${
                  formData.has_medical_needs
                    ? 'bg-rose-500/20 border-rose-500/50 text-rose-300'
                    : 'bg-gray-950 border-gray-800 text-gray-400 hover:border-gray-700'
                }`}
              >
                <HeartPulse className="w-4 h-4 text-rose-400" />
                <span>Chronic Illness / Meds</span>
              </button>

              <button
                type="button"
                onClick={() => setFormData({ ...formData, mobility_impaired: !formData.mobility_impaired })}
                className={`p-3 rounded-xl border text-left flex items-center space-x-2.5 text-xs font-mono transition-all col-span-2 sm:col-span-1 ${
                  formData.mobility_impaired
                    ? 'bg-purple-500/20 border-purple-500/50 text-purple-300'
                    : 'bg-gray-950 border-gray-800 text-gray-400 hover:border-gray-700'
                }`}
              >
                <Accessibility className="w-4 h-4 text-purple-400" />
                <span>Mobility Assistance</span>
              </button>
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-mono text-xs font-bold uppercase tracking-wider flex items-center justify-center space-x-2 shadow-lg transition-all"
          >
            <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Analyzing Vulnerability Profile...' : 'Generate AI Personalized Safety Instructions'}</span>
          </button>

          {/* Generated Result Display */}
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-5 rounded-2xl bg-gray-900/90 border border-gray-800 space-y-5"
            >
              <div className="p-3.5 rounded-xl bg-cyan-950/30 border border-cyan-500/30 text-xs text-cyan-200 leading-relaxed font-sans">
                <strong>AI Summary:</strong> {result.summary}
              </div>

              {/* Immediate Actions Checklist */}
              <div>
                <h4 className="text-xs font-bold font-mono text-rose-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4" /> Immediate Protective Actions
                </h4>
                <div className="space-y-2">
                  {result.immediate_actions.map((act, i) => {
                    const id = `act-${i}`;
                    const checked = checkedItems[id];
                    return (
                      <div
                        key={id}
                        onClick={() => toggleCheck(id)}
                        className={`p-2.5 rounded-xl border flex items-start space-x-2.5 text-xs cursor-pointer transition-colors ${
                          checked
                            ? 'bg-emerald-950/20 border-emerald-500/40 text-gray-400 line-through'
                            : 'bg-gray-950 border-gray-800 text-gray-200 hover:border-gray-700'
                        }`}
                      >
                        {checked ? (
                          <CheckSquare className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        ) : (
                          <Square className="w-4 h-4 text-gray-500 shrink-0 mt-0.5" />
                        )}
                        <span>{act}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Go-Bag Supplies Required */}
              <div>
                <h4 className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4" /> Customized Emergency Pack (Go-Bag)
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {result.supplies_checklist.map((item, i) => {
                    const id = `sup-${i}`;
                    const checked = checkedItems[id];
                    return (
                      <div
                        key={id}
                        onClick={() => toggleCheck(id)}
                        className={`p-2 rounded-lg border flex items-center space-x-2 text-xs cursor-pointer ${
                          checked
                            ? 'bg-emerald-950/20 border-emerald-500/40 text-gray-400 line-through'
                            : 'bg-gray-950 border-gray-800 text-gray-300'
                        }`}
                      >
                        {checked ? (
                          <CheckSquare className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <Square className="w-3.5 h-3.5 text-gray-500 shrink-0" />
                        )}
                        <span className="truncate">{item}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Special Precautions (Elderly/Pets/Children) */}
              {result.special_precautions.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold font-mono text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <HeartPulse className="w-4 h-4" /> Special Household Precautions
                  </h4>
                  <ul className="space-y-1.5 pl-2 text-xs text-gray-300">
                    {result.special_precautions.map((p, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-amber-400 mt-1">▸</span>
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Family Communication Plan */}
              <div className="p-3.5 rounded-xl bg-gray-950 border border-gray-800 text-xs text-gray-300 space-y-1">
                <span className="font-mono text-[10px] text-blue-400 uppercase font-bold block">
                  Family Communication Protocol:
                </span>
                <p>{result.communication_plan}</p>
              </div>
            </motion.div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-gray-800 bg-gray-900/60 flex items-center justify-between text-xs font-mono text-gray-400">
          <span className="flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5 text-cyan-400" />
            Aligned with FEMA & NDMA Emergency Protocols
          </span>
          <button
            onClick={() => window.print()}
            className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 flex items-center gap-1.5 transition-colors"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print Checklist</span>
          </button>
        </div>
      </div>
    </div>
  );
};
