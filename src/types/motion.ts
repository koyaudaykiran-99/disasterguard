import { RiskLevel } from './disaster';

export interface MotionConfig {
  reducedMotion: boolean;
  durationMultiplier: number;
}

export interface RiskMotionRules {
  pulseFrequencySeconds: number;
  glowIntensity: 'none' | 'subtle' | 'moderate' | 'strong';
  scaleMagnitude: number;
  borderAnimation: boolean;
}

export const RISK_MOTION_CONFIG: Record<RiskLevel, RiskMotionRules> = {
  LOW: {
    pulseFrequencySeconds: 0,
    glowIntensity: 'none',
    scaleMagnitude: 1.0,
    borderAnimation: false,
  },
  MODERATE: {
    pulseFrequencySeconds: 3.5,
    glowIntensity: 'subtle',
    scaleMagnitude: 1.02,
    borderAnimation: false,
  },
  HIGH: {
    pulseFrequencySeconds: 2.0,
    glowIntensity: 'moderate',
    scaleMagnitude: 1.04,
    borderAnimation: true,
  },
  CRITICAL: {
    pulseFrequencySeconds: 1.2,
    glowIntensity: 'strong',
    scaleMagnitude: 1.06,
    borderAnimation: true,
  },
};
