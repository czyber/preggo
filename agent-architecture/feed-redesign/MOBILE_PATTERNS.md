# Mobile Interaction Patterns
*Level 1 Strategy Document - Mobile UX Specifications*

## Overview

This document defines pregnancy-aware mobile interaction patterns that prioritize comfort, accessibility, and emotional well-being. Every pattern is designed considering the physical and emotional changes experienced during pregnancy, with special attention to fatigue, nausea, and changing dexterity needs.

## Design Philosophy for Pregnant Users

### Physical Considerations
- **Reduced Dexterity:** Larger touch targets, more forgiving gestures
- **Fatigue:** Minimize required precision and cognitive load
- **Nausea:** Reduce motion that could trigger discomfort
- **Changing Body:** One-handed operation becomes increasingly important
- **Emotional Sensitivity:** Gentle feedback, no harsh interactions

### Interaction Principles
1. **Effortless First:** Every action should require minimal physical effort
2. **Forgiving Always:** Interactions should be error-tolerant and recoverable
3. **Contextual Adaptation:** Interface adapts to user's current state and needs
4. **Gentle Feedback:** All responses feel supportive, never jarring
5. **One-Handed Optimized:** Critical functions accessible with thumb only

## Core Mobile Patterns

### 1. Pregnancy-Aware Touch Targets

**Standard Touch Target Sizing:**
- **Minimum:** 48px × 48px (meets WCAG guidelines)
- **Recommended:** 56px × 56px (comfortable for pregnancy changes)
- **Primary Actions:** 64px × 64px (love, memory, respond buttons)
- **Text Links:** 44px minimum height with generous padding

**Adaptive Sizing Logic:**
```typescript
interface TouchTargetConfig {
  baseSize: number
  pregnancyMultiplier: number
  fatigueAdjustment: number
  timeOfDayFactor: number
}

// Evening and fatigue states increase target sizes
const adaptiveSize = baseSize * pregnancyMultiplier * (1 + fatigueAdjustment)
```

**Visual Design:**
- Subtle visual boundaries to indicate touchable areas
- No fine borders that require precision
- Generous spacing between interactive elements
- Clear visual hierarchy with primary actions emphasized

### 2. Thumb Zone Navigation

**Thumb-Friendly Architecture:**
```
┌─────────────────────────────────┐ ← Status bar (read-only)
│     Content Area (View Only)    │
│                                 │ ← Content consumption zone
│                                 │
│                                 │
├─────────────────────────────────┤
│ Primary Actions (Thumb Zone)    │ ← 100-220px from bottom
│ ○ Love    ○ Memory    ○ Share   │
└─────────────────────────────────┘
```

**Action Zone Distribution:**
- **Primary Zone (0-100px from bottom):** Most frequent actions
- **Secondary Zone (100-220px from bottom):** Common interactions  
- **Tertiary Zone (220px+ from bottom):** Occasional actions
- **Content Zone (Above 220px):** Information consumption

**Primary Actions in Thumb Zone:**
- Send Love (heart gesture)
- Add to Memory Book
- Family Response prompt
- Quick photo sharing
- Voice note recording

### 3. Gesture Language for Pregnancy

**Core Gestures with Pregnancy Adaptations:**

#### Pull to Refresh - "Check for Family Love"
- **Standard:** Pull down from top
- **Pregnancy Adaptation:** 
  - Requires less travel distance (120px vs 180px)
  - More forgiving release timing
  - Message: "Checking for family love..." instead of generic text
  - Gentle bounce animation without harsh snap

#### Swipe Actions - "Gentle Intentions"
- **Swipe Right:** Send Love
  - Distance: 60px minimum (short swipe)
  - Visual: Heart particles from finger
  - Haptic: Gentle double pulse
  - Recovery: Swipe back to undo within 2 seconds

- **Swipe Left:** Add to Memory Book  
  - Distance: 60px minimum
  - Visual: Bookmark icon appears
  - Haptic: Soft single pulse
  - Confirmation: "Added to family memories" toast

#### Double Tap - "Quick Love"
- **Standard:** Two taps within 300ms
- **Pregnancy Adaptation:**
  - Extended to 500ms for slower reactions
  - Larger detection area (entire content card)
  - Visual: Heart burst from tap location
  - Gentle confetti animation

#### Long Press - "Thoughtful Action"
- **Duration:** 800ms (vs standard 500ms) for deliberate intent
- **Visual Progress:** Gentle ring fills around finger
- **Haptic Pattern:** Increasing pulse to confirm activation
- **Menu:** Soft shadow context menu with large targets

### 4. Scroll Behavior Optimization

**Pregnancy-Comfortable Scrolling:**
- **Momentum Preservation:** Natural deceleration curve
- **Rubber Band Effect:** Gentle bounce at scroll limits
- **Auto-Scroll Position:** Returns to last meaningful position
- **Fatigue Detection:** Reduces scroll sensitivity when user shows fatigue patterns

**Scroll Position Memory:**
```typescript
interface ScrollMemory {
  lastMeaningfulPosition: number
  sessionStartTime: Date
  interactionCount: number
  fatigueLevel: 'low' | 'medium' | 'high'
}

// Auto-return to meaningful content rather than exact scroll position
const resumePosition = calculateMeaningfulPosition(scrollMemory)
```

**Content Pacing:**
- Maximum 3 story cards visible at once
- Generous vertical spacing (32px between cards)
- Natural reading breaks every 5-6 posts
- Gentle "You're caught up" indicators

### 5. Adaptive Interface Behavior

**Time-of-Day Adaptations:**

#### Morning (6am-12pm)
- Brighter, more energetic color tones
- Standard touch target sizes
- Normal animation speeds
- Encouraging content prompts

#### Afternoon (12pm-6pm)  
- Balanced color palette
- Slightly larger touch targets
- Gentle reminder for rest periods
- Family activity highlights

#### Evening (6pm-10pm)
- Warmer, softer color tones
- Larger touch targets (+10px)
- Slower, more deliberate animations
- Reflection and memory prompts

#### Night (10pm-6am)
- Dark mode with warm undertones
- Largest touch targets (+20px)
- Minimal animations
- Sleep-friendly content suggestions

**Fatigue State Adaptations:**
```typescript
enum FatigueLevel {
  Fresh = 'fresh',      // Normal interactions
  Moderate = 'moderate', // Larger targets, slower pace
  High = 'high',        // Simplified UI, essential actions only
  Resting = 'resting'   // Read-only mode with gentle encouragement
}
```

**High Fatigue Mode:**
- Touch targets increased by 25%
- Reduced animation and effects
- Simplified navigation options
- Voice input prominently available
- "Rest mode" with minimal interactions

### 6. Voice Integration Patterns

**Pregnancy-Friendly Voice Commands:**

#### Content Creation
- "Share how I'm feeling today"
- "Add a photo to my journey"
- "Tell family about baby's kicks"
- "Record a voice note for baby"

#### Navigation  
- "Show me family responses"
- "Go to this week's milestones"
- "Find my memory book"
- "What did I share yesterday?"

#### Quick Actions
- "Send love to Mom's post"
- "Add this to memories"
- "Ask family a question"
- "Thank everyone for their support"

**Voice UI Design:**
- Large, easy-to-find voice button (bottom right corner)
- Visual feedback during listening
- Gentle error handling with suggestions
- Option to edit transcription before posting

### 7. Gestational Error Handling

**Forgiving Interaction Design:**

#### Accidental Actions
- **Problem:** Unintended swipes or taps due to changed dexterity
- **Solution:** 2-second undo window for all major actions
- **Visual:** Soft toast with "Undo" option
- **Example:** "Added to memories • Undo"

#### Network Interruptions  
- **Problem:** Poor connectivity in medical settings
- **Solution:** Graceful offline mode with sync indicators
- **Visual:** "Saving for when you're connected" message
- **Behavior:** Queue actions for later completion

#### Input Mistakes
- **Problem:** Typos or incomplete thoughts due to fatigue
- **Solution:** Smart auto-save and gentle editing prompts
- **Visual:** "Save draft?" appears after 10 seconds of inactivity
- **Recovery:** Easy access to draft restoration

### 8. Pregnancy Milestone Interactions

**Special Interaction Patterns for Important Moments:**

#### Milestone Achievement
- **Trigger:** System detects milestone-worthy post
- **Interaction:** Gentle celebration suggestion
- **Visual:** Soft sparkle animation around content
- **Choice:** "Celebrate with family?" prompt
- **Result:** Special sharing format if accepted

#### Family Response to Milestone
- **Visual:** Warm glow animation on family hearts
- **Sound:** Gentle chime (respects silent mode)  
- **Notification:** "Family is celebrating with you!"
- **Action:** Easy one-tap to view responses

#### Memory Book Addition
- **Auto-suggest:** Important posts flagged for memory book
- **Visual:** Subtle bookmark icon appears
- **Interaction:** Single tap to add, long press for options
- **Confirmation:** "Added to your family's story"

### 9. Accessibility Integration

**Pregnancy-Specific Accessibility:**

#### Vision Changes
- **High Contrast Mode:** Maintains warmth while improving readability
- **Text Size Scaling:** Up to 150% with preserved layout
- **Color Blindness Support:** Never rely on color alone for information
- **Night Vision:** Red-shifted dark mode for evening feeding prep

#### Motor Challenges  
- **Switch Control Integration:** Full app navigation via external switches
- **Voice Control:** Complete feature access through voice commands
- **Gesture Alternatives:** All swipe actions have button alternatives
- **Reduced Motion:** Respects system preference, maintains gentle feedback

#### Screen Reader Optimization
- **Pregnancy Context:** "Week 24 milestone post from Sarah"
- **Family Warmth:** "This post has received love from 4 family members"
- **Content Description:** "Ultrasound photo showing baby at 20 weeks"
- **Action Feedback:** "Love sent to Mom's post about baby's first kicks"

### 10. Performance Optimization

**Battery-Conscious Design:**
- **Animation Management:** Reduces complex animations when battery < 20%
- **Image Loading:** Progressive enhancement based on connection
- **Gesture Recognition:** Efficient touch event handling
- **Background Refresh:** Intelligent sync timing

**Memory Management:**
- **Image Caching:** Smart caching for frequently accessed photos
- **Scroll Performance:** Virtual scrolling for large post histories
- **State Management:** Efficient component state cleanup
- **Network Usage:** Batch requests and offline-first approach

**Loading States:**
- **Initial Load:** Pregnancy-themed skeleton screens
- **Image Loading:** Soft placeholders with gentle pulse
- **Content Loading:** "Gathering your family moments..." message
- **Network Error:** "Checking connection... we'll try again" message

### 11. Haptic Feedback Patterns

**Gentle Haptic Language:**

#### Love Actions
- **Single Soft Pulse:** Love sent successfully
- **Double Gentle Pulse:** Love received from family
- **Warm Tremor:** Multiple family members sending love

#### Memory Actions
- **Soft Tick:** Added to memory book
- **Growing Pulse:** Memory book achievement unlocked
- **Gentle Wave:** Family member added your post to their memories

#### Milestone Celebrations
- **Celebration Pattern:** Gentle build-up followed by soft burst
- **Family Join Pattern:** Soft pulse as each family member reacts
- **Achievement Pattern:** Three gentle pulses for major milestones

**Haptic Intensity Adaptation:**
- **High Energy:** Normal haptic feedback
- **Moderate Energy:** Reduced intensity (80% of normal)
- **Low Energy:** Minimal haptics (50% of normal)
- **Nausea Mode:** Haptics disabled entirely

### 12. Pregnancy Week Transitions

**Special Interaction for Week Changes:**

#### Week Progression Celebration
- **Timing:** Sunday evening or Monday morning
- **Visual:** Gentle progress animation
- **Content:** "Welcome to week 25" with baby development
- **Interaction:** Optional photo prompt for weekly documentation
- **Family:** Automatic family notification of progression

#### Trimester Transitions
- **Major Celebration:** Special animation and congratulations
- **Family Involvement:** Prompt to share excitement with family
- **Milestone Unlock:** New features or content become available
- **Memory Creation:** Automatic trimester memory book chapter

## Implementation Guidelines

### Development Priorities

**Phase 1: Core Patterns**
- Thumb zone navigation
- Basic gesture recognition
- Adaptive touch targets
- Essential accessibility features

**Phase 2: Pregnancy Adaptations**
- Time-of-day adaptations
- Fatigue level detection
- Voice integration
- Advanced haptic patterns

**Phase 3: Smart Features**
- Predictive UI adjustments
- Advanced error recovery
- Performance optimizations
- Extended accessibility

### Testing Strategy

**User Testing with Pregnant Users:**
- Various pregnancy stages (early, middle, late)
- Different physical comfort levels
- Range of tech comfort levels
- Diverse family structures

**Accessibility Testing:**
- Screen reader compatibility
- Switch control navigation
- Voice control accuracy
- High contrast effectiveness

**Performance Testing:**
- Battery usage measurement
- Memory usage monitoring
- Network efficiency validation
- Gesture recognition accuracy

### Success Metrics

**Interaction Quality:**
- Reduced accidental actions
- Increased successful voice commands
- Improved one-handed usage patterns
- Decreased interaction retry rates

**User Comfort:**
- Time spent in app without fatigue
- Successful content creation rates
- Family engagement response rates
- User-reported comfort scores

**Technical Performance:**
- Touch response latency
- Gesture recognition accuracy
- Battery usage efficiency
- Loading time optimization

---

*These mobile patterns create an interaction experience that adapts to the changing needs of pregnancy, ensuring that technology supports rather than burdens users during this important journey while maintaining the warm, supportive tone essential to family connection.*