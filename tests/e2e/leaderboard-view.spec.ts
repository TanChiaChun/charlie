import { expect, test } from '@playwright/test'

test('displays the latest available daily leaderboard', async ({ page }) => {
  const leaderboardData = {
    lastFetch: '2026-11-06T20:05:02',
    daily: {
      '2026-11-06': [],
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
  await expect(page.getByRole('heading', { name: 'daily' })).toBeVisible()
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
    lastFetch: '2026-11-10T02:05:02',
    daily: { '2026-11-10': [{ rank: 1, steps: 2883, username: 'User1' }] },
    weekly: {
      '2026-10-19': [
        { rank: 1, averageSteps: 17026.8, username: 'WeekUser' },
        { rank: 2, averageSteps: 15759.0, username: 'User3' },
      ],
    },
  }
  await page.route('**/leaderboard.json', (route) =>
    route.fulfill({ json: leaderboardData }),
  )
  await page.goto('/#/leaderboard')

  const records = page.getByTestId('leaderboard').locator(':scope > div')
  const firstRecord = records.first()

  await expect(page.getByRole('heading', { name: 'daily' })).toBeVisible()
  await expect(records).toHaveCount(1)
  await expect(firstRecord).toContainText('User1')
  await expect(firstRecord).toContainText('2,883')

  await page.getByRole('tab', { name: 'Weekly' }).click()
  await expect(page.getByRole('heading', { name: 'weekly' })).toBeVisible()
  await expect(page.getByText('19 Oct - 25 Oct')).toBeVisible()
  await expect(records).toHaveCount(2)
  await expect(firstRecord).toContainText('WeekUser')
  await expect(firstRecord).toContainText('17,026')

  await page.getByRole('tab', { name: 'Daily' }).click()
  await expect(page.getByRole('heading', { name: 'daily' })).toBeVisible()
  await expect(records).toHaveCount(1)
  await expect(firstRecord).toContainText('User1')
})

test('displays an error when leaderboard data fails to load', async ({
  page,
}) => {
  await page.route('**/leaderboard.json', async (route) => route.abort())

  await page.goto('/#/leaderboard')

  await expect(page.getByText('Failed to load leaderboard data.')).toBeVisible()
})
