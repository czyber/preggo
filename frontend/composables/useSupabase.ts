import { createClient, type SupabaseClient } from '@supabase/supabase-js'

let supabase: SupabaseClient | null = null

export const useSupabase = () => {
  if (!supabase) {
    const config = useRuntimeConfig()
    const supabaseUrl = config.public.supabaseUrl
    const supabaseAnonKey = config.public.supabaseAnonKey

    if (!supabaseUrl || !supabaseAnonKey) {
      throw new Error('Missing Supabase configuration. Please check your environment variables.')
    }

    supabase = createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
        flowType: 'pkce'
      }
    })
  }

  return supabase
}

// Composables for specific Supabase features
export const useSupabaseAuth = () => {
  const supabase = useSupabase()
  return supabase.auth
}

export const useSupabaseUser = () => {
  const auth = useSupabaseAuth()
  const user = ref(null)

  // Get current user
  const getCurrentUser = async () => {
    const { data } = await auth.getUser()
    user.value = data.user
    return data.user
  }

  // Listen for auth changes
  // DISABLED: Moved to useAuth.ts to prevent duplicate listeners causing infinite loops
  // auth.onAuthStateChange((event, session) => {
  //   user.value = session?.user || null
  // })

  return {
    user: readonly(user),
    getCurrentUser
  }
}

export const useSupabaseSession = () => {
  const auth = useSupabaseAuth()
  const session = ref(null)

  // Get current session
  const getCurrentSession = async () => {
    const { data } = await auth.getSession()
    session.value = data.session
    return data.session
  }

  // Listen for auth changes  
  // DISABLED: Moved to useAuth.ts to prevent duplicate listeners causing infinite loops
  // auth.onAuthStateChange((event, newSession) => {
  //   session.value = newSession
  // })

  return {
    session: readonly(session),
    getCurrentSession
  }
}