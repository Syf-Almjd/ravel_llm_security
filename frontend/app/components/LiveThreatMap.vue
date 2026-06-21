<template>
  <div class="threat-map-card card hover-lift">
    <div class="card-header">
      <div>
        <h3 class="card-title">Live Gateway Security & Threat Map</h3>
        <p class="section-desc">Active Ravel threat intelligence nodes defending local model endpoints</p>
      </div>
      <div class="live-counter">
        <span class="pulse-beacon threat-pulse"></span>
        <span class="counter-text font-semibold text-danger">LIVE AUDIT FEED</span>
      </div>
    </div>

    <!-- Stylized SVG Constellation Map -->
    <div class="map-visualizer">
      <svg class="network-svg" viewBox="0 0 800 300" fill="none">
        <!-- Connecting lines -->
        <g stroke="#E2E8F0" stroke-width="1.5">
          <line x1="100" y1="180" x2="250" y2="120" class="network-line" />
          <line x1="250" y1="120" x2="400" y2="150" class="network-line" />
          <line x1="400" y1="150" x2="550" y2="100" class="network-line" />
          <line x1="550" y1="100" x2="700" y2="200" class="network-line" />
          <line x1="250" y1="120" x2="320" y2="220" class="network-line" />
          <line x1="400" y1="150" x2="480" y2="230" class="network-line" />
          <line x1="550" y1="100" x2="620" y2="210" class="network-line" />
        </g>

        <!-- Dynamic alert links (drawn on alert) -->
        <path
          v-if="activeAlert"
          :d="`M ${activeAlert.x} ${activeAlert.y} L 400 150`"
          stroke="var(--danger)"
          stroke-width="2"
          stroke-dasharray="8 4"
          class="alert-path"
        />

        <!-- Network nodes -->
        <g>
          <!-- Gateway Nodes -->
          <circle cx="100" cy="180" r="6" fill="var(--text-muted)" />
          <circle cx="250" cy="120" r="6" fill="var(--text-muted)" />
          <circle cx="320" cy="220" r="6" fill="var(--text-muted)" />
          <circle cx="480" cy="230" r="6" fill="var(--text-muted)" />
          <circle cx="550" cy="100" r="6" fill="var(--text-muted)" />
          <circle cx="620" cy="210" r="6" fill="var(--text-muted)" />
          <circle cx="700" cy="200" r="6" fill="var(--text-muted)" />

          <!-- Main Secure Hub -->
          <circle cx="400" cy="150" r="10" fill="var(--brand-primary)" class="glow-active" />
          <circle cx="400" cy="150" r="16" stroke="var(--brand-primary)" stroke-width="1.5" opacity="0.3" />
        </g>

        <!-- Pulsing alert node -->
        <g v-if="activeAlert">
          <circle :cx="activeAlert.x" :cy="activeAlert.y" r="14" fill="var(--danger)" opacity="0.2" class="alert-pulse" />
          <circle :cx="activeAlert.x" :cy="activeAlert.y" r="6" fill="var(--danger)" />
        </g>
      </svg>

      <!-- Threat Alert overlay toast -->
      <Transition name="fade-slide">
        <div v-if="activeAlert" class="alert-toast glassmorphism">
          <span class="badge badge-danger">DEFLECTED</span>
          <div class="toast-body">
            <span class="toast-title font-semibold">{{ activeAlert.type }} Deflected</span>
            <span class="toast-meta text-muted">Gateway Node {{ activeAlert.node }} • {{ activeAlert.latency }}ms</span>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Threat Logs List -->
    <div class="threat-log-container">
      <div class="log-header font-semibold text-muted text-small">RECENT INCIDENT LOGS</div>
      <div class="log-list">
        <div v-for="log in threatLogs" :key="log.id" class="log-item animate-fade-in">
          <span class="log-dot threat-pulse"></span>
          <span class="log-time mono text-muted">{{ log.time }}</span>
          <span class="log-desc text-secondary"><strong class="text-primary">{{ log.type }}</strong> injection blocked at <code class="mono">{{ log.ip }}</code></span>
          <span class="log-badge badge badge-success">{{ log.action }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const nodesList = [
  { name: 'US-East-1', x: 100, y: 180 },
  { name: 'EU-West-1', x: 250, y: 120 },
  { name: 'AP-South-1', x: 320, y: 220 },
  { name: 'SA-East-1', x: 480, y: 230 },
  { name: 'AP-Northeast-1', x: 550, y: 100 },
  { name: 'US-West-2', x: 620, y: 210 },
  { name: 'EU-Central-1', x: 700, y: 200 }
]

const threatTypes = ['SQL Injection', 'System Prompt Leakage', 'Prompt Injection', 'Reverse Engineering', 'Remote Shell Payload']
const ipRanges = ['192.168.32.12', '10.0.12.87', '172.16.4.150', '82.102.14.99', '198.51.100.4']

const threatLogs = ref([
  { id: 1, time: '13:28:45', type: 'Prompt Injection', ip: '192.168.32.12', action: 'BLOCKED' },
  { id: 2, time: '13:27:12', type: 'System Leakage', ip: '10.0.12.87', action: 'BLOCKED' },
  { id: 3, time: '13:25:01', type: 'SQL Injection', ip: '172.16.4.150', action: 'BLOCKED' }
])

const activeAlert = ref(null)
let simulationTimer = null

const runSimulation = () => {
  const node = nodesList[Math.floor(Math.random() * nodesList.length)]
  const type = threatTypes[Math.floor(Math.random() * threatTypes.length)]
  const ip = ipRanges[Math.floor(Math.random() * ipRanges.length)]
  const latency = (Math.random() * 3 + 1.2).toFixed(1)

  // Show SVG Alert
  activeAlert.value = {
    x: node.x,
    y: node.y,
    node: node.name,
    type,
    latency
  }

  // Append Log
  const now = new Date()
  const timeStr = now.toTimeString().split(' ')[0]
  threatLogs.value.unshift({
    id: Date.now(),
    time: timeStr,
    type,
    ip,
    action: 'BLOCKED'
  })

  if (threatLogs.value.length > 5) {
    threatLogs.value.pop()
  }

  // Clear Alert after 2.5s
  setTimeout(() => {
    activeAlert.value = null
  }, 2500)

  // Next simulation run
  simulationTimer = setTimeout(runSimulation, Math.random() * 4000 + 4000)
}

onMounted(() => {
  simulationTimer = setTimeout(runSimulation, 2000)
})

onUnmounted(() => {
  if (simulationTimer) clearTimeout(simulationTimer)
})
</script>

<style scoped>
.threat-map-card {
  display: flex;
  flex-direction: column;
  height: 480px;
}

.live-counter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pulse-beacon {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--danger);
  display: inline-block;
}

.counter-text {
  font-size: 11px;
  letter-spacing: 0.05em;
}

.map-visualizer {
  position: relative;
  flex: 1;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.network-svg {
  width: 100%;
  height: 100%;
  max-height: 240px;
}

.network-line {
  stroke-dasharray: 4 4;
  opacity: 0.6;
}

.alert-path {
  stroke-dasharray: 6 3;
  animation: dash 1s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -12;
  }
}

.alert-pulse {
  animation: threatAlert 1.2s infinite;
}

.alert-toast {
  position: absolute;
  bottom: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-md);
  z-index: 10;
}

.toast-body {
  display: flex;
  flex-direction: column;
}

.toast-title {
  font-size: 13px;
  color: var(--text-primary);
}

.toast-meta {
  font-size: 11px;
}

.threat-log-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-header {
  font-size: 11px;
  letter-spacing: 0.05em;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.log-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--danger);
}

.log-time {
  font-size: 12px;
}

.log-desc {
  flex: 1;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.log-badge {
  font-size: 10px;
  padding: 2px 6px;
}

/* Vue Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
