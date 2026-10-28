<script setup lang="ts">
import { Card, CardContent } from '@/components/ui/card'
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
    const response = await fetch(
      `${import.meta.env.BASE_URL}users/${id}.json`,
      { cache: 'no-store' },
    )
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
  <div v-else class="space-y-3">
    <h1 class="text-lg font-bold sm:text-xl">Hello, {{ username }}</h1>
    <Card class="shadow-none">
      <CardContent>
        <DailyStepsChart :daily-steps />
      </CardContent>
    </Card>
  </div>
</template>
