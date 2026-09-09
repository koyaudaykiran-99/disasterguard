import { RiskLevel } from '../types';

export interface RiskTheme {
  level: RiskLevel;
  label: string;
  sublabel: string;
  colorHex: string;
  bgGlow: string;
  borderClass: string;
  badgeBg: string;
  badgeText: string;
  cardGrad: string;
  pulseClass: string;
}

export const RISK_THEMES: Record<RiskLevel, RiskTheme> = {
  LOW: {
    level: 'LOW',
    label: 'LOW RISK',
    sublabel: 'You are currently in a relatively safe area.',
    colorHex: '#10B981',
    bgGlow: 'rgba(16, 185, 129, 0.12)',
    borderClass: 'border-emerald-500/30',
    badgeBg: 'bg-emerald-500/15',
    badgeText: 'text-emerald-400 border-emerald-500/30',
    cardGrad: 'from-emerald-950/30 via-slate-900/60 to-slate-950/80',
    pulseClass: '',
  },
  MODERATE: {
    level: 'MODERATE',
    label: 'MODERATE ADVISORY',
    sublabel: 'Monitor weather updates; water levels slightly rising.',
    colorHex: '#F59E0B',
    bgGlow: 'rgba(245, 158, 11, 0.15)',
    borderClass: 'border-amber-500/35',
    badgeBg: 'bg-amber-500/15',
    badgeText: 'text-amber-400 border-amber-500/35',
    cardGrad: 'from-amber-950/35 via-slate-900/60 to-slate-950/80',
    pulseClass: 'animate-pulse-subtle',
  },
  HIGH: {
    level: 'HIGH',
    label: 'HIGH RISK ALERT',
    sublabel: 'Localized waterlogging probable. Prepare emergency kit.',
    colorHex: '#F97316',
    bgGlow: 'rgba(249, 115, 22, 0.2)',
    borderClass: 'border-orange-500/45',
    badgeBg: 'bg-orange-500/20',
    badgeText: 'text-orange-400 border-orange-500/45',
    cardGrad: 'from-orange-950/40 via-slate-900/70 to-slate-950/80',
    pulseClass: 'animate-pulse-urgent',
  },
  CRITICAL: {
    level: 'CRITICAL',
    label: 'CRITICAL DANGER',
    sublabel: 'Immediate evacuation required. Proceed to higher ground.',
    colorHex: '#EF4444',
    bgGlow: 'rgba(239, 68, 68, 0.25)',
    borderClass: 'border-rose-500/60 shadow-glow-critical',
    badgeBg: 'bg-rose-500/25',
    badgeText: 'text-rose-300 border-rose-500/50',
    cardGrad: 'from-rose-950/50 via-slate-900/70 to-slate-950/90',
    pulseClass: 'animate-pulse-urgent',
  },
};

export const getRiskTheme = (score: number): RiskTheme => {
  if (score < 25) return RISK_THEMES.LOW;
  if (score < 50) return RISK_THEMES.MODERATE;
  if (score < 75) return RISK_THEMES.HIGH;
  return RISK_THEMES.CRITICAL;
};
