import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';

export const AuthNetworkBackground: React.FC = () => {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0 bg-[#FAFAFA]" aria-hidden="true">
      {/* Delicate ambient grid */}
      <div 
        className="absolute inset-0 opacity-[0.035]"
        style={{
          backgroundImage: `radial-gradient(#0F172A 1px, transparent 1px)`,
          backgroundSize: '24px 24px'
        }}
      />

      {/* Subtle emergency network lines (SVG) */}
      <svg className="absolute inset-0 w-full h-full opacity-40" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="netRed" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#EF4444" stopOpacity="0.15" />
            <stop offset="50%" stopColor="#94A3B8" stopOpacity="0.1" />
            <stop offset="100%" stopColor="#EF4444" stopOpacity="0.05" />
          </linearGradient>
        </defs>

        <path
          d="M -100,150 Q 200,80 450,220 T 900,160"
          fill="none"
          stroke="url(#netRed)"
          strokeWidth="1.5"
          strokeDasharray="4 6"
        />
        <path
          d="M -50,400 Q 250,320 500,480 T 1000,380"
          fill="none"
          stroke="url(#netRed)"
          strokeWidth="1.2"
        />
        <path
          d="M 100,-50 Q 300,300 150,600 T 400,900"
          fill="none"
          stroke="#E2E8F0"
          strokeWidth="1"
        />
      </svg>

      {/* Breathing emergency pulse nodes */}
      {!shouldReduceMotion && (
        <>
          <motion.div
            className="absolute top-1/4 left-1/5 w-72 h-72 rounded-full bg-red-500/[0.03] blur-3xl"
            animate={{
              scale: [1, 1.15, 1],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          <motion.div
            className="absolute bottom-1/4 right-1/5 w-80 h-80 rounded-full bg-slate-400/[0.04] blur-3xl"
            animate={{
              scale: [1.1, 1, 1.1],
              opacity: [0.4, 0.2, 0.4],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        </>
      )}
    </div>
  );
};
