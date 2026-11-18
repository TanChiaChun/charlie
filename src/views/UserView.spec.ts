import type { VueWrapper } from '@vue/test-utils'
import type { Router } from 'vue-router'

import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import { nextTick } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'

import StatsCard from '@/components/StatsCard.vue'

import UserView from './UserView.vue'

describe('UserView', () => {
  let router: Router

  beforeEach(async () => {
    router = createRouter({
      history: createWebHashHistory(),
      routes: [
        { component: { template: '<div></div>' }, path: '/leaderboard' },
        { component: UserView, path: '/users/:id' },
      ],
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
      dailySteps: { '10/31': 8326, '11/01': 13668 },
      lastFetch: '2026-11-01T23:05:02',
      stats: {
        current10kStreak: 27,
        current10kStreakEnd: '2026-11-17',
        current10kStreakStart: '2026-10-12',
        current5kStreak: 2,
        current5kStreakEnd: '2026-11-01',
        current5kStreakStart: '2026-10-31',
        dailyRank: 2,
        longest10kStreak: 27,
        longest10kStreakEnd: '2026-11-17',
        longest10kStreakRank: 1,
        longest10kStreakStart: '2026-10-12',
        longest5kStreak: 18,
        longest5kStreakEnd: '2026-10-29',
        longest5kStreakRank: 3,
        longest5kStreakStart: '2026-10-12',
        monthlyAverage: 13668.0,
        monthlyRank: 5,
        weeklyAverage: 10997.0,
        weeklyRank: 11,
      },
      team: '1',
      username: 'User1',
    }
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ json: async () => mockUserData, ok: true })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mountUserView()
    await flushPromises()

    expect(wrapper.get('h1').text()).toBe('Hello, User1')
    const text = wrapper.text()
    expect(text).toContain('Team 1')
    expect(text).toContain('Last updated: 1 Nov, 11:05 pm')
    expect(text).toContain('Your Daily Steps')
    expect(text).toContain('23 Oct - 1 Nov')

    const leaderboardLink = wrapper.get('a[href="#/leaderboard"]')
    expect(leaderboardLink.text()).toContain('View Leaderboard')

    const statsCards = wrapper.findAllComponents(StatsCard)
    expect(statsCards).toHaveLength(7)

    const todayCardText = statsCards[0]?.text()
    expect(todayCardText).toContain('Today')
    expect(todayCardText).toContain('13,668')
    expect(todayCardText).toContain('#2')

    const weekCardText = statsCards[1]?.text()
    expect(weekCardText).toContain('This Week')
    expect(weekCardText).toContain('10,997')
    expect(weekCardText).toContain('#11')
    expect(weekCardText).toContain('26 Oct - 1 Nov')

    const monthCardText = statsCards[2]?.text()
    expect(monthCardText).toContain('November')
    expect(monthCardText).toContain('13,668')
    expect(monthCardText).toContain('#5')
    expect(monthCardText).toContain('1 Nov - 1 Nov')

    const current5kStreakCardText = statsCards[3]?.text()
    expect(current5kStreakCardText).toContain('Current 5K Streak')
    expect(current5kStreakCardText).toContain('2days')
    expect(current5kStreakCardText).toContain('31 Oct - 1 Nov')

    const longest5kStreakCardText = statsCards[4]?.text()
    expect(longest5kStreakCardText).toContain('Longest 5K Streak')
    expect(longest5kStreakCardText).toContain('18days')
    expect(longest5kStreakCardText).toContain('#3')
    expect(longest5kStreakCardText).toContain('12 Oct - 29 Oct')

    const current10kStreakCardText = statsCards[5]?.text()
    expect(current10kStreakCardText).toContain('Current 10K Weekday Streak')
    expect(current10kStreakCardText).toContain('27days')
    expect(current10kStreakCardText).toContain('12 Oct - 17 Nov')

    const longest10kStreakCardText = statsCards[6]?.text()
    expect(longest10kStreakCardText).toContain('Longest 10K Weekday Streak')
    expect(longest10kStreakCardText).toContain('27days')
    expect(longest10kStreakCardText).toContain('#1')
    expect(longest10kStreakCardText).toContain('12 Oct - 17 Nov')
  })

  test('renders zero values when user has no activity', async () => {
    const mockUserData = {
      dailySteps: { '10/31': 0 },
      lastFetch: '2026-11-03T23:05:02',
      stats: {
        current10kStreak: 0,
        current10kStreakEnd: null,
        current10kStreakStart: null,
        current5kStreak: 0,
        current5kStreakEnd: null,
        current5kStreakStart: null,
        dailyRank: null,
        longest10kStreak: 0,
        longest10kStreakEnd: null,
        longest10kStreakRank: null,
        longest10kStreakStart: null,
        longest5kStreak: 0,
        longest5kStreakEnd: null,
        longest5kStreakRank: null,
        longest5kStreakStart: null,
        monthlyAverage: 0.0,
        monthlyRank: null,
        weeklyAverage: 0.0,
        weeklyRank: null,
      },
      team: '2',
      username: 'User2',
    }
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ json: async () => mockUserData, ok: true })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mountUserView()
    await flushPromises()

    const statsCards = wrapper.findAllComponents(StatsCard)
    expect(statsCards).toHaveLength(7)

    const todayCardText = statsCards[0]?.text()
    expect(todayCardText).toContain('Today')
    expect(todayCardText).toContain('0steps')
    expect(todayCardText).not.toContain('Rank')

    const weekCardText = statsCards[1]?.text()
    expect(weekCardText).toContain('This Week')
    expect(weekCardText).toContain('0steps/day')
    expect(weekCardText).not.toContain('Rank')
    expect(weekCardText).toContain('2 Nov - 3 Nov')

    const monthCardText = statsCards[2]?.text()
    expect(monthCardText).toContain('November')
    expect(monthCardText).toContain('0steps/day')
    expect(monthCardText).not.toContain('Rank')
    expect(monthCardText).toContain('1 Nov - 3 Nov')

    const current5kStreakCardText = statsCards[3]?.text()
    expect(current5kStreakCardText).toContain('Current 5K Streak')
    expect(current5kStreakCardText).toContain('0days')

    const longest5kStreakCardText = statsCards[4]?.text()
    expect(longest5kStreakCardText).toContain('Longest 5K Streak')
    expect(longest5kStreakCardText).toContain('0days')
    expect(longest5kStreakCardText).not.toContain('Rank')

    const current10kStreakCardText = statsCards[5]?.text()
    expect(current10kStreakCardText).toContain('Current 10K Weekday Streak')
    expect(current10kStreakCardText).toContain('0days')

    const longest10kStreakCardText = statsCards[6]?.text()
    expect(longest10kStreakCardText).toContain('Longest 10K Weekday Streak')
    expect(longest10kStreakCardText).toContain('0days')
    expect(longest10kStreakCardText).not.toContain('Rank')
  })

  test('displays the completed November date range after November', async () => {
    const mockUserData = {
      dailySteps: { '10/31': 0 },
      lastFetch: '2026-12-01T23:05:02',
      stats: {
        current10kStreak: 0,
        current10kStreakEnd: null,
        current10kStreakStart: null,
        current5kStreak: 0,
        current5kStreakEnd: null,
        current5kStreakStart: null,
        dailyRank: null,
        longest10kStreak: 0,
        longest10kStreakEnd: null,
        longest10kStreakRank: null,
        longest10kStreakStart: null,
        longest5kStreak: 0,
        longest5kStreakEnd: null,
        longest5kStreakRank: null,
        longest5kStreakStart: null,
        monthlyAverage: 0.0,
        monthlyRank: null,
        weeklyAverage: 0.0,
        weeklyRank: null,
      },
      team: '3',
      username: 'User3',
    }
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ json: async () => mockUserData, ok: true })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mountUserView()
    await flushPromises()

    const statsCards = wrapper.findAllComponents(StatsCard)
    const monthCardText = statsCards[2]?.text()
    expect(monthCardText).toContain('November')
    expect(monthCardText).toContain('1 Nov - 30 Nov')
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
