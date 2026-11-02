import pluginVitest from '@vitest/eslint-plugin'
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from '@vue/eslint-config-typescript'
import { globalIgnores } from 'eslint/config'
import skipFormatting from 'eslint-config-prettier/flat'
import pluginPlaywright from 'eslint-plugin-playwright'
import simpleImportSort from 'eslint-plugin-simple-import-sort'
import pluginVue from 'eslint-plugin-vue'

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{vue,ts,mts,tsx}'],
  },

  globalIgnores([
    '**/dist/**',
    '**/dist-ssr/**',
    '**/coverage/**',
    'src/components/ui/',
  ]),

  ...pluginVue.configs['flat/recommended'],
  vueTsConfigs.recommended,

  {
    plugins: { 'simple-import-sort': simpleImportSort },
    rules: {
      'no-duplicate-imports': ['error', { allowSeparateTypeImports: true }],
      '@typescript-eslint/explicit-function-return-type': 'error',
      'simple-import-sort/imports': 'error',
      'simple-import-sort/exports': 'error',
    },
  },

  {
    ...pluginPlaywright.configs['flat/recommended'],
    files: ['e2e/**/*.{test,spec}.{js,ts,jsx,tsx}'],
  },

  {
    ...pluginVitest.configs.recommended,
    files: ['src/**/__tests__/*'],
  },

  skipFormatting,
)
