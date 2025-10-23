/** @type {import('tailwindcss').Config} */
const { fontFamily } = require('tailwindcss/defaultTheme');

module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', ...fontFamily.sans],
      },
      colors: {
        'primary': {
          DEFAULT: '#5E56F0', '50': '#F1F0FE', '100': '#DEDCFC', '200': '#BDB7FA', '300': '#9C93F7',
          '400': '#7B6EF5', '500': '#5E56F0', '600': '#4B45C0', '700': '#383390', '800': '#252260', '900': '#131130',
        },
        'secondary': '#10B981', 'success': '#22C55E', 'danger': '#EF4444', 'warning': '#F59E0B',
        'dark': {
          'bg': '#0D1117', 'card': '#161B22', 'border': '#30363D', 'text': '#E6EDF3', 'text-secondary': '#8B949E',
        },
        'light': { 'bg': '#F3F4F6', 'card': '#FFFFFF', 'border': '#E5E7EB', 'text': '#1F2937', 'text-secondary': '#6B7280' },
      },
      keyframes: {
        'shimmer': { '100%': { transform: 'translateX(100%)' } },
        'aurora': {
          from: { backgroundPosition: '0% 50%' },
          to: { backgroundPosition: '100% 50%' },
        },
        'slide-up': { '0%': { transform: 'translateY(20px)', opacity: 0 }, '100%': { transform: 'translateY(0)', opacity: 1 } },
        'fade-in': { from: { opacity: 0 }, to: { opacity: 1 } },
      },
      animation: {
        'shimmer': 'shimmer 1.5s infinite',
        'aurora': 'aurora 15s ease infinite',
        'slide-up': 'slide-up 0.5s ease-out forwards',
        'fade-in': 'fade-in 0.5s ease-in-out',
      },
      backgroundImage: {
        'aurora-gradient': 'linear-gradient(to right, #5E56F0, #10B981, #F59E0B, #5E56F0)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}