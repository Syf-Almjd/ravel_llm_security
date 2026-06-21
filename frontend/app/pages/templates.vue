<template>
  <div class="templates-page-container grid-mesh framer-appear">
    <!-- Header banner -->
    <div class="card header-banner margin-bottom-md glassmorphism">
      <div class="banner-content">
        <h2 class="gradient-text">Agent Persona Templates Center</h2>
        <p>Manage role-based behavior specifications. Instantly connect active sessions to custom guidelines, and toggle custom sandbox safety overrides.</p>
      </div>
      <button class="btn btn-primary hover-lift" @click="showCreateModal = true">+ Create Custom Persona</button>
    </div>

    <!-- Category Filter Tabs -->
    <div class="tabs-header" v-reveal="60">
      <button v-for="cat in categories" :key="cat"
              :class="['tab-btn', { active: activeCategory === cat }]"
              @click="activeCategory = cat">
        {{ cat }}
      </button>
    </div>

    <!-- Loading templates state -->
    <div v-if="isLoading" class="loading-state framer-appear">
      <div class="spinner"></div>
      <span>Loading personas...</span>
    </div>

    <!-- Grid items list -->
    <div v-else class="templates-grid" v-reveal>
      <div v-for="tpl in filteredTemplates" :key="tpl.id" class="card template-card">
        <div class="card-header">
          <div class="template-icon" v-html="getIconSvg(tpl.icon)"></div>
          <span v-if="tpl.is_builtin" class="badge badge-info">Built-in</span>
          <span v-else class="badge badge-warning">Custom</span>
        </div>
        <h3 class="template-name">{{ tpl.name }}</h3>
        <span class="template-cat-label">{{ tpl.category }}</span>
        <p class="template-desc">{{ tpl.description }}</p>
        
        <div class="template-actions">
          <button class="btn btn-primary w-full" @click="startSession(tpl)">
            Deploy Persona
          </button>
        </div>
      </div>
    </div>

    <!-- Create Custom Template Modal Overlay -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal-card card framer-appear">
        <div class="modal-header">
          <h3>Create Custom Persona</h3>
          <button class="close-btn" @click="showCreateModal = false">×</button>
        </div>
        <form @submit.prevent="handleCreateTemplate" class="modal-form">
          <div class="form-row">
            <div class="form-group flex-2">
              <label class="form-label" for="tplName">Persona Name</label>
              <input v-model="createForm.name" type="text" id="tplName" class="form-control" placeholder="Security Auditor" required />
            </div>
            <div class="form-group flex-1">
              <label class="form-label" for="tplIcon">Icon Theme</label>
              <select v-model="createForm.icon" id="tplIcon" class="form-control">
                <option value="🛡️">Security Shield</option>
                <option value="🔓">Security Lock</option>
                <option value="⚙️">DevOps Gear</option>
                <option value="🗄️">Database Cylinder</option>
                <option value="💻">Terminal/Computer</option>
                <option value="🎨">Software Design</option>
                <option value="📊">Bar Chart</option>
                <option value="🤖">Default Robot</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="tplCategory">Category</label>
            <select v-model="createForm.category" id="tplCategory" class="form-control">
              <option value="Security">Security & DevOps</option>
              <option value="Engineering">Software Engineering</option>
              <option value="Data & AI">Data & AI</option>
              <option value="Business">Business & Strategy</option>
              <option value="Creative">Creative & Content</option>
              <option value="Support">Support & Operations</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label" for="tplDesc">Short Description</label>
            <input v-model="createForm.description" type="text" id="tplDesc" class="form-control" placeholder="Briefly describe what this agent does..." required />
          </div>

          <div class="form-group">
            <label class="form-label" for="tplSystem">System Behavior Guidelines</label>
            <textarea v-model="createForm.system_prompt" id="tplSystem" class="form-control" rows="5" placeholder="You are a senior security researcher. Always analyze logs for vulnerabilities..." required></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isCreating">
              {{ isCreating ? 'Registering...' : 'Create Persona' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'

const { templates, fetchTemplates, createConversation, showAlert } = useStore()
const config = useRuntimeConfig()
const { authHeaders } = useAuth()

const isLoading = ref(true)
const activeCategory = ref('All')
const showCreateModal = ref(false)
const isCreating = ref(false)

const categories = ['All', 'Security', 'Engineering', 'Data & AI', 'Business', 'Creative', 'Support']

const createForm = reactive({
  name: '',
  icon: '🤖',
  category: 'Security',
  description: '',
  system_prompt: '',
  suggested_prompts: []
})

const filteredTemplates = computed(() => {
  if (activeCategory.value === 'All') return templates.value
  return templates.value.filter(t => t.category === activeCategory.value)
})

onMounted(async () => {
  await fetchTemplates()
  isLoading.value = false
})

const startSession = async (tpl) => {
  const newConv = await createConversation(`${tpl.name} Session`, tpl.id, tpl.category)
  navigateTo(`/chat/${newConv.id}`)
}

const handleCreateTemplate = async () => {
  isCreating.value = true
  try {
    await $fetch(`${config.public.apiBase}/api/templates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders()
      },
      body: {
        name: createForm.name,
        icon: createForm.icon,
        category: createForm.category,
        description: createForm.description,
        system_prompt: createForm.system_prompt,
        suggested_prompts: createForm.suggested_prompts
      }
    })
    
    // Refresh list
    await fetchTemplates()
    showCreateModal.value = false
    
    // Reset form
    createForm.name = ''
    createForm.icon = '🤖'
    createForm.category = 'Security'
    createForm.description = ''
    createForm.system_prompt = ''
  } catch (err) {
    console.error('Failed to create persona:', err)
    await showAlert(err.data?.detail || 'Failed to create persona', 'Error')
  } finally {
    isCreating.value = false
  }
}

const getIconSvg = (iconName) => {
  const mapping = {
    '🛡️': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
    '🔓': `<svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 9.9-1"></path></svg>`,
    '⚙️': `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`,
    '☁️': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path></svg>`,
    '🌐': `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>`,
    '🚨': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
    '💻': `<svg class="svg-icon" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>`,
    '🔧': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`,
    '🎨': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 14.7255 3.09032 17.1962 4.85857 19C5.35339 19.5 5.25 20.5 4.5 21C3.5 21.5 2.5 20 2.5 20"></path><circle cx="7.5" cy="10.5" r="1.5"></circle><circle cx="11.5" cy="7.5" r="1.5"></circle><circle cx="16.5" cy="9.5" r="1.5"></circle><circle cx="15.5" cy="14.5" r="1.5"></circle></svg>`,
    '📱': `<svg class="svg-icon" viewBox="0 0 24 24"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>`,
    '🔍': `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
    '🗄️': `<svg class="svg-icon" viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path></svg>`,
    '📊': `<svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>`,
    '🤖': `<svg class="svg-icon" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="15" x2="23" y2="15"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="15" x2="4" y2="15"></line></svg>`,
    '📈': `<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>`,
    '💬': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`,
    '👁️': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`,
    '📋': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>`,
    '📣': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>`,
    '🤝': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
    '⚖️': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22V8M5 12H19M5 12A4 4 0 0 1 9 8M19 12A4 4 0 0 1 15 8"></path></svg>`,
    '✍️': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 20h9"></path><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"></path></svg>`,
    '📝': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,
    '🧪': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M10 2v7.31L3.89 19.9c-.19.33-.08.76.25.95.1.06.22.09.34.09h15.04c.39 0 .71-.32.71-.71 0-.12-.03-.24-.09-.34L14 9.31V2"></path><line x1="8" y1="2" x2="16" y2="2"></line><line x1="8.5" y1="11" x2="15.5" y2="11"></line></svg>`,
    '💁': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
    '🎯': `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>`,
    '📅': `<svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`,
    '📑': `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M4 22V4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v18Z"></path><path d="M8 6h8"></path><path d="M8 10h8"></path><path d="M8 14h8"></path></svg>`
  }
  return mapping[iconName] || mapping['🤖']
}
</script>

<style scoped>
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

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

.template-card {
  display: flex;
  flex-direction: column;
  padding: 24px;
}

.template-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--brand-primary);
}

.template-icon .svg-icon {
  width: 24px;
  height: 24px;
  stroke-width: 2.2;
}

.template-name {
  font-size: 17px;
  margin-top: 16px;
  color: var(--text-primary);
}

.template-cat-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.template-desc {
  font-size: 13.5px;
  color: var(--text-secondary);
  line-height: 1.5;
  flex: 1;
  margin-bottom: 24px;
}

.template-actions {
  margin-top: auto;
}

.w-full {
  width: 100%;
}

/* Modal Overlay */
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
  max-width: 560px;
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

.form-row {
  display: flex;
  gap: 16px;
}

.flex-1 {
  flex: 1;
}

.flex-2 {
  flex: 2;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
