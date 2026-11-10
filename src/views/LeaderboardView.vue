<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import LeaderboardItem from '@/components/LeaderboardItem.vue'
import PageHeader from '@/components/PageHeader.vue'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type {
  DailyLeaderboardRecord,
  PeriodLeaderboardRecord,
  Streak5kLeaderboardRecord,
} from '@/types/leaderboard'

interface LeaderboardData {
  lastFetch: string
  daily: Record<string, DailyLeaderboardRecord[]>
  weekly: Record<string, PeriodLeaderboardRecord[]>
  streaks5k: Streak5kLeaderboardRecord[]
}

const periodTitles = {
  daily: 'Daily',
  weekly: 'Weekly',
  streaks5k: '5K Streak',
}

const status = ref<'pending' | 'success' | 'error'>('pending')
const leaderboardData = ref<LeaderboardData | null>(null)
const selectedPeriod = ref<'daily' | 'weekly' | 'streaks5k'>('daily')

const lastUpdated = computed(() =>
  leaderboardData.value?.lastFetch
    ? new Date(leaderboardData.value.lastFetch)
    : undefined,
)
const latestDateString = computed(() => {
  if (selectedPeriod.value === 'streaks5k') {
    return leaderboardData.value?.lastFetch.slice(0, 10)
  }

  const data = leaderboardData.value?.[selectedPeriod.value] ?? {}
  const dates = Object.keys(data).sort().reverse()

  return dates.find(
    (date) => data[date] !== undefined && data[date]?.length > 0,
  )
})
const latestDate = computed(() =>
  latestDateString.value ? new Date(latestDateString.value) : undefined,
)
const formattedLatestDate = computed(() => {
  const formatDate = (date: Date): string =>
    date.toLocaleDateString('en-SG', { day: 'numeric', month: 'short' })

  if (!latestDate.value) {
    return ''
  }

  switch (selectedPeriod.value) {
    case 'daily':
      return formatDate(latestDate.value)

    case 'weekly':
      if (!lastUpdated.value) {
        return ''
      }
      const weekFullEndDate = new Date(latestDate.value)
      weekFullEndDate.setDate(weekFullEndDate.getDate() + 6)
      const weekEndDate =
        weekFullEndDate < lastUpdated.value
          ? weekFullEndDate
          : lastUpdated.value
      return `${formatDate(latestDate.value)} - ${formatDate(weekEndDate)}`

    case 'streaks5k':
      const minDate = new Date(2026, 9, 12)
      return `${formatDate(minDate)} - ${formatDate(latestDate.value)}`

    default:
      return ''
  }
})
const latestRecords = computed(() => {
  switch (selectedPeriod.value) {
    case 'daily':
      if (!latestDateString.value) {
        return undefined
      }
      const dailyRecords = leaderboardData.value?.daily[latestDateString.value]
      return dailyRecords?.map(({ rank, steps, username }) => ({
        rank,
        value: steps,
        username,
      }))

    case 'weekly':
      if (!latestDateString.value) {
        return undefined
      }
      const weeklyRecords =
        leaderboardData.value?.weekly[latestDateString.value]
      return weeklyRecords?.map(({ rank, averageSteps, username }) => ({
        rank,
        value: Math.floor(averageSteps),
        username,
      }))

    case 'streaks5k':
      const streaks5kRecords = leaderboardData.value?.streaks5k
      return streaks5kRecords?.map(({ rank, days, username }) => ({
        rank,
        value: days,
        username,
      }))

    default:
      return undefined
  }
})
const maxValue = computed(() => latestRecords.value?.at(0)?.value ?? 1)

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
        <TabsTrigger value="streaks5k">5K Streak</TabsTrigger>
      </TabsList>
    </Tabs>

    <div class="flex items-center justify-between">
      <h2 class="font-semibold sm:text-lg">
        {{ periodTitles[selectedPeriod] }}
      </h2>
      <span class="text-muted-foreground text-sm">{{
        formattedLatestDate
      }}</span>
    </div>

    <div class="flex flex-col gap-6 sm:gap-7" data-testid="leaderboard">
      <LeaderboardItem
        v-for="record in latestRecords"
        :key="record.username"
        :record="record"
        :max-value="maxValue"
      />
    </div>
  </div>
</template>
