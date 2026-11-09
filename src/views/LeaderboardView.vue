<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import LeaderboardItem from '@/components/LeaderboardItem.vue'
import PageHeader from '@/components/PageHeader.vue'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type {
  LeaderboardRecord,
  PeriodLeaderboardRecord,
} from '@/types/leaderboard'

interface LeaderboardData {
  lastFetch: string
  daily: Record<string, LeaderboardRecord[]>
  weekly: Record<string, PeriodLeaderboardRecord[]>
}

const status = ref<'pending' | 'success' | 'error'>('pending')
const leaderboardData = ref<LeaderboardData | null>(null)
const selectedPeriod = ref<'daily' | 'weekly'>('daily')

const lastUpdated = computed(() =>
  leaderboardData.value?.lastFetch
    ? new Date(leaderboardData.value.lastFetch)
    : undefined,
)
const latestDate = computed(() => {
  const data = leaderboardData.value?.[selectedPeriod.value] ?? {}
  const dates = Object.keys(data).sort().reverse()

  return dates.find(
    (date) => data[date] !== undefined && data[date]?.length > 0,
  )
})
const formattedLatestDate = computed(() => {
  const formatDate = (date: Date): string =>
    date.toLocaleDateString('en-SG', { day: 'numeric', month: 'short' })

  if (!latestDate.value || !lastUpdated.value) {
    return ''
  }

  const startDate = new Date(latestDate.value)
  if (selectedPeriod.value === 'daily') {
    return formatDate(startDate)
  }

  const weekEnd = new Date(startDate)
  weekEnd.setDate(weekEnd.getDate() + 6)
  const endDate = weekEnd < lastUpdated.value ? weekEnd : lastUpdated.value

  return `${formatDate(startDate)} - ${formatDate(endDate)}`
})
const latestRecords = computed(() => {
  if (!latestDate.value) {
    return []
  }

  if (selectedPeriod.value === 'daily') {
    return leaderboardData.value?.daily[latestDate.value] ?? []
  }
  return (
    leaderboardData.value?.weekly[latestDate.value]?.map(
      ({ rank, averageSteps, username }) => ({
        rank,
        steps: Math.floor(averageSteps),
        username,
      }),
    ) ?? []
  )
})
const maxSteps = computed(() => latestRecords.value.at(0)?.steps ?? 1)

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

    <Tabs v-model="selectedPeriod">
      <TabsList class="w-full">
        <TabsTrigger value="daily">Daily</TabsTrigger>
        <TabsTrigger value="weekly">Weekly</TabsTrigger>
      </TabsList>
    </Tabs>

    <div class="flex items-center justify-between">
      <h2 class="font-semibold capitalize sm:text-lg">{{ selectedPeriod }}</h2>
      <span class="text-muted-foreground text-sm">{{
        formattedLatestDate
      }}</span>
    </div>

    <div class="flex flex-col gap-6 sm:gap-7" data-testid="leaderboard">
      <LeaderboardItem
        v-for="record in latestRecords"
        :key="record.username"
        :record="record"
        :max-steps="maxSteps"
      />
    </div>
  </div>
</template>
