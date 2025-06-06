<template>
  <div class="app-container">
    <header class="app-header">
      <button @click="$router.push('/cars')">Cars</button>
      <button @click="$router.push('/users')">Users</button>
    </header>

    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<script lang="ts">
export default {}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  background-color: #f0f0f0;
  padding: 10px 20px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  z-index: 100;
}

.app-header button {
  margin-right: 10px;
  padding: 8px 16px;
  cursor: pointer;
}

.app-content {
  margin-left: 40px;
  margin-top: 20px;
  max-width: 800px;
}
</style>
