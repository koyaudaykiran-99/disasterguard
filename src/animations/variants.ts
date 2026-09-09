import { Variants } from 'framer-motion';

// Page entrance and exit transitions
export const pageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 8,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.22,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
  exit: {
    opacity: 0,
    y: -6,
    transition: {
      duration: 0.18,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
};

// General fade
export const fadeVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } },
  exit: { opacity: 0, transition: { duration: 0.2 } },
};

// Slide Up
export const slideUpVariants: Variants = {
  hidden: { opacity: 0, y: 15 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] } },
};

// Scale variants for interactive buttons
export const scaleVariants: Variants = {
  initial: { scale: 1 },
  hover: { scale: 1.02 },
  tap: { scale: 0.96 },
};

// Viewport Card Entrance
export const cardVariants: Variants = {
  hidden: { opacity: 0, y: 15, scale: 0.99 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.35,
      ease: [0.16, 1, 0.3, 1],
    },
  },
};

// Critical Pulse Glow Aura
export const criticalPulseVariants: Variants = {
  initial: {
    boxShadow: '0 0 0 0 rgba(239, 68, 68, 0.4)',
    borderColor: 'rgba(239, 68, 68, 0.4)',
  },
  animate: {
    boxShadow: [
      '0 0 0 0 rgba(239, 68, 68, 0.4)',
      '0 0 16px 4px rgba(239, 68, 68, 0.25)',
      '0 0 0 0 rgba(239, 68, 68, 0.4)',
    ],
    borderColor: [
      'rgba(239, 68, 68, 0.4)',
      'rgba(239, 68, 68, 0.8)',
      'rgba(239, 68, 68, 0.4)',
    ],
    transition: {
      duration: 2.0,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Stagger Container
export const staggerContainerVariants: Variants = {
  hidden: { opacity: 1 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.02,
    },
  },
};

// Stagger Item
export const staggerItemVariants: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: [0.16, 1, 0.3, 1],
    },
  },
};
