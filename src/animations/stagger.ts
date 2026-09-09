/**
 * Calculate dynamic stagger delay for items
 * Card 1 -> 0ms, Card 2 -> 50ms, Card 3 -> 100ms, Card 4 -> 150ms
 */
export const getStaggerDelay = (index: number, stepMs = 50): number => {
  return (index * stepMs) / 1000;
};
