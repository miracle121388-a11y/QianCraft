import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page, type TestInfo } from '@playwright/test';

const WORKSPACE_ID = 'guizhou-miao-demo';

const ROUTES = [
  { name: 'workbench', path: `/?workspace=${WORKSPACE_ID}`, surface: '.workbench-shell' },
  { name: 'culture', path: `/nodes/culture?workspace=${WORKSPACE_ID}`, surface: '.node-detail-page' },
  { name: 'market', path: `/nodes/market?workspace=${WORKSPACE_ID}`, surface: '.node-detail-page' },
  { name: 'strategy', path: `/nodes/strategy?workspace=${WORKSPACE_ID}`, surface: '.node-detail-page' },
  { name: 'brief', path: `/nodes/brief?workspace=${WORKSPACE_ID}`, surface: '.node-detail-page' },
  { name: 'visual', path: `/nodes/visual?workspace=${WORKSPACE_ID}`, surface: '.node-detail-page' },
  { name: 'concept-a', path: `/nodes/concept-a?workspace=${WORKSPACE_ID}`, surface: '.node-detail-page' },
  { name: 'concept-b', path: `/nodes/concept-b?workspace=${WORKSPACE_ID}`, surface: '.node-detail-page' },
  { name: 'concept-c', path: `/nodes/concept-c?workspace=${WORKSPACE_ID}`, surface: '.node-detail-page' },
  { name: 'poster', path: `/nodes/poster?workspace=${WORKSPACE_ID}`, surface: '.node-detail-page' },
] as const;

async function openRoute(page: Page, route: (typeof ROUTES)[number]) {
  await page.goto(route.path);
  await page.locator(route.surface).waitFor({ state: 'visible' });
  await page.locator('img').evaluateAll(async (images) => {
    await Promise.all(images.map((image) => {
      const element = image as HTMLImageElement;
      return element.complete ? Promise.resolve() : element.decode().catch(() => undefined);
    }));
  });
  await page.waitForTimeout(120);
}

function violationSummary(violations: Awaited<ReturnType<AxeBuilder['analyze']>>['violations']) {
  return violations.map((violation) => ({
    id: violation.id,
    impact: violation.impact,
    help: violation.help,
    targets: violation.nodes.map((node) => node.target),
  }));
}

for (const route of ROUTES) {
  test(`${route.name} 满足可访问性、溢出与资源门槛`, async ({ page }, testInfo) => {
    await openRoute(page, route);

    const accessibility = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze();
    expect(violationSummary(accessibility.violations)).toEqual([]);

    const health = await page.evaluate(() => {
      const images = Array.from(document.images);
      return {
        documentOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        mainOverflow: (() => {
          const main = document.querySelector('main');
          return main ? main.scrollWidth - main.clientWidth : 0;
        })(),
        brokenImages: images.filter((image) => !image.complete || image.naturalWidth === 0).map((image) => image.src),
        missingAlt: images.filter((image) => !image.hasAttribute('alt')).map((image) => image.src),
        h1Count: document.querySelectorAll('h1').length,
      };
    });
    expect(health).toEqual({
      documentOverflow: 0,
      mainOverflow: 0,
      brokenImages: [],
      missingAlt: [],
      h1Count: 1,
    });

    if (testInfo.project.name === 'mobile-chromium') {
      const undersized = await page.locator('button, select, summary, a.detail-download, [role="button"]').evaluateAll((elements) => (
        elements.flatMap((element) => {
          if (element.closest('.react-flow__attribution')) return [];
          if (element.matches('a') && element.closest('p, li')) return [];
          const rect = element.getBoundingClientRect();
          const style = getComputedStyle(element);
          if (rect.width === 0 || rect.height === 0 || style.display === 'none' || style.visibility === 'hidden') return [];
          if (rect.width >= 43.5 && rect.height >= 43.5) return [];
          return [{
            name: element.getAttribute('aria-label') || element.textContent?.replace(/\s+/g, ' ').trim(),
            width: Math.round(rect.width),
            height: Math.round(rect.height),
          }];
        })
      ));
      expect(undersized).toEqual([]);
    }
  });
}

test('工作台提供拖拽等价路径、中文画布语义与完整弹层焦点', async ({ page }) => {
  await openRoute(page, ROUTES[0]);

  const evidenceTool = page.getByRole('button', { name: '证据库' });
  const addEvidenceButtons = page.getByRole('button', { name: /添加到画布/ });
  if (await addEvidenceButtons.count() === 0) await evidenceTool.click();
  const draggableEvidence = page.locator('.knowledge-center [draggable="true"]');
  await expect(addEvidenceButtons).toHaveCount(await draggableEvidence.count());
  await expect(page.locator('body')).not.toContainText('Press enter or space');

  const initialNodeCount = await page.locator('.react-flow__node').count();
  await addEvidenceButtons.first().click();
  await expect(page.locator('.react-flow__node')).toHaveCount(initialNodeCount + 1);
  await expect(page.getByRole('status')).toContainText('已在画布创建');

  const graphTrigger = page.getByRole('button', { name: '展开图谱' });
  if (!(await graphTrigger.isVisible())) await evidenceTool.click();
  await graphTrigger.click();
  const graphDialog = page.getByRole('dialog', { name: '贵州文化知识图谱' });
  await expect(graphDialog).toBeVisible();
  await expect(graphDialog.getByRole('button', { name: '关闭图谱' })).toBeFocused();
  const graphAccessibility = await new AxeBuilder({ page }).include('.graph-overlay').analyze();
  expect(violationSummary(graphAccessibility.violations)).toEqual([]);
  await page.keyboard.press('Shift+Tab');
  await expect.poll(() => graphDialog.evaluate((dialog) => dialog.contains(document.activeElement))).toBe(true);
  await page.keyboard.press('Escape');
  await expect(graphDialog).toBeHidden();
  await expect(graphTrigger).toBeFocused();

  await page.locator('.workspace-command summary').click();
  const newWorkspaceTrigger = page.getByRole('button', { name: '新建' });
  await newWorkspaceTrigger.click();
  const workspaceDialog = page.getByRole('dialog', { name: '创建新的文化文创链路' });
  await expect(workspaceDialog).toBeVisible();
  await expect(workspaceDialog.getByRole('textbox', { name: '工作区名称' })).toBeFocused();
  const workspaceAccessibility = await new AxeBuilder({ page }).include('.workspace-dialog').analyze();
  expect(violationSummary(workspaceAccessibility.violations)).toEqual([]);
  await page.keyboard.press('Shift+Tab');
  await expect(workspaceDialog.getByRole('button', { name: '创建并打开' })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(workspaceDialog).toBeHidden();
  await expect(newWorkspaceTrigger).toBeFocused();

  const decisionTrigger = page.locator('.tool-rail').getByRole('button', { name: '人工决策' });
  await decisionTrigger.click();
  const decisionDialog = page.getByRole('dialog', { name: '人工决策工作台' });
  await expect(decisionDialog).toBeVisible();
  const decisionAccessibility = await new AxeBuilder({ page }).include('.decision-studio').analyze();
  expect(violationSummary(decisionAccessibility.violations)).toEqual([]);
  await page.keyboard.press('Escape');
  await expect(decisionDialog).toBeHidden();
  await expect(decisionTrigger).toBeFocused();
});

test('画布支持指针平移和节点键盘移动', async ({ page }, testInfo) => {
  await openRoute(page, ROUTES[0]);

  if (testInfo.project.name === 'desktop-chromium') {
    const viewport = page.locator('.react-flow__viewport');
    const pane = page.locator('.react-flow__pane');
    const paneBox = await pane.boundingBox();
    expect(paneBox).not.toBeNull();
    const transformBeforePan = await viewport.getAttribute('style');
    await page.mouse.move(paneBox!.x + paneBox!.width * 0.55, paneBox!.y + paneBox!.height * 0.52);
    await page.mouse.down();
    await page.mouse.move(paneBox!.x + paneBox!.width * 0.65, paneBox!.y + paneBox!.height * 0.46, { steps: 6 });
    await page.mouse.up();
    await expect.poll(() => viewport.getAttribute('style')).not.toBe(transformBeforePan);
  }

  const firstNode = page.locator('.react-flow__node').first();
  const nodeBefore = await firstNode.getAttribute('style');
  await firstNode.focus();
  await firstNode.press('Enter');
  await firstNode.press('ArrowRight');
  await expect.poll(() => firstNode.getAttribute('style')).not.toBe(nodeBefore);
});

test('知识星图支持检索、选点、缩放和画布平移', async ({ page }, testInfo) => {
  await openRoute(page, ROUTES[1]);

  const search = page.getByRole('textbox', { name: '搜索文化记录' });
  await search.fill('蜡染');
  await expect(page.getByText('1 / 22', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: '苗族蜡染技艺，传统技艺，3 条来源', exact: true }).click();
  await expect(page.locator('.constellation-inspector h3')).toHaveText('苗族蜡染技艺');
  await expect(page.locator('.constellation-inspector')).toContainText('文化边界');
  await search.fill('');

  const viewport = page.locator('.constellation-stage > svg > g');
  const reset = page.getByRole('button', { name: '重置星图视图' });
  await reset.click();
  const initialTransform = await viewport.getAttribute('transform');
  await page.getByRole('button', { name: '缩小星图' }).click();
  await expect.poll(() => viewport.getAttribute('transform')).not.toBe(initialTransform);
  await reset.click();

  if (testInfo.project.name === 'desktop-chromium') {
    const canvas = page.getByRole('application', { name: /贵州在地文化关系星图/ });
    const box = await canvas.boundingBox();
    expect(box).not.toBeNull();
    await canvas.focus();
    const transformBeforeKeyboard = await viewport.getAttribute('transform');
    await canvas.press('ArrowRight');
    await expect.poll(() => viewport.getAttribute('transform')).not.toBe(transformBeforeKeyboard);
    await reset.click();

    const transformBeforeWheel = await viewport.getAttribute('transform');
    await canvas.hover();
    await page.mouse.wheel(0, -180);
    await expect.poll(() => viewport.getAttribute('transform')).not.toBe(transformBeforeWheel);
    await reset.click();

    const transformBeforePan = await viewport.getAttribute('transform');
    await page.mouse.move(box!.x + box!.width * 0.18, box!.y + box!.height * 0.42);
    await page.mouse.down();
    await page.mouse.move(box!.x + box!.width * 0.3, box!.y + box!.height * 0.49, { steps: 6 });
    await page.mouse.up();
    await expect.poll(() => viewport.getAttribute('transform')).not.toBe(transformBeforePan);
  } else {
    const canvas = page.getByRole('application', { name: /贵州在地文化关系星图/ });
    const touchActionBefore = await canvas.evaluate((element) => getComputedStyle(element).touchAction);
    expect(touchActionBefore).toContain('pan-y');
    const scroller = page.locator('.node-detail-page');
    await scroller.evaluate((element) => { element.scrollTop = 0; });
    await page.locator('.constellation-instruction').hover();
    await page.mouse.wheel(0, 320);
    await expect.poll(() => scroller.evaluate((element) => element.scrollTop)).toBeGreaterThan(0);

    const cdp = await page.context().newCDPSession(page);
    const touchToggle = page.locator('.constellation-instruction button');
    await page.getByRole('button', { name: '操作星图' }).click();
    await expect(touchToggle).toHaveAttribute('aria-pressed', 'true');
    await expect.poll(() => canvas.evaluate((element) => getComputedStyle(element).touchAction)).toBe('none');
    const box = await canvas.boundingBox();
    expect(box).not.toBeNull();
    const centerX = box!.x + box!.width * 0.5;
    const centerY = Math.max(90, Math.min(760, box!.y + box!.height * 0.55));
    const transformBeforeSinglePan = await viewport.getAttribute('transform');
    await cdp.send('Input.dispatchTouchEvent', {
      type: 'touchStart',
      touchPoints: [{ id: 1, x: centerX - 45, y: centerY }],
    });
    await cdp.send('Input.dispatchTouchEvent', {
      type: 'touchMove',
      touchPoints: [{ id: 1, x: centerX + 35, y: centerY + 40 }],
    });
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await expect.poll(() => viewport.getAttribute('transform')).not.toBe(transformBeforeSinglePan);
    await reset.click();

    const transformBeforePinch = await viewport.getAttribute('transform');
    await cdp.send('Input.dispatchTouchEvent', {
      type: 'touchStart',
      touchPoints: [
        { id: 1, x: centerX - 28, y: centerY },
        { id: 2, x: centerX + 28, y: centerY },
      ],
    });
    await cdp.send('Input.dispatchTouchEvent', {
      type: 'touchMove',
      touchPoints: [
        { id: 1, x: centerX - 58, y: centerY },
        { id: 2, x: centerX + 58, y: centerY },
      ],
    });
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await expect.poll(() => viewport.getAttribute('transform')).not.toBe(transformBeforePinch);
    await page.getByRole('button', { name: '完成' }).click();
    await expect.poll(() => canvas.evaluate((element) => getComputedStyle(element).touchAction)).toContain('pan-y');
  }
});

test('持续采集页面区分已核验知识、候选资料与授权阻断', async ({ page }) => {
  await openRoute(page, ROUTES[1]);
  const cultureConsole = page.locator('.collection-console--culture');
  await expect(cultureConsole).toContainText('22');
  await expect(cultureConsole).toContainText('32');
  await expect(cultureConsole).toContainText('文化候选队列');
  await expect(cultureConsole).toContainText('需人工核验后结构化');
  await page.route('**/api/collection/candidates', (route) => (
    route.request().method() === 'POST' ? route.abort('connectionfailed') : route.continue()
  ));
  const candidateUrl = cultureConsole.getByRole('textbox', { name: '公开来源地址' });
  const candidateTitle = cultureConsole.getByRole('textbox', { name: '资料标题' });
  await candidateUrl.fill('https://example.org/culture/retry-after-error');
  await candidateTitle.fill('失败后仍应保留的候选标题');
  await cultureConsole.getByRole('button', { name: '加入候选' }).click();
  await expect(cultureConsole.locator('.collection-error')).toBeVisible();
  await expect(candidateUrl).toHaveValue('https://example.org/culture/retry-after-error');
  await expect(candidateTitle).toHaveValue('失败后仍应保留的候选标题');
  await page.unroute('**/api/collection/candidates');

  await openRoute(page, ROUTES[2]);
  const marketDisclosure = page.locator('.collection-console-disclosure');
  await expect(marketDisclosure).not.toHaveAttribute('open', '');
  await marketDisclosure.locator('summary').click();
  const marketConsole = page.locator('.collection-console--market');
  await expect(marketConsole).toBeVisible();
  await expect(marketConsole.locator('.collection-platform-matrix')).toHaveAttribute('aria-label', '四平台授权与采集状态');
  await expect(marketConsole.getByText('等待授权', { exact: true })).toHaveCount(5);
  await expect(marketConsole).toContainText('不会把历史快照写成实时结果');
  await expect(page.getByText('378', { exact: true })).toBeVisible();
});

test('Windows 高对比模式保留选中态与星图层级', async ({ page }) => {
  await page.emulateMedia({ forcedColors: 'active' });
  await openRoute(page, ROUTES[0]);
  const evidenceButton = page.getByRole('button', { name: '证据库' });
  await evidenceButton.focus();
  const focusStyle = await evidenceButton.evaluate((element) => {
    const style = getComputedStyle(element);
    return { outlineStyle: style.outlineStyle, outlineWidth: style.outlineWidth };
  });
  expect(focusStyle.outlineStyle).not.toBe('none');
  expect(Number.parseFloat(focusStyle.outlineWidth)).toBeGreaterThanOrEqual(2);

  await openRoute(page, ROUTES[1]);
  const centerColors = await page.locator('.constellation-core').evaluate((element) => {
    const circle = element.querySelector('circle');
    const label = element.querySelector('text');
    return {
      circle: circle ? getComputedStyle(circle).fill : '',
      label: label ? getComputedStyle(label).fill : '',
    };
  });
  expect(centerColors.circle).not.toBe(centerColors.label);
  const nodeColors = await page.locator('.constellation-record-nodes').evaluate((element) => {
    const active = element.querySelector('g.is-active circle.is-node');
    const inactive = element.querySelector('g:not(.is-active) circle.is-node');
    return {
      active: active ? getComputedStyle(active).fill : '',
      inactive: inactive ? getComputedStyle(inactive).fill : '',
    };
  });
  expect(nodeColors.active).not.toBe(nodeColors.inactive);
});

test('持续采集轮询断线后不会保留在线假象', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-chromium', '连接状态只需在一套真实浏览器环境验证');
  await openRoute(page, ROUTES[1]);
  await expect(page.locator('.collection-overview-strip').getByText('在线', { exact: true })).toBeVisible();
  await page.route('**/api/collection/**', (route) => route.abort('connectionfailed'));
  await expect(page.getByText('采集控制面连接中断', { exact: true })).toBeVisible({ timeout: 16_000 });
  await expect(page.locator('.collection-overview-strip').getByText('中断', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: '暂停全部' })).toBeDisabled();
  const reconnectBox = await page.locator('.collection-error').getByRole('button', { name: '重新连接' }).boundingBox();
  expect(reconnectBox?.height ?? 0).toBeGreaterThanOrEqual(44);
});

test('采集控制面初次连接失败提供可触达恢复动作', async ({ page }) => {
  await page.route('**/api/collection/**', (route) => route.abort('connectionfailed'));
  await openRoute(page, ROUTES[1]);
  await expect(page.getByText('持续采集控制面不可用', { exact: true })).toBeVisible();
  const reconnect = page.locator('.collection-console--loading').getByRole('button', { name: '重新连接' });
  await expect(reconnect).toBeVisible();
  const reconnectBox = await reconnect.boundingBox();
  expect(reconnectBox?.height ?? 0).toBeGreaterThanOrEqual(44);
});

test('核心工作台与任务书视觉基线', async ({ page }, testInfo: TestInfo) => {
  await openRoute(page, ROUTES[0]);
  await expect(page).toHaveScreenshot(`workbench-${testInfo.project.name}.png`, { fullPage: false });

  await openRoute(page, ROUTES[4]);
  await expect(page).toHaveScreenshot(`brief-${testInfo.project.name}.png`, { fullPage: false });
});
