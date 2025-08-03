# Preggo Design System Implementation

## Overview
This document describes the implementation of the design system for the preggo pregnancy tracking app, built with Tailwind CSS and shadcn components, following the specifications in DESIGN_TOKENS.md.

## Design Philosophy
The design system embodies the core principles:
- **Warm and Inviting**: Creating a welcoming environment like a supportive friend
- **Empathetic and Supportive**: Gentle and understanding throughout the pregnancy journey
- **Calm and Reassuring**: Promoting peace and comfort for expecting parents

## Color Palette

### Primary Colors
- **Soft Pink** (`#F8BBD0`): Represents warmth and care - used for primary actions and highlights
- **Muted Lavender** (`#E1BEE7`): Adds calming and soothing effects - used for secondary elements  
- **Gentle Mint** (`#B2DFDB`): Evokes freshness and tranquility - used for supportive messaging

### Secondary Colors
- **Warm Beige** (`#FFF3E0`): Neutral background that complements primary colors
- **Light Coral** (`#FFCDD2`): Adds vibrancy for celebrations and milestones
- **Soft Sky Blue** (`#BBDEFB`): Brings openness and clarity for informational content

## Typography

### Font Families
- **Logo Font**: `Playwrite Perú` - Used exclusively for the logo in lowercase
- **Primary Font**: `Poppins` - Modern sans-serif for headings and navigation (weights: 300, 400, 500, 600, 700)
- **Secondary Font**: `Roboto` - Versatile font for body text and descriptions (weights: 300, 400, 500, 700)

### Usage Guidelines
- Use Poppins for headings, buttons, and navigation elements
- Use Roboto for body text, descriptions, and form labels
- Logo font only for the "preggo" brand name

## Components

### BaseButton
**Location**: `/Users/bernhardczypka/private/preggo/frontend/components/BaseButton.vue`

Pregnancy-themed button variants:
- `default`: Soft pink with warm text
- `supportive`: Gentle mint for encouraging actions
- `celebration`: Light coral for milestone celebrations
- `calming`: Muted lavender for soothing actions
- `secondary`: Warm beige for secondary actions
- `ghost`: Subtle hover effects
- `outline`: Bordered variant
- `link`: Text-only variant

Sizes: `sm`, `default`, `lg`, `icon`

### BaseInput  
**Location**: `/Users/bernhardczypka/private/preggo/frontend/components/BaseInput.vue`

Features:
- Floating label animation
- Soft rounded corners (rounded-xl)
- Pregnancy-themed variants matching buttons
- Built-in error and hint text support
- Accessible focus states with soft glows

### BaseCard
**Location**: `/Users/bernhardczypka/private/preggo/frontend/components/BaseCard.vue`

Variants:
- `default`: Clean white card with warm borders
- `supportive`: Gentle mint themed
- `celebration`: Light coral themed for achievements
- `calming`: Muted lavender for peaceful content
- `warm`: Warm beige for welcoming sections
- `milestone`: Gradient background for special moments
- `progress`: Subtle gradient for tracking elements

### BaseAlert
**Location**: `/Users/bernhardczypka/private/preggo/frontend/components/BaseAlert.vue`

Pregnancy-specific alert types:
- `supportive`: Gentle encouragement (heart icon)
- `celebration`: Achievement celebrations (sparkles icon)
- `milestone`: Important pregnancy milestones (baby icon)
- `calming`: Reassuring messages (heart icon)
- `encouragement`: Motivational content (heart icon)

Plus standard variants: `info`, `warning`, `destructive`, `success`

## Layout Structure

### Navigation
- Warm, semi-transparent header with backdrop blur
- Gradient logo icon combining soft pink and gentle mint
- Pregnancy-journey themed navigation (Home, Journey, Milestones, Health)
- Subtle hover animations with gentle lifts

### Main Content
- Warm beige background with low opacity
- Maximum width container for readability
- Fade-in animations for content sections

### Footer
- Supportive messaging emphasizing care and family focus
- Semi-transparent background with gradient
- Heart and baby icons for emotional connection

## Custom CSS Classes

### Utility Classes
```css
.pregnancy-card - Pre-styled card with warm beige background
.pregnancy-button - Pre-styled button with soft pink theme
.pregnancy-input - Pre-styled input with rounded design
.supportive-message - Gentle mint left-border message
.celebration-message - Light coral left-border message
```

### Animations
```css
.fade-in - 0.5s fade in animation
.slide-up - 0.3s slide up animation
```

## Tailwind Configuration
**Location**: `/Users/bernhardczypka/private/preggo/frontend/tailwind.config.js`

Custom colors added to extend theme:
- All design token colors as CSS variables
- shadcn-compatible color system
- Custom font family definitions
- Enhanced border radius variables
- Custom spacing utilities
- Pregnancy-themed animations

## CSS Custom Properties
**Location**: `/Users/bernhardczypka/private/preggo/frontend/assets/css/main.css`

Defines CSS custom properties for:
- Design system colors
- Light and dark theme support
- shadcn UI integration
- Typography base styles
- Accessibility improvements

## Best Practices

### Color Usage
- Use soft pink for primary actions and calls-to-action
- Use gentle mint for supportive, encouraging content
- Use light coral for celebrations and achievements
- Use muted lavender for calming, soothing elements
- Use warm beige for neutral backgrounds and containers

### Typography Hierarchy
- H1-H6: Poppins, font-weight 600, line-height 1.2
- Body text: Roboto, line-height 1.6
- Logo: Playwrite Perú, lowercase only
- Navigation: Poppins medium weight

### Spacing and Layout
- Use rounded-xl (12px) for most elements
- Use rounded-2xl (16px) for cards and larger components
- Prefer soft shadows over hard borders
- Use gentle animations for state transitions

### Accessibility
- High contrast ratios maintained for text
- Focus states with soft glows instead of harsh outlines
- Screen reader support with sr-only class
- Semantic HTML structure maintained

## Usage Examples

### Button Usage
```vue
<BaseButton variant="supportive" size="lg">
  Encourage Mom
</BaseButton>

<BaseButton variant="celebration">
  Celebrate Milestone!
</BaseButton>
```

### Card Usage
```vue
<BaseCard variant="milestone" title="20 Weeks!" description="Halfway there!">
  Content for milestone celebration
</BaseCard>
```

### Alert Usage
```vue
<BaseAlert variant="supportive" title="You're doing great!" dismissible>
  Remember to take your prenatal vitamins today.
</BaseAlert>
```

### Input Usage
```vue
<BaseInput 
  v-model="babyName" 
  label="Baby's Name" 
  variant="supportive"
  hint="You can change this anytime"
/>
```

## Implementation Status
✅ Tailwind configuration updated with design tokens  
✅ Google Fonts integration (Poppins, Roboto, Playwrite Perú)  
✅ CSS custom properties and base styles implemented  
✅ BaseButton component with pregnancy-themed variants  
✅ BaseInput component with floating labels and variants  
✅ BaseCard component with multiple pregnancy themes  
✅ BaseAlert component with supportive messaging  
✅ Default layout updated with warm, family-friendly design  
✅ Navigation structure with pregnancy journey focus  

## Next Steps
- Test components across different screen sizes
- Implement dark mode support for evening usage
- Add more pregnancy-specific icons and illustrations
- Create component documentation with live examples
- Implement haptic feedback for mobile interactions
- Add accessibility testing and improvements

The design system successfully creates a warm, inviting, and supportive environment that reflects the emotional journey of pregnancy while maintaining modern usability standards.