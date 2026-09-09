import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';

interface AuthCardProps {
  children: React.ReactNode;
  className?: string;
}

export const AuthCard: React.FC<AuthCardProps> = ({ children, className = '' }) => {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 18, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className={`relative z-10 w-full max-w-md mx-auto p-6 sm:p-8 rounded-3xl bg-white/90 backdrop-blur-xl border border-slate-200/90 shadow-[0_20px_50px_-12px_rgba(15,23,42,0.08),0_0_0_1px_rgba(15,23,42,0.03),inset_0_1px_1px_rgba(255,255,255,0.9)] transition-all ${className}`}
    >
      {/* Subtle top emergency indicator line */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-1 bg-gradient-to-r from-transparent via-red-500/80 to-transparent rounded-full" />
      {children}
    </motion.div>
  );
};
