<template>
  <div class="retro-body grid-mesh framer-appear" id="retro-landing-root">
    <!-- CRT Scanline overlay -->
    <div class="crt-overlay"></div>

    <!-- Navigation Header -->
    <header class="retro-header" id="nav-header">
      <div class="retro-container header-flex">
        <div class="retro-logo">
          <div class="retro-logo-icon">
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <polygon points="50,5 95,30 95,70 50,95 5,70 5,30" stroke="currentColor" stroke-width="6" stroke-linejoin="round" />
              <polygon points="50,20 80,38 80,62 50,80 20,62 20,38" stroke="currentColor" stroke-width="4" stroke-linejoin="round" stroke-dasharray="2 2" />
              <circle cx="50" cy="50" r="10" fill="currentColor" />
            </svg>
          </div>
          <span class="retro-title-text">CHRONOLINK</span>
        </div>
        
        <div class="telemetry-bar hidden-mobile">
          <span class="telemetry-dot active"></span>
          <span class="telemetry-text">TEMPORAL LOG: VAULT ACTIVE</span>
          <span class="telemetry-divider">|</span>
          <span class="telemetry-stat">EPOCH SYNC: 100.0%</span>
        </div>

        <nav class="retro-nav" id="main-nav">
          <a href="#concept" id="nav-link-concept">Concept</a>
          <a href="#customizer" id="nav-link-customizer">Tape Lab</a>
          <a href="#features" id="nav-link-features">Pillars</a>
          <a href="#console" id="nav-link-console">Terminal</a>
          <a href="#pricing" id="nav-link-pricing"> floppy Tiers</a>
        </nav>

        <div class="header-actions">
          <NuxtLink to="/" class="btn-retro btn-retro-cyan btn-sm" id="btn-back-home">
            Exit Console
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hero-section" id="hero">
      <div class="retro-container hero-grid">
        <div class="hero-text-block">
          <div class="retro-badge" id="hero-badge">SYSTEM VERSION // 88.4-OMEGA</div>
          <h1 class="retro-hero-title">
            Preserve Your Digital Essence <span class="text-glow">Across Eras</span>
          </h1>
          <p class="retro-hero-lead">
            ChronoLink translates raw credentials, digital secrets, and source code into offline, time-locked quantum-analog data capsules. Scheduled cryptographically to withstand centuries and unlock only at designated stellar epochs.
          </p>
          <div class="hero-button-group">
            <a href="#customizer" class="btn-retro btn-retro-magenta btn-lg" id="btn-hero-consign">
              Consign Capsule
            </a>
            <a href="#console" class="btn-retro btn-retro-secondary btn-lg" id="btn-hero-query">
              Query Vault
            </a>
          </div>
        </div>

        <!-- Hero Mainframe Visualization -->
        <div class="hero-visual-block">
          <div class="mainframe-case">
            <div class="mainframe-screen">
              <div class="screen-glare"></div>
              <div class="grid-radar">
                <div class="radar-line"></div>
                <div class="wireframe-capsule" :class="{ 'animating-capsule': isArchiving }">
                  <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <polygon points="50,15 85,35 85,65 50,85 15,65 15,35" stroke="var(--neon-color-cyan)" stroke-width="2" />
                    <line x1="50" y1="15" x2="50" y2="85" stroke="var(--neon-color-cyan)" stroke-width="1.5" stroke-dasharray="4 4" />
                    <line x1="15" y1="35" x2="85" y2="65" stroke="var(--neon-color-cyan)" stroke-width="1.5" stroke-dasharray="4 4" />
                    <line x1="15" y1="65" x2="85" y2="35" stroke="var(--neon-color-cyan)" stroke-width="1.5" stroke-dasharray="4 4" />
                    <circle cx="50" cy="50" r="18" stroke="var(--neon-color-magenta)" stroke-width="2" class="pulse-circle" />
                  </svg>
                </div>
              </div>
              <div class="telemetry-grid">
                <div class="tel-col">
                  <span>VECTOR: SECURE</span>
                  <span>CORE: CRITICAL</span>
                  <span>LOCK: ARMED</span>
                </div>
                <div class="tel-col text-right">
                  <span>DEC: 45.8821.9</span>
                  <span>RAST: ACTIVE</span>
                  <span>HZ: 60.0</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Concept Introduction Section -->
    <section class="concept-section" id="concept">
      <div class="retro-container">
        <div class="section-header-block">
          <span class="section-number">01 // CONTEXT</span>
          <h2 class="retro-section-title-alt">The Digital Archival Crisis</h2>
          <p class="section-subtitle">
            Modern storage media degrades in decades. Cloud infrastructures are vulnerable to geopolitical shifts. ChronoLink returns to the absolute resilience of physical analog structures augmented by quantum keys.
          </p>
        </div>

        <div class="concept-showcase">
          <div class="showcase-card-flat">
            <div class="card-num">I</div>
            <h3>Quantum Analog Medium</h3>
            <p>Our capsules record data onto multi-layer, physical micro-optic ribbons, shielding records against electromagnetic storms, solar flares, and cloud network decay.</p>
          </div>
          <div class="showcase-card-flat">
            <div class="card-num">II</div>
            <h3>Stellar Ephemeris Clock</h3>
            <p>No central server handles time validation. The unlock trigger relies on cryptographic block-hashes tied to planetary coordinate orbits and stellar alignments.</p>
          </div>
          <div class="showcase-card-flat">
            <div class="card-num">III</div>
            <h3>Zero-Knowledge Lock</h3>
            <p>The time-lock executes mathematically. Data is mathematically shielded under decentralized key shares that assemble only when the target time barrier is crossed.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Interactive Tape Lab (Capsule Customizer) -->
    <section class="customizer-section" id="customizer">
      <div class="retro-container">
        <div class="section-header-block">
          <span class="section-number">02 // CREATION LAB</span>
          <h2 class="retro-section-title-alt">Customize Your Cyber-Analog Capsule</h2>
          <p class="section-subtitle">
            Configure the visual telemetry, storage medium structure, and target lock-date of your archival capsule block.
          </p>
        </div>

        <div class="customizer-grid">
          <!-- Customizer Configuration Panel -->
          <div class="customizer-panel">
            <h3 class="panel-header-title">Capsule Specifications</h3>
            
            <div class="form-group-retro">
              <label for="capsule-label" class="label-retro">Capsule Name / Label</label>
              <input 
                type="text" 
                id="capsule-label" 
                v-model="capsuleLabel" 
                class="input-retro" 
                placeholder="e.g. PROJECT_GENESIS" 
                maxlength="20"
              />
              <span class="input-desc">Printed on the physically engraved metal chassis plate.</span>
            </div>

            <div class="form-group-retro">
              <label for="capsule-epoch" class="label-retro">Target Unlock Epoch (Year)</label>
              <select id="capsule-epoch" v-model="capsuleEpoch" class="select-retro">
                <option value="2050">Year 2050 (Early Archive)</option>
                <option value="2075">Year 2075 (Medium Archive)</option>
                <option value="2088">Year 2088 (Recommended)</option>
                <option value="2099">Year 2099 (Century Archive)</option>
                <option value="2150">Year 2150 (Deep Epoch)</option>
                <option value="2200">Year 2200 (Stellar Horizon)</option>
              </select>
              <span class="input-desc">The astronomical coordinate sync will release keys on Jan 1st of this year.</span>
            </div>

            <div class="form-group-retro">
              <label class="label-retro">Laser Chassis Color</label>
              <div class="color-picker-grid">
                <button 
                  type="button"
                  class="color-btn magenta-btn" 
                  :class="{ active: capsuleColor === 'magenta' }"
                  @click="capsuleColor = 'magenta'"
                  aria-label="Laser Magenta"
                ></button>
                <button 
                  type="button"
                  class="color-btn cyan-btn" 
                  :class="{ active: capsuleColor === 'cyan' }"
                  @click="capsuleColor = 'cyan'"
                  aria-label="Cyber Cyan"
                ></button>
                <button 
                  type="button"
                  class="color-btn lime-btn" 
                  :class="{ active: capsuleColor === 'lime' }"
                  @click="capsuleColor = 'lime'"
                  aria-label="Radioactive Lime"
                ></button>
                <button 
                  type="button"
                  class="color-btn amber-btn" 
                  :class="{ active: capsuleColor === 'amber' }"
                  @click="capsuleColor = 'amber'"
                  aria-label="Analog Amber"
                ></button>
              </div>
            </div>

            <div class="form-group-retro">
              <label class="label-retro">Archival Medium Density</label>
              <div class="radio-retro-group">
                <label class="radio-retro">
                  <input type="radio" value="standard" v-model="capsuleMedium" />
                  <span class="radio-custom"></span>
                  Standard Magnetic Optic (8-bit)
                </label>
                <label class="radio-retro">
                  <input type="radio" value="quantum" v-model="capsuleMedium" />
                  <span class="radio-custom"></span>
                  Quantum Entangled Ribbon (16-bit)
                </label>
                <label class="radio-retro">
                  <input type="radio" value="omega" v-model="capsuleMedium" />
                  <span class="radio-custom"></span>
                  Stellar Horizon Ribbon (32-bit)
                </label>
              </div>
            </div>
          </div>

          <!-- Dynamic Visual Preview Card -->
          <div class="customizer-preview">
            <h3 class="panel-header-title text-center">Mainframe Preview (Real-time Link)</h3>
            
            <div class="cassette-container" :style="{ '--active-color': activeColorHex, '--active-glow': activeColorGlow }">
              <!-- SVG Cassette -->
              <svg viewBox="0 0 400 240" fill="none" class="cassette-svg" xmlns="http://www.w3.org/2000/svg">
                <!-- Cassette Body Outer -->
                <rect x="10" y="10" width="380" height="220" rx="12" fill="#0d0e19" stroke="var(--active-color)" stroke-width="4" />
                <!-- Inset lines -->
                <rect x="25" y="25" width="350" height="190" rx="8" fill="#06070d" stroke="var(--active-color)" stroke-width="2" stroke-dasharray="4 2" />
                
                <!-- Label area -->
                <rect x="60" y="40" width="280" height="70" rx="4" fill="#0e101f" stroke="var(--active-color)" stroke-width="2" />
                <!-- Capsule details printed inside -->
                <text x="75" y="65" fill="var(--active-color)" font-family="'Share Tech Mono', monospace" font-size="16" letter-spacing="1">LABEL: {{ capsuleLabel || 'UNNAMED' }}</text>
                <text x="75" y="90" fill="#f0f2fa" font-family="'Share Tech Mono', monospace" font-size="14">MEDIUM: {{ capsuleMedium.toUpperCase() }} / TIME-LOCK: {{ capsuleEpoch }} A.D.</text>

                <!-- Left Reel Window -->
                <circle cx="130" cy="155" r="32" fill="#06070d" stroke="var(--active-color)" stroke-width="2" />
                <!-- Left spinning wheels spokes -->
                <g class="cassette-wheel" :class="{ rotating: isArchiving }">
                  <circle cx="130" cy="155" r="10" fill="var(--active-color)" />
                  <line x1="130" y1="123" x2="130" y2="187" stroke="var(--active-color)" stroke-width="3" />
                  <line x1="98" y1="155" x2="162" y2="155" stroke="var(--active-color)" stroke-width="3" />
                  <line x1="107" y1="132" x2="153" y2="178" stroke="var(--active-color)" stroke-width="3" />
                  <line x1="107" y1="178" x2="153" y2="132" stroke="var(--active-color)" stroke-width="3" />
                </g>

                <!-- Right Reel Window -->
                <circle cx="270" cy="155" r="32" fill="#06070d" stroke="var(--active-color)" stroke-width="2" />
                <!-- Right spinning wheels spokes -->
                <g class="cassette-wheel" :class="{ rotating: isArchiving }">
                  <circle cx="270" cy="155" r="10" fill="var(--active-color)" />
                  <line x1="270" y1="123" x2="270" y2="187" stroke="var(--active-color)" stroke-width="3" />
                  <line x1="238" y1="155" x2="302" y2="155" stroke="var(--active-color)" stroke-width="3" />
                  <line x1="247" y1="132" x2="293" y2="178" stroke="var(--active-color)" stroke-width="3" />
                  <line x1="247" y1="178" x2="293" y2="132" stroke="var(--active-color)" stroke-width="3" />
                </g>

                <!-- Cassette Center Holes & Trailing slots -->
                <rect x="170" y="145" width="60" height="20" rx="3" fill="#0d0e19" stroke="var(--active-color)" stroke-width="1.5" />
                <circle cx="180" cy="155" r="5" fill="#f0f2fa" />
                <circle cx="220" cy="155" r="5" fill="#f0f2fa" />
              </svg>
            </div>
            
            <div class="specs-telemetry text-center">
              <span>STATUS: READY FOR BURNING</span>
              <span>CHASSIS RESISTANCE: 4800 Gs</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Core Technology Pillars (Feature Grid) -->
    <section class="features-section" id="features">
      <div class="retro-container">
        <div class="section-header-block">
          <span class="section-number">03 // ARCHITECTURE</span>
          <h2 class="retro-section-title-alt">The Archival Foundations</h2>
          <p class="section-subtitle">
            ChronoLink operates across physical hardware nodes, cryptographic clock parameters, and time-stamped proof systems.
          </p>
        </div>

        <div class="pillars-grid">
          <!-- Pillar 1 -->
          <div class="pillar-panel">
            <div class="panel-scanner"></div>
            <div class="pillar-header">
              <svg class="svg-icon pillar-icon" viewBox="0 0 24 24" style="width: 24px; height: 24px; color: var(--neon-color-cyan); margin-right: 8px;"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle><path d="M12 2v20M2 12h20"></path></svg>
              <h4>Chronostate Routing</h4>
            </div>
            <p>Routes the encrypted block across offline storage vaults embedded within high-density, geothermal bunkers. Bypasses standard digital routing networks entirely.</p>
          </div>

          <!-- Pillar 2 -->
          <div class="pillar-panel">
            <div class="panel-scanner"></div>
            <div class="pillar-header">
              <svg class="svg-icon pillar-icon" viewBox="0 0 24 24" style="width: 24px; height: 24px; color: var(--neon-color-cyan); margin-right: 8px;"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
              <h4>Laser Optic Ribbon</h4>
            </div>
            <p>Encodes digital packets directly onto synthetic quartz optical ribbons. Immune to chemical degradation, thermal stress, and standard bit-rot phenomena.</p>
          </div>

          <!-- Pillar 3 -->
          <div class="pillar-panel">
            <div class="pillar-header">
              <svg class="svg-icon pillar-icon" viewBox="0 0 24 24" style="width: 24px; height: 24px; color: var(--neon-color-cyan); margin-right: 8px;"><circle cx="12" cy="12" r="6"></circle><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" transform="rotate(30 12 12)"></path></svg>
              <h4>Stellar Lock Sync</h4>
            </div>
            <p>Integrates astronomical coordinate trackers. Solves mathematical decryption formulas using planetary position telemetry, rendering pre-mature cracking impossible.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Interactive Terminal Sandbox -->
    <section class="console-section" id="console">
      <div class="retro-container">
        <div class="section-header-block">
          <span class="section-number">04 // SIMULATOR</span>
          <h2 class="retro-section-title-alt">Initiate Temporal Vaulting Sequence</h2>
          <p class="section-subtitle">
            Input a test message or codebase manifest below to simulate the physical laser-burning and time-lock packaging process.
          </p>
        </div>

        <div class="terminal-wrapper">
          <!-- Terminal Main Frame -->
          <div class="terminal-body">
            <div class="terminal-bar">
              <div class="term-dots">
                <span class="term-dot red"></span>
                <span class="term-dot yellow"></span>
                <span class="term-dot green"></span>
              </div>
              <div class="term-title">CHRONO-WRITER OPERATING SYSTEMS v1.2</div>
              <div class="term-status-badge">SECURE_NODE_8</div>
            </div>

            <div class="terminal-content">
              <!-- Console log output -->
              <div class="console-logs-area" ref="logsContainer">
                <div class="log-row intro-log">CHRONOLINK CONSOLE SUBSYSTEM ACTIVE</div>
                <div class="log-row">MODEL: QUANTUM-LOCK-88</div>
                <div class="log-row">SYSTEM STATUS: READY FOR INPUT PAYLOAD</div>
                <div class="log-row">----------------------------------------</div>
                
                <!-- Dynamic Logs -->
                <div class="log-row" v-for="(log, idx) in consoleLogs" :key="idx">
                  <span class="log-time">[{{ log.timestamp }}]</span> {{ log.text }}
                </div>

                <!-- Simulation Success Panel -->
                <div class="success-alert-block" v-if="showSuccess">
                  <div class="success-header">▼ CAPSULE SEALED AND VAULTED ▼</div>
                  <div class="success-details">
                    <span>CAPSULE INDEX: {{ generatedHash }}</span>
                    <span>TARGET UNLOCK: YEAR {{ capsuleEpoch }} A.D.</span>
                    <span>DENSITY VALUE: {{ capsuleMedium.toUpperCase() }} GRADE</span>
                    <span>LOCK SHA-256: e8b9c2409f87ba6209...</span>
                  </div>
                  <div class="success-note">
                    Laser burning sequence completed. Cryptographic timeline keys successfully routed to astronomical coordinate vaults. See you in the future.
                  </div>
                </div>

                <!-- Active processing cursor -->
                <div class="log-row cursor-row" v-if="isArchiving">
                  <span class="cursor-block"></span>
                  <span>Writing blocks: {{ consoleProgress }}%</span>
                </div>
              </div>

              <!-- Interactive Controls inside the Terminal -->
              <div class="terminal-input-bar">
                <span class="terminal-prompt">$</span>
                <input 
                  type="text" 
                  id="terminal-input"
                  v-model="consolePayload" 
                  class="terminal-input-field" 
                  placeholder="Enter message to store in the time capsule..."
                  :disabled="isArchiving"
                  @keyup.enter="runArchival"
                />
                <button 
                  type="button"
                  class="terminal-send-btn" 
                  @click="runArchival" 
                  :disabled="isArchiving || !consolePayload.trim()"
                  id="btn-execute-vault"
                >
                  {{ isArchiving ? 'BURNING...' : 'SECURE VAULT' }}
                </button>
              </div>

              <!-- Progress bar representation -->
              <div class="terminal-progress-container" v-if="isArchiving">
                <div class="progress-bar-fill" :style="{ width: consoleProgress + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing Consignment Floppy Cards -->
    <section class="pricing-section" id="pricing">
      <div class="retro-container">
        <div class="section-header-block">
          <span class="section-number">05 // CONSIGNMENT RATES</span>
          <h2 class="retro-section-title-alt">Archival Tiers</h2>
          <p class="section-subtitle">
            Choose the lock length, ribbon configuration, and structural protection capsule for your digital heritage.
          </p>
        </div>

        <div class="floppy-grid">
          <!-- Floppy 1 -->
          <div class="floppy-disk">
            <div class="floppy-metal-slider">
              <span class="slider-notch"></span>
            </div>
            <div class="floppy-label-plate">
              <span class="floppy-hd-badge font-semibold">HD</span>
              <div class="floppy-label-title">THE VOYAGER</div>
              <div class="floppy-label-epoch">10-YEAR SECURE LOCK</div>
              <div class="floppy-features">
                <ul>
                  <li>- 8-bit Magnetic Ribbon</li>
                  <li>- Ceramic Hard Shell Case</li>
                  <li>- Decryption Registry Sync</li>
                  <li>- Standard Solar Shielding</li>
                </ul>
              </div>
              <div class="floppy-price">$49</div>
              <button 
                type="button" 
                class="btn-retro btn-retro-cyan btn-full margin-top-xs"
                @click="capsuleEpoch = '2050'; capsuleMedium = 'standard'; capsuleLabel = 'VOYAGER_CAPSULE'"
              >
                SELECT TIER
              </button>
            </div>
            <div class="floppy-write-protect"></div>
          </div>

          <!-- Floppy 2 -->
          <div class="floppy-disk premium-disk">
            <div class="floppy-metal-slider">
              <span class="slider-notch"></span>
            </div>
            <div class="floppy-label-plate">
              <span class="floppy-hd-badge font-semibold">HD</span>
              <div class="floppy-label-title">THE EPOCH</div>
              <div class="floppy-label-epoch">50-YEAR CHRONO SECURE</div>
              <div class="floppy-features">
                <ul>
                  <li>- 16-bit Quantum Ribbon</li>
                  <li>- Titanium-Coated Chassis</li>
                  <li>- Geothermal Bunker Route</li>
                  <li>- Active Flare Deflection</li>
                </ul>
              </div>
              <div class="floppy-price">$149</div>
              <button 
                type="button" 
                class="btn-retro btn-retro-magenta btn-full margin-top-xs"
                @click="capsuleEpoch = '2088'; capsuleMedium = 'quantum'; capsuleLabel = 'EPOCH_CAPSULE'"
              >
                SELECT TIER
              </button>
            </div>
            <div class="floppy-write-protect"></div>
          </div>

          <!-- Floppy 3 -->
          <div class="floppy-disk">
            <div class="floppy-metal-slider">
              <span class="slider-notch"></span>
            </div>
            <div class="floppy-label-plate">
              <span class="floppy-hd-badge font-semibold">HD</span>
              <div class="floppy-label-title">DEEP COSMOS</div>
              <div class="floppy-label-epoch">100-YEAR VAULT LOCK</div>
              <div class="floppy-features">
                <ul>
                  <li>- 32-bit Stellar Ribbon</li>
                  <li>- Quartz Enclosed Capsule</li>
                  <li>- Multi-Orbit Clock Registry</li>
                  <li>- Complete EMP Protection</li>
                </ul>
              </div>
              <div class="floppy-price">$399</div>
              <button 
                type="button" 
                class="btn-retro btn-retro-amber btn-full margin-top-xs"
                @click="capsuleEpoch = '2200'; capsuleMedium = 'omega'; capsuleLabel = 'COSMOS_CAPSULE'"
              >
                SELECT TIER
              </button>
            </div>
            <div class="floppy-write-protect"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Synthwave Grid Sunset (CTA) -->
    <section class="cta-sunset-section">
      <div class="wireframe-sun"></div>
      
      <!-- Scrolling perspective grid floor -->
      <div class="perspective-grid-floor"></div>

      <div class="retro-container cta-overlay-content">
        <h2 class="cta-title-text text-glow-magenta">Begin Your Temporal Consignment</h2>
        <p class="cta-sub-text">
          Protect your assets against the degradation of the digital cloud era. Lock your capsule now.
        </p>
        <div class="text-center margin-top-md">
          <a href="#customizer" class="btn-retro btn-retro-magenta btn-xl" id="btn-cta-launch">
            LAUNCH TAPE LAB
          </a>
        </div>
      </div>
    </section>

    <!-- Telemetry Footer -->
    <footer class="retro-footer">
      <div class="retro-container footer-grid-layout">
        <div class="footer-brand">
          <span class="brand-monogram">C//L</span>
          <span class="footer-copy-text">&copy; 2026 CHRONOLINK SYSTEMS. ALL TIMES REGISTERED.</span>
        </div>
        <div class="footer-system-status">
          <span>LATENCY: 0.88ms</span>
          <span>SYNC: STELLAR_CLOCK_OK</span>
          <span>SECURITY: SECURE_100</span>
        </div>
        <div class="footer-nav-links">
          <a href="#hero">Top</a>
          <a href="#concept">Concept</a>
          <a href="#customizer">Lab</a>
          <a href="#console">Terminal</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'

definePageMeta({
  layout: 'empty'
})

useHead({
  title: 'ChronoLink Systems — Retro-Futuristic Digital Archive',
  meta: [
    { name: 'description', content: 'Preserve your digital legacy across the streams of time. ChronoLink packages messages, keys, and codebases in time-locked cyber-analog capsules.' }
  ],
  link: [
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600;700&display=swap' }
  ]
})

// Customizer state variables
const capsuleLabel = ref('CORE_ARCHIVE_88')
const capsuleEpoch = ref('2088')
const capsuleColor = ref('magenta') // magenta, cyan, lime, amber
const capsuleMedium = ref('quantum') // standard, quantum, omega

// Simulator variables
const consolePayload = ref('')
const isArchiving = ref(false)
const consoleProgress = ref(0)
const consoleLogs = ref([])
const showSuccess = ref(false)
const generatedHash = ref('')
const logsContainer = ref(null)

const colorsMap = {
  magenta: { hex: '#ff007f', glow: 'rgba(255, 0, 127, 0.4)' },
  cyan: { hex: '#00f3ff', glow: 'rgba(0, 243, 255, 0.4)' },
  lime: { hex: '#39ff14', glow: 'rgba(57, 255, 20, 0.4)' },
  amber: { hex: '#ffaa00', glow: 'rgba(255, 170, 0, 0.4)' }
}

const activeColorHex = computed(() => colorsMap[capsuleColor.value]?.hex || '#ff007f')
const activeColorGlow = computed(() => colorsMap[capsuleColor.value]?.glow || 'rgba(255, 0, 127, 0.4)')

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const runArchival = async () => {
  if (!consolePayload.value.trim() || isArchiving.value) return
  
  isArchiving.value = true
  showSuccess.value = false
  consoleProgress.value = 0
  consoleLogs.value = []
  
  const steps = [
    'Establishing Chronostatic Synchronizer interface...',
    'Checking quantum entanglement register... STATUS: OK',
    'Activating zero-knowledge storage vault block...',
    'Encrypting payload with local SHA-256 entropy node...',
    `Creating laser chassis stamp: "${capsuleLabel.value || 'UNNAMED'}"`,
    `Calibrating target unlock alignment for Stellar Epoch ${capsuleEpoch.value} A.D.`,
    `Modulating optical frequency: ${capsuleMedium.value.toUpperCase()} DENSITY TYPE`,
    'Locking archival registry node parameters...',
    'Analog ribbon physical write cycle: ENGAGED [Progress 100%]',
    'Validating cryptographic timeline seal...'
  ]

  for (let i = 0; i < steps.length; i++) {
    consoleLogs.value.push({
      text: steps[i],
      timestamp: new Date().toLocaleTimeString()
    })
    consoleProgress.value = Math.min(Math.round(((i + 1) / steps.length) * 100), 100)
    
    // Auto-scroll logs to bottom
    await nextTick()
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
    
    await sleep(400 + Math.random() * 250)
  }

  generatedHash.value = 'CLK-' + Math.random().toString(36).substring(2, 9).toUpperCase() + '-' + capsuleEpoch.value
  showSuccess.value = true
  isArchiving.value = false
  consolePayload.value = ''
  
  await nextTick()
  if (logsContainer.value) {
    logsContainer.value.scrollTop = logsContainer.value.scrollHeight
  }
}

// Watch logs to scroll logs
watch(consoleLogs, async () => {
  await nextTick()
  if (logsContainer.value) {
    logsContainer.value.scrollTop = logsContainer.value.scrollHeight
  }
}, { deep: true })
</script>

<style scoped>
/* Reset and base page rules specifically scoped for retro layout */
.retro-body {
  background-color: #04040a;
  color: #f0f2fa;
  font-family: 'Inter', -apple-system, sans-serif;
  line-height: 1.6;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 0;
  
  /* Primary variables */
  --neon-color-magenta: #ff007f;
  --neon-color-cyan: #00f3ff;
  --neon-color-lime: #39ff14;
  --neon-color-amber: #ffaa00;
  --panel-bg: #090a12;
  --panel-bg-subtle: #0d0f1c;
  --panel-border: #181b35;
}

/* Base layout container */
.retro-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Glare & scanline styling for vintage TV monitor effect */
.crt-overlay {
  content: " ";
  display: block;
  position: fixed;
  top: 0; left: 0; bottom: 0; right: 0;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
  z-index: 9999;
  background-size: 100% 4px, 3px 100%;
  pointer-events: none;
  opacity: 0.8;
}

.crt-overlay::after {
  content: " ";
  display: block;
  position: fixed;
  top: 0; left: 0; bottom: 0; right: 0;
  background: radial-gradient(circle, rgba(0,0,0,0) 60%, rgba(0,0,0,0.5) 100%);
  pointer-events: none;
  z-index: 10000;
}

/* Background grid mesh */
.grid-mesh {
  background-image: linear-gradient(rgba(24, 27, 53, 0.25) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(24, 27, 53, 0.25) 1px, transparent 1px);
  background-size: 40px 40px;
}

/* Navigation header block */
.retro-header {
  border-bottom: 2px solid var(--panel-border);
  background-color: rgba(9, 10, 18, 0.9);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 100;
  height: 80px;
}

.header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.retro-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.retro-logo-icon {
  width: 38px;
  height: 38px;
  color: var(--neon-color-cyan);
}

.retro-title-text {
  font-family: 'Orbitron', sans-serif;
  font-weight: 900;
  font-size: 22px;
  letter-spacing: 0.15em;
  background: linear-gradient(135deg, #ffffff 0%, var(--neon-color-cyan) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Telemetry display bar */
.telemetry-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: #718096;
  border: 1px solid var(--panel-border);
  padding: 6px 12px;
  background-color: #05050a;
  border-radius: 4px;
}

.telemetry-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--neon-color-magenta);
}

.telemetry-dot.active {
  animation: telemetryPulse 1s infinite alternate;
}

@keyframes telemetryPulse {
  0% { opacity: 0.3; box-shadow: 0 0 0px var(--neon-color-magenta); }
  100% { opacity: 1; box-shadow: 0 0 8px var(--neon-color-magenta); }
}

.telemetry-divider {
  color: var(--panel-border);
}

.retro-nav {
  display: flex;
  gap: 24px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 14px;
}

.retro-nav a {
  color: #a0aec0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
  position: relative;
  padding: 6px 0;
}

.retro-nav a::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--neon-color-magenta);
  transition: width 0.2s ease;
}

.retro-nav a:hover {
  color: #ffffff;
  text-shadow: 0 0 8px var(--neon-color-magenta);
}

.retro-nav a:hover::after {
  width: 100%;
}

/* Interactive custom styled buttons */
.btn-retro {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: 'Share Tech Mono', monospace;
  text-transform: uppercase;
  font-weight: bold;
  letter-spacing: 0.08em;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  border: 2px solid transparent;
  outline: none;
}

.btn-retro-magenta {
  background-color: var(--neon-color-magenta);
  color: #ffffff;
  border-color: var(--neon-color-magenta);
  box-shadow: 0 0 12px rgba(255, 0, 127, 0.3);
}

.btn-retro-magenta:hover {
  background-color: transparent;
  color: var(--neon-color-magenta);
  box-shadow: 0 0 20px rgba(255, 0, 127, 0.6);
  transform: translateY(-2px);
}

.btn-retro-cyan {
  background-color: var(--neon-color-cyan);
  color: #04040a;
  border-color: var(--neon-color-cyan);
  box-shadow: 0 0 12px rgba(0, 243, 255, 0.3);
}

.btn-retro-cyan:hover {
  background-color: transparent;
  color: var(--neon-color-cyan);
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.6);
  transform: translateY(-2px);
}

.btn-retro-amber {
  background-color: var(--neon-color-amber);
  color: #04040a;
  border-color: var(--neon-color-amber);
  box-shadow: 0 0 12px rgba(255, 170, 0, 0.3);
}

.btn-retro-amber:hover {
  background-color: transparent;
  color: var(--neon-color-amber);
  box-shadow: 0 0 20px rgba(255, 170, 0, 0.6);
  transform: translateY(-2px);
}

.btn-retro-secondary {
  background-color: transparent;
  color: #ffffff;
  border-color: var(--panel-border);
}

.btn-retro-secondary:hover {
  border-color: #ffffff;
  background-color: rgba(255, 255, 255, 0.05);
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.btn-retro:active {
  transform: translateY(1px) !important;
}

.btn-sm {
  padding: 6px 16px;
  font-size: 13px;
}

.btn-lg {
  padding: 12px 28px;
  font-size: 16px;
}

.btn-xl {
  padding: 16px 36px;
  font-size: 18px;
  border-width: 3px;
}

.btn-full {
  width: 100%;
}

/* Hero layout */
.hero-section {
  padding: 100px 0;
  border-bottom: 2px solid var(--panel-border);
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 60px;
  align-items: center;
}

.retro-badge {
  font-family: 'Share Tech Mono', monospace;
  color: var(--neon-color-magenta);
  font-weight: bold;
  letter-spacing: 0.1em;
  font-size: 13px;
  margin-bottom: 16px;
  display: inline-block;
  border: 1px solid var(--neon-color-magenta);
  padding: 4px 10px;
  background-color: rgba(255, 0, 127, 0.05);
  border-radius: 4px;
}

.retro-hero-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 58px;
  font-weight: 900;
  line-height: 1.15;
  letter-spacing: -0.01em;
  margin-bottom: 24px;
  color: #ffffff;
}

.text-glow {
  color: var(--neon-color-cyan);
  text-shadow: 0 0 12px rgba(0, 243, 255, 0.5);
}

.retro-hero-lead {
  font-size: 17px;
  color: #a0aec0;
  margin-bottom: 40px;
  line-height: 1.7;
}

.hero-button-group {
  display: flex;
  gap: 20px;
}

/* Mainframe terminal visual container */
.mainframe-case {
  background: #10121d;
  border: 4px solid var(--panel-border);
  box-shadow: 0 20px 40px rgba(0,0,0,0.6), inset 0 2px 0 rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 16px;
  position: relative;
}

.mainframe-case::before {
  content: "";
  position: absolute;
  top: -4px; left: 20px; width: 60px; height: 4px;
  background: var(--neon-color-magenta);
}

.mainframe-screen {
  background: #020307;
  border: 2px solid #04040a;
  border-radius: 8px;
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.screen-glare {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0) 50%);
  pointer-events: none;
}

.grid-radar {
  height: 220px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(24, 27, 53, 0.6);
  background: radial-gradient(circle, rgba(9, 10, 18, 0.7) 0%, rgba(2, 3, 7, 0.9) 100%);
  border-radius: 4px;
  overflow: hidden;
}

.radar-line {
  position: absolute;
  top: 50%; left: 0; width: 100%; height: 1px;
  background: rgba(0, 243, 255, 0.15);
}

.wireframe-capsule {
  width: 140px;
  height: 140px;
  position: relative;
  transition: transform 0.5s ease;
}

.wireframe-capsule svg {
  width: 100%;
  height: 100%;
  animation: spinWireframe 10s linear infinite;
}

.animating-capsule svg {
  animation: spinWireframeFast 2s linear infinite, shakeCapsule 0.2s infinite alternate;
}

@keyframes spinWireframe {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes spinWireframeFast {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes shakeCapsule {
  0% { translate: -1px -1px; }
  100% { translate: 1px 1px; }
}

.pulse-circle {
  animation: pulseScale 2s infinite alternate;
  transform-origin: center;
}

@keyframes pulseScale {
  0% { transform: scale(0.8); opacity: 0.4; }
  100% { transform: scale(1.2); opacity: 0.9; }
}

.telemetry-grid {
  display: flex;
  justify-content: space-between;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: var(--neon-color-cyan);
  margin-top: 16px;
  opacity: 0.8;
}

.tel-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Concept Cards grid */
.concept-section {
  padding: 100px 0;
  background-color: var(--panel-bg);
  border-bottom: 2px solid var(--panel-border);
}

.section-header-block {
  text-align: center;
  max-width: 700px;
  margin: 0 auto 60px auto;
}

.section-number {
  font-family: 'Share Tech Mono', monospace;
  color: var(--neon-color-magenta);
  font-size: 13px;
  font-weight: bold;
  letter-spacing: 0.15em;
  display: block;
  margin-bottom: 12px;
}

.retro-section-title-alt {
  font-family: 'Orbitron', sans-serif;
  font-weight: 800;
  font-size: 38px;
  color: #ffffff;
  margin-bottom: 20px;
}

.section-subtitle {
  font-size: 16px;
  color: #718096;
  line-height: 1.6;
}

.concept-showcase {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.showcase-card-flat {
  background-color: var(--panel-bg-subtle);
  border: 1px solid var(--panel-border);
  padding: 40px 30px;
  border-radius: 6px;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
}

.showcase-card-flat::before {
  content: "";
  position: absolute;
  top: 0; left: 0; width: 100%; height: 3px;
  background-color: var(--panel-border);
  transition: background-color 0.25s ease;
}

.showcase-card-flat:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 243, 255, 0.4);
}

.showcase-card-flat:hover::before {
  background-color: var(--neon-color-cyan);
}

.card-num {
  font-family: 'Orbitron', sans-serif;
  font-size: 24px;
  font-weight: 900;
  color: var(--neon-color-magenta);
  margin-bottom: 20px;
  opacity: 0.8;
}

.showcase-card-flat h3 {
  font-family: 'Orbitron', sans-serif;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #ffffff;
}

.showcase-card-flat p {
  font-size: 14.5px;
  color: #a0aec0;
  line-height: 1.6;
}

/* Customizer Lab section layout */
.customizer-section {
  padding: 100px 0;
  border-bottom: 2px solid var(--panel-border);
}

.customizer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: flex-start;
}

.customizer-panel {
  background-color: var(--panel-bg-subtle);
  border: 2px solid var(--panel-border);
  border-radius: 8px;
  padding: 30px;
}

.panel-header-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  text-transform: uppercase;
  color: #ffffff;
  border-bottom: 2px solid var(--panel-border);
  padding-bottom: 16px;
  margin-bottom: 24px;
  letter-spacing: 0.05em;
}

.form-group-retro {
  margin-bottom: 24px;
}

.label-retro {
  display: block;
  font-family: 'Share Tech Mono', monospace;
  font-size: 14px;
  color: #a0aec0;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.input-retro {
  width: 100%;
  background-color: #04040a;
  border: 1px solid var(--panel-border);
  color: #ffffff;
  padding: 12px 16px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 16px;
  border-radius: 4px;
  outline: none;
  transition: all 0.2s ease;
}

.input-retro:focus {
  border-color: var(--neon-color-magenta);
  box-shadow: 0 0 8px rgba(255, 0, 127, 0.2);
}

.select-retro {
  width: 100%;
  background-color: #04040a;
  border: 1px solid var(--panel-border);
  color: #ffffff;
  padding: 12px 16px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 16px;
  border-radius: 4px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.select-retro:focus {
  border-color: var(--neon-color-cyan);
}

.input-desc {
  font-size: 11.5px;
  color: #718096;
  margin-top: 6px;
  display: block;
}

.color-picker-grid {
  display: flex;
  gap: 16px;
}

.color-btn {
  width: 38px;
  height: 38px;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid #04040a;
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.color-btn.active {
  transform: scale(1.1);
  border-color: #ffffff;
}

.magenta-btn { background-color: var(--neon-color-magenta); }
.cyan-btn { background-color: var(--neon-color-cyan); }
.lime-btn { background-color: var(--neon-color-lime); }
.amber-btn { background-color: var(--neon-color-amber); }

.radio-retro-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-retro {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 14px;
  color: #ffffff;
  cursor: pointer;
  user-select: none;
}

.radio-retro input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.radio-custom {
  height: 18px;
  width: 18px;
  background-color: #04040a;
  border: 1px solid var(--panel-border);
  border-radius: 2px;
  display: inline-block;
  position: relative;
}

.radio-retro:hover input ~ .radio-custom {
  border-color: var(--neon-color-cyan);
}

.radio-retro input:checked ~ .radio-custom {
  border-color: var(--neon-color-cyan);
  background-color: rgba(0, 243, 255, 0.1);
}

.radio-custom::after {
  content: "";
  position: absolute;
  display: none;
  left: 5px; top: 2px; width: 6px; height: 10px;
  border: solid var(--neon-color-cyan);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.radio-retro input:checked ~ .radio-custom::after {
  display: block;
}

/* Cassette Visual rendering */
.customizer-preview {
  background-color: var(--panel-bg-subtle);
  border: 2px solid var(--panel-border);
  border-radius: 8px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: sticky;
  top: 100px;
}

.cassette-container {
  width: 100%;
  max-width: 400px;
  background-color: #06070d;
  padding: 20px;
  border-radius: 8px;
  border: 2px solid var(--panel-border);
  box-shadow: 0 0 30px var(--active-glow);
  transition: all 0.3s ease;
  margin-bottom: 24px;
}

.cassette-svg {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0 4px var(--active-glow));
}

.cassette-wheel {
  transform-origin: 130px 155px;
}

.cassette-wheel:nth-of-type(2) {
  transform-origin: 270px 155px;
}

.cassette-wheel.rotating {
  animation: reelSpin 1.5s linear infinite;
}

@keyframes reelSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.specs-telemetry {
  display: flex;
  gap: 20px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: #718096;
}

/* Feature Panels matrix block */
.features-section {
  padding: 100px 0;
  background-color: var(--panel-bg);
  border-bottom: 2px solid var(--panel-border);
}

.pillars-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.pillar-panel {
  background-color: var(--panel-bg-subtle);
  border: 2px solid var(--panel-border);
  padding: 30px;
  border-radius: 6px;
  position: relative;
  overflow: hidden;
}

.panel-scanner {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 2px;
  background: linear-gradient(90deg, transparent, var(--neon-color-magenta), transparent);
  animation: scanningPanel 3s infinite linear;
}

@keyframes scanningPanel {
  0% { top: 0%; opacity: 0; }
  5% { opacity: 0.8; }
  95% { opacity: 0.8; }
  100% { top: 100%; opacity: 0; }
}

.pillar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.pillar-icon {
  font-size: 24px;
}

.pillar-panel h4 {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  color: #ffffff;
}

.pillar-panel p {
  font-size: 14px;
  color: #a0aec0;
  line-height: 1.6;
}

/* Terminal Console design layout */
.console-section {
  padding: 100px 0;
  border-bottom: 2px solid var(--panel-border);
}

.terminal-wrapper {
  max-width: 850px;
  margin: 0 auto;
}

.terminal-body {
  background-color: #020306;
  border: 2px solid var(--panel-border);
  box-shadow: 0 20px 40px rgba(0,0,0,0.8), 0 0 20px rgba(24, 27, 53, 0.5);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.terminal-bar {
  background-color: #0b0c16;
  border-bottom: 2px solid var(--panel-border);
  padding: 12px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.term-dots {
  display: flex;
  gap: 8px;
}

.term-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.term-dot.red { background-color: #fc8181; }
.term-dot.yellow { background-color: #ecc94b; }
.term-dot.green { background-color: #48bb78; }

.term-title {
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: #718096;
  letter-spacing: 0.05em;
}

.term-status-badge {
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: var(--neon-color-lime);
  background-color: rgba(57, 255, 20, 0.08);
  border: 1px solid var(--neon-color-lime);
  padding: 2px 6px;
  border-radius: 2px;
}

.terminal-content {
  padding: 24px;
  font-family: 'Share Tech Mono', monospace;
}

.console-logs-area {
  height: 280px;
  overflow-y: auto;
  margin-bottom: 20px;
  color: #cbd5e0;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-row {
  line-height: 1.5;
}

.intro-log {
  color: var(--neon-color-cyan);
  font-weight: bold;
}

.log-time {
  color: #4a5568;
  margin-right: 8px;
}

.cursor-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--neon-color-lime);
}

.cursor-block {
  width: 8px;
  height: 15px;
  background-color: var(--neon-color-lime);
  animation: blinkCursor 0.8s infinite alternate;
}

@keyframes blinkCursor {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

.success-alert-block {
  border: 1px solid var(--neon-color-lime);
  background-color: rgba(57, 255, 20, 0.04);
  padding: 16px;
  margin: 12px 0;
  border-radius: 4px;
  animation: borderFlicker 0.15s infinite alternate;
}

.success-header {
  color: var(--neon-color-lime);
  font-weight: bold;
  font-size: 15px;
  margin-bottom: 12px;
  text-shadow: 0 0 4px rgba(57, 255, 20, 0.4);
}

.success-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 16px;
  color: #cbd5e0;
  font-size: 13px;
  margin-bottom: 12px;
}

.success-note {
  font-size: 12.5px;
  color: #a0aec0;
  border-top: 1px dashed rgba(57, 255, 20, 0.2);
  padding-top: 10px;
}

.terminal-input-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  border-top: 2px solid var(--panel-border);
  padding-top: 16px;
}

.terminal-prompt {
  color: var(--neon-color-magenta);
  font-weight: bold;
  font-size: 18px;
}

.terminal-input-field {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #ffffff;
  font-family: 'Share Tech Mono', monospace;
  font-size: 16px;
}

.terminal-send-btn {
  background-color: var(--panel-border);
  border: 1px solid var(--panel-border);
  color: #ffffff;
  padding: 8px 20px;
  cursor: pointer;
  border-radius: 4px;
  font-family: 'Share Tech Mono', monospace;
  transition: all 0.2s ease;
}

.terminal-send-btn:hover:not(:disabled) {
  border-color: var(--neon-color-lime);
  color: var(--neon-color-lime);
  background-color: rgba(57, 255, 20, 0.05);
}

.terminal-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.terminal-progress-container {
  height: 4px;
  background-color: #0b0c16;
  margin-top: 12px;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background-color: var(--neon-color-lime);
  box-shadow: 0 0 8px var(--neon-color-lime);
  transition: width 0.2s linear;
}

/* Pricing cards floppy disks */
.pricing-section {
  padding: 100px 0;
  background-color: var(--panel-bg);
  border-bottom: 2px solid var(--panel-border);
}

.floppy-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
  max-width: 1000px;
  margin: 0 auto;
}

.floppy-disk {
  background-color: #1a1e2f; /* Deep blue-gray plastic texture */
  border-radius: 12px 12px 0 0;
  padding: 24px;
  position: relative;
  border: 3px solid var(--panel-border);
  box-shadow: 0 15px 30px rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  height: 380px;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.floppy-disk:hover {
  transform: translateY(-8px);
}

.premium-disk {
  border-color: var(--neon-color-magenta);
  box-shadow: 0 20px 40px rgba(255, 0, 127, 0.15);
}

.floppy-metal-slider {
  height: 45px;
  width: 100px;
  background: linear-gradient(180deg, #718096 0%, #cbd5e0 50%, #4a5568 100%);
  border-radius: 4px;
  margin: 0 auto 20px auto;
  position: relative;
  border: 1px solid #2d3748;
}

.slider-notch {
  width: 12px;
  height: 25px;
  background-color: #0f121d;
  position: absolute;
  top: 10px;
  left: 20px;
  border-radius: 2px;
}

.floppy-label-plate {
  background-color: #ffffff; /* White label sticker */
  border-radius: 4px;
  flex: 1;
  padding: 16px;
  color: #1a202c;
  display: flex;
  flex-direction: column;
  position: relative;
}

.floppy-hd-badge {
  position: absolute;
  right: 12px;
  top: 12px;
  font-size: 11px;
  color: #e2e8f0;
  background-color: #1a202c;
  padding: 1px 4px;
  border-radius: 2px;
}

.floppy-label-title {
  font-family: 'Orbitron', sans-serif;
  font-weight: 800;
  font-size: 16px;
  margin-bottom: 2px;
  color: #1a202c;
}

.floppy-label-epoch {
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: #718096;
  margin-bottom: 12px;
}

.floppy-features {
  font-size: 12px;
  line-height: 1.5;
  color: #4a5568;
  flex: 1;
}

.floppy-features ul {
  list-style: none;
}

.floppy-price {
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  font-weight: 900;
  text-align: right;
  margin-top: auto;
  color: #1a202c;
  border-top: 1px dashed #e2e8f0;
  padding-top: 8px;
}

.floppy-write-protect {
  position: absolute;
  bottom: 12px;
  right: 12px;
  width: 14px;
  height: 14px;
  background-color: #0f121d;
  border-radius: 2px;
}

.margin-top-xs { margin-top: 12px; }

/* Synthwave Sunset (CTA Landscape) layout */
.cta-sunset-section {
  height: 500px;
  background: linear-gradient(to bottom, #05050a 0%, #1e002a 60%, #4d0046 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-bottom: 2px solid var(--panel-border);
}

.wireframe-sun {
  width: 250px;
  height: 250px;
  background: linear-gradient(to bottom, var(--neon-color-magenta) 0%, var(--neon-color-amber) 100%);
  border-radius: 50%;
  position: absolute;
  top: 50px;
  box-shadow: 0 0 80px rgba(255, 0, 127, 0.4);
  /* Synthwave horizontal slices */
  mask-image: linear-gradient(
    to bottom,
    white 0%,
    white 60%,
    transparent 60%,
    transparent 65%,
    white 65%,
    white 75%,
    transparent 75%,
    transparent 80%,
    white 80%,
    white 88%,
    transparent 88%,
    transparent 92%,
    white 92%,
    white 97%,
    transparent 97%
  );
  -webkit-mask-image: linear-gradient(
    to bottom,
    white 0%,
    white 60%,
    transparent 60%,
    transparent 65%,
    white 65%,
    white 75%,
    transparent 75%,
    transparent 80%,
    white 80%,
    white 88%,
    transparent 88%,
    transparent 92%,
    white 92%,
    white 97%,
    transparent 97%
  );
}

.perspective-grid-floor {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 250px;
  background-image: 
    linear-gradient(rgba(0, 243, 255, 0.2) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 243, 255, 0.2) 1px, transparent 1px);
  background-size: 40px 40px;
  transform: perspective(180px) rotateX(75deg);
  transform-origin: top center;
  animation: gridMovement 15s linear infinite;
}

@keyframes gridMovement {
  0% { background-position: 0 0; }
  100% { background-position: 0 300px; }
}

.cta-overlay-content {
  position: relative;
  z-index: 10;
  text-align: center;
  max-width: 650px;
}

.cta-title-text {
  font-family: 'Orbitron', sans-serif;
  font-weight: 900;
  font-size: 44px;
  color: #ffffff;
  margin-bottom: 16px;
  text-transform: uppercase;
}

.text-glow-magenta {
  text-shadow: 0 0 15px var(--neon-color-magenta);
}

.cta-sub-text {
  font-size: 16px;
  color: #e2e8f0;
}

/* Footer structure */
.retro-footer {
  background-color: #04040a;
  border-top: 2px solid var(--panel-border);
  padding: 40px 0;
}

.footer-grid-layout {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand-monogram {
  font-family: 'Orbitron', sans-serif;
  font-weight: bold;
  color: var(--neon-color-cyan);
  border: 1px solid var(--neon-color-cyan);
  padding: 4px 8px;
  font-size: 14px;
}

.footer-copy-text {
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: #4a5568;
}

.footer-system-status {
  display: flex;
  gap: 16px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: var(--neon-color-magenta);
}

.footer-nav-links {
  display: flex;
  gap: 20px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 12px;
}

.footer-nav-links a {
  color: #718096;
}

.footer-nav-links a:hover {
  color: #ffffff;
}

.margin-top-md { margin-top: 32px; }
.text-center { text-align: center; }

/* Responsive adjustments */
@media (max-width: 992px) {
  .hero-grid, .customizer-grid, .concept-showcase, .pillars-grid, .floppy-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
  .hero-text-block {
    text-align: center;
  }
  .hero-button-group {
    justify-content: center;
  }
  .retro-hero-title {
    font-size: 40px;
  }
  .customizer-preview {
    position: static;
  }
  .hidden-mobile {
    display: none !important;
  }
}
</style>
