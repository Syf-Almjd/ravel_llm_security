export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated, isAdmin } = useAuth()

  // Public pages
  const isPublic = to.path === '/' || to.path === '/login' || to.path === '/register'

  // If not authenticated and trying to access a protected page
  if (!isAuthenticated.value && !isPublic) {
    return navigateTo('/login')
  }

  // If authenticated and trying to access login/register
  if (isAuthenticated.value && (to.path === '/login' || to.path === '/register')) {
    return navigateTo('/dashboard')
  }

  // If authenticated but not admin trying to access admin panel
  if (isAuthenticated.value && to.path.startsWith('/admin') && !isAdmin.value) {
    return navigateTo('/dashboard')
  }
})
