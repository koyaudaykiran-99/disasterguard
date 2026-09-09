import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { staggerContainerVariants, staggerItemVariants } from '../../animations/variants';

interface StaggeredListProps {
  children: React.ReactNode[];
  className?: string;
  staggerStepMs?: number;
}

export const StaggeredList: React.FC<StaggeredListProps> = ({
  children,
  className = 'space-y-4',
}) => {
  const shouldReduceMotion = useReducedMotion();

  if (shouldReduceMotion) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={staggerContainerVariants}
      className={className}
    >
      {React.Children.map(children, (child, idx) => (
        <motion.div key={idx} variants={staggerItemVariants}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
};
