<template>
  <Transition name="fade">
    <div v-if="dialog && dialog.isOpen" class="modal-dialog-overlay" @click.self="handleCancel">
      <div class="modal-dialog-card card animate-scale-in">
        <div class="modal-dialog-header">
          <div class="modal-dialog-icon-wrapper" :class="dialog.type">
            <!-- Alert Icon -->
            <svg v-if="dialog.type === 'alert'" class="svg-icon" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <!-- Confirm/Shield Icon -->
            <svg v-else class="svg-icon" viewBox="0 0 24 24">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <h3 class="modal-dialog-title">{{ dialog.title }}</h3>
        </div>
        <div class="modal-dialog-body">
          <p>{{ dialog.message }}</p>
        </div>
        <div class="modal-dialog-actions">
          <button 
            v-if="dialog.type === 'confirm'" 
            class="btn btn-secondary hover-lift" 
            @click="handleCancel"
          >
            Cancel
          </button>
          <button 
            class="btn btn-primary hover-lift" 
            @click="handleConfirm"
          >
            {{ dialog.type === 'confirm' ? 'Confirm' : 'OK' }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
const { dialog } = useStore()

const handleConfirm = () => {
  if (dialog.value.resolve) {
    dialog.value.resolve(true)
  }
}

const handleCancel = () => {
  if (dialog.value.resolve) {
    dialog.value.resolve(false)
  }
}
</script>

<style scoped>
.modal-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 24px;
}

.modal-dialog-card {
  width: 100%;
  max-width: 440px;
  padding: 24px;
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-dialog-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-dialog-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.modal-dialog-icon-wrapper.alert {
  color: var(--brand-primary);
}

.modal-dialog-icon-wrapper.confirm {
  color: var(--brand-primary);
}

.modal-dialog-icon-wrapper .svg-icon {
  width: 20px;
  height: 20px;
}

.modal-dialog-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.modal-dialog-body {
  font-size: 13.5px;
  line-height: 1.5;
  color: var(--text-secondary);
}

.modal-dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.animate-scale-in {
  animation: scaleIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
