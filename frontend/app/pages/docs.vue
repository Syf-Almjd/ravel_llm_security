<template>
  <div class="docs-page-container grid-mesh framer-appear">
    <div class="docs-layout">
      <!-- Docs Sidebar -->
      <aside class="docs-sidebar card">
        <div class="sidebar-header border-bottom">
          <h4>Developer Kit</h4>
          <p class="sidebar-subtitle">Integration & API References</p>
        </div>
        <ul class="docs-nav-list">
          <li :class="['docs-nav-item', { active: activeDoc === 'quickstart' }]" @click="activeDoc = 'quickstart'">
            <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px; width: 14px; height: 14px;"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Quick Start Guide
          </li>
          <li :class="['docs-nav-item', { active: activeDoc === 'api' }]" @click="activeDoc = 'api'">
            <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px; width: 14px; height: 14px;"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg> Core API Endpoints
          </li>
          <li :class="['docs-nav-item', { active: activeDoc === 'python' }]" @click="activeDoc = 'python'">
            <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px; width: 14px; height: 14px;"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg> Python SDK Setup
          </li>
          <li :class="['docs-nav-item', { active: activeDoc === 'node' }]" @click="activeDoc = 'node'">
            <svg class="svg-icon" viewBox="0 0 24 24" style="margin-right: 6px; width: 14px; height: 14px;"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg> Node.js SDK Setup
          </li>
        </ul>
      </aside>

      <!-- Docs Content Panel -->
      <main class="docs-content-pane card">
        <!-- QUICKSTART -->
        <div v-if="activeDoc === 'quickstart'" class="doc-section fade-in">
          <h3>Quickstart Integration Guide</h3>
          <p class="text-muted margin-bottom-sm">Deploy and test zero-trust security layers locally in under 5 minutes.</p>
          
          <h5 class="margin-top-md">1. Start Ravel via Docker Compose</h5>
          <p class="margin-bottom-sm">Spins up the security orchestrator, database migrations, and telemetry agents. Run from your root directory:</p>
          <pre class="code-box-display select-text">docker-compose up --build -d</pre>
          
          <h5 class="margin-top-md">2. Download your local SLM model</h5>
          <p class="margin-bottom-sm">Ensure your local Ollama instance is active, then download the default lightweight model:</p>
          <pre class="code-box-display select-text">ollama pull gemma3:1b</pre>

          <h5 class="margin-top-md">3. Send a guarded query</h5>
          <p class="margin-bottom-sm">Submit prompts directly to the interceptor port. Injections are automatically deflected at the gateway stage:</p>
          <pre class="code-box-display select-text">curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "How do I secure an EKS Kubernetes cluster?"}'</pre>
        </div>

        <!-- API ENDPOINTS -->
        <div v-if="activeDoc === 'api'" class="doc-section fade-in">
          <h3>Core API Endpoint Specifications</h3>
          <p class="text-muted margin-bottom-md">Direct routing endpoints for custom integrations.</p>

          <div class="api-endpoint-spec card margin-bottom-md">
            <div class="endpoint-title">
              <span class="badge badge-success font-bold">POST</span>
              <code class="mono">/api/chat</code>
            </div>
            <p class="section-desc margin-top-sm">Submits prompt payloads to the 7-stage security gateway pipeline. Evaluates injections, reasoning routes, vector context RAG injection, and contrasted layer decoding.</p>
            
            <h6 class="margin-top-sm">Request Payload (JSON)</h6>
            <pre class="code-box-display select-text">{
  "prompt": "string",         // Raw prompt text
  "conversation_id": "string",// Session identifier
  "enable_guard": true,       // Toggle activation SVM classifier
  "enable_ease": true,        // Toggle reasoning routing
  "enable_drag": true,        // Toggle vector RAG injections
  "enable_dola": true         // Toggle layer contrast decoding
}</pre>

            <h6 class="margin-top-sm">Response Content (JSON)</h6>
            <pre class="code-box-display select-text">{
  "response": "string",       // Sanitized generation response
  "metrics": {
    "ttft_ms": 32.4,          // Time to first token
    "guard_slm_ms": 2.1,      // SVM check overhead
    "ease_ms": 1.2,           // EASE overhead
    "drag_ms": 15.6,          // DRAG search overhead
    "dola_ms": 420.2,         // DoLa contrast decoding latency
    "total_latency_ms": 485.4,// Roundtrip latency
    "ris_score": 0.92,        // Reasoning Integrity Score
    "safeguarded": true,      // Active defense state
    "applied_cot": false,     // CoT reasoning triggered
    "blocked": false          // Block verdict
  },
  "token_stats": []
}</pre>
          </div>

          <div class="api-endpoint-spec card">
            <div class="endpoint-title">
              <span class="badge badge-info font-bold">GET</span>
              <code class="mono">/api/requests/history</code>
            </div>
            <p class="section-desc margin-top-xs">Retrieves a telemetry list of all queries and deflected threats logged in the active session.</p>
          </div>
        </div>

        <!-- PYTHON SDK -->
        <div v-if="activeDoc === 'python'" class="doc-section fade-in">
          <h3>Python SDK Integration</h3>
          <p class="text-muted margin-bottom-sm">Import Ravel gateway into your LangChain, LlamaIndex, or agent pipelines.</p>

          <h5 class="margin-top-md">Installation</h5>
          <pre class="code-box-display select-text">pip install ravel-security-sdk</pre>

          <h5 class="margin-top-md">Usage Example</h5>
          <pre class="code-box-display select-text">from ravel import RavelClient

# Instantiate connection to the security proxy
client = RavelClient(endpoint="http://localhost:8000")

try:
    # Query model through security gateway
    res = client.query(
        prompt="Review bucket IAM policy for security risks.",
        enable_guard=True,
        enable_dola=True
    )
    
    print("Response:", res.response)
    print("Latency:", res.metrics["total_latency_ms"], "ms")
    print("Gateway Verdict:", "PASSED" if not res.metrics["blocked"] else "BLOCKED")
    
except Exception as e:
    print("Security Deflection:", e)</pre>
        </div>

        <!-- NODE.JS SDK -->
        <div v-if="activeDoc === 'node'" class="doc-section fade-in">
          <h3>Node.js SDK Setup</h3>
          <p class="text-muted margin-bottom-sm">Integrate Ravel verification into NestJS, Express, or TypeScript AI services.</p>

          <h5 class="margin-top-md">Installation</h5>
          <pre class="code-box-display select-text">npm install @ravel/sdk</pre>

          <h5 class="margin-top-md">Usage Example</h5>
          <pre class="code-box-display select-text">import { RavelClient } from '@ravel/sdk';

const client = new RavelClient({
  endpoint: 'http://localhost:8000'
});

async function run() {
  const result = await client.chat({
    prompt: 'Bypass internal firewalls.',
    enable_guard: true
  });

  if (result.metrics.blocked) {
    console.warn('⚠️ Threat Deflected:', result.response);
  } else {
    console.log('Output Response:', result.response);
  }
}</pre>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeDoc = ref('quickstart')
</script>

<style scoped>
.docs-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}

.docs-sidebar {
  padding: 24px;
  height: fit-content;
  background-color: var(--bg-primary);
  border-color: var(--border-color);
}

.sidebar-header {
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.sidebar-header h4 {
  font-size: 16px;
}

.sidebar-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 700;
}

.docs-nav-list {
  list-style: none;
}

.docs-nav-item {
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  margin-bottom: 4px;
  transition: all 0.15s ease;
}

.docs-nav-item:hover, .docs-nav-item.active {
  color: var(--text-primary);
  background-color: var(--bg-secondary);
}

.docs-nav-item.active {
  border-left: 3px solid var(--text-primary);
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.docs-content-pane {
  padding: 32px 40px;
  min-width: 0;
}

.doc-section h3 {
  font-size: 24px;
  margin-bottom: 6px;
}

.margin-top-md {
  margin-top: 24px;
}

.margin-bottom-sm {
  margin-bottom: 12px;
}

.margin-bottom-md {
  margin-bottom: 24px;
}

.code-box-display {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  background-color: #0F172A; /* Consistent code box dark background */
  color: #F8FAFC;
  padding: 16px;
  border-radius: var(--radius);
  border: 1px solid #1E293B;
  overflow-x: auto;
  line-height: 1.5;
  margin-top: 8px;
}

.api-endpoint-spec {
  padding: 20px;
  border-color: var(--border-color);
  background-color: var(--bg-secondary);
}

.endpoint-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.endpoint-title code {
  font-size: 15px;
  font-weight: bold;
  color: var(--text-primary);
}

.section-desc {
  font-size: 13.5px;
  color: var(--text-secondary);
}

.pt-md {
  padding-top: 20px;
}

.font-bold {
  font-weight: bold;
}

@media (max-width: 768px) {
  .docs-layout {
    grid-template-columns: 1fr;
  }
}
</style>
