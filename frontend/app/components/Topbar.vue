<template>
  <header class="topbar">
    <div class="topbar-left">
      <h1 class="topbar-title-text">{{ pageTitle }}</h1>
    </div>
    <div class="topbar-right">
      <!-- Model Picker -->
      <div class="model-picker">
        <svg class="svg-icon model-picker-icon" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="15" x2="23" y2="15"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="15" x2="4" y2="15"></line></svg>
        <select :value="settings.selectedModel" @change="handleModelChange" class="select-dropdown">
          <option value="gemma3:1b">gemma3:1b (1.2B SLM)</option>
          <option value="llama3.2:1b">llama3.2:1b (1.2B SLM)</option>
          <option value="qwen2.5:1.5b">qwen2.5:1.5b (1.5B SLM)</option>
          <option value="gemma3:3b">gemma3:3b (Fast 3B)</option>
        </select>
      </div>

      <!-- Latency Indicator -->
      <div class="latency-indicator" title="Last measured roundtrip network latency to LLM">
        <span class="latency-label">RTT:</span>
        <span class="latency-val">{{ lastRtt ? `${lastRtt.toFixed(0)} ms` : '-- ms' }}</span>
      </div>

 
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const { settings, updateSettings } = useStore()
const lastRtt = useState('last_rtt', () => null)
const route = useRoute()

const routeTitles = {
  'index': 'Zero-Trust Ravel Gateway',
  'dashboard': 'Platform Security Dashboard',
  'templates': 'Agent Persona Templates',
  'chat': 'Real-Time Security Workspace',
  'chat-id': 'Real-Time Security Workspace',
  'memory': 'Persistent Agent Memory',
  'security': 'Security Hub & Telemetry Log',
  'settings': 'Platform & Model Settings',
  'docs': 'Developer Documentation',
  'admin': 'System-wide Admin Console'
}

const pageTitle = computed(() => {
  // Map page route name to page title
  const name = route.name
  return routeTitles[name] || 'Ravel Security Workspace'
})

const handleModelChange = (e) => {
  updateSettings({ selectedModel: e.target.value })
}
</script>

<style scoped>
.topbar-title-text {
  font-size: 20px;
  color: var(--text-primary);
  font-weight: 600;
  font-family: 'Outfit', sans-serif;
}

.model-picker {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
}

.model-picker-icon {
  font-size: 16px;
}

.select-dropdown {
  background: none;
  border: none;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-secondary);
  outline: none;
  cursor: pointer;
  padding-right: 4px;
}

.latency-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13.5px;
  color: var(--text-secondary);
}

.latency-label {
  color: var(--text-muted);
  font-weight: 500;
}

.latency-val {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
}

.topbar-btn {
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  transition: background-color 0.2s;
  color: var(--text-secondary);
}

.topbar-btn:hover {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.bell-icon {
  font-size: 16px;
}

.btn-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background-color: var(--danger);
  border-radius: 50%;
  border: 2px solid var(--bg-primary);
}
</style>
