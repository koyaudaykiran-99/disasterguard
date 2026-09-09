import { Transition } from 'framer-motion';
import { DURATION_PRESETS, FAST_EASE, SMOOTH_EASE, SPRING_PRESET } from './motionConfig';

export const pageTransitionConfig: Transition = {
  duration: DURATION_PRESETS.snappy,
  ease: FAST_EASE,
};

export const cardEntranceTransition: Transition = {
  duration: DURATION_PRESETS.standard,
  ease: SMOOTH_EASE,
};

export const counterSpringConfig = {
  stiffness: 75,
  damping: 15,
};

export const sosPulseTransition: Transition = {
  repeat: Infinity,
  repeatType: 'reverse',
  duration: 2,
  ease: 'easeInOut',
};

export const criticalPulseTransition: Transition = {
  repeat: Infinity,
  repeatType: 'reverse',
  duration: 1.2,
  ease: 'easeInOut',
};
