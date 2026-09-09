import React from 'react';
import { motion } from 'framer-motion';
import { pageVariants } from '../../lib/animations';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface PageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

export const PageTransition: React.FC<PageTransitionProps> = ({ children, className = '' }) => {
  const reducedMotion = useReducedMotion();

  if (reducedMotion) {
    return <div className={`w-full min-h-full ${className}`}>{children}</div>;
  }

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className={`w-full min-h-full ${className}`}
    >
      {children}
    </motion.div>
  );
};
