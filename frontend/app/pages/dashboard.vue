<template>
  <div class="dashboard-page grid-mesh framer-appear">
    <!-- Header banner -->
    <div class="card header-banner margin-bottom-md glassmorphism">
      <div class="banner-content">
        <h2 class="gradient-text">Gateway Analytics Operations Center</h2>
        <p>Monitor real-time threat deflections, selective compute pipeline latencies, and node statuses across your workspace.</p>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="loading-state card framer-appear">
      <div class="spinner"></div>
      <span>Retrieving platform metrics...</span>
    </div>

    <!-- Error state -->
    <div v-else-if="errorMsg" class="error-state card framer-appear">
      <h3>Failed to load telemetry data</h3>
      <p>{{ errorMsg }}</p>
      <button class="btn btn-primary" @click="loadData">Retry Load</button>
    </div>

    <!-- Content -->
    <div v-else class="dashboard-content">
      <!-- Top Stats Grid -->
      <div class="stats-grid">
        <div class="card stat-card hover-lift framer-appear delay-1">
          <span class="stat-label">Queries Monitored</span>
          <div class="stat-value">{{ totalRequests }}</div>
          <span class="stat-change text-success">✔ Active defense online</span>
        </div>

        <div class="card stat-card hover-lift framer-appear delay-2">
          <span class="stat-label">Deflected Attacks</span>
          <div class="stat-value text-danger">{{ blockedRequests }}</div>
          <span class="stat-change text-secondary">{{ blockRate.toFixed(1) }}% intercept rate</span>
        </div>

        <div class="card stat-card hover-lift framer-appear delay-3">
          <span class="stat-label">Avg Pipeline RTT</span>
          <div class="stat-value">{{ avgLatency.toFixed(0) }}<span class="unit">ms</span></div>
          <span class="stat-change text-muted">Selective compute active</span>
        </div>

        <div class="card stat-card hover-lift framer-appear delay-4">
          <span class="stat-label">Avg Reasoning (RIS)</span>
          <div class="stat-value text-success">{{ avgRis.toFixed(2) }}</div>
          <span class="stat-change text-muted">Factual alignment score</span>
        </div>
      </div>

      <!-- Main Visualizations Grid -->
      <div class="analytics-row" v-reveal>
        <!-- Live Threat Map (Left side) -->
        <LiveThreatMap />

        <!-- Router & Node Health (Right side) -->
        <div class="right-column-panel">
          <!-- EASE Routing Card -->
          <div class="card ease-card hover-lift margin-bottom-md" v-reveal="100">
            <div class="card-header">
              <div>
                <h3 class="card-title">EASE Reasoning Router</h3>
                <p class="card-subtitle">Selective compute decisions</p>
              </div>
            </div>
            <div class="ease-list">
              <div class="ease-item">
                <div class="ease-indicator direct"></div>
                <div class="ease-info">
                  <span class="ease-name">Direct Route</span>
                  <span class="ease-desc">Fast standard execution</span>
                </div>
                <span class="ease-count">{{ directRouteCount }}</span>
              </div>
              <div class="ease-item">
                <div class="ease-indicator cot"></div>
                <div class="ease-info">
                  <span class="ease-name">Chain-of-Thought</span>
                  <span class="ease-desc">Deep reasoning route</span>
                </div>
                <span class="ease-count">{{ cotRouteCount }}</span>
              </div>
              <div class="ease-item">
                <div class="ease-indicator blocked"></div>
                <div class="ease-info">
                  <span class="ease-name">Blocked</span>
                  <span class="ease-desc">Intercepted threat route</span>
                </div>
                <span class="ease-count">{{ blockedRequests }}</span>
              </div>
            </div>
          </div>

          <!-- Active Gateway Health Nodes -->
          <div class="card node-health-card hover-lift" v-reveal="200">
            <div class="card-header">
              <div>
                <h3 class="card-title">Active Gateway Nodes</h3>
                <p class="card-subtitle">Active connection status endpoints</p>
              </div>
            </div>
            <div class="node-list">
              <div class="node-item">
                <span class="status-dot"></span>
                <span class="node-name font-semibold text-secondary">Ravel Security Gateway</span>
                <span class="node-val badge badge-success">Online</span>
              </div>
              <div class="node-item">
                <span :class="['status-dot', { 'error': !ollamaOnline }]"></span>
                <span class="node-name font-semibold text-secondary">Local Model (Ollama)</span>
                <span :class="['node-val badge', ollamaOnline ? 'badge-success' : 'badge-danger']">
                  {{ ollamaOnline ? 'Connected' : 'Offline' }}
                </span>
              </div>
              <div class="node-item">
                <span class="status-dot"></span>
                <span class="node-name font-semibold text-secondary">Provider API Proxy</span>
                <span class="node-val badge badge-info">Idle</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Latency & Forensics Charts -->
      <div class="chart-section margin-bottom-md" v-reveal>
        <div class="card chart-card hover-lift">
          <div class="card-header">
            <div>
              <h3 class="card-title">Security & Latency Profiles</h3>
              <p class="card-subtitle">Transaction durations (ms) for the last 15 gateway queries</p>
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="chartCanvas" width="800" height="200" class="canvas-chart"></canvas>
          </div>
        </div>
      </div>

      <!-- Tables Row -->
      <div class="tables-row">
        <!-- Recent Threats -->
        <div class="card table-card hover-lift">
          <div class="card-header">
            <div>
              <h3 class="card-title">Recent Deflected Threats</h3>
              <p class="card-subtitle">Security intercepts in this workspace</p>
            </div>
            <NuxtLink to="/security" class="btn btn-secondary btn-sm">View Logs</NuxtLink>
          </div>
          <div class="table-wrapper">
            <div v-if="recentThreats.length === 0" class="table-empty">
              <p>No security threats intercepted yet.</p>
            </div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Payload</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in recentThreats" :key="t.timestamp">
                  <td class="mono text-muted">{{ formatTime(t.timestamp) }}</td>
                  <td class="text-truncate-cell" :title="t.prompt">{{ t.prompt }}</td>
                  <td><span class="badge badge-danger">Blocked</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Recent Requests -->
        <div class="card table-card hover-lift">
          <div class="card-header">
            <div>
              <h3 class="card-title">Monitor History</h3>
              <p class="card-subtitle">Recent pipeline transactions</p>
            </div>
            <NuxtLink to="/security" class="btn btn-secondary btn-sm">Inspect Traces</NuxtLink>
          </div>
          <div class="table-wrapper">
            <div v-if="recentRequests.length === 0" class="table-empty">
              <p>No queries processed yet. Use the Security Chat.</p>
            </div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Prompt</th>
                  <th>Latency</th>
                  <th>RIS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in recentRequests" :key="r.timestamp">
                  <td class="mono text-muted">{{ formatTime(r.timestamp) }}</td>
                  <td class="text-truncate-cell" :title="r.prompt">{{ r.prompt }}</td>
                  <td class="mono">{{ r.metrics.blocked ? '--' : `${r.metrics.total_latency_ms.toFixed(0)} ms` }}</td>
                  <td class="mono font-semibold">{{ r.metrics.blocked ? '--' : r.metrics.ris_score.toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

const { authHeaders } = useAuth()
const config = useRuntimeConfig()

const isLoading = ref(true)
const errorMsg = ref('')
const chartCanvas = ref(null)
const ollamaOnline = ref(false)

const history = ref([])
const telemetry = ref({})

// Calculated computed metrics
const totalRequests = computed(() => history.value.length)
const blockedRequests = computed(() => history.value.filter(r => r.metrics.blocked).length)
const blockRate = computed(() => totalRequests.value > 0 ? (blockedRequests.value / totalRequests.value) * 100 : 0)

const activeRequests = computed(() => history.value.filter(r => !r.metrics.blocked))
const avgLatency = computed(() => activeRequests.value.length > 0
  ? activeRequests.value.reduce((sum, r) => sum + r.metrics.total_latency_ms, 0) / activeRequests.value.length
  : 0
)

const avgRis = computed(() => activeRequests.value.length > 0
  ? activeRequests.value.reduce((sum, r) => sum + r.metrics.ris_score, 0) / activeRequests.value.length
  : 0
)

const directRouteCount = computed(() => history.value.filter(r => !r.metrics.blocked && !r.metrics.applied_cot).length)
const cotRouteCount = computed(() => history.value.filter(r => !r.metrics.blocked && r.metrics.applied_cot).length)

const recentThreats = computed(() => history.value
  .filter(r => r.metrics.blocked)
  .slice(-5)
  .reverse()
)

const recentRequests = computed(() => history.value
  .slice(-5)
  .reverse()
)

const loadData = async () => {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const [telemetryRes, historyRes, healthRes] = await Promise.all([
      $fetch(`${config.public.apiBase}/api/telemetry`, { headers: authHeaders() }).catch(() => ({})),
      $fetch(`${config.public.apiBase}/api/requests/history`, { headers: authHeaders() }).catch(() => []),
      $fetch(`${config.public.apiBase}/api/health`, { headers: authHeaders() }).catch(() => ({ ollama_connected: false }))
    ])
    
    ollamaOnline.value = healthRes.ollama_connected || false
    telemetry.value = telemetryRes
    history.value = historyRes || []

    nextTick(() => {
      drawChart()
    })
  } catch (err) {
    console.error('Failed to load metrics:', err)
    errorMsg.value = err.message || 'Connection failed'
  } finally {
    isLoading.value = false
  }
}

const formatTime = (ts) => {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const drawChart = () => {
  const canvas = chartCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const padLeft = 50
  const padRight = 20
  const padTop = 20
  const padBottom = 30

  const w = canvas.width - padLeft - padRight
  const h = canvas.height - padTop - padBottom

  const plotItems = history.value.slice(-15)
  if (plotItems.length === 0) {
    ctx.fillStyle = '#94A3B8'
    ctx.font = '13px monospace'
    ctx.textAlign = 'center'
    ctx.fillText('Awaiting live telemetry streams...', canvas.width / 2, canvas.height / 2)
    return
  }

  const maxVal = Math.max(100, ...plotItems.map(item => item.metrics.total_latency_ms))
  const stepX = plotItems.length > 1 ? w / (plotItems.length - 1) : w

  // Draw grid
  ctx.strokeStyle = '#F1F5F9'
  ctx.lineWidth = 1
  ctx.fillStyle = '#94A3B8'
  ctx.font = '10px JetBrains Mono, monospace'
  ctx.textAlign = 'right'

  const yLines = 4
  for (let i = 0; i <= yLines; i++) {
    const val = (maxVal / yLines) * i
    const y = padTop + h - (h / yLines) * i
    
    ctx.beginPath()
    ctx.moveTo(padLeft, y)
    ctx.lineTo(padLeft + w, y)
    ctx.stroke()

    ctx.fillText(`${val.toFixed(0)}ms`, padLeft - 8, y + 3)
  }

  // Plot Line
  ctx.strokeStyle = '#2563EB'
  ctx.lineWidth = 3
  ctx.lineJoin = 'round'
  ctx.lineCap = 'round'
  
  const gradient = ctx.createLinearGradient(0, padTop, 0, padTop + h)
  gradient.addColorStop(0, 'rgba(37, 99, 235, 0.1)')
  gradient.addColorStop(1, 'rgba(37, 99, 235, 0.0)')

  ctx.beginPath()
  plotItems.forEach((item, index) => {
    const x = padLeft + index * stepX
    const y = padTop + h - (item.metrics.total_latency_ms / maxVal) * h
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()

  if (plotItems.length > 1) {
    ctx.lineTo(padLeft + (plotItems.length - 1) * stepX, padTop + h)
    ctx.lineTo(padLeft, padTop + h)
    ctx.closePath()
    ctx.fillStyle = gradient
    ctx.fill()
  }

  // Draw Points
  plotItems.forEach((item, index) => {
    const x = padLeft + index * stepX
    const y = padTop + h - (item.metrics.total_latency_ms / maxVal) * h
    
    ctx.beginPath()
    ctx.arc(x, y, 4.5, 0, 2 * Math.PI)
    ctx.fillStyle = item.metrics.blocked ? '#EF4444' : '#2563EB'
    ctx.fill()
    ctx.strokeStyle = '#FFFFFF'
    ctx.lineWidth = 1.5
    ctx.stroke()
  })

  // Labels
  ctx.fillStyle = '#94A3B8'
  ctx.textAlign = 'center'
  plotItems.forEach((item, index) => {
    if (index % 3 === 0 || index === plotItems.length - 1) {
      const x = padLeft + index * stepX
      ctx.fillText(formatTime(item.timestamp), x, padTop + h + 18)
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
}

.header-banner {
  padding: 24px 32px;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  min-height: 280px;
  text-align: center;
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

.unit {
  font-size: 16px;
  color: var(--text-muted);
  margin-left: 2px;
}

.analytics-row {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
  margin-bottom: 24px;
}

.right-column-panel {
  display: flex;
  flex-direction: column;
}

.chart-card {
  min-width: 0;
}

.chart-container {
  margin-top: 16px;
  width: 100%;
}

.canvas-chart {
  width: 100% !important;
  height: auto !important;
}

.card-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.ease-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.ease-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.ease-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.ease-indicator.direct { background-color: var(--success); }
.ease-indicator.cot { background-color: var(--warning); }
.ease-indicator.blocked { background-color: var(--danger); }

.ease-info {
  flex: 1;
}

.ease-name {
  display: block;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary);
}

.ease-desc {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
}

.ease-count {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: bold;
}

/* Node Health panel */
.node-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.node-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.node-name {
  flex: 1;
  font-size: 13px;
}

.node-val {
  font-size: 10px;
  padding: 2px 6px;
}

.tables-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.table-card {
  padding: 20px 24px;
}

.table-wrapper {
  margin-top: 16px;
}

.text-truncate-cell {
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.table-empty {
  padding: 48px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13.5px;
}

@media (max-width: 992px) {
  .analytics-row, .tables-row {
    grid-template-columns: 1fr;
  }
}
</style>
