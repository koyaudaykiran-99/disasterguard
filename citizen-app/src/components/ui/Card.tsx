import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  elevated?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  elevated = false,
}) => {
  return (
    <div
      className={`rounded-2xl p-4 transition-all ${
        elevated ? 'glass-panel-elevated shadow-xl' : 'glass-panel shadow-md'
      } ${className}`}
    >
      {children}
    </div>
  );
};
