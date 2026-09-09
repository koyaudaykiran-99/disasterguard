import { Variants, Transition } from 'framer-motion';

// Premium smooth spring physics
export const smoothSpring: Transition = {
  type: 'spring',
  stiffness: 120,
  damping: 18,
  mass: 0.8,
};

export const gentleSpring: Transition = {
  type: 'spring',
  stiffness: 90,
  damping: 15,
};

export const snappySpring: Transition = {
  type: 'spring',
  stiffness: 260,
  damping: 24,
};

// Page Transition Variants
export const pageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 12,
    scale: 0.99,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.28,
      ease: [0.16, 1, 0.3, 1],
    },
  },
  exit: {
    opacity: 0,
    y: -8,
    scale: 0.99,
    transition: {
      duration: 0.2,
      ease: [0.4, 0, 1, 1],
    },
  },
};

// Opening Sequence Stagger Container
export const openingContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.09,
      delayChildren: 0.05,
    },
  },
};

// Child item fade & spring up
export const openingItemVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 18,
    scale: 0.97,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: smoothSpring,
  },
};

// Staggered list variants for generic feeds
export const listContainerVariants: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.06,
    },
  },
};

export const listItemVariants: Variants = {
  hidden: { opacity: 0, y: 14 },
  show: {
    opacity: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 140,
      damping: 18,
    },
  },
};

// Card Tap & Hover Feedback
export const cardInteractiveVariants: Variants = {
  rest: { scale: 1, y: 0 },
  hover: { scale: 1.015, y: -2, transition: { duration: 0.18 } },
  tap: { scale: 0.97, y: 1, transition: { duration: 0.1 } },
};

// SOS Breathing Glow Motion
export const sosBreathingVariants: Variants = {
  idle: {
    scale: [1, 1.035, 1],
    boxShadow: [
      '0 8px 24px -4px rgba(239, 68, 68, 0.45)',
      '0 14px 38px -2px rgba(239, 68, 68, 0.7)',
      '0 8px 24px -4px rgba(239, 68, 68, 0.45)',
    ],
    transition: {
      duration: 3.2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
  tap: {
    scale: 0.94,
    boxShadow: '0 4px 14px 0px rgba(239, 68, 68, 0.85)',
    transition: { duration: 0.08 },
  },
};
