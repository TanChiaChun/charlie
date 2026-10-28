<script setup lang="ts">
import { VisGroupedBar, VisXYContainer } from '@unovis/vue'
import type { ChartConfig } from '@/components/ui/chart'
import { ChartContainer } from '@/components/ui/chart'

interface Data {
  date: Date
  steps: number
}

const props = defineProps<{ dailySteps: Data[] }>()

const MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000
const chartConfig = {} satisfies ChartConfig
</script>

<template>
  <ChartContainer :config="chartConfig">
    <VisXYContainer :data="props.dailySteps">
      <VisGroupedBar
        :x="(d: Data) => d.date"
        :y="(d: Data) => d.steps"
        :data-step="MILLISECONDS_PER_DAY"
      />
    </VisXYContainer>
  </ChartContainer>
</template>
