import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot,
  Send,
  Sparkles,
  ShieldAlert,
  HeartPulse,
  CloudRain,
  Radio,
  RefreshCw,
  HelpCircle,
  Lightbulb,
  CornerDownLeft,
  User,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Trash2,
  Layers,
  ChevronRight
} from 'lucide-react';
import { sendAIChat, ChatMessage } from '../../services/aiService';
import { useDisaster } from '../../context/DisasterContext';

interface EmergencyAIAssistantProps {
  onOpenSafetyPlan?: () => void;
  compact?: boolean;
}

interface ExtendedMessage extends ChatMessage {
  suggested_actions?: string[];
  emergency_level?: string;
  severity?: string;
  sources?: string[];
  recommendations?: string[];
  warnings?: string[];
  data_freshness?: string;
}

const PERSONAS = [
  {
    id: 'COMMAND_DISPATCHER',
    label: 'Command Dispatcher',
    description: 'Tactical emergency ops & resource allocation',
    icon: Radio,
    color: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  },
  {
    id: 'CITIZEN_GUIDE',
    label: 'Citizen Guide',
    description: 'Calm, clear evacuation & survival steps',
    icon: Bot,
    color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  },
  {
    id: 'FIRST_AID',
    label: 'Medical & First Aid',
    description: 'Triage, hypothermia & injury care',
    icon: HeartPulse,
    color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
  },
  {
    id: 'HYDROLOGY_ANALYST',
    label: 'Hydrology Analyst',
    description: 'Sensor telemetry, rainfall & basin runoff',
    icon: CloudRain,
    color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
  },
];

const QUICK_ACTIONS = [
  'Current Situation',
  'Critical Incidents',
  'Generate Briefing',
  'Explain Flood Risk',
  'Rescue Status',
  'Active Alerts',
  'Find Safest Shelter',
];

export const EmergencyAIAssistant: React.FC<EmergencyAIAssistantProps> = ({
  onOpenSafetyPlan,
  compact = false,
}) => {
  const { alerts, dashboardStats } = useDisaster();
  const [persona, setPersona] = useState<string>('COMMAND_DISPATCHER');
  const [inputMessage, setInputMessage] = useState<string>('');
  const [messages, setMessages] = useState<ExtendedMessage[]>([
    {
      role: 'assistant',
      content:
        '**AI EMERGENCY DECISION SUPPORT ONLINE**\n\nI am synchronized with authoritative PostgreSQL tables, Scikit-Learn ML models, and live telemetry feeds. Select a quick action below or ask any operational query regarding flood risk, unassigned distress calls, shelter routing, or field rescue dispatch.',
      suggested_actions: [
        'Current Situation',
        'Critical Incidents',
        'Generate Briefing',
      ],
      emergency_level: 'INFO',
      severity: 'INFO',
      sources: ['PostgreSQL 18 + PostGIS', 'Scikit-Learn ML Registry v2.0'],
      data_freshness: 'Live Database Snapshot',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || isLoading) return;

    const userMsg: ExtendedMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMessage('');
    setIsLoading(true);

    try {
      const response = await sendAIChat(
        text,
        persona,
        messages.map((m) => ({ role: m.role, content: m.content })),
        {
          activeAlertCount: alerts.length,
          rainfallMm: dashboardStats.rainfallMm,
          floodRisk: dashboardStats.floodRiskPercent,
        }
      );

      const assistantMsg: ExtendedMessage = {
        role: 'assistant',
        content: response.answer || response.reply,
        suggested_actions: response.suggested_actions || response.recommendations,
        emergency_level: response.emergency_level,
        severity: response.severity || response.emergency_level,
        sources: response.sources,
        recommendations: response.recommendations || response.suggested_actions,
        warnings: response.warnings,
        data_freshness: response.data_freshness || 'Live PostgreSQL & telemetry',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '⚠️ **AI Service Communication Error**\n\nUnable to reach backend AI reasoning engine. Primary database and real-time dashboard remain fully operational.',
          emergency_level: 'WARNING',
          severity: 'MODERATE',
          warnings: ['AI reasoning service temporarily unavailable.'],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: '**Conversation Reset.** Live emergency telemetry and database connection are active.',
        suggested_actions: ['Current Situation', 'Generate Briefing'],
        emergency_level: 'INFO',
        severity: 'INFO',
        sources: ['PostgreSQL 18 + PostGIS'],
        data_freshness: 'Live Database Snapshot',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
    ]);
  };

  const getSeverityBadgeClass = (sev?: string) => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/40';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
      case 'MODERATE':
      case 'WARNING':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'LOW':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
    }
  };

  return (
    <div
      className={`glass-panel rounded-2xl border border-gray-800 flex flex-col ${
        compact ? 'h-[520px]' : 'h-[740px]'
      } overflow-hidden shadow-2xl bg-command-card`}
    >
      {/* Top Header */}
      <div className="p-4 border-b border-gray-800/80 bg-gray-900/60 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20">
            <Bot className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-gray-100 text-sm font-mono tracking-wide">
                DISASTERGUARD AI AGENT
              </h3>
              <span className="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-[10px] font-mono font-bold flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> DECISION SUPPORT
              </span>
            </div>
            <p className="text-[11px] text-gray-400 font-mono flex items-center gap-2 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              PostgreSQL Grounded | {alerts.length} Active Alerts | {dashboardStats.rainfallMm}mm 24h Rain
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onOpenSafetyPlan && (
            <button
              onClick={onOpenSafetyPlan}
              className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-amber-600/30 to-orange-600/30 hover:from-amber-600/40 hover:to-orange-600/40 text-amber-300 border border-amber-500/40 text-xs font-mono font-semibold flex items-center gap-1.5 transition-all shadow-md"
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Safety Plan</span>
            </button>
          )}
          <button
            onClick={handleClearChat}
            title="Clear conversation"
            className="p-1.5 rounded-xl bg-gray-800/80 hover:bg-gray-700 text-gray-400 hover:text-gray-200 border border-gray-700 transition-all text-xs"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Persona Switcher Tabs */}
      <div className="px-4 py-2 bg-gray-950/40 border-b border-gray-800/60 flex items-center space-x-2 overflow-x-auto text-xs font-mono">
        <span className="text-gray-500 mr-1 flex items-center text-[11px]">
          <Activity className="w-3 h-3 mr-1" /> PERSONA:
        </span>
        {PERSONAS.map((p) => {
          const Icon = p.icon;
          const isActive = persona === p.id;
          return (
            <button
              key={p.id}
              onClick={() => setPersona(p.id)}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border transition-all whitespace-nowrap ${
                isActive
                  ? `${p.color} font-bold shadow-md`
                  : 'text-gray-400 border-gray-800 hover:text-gray-200 hover:bg-gray-800/40'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{p.label}</span>
            </button>
          );
        })}
      </div>

      {/* Chat Messages Log */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 font-sans text-sm">
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={idx}
              className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}
            >
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                  isUser
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-800 text-cyan-400 border border-cyan-500/30'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`max-w-[85%] rounded-2xl p-4 border transition-all ${
                  isUser
                    ? 'bg-blue-600/20 border-blue-500/40 text-gray-100'
                    : 'bg-gray-900/80 border-gray-800 text-gray-200 shadow-md'
                }`}
              >
                <div className="flex items-center justify-between gap-4 mb-2 text-[11px] font-mono text-gray-400">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-300">
                      {isUser ? 'Operator' : 'DisasterGuard Agent'}
                    </span>
                    {!isUser && msg.severity && (
                      <span className={`px-2 py-0.2 rounded text-[9px] font-bold border ${getSeverityBadgeClass(msg.severity)}`}>
                        {msg.severity}
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] text-gray-500">{msg.timestamp}</span>
                </div>

                {/* Body Text with Markdown formatting */}
                <div className="space-y-2 text-xs md:text-sm leading-relaxed whitespace-pre-line">
                  {msg.content.split('\n\n').map((paragraph, pIdx) => {
                    if (paragraph.startsWith('###')) {
                      return (
                        <h4 key={pIdx} className="font-bold text-cyan-300 text-sm border-b border-gray-800 pb-1 mt-1">
                          {paragraph.replace(/###\s*/, '')}
                        </h4>
                      );
                    }
                    if (paragraph.startsWith('•') || paragraph.startsWith('1.') || paragraph.startsWith('-')) {
                      return (
                        <div key={pIdx} className="pl-1 space-y-1 font-sans">
                          {paragraph.split('\n').map((line, lIdx) => (
                            <div key={lIdx} className="flex items-start gap-2">
                              <span className="text-cyan-400 mt-1">▸</span>
                              <span>{line.replace(/^[•\-\d\.]+\s*/, '')}</span>
                            </div>
                          ))}
                        </div>
                      );
                    }
                    return (
                      <p key={pIdx} className={paragraph.startsWith('**') ? 'font-semibold text-cyan-200' : ''}>
                        {paragraph.replace(/\*\*/g, '')}
                      </p>
                    );
                  })}
                </div>

                {/* Structured Recommendations Box */}
                {msg.recommendations && msg.recommendations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-800/80 bg-blue-950/20 rounded-xl p-2.5 border border-blue-900/30">
                    <span className="text-[10px] font-mono text-cyan-300 block mb-1.5 flex items-center gap-1 font-bold">
                      <Lightbulb className="w-3.5 h-3.5 text-amber-400" /> TACTICAL RECOMMENDATIONS (ADVISORY):
                    </span>
                    <div className="space-y-1">
                      {msg.recommendations.map((rec, rIdx) => (
                        <div key={rIdx} className="flex items-start gap-2 text-xs text-gray-300">
                          <ChevronRight className="w-3 h-3 text-cyan-400 mt-0.5 shrink-0" />
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Warnings Section */}
                {msg.warnings && msg.warnings.length > 0 && (
                  <div className="mt-2 p-2 rounded-lg bg-amber-950/20 border border-amber-800/40 text-[11px] text-amber-300/90 flex items-start gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 mt-0.5 shrink-0" />
                    <div>{msg.warnings.join(' ')}</div>
                  </div>
                )}

                {/* Suggested Action Chips */}
                {msg.suggested_actions && msg.suggested_actions.length > 0 && (
                  <div className="mt-2.5 pt-2 flex flex-wrap gap-1.5">
                    {msg.suggested_actions.map((act, aIdx) => (
                      <button
                        key={aIdx}
                        onClick={() => handleSendMessage(act)}
                        className="px-2.5 py-1 rounded-md bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-cyan-300 text-[11px] font-mono border border-gray-700 flex items-center gap-1 transition-all"
                      >
                        <span>{act}</span>
                        <CornerDownLeft className="w-2.5 h-2.5 text-gray-500" />
                      </button>
                    ))}
                  </div>
                )}

                {/* Sources & Freshness Footnote */}
                {!isUser && (
                  <div className="mt-3 pt-2 border-t border-gray-800/60 flex flex-wrap items-center justify-between text-[10px] font-mono text-gray-500 gap-2">
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                        <span>Grounded in: {msg.sources.slice(0, 4).join(' • ')}</span>
                      </div>
                    )}
                    {msg.data_freshness && (
                      <div className="flex items-center gap-1 text-gray-400">
                        <Clock className="w-3 h-3 text-cyan-400" />
                        <span>{msg.data_freshness}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-xl bg-gray-800 text-cyan-400 border border-cyan-500/30 flex items-center justify-center">
              <Bot className="w-4 h-4 animate-spin" />
            </div>
            <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-4 flex items-center space-x-2 text-xs font-mono text-gray-400">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
              <span>Querying PostgreSQL facts & executing AI decision support...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Inquiries Bar */}
      <div className="px-4 py-2.5 bg-gray-950/70 border-t border-gray-800/80 overflow-x-auto flex items-center space-x-2">
        <span className="text-[10px] font-mono text-gray-500 flex items-center shrink-0 font-bold">
          <HelpCircle className="w-3 h-3 mr-1 text-cyan-400" /> QUICK ACTIONS:
        </span>
        {QUICK_ACTIONS.map((prompt, pIdx) => (
          <button
            key={pIdx}
            onClick={() => handleSendMessage(prompt)}
            className="px-2.5 py-1 rounded-lg bg-gray-900 hover:bg-gray-800 border border-gray-800 hover:border-cyan-500/50 text-gray-300 hover:text-cyan-300 text-[11px] font-mono whitespace-nowrap transition-colors shadow-sm"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Message Input Box */}
      <div className="p-3 border-t border-gray-800 bg-gray-900/90 flex items-center space-x-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSendMessage();
          }}
          placeholder="Ask AI Agent anything about active incidents, flood predictions, or rescue status..."
          className="flex-1 bg-gray-950 border border-gray-800 rounded-xl px-4 py-2.5 text-xs md:text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors font-mono"
        />
        <button
          onClick={() => handleSendMessage()}
          disabled={!inputMessage.trim() || isLoading}
          className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-40 text-white rounded-xl font-mono text-xs font-bold flex items-center space-x-1.5 transition-all shadow-lg shadow-cyan-500/10"
        >
          <span>Send</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
