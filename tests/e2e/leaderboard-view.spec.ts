import { expect, test } from '@playwright/test'

test('displays the latest available daily leaderboard', async ({ page }) => {
  const leaderboardData = {
    daily: {
      '2026-11-05': [
        { rank: 1, steps: 30000, username: 'User9' },
        { rank: 2, steps: 29636, username: 'User10' },
        { rank: 3, steps: 21120, username: 'User8' },
        { rank: 4, steps: 20477, username: 'User7' },
        { rank: 5, steps: 17453, username: 'User6' },
        { rank: 6, steps: 17333, username: 'User5' },
        { rank: 7, steps: 17229, username: 'User4' },
        { rank: 8, steps: 16795, username: 'User3' },
        { rank: 9, steps: 16495, username: 'User2' },
        { rank: 10, steps: 15000, username: 'User1' },
      ],
      '2026-11-06': [],
    },
    lastFetch: '2026-11-06T20:05:02',
    monthly: [{ averageSteps: 19266.8, rank: 1, username: 'NovUser' }],
    monthlyTeams: [{ averageSteps: 8000.0, rank: 1, team: 'Team1' }],
    streaks5k: [{ days: 29, rank: 1, username: 'User2' }],
    weekly: {
      '2026-10-12': [{ averageSteps: 15756.3, rank: 1, username: 'User1' }],
    },
  }
  await page.route('**/leaderboard.json', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1000))

    await route.fulfill({ json: leaderboardData })
  })

  await page.goto('/#/leaderboard')

  await expect(page.getByText('Loading...')).toBeVisible()

  await expect(page.getByRole('heading', { name: 'Leaderboard' })).toBeVisible()
  await expect(page.getByText('Last updated: 6 Nov')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Daily' })).toBeVisible()
  await expect(page.getByText('5 Nov')).toBeVisible()

  const leaderboard = page.getByTestId('leaderboard')
  await expect(leaderboard).toBeVisible()

  const records = leaderboard.locator(':scope > div')
  await expect(records).toHaveCount(10)

  const firstRecord = records.first()
  await expect(firstRecord).toContainText('1')
  await expect(firstRecord.locator('.bg-brand')).toHaveAttribute(
    'style',
    'width: 100%;',
  )

  const lastRecord = records.last()
  await expect(lastRecord).toContainText('10')
  await expect(lastRecord.locator('.bg-brand')).toHaveAttribute(
    'style',
    'width: 50%;',
  )
})

test('switches between daily and weekly leaderboards', async ({ page }) => {
  const leaderboardData = {
    daily: { '2026-11-10': [{ rank: 1, steps: 2883, username: 'User1' }] },
    lastFetch: '2026-11-10T02:05:02',
    monthly: [{ averageSteps: 19266.8, rank: 1, username: 'NovUser' }],
    monthlyTeams: [{ averageSteps: 8000.0, rank: 1, team: 'Team1' }],
    streaks5k: [{ days: 29, rank: 1, username: 'User2' }],
    weekly: {
      '2026-10-19': [
        { averageSteps: 17026.8, rank: 1, username: 'WeekUser' },
        { averageSteps: 15759.0, rank: 2, username: 'User3' },
      ],
    },
  }
  await page.route('**/leaderboard.json', (route) =>
    route.fulfill({ json: leaderboardData }),
  )
  await page.goto('/#/leaderboard')

  const records = page.getByTestId('leaderboard').locator(':scope > div')
  const firstRecord = records.first()

  await expect(page.getByRole('heading', { name: 'Daily' })).toBeVisible()
  await expect(records).toHaveCount(1)
  await expect(firstRecord).toContainText('User1')
  await expect(firstRecord).toContainText('2,883')

  await page.getByRole('tab', { name: 'Weekly' }).click()
  await expect(page.getByRole('heading', { name: 'Weekly' })).toBeVisible()
  await expect(page.getByText('19 Oct - 25 Oct')).toBeVisible()
  await expect(records).toHaveCount(2)
  await expect(firstRecord).toContainText('WeekUser')
  await expect(firstRecord).toContainText('17,026')

  await page.getByRole('tab', { name: 'Daily' }).click()
  await expect(page.getByRole('heading', { name: 'Daily' })).toBeVisible()
  await expect(records).toHaveCount(1)
  await expect(firstRecord).toContainText('User1')
})

test('displays the November leaderboard', async ({ page }) => {
  const leaderboardData = {
    daily: { '2026-11-10': [{ rank: 1, steps: 2883, username: 'User1' }] },
    lastFetch: '2026-11-10T02:05:02',
    monthly: [
      { averageSteps: 19266.8, rank: 1, username: 'NovUser' },
      { averageSteps: 16451.5, rank: 2, username: 'User2' },
    ],
    monthlyTeams: [{ averageSteps: 8000.0, rank: 1, team: 'Team1' }],
    streaks5k: [{ days: 29, rank: 1, username: 'User2' }],
    weekly: {
      '2026-10-12': [{ averageSteps: 15756.3, rank: 1, username: 'User1' }],
    },
  }
  await page.route('**/leaderboard.json', (route) =>
    route.fulfill({ json: leaderboardData }),
  )
  await page.goto('/#/leaderboard')

  await page.getByRole('tab', { name: 'November' }).click()
  await expect(page.getByRole('heading', { name: 'November' })).toBeVisible()
  await expect(page.getByText('1 Nov - 10 Nov')).toBeVisible()

  const records = page.getByTestId('leaderboard').locator(':scope > div')
  await expect(records).toHaveCount(2)

  const firstRecord = records.first()
  await expect(firstRecord).toContainText('NovUser')
  await expect(firstRecord).toContainText('19,266')
})

test('displays the November team leaderboard', async ({ page }) => {
  const leaderboardData = {
    daily: { '2026-11-10': [{ rank: 1, steps: 2883, username: 'User1' }] },
    lastFetch: '2026-11-10T02:05:02',
    monthly: [{ averageSteps: 19266.8, rank: 1, username: 'NovUser' }],
    monthlyTeams: [
      { averageSteps: 8000.0, rank: 1, team: 'Team1' },
      { averageSteps: 6000.0, rank: 2, team: 'Team2' },
    ],
    streaks5k: [{ days: 29, rank: 1, username: 'User2' }],
    weekly: {
      '2026-10-12': [{ averageSteps: 15756.3, rank: 1, username: 'User1' }],
    },
  }
  await page.route('**/leaderboard.json', (route) =>
    route.fulfill({ json: leaderboardData }),
  )
  await page.goto('/#/leaderboard')

  await page.getByRole('tab', { name: 'November' }).click()
  await page.getByRole('tab', { name: 'Team' }).click()

  const records = page.getByTestId('leaderboard').locator(':scope > div')
  await expect(records).toHaveCount(2)

  const firstRecord = records.first()
  await expect(firstRecord).toContainText('Team1')
})

test('displays the 5K streak leaderboard', async ({ page }) => {
  const leaderboardData = {
    daily: { '2026-11-10': [{ rank: 1, steps: 2883, username: 'User1' }] },
    lastFetch: '2026-11-10T15:05:02',
    monthly: [{ averageSteps: 19266.8, rank: 1, username: 'NovUser' }],
    monthlyTeams: [{ averageSteps: 8000.0, rank: 1, team: 'Team1' }],
    streaks5k: [
      { days: 29, rank: 1, username: '5kUser' },
      { days: 29, rank: 1, username: 'User6' },
      { days: 28, rank: 3, username: 'User10' },
      { days: 28, rank: 3, username: 'User1' },
      { days: 23, rank: 5, username: 'User5' },
      { days: 22, rank: 6, username: 'User11' },
      { days: 20, rank: 7, username: 'User3' },
      { days: 18, rank: 8, username: 'User7' },
      { days: 17, rank: 9, username: 'User8' },
      { days: 17, rank: 9, username: 'User4' },
      { days: 17, rank: 9, username: 'User9' },
    ],
    weekly: {
      '2026-10-12': [{ averageSteps: 15756.3, rank: 1, username: 'User1' }],
    },
  }
  await page.route('**/leaderboard.json', (route) =>
    route.fulfill({ json: leaderboardData }),
  )
  await page.goto('/#/leaderboard')

  await page.getByRole('tab', { name: '5K Streak' }).click()
  await expect(page.getByRole('heading', { name: '5K Streak' })).toBeVisible()
  await expect(page.getByText('12 Oct - 10 Nov')).toBeVisible()

  const records = page.getByTestId('leaderboard').locator(':scope > div')
  await expect(records).toHaveCount(11)

  const firstRecord = records.first()
  await expect(firstRecord).toContainText('5kUser')
  await expect(firstRecord).toContainText('29')
})

test('displays an error when leaderboard data fails to load', async ({
  page,
}) => {
  await page.route('**/leaderboard.json', async (route) => route.abort())

  await page.goto('/#/leaderboard')

  await expect(page.getByText('Failed to load leaderboard data.')).toBeVisible()
})
