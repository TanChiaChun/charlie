// @vitest-environment node
import { afterEach, describe, expect, it } from 'vitest'
import {
  mkdir,
  mkdtemp,
  readFile,
  readdir,
  rm,
  writeFile,
} from 'node:fs/promises'
import { join } from 'node:path'
import { prepareUserData } from '../scripts/prepare-user-data.mjs'
import { tmpdir } from 'node:os'

const temporaryDirectories: string[] = []

afterEach(async () => {
  await Promise.all(
    temporaryDirectories.splice(0).map((path) => rm(path, { recursive: true })),
  )
})

async function fixture(
  steps: unknown,
  ids: unknown,
): Promise<{
  stepsPath: string
  idsPath: string
  outputPath: string
  rawPath: string
}> {
  const directory = await mkdtemp(join(tmpdir(), 'charlie-user-data-'))
  temporaryDirectories.push(directory)
  const stepsPath = join(directory, 'steps.json')
  const idsPath = join(directory, 'ids.json')
  const outputPath = join(directory, 'output')
  const rawPath = join(directory, 'raw')
  await mkdir(join(rawPath, '20261013'), { recursive: true })
  await writeFile(join(rawPath, '20261013', '20261013070502.csv'), '')
  await writeFile(join(rawPath, '20261013', '20261013080502.csv'), '')
  await mkdir(join(rawPath, '20261012'), { recursive: true })
  await writeFile(join(rawPath, '20261012', '20261012230502.csv'), '')
  await writeFile(stepsPath, JSON.stringify(steps))
  await writeFile(idsPath, JSON.stringify(ids))
  return { stepsPath, idsPath, outputPath, rawPath }
}

describe('per-user data preparation', () => {
  it('writes only the selected user identity and steps and removes stale generated files', async () => {
    const paths = await fixture(
      { Alice: { '10/01': 123 }, Bob: { '10/02': 456 } },
      { Alice: 'aaaaaaaa', Bob: 'bbbbbbbb' },
    )
    expect(await prepareUserData(paths)).toBe(2)
    expect((await readdir(paths.outputPath)).sort()).toEqual([
      'aaaaaaaa.json',
      'bbbbbbbb.json',
    ])
    expect(
      JSON.parse(
        await readFile(join(paths.outputPath, 'aaaaaaaa.json'), 'utf8'),
      ),
    ).toEqual({
      username: 'Alice',
      dailySteps: { '10/01': 123 },
      lastUpdated: '20261013080502',
    })
    expect(
      JSON.parse(
        await readFile(join(paths.outputPath, 'bbbbbbbb.json'), 'utf8'),
      ),
    ).toEqual({
      username: 'Bob',
      dailySteps: { '10/02': 456 },
      lastUpdated: '20261013080502',
    })
    await writeFile(paths.stepsPath, JSON.stringify({ Alice: {} }))
    await writeFile(paths.idsPath, JSON.stringify({ Alice: 'aaaaaaaa' }))
    await prepareUserData(paths)
    expect(await readdir(paths.outputPath)).toEqual(['aaaaaaaa.json'])
    expect(
      await readFile(join(paths.outputPath, 'aaaaaaaa.json'), 'utf8'),
    ).toBe(
      '{"username":"Alice","dailySteps":{},"lastUpdated":"20261013080502"}\n',
    )
  })

  it('fails explicitly when raw timestamp files are missing', async () => {
    const paths = await fixture({ Alice: {} }, { Alice: 'aaaaaaaa' })
    await rm(paths.rawPath, { recursive: true })
    await mkdir(paths.rawPath)
    await expect(prepareUserData(paths)).rejects.toThrow(
      'No timestamped raw CSV',
    )
    await expect(readdir(paths.outputPath)).rejects.toThrow()
  })

  it.each([
    [{ Alice: {} }, {}, 'Missing public ID'],
    [{}, { Alice: 'aaaaaaaa' }, 'Missing steps'],
    [
      { Alice: {}, Bob: {} },
      { Alice: 'aaaaaaaa', Bob: 'aaaaaaaa' },
      'duplicate',
    ],
    [{ Alice: {} }, { Alice: '../badid' }, 'Invalid'],
    [{ Alice: { '02/30': 1 } }, { Alice: 'aaaaaaaa' }, 'Invalid step date'],
    [{ Alice: { '10/01': -1 } }, { Alice: 'aaaaaaaa' }, 'Invalid step count'],
    [[], {}, 'must be objects'],
  ])(
    'rejects invalid inputs before publishing files (%#)',
    async (steps, ids, message) => {
      const paths = await fixture(steps, ids)
      await expect(prepareUserData(paths)).rejects.toThrow(message)
      await expect(readdir(paths.outputPath)).rejects.toThrow()
    },
  )
})
