/**
 * Avatar utility for consistent user avatars throughout the app
 * Uses design tokens and calculates fixed colors based on user ID
 */

// Design token colors for avatars (warm, pregnancy-friendly palette)
const AVATAR_COLORS = [
  '#F8BBD0', // soft-pink
  '#B2DFDB', // gentle-mint  
  '#E1BEE7', // muted-lavender
  '#FFCDD2', // light-coral
  '#BBDEFB', // soft-blue
  '#C8E6C9', // sage-green
  '#DBEAFE', // light-blue (replaced warm-peach)
  '#F8BBD0', // rose-pink
  '#D1C4E9', // soft-purple
  '#DCEDC8', // light-green
] as const

interface User {
  id?: string
  email?: string
  first_name?: string
  last_name?: string
  display_name?: string
}

/**
 * Generate a consistent hex color for a user based on their ID
 */
export function getUserAvatarColor(userId?: string): string {
  if (!userId) {
    return AVATAR_COLORS[0] // Default to soft-pink
  }
  
  // Create a simple hash from the user ID
  let hash = 0
  for (let i = 0; i < userId.length; i++) {
    const char = userId.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32-bit integer
  }
  
  // Use absolute value and modulo to get consistent color index
  const colorIndex = Math.abs(hash) % AVATAR_COLORS.length
  return AVATAR_COLORS[colorIndex]
}

/**
 * Get user initials for avatar display
 */
export function getUserInitials(user?: User): string {
  if (!user) {
    return '?'
  }
  
  // Try display_name first, then first/last name, then email
  let name = ''
  if (user.display_name) {
    name = user.display_name
  } else if (user.first_name && user.last_name) {
    name = `${user.first_name} ${user.last_name}`
  } else if (user.first_name) {
    name = user.first_name
  } else if (user.email) {
    name = user.email
  } else {
    return '?'
  }
  
  const words = name.split(' ').filter(word => word.length > 0)
  
  if (words.length === 0) {
    return '?'
  }
  
  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase()
  }
  
  // Take first letter of first two words
  return words
    .slice(0, 2)
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
}

/**
 * Get user display name for showing full name
 */
export function getUserDisplayName(user?: User): string {
  if (!user) {
    return 'Unknown User'
  }
  
  if (user.display_name) {
    return user.display_name
  }
  
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`
  }
  
  if (user.first_name) {
    return user.first_name
  }
  
  if (user.email) {
    return user.email
  }
  
  return 'Anonymous'
}

/**
 * Generate avatar CSS classes for consistent styling
 */
export function getAvatarClasses(size: 'sm' | 'md' | 'lg' = 'md'): string {
  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm', 
    lg: 'w-12 h-12 text-base'
  }
  
  return `${sizeClasses[size]} rounded-full flex items-center justify-center font-medium text-white`
}