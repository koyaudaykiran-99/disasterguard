import React from 'react';
import { RiskLevel } from '../../types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: RiskLevel | 'neutral' | 'info';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  className = '',
}) => {
  const variantStyles = {
    LOW: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    MODERATE: 'bg-amber-500/15 text-amber-300 border-amber-500/35',
    HIGH: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
    CRITICAL: 'bg-rose-500/25 text-rose-200 border-rose-500/50 animate-pulse',
    neutral: 'bg-slate-800 text-slate-300 border-slate-700',
    info: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  }[variant];

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider border ${variantStyles} ${className}`}
    >
      {children}
    </span>
  );
};
