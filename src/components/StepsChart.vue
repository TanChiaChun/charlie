<script setup lang="ts">
import {
  ChartContainer,
  ChartCrosshair,
  ChartTooltip,
  ChartTooltipContent,
  componentToString,
} from '@/components/ui/chart'
import { VisAxis, VisGroupedBar, VisXYContainer } from '@unovis/vue'
import type { StepPoint } from '@/lib/steps'

const chartConfig = {
  steps: {
    label: 'Steps',
  },
}
const props = defineProps<{ data: StepPoint[] }>()
const dateFormat = new Intl.DateTimeFormat('en', {
  month: 'short',
  day: 'numeric',
})
</script>

<template>
  <ChartContainer :config="chartConfig">
    <VisXYContainer :data="props.data">
      <VisGroupedBar
        :x="(d: StepPoint) => d.date.getTime()"
        :y="(d: StepPoint) => d.steps"
        :data-step="24 * 60 * 60 * 1000"
        :group-padding="0.2"
        :group-max-width="80"
      />
      <VisAxis
        type="x"
        :x="(d: StepPoint) => d.date.getTime()"
        :tick-format="(d: number) => dateFormat.format(new Date(d))"
        :tick-values="props.data.map((d) => d.date.getTime())"
        label="Date"
        :grid-line="false"
      />
      <VisAxis type="y" :tick-format="(d: number) => d" label="Steps" />
      <ChartTooltip />
      <ChartCrosshair
        :x="(d: StepPoint) => d.date.getTime()"
        :y="(d: StepPoint) => d.steps"
        :template="
          componentToString(chartConfig, ChartTooltipContent, {
            hideLabel: true,
          })
        "
      />
    </VisXYContainer>
  </ChartContainer>
</template>
