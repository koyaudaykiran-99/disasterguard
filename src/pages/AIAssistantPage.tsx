import React, { useState } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { EmergencyAIAssistant } from '../components/ai/EmergencyAIAssistant';
import { RiskInterpretationCard } from '../components/ai/RiskInterpretationCard';
import { PersonalizedSafetyModal } from '../components/ai/PersonalizedSafetyModal';
import { Bot, Sparkles, ShieldCheck, Layers, HelpCircle, Activity } from 'lucide-react';

export const AIAssistantPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'CHAT' | 'RISK' | 'SAFETY'>('CHAT');
  const [isSafetyModalOpen, setIsSafetyModalOpen] = useState<boolean>(false);

  return (
    <PageTransition className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-gray-800">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-500 text-white shadow-xl shadow-blue-500/20">
            <Bot className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-gray-100 font-mono tracking-wide">
                EMERGENCY AI INTELLIGENCE SUITE
              </h2>
              <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-[10px] font-mono font-bold flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> GPT ASTRA ACTIVE
              </span>
            </div>
            <p className="text-xs text-gray-400 font-mono mt-1">
              Conversational Response Assistant, Personalized Survival Instructions & Hydrological Diagnostics
            </p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center space-x-2 bg-gray-900/90 p-1.5 rounded-2xl border border-gray-800 text-xs font-mono">
          <button
            onClick={() => setActiveTab('CHAT')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl transition-all ${
              activeTab === 'CHAT'
                ? 'bg-blue-600 text-white font-bold shadow-lg shadow-blue-600/30'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>AI Assistant</span>
          </button>

          <button
            onClick={() => setActiveTab('RISK')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl transition-all ${
              activeTab === 'RISK'
                ? 'bg-indigo-600 text-white font-bold shadow-lg shadow-indigo-600/30'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Risk Interpretation</span>
          </button>

          <button
            onClick={() => {
              setActiveTab('SAFETY');
              setIsSafetyModalOpen(true);
            }}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl transition-all ${
              activeTab === 'SAFETY'
                ? 'bg-amber-600 text-white font-bold shadow-lg shadow-amber-600/30'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Safety Instructions</span>
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {activeTab === 'CHAT' && (
        <EmergencyAIAssistant onOpenSafetyPlan={() => setIsSafetyModalOpen(true)} />
      )}

      {activeTab === 'RISK' && (
        <div className="space-y-6">
          <RiskInterpretationCard onOpenAssistant={() => setActiveTab('CHAT')} />
        </div>
      )}

      {activeTab === 'SAFETY' && (
        <div className="glass-panel p-12 text-center rounded-2xl border border-gray-800 space-y-4">
          <ShieldCheck className="w-12 h-12 text-amber-400 mx-auto" />
          <h3 className="text-lg font-bold text-gray-100 font-mono">
            Personalized Safety Plan Generator
          </h3>
          <p className="text-xs text-gray-400 font-mono max-w-md mx-auto">
            Configure your household size, dwelling type, and specific vulnerability factors to receive tailored survival checklists.
          </p>
          <button
            onClick={() => setIsSafetyModalOpen(true)}
            className="px-5 py-2.5 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-mono text-xs font-bold rounded-xl shadow-lg transition-all"
          >
            Open Interactive Safety Generator
          </button>
        </div>
      )}

      {/* Personalized Safety Modal */}
      <PersonalizedSafetyModal
        isOpen={isSafetyModalOpen}
        onClose={() => setIsSafetyModalOpen(false)}
      />
    </PageTransition>
  );
};
