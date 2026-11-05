<script setup lang="ts">
import { VisAxis, VisGroupedBar, VisXYContainer } from '@unovis/vue'
import { computed } from 'vue'

import type { ChartConfig } from '@/components/ui/chart'
import {
  ChartContainer,
  ChartCrosshair,
  ChartTooltip,
  ChartTooltipContent,
  componentToString,
} from '@/components/ui/chart'

interface Data {
  date: Date
  steps: number
}

const props = defineProps<{ data: Data[] }>()

const MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000
const chartConfig = {
  steps: {
    label: 'steps',
  },
} satisfies ChartConfig

const tickValues = computed(() => props.data.map((d) => d.date))

const x = (d: Data): Date => d.date
const y = (d: Data): number => d.steps
const tickFormat = (d: number): number => new Date(d).getDate()
</script>

<template>
  <ChartContainer :config="chartConfig">
    <VisXYContainer :data>
      <VisGroupedBar :x :y :data-step="MILLISECONDS_PER_DAY" />

      <VisAxis type="x" :tick-format :tick-values :grid-line="false" />
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
