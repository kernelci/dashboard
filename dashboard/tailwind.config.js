/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: '',
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
      colors: {
        bgSecondary: '#343638',
        lightBlue: '#11B3E6',
        'onSecondary-10': '#FFFFFF1A',
        white: '#FFFFFF',
        lightGray: '#F4F4F4',
        mediumGray: '#EAEAEA',
        darkGray: '#D6D6D6',
        darkGray2: '#767676',
        dimGray: '#454545',
        dimBlack: '#333333',
        weakGray: '#B3B3B3',
        black: '#000000',
        lightRed: '#FFBBBB',
        yellow: '#FFD27C',
        lightGreen: '#C9FADA',
        green: '#53D07C',
        red: '#E15739',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
