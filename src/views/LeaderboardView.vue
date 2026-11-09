<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import LeaderboardItem from '@/components/LeaderboardItem.vue'
import PageHeader from '@/components/PageHeader.vue'
import type { LeaderboardRecord } from '@/types/leaderboard'

interface LeaderboardData {
  lastFetch: string
  daily: Record<string, LeaderboardRecord[]>
}

const status = ref<'pending' | 'success' | 'error'>('pending')
const leaderboardData = ref<LeaderboardData | null>(null)

const lastUpdated = computed(() =>
  leaderboardData.value?.lastFetch
    ? new Date(leaderboardData.value.lastFetch)
    : undefined,
)
const latestDate = computed(() => {
  const daily = leaderboardData.value?.daily ?? {}
  const dates = Object.keys(daily).sort().reverse()

  return dates.find(
    (date) => daily[date] !== undefined && daily[date]?.length > 0,
  )
})
const formattedLatestDate = computed(() => {
  if (!latestDate.value) {
    return ''
  }

  return new Date(latestDate.value).toLocaleDateString('en-SG', {
    day: 'numeric',
    month: 'short',
  })
})
const latestDailyRecords = computed(() =>
  latestDate.value ? leaderboardData.value?.daily[latestDate.value] : [],
)
const maxDailySteps = computed(
  () => latestDailyRecords.value?.at(0)?.steps ?? 1,
)

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
  <div v-else class="space-y-5">
    <PageHeader title="Leaderboard" :last-updated />

    <div class="flex items-center justify-between">
      <h2 class="font-semibold sm:text-lg">Daily</h2>
      <span class="text-muted-foreground text-sm">{{
        formattedLatestDate
      }}</span>
    </div>

    <div class="flex flex-col gap-6 sm:gap-7" data-testid="leaderboard">
      <LeaderboardItem
        v-for="record in latestDailyRecords"
        :key="record.username"
        :record="record"
        :max-steps="maxDailySteps"
      />
    </div>
  </div>
</template>
