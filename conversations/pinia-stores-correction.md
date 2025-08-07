# Pinia Stores Correction

## Overview

This document records the critical correction made to the frontend architecture on 2025-08-03. The pregnancy tracking app "preggo" was incorrectly using Vue composables for state management when it should have been using Pinia stores following the established pattern.

## Problem Identified

During development, I mistakenly created Vue composables for data operations when the project already had an established pattern of using Pinia stores for state management. This was evident from:

1. The existing `items.ts` store in `/stores/` directory
2. The project's use of Pinia for reactive state management
3. The established pattern of using `defineStore` with state, getters, and actions

## Incorrect Implementation (Deleted)

The following composables were incorrectly created and have been **deleted**:

- `composables/useAuth.ts` - Authentication operations
- `composables/usePregnancy.ts` - Pregnancy data management  
- `composables/useFamily.ts` - Family groups and members
- `composables/usePosts.ts` - Posts, comments, reactions
- `composables/useMilestones.ts` - Milestones and appointments
- `composables/useHealth.ts` - Health tracking data
- `composables/useStorage.ts` - Storage operations

**Note:** Only `composables/useApi.ts` was kept as it serves as the API client layer.

## Correct Implementation (Created)

The following Pinia stores were created following the established pattern from `items.ts`:

### 1. Authentication Store (`stores/auth.ts`)
- **State**: `user`, `isAuthenticated`, `loading`, `error`
- **Getters**: `currentUser`, `isLoggedIn`, `userRole`, `userPreferences`
- **Actions**: `login()`, `register()`, `getCurrentUser()`, `updateUser()`, `logout()`, `reset()`
- **Types**: `UserResponse`, `LoginRequest`, `RegisterRequest`, `AuthResponse`

### 2. Pregnancy Store (`stores/pregnancy.ts`)
- **State**: `pregnancies`, `currentPregnancy`, `loading`, `error`
- **Getters**: `getPregnancyById()`, `activePregnancies`, `completedPregnancies`, `currentWeek`, `dueDate`, `babyInfo`
- **Actions**: `fetchPregnancies()`, `createPregnancy()`, `updatePregnancy()`, `deletePregnancy()`, `fetchPregnancyById()`, `setCurrentPregnancy()`, `reset()`
- **Types**: `PregnancyResponse`, `PregnancyCreate`, `PregnancyUpdate`

### 3. Family Store (`stores/family.ts`)
- **State**: `familyGroups`, `currentFamilyGroup`, `familyMembers`, `familyInvitations`, `loading`, `error`
- **Getters**: `getFamilyGroupById()`, `getFamilyMemberById()`, `activeFamilyMembers`, `pendingInvitations`, `acceptedInvitations`, `currentFamilyMembers`
- **Actions**: `fetchFamilyGroups()`, `createFamilyGroup()`, `updateFamilyGroup()`, `fetchFamilyMembers()`, `addFamilyMember()`, `updateFamilyMember()`, `removeFamilyMember()`, `fetchFamilyInvitations()`, `createFamilyInvitation()`, `updateFamilyInvitation()`, `setCurrentFamilyGroup()`, `reset()`
- **Types**: `FamilyGroupResponse`, `FamilyGroupCreate`, `FamilyGroupUpdate`, `FamilyMemberResponse`, `FamilyMemberCreate`, `FamilyMemberUpdate`, `FamilyInvitationResponse`, `FamilyInvitationCreate`, `FamilyInvitationUpdate`

### 4. Posts Store (`stores/posts.ts`)
- **State**: `posts`, `comments`, `currentPost`, `loading`, `error`
- **Getters**: `getPostById()`, `getCommentsForPost()`, `publicPosts`, `familyPosts`, `privatePosts`, `postsWithMedia`, `postsByType()`
- **Actions**: `fetchPosts()`, `createPost()`, `updatePost()`, `deletePost()`, `fetchPostComments()`, `createComment()`, `updateComment()`, `deleteComment()`, `likePost()`, `viewPost()`, `sharePost()`, `setCurrentPost()`, `reset()`
- **Types**: `PostResponse`, `PostCreate`, `PostUpdate`, `CommentResponse`, `CommentCreate`, `CommentUpdate`, `MediaItemCreate`, `PostViewCreate`, `PostShareCreate`

### 5. Milestones Store (`stores/milestones.ts`)
- **State**: `milestones`, `appointments`, `importantDates`, `weeklyChecklists`, `currentMilestone`, `currentAppointment`, `loading`, `error`
- **Getters**: `getMilestoneById()`, `getAppointmentById()`, `completedMilestones`, `pendingMilestones`, `upcomingAppointments`, `pastAppointments`, `milestonesByWeek()`, `milestonesByType()`
- **Actions**: `fetchMilestones()`, `createMilestone()`, `updateMilestone()`, `deleteMilestone()`, `fetchAppointments()`, `createAppointment()`, `updateAppointment()`, `deleteAppointment()`, `fetchWeeklyChecklists()`, `createWeeklyChecklist()`, `updateWeeklyChecklist()`, `setCurrentMilestone()`, `setCurrentAppointment()`, `reset()`
- **Types**: `MilestoneResponse`, `MilestoneCreate`, `MilestoneUpdate`, `AppointmentResponse`, `AppointmentCreate`, `AppointmentUpdate`, `ImportantDateCreate`, `WeeklyChecklistCreate`, `WeeklyChecklistUpdate`

### 6. Health Store (`stores/health.ts`)
- **State**: `pregnancyHealth`, `healthAlerts`, `symptoms`, `weightEntries`, `moodEntries`, `loading`, `error`
- **Getters**: `getHealthAlertById()`, `activeHealthAlerts`, `criticalHealthAlerts`, `recentSymptoms()`, `recentWeightEntries()`, `recentMoodEntries()`, `averageMoodRating()`, `weightTrend`
- **Actions**: `fetchPregnancyHealth()`, `createPregnancyHealth()`, `updatePregnancyHealth()`, `fetchHealthAlerts()`, `createHealthAlert()`, `updateHealthAlert()`, `fetchSymptoms()`, `trackSymptom()`, `fetchWeightEntries()`, `createWeightEntry()`, `fetchMoodEntries()`, `createMoodEntry()`, `reset()`
- **Types**: `PregnancyHealthCreate`, `PregnancyHealthUpdate`, `HealthAlertResponse`, `HealthAlertCreate`, `HealthAlertUpdate`, `SymptomTrackingCreate`, `WeightEntryCreate`, `MoodEntryCreate`

## Pattern Consistency

All stores follow the exact same pattern as the original `items.ts` store:

1. **Import Structure**: 
   ```typescript
   import { defineStore } from 'pinia'
   import type { components } from '@/types/api'
   ```

2. **Type Aliases**: Clean type aliases from the generated API types
   ```typescript
   type User = components['schemas']['UserResponse']
   ```

3. **Store Definition**: Using `defineStore` with consistent structure
   ```typescript
   export const useStoreNameStore = defineStore('storeName', {
     state: () => ({ /* reactive state */ }),
     getters: { /* computed properties */ },
     actions: { /* methods for API calls and state mutations */ }
   })
   ```

4. **Error Handling**: Consistent error handling pattern in all actions
5. **API Integration**: All stores use the `useApi()` composable for API calls
6. **Loading States**: All stores include loading and error state management
7. **Reset Method**: All stores include a `reset()` method for clearing state

## Updated References

The following page files were updated to use the new Pinia stores:

### `pages/index.vue`
- **Before**: `useAuth()`, `usePregnancy()`
- **After**: `useAuthStore()`, `usePregnancyStore()`
- Updated computed properties to use store getters
- Updated methods to use store actions

### `pages/auth/login.vue`
- **Before**: `useAuth()`
- **After**: `useAuthStore()`
- Updated login logic to use `authStore.login()`

### `pages/auth/signup.vue`
- **Before**: `useAuth()`
- **After**: `useAuthStore()`
- Updated registration logic to use `authStore.register()`

## Directory Structure After Correction

```
frontend/
├── composables/
│   └── useApi.ts              # ✅ Kept - API client layer
├── stores/
│   ├── items.ts              # ✅ Original example store
│   ├── auth.ts               # ✅ New - Authentication
│   ├── pregnancy.ts          # ✅ New - Pregnancy data
│   ├── family.ts             # ✅ New - Family management
│   ├── posts.ts              # ✅ New - Posts and comments
│   ├── milestones.ts         # ✅ New - Milestones and appointments
│   └── health.ts             # ✅ New - Health tracking
└── pages/
    ├── index.vue             # ✅ Updated to use stores
    └── auth/
        ├── login.vue         # ✅ Updated to use stores
        └── signup.vue        # ✅ Updated to use stores
```

## Key Benefits of the Correction

1. **Consistency**: All state management now follows the same established pattern
2. **Type Safety**: Full TypeScript integration with generated API types
3. **Reactivity**: Proper Vue 3 reactivity with Pinia's state management
4. **Reusability**: Stores can be easily imported and used across components
5. **Maintainability**: Single source of truth for each domain's state
6. **Performance**: Pinia's optimized reactivity system
7. **DevTools**: Full integration with Vue DevTools for debugging

## Lessons Learned

1. **Always examine existing patterns** before creating new architecture components
2. **State management strategy should be consistent** across the entire application
3. **Composables are for reusable logic**, not state management in a Pinia app
4. **Following established patterns** reduces complexity and improves maintainability

## Future Development

Going forward, all new features should:

1. **Use Pinia stores for state management** following the established pattern
2. **Use composables only for reusable logic** like `useApi()` for API calls
3. **Follow the same structure** for state, getters, and actions
4. **Include proper TypeScript types** from the generated API schemas
5. **Implement consistent error handling** and loading states

This correction ensures the frontend architecture is consistent, maintainable, and follows Vue 3 + Pinia best practices.
