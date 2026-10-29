<script setup lang="ts">
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

defineProps<{
  title: string
  value: number
  unit: string
  rank: number | null
  subtitle?: string
}>()
</script>

<template>
  <Card class="gap-0 py-4 shadow-none sm:py-5">
    <CardHeader class="px-4 sm:px-5">
      <CardTitle class="text-muted-foreground text-xs font-medium sm:text-sm">{{
        title
      }}</CardTitle>
    </CardHeader>
    <CardContent class="px-4 sm:px-5">
      <div class="flex items-baseline gap-1">
        <p class="text-2xl font-bold sm:text-3xl">
          {{ value.toLocaleString() }}
        </p>
        <span class="text-muted-foreground text-xs sm:text-sm">{{ unit }}</span>
      </div>
      <div
        class="text-muted-foreground flex items-baseline justify-between text-xs sm:text-sm"
      >
        <p v-if="rank">
          Rank
          <span class="text-foreground font-medium">#{{ rank }}</span>
        </p>
        <span v-if="subtitle" class="text-xs">{{ subtitle }}</span>
      </div>
    </CardContent>
  </Card>
</template>
