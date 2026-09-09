import React from 'react';
import { Header } from '../ui/Header';
import { BottomNav } from './BottomNav';

interface ShellProps {
  children: React.ReactNode;
}

export const Shell: React.FC<ShellProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-citizen-text-primary flex justify-center relative overflow-x-hidden selection:bg-cyan-500 selection:text-black">
      
      {/* Desktop Ambient Background Accents */}
      <div className="fixed inset-0 pointer-events-none hidden md:block overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-900/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-900/10 rounded-full blur-3xl" />
      </div>

      {/* Main Centered Mobile Device Frame */}
      <div className="w-full max-w-md min-h-screen bg-citizen-bg border-x border-slate-800/80 flex flex-col relative z-10 shadow-2xl">
        {/* Top Sticky Header */}
        <Header locationName="Guntur, Andhra Pradesh" />

        {/* Scrollable Page Body */}
        <main className="flex-1 pb-28 px-4 pt-4 overflow-y-auto">
          {children}
        </main>

        {/* Floating Mobile Bottom Navigation */}
        <BottomNav />
      </div>
    </div>
  );
};
