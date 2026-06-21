<template>
  <div class="empty-layout">
    <slot />
  </div>
</template>

<style scoped>
.empty-layout {
  min-height: 100vh;
  background-color: var(--bg-secondary);
}
</style>
