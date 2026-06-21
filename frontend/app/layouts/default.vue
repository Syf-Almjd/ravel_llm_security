<template>
  <div class="app-layout">
    <Sidebar />
    <main class="main-wrapper">
      <Topbar />
      <div class="content-container">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
const { fetchProfile } = useAuth()

// Fetch latest profile stats on initial load
onMounted(() => {
  fetchProfile()
})
</script>
