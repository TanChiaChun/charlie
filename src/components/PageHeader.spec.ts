import { mount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import PageHeader from './PageHeader.vue'

describe('PageHeader', () => {
  test('displays title, subtitle, and formatted last updated date', () => {
    const wrapper = mount(PageHeader, {
      props: {
        title: 'Hello, User1',
        subtitle: 'Team 1',
        lastUpdated: new Date(2026, 10, 8, 17, 15, 2),
      },
    })

    expect(wrapper.get('h1').text()).toBe('Hello, User1')
    expect(wrapper.findAll('p').map((p) => p.text())).toEqual([
      'Team 1',
      'Last updated: 8 Nov, 5:15 pm',
    ])
  })

  test('displays only title when optional details are not provided', () => {
    const wrapper = mount(PageHeader, { props: { title: 'Hello, User2' } })

    expect(wrapper.get('h1').text()).toBe('Hello, User2')
    expect(wrapper.find('p').exists()).toBe(false)
  })
})
