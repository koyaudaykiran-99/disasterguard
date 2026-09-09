/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        command: {
          bg: '#F8FAFC',
          card: '#FFFFFF',
          header: '#FFFFFF',
          sidebar: '#FFFFFF',
          border: '#E2E8F0',
          accent: '#2563EB',
          subtle: '#F1F5F9',
        },
        risk: {
          low: '#10b981',
          moderate: '#f59e0b',
          high: '#f97316',
          critical: '#ef4444',
        }
      },
      boxShadow: {
        'card-3d': '0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03), inset 0 1px 0 rgba(255, 255, 255, 0.9)',
        'card-3d-hover': '0 20px 30px -10px rgba(0, 0, 0, 0.08), 0 10px 15px -5px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 1)',
        'glow-red': '0 0 25px rgba(239, 68, 68, 0.4), 0 4px 12px rgba(239, 68, 68, 0.25)',
        'inset-3d': 'inset 0 2px 4px rgba(0, 0, 0, 0.04)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'radar-sweep': 'sweep 3s linear infinite',
        'pulse-subtle': 'pulseSubtle 3s ease-in-out infinite',
        'pulse-strong': 'pulseStrong 1.5s ease-in-out infinite',
        'breathing': 'breathing 4s ease-in-out infinite',
      },
      keyframes: {
        sweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.03)' },
        },
        pulseStrong: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.9', transform: 'scale(1.07)' },
        },
        breathing: {
          '0%, 100%': { opacity: '0.7', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.04)' },
        }
      }
    },
  },
  plugins: [],
}
