import React from 'react';
import { motion } from 'framer-motion';
import { AnimatedCounter } from './AnimatedCounter';
import { getRiskTheme } from '../../lib/theme';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface RiskScoreProps {
  score: number; // 0 to 100
  size?: number;
  strokeWidth?: number;
}

export const RiskScore: React.FC<RiskScoreProps> = ({
  score,
  size = 170,
  strokeWidth = 12,
}) => {
  const reducedMotion = useReducedMotion();
  const theme = getRiskTheme(score);

  const radius = (size - strokeWidth * 2) / 2;
  const center = size / 2;
  
  // 240 degree gauge (leaves bottom 120 open)
  const arcDegree = 240;
  const fullCircumference = 2 * Math.PI * radius;
  const arcLength = (arcDegree / 360) * fullCircumference;
  
  // Percentage of arc filled
  const fillLength = (score / 100) * arcLength;
  const strokeDashoffset = arcLength - fillLength;

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-[210deg] overflow-visible"
      >
        <defs>
          <filter id="gaugeGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor={theme.colorHex} floodOpacity="0.45" />
          </filter>
        </defs>

        {/* Background Track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(51, 65, 85, 0.3)"
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${fullCircumference}`}
          strokeLinecap="round"
        />

        {/* Dynamic Foreground Animated Progress Track */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={theme.colorHex}
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${fullCircumference}`}
          initial={{ strokeDashoffset: arcLength }}
          animate={{ strokeDashoffset: reducedMotion ? strokeDashoffset : strokeDashoffset }}
          transition={{
            type: 'spring',
            stiffness: 55,
            damping: 14,
            delay: reducedMotion ? 0 : 0.4,
          }}
          strokeLinecap="round"
          filter="url(#gaugeGlow)"
        />
      </svg>

      {/* Center Numeric Typography */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pt-2 select-none">
        <span className="text-[10px] font-mono tracking-widest uppercase text-citizen-text-muted font-bold">
          Risk Index
        </span>
        <div className="flex items-baseline space-x-1 my-0.5">
          <AnimatedCounter
            value={score}
            className="text-4xl font-extrabold tracking-tight text-citizen-text-primary font-mono"
          />
          <span className="text-sm font-semibold text-citizen-text-muted font-mono">/100</span>
        </div>
        <span
          className="text-[11px] font-mono font-bold tracking-wider uppercase px-2 py-0.5 rounded-full border"
          style={{
            color: theme.colorHex,
            borderColor: `${theme.colorHex}40`,
            backgroundColor: `${theme.colorHex}15`,
          }}
        >
          {theme.label.split(' ')[0]}
        </span>
      </div>
    </div>
  );
};
