<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  lastUpdated?: Date
  subtitle?: string
  title: string
}>()

const formattedLastUpdated = computed(() =>
  props.lastUpdated?.toLocaleString('en-SG', {
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    month: 'short',
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
