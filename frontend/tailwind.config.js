/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue"
  ],
  theme: {
    extend: {
      colors: {
        // Primary Colors
        'soft-pink': '#F8BBD0',
        'muted-lavender': '#E1BEE7',
        'gentle-mint': '#B2DFDB',
        
        // Secondary Colors
        'warm-neutral': '#F8FAFC',
        'light-coral': '#FFCDD2',
        'soft-blue': '#BBDEFB',
        
        // Preggo brand colors for shadcn components
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      fontFamily: {
        'logo': ['Lato', 'sans-serif'],
        'primary': ['Poppins', 'sans-serif'],
        'secondary': ['Roboto', 'sans-serif'],
        'sans': ['Poppins', 'sans-serif'],
        'body': ['Roboto', 'sans-serif'],
      },
      borderRadius: {
        'lg': 'var(--radius)',
        'md': 'calc(var(--radius) - 2px)',
        'sm': 'calc(var(--radius) - 4px)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'celebration-ripple': 'ripple 2s ease-out forwards',
        'celebration-heart': 'heartEmerge 0.8s ease-out forwards',
        'celebration-pulse': 'heartPulse 0.6s ease-in-out',
        'celebration-sparkle': 'sparkleFloat 1.5s ease-out forwards',
        'celebration-glow': 'glowFade 2.5s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        ripple: {
          '0%': { transform: 'scale(0)', opacity: '0.8' },
          '50%': { opacity: '0.4' },
          '100%': { transform: 'scale(4)', opacity: '0' },
        },
        heartEmerge: {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '70%': { transform: 'scale(1.1)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        heartPulse: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.1)' },
        },
        sparkleFloat: {
          '0%': { transform: 'translateY(0) scale(0)', opacity: '0' },
          '20%': { opacity: '1', transform: 'scale(1)' },
          '100%': { transform: 'translateY(-80px) scale(0.5)', opacity: '0' },
        },
        glowFade: {
          '0%': { opacity: '0', transform: 'scale(0.8)' },
          '30%': { opacity: '1', transform: 'scale(1)' },
          '70%': { opacity: '0.8' },
          '100%': { opacity: '0', transform: 'scale(1.2)' },
        },
      },
    },
  },
  plugins: [],
}