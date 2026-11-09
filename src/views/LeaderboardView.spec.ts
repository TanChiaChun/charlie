import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, test, vi } from 'vitest'
import { nextTick } from 'vue'

import LeaderboardItem from '@/components/LeaderboardItem.vue'

import LeaderboardView from './LeaderboardView.vue'

describe('LeaderboardView', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.resetAllMocks()
  })

  test('displays the latest available daily leaderboard', async () => {
    const mockLeaderboardData = {
      lastFetch: '2026-11-06T20:05:02',
      daily: {
        '2026-11-06': [],
        '2026-11-05': [
          { rank: 1, steps: 30000, username: 'User10' },
          { rank: 2, steps: 29636, username: 'User9' },
          { rank: 3, steps: 21120, username: 'User8' },
          { rank: 4, steps: 20477, username: 'User7' },
          { rank: 5, steps: 17453, username: 'User6' },
          { rank: 6, steps: 17333, username: 'User5' },
          { rank: 7, steps: 17229, username: 'User4' },
          { rank: 8, steps: 16795, username: 'User3' },
          { rank: 9, steps: 16495, username: 'User2' },
          { rank: 10, steps: 15000, username: 'User1' },
        ],
      },
    }
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => mockLeaderboardData })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mount(LeaderboardView)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('Leaderboard')
    expect(text).toContain('Last updated: 6 Nov, 8:05 pm')
    expect(wrapper.get('h2').text()).toBe('daily')
    expect(text).toContain('5 Nov')

    const leaderboardItems = wrapper.findAllComponents(LeaderboardItem)
    expect(leaderboardItems).toHaveLength(10)

    expect(leaderboardItems[2]?.text()).toContain('3')
    expect(leaderboardItems[8]?.text()).toContain('User2')
    expect(leaderboardItems[5]?.text()).toContain('17,333')

    const lastProgressBar = leaderboardItems[9]?.get('.bg-brand')
    expect(lastProgressBar?.attributes('style')).toContain('width: 50%')
  })

  test('displays all available records when fewer than 10 exist', async () => {
    const mockLeaderboardData = {
      lastFetch: '2026-11-06T20:05:02',
      daily: {
        '2026-11-06': [{ rank: 1, steps: 589, username: 'User9' }],
        '2026-11-05': [
          { rank: 1, steps: 31389, username: 'User10' },
          { rank: 2, steps: 30636, username: 'User9' },
          { rank: 3, steps: 21120, username: 'User8' },
          { rank: 4, steps: 20477, username: 'User7' },
          { rank: 5, steps: 17453, username: 'User6' },
          { rank: 6, steps: 17333, username: 'User5' },
          { rank: 7, steps: 17229, username: 'User4' },
          { rank: 8, steps: 16795, username: 'User3' },
          { rank: 9, steps: 16495, username: 'User2' },
          { rank: 10, steps: 15445, username: 'User1' },
        ],
      },
    }
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => mockLeaderboardData })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mount(LeaderboardView)
    await flushPromises()

    const leaderboardItems = wrapper.findAllComponents(LeaderboardItem)
    expect(leaderboardItems).toHaveLength(1)

    const firstLeaderboardItemText = leaderboardItems[0]?.text()
    expect(firstLeaderboardItemText).toContain('1')
    expect(firstLeaderboardItemText).toContain('User9')
    expect(firstLeaderboardItemText).toContain('589')

    const firstProgressBar = leaderboardItems[0]?.get('.bg-brand')
    expect(firstProgressBar?.attributes('style')).toContain('width: 100%')
  })

  test('displays the latest available weekly leaderboard', async () => {
    const mockLeaderboardData = {
      lastFetch: '2026-11-10T02:05:02',
      daily: { '2026-11-10': [{ rank: 1, steps: 2883, username: 'User1' }] },
      weekly: {
        '2026-10-12': [
          { rank: 1, averageSteps: 15756.3, username: 'User1' },
          { rank: 2, averageSteps: 15256.6, username: 'User3' },
        ],
        '2026-10-19': [
          { rank: 1, averageSteps: 17026.8, username: 'WeekUser' },
          { rank: 2, averageSteps: 15759.0, username: 'User3' },
          { rank: 3, averageSteps: 15136.3, username: 'User1' },
        ],
      },
    }
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => mockLeaderboardData })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mount(LeaderboardView)
    await flushPromises()

    await wrapper.get('button[role="tab"]:nth-child(2)').trigger('mousedown')

    const text = wrapper.text()
    expect(text).toContain('Leaderboard')
    expect(text).toContain('Last updated: 10 Nov, 2:05 am')
    expect(wrapper.get('h2').text()).toBe('weekly')
    expect(text).toContain('19 Oct - 25 Oct')

    const leaderboardItems = wrapper.findAllComponents(LeaderboardItem)
    expect(leaderboardItems).toHaveLength(3)

    const firstLeaderboardItemText = leaderboardItems[0]?.text()
    expect(firstLeaderboardItemText).toContain('WeekUser')
    expect(firstLeaderboardItemText).toContain('17,026')
  })

  test('displays loading state while fetching leaderboard data', async () => {
    const fetchMock = vi.fn().mockReturnValue(new Promise(() => {}))
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mount(LeaderboardView)
    await nextTick()

    expect(wrapper.text()).toContain('Loading...')
  })

  test('displays error state when fetching data fails', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: false })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mount(LeaderboardView)
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load leaderboard data.')
  })
})
