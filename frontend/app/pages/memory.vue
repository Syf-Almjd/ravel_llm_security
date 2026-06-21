<template>
  <div class="memory-page-container grid-mesh framer-appear">
    <!-- Header banner -->
    <div class="card header-banner margin-bottom-md glassmorphism">
      <div class="banner-content">
        <h2 class="gradient-text">Agent Memory Bank</h2>
        <p>Manage persistent knowledge structures. View facts and preferences extracted from conversation threads, edit importance tags, or sync workspace backups.</p>
      </div>
      <div class="banner-actions">
        <!-- Import trigger -->
        <label class="btn btn-secondary cursor-pointer hover-lift" for="import-md-file">
          <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
          <span>Import MD</span>
          <input type="file" id="import-md-file" @change="handleImportMarkdown" accept=".md" class="hidden-input" />
        </label>
        <button class="btn btn-secondary hover-lift" @click="handleExportMarkdown">
          <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          <span>Export MD</span>
        </button>
      </div>
    </div>

    <!-- Filters Row -->
    <div class="filters-row card margin-bottom-md" v-reveal="60">
      <div class="filter-group">
        <label class="form-label">Persona Filter</label>
        <select v-model="selectedTemplate" @change="loadMemories" class="form-control select-dropdown">
          <option value="">All Personas</option>
          <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>
    </div>

    <!-- Category Tabs -->
    <div class="tabs-header" v-reveal="120">
      <button v-for="type in memoryTypes" :key="type"
              :class="['tab-btn', { active: activeType === type }]"
              @click="activeType = type">
        {{ type }}
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="loading-state framer-appear">
      <div class="spinner"></div>
      <span>Retrieving memory bank...</span>
    </div>

    <!-- Memory Table list -->
    <div v-else class="table-container card" v-reveal>
      <div v-if="filteredMemories.length === 0" class="table-empty">
        <p>No persistent memories found. Interact with agents in the Security Chat to extract memories automatically.</p>
      </div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Type</th>
            <th>Content</th>
            <th>Importance</th>
            <th>Created</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in filteredMemories" :key="m.id">
            <td>
              <span :class="['badge', getTypeBadgeClass(m.memory_type)]">{{ m.memory_type }}</span>
            </td>
            <td class="memory-content-cell">{{ m.content }}</td>
            <td class="mono font-semibold">{{ (m.importance * 100).toFixed(0) }}%</td>
            <td class="text-muted text-small">{{ formatDate(m.created_at) }}</td>
            <td class="text-right">
              <div class="action-buttons">
                <button class="btn btn-secondary btn-sm" @click="openEditModal(m)">Edit</button>
                <button class="btn btn-danger btn-sm" @click="handleDeleteMemory(m.id)">Delete</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Memory Modal Overlay -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-card card framer-appear">
        <div class="modal-header">
          <h3>Edit Memory Content</h3>
          <button class="close-btn" @click="showEditModal = false">×</button>
        </div>
        <form @submit.prevent="handleUpdateMemory" class="modal-form">
          <div class="form-group">
            <label class="form-label">Memory Type</label>
            <input type="text" class="form-control" :value="editForm.type" disabled />
          </div>

          <div class="form-group">
            <label class="form-label" for="editContent">Content Text</label>
            <textarea v-model="editForm.content" id="editContent" class="form-control" rows="4" required></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">Importance Level: {{ (editForm.importance * 100).toFixed(0) }}%</label>
            <input v-model.number="editForm.importance" type="range" min="0" max="1" step="0.05" class="slider-input" />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showEditModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : 'Save Memory' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'

const config = useRuntimeConfig()
const { authHeaders } = useAuth()
const { templates, fetchTemplates, showAlert, showConfirm } = useStore()

const memories = ref([])
const isLoading = ref(true)
const selectedTemplate = ref('')
const activeType = ref('All')
const showEditModal = ref(false)
const isSaving = ref(false)

const memoryTypes = ['All', 'fact', 'preference', 'instruction', 'correction', 'context']

const editForm = reactive({
  id: '',
  type: '',
  content: '',
  importance: 0.5
})

const filteredMemories = computed(() => {
  let list = memories.value
  if (activeType.value !== 'All') {
    list = list.filter(m => m.memory_type === activeType.value)
  }
  return list
})

const loadMemories = async () => {
  isLoading.value = true
  try {
    let url = `${config.public.apiBase}/api/memories`
    if (selectedTemplate.value) {
      url += `?template_id=${selectedTemplate.value}`
    }
    const data = await $fetch(url, { headers: authHeaders() })
    memories.value = data
  } catch (err) {
    console.error('Failed to load memories:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    fetchTemplates(),
    loadMemories()
  ])
})

const openEditModal = (m) => {
  editForm.id = m.id
  editForm.type = m.memory_type
  editForm.content = m.content
  editForm.importance = m.importance
  showEditModal.value = true
}

const handleUpdateMemory = async () => {
  isSaving.value = true
  try {
    await $fetch(`${config.public.apiBase}/api/memories/${editForm.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders()
      },
      body: {
        content: editForm.content,
        importance: editForm.importance
      }
    })
    await loadMemories()
    showEditModal.value = false
  } catch (err) {
    console.error('Failed to update memory:', err)
    await showAlert(err.data?.detail || 'Failed to update memory', 'Error')
  } finally {
    isSaving.value = false
  }
}

const handleDeleteMemory = async (id) => {
  if (await showConfirm('Delete this memory? OUTDATING or WRONG context facts will be cleaned.')) {
    try {
      await $fetch(`${config.public.apiBase}/api/memories/${id}`, {
        method: 'DELETE',
        headers: authHeaders()
      })
      await loadMemories()
    } catch (err) {
      console.error('Failed to delete memory:', err)
    }
  }
}

const handleExportMarkdown = () => {
  const token = localStorage.getItem('ravel_token')
  window.open(`${config.public.apiBase}/api/memories/export?token=${token}`, '_blank')
}

const handleImportMarkdown = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    isLoading.value = true
    const result = await $fetch(`${config.public.apiBase}/api/memories/import`, {
      method: 'POST',
      headers: {
        ...authHeaders()
      },
      body: formData
    })
    await showAlert(result.message || 'Imported successfully', 'Success')
    await loadMemories()
  } catch (err) {
    console.error('Failed to import memories:', err)
    await showAlert(err.data?.detail || 'Import failed', 'Error')
  } finally {
    isLoading.value = false
  }
}

const getTypeBadgeClass = (type) => {
  if (type === 'fact') return 'badge-info'
  if (type === 'preference') return 'badge-success'
  if (type === 'instruction') return 'badge-warning'
  if (type === 'correction') return 'badge-danger'
  return 'badge-secondary'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
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

.banner-actions {
  display: flex;
  gap: 12px;
}

.filters-row {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  background-color: var(--bg-primary);
  border-color: var(--border-color);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 220px;
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

.table-container {
  padding: 0;
  overflow: hidden;
}

.table-empty {
  padding: 64px;
  text-align: center;
  color: var(--text-muted);
}

.memory-content-cell {
  max-width: 420px;
  font-weight: 500;
  color: var(--text-primary);
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.text-right {
  text-align: right;
}

.hidden-input {
  display: none;
}

.cursor-pointer {
  cursor: pointer;
}

/* Modal Styling */
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
  max-width: 480px;
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

.slider-input {
  width: 100%;
  margin-top: 8px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
