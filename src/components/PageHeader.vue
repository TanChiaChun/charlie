<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  subtitle?: string
  lastUpdated?: Date
}>()

const formattedLastUpdated = computed(() =>
  props.lastUpdated?.toLocaleString('en-SG', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }),
)
</script>

<template>
  <div>
    <h1 class="text-lg font-bold sm:text-xl">{{ title }}</h1>
    <p v-if="subtitle" class="text-muted-foreground text-xs sm:text-sm">
      {{ subtitle }}
    </p>
    <p
      v-if="formattedLastUpdated"
      class="text-muted-foreground text-xs sm:text-sm"
    >
      Last updated: {{ formattedLastUpdated }}
    </p>
  </div>
</template>
