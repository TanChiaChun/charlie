<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import LeaderboardItem from '@/components/LeaderboardItem.vue'
import type { LeaderboardRecord } from '@/types/leaderboard'

interface LeaderboardData {
  daily: Record<string, LeaderboardRecord[]>
}

const status = ref<'pending' | 'success' | 'error'>('pending')
const leaderboardData = ref<LeaderboardData | null>(null)

const latestDailyRecords = computed(() => {
  const daily = leaderboardData.value?.daily ?? {}
  const dates = Object.keys(daily).sort().reverse()

  return (
    dates
      .map((date) => daily[date])
      .find((records) => records !== undefined && records.length > 0) ?? []
  )
})
const maxDailySteps = computed(() => latestDailyRecords.value[0]?.steps ?? 1)

onMounted(async () => {
  try {
    const response = await fetch(
      `${import.meta.env.BASE_URL}leaderboard.json`,
      {
        cache: 'no-store',
      },
    )
    if (!response.ok) {
      throw new Error(`Failed to fetch leaderboard data: ${response.status}`)
    }

    leaderboardData.value = await response.json()
    status.value = 'success'
  } catch {
    status.value = 'error'
  }
})
</script>

<template>
  <div v-if="status === 'pending'">Loading...</div>
  <div v-else-if="status === 'error'">Failed to load leaderboard data.</div>
  <div v-else class="flex flex-col gap-6 sm:gap-7" data-testid="leaderboard">
    <LeaderboardItem
      v-for="record in latestDailyRecords"
      :key="record.username"
      :record="record"
      :max-steps="maxDailySteps"
    />
  </div>
</template>
