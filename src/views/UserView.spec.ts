import type { VueWrapper } from '@vue/test-utils'
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import { nextTick } from 'vue'
import type { Router } from 'vue-router'
import { createRouter, createWebHashHistory } from 'vue-router'

import StatsCard from '@/components/StatsCard.vue'

import UserView from './UserView.vue'

describe('UserView', () => {
  let router: Router

  beforeEach(async () => {
    router = createRouter({
      history: createWebHashHistory(),
      routes: [{ path: '/users/:id', component: UserView }],
    })
    await router.push('/users/izG78Bhy')
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.resetAllMocks()
  })

  const mountUserView = (): VueWrapper =>
    mount(UserView, {
      global: { plugins: [router], stubs: { DailyStepsChart: true } },
    })

  test('renders user details and statistics correctly', async () => {
    const mockUserData = {
      username: 'User1',
      lastFetch: '2026-11-01T23:05:02',
      dailySteps: { '10/31': 8326, '11/01': 13668 },
      stats: {
        dailyRank: 2,
        weeklyAverage: 10997.0,
        weeklyRank: 11,
        longest5kStreak: 18,
        longest5kStreakRank: 3,
        longest5kStreakStart: '2026-10-12',
        longest5kStreakEnd: '2026-10-29',
        current5kStreak: 2,
        current5kStreakStart: '2026-10-31',
        current5kStreakEnd: '2026-11-01',
      },
    }
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => mockUserData })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mountUserView()
    await flushPromises()

    expect(wrapper.get('h1').text()).toBe('Hello, User1')
    const text = wrapper.text()
    expect(text).toContain('Last updated: 1 Nov, 11:05 pm')
    expect(text).toContain('Your Daily Steps')
    expect(text).toContain('23 Oct - 1 Nov')

    const statsCards = wrapper.findAllComponents(StatsCard)
    expect(statsCards).toHaveLength(4)

    const todayCardText = statsCards[0]?.text()
    expect(todayCardText).toContain('Today')
    expect(todayCardText).toContain('13,668')
    expect(todayCardText).toContain('#2')

    const weekCardText = statsCards[1]?.text()
    expect(weekCardText).toContain('This Week')
    expect(weekCardText).toContain('10,997')
    expect(weekCardText).toContain('#11')
    expect(weekCardText).toContain('26 Oct - 1 Nov')

    const current5kStreakCardText = statsCards[2]?.text()
    expect(current5kStreakCardText).toContain('Current 5K Streak')
    expect(current5kStreakCardText).toContain('2days')
    expect(current5kStreakCardText).toContain('31 Oct - 1 Nov')

    const longest5kStreakCardText = statsCards[3]?.text()
    expect(longest5kStreakCardText).toContain('Longest 5K Streak')
    expect(longest5kStreakCardText).toContain('18days')
    expect(longest5kStreakCardText).toContain('#3')
    expect(longest5kStreakCardText).toContain('12 Oct - 29 Oct')
  })

  test('renders zero values when user has no activity', async () => {
    const mockUserData = {
      username: 'User2',
      lastFetch: '2026-11-01T23:05:02',
      dailySteps: { '10/31': 0 },
      stats: {
        dailyRank: null,
        weeklyAverage: 0.0,
        weeklyRank: null,
        longest5kStreak: 0,
        longest5kStreakRank: null,
        longest5kStreakStart: null,
        longest5kStreakEnd: null,
        current5kStreak: 0,
        current5kStreakStart: null,
        current5kStreakEnd: null,
      },
    }
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => mockUserData })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mountUserView()
    await flushPromises()

    const statsCards = wrapper.findAllComponents(StatsCard)
    expect(statsCards).toHaveLength(4)

    const todayCardText = statsCards[0]?.text()
    expect(todayCardText).toContain('Today')
    expect(todayCardText).toContain('0steps')
    expect(todayCardText).not.toContain('Rank')

    const weekCardText = statsCards[1]?.text()
    expect(weekCardText).toContain('This Week')
    expect(weekCardText).toContain('0steps/day')
    expect(weekCardText).not.toContain('Rank')
    expect(weekCardText).toContain('26 Oct - 1 Nov')

    const current5kStreakCardText = statsCards[2]?.text()
    expect(current5kStreakCardText).toContain('Current 5K Streak')
    expect(current5kStreakCardText).toContain('0days')

    const longest5kStreakCardText = statsCards[3]?.text()
    expect(longest5kStreakCardText).toContain('Longest 5K Streak')
    expect(longest5kStreakCardText).toContain('0days')
    expect(longest5kStreakCardText).not.toContain('Rank')
  })

  test('fetches user data again when route id changes', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    mountUserView()
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(fetchMock).toHaveBeenLastCalledWith('/users/izG78Bhy.json', {
      cache: 'no-store',
    })

    await router.push('/users/NttLygXS')
    await flushPromises()
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock).toHaveBeenLastCalledWith('/users/NttLygXS.json', {
      cache: 'no-store',
    })
  })

  test('displays loading state while fetching user data', async () => {
    const fetchMock = vi.fn().mockReturnValue(new Promise(() => {}))
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mountUserView()
    await nextTick()

    expect(wrapper.text()).toContain('Loading...')
  })

  test('displays error state when fetching user data fails', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: false })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mountUserView()
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load user data.')
  })
})
