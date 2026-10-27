<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const status = ref<'pending' | 'success' | 'error'>('pending')
const username = ref<string | null>(null)

watch(
  () => route.params.id,
  async (id) => {
    const response = await fetch(`/users/${id}.json`)
    try {
      const result = await response.json()
      username.value = result.username
      status.value = 'success'
    } catch {
      status.value = 'error'
    }
  },
  { immediate: true },
)
</script>

<template>
  <div v-if="status === 'pending'">Loading...</div>
  <div v-else-if="status === 'error'">Failed to load user data.</div>
  <div v-else>
    <h1>Hello, {{ username }}</h1>
  </div>
</template>
