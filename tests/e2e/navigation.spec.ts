import { expect, test } from '@playwright/test'

test('displays not found page at root', async ({ page }) => {
  await page.goto('/')

  await expect(page).toHaveTitle('SG R&D Walking Challenge')
  await expect(
    page.getByRole('heading', { name: 'Page not found' }),
  ).toBeVisible()
})
