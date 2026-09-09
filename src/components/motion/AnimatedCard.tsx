import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { cardVariants } from '../../animations/variants';

interface AnimatedCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  onClick?: () => void;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  className = '',
  delay = 0,
  onClick,
}) => {
  const shouldReduceMotion = useReducedMotion();

  if (shouldReduceMotion) {
    return (
      <div onClick={onClick} className={`glass-panel rounded-xl p-5 ${className}`}>
        {children}
      </div>
    );
  }

  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-20px' }}
      transition={{ delay }}
      variants={cardVariants}
      whileHover={{ y: -2, transition: { duration: 0.15 } }}
      onClick={onClick}
      className={`glass-panel-interactive rounded-xl p-5 shadow-lg ${className}`}
    >
      {children}
    </motion.div>
  );
};
