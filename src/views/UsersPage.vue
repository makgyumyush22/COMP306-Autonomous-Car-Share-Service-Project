<template>
  <div>
    <h2>Users</h2>
    <div v-if="error" style="color: red">{{ error }}</div>
    <ul v-else>
      <li v-for="user in users" :key="user.user_id">
        {{ user.user_id }} - {{ user.user_name }}
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'

interface User {
  user_id: number
  user_name: string
}

export default defineComponent({
  setup() {
    const users = ref<User[]>([])
    const error = ref<string | null>(null)

    onMounted(async () => {
      try {
        const res = await fetch('http://localhost:5000/users')
        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`)
        users.value = await res.json()
      } catch (e) {
        error.value = 'Failed to load users.'
      }
    })

    return { users, error }
  },
})
</script>

<style scoped>
h2 {
  margin-bottom: 10px;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  padding: 4px 0;
}
</style>
