<script setup lang="ts">
import { ref, watch } from 'vue'
import DailyStepsChart from '@/components/DailyStepsChart.vue'
import { useRoute } from 'vue-router'

const route = useRoute()

interface UserData {
  username: string
  dailySteps: Record<string, number>
}

const status = ref<'pending' | 'success' | 'error'>('pending')
const username = ref<string | null>(null)
const dailySteps = ref<{ date: Date; steps: number }[]>([])

watch(
  () => route.params.id,
  async (id) => {
    const response = await fetch(`/users/${id}.json`, { cache: 'no-store' })
    try {
      const result: UserData = await response.json()
      username.value = result.username
      dailySteps.value = Object.entries(result.dailySteps).map(
        ([date, steps]) => ({
          date: new Date(`2026/${date}`),
          steps,
        }),
      )
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
    <DailyStepsChart :daily-steps />
  </div>
</template>
