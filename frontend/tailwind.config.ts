import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0A0A0A',      // Dark theme primary
        surface: '#1A1A1A',        // Card backgrounds
        border: '#2A2A2A',         // Subtle borders
        text: {
          primary: '#FFFFFF',      // Primary text
          secondary: '#9CA3AF',    // Secondary text
          muted: '#6B7280'         // Muted text
        },
        accent: '#3B82F6',         // Blue accent
        status: {
          success: '#10B981',      // Green
          warning: '#F59E0B',      // Yellow
          danger: '#EF4444',       // Red
          info: '#3B82F6'          // Blue
        }
      },
      spacing: {
        'xs': '0.25rem',
        'sm': '0.5rem', 
        'md': '1rem',
        'lg': '1.5rem',
        'xl': '2rem',
        'xxl': '3rem'
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 2s infinite'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      },
      transitionDuration: {
        '150': '150ms',
      },
      transitionTimingFunction: {
        'ease-in-out': 'ease-in-out',
      }
    },
  },
  plugins: [],
}
export default config