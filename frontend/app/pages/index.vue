<template>
  <div class="landing-page-wrapper grid-mesh framer-appear">
    <!-- Navigation -->
    <header class="nav-header glassmorphism">
      <div class="container nav-container">
        <div class="brand">
          <div class="brand-logo-circle glow-active">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span class="brand-name">Ravel</span>
        </div>
        <nav class="nav-links">
          <a href="#playground">Playground</a>
          <a href="#features">Features</a>
          <a href="#pipeline">Pipeline Shield</a>
          <a href="#templates">Personas</a>
        </nav>
        <div class="nav-actions">
          <NuxtLink to="/login" class="btn btn-secondary btn-sm">Sign In</NuxtLink>
          <NuxtLink to="/register" class="btn btn-primary btn-sm">Deploy Shield</NuxtLink>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
      <div class="container hero-grid">
        <div class="hero-content">
          <div class="badge badge-info margin-bottom-sm glow-active">v2.4 Core Active Shield</div>
          <h1 class="gradient-text">Zero-Trust Security Skins for AI Agents</h1>
          <p>Deploy secure runtime wrappers over local models and commercial APIs. Deflect prompt injections, sandbox tool calls, block memory poisoning, and view real-time latency diagnostics.</p>
          <div class="hero-actions">
            <NuxtLink to="/register" class="btn btn-primary btn-lg">Deploy Security Skin</NuxtLink>
            <a href="#playground" class="btn btn-secondary btn-lg">Try Interactive Sandbox</a>
          </div>
        </div>
        
        <div class="hero-visual animate-float">
          <TerminalMock />
        </div>
      </div>
    </section>

    <!-- Dynamic Sandbox Playground Section -->
    <section class="sandbox-section" id="playground">
      <div class="container">
        <div class="section-title-block">
          <span class="section-tag">Interactive Evaluation</span>
          <h2 class="section-title">Live Pipeline Sandbox Sandbox</h2>
          <p class="section-subtitle">Type standard prompts or jailbreak payloads to inspect the selective compute path and deflection latencies in real-time.</p>
        </div>
        <div class="sandbox-wrapper">
          <InteractiveSandbox />
        </div>
      </div>
    </section>

    <!-- Model Support Showcase -->
    <section class="providers-bar">
      <div class="container">
        <div class="providers-label">Native Model & API Gateway Integrations</div>
        <div class="providers-grid">
          <div class="provider-card card">
            <svg class="svg-icon" viewBox="0 0 24 24" style="width: 28px; height: 28px; color: var(--brand-primary);"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path></svg>
            <div class="provider-info">
              <div class="provider-title font-semibold">Ollama</div>
              <div class="provider-desc text-muted">Local host gateway</div>
            </div>
          </div>
          <div class="provider-card card">
            <svg class="svg-icon" viewBox="0 0 24 24" style="width: 28px; height: 28px; color: var(--brand-primary);"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="15" x2="23" y2="15"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="15" x2="4" y2="15"></line></svg>
            <div class="provider-info">
              <div class="provider-title font-semibold">OpenAI</div>
              <div class="provider-desc text-muted">GPT Models API</div>
            </div>
          </div>
          <div class="provider-card card">
            <svg class="svg-icon" viewBox="0 0 24 24" style="width: 28px; height: 28px; color: var(--brand-primary);"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            <div class="provider-info">
              <div class="provider-title font-semibold">Anthropic</div>
              <div class="provider-desc text-muted">Claude Models API</div>
            </div>
          </div>
          <div class="provider-card card">
            <svg class="svg-icon" viewBox="0 0 24 24" style="width: 28px; height: 28px; color: var(--brand-primary);"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
            <div class="provider-info">
              <div class="provider-title font-semibold">Gemini</div>
              <div class="provider-desc text-muted">Google AI API</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pipeline Visualizer -->
    <section class="pipeline-section" id="pipeline">
      <div class="container">
        <div class="section-title-block">
          <span class="section-tag">Zero Trust Processing</span>
          <h2 class="section-title">7-Stage Guardrail Pipeline</h2>
          <p class="section-subtitle">Every user prompt is validated, routed, augmented, and audited through our low-latency shield.</p>
        </div>

        <div class="pipeline-wrapper">
          <div class="pipe-node card hover-lift">
            <div class="pipe-details">
              <span class="pipe-indicator checked">✔</span>
              <span class="pipe-name">1. Unicode Sanitizer</span>
              <span class="pipe-info">Strips malicious character formatting & HTML injections</span>
            </div>
            <div class="pipe-time">&lt; 0.1ms</div>
          </div>
          <div class="pipe-arrow">↓</div>
          
          <div class="pipe-node card hover-lift">
            <div class="pipe-details">
              <span class="pipe-indicator checked">✔</span>
              <span class="pipe-name">2. GUARD-SLM Activation</span>
              <span class="pipe-info">Fast SVM classifier flags prompt injections & jailbreaks</span>
            </div>
            <div class="pipe-time">3.5ms</div>
          </div>
          <div class="pipe-arrow">↓</div>

          <div class="pipe-node card hover-lift">
            <div class="pipe-details">
              <span class="pipe-indicator checked">✔</span>
              <span class="pipe-name">3. EASE Intent Router</span>
              <span class="pipe-info">Routes complex tasks to Chain of Thought (CoT)</span>
            </div>
            <div class="pipe-time">0.8ms</div>
          </div>
          <div class="pipe-arrow">↓</div>

          <div class="pipe-node card hover-lift">
            <div class="pipe-details">
              <span class="pipe-indicator checked">✔</span>
              <span class="pipe-name">4. DRAG Knowledge Context</span>
              <span class="pipe-info">Injects vectorized reference context facts & memories</span>
            </div>
            <div class="pipe-time">1.2ms</div>
          </div>
          <div class="pipe-arrow">↓</div>

          <div class="pipe-node card hover-lift">
            <div class="pipe-details">
              <span class="pipe-indicator checked">✔</span>
              <span class="pipe-name">5. Contrasted Inference (DoLa)</span>
              <span class="pipe-info">Early vs late layer decoding suppresses hallucinations</span>
            </div>
            <div class="pipe-time">120ms</div>
          </div>
          <div class="pipe-arrow">↓</div>

          <div class="pipe-node card hover-lift">
            <div class="pipe-details">
              <span class="pipe-indicator checked">✔</span>
              <span class="pipe-name">6. RIS Integrity Audit</span>
              <span class="pipe-info">Validates alignment and filters leakage risks</span>
            </div>
            <div class="pipe-time">12ms</div>
          </div>
          <div class="pipe-arrow">↓</div>

          <div class="pipe-node card highlight glow-active">
            <div class="pipe-details">
              <span class="pipe-indicator active">✔</span>
              <span class="pipe-name">7. Secure Output Dispatch</span>
              <span class="pipe-info">Clean response forwarded to agent consumer</span>
            </div>
            <div class="pipe-time">Done</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Personas -->
    <section class="templates-showcase" id="templates">
      <div class="container">
        <div class="section-title-block">
          <span class="section-tag">Personas</span>
          <h2 class="section-title">Preloaded Agent Personas</h2>
          <p class="section-subtitle">Shape interactions instantly with secure, role-specific prompts and custom configurations.</p>
        </div>

        <div class="showcase-grid">
          <div class="showcase-card card hover-lift">
            <div class="showcase-header">
              <svg class="svg-icon" viewBox="0 0 24 24" style="width: 24px; height: 24px; color: var(--brand-primary);"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
              <h3 class="showcase-name">Security Analyst</h3>
            </div>
            <p class="showcase-desc">Specialized in threat modeling, vulnerability assessments, and secure logging code audits.</p>
          </div>
          <div class="showcase-card card hover-lift">
            <div class="showcase-header">
              <svg class="svg-icon" viewBox="0 0 24 24" style="width: 24px; height: 24px; color: var(--brand-primary);"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 9.9-1"></path></svg>
              <h3 class="showcase-name">Penetration Tester</h3>
            </div>
            <p class="showcase-desc">Ethical hacking simulation to identify weaknesses in software code configurations.</p>
          </div>
          <div class="showcase-card card hover-lift">
            <div class="showcase-header">
              <svg class="svg-icon" viewBox="0 0 24 24" style="width: 24px; height: 24px; color: var(--brand-primary);"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
              <h3 class="showcase-name">Fullstack Engineer</h3>
            </div>
            <p class="showcase-desc">Generates robust, secure frontend structures and backend API integrations on the fly.</p>
          </div>
          <div class="showcase-card card hover-lift">
            <div class="showcase-header">
              <svg class="svg-icon" viewBox="0 0 24 24" style="width: 24px; height: 24px; color: var(--brand-primary);"><path d="M12 22V8M5 12H19M5 12A4 4 0 0 1 9 8M19 12A4 4 0 0 1 15 8"></path></svg>
              <h3 class="showcase-name">Compliance Officer</h3>
            </div>
            <p class="showcase-desc">Audits code, dependencies, and architecture patterns against SOC2, NIST, and GDPR standards.</p>
          </div>
        </div>
        <div class="text-center margin-top-md">
          <NuxtLink to="/register" class="btn btn-secondary">Create Account to See All 30+ Personas</NuxtLink>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="container">
        <h2>Upgrade Your Agent Security Standard</h2>
        <p>Deploy Ravel on top of your local models. Stop jailbreaks, prevent memory poisoning, and audit LLM traffic in real-time.</p>
        <NuxtLink to="/register" class="btn btn-primary btn-lg glow-active">Get Started Free</NuxtLink>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="container footer-flex">
        <span class="footer-copyright">&copy; 2026 Ravel. Zero-Trust Security for AI Agents.</span>
        <div class="footer-links">
          <NuxtLink to="/docs">Documentation</NuxtLink>
          <NuxtLink to="/docs">API Reference</NuxtLink>
          <a href="https://github.com" target="_blank">GitHub</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
definePageMeta({
  layout: 'empty'
})
</script>

<style scoped>
.landing-page-wrapper {
  background-color: var(--bg-primary);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Header */
.nav-header {
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 72px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: var(--text-primary);
  color: var(--bg-primary);
  border-radius: var(--radius-sm);
}

.brand-logo-circle svg {
  width: 20px;
  height: 20px;
  stroke: var(--bg-primary);
}

.brand-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Outfit', sans-serif;
}

.nav-links {
  display: flex;
  gap: 32px;
  font-size: 14.5px;
  font-weight: 600;
  color: var(--text-secondary);
}

.nav-links a:hover {
  color: var(--brand-primary);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Hero Section */
.hero {
  padding: 96px 0 80px 0;
  border-bottom: 1px solid var(--border-color);
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 64px;
  align-items: center;
}

.hero-content h1 {
  font-size: 56px;
  line-height: 1.1;
  margin-bottom: 24px;
}

.hero-content p {
  font-size: 17px;
  color: var(--text-secondary);
  margin-bottom: 36px;
  max-width: 520px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.btn-lg {
  padding: 12px 28px;
  font-size: 15px;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13.5px;
}

/* Sandbox Playground Section */
.sandbox-section {
  padding: 80px 0;
  border-bottom: 1px solid var(--border-color);
}

.sandbox-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

/* Providers Showcase */
.providers-bar {
  padding: 64px 0;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
}

.providers-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 32px;
  font-weight: 700;
  text-align: center;
}

.providers-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.provider-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
}

.provider-icon {
  font-size: 28px;
}

.provider-title {
  font-size: 15px;
  color: var(--text-primary);
}

.provider-desc {
  font-size: 11px;
}

/* Pipeline Viz */
.pipeline-section {
  padding: 96px 0;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.pipeline-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  max-width: 680px;
  margin: 40px auto 0 auto;
}

.pipe-node {
  width: 100%;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-sm);
}

.pipe-node.highlight {
  border-color: var(--brand-border);
  background-color: var(--brand-subtle);
}

.pipe-details {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pipe-indicator {
  font-size: 14px;
  font-weight: bold;
}

.pipe-indicator.checked {
  color: var(--success);
}

.pipe-indicator.active {
  color: var(--brand-primary);
}

.pipe-name {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  font-size: 13.5px;
}

.pipe-info {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 12px;
}

.pipe-time {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: var(--text-secondary);
}

.pipe-arrow {
  color: var(--text-muted);
  font-size: 18px;
  font-weight: bold;
}

/* Templates Showcase */
.templates-showcase {
  padding: 96px 0;
  border-bottom: 1px solid var(--border-color);
}

.showcase-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.showcase-card {
  padding: 24px;
}

.showcase-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.showcase-icon {
  font-size: 24px;
}

.showcase-name {
  font-size: 16px;
  font-weight: 600;
}

.showcase-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* CTA */
.cta-section {
  padding: 120px 0;
  text-align: center;
}

.cta-section h2 {
  font-size: 44px;
  margin-bottom: 20px;
}

.cta-section p {
  font-size: 18px;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto 36px auto;
}

/* Footer */
.footer {
  padding: 48px 0;
  color: var(--text-muted);
  font-size: 13.5px;
}

.footer-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
}

.footer-links {
  display: flex;
  gap: 24px;
}

.footer-links a:hover {
  color: var(--brand-primary);
}

.margin-bottom-sm {
  margin-bottom: 12px;
}

.margin-top-md {
  margin-top: 32px;
}

.text-center {
  text-align: center;
}

/* Responsive */
@media (max-width: 992px) {
  .hero-grid, .providers-grid, .showcase-grid {
    grid-template-columns: 1fr;
  }
  .hero-content {
    text-align: center;
  }
  .hero-actions {
    justify-content: center;
  }
}
</style>
