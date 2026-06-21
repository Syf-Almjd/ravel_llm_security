<template>
  <div class="chat-layout-wrapper">
    <!-- Left panel: Sessions History -->
    <aside class="chat-sessions-sidebar">
      <div class="sidebar-actions">
        <button class="btn btn-primary w-full" @click="handleCreateSession">
          <span class="plus-icon">+</span> New Session
        </button>
      </div>

      <div class="search-box-wrapper">
        <svg class="svg-icon search-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input v-model="searchQuery" type="text" placeholder="Search sessions..." class="search-input" />
      </div>

      <div class="sessions-list-scroll">
        <div v-if="filteredGroups.length === 0" class="list-empty">
          <span>No sessions found</span>
        </div>

        <div v-else v-for="group in filteredGroups" :key="group.name" class="history-group">
          <div class="history-group-header">{{ group.name }}</div>
          <ul class="history-group-list">
            <li v-for="c in group.items" :key="c.id" 
                :class="['history-item', { active: activeId === c.id }]"
                @click="navigateToSession(c.id)">
              <div class="history-item-body">
                <span class="history-item-title" :title="c.title">{{ c.title }}</span>
                <span :class="['category-badge', getCatClass(c.category)]">{{ c.category }}</span>
              </div>
              <div class="history-item-controls">
                <svg v-if="c.pinned" class="svg-icon pinned-indicator" viewBox="0 0 24 24" style="color: var(--brand-primary);"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                <button class="delete-btn" @click.stop="handleDeleteSession(c.id)" title="Delete Session">
                  <svg class="svg-icon delete-icon" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                </button>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </aside>

    <!-- Center panel: Nested page (Empty state or active chat) -->
    <div class="chat-main-feed">
      <NuxtPage :chat-config="config" @update-category="updateSessionCategory" />
    </div>

    <!-- Right panel: Config Drawer -->
    <aside :class="['config-drawer', { collapsed: isDrawerCollapsed }]">
      <div class="drawer-header">
        <h4>Guardrail Configurations</h4>
        <span class="drawer-subtitle">Active pipeline filters</span>
      </div>

      <div class="drawer-content">
        <!-- Raw Mode Switch -->
        <div class="raw-toggle-card card">
          <label class="checkbox-label">
            <input type="checkbox" v-model="config.raw_mode" class="form-checkbox" />
            <span class="raw-label-text">Raw Mode (Bypass Ravel)</span>
          </label>
          <p class="policy-desc">Disable all gateway shield verifications. Send prompt directly to model.</p>
        </div>

        <!-- Individual Toggles -->
        <div class="toggles-list" :class="{ disabled: config.raw_mode }">
          <div class="policy-toggle-item card">
            <div class="toggle-item-header">
              <span class="policy-title">GUARD-SLM Shield</span>
              <label class="switch-toggle">
                <input type="checkbox" v-model="config.enable_guard" :disabled="config.raw_mode" />
                <span class="slider"></span>
              </label>
            </div>
            <p class="policy-desc">SVM classifier operating on early layer activations to flag prompt injections.</p>
          </div>

          <div class="policy-toggle-item card">
            <div class="toggle-item-header">
              <span class="policy-title">EASE Reasoning Router</span>
              <label class="switch-toggle">
                <input type="checkbox" v-model="config.enable_ease" :disabled="config.raw_mode" />
                <span class="slider"></span>
              </label>
            </div>
            <p class="policy-desc">Routes complex requests to deep Chain-of-Thought thinking, bypassing simple ones.</p>
          </div>

          <div class="policy-toggle-item card">
            <div class="toggle-item-header">
              <span class="policy-title">DRAG Knowledge Retrieval</span>
              <label class="switch-toggle">
                <input type="checkbox" v-model="config.enable_drag" :disabled="config.raw_mode" />
                <span class="slider"></span>
              </label>
            </div>
            <p class="policy-desc">Fetches facts from vector database and injects references to prevent hallucinations.</p>
          </div>

          <div class="policy-toggle-item card">
            <div class="toggle-item-header">
              <span class="policy-title">DoLa Layer Contrasting</span>
              <label class="switch-toggle">
                <input type="checkbox" v-model="config.enable_dola" :disabled="config.raw_mode" />
                <span class="slider"></span>
              </label>
            </div>
            <p class="policy-desc">Contrasts probabilities from early vs late layers to suppress factual hallucinations.</p>
          </div>
        </div>

        <!-- Category Select -->
        <div class="drawer-section border-top">
          <h5>Session Category</h5>
          <select v-model="config.category" class="form-control select-dropdown margin-top-sm" @change="handleCategoryChange">
            <option value="General">General Inquiries</option>
            <option value="Red Team">Red Team Testing</option>
            <option value="Audit">Compliance Audit</option>
          </select>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const { sortedConversations, createConversation, deleteConversation, fetchConversations, updateConversationCategory, showConfirm } = useStore()
const route = useRoute()

const searchQuery = ref('')
const isDrawerCollapsed = useState('chat_drawer_collapsed', () => false)

// Shared reactive config using useState
const config = useState('chat_config', () => ({
  enable_guard: true,
  enable_ease: true,
  enable_drag: true,
  enable_dola: true,
  raw_mode: false,
  category: 'General'
}))

const activeId = computed(() => route.params.id)

// Fetch lists on load
onMounted(async () => {
  await fetchConversations()
  
  // Set category from active conversation if present
  if (activeId.value) {
    const activeConv = sortedConversations.value.find(c => c.id === activeId.value)
    if (activeConv) {
      config.value.category = activeConv.category
    }
  }
})

// Listen to conversation load and sync category
watch(activeId, (newId) => {
  if (newId) {
    const activeConv = sortedConversations.value.find(c => c.id === newId)
    if (activeConv) {
      config.value.category = activeConv.category
    }
  }
})

const handleCreateSession = async () => {
  const newConv = await createConversation('New Security Session', null, config.value.category)
  navigateTo(`/chat/${newConv.id}`)
}

const navigateToSession = (id) => {
  navigateTo(`/chat/${id}`)
}

const handleDeleteSession = async (id) => {
  if (await showConfirm('Delete this conversation history thread?')) {
    await deleteConversation(id)
    if (activeId.value === id) {
      navigateTo('/chat')
    }
  }
}

const handleCategoryChange = () => {
  if (activeId.value) {
    updateSessionCategory(config.value.category)
  }
}

const updateSessionCategory = (newCat) => {
  config.value.category = newCat
  if (activeId.value) {
    updateConversationCategory(activeId.value, newCat)
  }
}

const getCatClass = (cat) => {
  if (cat === 'Red Team') return 'badge-danger'
  if (cat === 'Audit') return 'badge-info'
  return 'badge-success'
}

// Group conversations by date
const filteredGroups = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  const filtered = sortedConversations.value.filter(c => 
    c.title.toLowerCase().includes(query) ||
    c.category.toLowerCase().includes(query)
  )

  if (filtered.length === 0) return []

  const groups = {
    'Today': [],
    'Yesterday': [],
    'Last 7 Days': [],
    'Older': []
  }

  const now = new Date()
  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)

  filtered.forEach(c => {
    const date = new Date(c.createdAt)
    const diffTime = Math.abs(now - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    const isToday = date.toDateString() === now.toDateString()
    const isYesterday = date.toDateString() === yesterday.toDateString()

    if (isToday) {
      groups['Today'].push(c)
    } else if (isYesterday) {
      groups['Yesterday'].push(c)
    } else if (diffDays <= 7) {
      groups['Last 7 Days'].push(c)
    } else {
      groups['Older'].push(c)
    }
  })

  return Object.entries(groups)
    .map(([name, items]) => ({ name, items }))
    .filter(g => g.items.length > 0)
})
</script>

<style scoped>
.chat-layout-wrapper {
  display: grid;
  grid-template-columns: 260px 1fr 300px;
  height: calc(100vh - var(--topbar-height));
  margin: -24px; /* Compensate padding in content-container */
}

/* Sessions Sidebar */
.chat-sessions-sidebar {
  background-color: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-actions {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.plus-icon {
  font-size: 16px;
  font-weight: bold;
}

.w-full {
  width: 100%;
}

.search-box-wrapper {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.search-icon {
  width: 14px;
  height: 14px;
  color: var(--text-muted);
}

.search-input {
  background: none;
  border: none;
  font-size: 13.5px;
  outline: none;
  width: 100%;
  color: var(--text-primary);
}

.sessions-list-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 16px 8px;
}

.list-empty {
  padding: 32px 16px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}

.history-group {
  margin-bottom: 20px;
}

.history-group-header {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 8px;
  padding-left: 8px;
}

.history-group-list {
  list-style: none;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  margin-bottom: 4px;
  transition: background-color 0.15s ease;
}

.history-item:hover {
  background-color: var(--bg-secondary);
}

.history-item.active {
  background-color: var(--bg-secondary);
  border-left: 3px solid var(--text-primary);
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.history-item-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-item-title {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-badge {
  font-size: 9px;
  font-weight: bold;
  padding: 1px 6px;
  border-radius: 50px;
  width: fit-content;
}

.history-item-controls {
  display: flex;
  align-items: center;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s;
}

.history-item:hover .history-item-controls {
  opacity: 1;
}

.pinned-indicator {
  width: 14px;
  height: 14px;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn .delete-icon {
  width: 14px;
  height: 14px;
  color: var(--text-muted);
  transition: color 0.2s;
}

.delete-btn:hover {
  opacity: 1;
}

.delete-btn:hover .delete-icon {
  color: #ef4444;
}

/* Chat Main Feed */
.chat-main-feed {
  flex: 1;
  min-width: 0;
  height: 100%;
}

/* Right Config Drawer */
.config-drawer {
  background-color: var(--bg-primary);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 300px;
  transition: width 0.2s ease;
}

.config-drawer.collapsed {
  width: 0;
  overflow: hidden;
  border-left: none;
}

.drawer-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.drawer-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: bold;
  letter-spacing: 0.05em;
}

.drawer-content {
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.raw-toggle-card {
  padding: 16px;
  border-color: var(--border-color);
  background-color: var(--bg-secondary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.raw-label-text {
  font-size: 13.5px;
  font-weight: bold;
  color: var(--text-primary);
}

.toggles-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: opacity 0.2s;
}

.toggles-list.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.policy-toggle-item {
  padding: 14px;
}

.toggle-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.policy-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary);
}

.policy-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
}

/* Switch styling */
.switch-toggle {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
}

.switch-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--border-hover);
  transition: .2s;
  border-radius: 20px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .2s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--text-primary);
}

input:checked + .slider:before {
  transform: translateX(16px);
}

.border-top {
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}

.margin-top-sm {
  margin-top: 8px;
}
</style>
