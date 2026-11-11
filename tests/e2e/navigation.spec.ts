import { expect, test } from '@playwright/test'

test('displays not found page at root', async ({ page }) => {
  await page.goto('/')

  await expect(page).toHaveTitle('SG R&D Walking Challenge')
  await expect(
    page.getByRole('heading', { name: 'Page not found' }),
  ).toBeVisible()
})

test('navigates from user view to leaderboard', async ({ page }) => {
  const userData = {
    username: 'User1',
    lastFetch: '2026-11-01T23:05:02',
    dailySteps: { '11/01': 13668, '10/31': 8326 },
    stats: {
      dailyRank: 2,
      weeklyAverage: 10997.0,
      weeklyRank: 11,
      monthlyAverage: 13668.0,
      monthlyRank: 15,
      longest5kStreak: 18,
      longest5kStreakRank: 3,
      longest5kStreakStart: '2026-10-12',
      longest5kStreakEnd: '2026-10-29',
      current5kStreak: 2,
      current5kStreakStart: '2026-10-31',
      current5kStreakEnd: '2026-11-01',
    },
  }
  await page.route('**/users/zocJvWkQ.json', async (route) => {
    await route.fulfill({ json: userData })
  })
  await page.goto('/#/users/zocJvWkQ')

  await page.getByRole('link', { name: 'View Leaderboard' }).click()
  await expect(page).toHaveURL(/#\/leaderboard$/)
})
