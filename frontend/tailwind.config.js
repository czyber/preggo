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
        // Primary Colors (sophisticated neutrals)
        'warm-graphite': '#2C2937',
        'soft-charcoal': '#4A4754',
        'neutral-gray': '#6B6875',
        
        // Accent Colors (brighter and more vibrant)
        'blush-rose': '#E6A5B0',        // Increased saturation ~40%, brighter
        'sage-green': '#9BC089',        // Increased saturation ~45%, fresher green
        'dusty-lavender': '#C8B8D8',    // Increased saturation ~35%, more purple
        
        // Clean Neutral Colors (better contrast and brightness)
        'pure-white': '#FFFFFF',        // True white
        'off-white': '#FCFCFC',        // Lighter and more distinct
        'warm-gray': '#F8F7F5',        // More distinct, less muddy
        'light-gray': '#E5E3E0',       // Better contrast
        
        // Additional clean background options
        'neutral-50': '#F9F9F8',       // Very light but not muddy
        'accent-light': {
          'blush': '#F5ECED',          // Clean blush background
          'sage': '#F0F4ED',           // Clean sage background  
          'lavender': '#F3F0F5',       // Clean lavender background
        },
        
        // Semantic Colors (muted and professional)
        'success': '#7DA068',
        'warning': '#D4A574',
        'error': '#C67B7B',
        'info': '#8B9DC3',
        
        // Legacy colors (for gradual migration)
        'soft-pink': '#E8B4B8', // mapped to blush-rose
        'muted-lavender': '#C3B5D1', // mapped to dusty-lavender
        'gentle-mint': '#A8C09A', // mapped to sage-green
        'warm-neutral': '#FAFAF9', // mapped to off-white
        'light-coral': '#E8B4B8', // mapped to blush-rose
        'soft-blue': '#8B9DC3', // mapped to info
        
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
        'logo': ['Inter Display', 'Inter', 'system-ui', 'sans-serif'],
        'primary': ['Inter', 'system-ui', 'sans-serif'],
        'secondary': ['Inter', 'system-ui', 'sans-serif'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
      },
      fontWeight: {
        'thin': '200',
        'light': '300',
        'normal': '400',
        'medium': '500',
        'semibold': '600',
        'bold': '700',
      },
      borderRadius: {
        'lg': 'var(--radius)',
        'md': 'calc(var(--radius) - 2px)',
        'sm': 'calc(var(--radius) - 4px)',
        'subtle': '4px',
        'default': '8px',
        'rounded': '12px',
        'pill': '9999px',
      },
      boxShadow: {
        'xs': '0 1px 2px rgba(44, 41, 55, 0.04)',
        'sm': '0 2px 4px rgba(44, 41, 55, 0.06)',
        'md': '0 4px 8px rgba(44, 41, 55, 0.08)',
        'lg': '0 8px 16px rgba(44, 41, 55, 0.10)',
        'xl': '0 16px 32px rgba(44, 41, 55, 0.12)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        // 8px grid system
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px',
        '4xl': '96px',
      },
      animation: {
        // Refined, subtle animations
        'fade-in': 'fadeIn 0.3s cubic-bezier(0.4, 0.0, 0.2, 1)',
        'slide-up': 'slideUp 0.3s cubic-bezier(0.4, 0.0, 0.2, 1)',
        'gentle-scale': 'gentleScale 0.2s cubic-bezier(0.4, 0.0, 0.2, 1)',
        'subtle-glow': 'subtleGlow 2s ease-in-out infinite',
        // Legacy celebration animations (for gradual migration)
        'celebration-ripple': 'ripple 2s ease-out forwards',
        'celebration-heart': 'heartEmerge 0.8s ease-out forwards',
        'celebration-pulse': 'heartPulse 0.6s ease-in-out',
        'celebration-sparkle': 'sparkleFloat 1.5s ease-out forwards',
        'celebration-glow': 'glowFade 2.5s ease-in-out',
        'gentle-pulse': 'gentlePulse 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        gentleScale: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.02)' },
          '100%': { transform: 'scale(1)' },
        },
        subtleGlow: {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '0.8' },
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
        gentlePulse: {
          '0%, 100%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.02)', opacity: '0.9' },
        },
      },
    },
  },
  plugins: [],
}