import React from 'react';
import { motion, useReducedMotion, TargetAndTransition } from 'framer-motion';
import { AlertTriangle, Radio } from 'lucide-react';

interface EmergencySOSButtonProps {
  active?: boolean;
  onClick?: () => void;
  size?: 'md' | 'lg';
  className?: string;
}

export const EmergencySOSButton: React.FC<EmergencySOSButtonProps> = ({
  active = false,
  onClick,
  size = 'md',
  className = '',
}) => {
  const shouldReduceMotion = useReducedMotion();

  // Pulse animation states
  const getPulseVariant = (): TargetAndTransition => {
    if (shouldReduceMotion) return {};

    if (active) {
      return {
        scale: [1, 1.04, 1],
        boxShadow: [
          '0 0 20px rgba(239, 68, 68, 0.4), 0 0 0 0 rgba(239, 68, 68, 0.6)',
          '0 0 40px rgba(239, 68, 68, 0.7), 0 0 0 16px rgba(239, 68, 68, 0)',
          '0 0 20px rgba(239, 68, 68, 0.4), 0 0 0 0 rgba(239, 68, 68, 0.6)',
        ],
        transition: {
          duration: 1.4,
          repeat: Infinity,
          ease: 'easeInOut',
        },
      };
    }

    return {
      scale: [1, 1.02, 1],
      boxShadow: [
        '0 0 15px rgba(239, 68, 68, 0.2), 0 0 0 0 rgba(239, 68, 68, 0.3)',
        '0 0 25px rgba(239, 68, 68, 0.4), 0 0 0 10px rgba(239, 68, 68, 0)',
        '0 0 15px rgba(239, 68, 68, 0.2), 0 0 0 0 rgba(239, 68, 68, 0.3)',
      ],
      transition: {
        duration: 2.6,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    };
  };

  const dimensions = size === 'lg' ? 'px-8 py-5 text-lg' : 'px-6 py-3.5 text-sm';

  return (
    <motion.button
      type="button"
      role="button"
      aria-label={active ? "Emergency SOS Beacon is Active" : "Trigger Emergency Distress Beacon"}
      onClick={onClick}
      animate={getPulseVariant()}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.96 }}
      transition={{ type: 'spring', stiffness: 300, damping: 18 }}
      className={`relative inline-flex items-center justify-center font-bold tracking-wider uppercase rounded-xl transition-colors cursor-pointer select-none border ${
        active
          ? 'bg-red-600 hover:bg-red-500 text-white border-red-400'
          : 'bg-gradient-to-r from-red-600 via-rose-600 to-red-700 hover:from-red-500 hover:to-rose-600 text-white border-red-500/40'
      } ${dimensions} ${className}`}
    >
      <span className="relative z-10 flex items-center space-x-2.5">
        {active ? (
          <Radio className="w-5 h-5 text-white animate-pulse" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-red-100" />
        )}
        <span>{active ? 'SOS DISPATCH ACTIVE' : 'EMERGENCY SOS'}</span>
      </span>

      {/* Subtle indicator ring */}
      {active && (
        <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-yellow-300"></span>
        </span>
      )}
    </motion.button>
  );
};
