import { computed } from 'vue'

export const useAuth = () => {
  const currentUser = useState<any>('auth_user', () => null)
  const token = useState<string | null>('auth_token', () => null)
  const config = useRuntimeConfig()

  // On client side, load from localStorage
  if (import.meta.client && !token.value) {
    token.value = localStorage.getItem('ravel_token')
    const savedUser = localStorage.getItem('ravel_user')
    if (savedUser) {
      currentUser.value = JSON.parse(savedUser)
    }
  }

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => currentUser.value?.role === 'admin')

  const authHeaders = () => {
    return token.value ? { 'Authorization': `Bearer ${token.value}` } : {}
  }

  const setAuth = (user: any, jwtToken: string) => {
    currentUser.value = user
    token.value = jwtToken
    if (import.meta.client) {
      localStorage.setItem('ravel_token', jwtToken)
      localStorage.setItem('ravel_user', JSON.stringify(user))
    }
  }

  const clearAuth = () => {
    currentUser.value = null
    token.value = null
    if (import.meta.client) {
      localStorage.removeItem('ravel_token')
      localStorage.removeItem('ravel_user')
      navigateTo('/login')
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const res = await $fetch<any>(`${config.public.apiBase}/api/auth/login`, {
        method: 'POST',
        body: { email, password }
      })
      setAuth(res.user, res.token)
      return { success: true }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || err.message || 'Login failed' }
    }
  }

  const register = async (displayName: string, email: string, password: string) => {
    try {
      const res = await $fetch<any>(`${config.public.apiBase}/api/auth/register`, {
        method: 'POST',
        body: { display_name: displayName, email, password }
      })
      setAuth(res.user, res.token)
      return { success: true }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || err.message || 'Registration failed' }
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await $fetch(`${config.public.apiBase}/api/auth/logout`, {
          method: 'POST',
          headers: authHeaders()
        })
      }
    } catch (err) {
      console.warn('Logout request failed on server:', err)
    } finally {
      clearAuth()
    }
  }

  const fetchProfile = async () => {
    if (!token.value) return
    try {
      const user = await $fetch<any>(`${config.public.apiBase}/api/auth/me`, {
        headers: authHeaders()
      })
      currentUser.value = user
      if (import.meta.client) {
        localStorage.setItem('ravel_user', JSON.stringify(user))
      }
    } catch (err: any) {
      if (err.status === 401) {
        clearAuth()
      }
    }
  }

  const updateProfile = async (displayName: string, initials: string) => {
    try {
      const user = await $fetch<any>(`${config.public.apiBase}/api/auth/me`, {
        method: 'PUT',
        headers: authHeaders(),
        body: { display_name: displayName, avatar_initials: initials }
      })
      currentUser.value = user
      if (import.meta.client) {
        localStorage.setItem('ravel_user', JSON.stringify(user))
      }
      return { success: true }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || err.message }
    }
  }

  return {
    currentUser,
    token,
    isAuthenticated,
    isAdmin,
    authHeaders,
    login,
    register,
    logout,
    fetchProfile,
    updateProfile,
    clearAuth
  }
}
