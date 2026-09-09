import React, { useEffect, useState } from 'react';
import { useSpring, useMotionValue } from 'framer-motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface AnimatedCounterProps {
  value: number;
  className?: string;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  className = '',
}) => {
  const reducedMotion = useReducedMotion();
  const motionVal = useMotionValue(0);
  const springVal = useSpring(motionVal, {
    stiffness: 65,
    damping: 14,
    mass: 0.8,
  });
  const [displayVal, setDisplayVal] = useState<number>(reducedMotion ? value : 0);

  useEffect(() => {
    if (reducedMotion) {
      setDisplayVal(value);
      return;
    }
    motionVal.set(value);
    const unsubscribe = springVal.on('change', (latest) => {
      setDisplayVal(Math.round(latest));
    });
    return () => unsubscribe();
  }, [value, motionVal, springVal, reducedMotion]);

  return <span className={className}>{displayVal}</span>;
};
