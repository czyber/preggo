# Preggo Content Database

This directory contains the comprehensive pregnancy content system for the Preggo app, designed to provide supportive, medically accurate, and culturally sensitive content throughout the entire pregnancy journey.

## Directory Structure

```
content-database/
├── baby-development/          # Weekly baby development content
├── weekly-tips/              # Comprehensive weekly guidance tips
├── emotional-support/        # Mental health and emotional wellness content
├── family-engagement/        # Activities to strengthen family bonds
├── cultural-adaptations/     # Templates for diverse cultural contexts
├── seed-data/               # Database-ready JSON files for initial content
├── content-templates/       # Standardized templates for content creation
└── README.md               # This documentation file
```

## Content Philosophy

### Core Principles
- **Companionship Over Information**: Content feels like advice from a caring, knowledgeable friend
- **Progressive Disclosure**: Information unfolds naturally without overwhelming users
- **Celebration-Focused**: Every stage of pregnancy is celebrated and supported
- **Family-Inclusive**: Content considers the entire family unit and support system
- **Culturally Sensitive**: Respectful of diverse backgrounds, traditions, and choices

### Tone and Voice
Following the design tokens from `/specs/DESIGN_TOKENS.md`:
- **Warm and Inviting**: Welcoming, supportive friend tone
- **Empathetic and Supportive**: Gentle, understanding language  
- **Calm and Reassuring**: Promotes peace and comfort
- **Medically Accurate**: Evidence-based while remaining approachable

## Content Categories

### 1. Baby Development (`/baby-development/`)
Creative, wonder-inspiring weekly development content featuring:
- **Creative Size Comparisons**: Beyond traditional fruits to personal, meaningful objects
- **Development Highlights**: Key milestones and achievements each week
- **Amazing Facts**: Wonder-inducing information about baby's capabilities
- **Connection Activities**: Ways families can bond with baby at each stage
- **Family Sharing Prompts**: Ready-to-share updates for family networks

**Example Files:**
- `week-04.json` - Foundation building and genetic programming
- `week-06.json` - First heartbeat milestone
- `week-12.json` - End of first trimester celebration
- `week-20.json` - Halfway milestone and anatomy scan

### 2. Weekly Tips (`/weekly-tips/`)
Comprehensive guidance organized by categories:
- **Health & Wellness**: Physical care, nutrition, symptom management
- **Emotional Support**: Processing feelings, anxiety management, joy cultivation
- **Preparation**: Planning tasks, appointments, practical preparations  
- **Partner & Family**: Involving loved ones, communication, relationship care
- **Self-Care**: Rest, comfort, personal nurturing
- **Milestone Celebration**: Acknowledging progress and special moments

### 3. Emotional Support (`/emotional-support/`)
Mental health and emotional wellness content:
- **Anxiety Management**: Coping strategies for pregnancy worries
- **Complex Emotions**: Validation for mixed feelings and uncertainty
- **Identity Changes**: Processing the transition to parenthood
- **Relationship Guidance**: Navigating changing dynamics
- **Support System Building**: Creating and maintaining connections

### 4. Family Engagement (`/family-engagement/`)
Activities and prompts to strengthen family bonds:
- **Partner Bonding**: Activities for couples throughout pregnancy
- **Extended Family Involvement**: Ways to include grandparents and relatives
- **Memory Creation**: Photo, journaling, and keepsake suggestions
- **Communication Guidance**: Facilitating healthy family conversations
- **Celebration Planning**: Milestone and announcement ideas

### 5. Cultural Adaptations (`/cultural-adaptations/`)
Framework for inclusive, respectful content:
- **Cultural Sensitivity Guidelines**: Ensuring respectful content for all backgrounds
- **Family Structure Adaptations**: Single parents, same-sex couples, extended families
- **Religious Considerations**: Respectful integration of spiritual elements
- **Socioeconomic Sensitivity**: Accessible content regardless of economic circumstances
- **Language Guidelines**: Inclusive terminology and assumptions

## Database Integration

### Seed Data Format (`/seed-data/`)
Content is structured to match the backend `PregnancyContent` model:

```json
{
  "content_type": "BABY_DEVELOPMENT",
  "week_number": 12,
  "trimester": 1,
  "title": "First Trimester Victory",
  "subtitle": "All systems in place",
  "content_body": "Markdown formatted content...",
  "content_summary": "Brief summary for cards...",
  "reading_time_minutes": 4,
  "priority": 100,
  "tags": ["milestone", "celebration"],
  "personalization_rules": {...},
  "target_audience": ["first_time_parent"],
  "medical_review_status": "APPROVED",
  "delivery_methods": ["FEED_INTEGRATION"],
  "optimal_delivery_time": "09:00",
  "is_active": true,
  "version": 1
}
```

### Content Categories Available:
- `BABY_DEVELOPMENT` - Weekly development milestones
- `WEEKLY_TIP` - Comprehensive weekly guidance
- `EMOTIONAL_SUPPORT` - Mental health and emotional content  
- `HEALTH_WELLNESS` - Physical health guidance
- `PREPARATION` - Planning and preparation tasks
- `PARTNER_FAMILY` - Family relationship content
- `MILESTONE_CELEBRATION` - Special moment recognition

## Content Management (`/content-templates/`)

### Quality Assurance Standards
- **Medical Accuracy**: Healthcare provider review for all health content
- **Cultural Sensitivity**: Inclusive language and diverse perspective review
- **Accessibility**: 8th grade reading level, screen reader compatibility
- **User Testing**: Feedback from diverse user groups before publication

### Personalization Framework
Content adapts based on:
- **Pregnancy Stage**: Week-specific and trimester-appropriate information
- **Family Structure**: Single parents, couples, extended family involvement
- **Cultural Background**: Traditions, values, and cultural considerations
- **Emotional State**: Anxiety-sensitive, celebration-amplifying content
- **Information Preferences**: Detail level and communication style preferences

### Update and Maintenance Workflow
1. **Content Creation**: Evidence-based writing following templates
2. **Medical Review**: Healthcare provider accuracy validation
3. **Cultural Review**: Inclusive language and sensitivity check
4. **User Testing**: Feedback from diverse pregnancy demographics  
5. **Publication**: Approved content activation in system
6. **Ongoing Monitoring**: User feedback integration and regular updates

## Usage Instructions

### For Content Creators
1. Use templates in `/content-templates/` for consistent structure
2. Follow cultural sensitivity guidelines in `/cultural-adaptations/`
3. Ensure medical accuracy through proper review process
4. Test content with diverse user groups before publication

### For Developers
1. Import seed data files for initial database population
2. Use content structure for new content creation endpoints
3. Implement personalization rules for adaptive content delivery
4. Follow accessibility guidelines for content presentation

### For Product Teams
1. Reference content strategy documents for feature alignment
2. Use engagement metrics to identify content improvement opportunities
3. Coordinate with medical and cultural review boards for content updates
4. Monitor user feedback for continuous content improvement

## Key Sample Content

### Baby Development Highlights
- **Week 4**: "Smaller than the period at the end of this sentence, but already containing all the instructions for your baby's entire development"
- **Week 6**: "Two hearts are now beating in your body - yours and your baby's"
- **Week 12**: "All major organs are now in place - time to celebrate this incredible milestone!"
- **Week 20**: "Your baby can hear your voice now - start those bedtime stories and lullabies!"

### Emotional Support Themes
- Validation that complex emotions are normal and healthy
- Practical anxiety management strategies for pregnancy concerns
- Support for identity changes and relationship adjustments
- Encouragement for seeking professional help when needed

### Family Engagement Focus
- Partner bonding activities throughout all trimesters
- Ways to involve extended family in the pregnancy journey
- Memory creation and documentation suggestions
- Communication strategies for family harmony

## Success Metrics

### User Engagement
- Content completion and reading time
- Family sharing of content within networks
- Return visits and content bookmarking
- Memory book integration rates

### User Satisfaction  
- Helpfulness ratings and feedback
- Emotional impact and comfort scores
- Cultural appropriateness assessments
- Accessibility and usability ratings

### Medical Quality
- Healthcare provider feedback and endorsements
- Medical accuracy validation scores
- User-reported safety and concern tracking
- Professional community engagement

## Contributing

When adding new content:
1. Follow established templates and guidelines
2. Ensure medical review for health-related content
3. Include cultural sensitivity considerations
4. Test content with diverse user groups
5. Update relevant seed data files
6. Document any new personalization rules or adaptations

This content database forms the foundation of the Preggo app's supportive, comprehensive pregnancy journey experience, designed to feel like having a knowledgeable, caring friend available 24/7 throughout the entire pregnancy experience.