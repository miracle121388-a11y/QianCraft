import { defineConfig } from '@playwright/test';

const condaEnvironment = process.env.QIANCRAFT_CONDA_ENV?.trim() || 'qiancraft';
if (!/^[A-Za-z0-9_.-]+$/.test(condaEnvironment)) {
  throw new Error('QIANCRAFT_CONDA_ENV 只能包含字母、数字、点、下划线和连字符。');
}
const pythonCommand = process.env.QIANCRAFT_PYTHON_COMMAND?.trim()
  || `conda run --no-capture-output -n ${condaEnvironment} python -m app.tool_api --port 8787`;
const chromiumExecutablePath = process.env.QIANCRAFT_CHROMIUM_EXECUTABLE_PATH?.trim();
const canonicalMarketPlatforms = process.env.MEDIACRAWLER_PLATFORMS?.trim()
  || 'xhs,bili,wb';

export default defineConfig({
  testDir: './tests/ui',
  outputDir: '.playwright-results',
  fullyParallel: false,
  workers: 1,
  timeout: 45_000,
  expect: {
    timeout: 8_000,
    toHaveScreenshot: {
      animations: 'disabled',
      caret: 'hide',
      maxDiffPixelRatio: 0.002,
    },
  },
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: '.playwright-report' }],
  ],
  use: {
    baseURL: 'http://127.0.0.1:3000',
    colorScheme: 'light',
    contextOptions: { reducedMotion: 'reduce' },
    locale: 'zh-CN',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'off',
    launchOptions: chromiumExecutablePath
      ? { executablePath: chromiumExecutablePath }
      : undefined,
  },
  projects: [
    {
      name: 'desktop-chromium',
      use: {
        browserName: 'chromium',
        viewport: { width: 1440, height: 960 },
      },
    },
    {
      name: 'mobile-chromium',
      use: {
        browserName: 'chromium',
        deviceScaleFactor: 1,
        hasTouch: true,
        isMobile: true,
        viewport: { width: 390, height: 844 },
      },
    },
  ],
  webServer: [
    {
      command: pythonCommand,
      cwd: '..',
      env: {
        MEDIACRAWLER_PLATFORMS: canonicalMarketPlatforms,
      },
      url: 'http://127.0.0.1:8787/api/health',
      reuseExistingServer: true,
      timeout: 120_000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
    {
      command: 'pnpm exec vinext dev --hostname 127.0.0.1 --port 3000',
      cwd: '.',
      url: 'http://127.0.0.1:3000',
      reuseExistingServer: true,
      timeout: 120_000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
  ],
});
