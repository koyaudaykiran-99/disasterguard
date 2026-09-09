/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        citizen: {
          bg: '#F8FAFC',
          surface: '#FFFFFF',
          'surface-elevated': '#FFFFFF',
          'surface-glass': 'rgba(255, 255, 255, 0.9)',
          border: '#E2E8F0',
          'border-subtle': 'rgba(226, 232, 240, 0.8)',
          'text-primary': '#0F172A',
          'text-secondary': '#475569',
          'text-muted': '#64748B',
          accent: '#2563EB',
        },
        risk: {
          low: '#10B981',
          moderate: '#F59E0B',
          high: '#F97316',
          critical: '#EF4444',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      boxShadow: {
        'card-3d': '0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03), inset 0 1px 0 rgba(255, 255, 255, 0.9)',
        'card-3d-hover': '0 20px 30px -10px rgba(0, 0, 0, 0.08), 0 10px 15px -5px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 1)',
        'glow-low': '0 0 25px -5px rgba(16, 185, 129, 0.35)',
        'glow-moderate': '0 0 25px -5px rgba(245, 158, 11, 0.35)',
        'glow-high': '0 0 30px -5px rgba(249, 115, 22, 0.4)',
        'glow-critical': '0 0 35px -5px rgba(239, 68, 68, 0.45)',
        'sos': '0 12px 30px -5px rgba(239, 68, 68, 0.5), inset 0 2px 4px rgba(255, 255, 255, 0.4)',
        'sos-halo': '0 0 30px rgba(239, 68, 68, 0.5), 0 0 60px rgba(239, 68, 68, 0.25)',
      },
      animation: {
        'pulse-subtle': 'pulseSubtle 3s ease-in-out infinite',
        'pulse-urgent': 'pulseUrgent 1.8s ease-in-out infinite',
        'breathing-sos': 'breatheSos 4s ease-in-out infinite',
      },
      keyframes: {
        pulseSubtle: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.85', transform: 'scale(1.02)' },
        },
        pulseUrgent: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.75', transform: 'scale(1.04)' },
        },
        breatheSos: {
          '0%, 100%': { transform: 'scale(1)', boxShadow: '0 10px 25px -5px rgba(239, 68, 68, 0.4)' },
          '50%': { transform: 'scale(1.03)', boxShadow: '0 15px 35px -3px rgba(239, 68, 68, 0.65)' },
        },
      },
    },
  },
  plugins: [],
};
