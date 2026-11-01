import { describe, expect, test } from 'vitest'
import StatsCard from './StatsCard.vue'
import { mount } from '@vue/test-utils'

describe('StatsCard', () => {
  test('renders title, formatted value and unit without rank', () => {
    const wrapper = mount(StatsCard, {
      props: { title: 'Today', value: 10000, unit: 'steps' },
    })

    const text = wrapper.text()
    expect(text).toContain('Today')
    expect(text).toContain('10,000')
    expect(text).toContain('steps')
    expect(text).not.toContain('Rank')
  })

  test('renders title, formatted value, unit, rank and subtitle', () => {
    const wrapper = mount(StatsCard, {
      props: {
        title: 'This Week',
        value: 8888,
        unit: 'steps/day',
        rank: 1,
        subtitle: '26 Oct - 1 Nov',
      },
    })

    const text = wrapper.text()
    expect(text).toContain('This Week')
    expect(text).toContain('8,888')
    expect(text).toContain('steps/day')
    expect(text).toContain('Rank')
    expect(text).toContain('#1')
    expect(text).toContain('26 Oct - 1 Nov')
  })
})
