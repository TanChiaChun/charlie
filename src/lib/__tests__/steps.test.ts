import { describe, expect, it } from 'vitest'
import {
  formatRawTimestamp,
  isPublicId,
  parseDailySteps,
  parseUserSteps,
} from '../steps'

describe('daily steps', () => {
  it('parses a username with its steps', () => {
    const user = parseUserSteps({
      username: 'Alice',
      lastUpdated: '20261013080502',
      dailySteps: { '10/01': 123 },
    })
    expect(user.username).toBe('Alice')
    expect(user.points[0]?.steps).toBe(123)
    expect(user.lastUpdated).toBe('2026-10-13 08:05:02')
  })

  it.each(['20260230080502', '20261013240502', '20261013086002', 'not-a-date'])(
    'rejects invalid raw timestamps (%s)',
    (value) => {
      expect(() => formatRawTimestamp(value)).toThrow()
    },
  )

  it.each([
    {},
    { username: '' },
    { username: ' ' },
    { username: 123 },
    { username: 'Alice', dailySteps: [] },
  ])('rejects invalid user data (%#)', (data) => {
    expect(() => parseUserSteps(data)).toThrow()
  })

  it('sorts dates and preserves zero values', () => {
    const points = parseDailySteps({ '10/02': 0, '09/30': 120 })
    expect(points.map((point) => point.steps)).toEqual([120, 0])
    expect(points[0]?.date.getFullYear()).toBe(2026)
    expect(points[0]?.date.getMonth()).toBe(8)
  })

  it('accepts an empty dataset', () => {
    expect(parseDailySteps({})).toEqual([])
  })

  it.each([
    null,
    [],
    { '02/29': 10 },
    { '13/01': 1 },
    { '10/01': '1' },
    { '10/01': Infinity },
    { '10/01': -1 },
    { '1/01': 2 },
  ])('rejects invalid data (%#)', (data) => {
    expect(() => parseDailySteps(data)).toThrow()
  })

  it('accepts opaque IDs but not paths or arbitrary names', () => {
    expect(isPublicId('Ab_-1234')).toBe(true)
    expect(isPublicId('../other')).toBe(false)
    expect(isPublicId('short')).toBe(false)
  })
})
