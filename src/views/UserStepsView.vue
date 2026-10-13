<script setup lang="ts">
import { type StepPoint, isPublicId, parseUserSteps } from '@/lib/steps'
import { ref, watch } from 'vue'
import StepsChart from '@/components/StepsChart.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const points = ref<StepPoint[]>([])
const username = ref('')
const lastUpdated = ref('')
const status = ref<'loading' | 'ready' | 'unavailable' | 'error'>('loading')
const retry = ref(0)

watch(
  [(): string | string[] | undefined => route.params.publicId, retry],
  async ([publicId], _previous, onCleanup): Promise<void> => {
    const controller = new AbortController()
    onCleanup(() => controller.abort())
    points.value = []
    username.value = ''
    lastUpdated.value = ''
    status.value = 'loading'
    if (typeof publicId !== 'string' || !isPublicId(publicId)) {
      status.value = 'unavailable'
      return
    }

    try {
      const dataUrl = new URL(
        `${import.meta.env.BASE_URL}user-data/${encodeURIComponent(publicId)}.json`,
        window.location.origin,
      )
      dataUrl.searchParams.set('refresh', Date.now().toString())
      const response = await fetch(dataUrl, {
        signal: controller.signal,
        cache: 'no-store',
      })
      if (controller.signal.aborted) return
      if (response.status === 404) {
        status.value = 'unavailable'
        return
      }
      if (!response.ok) {
        throw new Error(`Step data request failed (${response.status}).`)
      }
      const data: unknown = await response.json()
      if (controller.signal.aborted) return
      const user = parseUserSteps(data)
      points.value = user.points
      username.value = user.username
      lastUpdated.value = user.lastUpdated
      status.value = 'ready'
    } catch (error) {
      if (controller.signal.aborted) return
      console.error('Unable to load step data.', error)
      status.value = 'error'
    }
  },
  { immediate: true },
)
</script>

<template>
  <section>
    <p v-if="status === 'ready'" class="mb-2 text-xl">Hello, {{ username }}!</p>
    <p v-if="status === 'ready'" class="text-sm text-muted-foreground">
      Last updated: {{ lastUpdated }}
    </p>
    <p v-if="status === 'loading'" class="mt-4" role="status">
      Loading your steps...
    </p>
    <p v-else-if="status === 'unavailable'" class="mt-4" role="alert">
      This link is unavailable. Please check the personal link you received.
    </p>
    <div v-else-if="status === 'error'" class="mt-4" role="alert">
      <p>Could not load your steps. Please try again.</p>
      <button
        class="mt-2 rounded border px-3 py-1"
        type="button"
        @click="retry++"
      >
        Retry
      </button>
    </div>
    <template v-else>
      <StepsChart v-if="points.length" class="mt-4" :data="points" />
      <p v-else class="mt-4">No step data yet.</p>
    </template>
  </section>
</template>
