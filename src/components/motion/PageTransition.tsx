import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { pageVariants } from '../../animations/variants';

interface PageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

export const PageTransition: React.FC<PageTransitionProps> = ({ children, className = '' }) => {
  const shouldReduceMotion = useReducedMotion();

  if (shouldReduceMotion) {
    return <div className={`w-full min-h-screen ${className}`}>{children}</div>;
  }

  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      className={`w-full min-h-screen ${className}`}
    >
      {children}
    </motion.div>
  );
};
