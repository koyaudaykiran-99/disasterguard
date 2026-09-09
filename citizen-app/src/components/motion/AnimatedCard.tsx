import React from 'react';
import { motion } from 'framer-motion';
import { cardInteractiveVariants } from '../../lib/animations';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface AnimatedCardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  interactive?: boolean;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  className = '',
  onClick,
  interactive = true,
}) => {
  const reducedMotion = useReducedMotion();

  return (
    <motion.div
      variants={!reducedMotion && interactive ? cardInteractiveVariants : undefined}
      initial="rest"
      whileHover={!reducedMotion && interactive ? 'hover' : undefined}
      whileTap={!reducedMotion && interactive ? 'tap' : undefined}
      onClick={onClick}
      className={`glass-panel rounded-2xl p-4 transition-colors ${
        interactive ? 'cursor-pointer hover:border-citizen-accent/30' : ''
      } ${className}`}
    >
      {children}
    </motion.div>
  );
};
