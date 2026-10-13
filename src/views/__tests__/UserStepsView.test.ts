import { type VueWrapper, flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import App from '@/App.vue'
import NotFoundView from '../NotFoundView.vue'
import UserStepsView from '../UserStepsView.vue'

vi.mock('@/components/StepsChart.vue', async () => {
  const { defineComponent } = await import('vue')
  return {
    default: defineComponent({
      props: ['data'],
      template: '<div data-test="chart">{{ JSON.stringify(data) }}</div>',
    }),
  }
})

const fetchMock = vi.fn<typeof fetch>()
let wrapper: VueWrapper | undefined

beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock)
  fetchMock.mockReset()
})

afterEach(() => {
  wrapper?.unmount()
  wrapper = undefined
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

async function open(
  path = '/users/aaaaaaaa',
): Promise<ReturnType<typeof createRouter>> {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/users/:publicId', component: UserStepsView },
      { path: '/:pathMatch(.*)*', component: NotFoundView },
    ],
  })
  await router.push(path)
  await router.isReady()
  wrapper = mount(App, { global: { plugins: [router] } })
  return router
}

describe('personal step pages', () => {
  it('fetches only the selected user and reacts to route changes', async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          username: 'Alice',
          dailySteps: { '10/01': 123 },
          lastUpdated: '20261013080502',
        }),
      ),
    )
    const router = await open()
    expect(wrapper?.text()).toContain('Loading')
    await flushPromises()
    expect(wrapper?.get('[data-test="chart"]').text()).toContain('"steps":123')
    expect(wrapper?.text()).toContain('Hello, Alice!')
    expect(wrapper?.text()).toContain('Last updated: 2026-10-13 08:05:02')
    expect(fetchMock).toHaveBeenCalledWith(
      '/user-data/aaaaaaaa.json',
      expect.any(Object),
    )
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          username: 'Bob',
          dailySteps: { '10/02': 456 },
          lastUpdated: '20261013090502',
        }),
      ),
    )
    await router.push('/users/bbbbbbbb')
    expect(wrapper?.find('[data-test="chart"]').exists()).toBe(false)
    expect(wrapper?.text()).not.toContain('Hello, Alice!')
    expect(wrapper?.text()).not.toContain('Last updated:')
    await flushPromises()
    expect(wrapper?.get('[data-test="chart"]').text()).toContain('"steps":456')
    expect(wrapper?.text()).not.toContain('"steps":123')
    expect(wrapper?.text()).toContain('Hello, Bob!')
    expect(wrapper?.text()).toContain('Last updated: 2026-10-13 09:05:02')
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('ignores late responses from the previous user', async () => {
    let resolveFirst!: (value: Response) => void
    fetchMock.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveFirst = resolve
        }),
    )
    const router = await open()
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          username: 'Bob',
          dailySteps: { '10/02': 456 },
          lastUpdated: '20261013080502',
        }),
      ),
    )
    await router.push('/users/bbbbbbbb')
    await flushPromises()
    resolveFirst(
      new Response(
        JSON.stringify({
          username: 'Alice',
          dailySteps: { '10/01': 123 },
          lastUpdated: '20261013080502',
        }),
      ),
    )
    await flushPromises()
    expect(wrapper?.get('[data-test="chart"]').text()).toContain('"steps":456')
    expect(wrapper?.text()).toContain('Hello, Bob!')
    expect(wrapper?.text()).not.toContain('Alice')
  })

  it('does not request malformed IDs', async () => {
    await open('/users/invalid')
    await flushPromises()
    expect(wrapper?.text()).toContain('link is unavailable')
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('handles missing users', async () => {
    fetchMock.mockResolvedValue(new Response('', { status: 404 }))
    await open()
    await flushPromises()
    expect(wrapper?.text()).toContain('link is unavailable')
    expect(wrapper?.find('button').exists()).toBe(false)
  })

  it('handles empty data', async () => {
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({
          username: 'Alice',
          dailySteps: {},
          lastUpdated: '20261013080502',
        }),
      ),
    )
    await open()
    await flushPromises()
    expect(wrapper?.text()).toContain('No step data yet')
    expect(wrapper?.text()).toContain('Hello, Alice!')
  })

  it.each(['network', 'http', 'json', 'shape'])(
    'shows errors and supports retry: %s',
    async (failure) => {
      const log = vi.spyOn(console, 'error').mockImplementation(() => {})
      if (failure === 'network')
        fetchMock.mockRejectedValueOnce(new Error('Offline'))
      if (failure === 'http')
        fetchMock.mockResolvedValueOnce(new Response('', { status: 500 }))
      if (failure === 'json')
        fetchMock.mockResolvedValueOnce(new Response('<html>'))
      if (failure === 'shape')
        fetchMock.mockResolvedValueOnce(new Response('[]'))
      await open()
      await flushPromises()
      expect(wrapper?.text()).toContain('Could not load your steps')
      expect(log).toHaveBeenCalled()
      fetchMock.mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            username: 'Alice',
            dailySteps: { '10/01': 123 },
            lastUpdated: '20261013080502',
          }),
        ),
      )
      await wrapper?.get('button').trigger('click')
      await flushPromises()
      expect(wrapper?.find('[data-test="chart"]').exists()).toBe(true)
    },
  )

  it('shows no user directory at the root or unknown paths', async () => {
    await open('/')
    await flushPromises()
    expect(wrapper?.text()).toContain('personal link')
    expect(wrapper?.find('a').exists()).toBe(false)
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
