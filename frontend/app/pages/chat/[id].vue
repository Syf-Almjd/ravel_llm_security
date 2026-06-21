<template>
  <div class="chat-session-container grid-mesh">
    <!-- Chat Header -->
    <header class="chat-session-header glassmorphism">
      <div class="header-info">
        <h3 class="session-title">{{ activeConv?.title || 'Loading Session...' }}</h3>
        <div class="session-meta">
          <span :class="['category-badge-indicator', getCatClass(activeConv?.category)]">
            {{ activeConv?.category || 'General' }}
          </span>
          <span class="status-dot glow-active"></span>
          <span class="status-lbl">Gateway Shield Active</span>
        </div>
      </div>

      <div class="header-actions">
        <!-- Pin Button -->
        <button class="action-icon-btn hover-lift" @click="handlePin" :title="activeConv?.pinned ? 'Unpin Session' : 'Pin Session'">
          <svg class="svg-icon" viewBox="0 0 24 24" :style="{ opacity: activeConv?.pinned ? 1 : 0.4 }"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
        </button>

        <!-- Export JSON Logs -->
        <button class="action-icon-btn hover-lift" @click="handleExport" title="Export Session (JSON)">
          <svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        </button>

        <!-- Toggle Config Drawer -->
        <button class="btn btn-secondary btn-sm hover-lift" @click="toggleDrawer">
          <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> Pipeline Config
        </button>
      </div>
    </header>

    <!-- Messages List Feed with Vue TransitionGroup -->
    <div class="messages-feed-scroll" ref="scrollRef">
      <div class="messages-list">
        <TransitionGroup name="list-fade">
          <div v-for="msg in messages" :key="msg.id" :class="['message-row', msg.sender === 'user' ? 'user' : 'assistant']">
            <div :class="['message-bubble hover-lift', { 'blocked-response threat-pulse': msg.metrics?.blocked }]">
              <!-- Text content rendered as Markdown -->
              <div class="message-text" v-html="parseMarkdown(msg.text)"></div>
              <div class="message-meta-time">
                <span>{{ formatMsgTime(msg.timestamp) }}</span>
              </div>

              <!-- Security Diagnostic Card (Replaces native details accordion) -->
              <div v-if="msg.sender === 'assistant' && msg.metrics" class="security-card card">
                <div class="security-card-header" @click="toggleDiag(msg.id)">
                  <div class="summary-left">
                    <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                    <span class="font-semibold text-secondary">Ravel Diagnostics</span>
                  </div>
                  <div class="summary-right">
                    <span :class="['badge', getScoreBadgeClass(msg.metrics)]">
                      {{ getScoreLabel(msg.metrics) }}
                    </span>
                    <span class="chevron" :class="{ rotated: openDiagIds[msg.id] }">▼</span>
                  </div>
                </div>

                <div v-if="openDiagIds[msg.id]" class="security-details-body framer-appear">
                  <div class="diag-grid">
                    <div class="diag-col">
                      <div class="diag-detail-item">
                        <span class="diag-detail-label">E2E Latency:</span>
                        <span class="diag-detail-val mono">{{ formatLatency(msg.metrics.total_latency_ms) }}</span>
                      </div>
                      <div class="diag-detail-item">
                        <span class="diag-detail-label">Time To First Token:</span>
                        <span class="diag-detail-val mono">{{ formatLatency(msg.metrics.ttft_ms) }}</span>
                      </div>
                      <div class="diag-detail-item">
                        <span class="diag-detail-label">Factual Score (RIS):</span>
                        <span class="diag-detail-val mono text-success font-semibold">{{ msg.metrics.ris_score.toFixed(2) }}</span>
                      </div>
                    </div>
                    <div class="diag-col border-left">
                      <div v-if="!msg.metrics.blocked">
                        <div class="diag-detail-item">
                          <span class="diag-detail-label">GUARD-SLM Speed:</span>
                          <span class="diag-detail-val mono">{{ formatLatency(msg.metrics.guard_slm_ms) }}</span>
                        </div>
                        <div class="diag-detail-item">
                          <span class="diag-detail-label">Router (EASE):</span>
                          <span class="diag-detail-val mono">{{ formatLatency(msg.metrics.ease_ms) }}</span>
                        </div>
                        <div class="diag-detail-item">
                          <span class="diag-detail-label">DRAG Retrieve (RAG):</span>
                          <span class="diag-detail-val mono">{{ formatLatency(msg.metrics.drag_ms) }}</span>
                        </div>
                      </div>
                      <div v-else>
                        <div class="diag-detail-item">
                          <span class="diag-detail-label text-danger font-semibold">Incident:</span>
                          <span class="diag-detail-val text-danger font-semibold">Prompt Override</span>
                        </div>
                        <div class="diag-detail-item">
                          <span class="diag-detail-label">Deflection Time:</span>
                          <span class="diag-detail-val mono">{{ formatLatency(msg.metrics.guard_slm_ms) }}</span>
                        </div>
                        <div class="diag-detail-item">
                          <span class="diag-detail-label">Severity:</span>
                          <span class="diag-detail-val text-danger font-semibold">CRITICAL</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- DoLa contrased tokens viz -->
                  <div v-if="msg.token_stats && msg.token_stats.length > 0" class="dola-tokens-section">
                    <span class="diag-detail-label block font-semibold text-muted text-small margin-bottom-sm">DOLA CONTRASTED DECODER VALUES</span>
                    <div class="dola-token-bubbles">
                      <span v-for="(t, tIdx) in msg.token_stats" :key="tIdx" 
                            :class="['dola-token', { adjusted: t.adjusted_by_dola }]"
                            :title="t.adjusted_by_dola ? 'Adjusted by DoLa contrasting layers' : 'Factual token'">
                        <span class="tok-txt font-semibold">{{ t.token }}</span>
                        <span class="dola-prob mono">{{ t.contrasted_prob.toFixed(2) }}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </TransitionGroup>

        <!-- Generating spinner state -->
        <div v-if="isGenerating" class="message-row assistant">
          <div class="message-bubble loading-bubble hover-lift">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span class="loading-sub-text font-semibold">Ravel processing selective compute trace...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Box Form Area -->
    <div class="chat-input-wrapper-box glassmorphism">
      <form @submit.prevent="handleFormSubmit" class="chat-form">
        <div class="textarea-container">
          <textarea
            v-model="promptInput"
            @keydown.enter.prevent="handleEnterKey"
            placeholder="Type a prompt to analyze... (Shift+Enter for newline)"
            rows="1"
            ref="inputRef"
            required
            :disabled="isGenerating"
          ></textarea>
          <button type="submit" class="btn btn-primary send-btn glow-active" :disabled="!promptInput.trim() || isGenerating">
            <svg fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"></path>
            </svg>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'

const route = useRoute()
const config = useRuntimeConfig()
const { authHeaders } = useAuth()
const { sortedConversations, togglePinConversation } = useStore()

const activeId = computed(() => route.params.id)
const activeConv = computed(() => sortedConversations.value.find(c => c.id === activeId.value))

const messages = ref([])
const promptInput = ref('')
const isGenerating = ref(false)
const scrollRef = ref(null)
const inputRef = ref(null)
const openDiagIds = ref({})

const sharedConfig = useState('chat_config')
const isDrawerCollapsed = useState('chat_drawer_collapsed')
const lastRtt = useState('last_rtt')

// Toggle custom Diagnostics view
const toggleDiag = (id) => {
  openDiagIds.value[id] = !openDiagIds.value[id]
}

// Fetch messages on mount or id change
const fetchSessionMessages = async () => {
  if (!activeId.value) return
  try {
    const data = await $fetch(`${config.public.apiBase}/api/conversations/${activeId.value}/messages`, {
      headers: authHeaders()
    })
    messages.value = data
    scrollToBottom()
  } catch (err) {
    console.error('Failed to fetch messages:', err)
  }
}

onMounted(async () => {
  await fetchSessionMessages()
  
  if (inputRef.value) {
    inputRef.value.focus()
  }

  if (route.query.init_prompt) {
    const initPrompt = decodeURIComponent(route.query.init_prompt)
    navigateTo(`/chat/${activeId.value}`, { replace: true })
    promptInput.value = initPrompt
    await handleFormSubmit()
  }
})

watch(activeId, async () => {
  await fetchSessionMessages()
  openDiagIds.value = {}
  if (inputRef.value) {
    inputRef.value.focus()
  }
})

const handlePin = async () => {
  if (activeId.value) {
    await togglePinConversation(activeId.value)
  }
}

const handleExport = () => {
  if (!activeConv.value) return
  const payload = {
    ...activeConv.value,
    messages: messages.value
  }
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(payload, null, 2))
  const downloadAnchor = document.createElement('a')
  downloadAnchor.setAttribute("href", dataStr)
  downloadAnchor.setAttribute("download", `ravel_session_${activeId.value}.json`)
  document.body.appendChild(downloadAnchor)
  downloadAnchor.click()
  downloadAnchor.remove()
}

const toggleDrawer = () => {
  isDrawerCollapsed.value = !isDrawerCollapsed.value
}

const handleEnterKey = (e) => {
  if (e.shiftKey) {
    promptInput.value += '\n'
  } else {
    handleFormSubmit()
  }
}

const handleFormSubmit = async () => {
  const text = promptInput.value.trim()
  if (!text || isGenerating.value) return

  const userMsgId = 'msg_user_' + Math.random().toString(36).substring(2, 9)
  messages.value.push({
    id: userMsgId,
    sender: 'user',
    text: text,
    timestamp: new Date().toISOString()
  })

  promptInput.value = ''
  isGenerating.value = true
  scrollToBottom()

  try {
    const settings = localStorage.getItem('ravel_settings')
    const parsedSettings = settings ? JSON.parse(settings) : {}
    const modelName = parsedSettings.selectedModel || 'gemma3:1b'
    const endpoint = parsedSettings.ollamaEndpoint || 'http://localhost:11434'

    const postBody = {
      prompt: text,
      conversation_id: activeId.value,
      template_id: activeConv.value?.template_id || null,
      enable_guard: sharedConfig.value.raw_mode ? false : sharedConfig.value.enable_guard,
      enable_ease: sharedConfig.value.raw_mode ? false : sharedConfig.value.enable_ease,
      enable_drag: sharedConfig.value.raw_mode ? false : sharedConfig.value.enable_drag,
      enable_dola: sharedConfig.value.raw_mode ? false : sharedConfig.value.enable_dola,
      ollama_endpoint: endpoint,
      model_name: modelName
    }

    const response = await $fetch(`${config.public.apiBase}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders()
      },
      body: postBody
    })

    lastRtt.value = response.metrics.total_latency_ms

    const aid = 'msg_assistant_' + Math.random().toString(36).substring(2, 9)
    messages.value.push({
      id: aid,
      sender: 'assistant',
      text: response.response,
      metrics: response.metrics,
      token_stats: response.token_stats,
      timestamp: new Date().toISOString()
    })

    // Auto open diagnostic panel for new incoming messages to make it look active!
    openDiagIds.value[aid] = true

    const parentConv = sortedConversations.value.find(c => c.id === activeId.value)
    if (parentConv) {
      parentConv.updatedAt = new Date().toISOString()
      if (parentConv.title === 'New Security Session' || parentConv.title === 'New Session') {
        parentConv.title = text.substring(0, 30) + (text.length > 30 ? '...' : '')
      }
    }

  } catch (err) {
    console.error('Failed to post query:', err)
    messages.value.push({
      id: 'msg_error_' + Math.random().toString(36).substring(2, 9),
      sender: 'assistant',
      text: `Gateway Interception Error: ${err.message || 'Check connection to backend server.'}`,
      metrics: { blocked: true, total_latency_ms: 0, ttft_ms: 0, ris_score: 0, guard_slm_ms: 0 },
      timestamp: new Date().toISOString()
    })
  } finally {
    isGenerating.value = false
    scrollToBottom()
  }
}

const parseMarkdown = (text) => {
  return marked.parse(text)
}

const formatMsgTime = (ts) => {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatLatency = (ms) => {
  if (ms === undefined || ms === null) return '--'
  return `${ms.toFixed(1)} ms`
}

const getScoreLabel = (metrics) => {
  if (metrics.blocked) return 'Blocked'
  return metrics.applied_cot ? 'Deep CoT' : 'Standard'
}

const getScoreBadgeClass = (metrics) => {
  if (metrics.blocked) return 'badge-danger'
  return metrics.applied_cot ? 'badge-warning' : 'badge-success'
}

const getCatClass = (cat) => {
  if (cat === 'Red Team') return 'badge-danger'
  if (cat === 'Audit') return 'badge-info'
  return 'badge-success'
}

const scrollToBottom = () => {
  nextTick(() => {
    if (scrollRef.value) {
      scrollRef.value.scrollTop = scrollRef.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.chat-session-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--bg-secondary);
}

.chat-session-header {
  height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.session-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.session-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11.5px;
  color: var(--text-secondary);
}

.category-badge-indicator {
  font-size: 9px;
  font-weight: bold;
  padding: 1px 6px;
  border-radius: 50px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--success);
}

.status-lbl {
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-icon-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  opacity: 0.7;
  padding: 6px;
  border-radius: var(--radius-sm);
}

.action-icon-btn:hover {
  background-color: var(--bg-secondary);
  opacity: 1;
}

/* Messages feed area */
.messages-feed-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.message-row {
  display: flex;
  width: 100%;
}

.message-row.user {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 85%;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 16px 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-row.user .message-bubble {
  background-color: var(--text-primary);
  color: var(--bg-primary);
  border-color: var(--text-primary);
}

.blocked-response {
  border-color: var(--danger-border) !important;
  background-color: var(--danger-bg) !important;
  color: var(--danger) !important;
}

.message-text {
  font-size: 14.5px;
  line-height: 1.5;
}

.message-text :deep(p) {
  margin-bottom: 8px;
}

.message-text :deep(p:last-child) {
  margin-bottom: 0;
}

.message-text :deep(pre) {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 12px;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin: 8px 0;
}

.message-row.user .message-text :deep(pre) {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.1);
}

.message-text :deep(code) {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}

.message-meta-time {
  font-size: 11px;
  color: var(--text-muted);
  text-align: right;
}

.message-row.user .message-meta-time {
  color: rgba(255, 255, 255, 0.6);
}

/* Security Diagnostics Card */
.security-card {
  padding: 0;
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-top: 12px;
  border-color: var(--border-color);
}

.security-card-header {
  padding: 10px 14px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-secondary);
}

.summary-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-shield-icon {
  font-size: 14px;
}

.summary-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chevron {
  font-size: 10px;
  color: var(--text-muted);
  transition: transform 0.2s;
}

.chevron.rotated {
  transform: rotate(180deg);
}

.security-details-body {
  padding: 14px;
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-primary);
}

.diag-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.diag-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.diag-col.border-left {
  border-left: 1px solid var(--border-color);
  padding-left: 16px;
}

.diag-detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.diag-detail-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.diag-detail-val {
  color: var(--text-primary);
  font-weight: 600;
}

.dola-tokens-section {
  margin-top: 16px;
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
}

.dola-token-bubbles {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.dola-token {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 3px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.dola-token:hover {
  border-color: var(--text-muted);
  background-color: var(--bg-hover);
}

.dola-token.adjusted {
  background-color: var(--brand-subtle);
  border-color: var(--brand-border);
  color: var(--brand-primary);
}

.dola-prob {
  font-size: 9px;
  color: var(--text-muted);
}

/* Loading bubble */
.loading-bubble {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: var(--text-muted);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}

.loading-sub-text {
  font-size: 11.5px;
  color: var(--text-muted);
}

/* Form Submit Area */
.chat-input-wrapper-box {
  padding: 16px 24px;
  background-color: var(--bg-primary);
  border-top: 1px solid var(--border-color);
}

.chat-form {
  max-width: 800px;
  margin: 0 auto;
}

.textarea-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 8px 12px;
  background-color: var(--bg-input);
}

.textarea-container:focus-within {
  border-color: var(--text-primary);
}

.textarea-container textarea {
  flex: 1;
  background: none;
  border: none;
  font-size: 14px;
  outline: none;
  resize: none;
  max-height: 120px;
  padding: 4px 0;
  color: var(--text-primary);
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.send-btn svg {
  width: 18px;
  height: 18px;
}

/* Vue list-fade Transition */
.list-fade-enter-active,
.list-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.list-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.list-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>
