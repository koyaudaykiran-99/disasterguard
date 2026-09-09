import React from 'react';
import { useLocation } from 'react-router-dom';
import { Header } from '../ui/Header';
import { BottomNav } from './BottomNav';

interface ShellProps {
  children: React.ReactNode;
}

export const Shell: React.FC<ShellProps> = ({ children }) => {
  const location = useLocation();
  const isAuthRoute = location.pathname === '/login' || location.pathname === '/signup';

  if (isAuthRoute) {
    return (
      <div className="min-h-screen bg-[#FAFAFA] text-slate-900 flex justify-center relative overflow-x-hidden">
        <main className="w-full flex-1 flex flex-col justify-center">
          {children}
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-citizen-text-primary flex justify-center relative overflow-x-hidden selection:bg-red-500 selection:text-white">
      {/* Desktop Ambient Background Accents */}
      <div className="fixed inset-0 pointer-events-none hidden md:block overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-red-950/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-slate-900/20 rounded-full blur-3xl" />
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
