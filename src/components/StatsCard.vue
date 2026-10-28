<script setup lang="ts">
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

defineProps<{
  title: string
  value: number
  rank: number | null
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
      <p class="text-2xl font-bold sm:text-3xl">{{ value.toLocaleString() }}</p>
      <p v-if="rank" class="text-muted-foreground text-xs sm:text-sm">
        Rank
        <span class="text-foreground font-medium">#{{ rank }}</span>
      </p>
    </CardContent>
  </Card>
</template>
