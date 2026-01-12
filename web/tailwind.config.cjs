/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'bg-primary': '#0D0D0D',
        'bg-secondary': '#1A1A1A',
        'bg-tertiary': '#262626',
        'bg-card': '#1F1F1F',
        'bg-hover': '#2A2A2A',
        'accent-gold': '#C9A227',
        'accent-blue': '#4A9EFF',
        'text-primary': '#F5F5F5',
        'text-secondary': '#A0A0A0',
        'rarity-common': '#1A1718',
        'rarity-uncommon': '#707883',
        'rarity-rare': '#A58E4A',
        'rarity-mythic': '#BF4427',
        'mana-white': '#F8F6D8',
        'mana-blue': '#0E68AB',
        'mana-black': '#150B00',
        'mana-red': '#D3202A',
        'mana-green': '#00733E',
        'colorless': '#CBC2BF',
      },
      fontFamily: {
        display: ['Cinzel', 'serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
