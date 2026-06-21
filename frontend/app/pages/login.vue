<template>
  <div class="auth-page grid-mesh">
    <div class="auth-card card framer-appear">
      <div class="auth-header">
        <div class="auth-logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h2>Sign In to Ravel</h2>
        <p class="auth-tagline">Access your zero-trust gateway workspace</p>
      </div>

      <!-- Error alert -->
      <div v-if="errorMsg" class="alert alert-danger">
        <span>⚠️ {{ errorMsg }}</span>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label class="form-label" for="email">Email Address</label>
          <input
            v-model="form.email"
            type="email"
            id="email"
            class="form-control"
            placeholder="you@company.com"
            required
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="password">Password</label>
          <input
            v-model="form.password"
            type="password"
            id="password"
            class="form-control"
            placeholder="••••••••"
            required
            :disabled="isLoading"
          />
        </div>

        <button type="submit" class="btn btn-primary w-full" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span>{{ isLoading ? 'Authenticating...' : 'Sign In' }}</span>
        </button>
      </form>

      <div class="auth-footer">
        <span>Don't have an account?</span>
        <NuxtLink to="/register" class="auth-link">Register here</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

definePageMeta({
  layout: 'empty'
})

const { login } = useAuth()

const form = reactive({
  email: '',
  password: ''
})

const isLoading = ref(false)
const errorMsg = ref('')

const handleSubmit = async () => {
  isLoading.value = true
  errorMsg.value = ''
  
  const result = await login(form.email, form.password)
  
  if (result.success) {
    navigateTo('/dashboard')
  } else {
    errorMsg.value = result.error
  }
  
  isLoading.value = false
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-secondary);
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 40px 32px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background-color: var(--text-primary);
  color: var(--bg-primary);
  border-radius: var(--radius);
  margin-bottom: 16px;
}

.auth-logo svg {
  width: 24px;
  height: 24px;
  stroke: var(--bg-primary);
}

.auth-tagline {
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 4px;
}

.w-full {
  width: 100%;
}

.alert {
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  margin-bottom: 20px;
}

.alert-danger {
  background-color: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 13.5px;
  color: var(--text-secondary);
  display: flex;
  justify-content: center;
  gap: 6px;
}

.auth-link {
  color: var(--brand-primary);
  font-weight: 600;
}

.auth-link:hover {
  text-decoration: underline;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
