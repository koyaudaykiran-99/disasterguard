import { Transition } from 'framer-motion';

export const SPRING_PRESET: Transition = {
  type: 'spring',
  stiffness: 120,
  damping: 14,
  mass: 0.8,
};

export const FAST_EASE = [0.25, 0.1, 0.25, 1] as const;
export const SMOOTH_EASE = [0.16, 1, 0.3, 1] as const;

export const DURATION_PRESETS = {
  snappy: 0.2,
  standard: 0.35,
  expressive: 0.5,
  radarSweep: 3.0,
} as const;

/**
 * Utility to check if window reduced motion is requested
 */
export const isReducedMotionActive = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};
