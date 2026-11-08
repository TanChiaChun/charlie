<script setup lang="ts">
import { computed } from 'vue'

import type { LeaderboardRecord } from '@/types/leaderboard'

const props = defineProps<{ record: LeaderboardRecord; maxSteps: number }>()

const progress = computed(() => (props.record.steps / props.maxSteps) * 100)
</script>

<template>
  <div class="flex items-center gap-4">
    <span
      class="text-muted-foreground w-5 text-center text-lg font-semibold tabular-nums"
      >{{ record.rank }}</span
    >

    <div class="flex-1 space-y-1">
      <div class="flex items-center justify-between gap-3">
        <span class="font-medium sm:text-lg">{{ record.username }}</span>
        <span class="text-muted-foreground tabular-nums">{{
          record.steps.toLocaleString()
        }}</span>
      </div>

      <div class="bg-muted h-2 rounded-full">
        <div
          class="bg-brand h-full rounded-full"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>
