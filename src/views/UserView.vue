<script setup lang="ts">
import { Card, CardContent } from '@/components/ui/card'
import { computed, ref, watch } from 'vue'
import DailyStepsChart from '@/components/DailyStepsChart.vue'
import StatsCard from '@/components/StatsCard.vue'
import { useRoute } from 'vue-router'

const route = useRoute()

interface UserData {
  username: string
  lastFetch: string
  dailySteps: Record<string, number>
  stats: {
    dailyRank: number | null
    weeklyAverage: number
    weeklyRank: number | null
    longest5kStreak: number
    longest5kStreakRank: number
    longest5kStreakStart: string | null
    longest5kStreakEnd: string | null
    current5kStreak: number
    current5kStreakStart: string | null
    current5kStreakEnd: string | null
  }
}

const status = ref<'pending' | 'success' | 'error'>('pending')
const username = ref<string | null>(null)
const lastFetch = ref<Date | null>(null)
const dailySteps = ref<{ date: Date; steps: number }[]>([])
const dailyRank = ref<number | null>(null)
const weeklyAverage = ref<number>(0)
const weeklyRank = ref<number | null>(null)
const longest5kStreak = ref<number>(0)
const longest5kStreakRank = ref<number>(0)
const longest5kStreakStart = ref<Date | null>(null)
const longest5kStreakEnd = ref<Date | null>(null)
const current5kStreak = ref<number>(0)
const current5kStreakStart = ref<Date | null>(null)
const current5kStreakEnd = ref<Date | null>(null)

const formattedLastFetch = computed(() => {
  if (!lastFetch.value) {
    return ''
  }

  return lastFetch.value.toLocaleString('en-SG', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
})
const todaySteps = computed(() => {
  return (
    dailySteps.value.find(
      ({ date }) =>
        date.getMonth() === lastFetch.value?.getMonth() &&
        date.getDate() === lastFetch.value?.getDate(),
    )?.steps ?? 0
  )
})
const weekRange = computed(() => {
  if (!lastFetch.value) {
    return ''
  }

  const end = lastFetch.value
  const day = end.getDay()
  const start = new Date(end)
  start.setDate(start.getDate() - (day === 0 ? 6 : day - 1))

  const formatDate = (date: Date): string =>
    date.toLocaleDateString('en-SG', {
      day: 'numeric',
      month: 'short',
    })

  return `${formatDate(start)} - ${formatDate(end)}`
})
const longest5kStreakRange = computed(() =>
  formatDateRange(longest5kStreakStart.value, longest5kStreakEnd.value),
)
const current5kStreakRange = computed(() =>
  formatDateRange(current5kStreakStart.value, current5kStreakEnd.value),
)

function formatDateRange(start: Date | null, end: Date | null): string {
  if (!start || !end) {
    return ''
  }

  const formatDate = (date: Date): string =>
    date.toLocaleDateString('en-SG', {
      day: 'numeric',
      month: 'short',
    })

  return `${formatDate(start)} - ${formatDate(end)}`
}

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
      lastFetch.value = new Date(result.lastFetch)
      dailySteps.value = Object.entries(result.dailySteps).map(
        ([date, steps]) => ({
          date: new Date(`2026/${date}`),
          steps,
        }),
      )
      dailyRank.value = result.stats.dailyRank
      weeklyAverage.value = Math.floor(result.stats.weeklyAverage)
      weeklyRank.value = result.stats.weeklyRank
      longest5kStreak.value = result.stats.longest5kStreak
      longest5kStreakRank.value = result.stats.longest5kStreakRank
      longest5kStreakStart.value = result.stats.longest5kStreakStart
        ? new Date(result.stats.longest5kStreakStart)
        : null
      longest5kStreakEnd.value = result.stats.longest5kStreakEnd
        ? new Date(result.stats.longest5kStreakEnd)
        : null
      current5kStreak.value = result.stats.current5kStreak
      current5kStreakStart.value = result.stats.current5kStreakStart
        ? new Date(result.stats.current5kStreakStart)
        : null
      current5kStreakEnd.value = result.stats.current5kStreakEnd
        ? new Date(result.stats.current5kStreakEnd)
        : null

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
  <div v-else class="space-y-5">
    <div>
      <h1 class="text-lg font-bold sm:text-xl">Hello, {{ username }}</h1>
      <p class="text-muted-foreground text-xs sm:text-sm">
        Last updated: {{ formattedLastFetch }}
      </p>
    </div>

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <StatsCard
        title="Today"
        :value="todaySteps"
        unit="steps"
        :rank="dailyRank"
      />
      <StatsCard
        title="This Week"
        :value="weeklyAverage"
        unit="steps/day"
        :rank="weeklyRank"
        :subtitle="weekRange"
      />
    </div>

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <StatsCard
        title="Current 5K Streak"
        :value="current5kStreak"
        unit="days"
        :subtitle="current5kStreakRange"
      />
      <StatsCard
        title="Longest 5K Streak"
        :value="longest5kStreak"
        unit="days"
        :rank="longest5kStreakRank"
        :subtitle="longest5kStreakRange"
      />
    </div>

    <Card class="shadow-none">
      <CardContent>
        <DailyStepsChart :daily-steps />
      </CardContent>
    </Card>
  </div>
</template>
