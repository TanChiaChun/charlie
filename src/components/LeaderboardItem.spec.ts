import { mount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import LeaderboardItem from './LeaderboardItem.vue'

describe('LeaderboardItem', () => {
  test('displays leaderboard record and progress', () => {
    const wrapper = mount(LeaderboardItem, {
      props: {
        record: { rank: 1, steps: 8000, username: 'User1' },
        maxSteps: 10000,
      },
    })

    const text = wrapper.text()
    expect(text).toContain('1')
    expect(text).toContain('User1')
    expect(text).toContain('8,000')

    const progressBar = wrapper.get('.bg-brand')
    expect(progressBar.attributes('style')).toContain('width: 80%')
  })
})
