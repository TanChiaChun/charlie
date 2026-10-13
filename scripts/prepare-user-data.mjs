import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import {
  formatRawTimestamp,
  isPublicId,
  isRecord,
  parseDailySteps,
} from '../src/lib/steps.ts'
import { mkdir, readFile, readdir, unlink, writeFile } from 'node:fs/promises'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')

/** @returns {Promise<number>} */
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type -- JavaScript uses JSDoc return types.
export async function prepareUserData({
  stepsPath = join(root, 'build-data', 'user_daily_steps.json'),
  idsPath = resolve(
    root,
    '..',
    'charlie-data',
    'data',
    'output',
    'user_public_ids.json',
  ),
  rawPath = resolve(dirname(idsPath), '..', 'raw'),
  outputPath = join(root, 'public', 'user-data'),
} = {}) {
  const steps = JSON.parse(await readFile(stepsPath, 'utf8'))
  const ids = JSON.parse(await readFile(idsPath, 'utf8'))
  if (!isRecord(steps) || !isRecord(ids)) {
    throw new Error('Steps and public IDs must be objects.')
  }

  const usedIds = new Set()
  for (const [username, id] of Object.entries(ids)) {
    if (!username.trim()) {
      throw new Error('Username must not be empty.')
    }
    if (typeof id !== 'string' || !isPublicId(id) || usedIds.has(id)) {
      throw new Error(`Invalid or duplicate public ID for ${username}`)
    }
    usedIds.add(id)
  }
  const files = new Map()
  for (const [username, dailySteps] of Object.entries(steps)) {
    if (!Object.hasOwn(ids, username)) {
      throw new Error(`Missing public ID for ${username}`)
    }
    parseDailySteps(dailySteps)
    files.set(`${ids[username]}.json`, { username, dailySteps })
  }
  for (const username of Object.keys(ids)) {
    if (!Object.hasOwn(steps, username)) {
      throw new Error(`Missing steps for ${username}`)
    }
  }

  const timestamps = []
  for (const directory of await readdir(rawPath, { withFileTypes: true })) {
    if (!directory.isDirectory() || !/^\d{8}$/.test(directory.name)) continue
    for (const file of await readdir(join(rawPath, directory.name), {
      withFileTypes: true,
    })) {
      if (!file.isFile() || !/^\d{14}\.csv$/.test(file.name)) continue
      const timestamp = file.name.slice(0, 14)
      formatRawTimestamp(timestamp)
      if (!timestamp.startsWith(directory.name)) {
        throw new Error(
          `Raw timestamp does not match its date directory: ${file.name}`,
        )
      }
      timestamps.push(timestamp)
    }
  }
  const lastUpdated = timestamps.sort().at(-1)
  if (!lastUpdated) {
    throw new Error(`No timestamped raw CSV files found in ${rawPath}`)
  }
  await mkdir(outputPath, { recursive: true })
  for (const entry of await readdir(outputPath, { withFileTypes: true })) {
    if (
      entry.isFile() &&
      /^[A-Za-z0-9_-]{8}\.json$/.test(entry.name) &&
      !files.has(entry.name)
    ) {
      await unlink(join(outputPath, entry.name))
    }
  }
  for (const [name, content] of files) {
    await writeFile(
      join(outputPath, name),
      `${JSON.stringify({ ...content, lastUpdated })}\n`,
    )
  }
  return files.size
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(resolve(process.argv[1])).href
) {
  const args = process.argv.slice(2)
  if (args.length > 2) {
    throw new Error(
      'Usage: node scripts/prepare-user-data.mjs [public-id-json-path] [raw-data-directory]',
    )
  }
  const idsPath = args[0] ? resolve(args[0]) : undefined
  const rawPath = args[1] ? resolve(args[1]) : undefined
  const count = await prepareUserData({ idsPath, rawPath })
  console.log(`Prepared ${count} individual user data files.`)
}
