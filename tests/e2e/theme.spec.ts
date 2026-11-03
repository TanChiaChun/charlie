import { expect, test } from '@playwright/test'

test('follows system dark mode preference', async ({ page }) => {
  await page.goto('/')

  await expect(page.locator('html')).not.toContainClass('dark')

  await page.emulateMedia({ colorScheme: 'dark' })
  await expect(page.locator('html')).toContainClass('dark')
})
