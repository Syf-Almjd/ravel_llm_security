<template>
  <div class="admin-page grid-mesh framer-appear">
    <!-- Header banner -->
    <div class="card header-banner margin-bottom-md glassmorphism">
      <div class="banner-content">
        <h2 class="gradient-text">System Administration Console</h2>
        <p>Monitor system-wide metrics, manage user roles, audit multi-user conversations, and override global gateway policies.</p>
      </div>
      <div class="banner-status-badge">
        <span class="badge badge-success">Admin Access Granted</span>
      </div>
    </div>

    <!-- Admin Tabs Navigation -->
    <div class="tabs-header" v-reveal="60">
      <button :class="['tab-btn', { active: activeTab === 'overview' }]" @click="activeTab = 'overview'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg> Overview
      </button>
      <button :class="['tab-btn', { active: activeTab === 'users' }]" @click="activeTab = 'users'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg> Users
      </button>
      <button :class="['tab-btn', { active: activeTab === 'conversations' }]" @click="activeTab = 'conversations'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg> Conversations
      </button>
      <button :class="['tab-btn', { active: activeTab === 'forensics' }]" @click="activeTab = 'forensics'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> Forensics
      </button>
      <button :class="['tab-btn', { active: activeTab === 'settings' }]" @click="activeTab = 'settings'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg> Settings
      </button>
    </div>

    <!-- Loading admin data state -->
    <div v-if="isLoading" class="loading-state framer-appear">
      <div class="spinner"></div>
      <span>Loading administrative vault...</span>
    </div>

    <div v-else>
      <!-- 1. STATS OVERVIEW -->
      <div v-if="activeTab === 'overview'" class="tab-content framer-appear">
        <div class="stats-grid">
          <div class="card stat-card">
            <span class="stat-label">System-Wide Users</span>
            <div class="stat-value">{{ stats.total_users || 0 }}</div>
            <span class="stat-change text-success">Active registration</span>
          </div>

          <div class="card stat-card">
            <span class="stat-label">Total Security Sessions</span>
            <div class="stat-value">{{ stats.total_conversations || 0 }}</div>
            <span class="stat-change text-muted">Across all user environments</span>
          </div>

          <div class="card stat-card">
            <span class="stat-label">System-Wide Threats Blocked</span>
            <div class="stat-value text-danger">{{ stats.total_threats || 0 }}</div>
            <span class="stat-change text-danger">Adversarial deflections</span>
          </div>

          <div class="card stat-card">
            <span class="stat-label">Total API Calls</span>
            <div class="stat-value">{{ stats.total_requests || 0 }}</div>
            <span class="stat-change text-muted">Shielded pipeline requests</span>
          </div>
        </div>

        <!-- System Uptime / Template list -->
        <div class="card margin-top-md">
          <div class="card-header border-bottom">
            <h4>Popular Agent Personas</h4>
          </div>
          <div class="popular-templates-list margin-top-sm">
            <div v-for="(count, name) in stats.popular_templates" :key="name" class="template-ranking-item">
              <span class="tpl-rank-name" style="display: inline-flex; align-items: center; gap: 6px;">
                <svg class="svg-icon" viewBox="0 0 24 24" style="width: 14px; height: 14px;"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                {{ name }}
              </span>
              <span class="badge badge-info mono">{{ count }} sessions</span>
            </div>
            <div v-if="!stats.popular_templates || Object.keys(stats.popular_templates).length === 0" class="table-empty">
              No persona usage records collected yet.
            </div>
          </div>
        </div>
      </div>

      <!-- 2. USER DATABASE -->
      <div v-if="activeTab === 'users'" class="tab-content card framer-appear">
        <div class="table-header">
          <h3>Register User Database</h3>
          <input v-model="userSearchQuery" type="text" placeholder="Search users by email..." class="form-control table-search-input" />
        </div>

        <div class="table-container margin-top-sm">
          <table class="table">
            <thead>
              <tr>
                <th>Teammate Account</th>
                <th>Privilege Role</th>
                <th>Security Verdicts</th>
                <th>Access Status</th>
                <th>Registered</th>
                <th class="text-right">Administration</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td class="font-semibold">{{ user.email }} ({{ user.display_name }})</td>
                <td>
                  <span :class="['badge', user.role === 'admin' ? 'badge-success' : 'badge-info']">
                    {{ user.role }}
                  </span>
                </td>
                <td class="mono font-semibold">{{ user.threat_count || 0 }} threats</td>
                <td>
                  <span :class="['badge', user.is_active ? 'badge-success' : 'badge-danger']">
                    {{ user.is_active ? 'Active' : 'Banned' }}
                  </span>
                </td>
                <td class="text-muted text-small">{{ formatDate(user.created_at) }}</td>
                <td class="text-right">
                  <div class="action-buttons">
                    <button class="btn btn-secondary btn-sm" @click="handleToggleRole(user)">
                      {{ user.role === 'admin' ? 'Demote User' : 'Promote Admin' }}
                    </button>
                    <button :class="['btn btn-sm', user.is_active ? 'btn-danger' : 'btn-primary']" @click="handleToggleBan(user)">
                      {{ user.is_active ? 'Ban Account' : 'Unban Account' }}
                    </button>
                    <button class="btn btn-danger btn-sm" @click="handleDeleteUser(user.id)">Delete</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 3. ALL CONVERSATIONS -->
      <div v-if="activeTab === 'conversations'" class="tab-content card framer-appear">
        <div class="table-header">
          <h3>Global User Conversations</h3>
          <input v-model="convSearchQuery" type="text" placeholder="Search by title..." class="form-control table-search-input" />
        </div>

        <div class="table-container margin-top-sm">
          <table class="table">
            <thead>
              <tr>
                <th>User Account</th>
                <th>Session Title</th>
                <th>Category</th>
                <th>Messages</th>
                <th>Created</th>
                <th class="text-right">Inspect</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in filteredConversations" :key="c.id">
                <td class="font-semibold">{{ c.user_email || 'System user' }}</td>
                <td class="font-semibold text-primary">{{ c.title }}</td>
                <td><span class="badge badge-info">{{ c.category }}</span></td>
                <td class="mono">{{ c.message_count || 0 }} msgs</td>
                <td class="text-muted text-small">{{ formatDate(c.createdAt) }}</td>
                <td class="text-right">
                  <button class="btn btn-secondary btn-sm" @click="inspectUserConversation(c.id)">View Messages</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 4. GLOBAL FORENSICS -->
      <div v-if="activeTab === 'forensics'" class="tab-content grid-two-cols framer-appear">
        <!-- Threats Log -->
        <div class="card">
          <div class="card-header border-bottom">
            <h4>Global Blocked Threats</h4>
          </div>
          <div class="table-container margin-top-sm">
            <div v-if="globalThreats.length === 0" class="table-empty">No threats logged yet.</div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>User</th>
                  <th>Type</th>
                  <th>Payload Snippet</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in globalThreats" :key="t.id">
                  <td class="mono text-muted text-small">{{ formatTime(t.created_at) }}</td>
                  <td class="text-small font-semibold">{{ t.user_email }}</td>
                  <td><span class="badge badge-danger">{{ t.threat_type }}</span></td>
                  <td class="prompt-text-truncated" :title="t.prompt">{{ t.prompt }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Requests Log -->
        <div class="card">
          <div class="card-header border-bottom">
            <h4>Global API Traffic</h4>
          </div>
          <div class="table-container margin-top-sm">
            <div v-if="globalRequests.length === 0" class="table-empty">No API requests processed yet.</div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>User</th>
                  <th>RTT Latency</th>
                  <th>Prompt Snippet</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in globalRequests" :key="r.id">
                  <td class="mono text-muted text-small">{{ formatTime(r.created_at) }}</td>
                  <td class="text-small font-semibold">{{ r.user_email }}</td>
                  <td class="mono">{{ r.metrics?.total_latency_ms ? `${r.metrics.total_latency_ms.toFixed(0)} ms` : '--' }}</td>
                  <td class="prompt-text-truncated" :title="r.prompt">{{ r.prompt }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 5. SYSTEM SETTINGS OVERRIDES -->
      <div v-if="activeTab === 'settings'" class="tab-content card framer-appear">
        <div class="card-header">
          <h3 class="card-title">Global Administrative Overrides</h3>
        </div>
        <form @submit.prevent="saveAdminSettings" class="margin-top-sm">
          <div class="grid-two-cols">
            <div class="form-group">
              <label class="form-label" for="defaultOllama">Default Ollama Endpoint</label>
              <input v-model="adminSettingsForm.ollama_endpoint" type="text" id="defaultOllama" class="form-control" />
            </div>

            <div class="form-group">
              <label class="form-label" for="defaultModel">Default Model Selection</label>
              <input v-model="adminSettingsForm.model_name" type="text" id="defaultModel" class="form-control" />
            </div>

            <div class="form-group">
              <label class="form-label" for="maxMem">Max Memories Per User Account</label>
              <input v-model.number="adminSettingsForm.max_memories_per_user" type="number" id="maxMem" class="form-control" />
            </div>

            <div class="form-group">
              <label class="form-label" for="guardThreshold">GUARD SLM Deflection Threshold</label>
              <input v-model.number="adminSettingsForm.guard_confidence_threshold" type="number" min="0" max="1" step="0.05" id="guardThreshold" class="form-control" />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Save Global System Overrides</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Read-only user conversation inspector modal -->
    <div v-if="inspectingConversation" class="modal-overlay">
      <div class="modal-card card animate-fade-in large-modal">
        <div class="modal-header">
          <h3>Auditing Conversation Logs</h3>
          <button class="close-btn" @click="inspectingConversation = null">×</button>
        </div>
        <div class="modal-body scroll-body read-only-chat">
          <div v-if="inspectingMessagesLoading" class="loading-state">
            <div class="spinner"></div>
            <span>Fetching messages history...</span>
          </div>
          <div v-else class="admin-message-list">
            <div v-for="m in inspectingMessages" :key="m.id" :class="['admin-msg-row', m.sender]">
              <div class="admin-msg-bubble">
                <span class="msg-sender-header font-bold">{{ m.sender === 'user' ? 'USER' : 'ASSISTANT' }} ({{ formatTime(m.timestamp) }})</span>
                <p class="margin-top-xs">{{ m.text }}</p>
                <div v-if="m.metrics" class="metrics-block mono text-muted margin-top-xs">
                  Latency: {{ m.metrics.total_latency_ms }}ms | RIS Score: {{ m.metrics.ris_score }} | Blocked: {{ m.metrics.blocked }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch, computed } from 'vue'

const config = useRuntimeConfig()
const { authHeaders } = useAuth()
const { showAlert, showConfirm } = useStore()

const isLoading = ref(true)
const activeTab = ref('overview')

// Telemetry overview stats
const stats = ref({})

// User database states
const users = ref([])
const userSearchQuery = ref('')

// Conversations inspector states
const conversations = ref([])
const convSearchQuery = ref('')
const inspectingConversation = ref(null)
const inspectingMessages = ref([])
const inspectingMessagesLoading = ref(false)

// Forensics states
const globalThreats = ref([])
const globalRequests = ref([])

// Settings states
const adminSettingsForm = reactive({
  ollama_endpoint: '',
  model_name: '',
  max_memories_per_user: 500,
  guard_confidence_threshold: 0.5
})

const loadAdminData = async () => {
  isLoading.value = true
  try {
    const headers = authHeaders()
    
    // Fetch stats
    const statsData = await $fetch(`${config.public.apiBase}/api/admin/stats`, { headers })
    stats.value = statsData

    // Fetch users list
    const usersData = await $fetch(`${config.public.apiBase}/api/admin/users`, { headers })
    users.value = usersData

    // Fetch all conversations list
    const convData = await $fetch(`${config.public.apiBase}/api/admin/conversations`, { headers })
    conversations.value = convData

    // Fetch global threats & requests logs
    const threatsData = await $fetch(`${config.public.apiBase}/api/admin/threats`, { headers })
    globalThreats.value = threatsData

    const requestsData = await $fetch(`${config.public.apiBase}/api/admin/requests`, { headers })
    globalRequests.value = requestsData

    // Fetch global settings overrides
    const settingsData = await $fetch(`${config.public.apiBase}/api/admin/settings`, { headers })
    Object.assign(adminSettingsForm, settingsData)

  } catch (err) {
    console.error('Failed to load administrative vault:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadAdminData()
})

watch(activeTab, async () => {
  await loadAdminData()
})

const filteredUsers = computed(() => {
  const query = userSearchQuery.value.trim().toLowerCase()
  return users.value.filter(u => u.email.toLowerCase().includes(query))
})

const filteredConversations = computed(() => {
  const query = convSearchQuery.value.trim().toLowerCase()
  return conversations.value.filter(c => c.title.toLowerCase().includes(query))
})

const handleToggleRole = async (user) => {
  const nextRole = user.role === 'admin' ? 'user' : 'admin'
  if (await showConfirm(`Change authorization access role of ${user.email} to ${nextRole}?`)) {
    try {
      await $fetch(`${config.public.apiBase}/api/admin/users/${user.id}/role?role=${nextRole}`, {
        method: 'PUT',
        headers: authHeaders()
      })
      await loadAdminData()
    } catch (err) {
      console.error(err)
    }
  }
}

const handleToggleBan = async (user) => {
  const action = user.is_active ? 'ban' : 'unban'
  if (await showConfirm(`Are you sure you want to ${action} ${user.email}?`)) {
    try {
      await $fetch(`${config.public.apiBase}/api/admin/users/${user.id}/ban`, {
        method: 'PUT',
        headers: authHeaders()
      })
      await loadAdminData()
    } catch (err) {
      console.error(err)
    }
  }
}

const handleDeleteUser = async (id) => {
  if (await showConfirm('Permanently delete this user and purge all their secure conversations and memories? THIS ACTION CANNOT BE UNDONE.')) {
    try {
      await $fetch(`${config.public.apiBase}/api/admin/users/${id}`, {
        method: 'DELETE',
        headers: authHeaders()
      })
      await loadAdminData()
    } catch (err) {
      console.error(err)
    }
  }
}

const inspectUserConversation = async (convId) => {
  inspectingConversation.value = convId
  inspectingMessagesLoading.value = true
  inspectingMessages.value = []
  try {
    const data = await $fetch(`${config.public.apiBase}/api/admin/conversations/${convId}`, {
      headers: authHeaders()
    })
    inspectingMessages.value = data
  } catch (err) {
    console.error('Failed to audit messages:', err)
  } finally {
    inspectingMessagesLoading.value = false
  }
}

const saveAdminSettings = async () => {
  try {
    await $fetch(`${config.public.apiBase}/api/admin/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders()
      },
      body: adminSettingsForm
    })
    await showAlert('Global administrative defaults saved successfully!', 'Success')
  } catch (err) {
    console.error(err)
    await showAlert('Failed to save settings: ' + err.message, 'Error')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
</script>

<style scoped>
.grid-two-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.header-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background-color: var(--bg-primary);
  border-color: var(--border-color);
}

.banner-content h2 {
  font-size: 22px;
  margin-bottom: 4px;
}

.banner-content p {
  font-size: 14.5px;
  color: var(--text-secondary);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px;
  gap: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: var(--brand-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.table-header h3 {
  font-size: 16px;
  font-weight: 600;
}

.table-search-input {
  width: 240px;
  font-size: 13px;
  padding: 8px 12px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.text-right {
  text-align: right;
}

.prompt-text-truncated {
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 13px;
}

.template-ranking-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px dashed var(--border-color);
}

.tpl-rank-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

/* Modal inspector styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.modal-card {
  width: 100%;
  max-width: 680px;
  padding: 32px;
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-lg);
  background-color: var(--bg-primary);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h3 {
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-muted);
}

.close-btn:hover {
  color: var(--text-primary);
}

.scroll-body {
  max-height: 480px;
  overflow-y: auto;
}

.admin-message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.admin-msg-row {
  display: flex;
  width: 100%;
}

.admin-msg-row.user {
  justify-content: flex-end;
}

.admin-msg-bubble {
  max-width: 80%;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
}

.admin-msg-row.user .admin-msg-bubble {
  background-color: var(--text-primary);
  color: var(--bg-primary);
  border-color: var(--text-primary);
}

.msg-sender-header {
  font-size: 11px;
  color: var(--text-muted);
  display: block;
}

.admin-msg-row.user .msg-sender-header {
  color: rgba(255, 255, 255, 0.6);
}

.metrics-block {
  font-size: 10.5px;
  border-top: 1px dashed var(--border-color);
  padding-top: 6px;
  margin-top: 8px;
}

.admin-msg-row.user .metrics-block {
  border-top-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
}

.margin-top-xs {
  margin-top: 4px;
}
.font-bold {
  font-weight: bold;
}
</style>
