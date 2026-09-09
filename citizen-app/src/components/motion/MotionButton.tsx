import React from 'react';
import { motion } from 'framer-motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface MotionButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
}

export const MotionButton: React.FC<MotionButtonProps> = ({
  children,
  className = '',
  variant = 'primary',
  disabled,
  onClick,
  ...props
}) => {
  const reducedMotion = useReducedMotion();

  const variantClasses = {
    primary: 'bg-citizen-accent hover:bg-cyan-400 text-slate-950 font-bold shadow-lg shadow-cyan-950/40',
    secondary: 'bg-slate-800 hover:bg-slate-700 text-citizen-text-primary border border-slate-700',
    danger: 'bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-950/50',
    ghost: 'bg-transparent hover:bg-slate-800/60 text-citizen-text-secondary hover:text-white',
  }[variant];

  return (
    <motion.button
      whileHover={!reducedMotion && !disabled ? { scale: 1.02 } : undefined}
      whileTap={!reducedMotion && !disabled ? { scale: 0.96 } : undefined}
      disabled={disabled}
      onClick={onClick}
      className={`min-h-[44px] px-4 py-2.5 rounded-xl font-medium text-sm flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-citizen-accent/50 disabled:opacity-50 disabled:cursor-not-allowed ${variantClasses} ${className}`}
      {...(props as any)}
    >
      {children}
    </motion.button>
  );
};
