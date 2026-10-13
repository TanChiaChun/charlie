export type StepPoint = {
  date: Date
  steps: number
}

export function isPublicId(value: string): boolean {
  return /^[A-Za-z0-9_-]{8}$/.test(value)
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

export function parseUserSteps(value: unknown): {
  username: string
  points: StepPoint[]
  lastUpdated: string
} {
  if (
    !isRecord(value) ||
    typeof value.username !== 'string' ||
    !value.username.trim()
  ) {
    throw new Error('User data must include a username.')
  }
  if (typeof value.lastUpdated !== 'string') {
    throw new Error('User data must include a last-updated timestamp.')
  }
  return {
    username: value.username,
    points: parseDailySteps(value.dailySteps),
    lastUpdated: formatRawTimestamp(value.lastUpdated),
  }
}

export function formatRawTimestamp(value: string): string {
  if (!/^\d{14}$/.test(value)) {
    throw new Error('Invalid raw data timestamp.')
  }
  const iso = `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}T${value.slice(8, 10)}:${value.slice(10, 12)}:${value.slice(12, 14)}`
  const date = new Date(`${iso}Z`)
  if (
    !Number.isFinite(date.getTime()) ||
    date.toISOString() !== `${iso}.000Z`
  ) {
    throw new Error('Invalid raw data timestamp.')
  }
  return iso.replace('T', ' ')
}

export function parseDailySteps(value: unknown): StepPoint[] {
  if (!isRecord(value)) {
    throw new Error('Daily steps must be an object.')
  }

  return Object.entries(value)
    .map(([key, steps]) => {
      if (!/^\d{2}\/\d{2}$/.test(key)) {
        throw new Error(`Invalid step date: ${key}`)
      }
      const month = Number(key.slice(0, 2))
      const day = Number(key.slice(3))
      const date = new Date(2026, month - 1, day)
      if (date.getMonth() !== month - 1 || date.getDate() !== day) {
        throw new Error(`Invalid step date: ${key}`)
      }
      if (typeof steps !== 'number' || !Number.isFinite(steps) || steps < 0) {
        throw new Error(`Invalid step count for ${key}`)
      }
      return { date, steps }
    })
    .sort((a, b) => a.date.getTime() - b.date.getTime())
}
