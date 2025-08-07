# Feed Components Specification
*Level 1 Strategy Document - Component Architecture*

## Overview

This document specifies the redesigned feed components that implement the supportive pregnancy companion philosophy. Each component is designed with mobile-first principles, pregnancy-aware interactions, and warm minimalistic aesthetics.

## Component Architecture

### Simplified Component Hierarchy

```
FeedJourney (Main Container)
├── JourneyHeader (Context + Navigation)
├── StoryCard (Individual Posts)
│   ├── MomentContent (Core Content)
│   ├── PregnancyContext (Week/Mood Info)
│   └── FamilyWarmth (Support Indicators)
├── MemoryPrompt (Gentle Content Suggestions)
└── JourneyProgress (Week Indicator)
```

## Core Components

### 1. FeedJourney (Main Container)

**Purpose:** Replace FeedTimeline with a story-driven pregnancy journey experience

**Visual Design:**
- Full viewport with gentle vertical rhythm
- Background: Warm Beige (#FFF3E0) with subtle texture
- Content max-width: 320px (mobile) / 420px (larger screens)
- Padding: 16px horizontal, 20px vertical
- Scroll behavior: Smooth with momentum

**Props Interface:**
```typescript
interface FeedJourneyProps {
  pregnancyId: string
  currentWeek: number
  userMood?: 'tired' | 'excited' | 'anxious' | 'peaceful'
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night'
  familyActivity: 'high' | 'medium' | 'low'
}
```

**State Management:**
- Current story card focus
- User's interaction preferences
- Content loading state with pregnancy-themed placeholders
- Family engagement context

**Mobile Considerations:**
- Pull-to-refresh with gentle bounce animation
- Scroll position memory for returning users
- One-handed operation optimization
- Adaptive content sizing based on device and time

**Accessibility:**
- Screen reader navigation with pregnancy context
- High contrast mode support
- Reduced motion preferences honored
- Voice control integration points

---

### 2. JourneyHeader (Context + Navigation)

**Purpose:** Replace complex filters with gentle discovery and pregnancy context

**Visual Design:**
- Height: 120px with breathing room
- Background: Semi-transparent white with subtle blur
- Sticky positioning with gentle slide animation
- Typography: Poppins 24px for greeting, 16px for context

**Layout Structure:**
```
┌─────────────────────────────────────┐
│  Good morning, Sarah ☀️             │
│  Week 24 · Baby is growing strong   │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│  │Today│ │Mile-│ │Fami-│ │Memo-│   │
│  │     │ │stone│ │ ly  │ │ries │   │
│  └─────┘ └─────┘ └─────┘ └─────┘   │
└─────────────────────────────────────┘
```

**Personalized Greeting Logic:**
- Time-aware: "Good morning/afternoon/evening"
- Mood-aware: Adjust tone based on recent posts
- Week-aware: Include relevant pregnancy milestone
- Weather-aware: "Perfect day for a walk" / "Cozy day to rest"

**Navigation Pills:**
- **Today**: Current day's moments and family responses
- **Milestones**: Special achievements and celebrations
- **Family**: Posts with high family warmth
- **Memories**: Past weeks for gentle reflection

**Props Interface:**
```typescript
interface JourneyHeaderProps {
  userName: string
  currentWeek: number
  babyDevelopment: string
  recentMood?: string
  weatherContext?: string
  activeFilter: 'today' | 'milestones' | 'family' | 'memories'
  onFilterChange: (filter: string) => void
}
```

**Mobile Optimizations:**
- Touch targets: 48px minimum height
- Horizontal scrolling for navigation if needed
- Thumb-friendly positioning
- Collapse to minimal state on scroll

---

### 3. StoryCard (Individual Posts)

**Purpose:** Replace social media post cards with warm, story-driven content presentation

**Visual Design:**
- Background: Pure white with subtle shadow
- Border-radius: 16px for warmth
- Margin: 24px bottom for breathing room
- Padding: 20px all around
- Max-width: 100% with 16px horizontal margins

**Layout Philosophy:**
Content takes center stage with supporting elements positioned as gentle whispers around the main story.

```
┌─────────────────────────────────┐
│                                 │
│     [Hero Content Area]         │
│                                 │
│  Week 24 · Feeling grateful 🙏 │
│                                 │
│         [Family Warmth]         │
│                                 │
└─────────────────────────────────┘
```

**Content Hierarchy:**
1. **Hero Content** (80% visual weight)
2. **Context Whisper** (15% visual weight)  
3. **Family Warmth** (5% visual weight)

**Props Interface:**
```typescript
interface StoryCardProps {
  post: EnrichedPost
  familyWarmth: FamilyWarmthIndicator
  userPermissions: UserPermissions
  cardSize: 'comfortable' | 'cozy' | 'minimal'
  emotionalTone: 'supportive' | 'celebratory' | 'gentle'
}
```

**Interaction States:**
- **Resting:** Gentle shadow, soft corners
- **Focus:** Slightly elevated, warmer glow
- **Active:** Minimal feedback, preserve tranquility
- **Memory-bound:** Subtle bookmark indicator

**Mobile Gestures:**
- **Swipe left:** Add to Memory Book (with gentle animation)
- **Swipe right:** Send Love (heart particles)
- **Double tap:** Quick love response
- **Long press:** Context menu with soft haptic

---

### 4. MomentContent (Core Content)

**Purpose:** Replace PostContent with pregnancy-focused content presentation

**Visual Design:**
- Typography: System font 17px for readability
- Line height: 1.6 for comfort
- Color: #374151 (readable gray)
- Generous spacing between elements

**Content Type Adaptations:**

#### Text Posts
- Maximum 3 lines before gentle truncation
- "Read more" link in Soft Pink (#F8BBD0)
- Pregnancy keywords highlighted with subtle background
- Emoji support with larger rendering for warmth

#### Photo Posts  
- Hero image with 12px border radius
- Maximum height: 300px with aspect ratio preservation
- Pregnancy-specific overlays:
  - Week indicator for belly photos
  - "Baby's first photo" for ultrasounds
  - Date stamp in elegant typography

#### Milestone Posts
- Special card treatment with gradient background
- Milestone icon with gentle pulse animation
- Achievement text in larger, celebratory typography
- Automatic family notification suggestions

#### Weekly Update Posts
- Week number prominently displayed
- Baby development snippet if available
- Mood indicator with appropriate emoji
- Progress visualization with gentle bar

**Props Interface:**
```typescript
interface MomentContentProps {
  content: PostContent
  pregnancyWeek: number
  postType: PostType
  mediaItems?: MediaItem[]
  milestoneContext?: MilestoneContext
  expandable: boolean
  onExpand?: () => void
  onMediaView?: (index: number) => void
}
```

**Accessibility Features:**
- Alt text for all images with pregnancy context
- Screen reader friendly milestone announcements
- High contrast text options
- Font size adaptation options

---

### 5. PregnancyContext (Context Whisper)

**Purpose:** Replace complex metadata display with gentle pregnancy context

**Visual Design:**
- Typography: 14px system font, #6B7280 color
- Position: Below main content, above family warmth
- Style: Subtle, non-intrusive information
- Layout: Horizontal flow with gentle separators

**Information Display:**
```
Week 24 · Feeling grateful 🙏 · 2 hours ago
```

**Context Elements:**
- **Week Badge:** Soft pill with week number
- **Mood Indicator:** Emoji + text in muted tone
- **Time Stamp:** Relative time in gentle language
- **Location:** If shared, with map pin icon
- **Special Indicators:** Milestone marker, family question flag

**Adaptive Display:**
- Hide non-essential context on small screens
- Emphasize important context (milestones, questions)
- Fade out context as post ages
- Show different context based on viewing user's relationship

**Props Interface:**
```typescript
interface PregnancyContextProps {
  week: number
  mood?: MoodType
  timestamp: Date
  location?: string
  isMilestone: boolean
  needsFamilyResponse: boolean
  viewerRelationship: RelationshipType
}
```

---

### 6. FamilyWarmth (Support Indicators)

**Purpose:** Replace engagement metrics with warm family connection indicators

**Visual Design:**
- Position: Bottom of story card
- Style: Subtle, warm, encouraging
- Animation: Gentle, never attention-grabbing
- Colors: Derived from family avatar colors

**Visual Patterns:**

#### Family Avatars Cluster
```
👤👤👤 Family is gathering around this moment
```
- Overlapping avatar circles
- Maximum 4 visible + "and X more"
- Warm background glow effect
- Gentle hover/tap reveals names

#### Love Glow Indicator
```
✨ Wrapped in family love ✨
```
- Soft gradient background
- Subtle sparkle animation
- Color intensity reflects family engagement
- No numbers, just warmth visualization

#### Recent Family Activity
```
Mom left a heart · Dad added to memories
```
- Recent family actions in gentle language
- Time-aware (fades after 24 hours)
- Relationship-specific icons
- Tap to view family responses

**Props Interface:**
```typescript
interface FamilyWarmthProps {
  familyHearts: FamilyMember[]
  recentActivity: FamilyActivity[]
  memoryMarkers: number
  supportLevel: 'gentle' | 'warm' | 'wrapped'
  showDetails: boolean
  onViewActivity?: () => void
}
```

**Interaction Design:**
- **Tap avatars:** View family responses in modal
- **Tap activity:** Expand recent family interactions
- **No counts:** Focus on warmth, not metrics
- **Gentle animations:** Hearts floating, warm glows

---

### 7. MemoryPrompt (Content Suggestions)

**Purpose:** Gentle encouragement for content creation and memory making

**Visual Design:**
- Card style: Soft background with dashed border
- Typography: Encouraging, personal tone
- Color: Muted Lavender (#E1BEE7) accents
- Position: Appears contextually in feed

**Prompt Types:**

#### Weekly Photo Reminder
```
┌─────────────────────────────────┐
│ 📸 Your weekly photo awaits      │
│                                 │
│ Document this amazing week of   │
│ your journey. Your family loves │
│ seeing how baby is growing!     │
│                                 │
│     [Take Photo] [Not Today]    │
└─────────────────────────────────┐
```

#### Milestone Celebration
```
┌─────────────────────────────────┐
│ 🎉 Time to celebrate!           │
│                                 │
│ You've reached week 20 - baby   │
│ can hear your voice now!        │
│                                 │
│     [Share Joy] [Save for Later]│
└─────────────────────────────────┘
```

#### Family Memory Opportunity
```
┌─────────────────────────────────┐
│ 💝 Create a family memory       │
│                                 │
│ Ask your family to share their  │
│ favorite moment from this week  │
│                                 │
│     [Ask Family] [Maybe Later]  │
└─────────────────────────────────┘
```

**Smart Timing:**
- Appears 2-3 times per week maximum
- Context-aware (morning for photo prompts)
- Respects user's mood and energy levels
- Dismissible with memory for user preferences

**Props Interface:**
```typescript
interface MemoryPromptProps {
  promptType: 'photo' | 'milestone' | 'family' | 'reflection'
  pregnancyWeek: number
  lastActivity: Date
  userEnergyLevel?: 'high' | 'medium' | 'low'
  onAccept: (action: string) => void
  onDismiss: () => void
}
```

---

### 8. JourneyProgress (Week Indicator)

**Purpose:** Gentle progress visualization without overwhelming detail

**Visual Design:**
- Position: Fixed bottom of screen or contextual in feed
- Style: Minimal progress indicator with week milestones
- Color: Gentle Mint (#B2DFDB) for progress
- Animation: Subtle growth and milestone celebrations

**Layout Options:**

#### Minimalist Progress Bar
```
Week 24 ●●●●●○○○○○ 40 weeks
```

#### Milestone Dots
```
○●●○●○○●○ Milestones achieved
```

#### Growth Curve (for special moments)
```
📊 Baby's growth journey visualization
```

**Information Display:**
- Current week prominently shown
- Next milestone hint
- Achievement celebrations
- Gentle future preview

**Props Interface:**
```typescript
interface JourneyProgressProps {
  currentWeek: number
  totalWeeks: number
  completedMilestones: Milestone[]
  upcomingMilestones: Milestone[]
  displayStyle: 'minimal' | 'detailed' | 'celebratory'
  onMilestoneView?: (milestone: Milestone) => void
}
```

## Component Interaction Patterns

### Gesture Integration

Each component responds to pregnancy-aware gestures:

**StoryCard Gestures:**
- **Swipe left:** Add to Memory Book (bookmark animation)
- **Swipe right:** Send Love (heart particles from touch point)
- **Double tap:** Quick love with gentle haptic feedback
- **Long press:** Context menu with soft shadows

**Navigation Gestures:**
- **Pull down:** Refresh with "Checking for family love" message
- **Swipe between filters:** Smooth transitions with pregnancy-themed animations

### State Management

**Shared State:**
- Current pregnancy week and context
- User's mood and energy level
- Family activity and warmth levels
- Memory book items and favorites

**Component State:**
- Individual card expansion states
- Current filter and sort preferences
- Loading states with pregnancy-themed placeholders
- User interaction preferences and accessibility settings

### Animation Philosophy

**Gentle Micro-interactions:**
- Fade transitions (200-300ms duration)
- Gentle scale transforms (1.0 to 1.02)
- Soft shadows and glows
- Natural easing curves (ease-out)
- Heart and sparkle particle effects
- Never jarring or attention-grabbing

**Celebratory Moments:**
- Milestone achievements with gentle confetti
- Family love with warm glow effects
- Memory additions with bookmark animations
- Week progression with growth celebrations

## Technical Implementation Notes

### Performance Considerations
- Virtual scrolling for large post histories
- Progressive image loading with elegant placeholders
- Gesture recognition with minimal processing
- Battery-conscious animation management

### Accessibility Integration
- Full VoiceOver/TalkBack support with pregnancy context
- High contrast mode with maintained warmth
- Reduced motion options
- Voice control integration points
- Screen reader friendly milestone announcements

### Testing Strategy
- Component isolation testing
- Gesture interaction testing
- Pregnancy context accuracy testing
- Family warmth calculation validation
- Performance testing on older devices

---

*These components work together to create a feed experience that feels like a supportive pregnancy companion rather than social media, focusing on meaningful family connection and gentle encouragement throughout the pregnancy journey.*