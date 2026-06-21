<template>
  <div class="settings-page grid-mesh framer-appear">
    <!-- Header banner -->
    <div class="card header-banner margin-bottom-md glassmorphism">
      <div class="banner-content">
        <h2 class="gradient-text">Workspace Settings Center</h2>
        <p>Configure model server endpoints, manage API keys, invite security teammates, and hot-reload active security policy engines.</p>
      </div>
    </div>

    <!-- Tabs header -->
    <div class="tabs-header" v-reveal="60">
      <button :class="['tab-btn', { active: activeTab === 'system' }]" @click="activeTab = 'system'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg> System & Models
      </button>
      <button :class="['tab-btn', { active: activeTab === 'keys' }]" @click="activeTab = 'keys'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path></svg> API Keys
      </button>
      <button :class="['tab-btn', { active: activeTab === 'team' }]" @click="activeTab = 'team'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg> Team Members
      </button>
      <button :class="['tab-btn', { active: activeTab === 'policies' }]" @click="activeTab = 'policies'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Pipeline Policies
      </button>
    </div>

    <!-- 1. SYSTEM & MODEL CONFIGURATION -->
    <div v-if="activeTab === 'system'" class="tab-content framer-appear" v-reveal="120">
      <div class="grid-two-cols">
        <!-- Ollama Connection settings -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Local LLM Gateway (Ollama)</h3>
          </div>
          <form @submit.prevent="saveSystemSettings" class="margin-top-sm">
            <div class="form-group">
              <label class="form-label" for="ollamaHost">Ollama Server Endpoint</label>
              <input v-model="systemForm.ollamaEndpoint" type="text" id="ollamaHost" class="form-control" required />
            </div>

            <div class="form-group">
              <label class="form-label" for="ollamaModel">Default Local Model</label>
              <input v-model="systemForm.selectedModel" type="text" id="ollamaModel" class="form-control" required />
            </div>

            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="testOllamaConnection" :disabled="isTestingOllama">
                {{ isTestingOllama ? 'Testing...' : 'Test Connection' }}
              </button>
              <button type="submit" class="btn btn-primary">Save Settings</button>
            </div>
            <div v-if="ollamaStatusMsg" :class="['status-alert margin-top-sm', ollamaStatusSuccess ? 'text-success' : 'text-danger']">
              {{ ollamaStatusMsg }}
            </div>
          </form>
        </div>

        <!-- External Provider Keys -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">API Provider Keys</h3>
          </div>
          <p class="section-desc margin-bottom-sm">Configure API credentials to deploy gateway skins for external hosted providers.</p>
          <form @submit.prevent="saveProviderKeys">
            <div class="form-group">
              <label class="form-label" for="openaiKey">OpenAI Secret Key</label>
              <input v-model="providerKeys.openai" type="password" id="openaiKey" class="form-control" placeholder="sk-proj-••••••••••••" />
            </div>

            <div class="form-group">
              <label class="form-label" for="anthropicKey">Anthropic API Key</label>
              <input v-model="providerKeys.anthropic" type="password" id="anthropicKey" class="form-control" placeholder="sk-ant-••••••••••••" />
            </div>

            <div class="form-group">
              <label class="form-label" for="geminiKey">Gemini API Key</label>
              <input v-model="providerKeys.gemini" type="password" id="geminiKey" class="form-control" placeholder="AIzaSy••••••••••••" />
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary">Save Provider Keys</button>
            </div>
            <div v-if="providerKeysSaved" class="status-alert text-success margin-top-sm">
              ✔ API keys saved to workspace storage.
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 2. API KEYS -->
    <div v-if="activeTab === 'keys'" class="tab-content card framer-appear">
      <div class="card-header">
        <div>
          <h3 class="card-title">Workspace API Credentials</h3>
          <p class="card-subtitle">Generate API keys to secure background agent tasks and scripts via the Ravel gateway</p>
        </div>
      </div>

      <form @submit.prevent="handleCreateKey" class="invite-form margin-top-sm">
        <div class="form-group flex-2">
          <label class="form-label" for="keyName">API Key Label</label>
          <input v-model="newKeyName" type="text" id="keyName" class="form-control" placeholder="e.g. Production Workflow Shield" required />
        </div>
        <button type="submit" class="btn btn-primary align-self-end">Generate Token</button>
      </form>

      <!-- Newly created key display banner -->
      <div v-if="newlyCreatedKey" class="alert alert-warning margin-top-sm">
        <strong>Copy your new secret key now!</strong> It won't be shown again for security:
        <div class="copy-key-box margin-top-sm">
          <code class="mono">{{ newlyCreatedKey.key }}</code>
          <button class="btn btn-secondary btn-sm" @click="copyToClipboard(newlyCreatedKey.key)">Copy</button>
        </div>
      </div>

      <div class="table-container margin-top-md">
        <div v-if="apiKeys.length === 0" class="table-empty">
          <p>No API credentials generated yet.</p>
        </div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>Label Name</th>
              <th>Secret Prefix</th>
              <th>Created At</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="key in apiKeys" :key="key.id">
              <td class="font-semibold">{{ key.name }}</td>
              <td class="mono">{{ key.key.substring(0, 10) }}••••••••</td>
              <td class="text-muted text-small">{{ formatDate(key.createdAt) }}</td>
              <td class="text-right">
                <button class="btn btn-danger btn-sm" @click="handleRevokeKey(key.id)">Revoke</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 3. TEAM MEMBERS -->
    <div v-if="activeTab === 'team'" class="tab-content card framer-appear">
      <div class="card-header">
        <div>
          <h3 class="card-title">Workspace Team Members</h3>
          <p class="card-subtitle">Invite analysts or administrators to inspect security audit dashboards</p>
        </div>
      </div>

      <form @submit.prevent="handleInviteMember" class="invite-form margin-top-sm">
        <div class="form-group flex-2">
          <label class="form-label" for="inviteEmail">E-mail Address</label>
          <input v-model="inviteForm.email" type="email" id="inviteEmail" class="form-control" placeholder="teammate@company.com" required />
        </div>
        <div class="form-group flex-1">
          <label class="form-label" for="inviteRole">Role Privilege</label>
          <select v-model="inviteForm.role" id="inviteRole" class="form-control select-dropdown">
            <option value="Administrator">Administrator (Read & Write)</option>
            <option value="Analyst (Viewer)">Security Analyst (Read Only)</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary align-self-end">Send Invite</button>
      </form>

      <div class="table-container margin-top-md">
        <table class="table">
          <thead>
            <tr>
              <th>Teammate Account</th>
              <th>Role Privilege</th>
              <th>Status</th>
              <th class="text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in teamMembers" :key="m.id">
              <td class="font-semibold">{{ m.email }}</td>
              <td class="mono font-semibold text-muted">{{ m.role }}</td>
              <td><span :class="['badge', m.status === 'ACTIVE' ? 'badge-success' : 'badge-warning']">{{ m.status }}</span></td>
              <td class="text-right">
                <button v-if="m.role !== 'Owner'" class="btn btn-danger btn-sm" @click="handleRemoveMember(m.id)">Remove</button>
                <span v-else class="text-muted text-small font-semibold">Protected</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 4. SYSTEM POLICIES (YAML EDITOR) -->
    <div v-if="activeTab === 'policies'" class="tab-content card framer-appear">
      <div class="card-header">
        <div>
          <h3 class="card-title">Active Security Policies (YAML)</h3>
          <p class="card-subtitle">Hot-reload active keyword lists, reasoning pathways, and injection scoring thresholds</p>
        </div>
        <button class="btn btn-primary" @click="savePolicy" :disabled="isSavingPolicy">
          {{ isSavingPolicy ? 'Reloading...' : 'Apply & Hot-Reload Policy' }}
        </button>
      </div>

      <div v-if="policySaveMsg" :class="['alert margin-top-sm', policySaveSuccess ? 'alert-success' : 'alert-danger']">
        {{ policySaveMsg }}
      </div>

      <div class="editor-wrapper margin-top-sm">
        <textarea v-model="policyYaml" class="form-control yaml-textarea mono" rows="18" placeholder="# Load active configuration policy..."></textarea>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const config = useRuntimeConfig()
const { authHeaders } = useAuth()
const { settings, updateSettings, apiKeys, fetchApiKeys, createApiKey, revokeApiKey, showAlert, showConfirm } = useStore()

const activeTab = ref('system')

// 1. System Config States
const systemForm = reactive({
  ollamaEndpoint: '',
  selectedModel: ''
})
const providerKeys = reactive({
  openai: '',
  anthropic: '',
  gemini: ''
})
const isTestingOllama = ref(false)
const ollamaStatusMsg = ref('')
const ollamaStatusSuccess = ref(false)
const providerKeysSaved = ref(false)

// 2. API Keys States
const newKeyName = ref('')
const newlyCreatedKey = ref(null)

// 3. Team States
const teamMembers = useState('workspace_team', () => [
  { id: '1', email: 'saif@ravel.ai', role: 'Owner', status: 'ACTIVE' },
  { id: '2', email: 'secops@ravel.ai', role: 'Administrator', status: 'ACTIVE' },
  { id: '3', email: 'analyst@ravel.ai', role: 'Analyst (Viewer)', status: 'ACTIVE' }
])
const inviteForm = reactive({
  email: '',
  role: 'Analyst (Viewer)'
})

// 4. Policy States
const policyYaml = ref('')
const isSavingPolicy = ref(false)
const policySaveMsg = ref('')
const policySaveSuccess = ref(false)

onMounted(async () => {
  // Sync system settings
  systemForm.ollamaEndpoint = settings.value.ollamaEndpoint
  systemForm.selectedModel = settings.value.selectedModel
  
  // Load local API keys
  await fetchApiKeys()

  // Load external keys if they exist in localstorage
  if (import.meta.client) {
    providerKeys.openai = localStorage.getItem('ravel_key_openai') || ''
    providerKeys.anthropic = localStorage.getItem('ravel_key_anthropic') || ''
    providerKeys.gemini = localStorage.getItem('ravel_key_gemini') || ''
  }

  // Load Policy
  await loadPolicy()
})

const saveSystemSettings = async () => {
  updateSettings({
    ollamaEndpoint: systemForm.ollamaEndpoint,
    selectedModel: systemForm.selectedModel
  })
  await showAlert('System configurations updated successfully!', 'Success')
}

const testOllamaConnection = async () => {
  isTestingOllama.value = true
  ollamaStatusMsg.value = ''
  try {
    const data = await $fetch(`${config.public.apiBase}/api/health?ollama_endpoint=${encodeURIComponent(systemForm.ollamaEndpoint)}`, {
      headers: authHeaders()
    })
    ollamaStatusSuccess.value = data.ollama_status === 'connected'
    ollamaStatusMsg.value = data.ollama_status === 'connected'
      ? `✔ Connected successfully to Ollama. Selected model size: ${data.model_loaded || 'unknown'}`
      : `⚠️ Connection failed: ${data.details || 'Ollama offline'}`
  } catch (err) {
    ollamaStatusSuccess.value = false
    ollamaStatusMsg.value = `⚠️ Connection check failed: ${err.message}`
  } finally {
    isTestingOllama.value = false
  }
}

const saveProviderKeys = () => {
  if (import.meta.client) {
    localStorage.setItem('ravel_key_openai', providerKeys.openai)
    localStorage.setItem('ravel_key_anthropic', providerKeys.anthropic)
    localStorage.setItem('ravel_key_gemini', providerKeys.gemini)
  }
  providerKeysSaved.value = true
  setTimeout(() => {
    providerKeysSaved.value = false
  }, 3000)
}

const handleCreateKey = () => {
  newlyCreatedKey.value = createApiKey(newKeyName.value)
  newKeyName.value = ''
}

const handleRevokeKey = async (id) => {
  if (await showConfirm('Revoke this API Key? Scripts using this token will fail immediately.')) {
    revokeApiKey(id)
  }
}

const copyToClipboard = async (text) => {
  navigator.clipboard.writeText(text)
  await showAlert('API Key copied to clipboard!', 'Clipboard')
}

const handleInviteMember = async () => {
  if (teamMembers.value.some(m => m.email.toLowerCase() === inviteForm.email.toLowerCase())) {
    await showAlert('This user is already a member of this workspace.', 'Invite Error')
    return
  }
  
  teamMembers.value.push({
    id: 'user_' + Math.random().toString(36).substring(2, 9),
    email: inviteForm.email,
    role: inviteForm.role,
    status: 'PENDING'
  })
  
  inviteForm.email = ''
  await showAlert('Teammate invitation link sent!', 'Invite Success')
}

const handleRemoveMember = async (id) => {
  const member = teamMembers.value.find(m => m.id === id)
  if (member && await showConfirm(`Revoke console access privileges for ${member.email}?`)) {
    teamMembers.value = teamMembers.value.filter(m => m.id !== id)
  }
}

const loadPolicy = async () => {
  try {
    const res = await $fetch(`${config.public.apiBase}/api/policy`, {
      headers: authHeaders()
    })
    policyYaml.value = res.yaml
  } catch (err) {
    console.error('Failed to load active policies:', err)
  }
}

const savePolicy = async () => {
  isSavingPolicy.value = true
  policySaveMsg.value = ''
  try {
    const res = await $fetch(`${config.public.apiBase}/api/policy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders()
      },
      body: {
        yaml: policyYaml.value
      }
    })
    policySaveSuccess.value = true
    policySaveMsg.value = `✔ ${res.message || 'Policy reloaded successfully'}`
  } catch (err) {
    policySaveSuccess.value = false
    policySaveMsg.value = `❌ Hot-Reload failed: ${err.data?.error || err.message}`
  } finally {
    isSavingPolicy.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.grid-two-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.section-desc {
  font-size: 13.5px;
  color: var(--text-secondary);
}

.status-alert {
  font-size: 13.5px;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.invite-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 16px 20px;
  border-radius: var(--radius);
}

.flex-1 {
  flex: 1;
}

.flex-2 {
  flex: 2;
}

.align-self-end {
  align-self: flex-end;
  height: 38px;
}

.copy-key-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
}

.alert {
  padding: 16px;
  border-radius: var(--radius);
  font-size: 14px;
}

.alert-success {
  background-color: var(--success-bg);
  color: var(--success);
  border: 1px solid var(--success-border);
}

.alert-danger {
  background-color: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.yaml-textarea {
  width: 100%;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  padding: 16px;
  line-height: 1.5;
  background-color: #0F172A; /* Code style dark background for policy */
  color: #F8FAFC;
  border-color: #1E293B;
  border-radius: var(--radius);
}

.yaml-textarea:focus {
  border-color: var(--brand-primary);
}

@media (max-width: 992px) {
  .grid-two-cols {
    grid-template-columns: 1fr;
  }
}
</style>
