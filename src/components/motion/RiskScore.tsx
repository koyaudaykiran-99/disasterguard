import React from 'react';
import { motion, useReducedMotion, TargetAndTransition } from 'framer-motion';
import { RiskLevel } from '../../types/disaster';
import { AnimatedCounter } from './AnimatedCounter';

interface RiskScoreProps {
  score: number;
  level: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const RiskScore: React.FC<RiskScoreProps> = ({
  score,
  level,
  size = 'md',
  showLabel = true,
}) => {
  const shouldReduceMotion = useReducedMotion();

  const strokeWidth = size === 'sm' ? 6 : size === 'md' ? 8 : 10;
  const radius = size === 'sm' ? 38 : size === 'md' ? 52 : 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getColorClass = (riskLevel: RiskLevel) => {
    switch (riskLevel) {
      case 'LOW':
        return {
          stroke: '#10b981',
          text: 'text-emerald-400',
          bg: 'bg-emerald-500/10',
          border: 'border-emerald-500/20',
          glow: 'shadow-emerald-500/10',
        };
      case 'MODERATE':
        return {
          stroke: '#f59e0b',
          text: 'text-amber-400',
          bg: 'bg-amber-500/10',
          border: 'border-amber-500/20',
          glow: 'shadow-amber-500/15',
        };
      case 'HIGH':
        return {
          stroke: '#f97316',
          text: 'text-orange-400',
          bg: 'bg-orange-500/10',
          border: 'border-orange-500/30',
          glow: 'shadow-orange-500/25',
        };
      case 'CRITICAL':
        return {
          stroke: '#ef4444',
          text: 'text-rose-500',
          bg: 'bg-rose-500/15',
          border: 'border-rose-500/40',
          glow: 'shadow-rose-500/40',
        };
    }
  };

  const colors = getColorClass(level);

  const getPulseAnimation = (): TargetAndTransition => {
    if (shouldReduceMotion) return {};

    switch (level) {
      case 'LOW':
        return {};
      case 'MODERATE':
        return {
          scale: [1, 1.02, 1],
          transition: { duration: 3.5, repeat: Infinity, ease: 'easeInOut' },
        };
      case 'HIGH':
        return {
          scale: [1, 1.03, 1],
          boxShadow: [
            '0 0 15px rgba(249, 115, 22, 0.15)',
            '0 0 25px rgba(249, 115, 22, 0.35)',
            '0 0 15px rgba(249, 115, 22, 0.15)',
          ],
          transition: { duration: 2.2, repeat: Infinity, ease: 'easeInOut' },
        };
      case 'CRITICAL':
        return {
          scale: [1, 1.04, 1],
          boxShadow: [
            '0 0 20px rgba(239, 68, 68, 0.25)',
            '0 0 35px rgba(239, 68, 68, 0.55)',
            '0 0 20px rgba(239, 68, 68, 0.25)',
          ],
          transition: { duration: 1.5, repeat: Infinity, ease: 'easeInOut' },
        };
    }
  };

  const dim = size === 'sm' ? 90 : size === 'md' ? 120 : 160;

  return (
    <div className="flex flex-col items-center justify-center">
      <motion.div
        animate={getPulseAnimation()}
        className={`relative flex items-center justify-center rounded-full p-2 border ${colors.border} ${colors.bg} ${colors.glow}`}
        style={{ width: dim + 16, height: dim + 16 }}
      >
        <svg width={dim} height={dim} className="transform -rotate-90">
          {/* Background circle track */}
          <circle
            cx={dim / 2}
            cy={dim / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            className="text-gray-800/60"
          />
          {/* Animated progress ring */}
          <motion.circle
            cx={dim / 2}
            cy={dim / 2}
            r={radius}
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            fill="transparent"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{
              duration: shouldReduceMotion ? 0.1 : 1.2,
              ease: [0.16, 1, 0.3, 1],
            }}
          />
        </svg>

        {/* Counter and Label inside ring */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-xs uppercase tracking-wider text-gray-400 font-medium">Risk</span>
          <div className={`font-bold font-mono ${colors.text} ${size === 'sm' ? 'text-xl' : size === 'md' ? 'text-3xl' : 'text-4xl'}`}>
            <AnimatedCounter value={score} />
          </div>
          <span className="text-[10px] text-gray-500 font-mono">/ 100</span>
        </div>
      </motion.div>

      {showLabel && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mt-2 font-mono text-xs font-semibold tracking-widest uppercase px-3 py-1 rounded-full border ${colors.border} ${colors.bg} ${colors.text}`}
        >
          {level} RISK
        </motion.div>
      )}
    </div>
  );
};
