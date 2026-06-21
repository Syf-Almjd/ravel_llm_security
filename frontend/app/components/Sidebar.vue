<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </div>
      <span class="sidebar-title">Ravel</span>
    </div>

    <nav class="sidebar-nav">
      <!-- CORE SECTION -->
      <div class="nav-section">
        <div class="nav-section-title">Core Operations</div>
        <ul class="nav-list">
          <li>
            <NuxtLink to="/dashboard" class="nav-link">
              <svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
              <span>Dashboard</span>
            </NuxtLink>
          </li>
          <li>
            <NuxtLink to="/templates" class="nav-link">
              <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
              <span>Personas</span>
            </NuxtLink>
          </li>
          <li>
            <NuxtLink to="/chat" class="nav-link">
              <svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
              <span>Security Chat</span>
            </NuxtLink>
          </li>
          <li>
            <NuxtLink to="/memory" class="nav-link">
              <svg class="svg-icon" viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path></svg>
              <span>Memory Bank</span>
            </NuxtLink>
          </li>
        </ul>
      </div>

      <!-- AUDIT & CONFIG SECTION -->
      <div class="nav-section">
        <div class="nav-section-title">Audit & Configuration</div>
        <ul class="nav-list">
          <li>
            <NuxtLink to="/security" class="nav-link">
              <svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
              <span>Security Hub</span>
            </NuxtLink>
          </li>
          <li>
            <NuxtLink to="/settings" class="nav-link">
              <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
              <span>Settings</span>
            </NuxtLink>
          </li>
          <li>
            <NuxtLink to="/docs" class="nav-link">
              <svg class="svg-icon" viewBox="0 0 24 24"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
              <span>Developer Docs</span>
            </NuxtLink>
          </li>
        </ul>
      </div>

      <!-- ADMINISTRATION SECTION -->
      <div v-if="isAdmin" class="nav-section">
        <div class="nav-section-title">Administration</div>
        <ul class="nav-list">
          <li>
            <NuxtLink to="/admin" class="nav-link">
              <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
              <span>Admin Console</span>
            </NuxtLink>
          </li>
        </ul>
      </div>
    </nav>

    <!-- USER FOOTER -->
    <div class="sidebar-footer">
      <div v-if="currentUser" class="user-profile-menu" @click="handleLogout">
        <div class="user-avatar">
          {{ currentUser.avatar_initials || currentUser.display_name?.substring(0, 2).toUpperCase() || 'US' }}
        </div>
        <div class="user-info">
          <div class="user-name">{{ currentUser.display_name }}</div>
          <div class="user-role">{{ currentUser.role }}</div>
        </div>
        <svg class="svg-icon logout-icon" title="Log Out" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
      </div>
    </div>
  </aside>
</template>

<script setup>
const { currentUser, isAdmin, logout } = useAuth()
const { showConfirm } = useStore()

const handleLogout = async () => {
  if (await showConfirm('Are you sure you want to log out?')) {
    await logout()
  }
}
</script>

<style scoped>
.logout-icon {
  font-size: 14px;
  opacity: 0.6;
  transition: opacity 0.2s;
}
.user-profile-menu:hover .logout-icon {
  opacity: 1;
}
</style>
