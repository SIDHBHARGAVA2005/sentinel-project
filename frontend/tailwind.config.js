/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        sentinel: {
          bg: '#0a0e1a',
          surface: '#0f1629',
          card: '#131d35',
          border: '#1e2d4a',
          accent: '#00d4ff',
          green: '#00ff88',
          red: '#ff3b5c',
          orange: '#ff8c00',
          yellow: '#ffd700',
          muted: '#4a5a7a',
          text: '#c8d8f0',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'scan-line': 'scanLine 2s linear infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'fade-in': 'fadeIn 0.4s ease both',
        'slide-up': 'slideUp 0.4s ease both',
      },
      keyframes: {
        scanLine: {
          '0%': { top: '0%' },
          '100%': { top: '100%' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #00d4ff33' },
          '100%': { boxShadow: '0 0 20px #00d4ff66, 0 0 40px #00d4ff22' },
        },
        fadeIn: {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
        slideUp: {
          from: { opacity: 0, transform: 'translateY(16px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
      }
    },
  },
  plugins: [],
}
