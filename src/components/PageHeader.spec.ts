import { mount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import PageHeader from './PageHeader.vue'

describe('PageHeader', () => {
  test('displays title and formatted last updated date', () => {
    const wrapper = mount(PageHeader, {
      props: {
        title: 'Hello, User1',
        lastUpdated: new Date(2026, 10, 8, 17, 15, 2),
      },
    })

    expect(wrapper.get('h1').text()).toBe('Hello, User1')
    expect(wrapper.get('p').text()).toBe('Last updated: 8 Nov, 5:15 pm')
  })

  test('displays only title when last updated date is not provided', () => {
    const wrapper = mount(PageHeader, { props: { title: 'Hello, User2' } })

    expect(wrapper.get('h1').text()).toBe('Hello, User2')
    expect(wrapper.find('p').exists()).toBe(false)
  })
})
