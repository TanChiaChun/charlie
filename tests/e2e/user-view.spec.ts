import { expect, test } from '@playwright/test'

const userData = {
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
    monthlyRank: 15,
    weeklyAverage: 10997.0,
    weeklyRank: 11,
  },
  team: '1',
  username: 'User1',
}

test('displays user view after data loads', async ({ page }) => {
  await page.route('**/users/zocJvWkQ.json', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1000))

    await route.fulfill({ json: userData })
  })

  await page.goto('/#/users/zocJvWkQ')

  await expect(page.getByText('Loading...')).toBeVisible()

  await expect(
    page.getByRole('heading', { name: 'Hello, User1' }),
  ).toBeVisible()
  await expect(page.getByText('Team 1')).toBeVisible()
  await expect(page.getByText('Last updated: 1 Nov')).toBeVisible()
  await expect(
    page.getByRole('heading', { name: 'Your Daily Steps' }),
  ).toBeVisible()
  await expect(page.getByText('23 Oct - 1 Nov')).toBeVisible()

  await expect(page.getByRole('heading', { name: 'Today' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'This Week' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'November' })).toBeVisible()
  await expect(
    page.getByRole('heading', { name: 'Current 5K Streak' }),
  ).toBeVisible()
  await expect(
    page.getByRole('heading', { name: 'Longest 5K Streak' }),
  ).toBeVisible()
  await expect(
    page.getByRole('heading', { name: 'Current 10K Weekday Streak' }),
  ).toBeVisible()
  await expect(
    page.getByRole('heading', { name: 'Longest 10K Weekday Streak' }),
  ).toBeVisible()

  const yAxis = page.locator('css=g[axis-type="y"]')
  const viewportWidth = page.viewportSize()?.width ?? 0
  if (viewportWidth < 640) {
    await expect(yAxis).toHaveCount(0)
  } else {
    await expect(yAxis).toBeVisible()
  }
})

test('displays error when URL changes to invalid user', async ({ page }) => {
  await page.route('**/users/zocJvWkQ.json', (route) =>
    route.fulfill({ json: userData }),
  )
  await page.route('**/users/zocJvWk.json', (route) =>
    route.fulfill({ status: 404 }),
  )

  await page.goto('/#/users/zocJvWkQ')
  await expect(
    page.getByRole('heading', { name: 'Hello, User1' }),
  ).toBeVisible()

  await page.goto('/#/users/zocJvWk')
  await expect(page.getByText('Failed to load user data.')).toBeVisible()
})
