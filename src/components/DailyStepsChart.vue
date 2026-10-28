<script setup lang="ts">
import {
  ChartContainer,
  ChartCrosshair,
  ChartTooltip,
  ChartTooltipContent,
  componentToString,
} from '@/components/ui/chart'
import { VisAxis, VisGroupedBar, VisXYContainer } from '@unovis/vue'
import type { ChartConfig } from '@/components/ui/chart'

interface Data {
  date: Date
  steps: number
}

defineProps<{ dailySteps: Data[] }>()

const MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000
const chartConfig = {
  steps: {
    label: 'steps',
  },
} satisfies ChartConfig
</script>

<template>
  <ChartContainer :config="chartConfig">
    <VisXYContainer :data="dailySteps">
      <VisGroupedBar
        :x="(d: Data) => d.date"
        :y="(d: Data) => d.steps"
        :data-step="MILLISECONDS_PER_DAY"
      />

      <VisAxis
        type="x"
        :tick-format="(d: number) => new Date(d).getDate()"
        :tick-values="dailySteps.map((d) => d.date)"
        :grid-line="false"
      />
      <VisAxis type="y" />

      <ChartTooltip />
      <ChartCrosshair
        :template="
          componentToString(chartConfig, ChartTooltipContent, {
            labelFormatter(d) {
              return new Date(d).toLocaleDateString('en-SG', {
                day: 'numeric',
                month: 'short',
              })
            },
          })
        "
      />
    </VisXYContainer>
  </ChartContainer>
</template>
