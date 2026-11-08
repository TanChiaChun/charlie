<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import DailyStepsChart from '@/components/DailyStepsChart.vue'
import PageHeader from '@/components/PageHeader.vue'
import StatsCard from '@/components/StatsCard.vue'
import { Card, CardContent } from '@/components/ui/card'

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
    longest5kStreakRank: number | null
    longest5kStreakStart: string | null
    longest5kStreakEnd: string | null
    current5kStreak: number
    current5kStreakStart: string | null
    current5kStreakEnd: string | null
  }
}

const status = ref<'pending' | 'success' | 'error'>('pending')
const userData = ref<UserData | null>(null)

const lastFetch = computed(() =>
  userData.value?.lastFetch ? new Date(userData.value.lastFetch) : null,
)
const dailySteps = computed(() =>
  Object.entries(userData.value?.dailySteps ?? {}).map(([date, steps]) => ({
    date: new Date(`2026/${date}`),
    steps,
  })),
)
const weeklyAverage = computed(() =>
  Math.floor(userData.value?.stats.weeklyAverage ?? 0),
)
const todaySteps = computed(
  () =>
    dailySteps.value.find(
      ({ date }) =>
        date.getMonth() === lastFetch.value?.getMonth() &&
        date.getDate() === lastFetch.value?.getDate(),
    )?.steps ?? 0,
)
const weekRange = computed(() => {
  if (!lastFetch.value) {
    return ''
  }

  const end = lastFetch.value
  const day = end.getDay()
  const start = new Date(end)
  start.setDate(start.getDate() - (day === 0 ? 6 : day - 1))

  return `${formatDate(start)} - ${formatDate(end)}`
})
const longest5kStreakRange = computed(() => {
  const { longest5kStreakStart, longest5kStreakEnd } =
    userData.value?.stats ?? {}

  return formatDateRange(longest5kStreakStart, longest5kStreakEnd)
})
const current5kStreakRange = computed(() => {
  const { current5kStreakStart, current5kStreakEnd } =
    userData.value?.stats ?? {}

  return formatDateRange(current5kStreakStart, current5kStreakEnd)
})

function formatDate(date: Date): string {
  return date.toLocaleDateString('en-SG', {
    day: 'numeric',
    month: 'short',
  })
}
function formatDateRange(
  start: string | null | undefined,
  end: string | null | undefined,
): string {
  if (!start || !end) {
    return ''
  }

  return `${formatDate(new Date(start))} - ${formatDate(new Date(end))}`
}

async function loadUserData(id: string): Promise<void> {
  status.value = 'pending'
  userData.value = null

  try {
    const response = await fetch(
      `${import.meta.env.BASE_URL}users/${id}.json`,
      { cache: 'no-store' },
    )
    if (!response.ok) {
      throw new Error(`Failed to fetch user data: ${response.status}`)
    }

    userData.value = await response.json()
    status.value = 'success'
  } catch {
    userData.value = null
    status.value = 'error'
  }
}

watch(
  () => route.params.id,
  (id) => {
    if (typeof id !== 'string') {
      status.value = 'error'
      return
    }

    loadUserData(id)
  },
  { immediate: true },
)
</script>

<template>
  <div v-if="status === 'pending'">Loading...</div>
  <div v-else-if="status === 'error'">Failed to load user data.</div>
  <div v-else-if="userData" class="space-y-5">
    <PageHeader
      :title="`Hello, ${userData.username}`"
      :last-updated="lastFetch ?? undefined"
    />

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <StatsCard
        title="Today"
        :value="todaySteps"
        unit="steps"
        :rank="userData.stats.dailyRank"
      />
      <StatsCard
        title="This Week"
        :value="weeklyAverage"
        unit="steps/day"
        :rank="userData.stats.weeklyRank"
        :subtitle="weekRange"
      />
    </div>

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <StatsCard
        title="Current 5K Streak"
        :value="userData.stats.current5kStreak"
        unit="days"
        :subtitle="current5kStreakRange"
      />
      <StatsCard
        title="Longest 5K Streak"
        :value="userData.stats.longest5kStreak"
        unit="days"
        :rank="userData.stats.longest5kStreakRank"
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
