<template>
  <div class="security-page grid-mesh framer-appear">
    <!-- Header banner -->
    <div class="card header-banner margin-bottom-md glassmorphism">
      <div class="banner-content">
        <h2 class="gradient-text">Security Hub Operations</h2>
        <p>Monitor real-time threat prevention logs, inspect granular pipeline latencies, and export compliance audit logs.</p>
      </div>
      <div class="banner-actions">
        <button class="btn btn-danger hover-lift" @click="handleResetMetrics">Reset Telemetry Metrics</button>
      </div>
    </div>

    <!-- Sub Tabs Navigation -->
    <div class="tabs-header">
      <button :class="['tab-btn', { active: activeTab === 'threats' }]" @click="activeTab = 'threats'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> Threat Log ({{ blockedHistory.length }})
      </button>
      <button :class="['tab-btn', { active: activeTab === 'requests' }]" @click="activeTab = 'requests'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg> Request Inspector ({{ history.length }})
      </button>
      <button :class="['tab-btn', { active: activeTab === 'reports' }]" @click="activeTab = 'reports'">
        <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Compliance Reports
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state framer-appear">
      <div class="spinner"></div>
      <span>Fetching security logs...</span>
    </div>

    <div v-else>
      <!-- 1. THREAT LOG TAB -->
      <div v-if="activeTab === 'threats'" class="tab-content card framer-appear">
        <div class="table-header">
          <h3>Deflected Prompt Injections & Attacks</h3>
          <input v-model="threatFilter" type="text" placeholder="Filter attacks..." class="form-control table-search-input" />
        </div>

        <div class="table-container margin-top-sm">
          <div v-if="filteredThreats.length === 0" class="table-empty">
            <p>No deflected threats match your search filters.</p>
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Target Prompt Payload</th>
                <th>Deflection Time</th>
                <th>Severity</th>
                <th>Verdict</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in filteredThreats" :key="t.timestamp">
                <td class="mono text-muted">{{ formatTime(t.timestamp) }}</td>
                <td class="prompt-text-column" :title="t.prompt">{{ t.prompt }}</td>
                <td class="mono">{{ t.metrics.guard_slm_ms.toFixed(1) }} ms</td>
                <td><span class="badge badge-danger">Critical</span></td>
                <td><span class="badge badge-danger">Blocked</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 2. REQUEST INSPECTOR TAB -->
      <div v-if="activeTab === 'requests'" class="tab-content card framer-appear">
        <div class="table-header">
          <h3>E2E Pipeline Telemetry Logs</h3>
          <input v-model="requestFilter" type="text" placeholder="Filter requests..." class="form-control table-search-input" />
        </div>

        <div class="table-container margin-top-sm">
          <div v-if="filteredRequests.length === 0" class="table-empty">
            <p>No request logs processed in this session.</p>
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Prompt Text</th>
                <th>EASE Route</th>
                <th>RTT Latency</th>
                <th>RIS Score</th>
                <th>Verdict</th>
                <th class="text-right">Inspection</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in filteredRequests" :key="r.timestamp">
                <td class="mono text-muted">{{ formatTime(r.timestamp) }}</td>
                <td class="prompt-text-column" :title="r.prompt">{{ r.prompt }}</td>
                <td>
                  <span :class="['badge', r.metrics.blocked ? 'badge-danger' : r.metrics.applied_cot ? 'badge-warning' : 'badge-success']">
                    {{ r.metrics.blocked ? 'Blocked' : r.metrics.applied_cot ? 'Chain-of-Thought' : 'Direct' }}
                  </span>
                </td>
                <td class="mono">{{ r.metrics.blocked ? '--' : `${r.metrics.total_latency_ms.toFixed(0)} ms` }}</td>
                <td class="mono font-semibold">{{ r.metrics.blocked ? '--' : r.metrics.ris_score.toFixed(2) }}</td>
                <td>
                  <span :class="['badge', r.metrics.blocked ? 'badge-danger' : 'badge-success']">
                    {{ r.metrics.blocked ? 'Deflected' : 'Passed' }}
                  </span>
                </td>
                <td class="text-right">
                  <button class="btn btn-secondary btn-sm" @click="inspectRequest(r)">Inspect Trace</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 3. COMPLIANCE REPORTS TAB -->
      <div v-if="activeTab === 'reports'" class="tab-content card framer-appear">
        <div class="reports-grid">
          <div class="report-settings-panel">
            <h3>Audit Report Generator</h3>
            <p class="section-desc margin-bottom-sm">Compile and download cryptographic records of deflective actions, user registrations, and vector retrievals.</p>
            
            <div class="form-group">
              <label class="form-label">Report Format</label>
              <select v-model="reportConfig.format" class="form-control">
                <option value="json">JSON Security Audit Trail</option>
                <option value="csv">CSV telemetry spreadsheet</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Log Scoping</label>
              <select v-model="reportConfig.scope" class="form-control">
                <option value="all">Include all logs (Requests + Threats)</option>
                <option value="threats">Threat logs only</option>
              </select>
            </div>

            <button class="btn btn-primary w-full" @click="generateReport">
              Download Compliance Report
            </button>
          </div>

          <div class="report-stats-panel border-left pl-md">
            <h3>Gateway Metrics Summary</h3>
            <div class="report-stats-list margin-top-sm">
              <div class="report-stat-item">
                <span class="lbl">Total Shielded Prompts:</span>
                <span class="val mono">{{ totalQueriesCount }}</span>
              </div>
              <div class="report-stat-item">
                <span class="lbl">Jailbreaks Deflected:</span>
                <span class="val mono text-danger">{{ blockedHistory.length }}</span>
              </div>
              <div class="report-stat-item">
                <span class="lbl">Avg Gateway Latency:</span>
                <span class="val mono">{{ avgLatency.toFixed(1) }} ms</span>
              </div>
              <div class="report-stat-item">
                <span class="lbl">Reasoning CoT Ratio:</span>
                <span class="val mono">{{ cotRatio.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Request Trace Inspection Modal -->
    <div v-if="inspectedRequestItem" class="modal-overlay">
      <div class="modal-card card framer-appear">
        <div class="modal-header">
          <h3>E2E Latency Trace Inspection</h3>
          <button class="close-btn" @click="inspectedRequestItem = null">×</button>
        </div>
        <div class="modal-body scroll-body">
          <div class="trace-section card margin-bottom-sm">
            <h5 class="mono text-muted">User Prompt Input</h5>
            <p class="trace-prompt-text">{{ inspectedRequestItem.prompt }}</p>
          </div>

          <h4 class="margin-bottom-sm">7-Stage Pipeline Execution Trace</h4>
          <div class="trace-pipeline-viz">
            <div class="trace-node">
              <span class="node-icon checked">✔</span>
              <span class="node-label">Unicode Sanitizer</span>
              <span class="node-time mono">&lt; 0.1ms</span>
            </div>
            <div class="trace-node">
              <span class="node-icon checked">✔</span>
              <span class="node-label">GUARD-SLM SVM Shield</span>
              <span class="node-time mono">{{ formatLatency(inspectedRequestItem.metrics.guard_slm_ms) }}</span>
            </div>
            <div class="trace-node">
              <span class="node-icon checked">✔</span>
              <span class="node-label">EASE Reasoning Router</span>
              <span class="node-time mono">{{ formatLatency(inspectedRequestItem.metrics.ease_ms) }}</span>
            </div>
            <div class="trace-node">
              <span class="node-icon checked">✔</span>
              <span class="node-label">DRAG Knowledge Retrieval</span>
              <span class="node-time mono">{{ formatLatency(inspectedRequestItem.metrics.drag_ms) }}</span>
            </div>
            <div class="trace-node">
              <span class="node-icon checked">✔</span>
              <span class="node-label">DoLa Generation Loop</span>
              <span class="node-time mono">{{ formatLatency(inspectedRequestItem.metrics.dola_ms) }}</span>
            </div>
            <div class="trace-node total">
              <span class="node-icon active">✔</span>
              <span class="node-label font-bold">Total Gateway RTT</span>
              <span class="node-time mono font-bold">{{ formatLatency(inspectedRequestItem.metrics.total_latency_ms) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'

const config = useRuntimeConfig()
const { authHeaders } = useAuth()
const { showConfirm } = useStore()

const isLoading = ref(true)
const activeTab = ref('threats')
const history = ref([])
const threatFilter = ref('')
const requestFilter = ref('')
const inspectedRequestItem = ref(null)

const reportConfig = reactive({
  format: 'json',
  scope: 'all'
})

const loadHistory = async () => {
  isLoading.value = true
  try {
    const data = await $fetch(`${config.public.apiBase}/api/requests/history`, {
      headers: authHeaders()
    })
    history.value = data
  } catch (err) {
    console.error('Failed to load telemetry history:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadHistory()
})

const blockedHistory = computed(() => {
  return history.value.filter(r => r.metrics.blocked)
})

const filteredThreats = computed(() => {
  const query = threatFilter.value.trim().toLowerCase()
  return blockedHistory.value.filter(t => 
    t.prompt.toLowerCase().includes(query)
  )
})

const filteredRequests = computed(() => {
  const query = requestFilter.value.trim().toLowerCase()
  return history.value.filter(r => 
    r.prompt.toLowerCase().includes(query)
  )
})

// Metrics summary calculations
const totalQueriesCount = computed(() => history.value.length)
const avgLatency = computed(() => {
  const active = history.value.filter(r => !r.metrics.blocked)
  return active.length > 0 ? active.reduce((sum, r) => sum + r.metrics.total_latency_ms, 0) / active.value || active.reduce((sum, r) => sum + r.metrics.total_latency_ms, 0) / active.length : 0
})
const cotRatio = computed(() => {
  const active = history.value.filter(r => !r.metrics.blocked)
  const cot = active.filter(r => r.metrics.applied_cot)
  return active.length > 0 ? (cot.length / active.length) * 100 : 0
})

const formatTime = (ts) => {
  return new Date(ts).toLocaleString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', month: 'short', day: 'numeric' })
}

const formatLatency = (ms) => {
  if (ms === undefined || ms === null) return '--'
  return `${ms.toFixed(1)} ms`
}

const inspectRequest = (item) => {
  inspectedRequestItem.value = item
}

const handleResetMetrics = async () => {
  if (await showConfirm('Clear and reset all telemetry data logs in this session? This action cannot be undone.')) {
    try {
      isLoading.value = true
      await $fetch(`${config.public.apiBase}/api/reset-metrics`, {
        method: 'POST',
        headers: authHeaders()
      })
      await loadHistory()
    } catch (err) {
      console.error('Failed to reset telemetry:', err)
    } finally {
      isLoading.value = false
    }
  }
}

const generateReport = () => {
  const format = reportConfig.format
  const scope = reportConfig.scope
  
  let dataToExport = history.value
  if (scope === 'threats') {
    dataToExport = blockedHistory.value
  }

  if (format === 'json') {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(dataToExport, null, 2))
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute("href", dataStr)
    downloadAnchor.setAttribute("download", `ravel_security_report_${Date.now()}.json`)
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  } else {
    // Generate CSV
    let csvContent = "data:text/csv;charset=utf-8,Timestamp,Prompt,Blocked,Latency,RIS\n"
    dataToExport.forEach(r => {
      const time = new Date(r.timestamp).toISOString()
      const promptEsc = `"${r.prompt.replace(/"/g, '""')}"`
      const blocked = r.metrics.blocked ? "TRUE" : "FALSE"
      const latency = r.metrics.blocked ? "" : r.metrics.total_latency_ms.toFixed(0)
      const ris = r.metrics.blocked ? "" : r.metrics.ris_score.toFixed(2)
      csvContent += `${time},${promptEsc},${blocked},${latency},${ris}\n`
    })
    const encodedUri = encodeURI(csvContent)
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute("href", encodedUri)
    downloadAnchor.setAttribute("download", `ravel_security_report_${Date.now()}.csv`)
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }
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

.prompt-text-column {
  max-width: 380px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
  color: var(--text-primary);
}

.table-empty {
  padding: 64px;
  text-align: center;
  color: var(--text-muted);
}

.text-right {
  text-align: right;
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

/* Compliance Reports styles */
.reports-grid {
  display: grid;
  grid-template-columns: 1fr 1.1fr;
  gap: 32px;
  padding: 12px;
}

.report-settings-panel h3, .report-stats-panel h3 {
  font-size: 16px;
  margin-bottom: 16px;
}

.section-desc {
  font-size: 13.5px;
  color: var(--text-secondary);
}

.border-left {
  border-left: 1px solid var(--border-color);
}

.pl-md {
  padding-left: 32px;
}

.report-stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.report-stat-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  padding: 10px 0;
  border-bottom: 1px dashed var(--border-color);
}

.report-stat-item .lbl {
  color: var(--text-secondary);
  font-weight: 500;
}

.report-stat-item .val {
  font-weight: 600;
  color: var(--text-primary);
}

/* Modal and trace */
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
  max-width: 520px;
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
  max-height: 420px;
  overflow-y: auto;
}

.trace-section {
  padding: 16px;
  border-color: var(--border-color);
  background-color: var(--bg-secondary);
}

.trace-prompt-text {
  font-size: 13.5px;
  color: var(--text-primary);
  margin-top: 6px;
  word-break: break-all;
}

.trace-pipeline-viz {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trace-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.trace-node.total {
  background-color: var(--brand-subtle);
  border-color: var(--brand-border);
}

.node-icon {
  margin-right: 8px;
}

.node-icon.checked {
  color: var(--success);
}

.node-icon.active {
  color: var(--brand-primary);
}

.node-label {
  flex: 1;
  color: var(--text-primary);
}

.node-time {
  color: var(--text-secondary);
}

.font-bold {
  font-weight: bold;
}
</style>
