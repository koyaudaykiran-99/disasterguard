import React from 'react';
import { motion } from 'framer-motion';
import { listContainerVariants, listItemVariants } from '../../lib/animations';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface StaggeredListProps {
  children: React.ReactNode;
  className?: string;
}

export const StaggeredList: React.FC<StaggeredListProps> = ({ children, className = '' }) => {
  const reducedMotion = useReducedMotion();

  if (reducedMotion) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      variants={listContainerVariants}
      initial="hidden"
      animate="show"
      className={className}
    >
      {React.Children.map(children, (child) => {
        if (!React.isValidElement(child)) return child;
        return <motion.div variants={listItemVariants}>{child}</motion.div>;
      })}
    </motion.div>
  );
};
