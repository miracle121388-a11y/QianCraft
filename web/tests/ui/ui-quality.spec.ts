import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page, type TestInfo } from '@playwright/test';

const WORKSPACE_ID = 'guizhou-miao-demo';

const ROUTES = [
  { name: 'workbench', path: `/workflow?workspace=${WORKSPACE_ID}`, surface: '.workbench-shell' },
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

const STUDIO_ROUTES = [
  { name: '今日设计', path: '/', ready: '.studio-facts' },
  { name: '在地文化内容库', path: '/libraries/culture', ready: '.studio-document-head' },
  { name: '爆款产品形态库', path: '/libraries/forms', ready: '.studio-form-table' },
  { name: '自由组合', path: '/create', ready: '.studio-composer' },
  { name: '全部设计', path: '/designs', ready: '.studio-design-grid--archive' },
  { name: '运行中心', path: '/operations', ready: '.studio-operation-summary' },
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

async function computedSurface(page: Page, selector: string) {
  return page.locator(selector).evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      backgroundColor: style.backgroundColor,
      backgroundImage: style.backgroundImage,
      boxShadow: style.boxShadow,
    };
  });
}

function violationSummary(violations: Awaited<ReturnType<AxeBuilder['analyze']>>['violations']) {
  return violations.map((violation) => ({
    id: violation.id,
    impact: violation.impact,
    help: violation.help,
    targets: violation.nodes.map((node) => node.target),
  }));
}

test('结果优先工具的六个一级页面读取真实 API 且可审计', async ({ page }) => {
  for (const route of STUDIO_ROUTES) {
    await page.goto(route.path);
    await page.locator(route.ready).waitFor({ state: 'visible' });
    await expect(page.locator('.studio-shell')).toBeVisible();
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(route.name);
    const health = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      h1Count: document.querySelectorAll('h1').length,
      placeholderFacts: document.body.textContent?.includes('22 条文化记录 · 378 个市场官') ?? false,
    }));
    expect(health).toEqual({ overflow: 0, h1Count: 1, placeholderFacts: false });
    const accessibility = await new AxeBuilder({ page })
      .include('.studio-shell')
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze();
    expect(violationSummary(accessibility.violations), route.name).toEqual([]);
  }

  const overview = await page.request.get('http://127.0.0.1:8787/api/studio/overview');
  expect(overview.ok()).toBe(true);
  const payload = await overview.json() as {
    today: { designCount: number };
    libraries: { culture: { recordCount: number }; forms: { recordCount: number; sampleSize: number } };
  };
  expect(payload.libraries.culture.recordCount).toBe(22);
  expect(payload.libraries.forms).toMatchObject({ recordCount: 10, sampleSize: 378 });
  expect(payload.today.designCount).toBeGreaterThan(0);
  expect(payload.today.designCount).toBeLessThanOrEqual(3);
});

for (const route of ROUTES) {
  test(`${route.name} 满足可访问性、溢出与资源门槛`, async ({ page }, testInfo) => {
    await openRoute(page, route);

    const routeSurface = await page.locator(route.surface).evaluate((root) => {
      const style = getComputedStyle(root);
      return {
        backgroundColor: style.backgroundColor,
        backgroundImage: style.backgroundImage,
      };
    });
    expect(routeSurface.backgroundImage).toBe('none');
    expect(routeSurface.backgroundColor).not.toBe('rgb(255, 255, 255)');

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

test('工作台应用 Tonal Focus Review 功能色块', async ({ page }) => {
  await openRoute(page, ROUTES[0]);

  const colors = await page.locator('.workbench-shell--instrument').evaluate((shell) => {
    const background = (selector: string) => {
      const element = shell.querySelector(selector);
      if (!element) throw new Error(`Missing ${selector}`);
      return getComputedStyle(element).backgroundColor;
    };

    return {
      shell: getComputedStyle(shell).backgroundColor,
      command: background('.app-bar'),
      rail: background('.tool-rail'),
      canvas: background('.flow-stage'),
      inspector: background('.inspector-slot'),
    };
  });

  expect(colors).toEqual({
    shell: 'rgb(230, 226, 218)',
    command: 'rgb(217, 225, 232)',
    rail: 'rgb(215, 225, 220)',
    canvas: 'rgb(227, 232, 235)',
    inspector: 'rgb(231, 221, 212)',
  });
});

test('终审回归：1024px 不套用完整电脑端 C2 几何', async ({ page }) => {
  await page.setViewportSize({ width: 1024, height: 900 });
  await openRoute(page, ROUTES[0]);

  const geometry = await page.locator('.workbench-shell--instrument').evaluate((shell) => {
    const size = (selector: string) => {
      const element = shell.querySelector(selector);
      if (!element) throw new Error(`Missing ${selector}`);
      const rect = element.getBoundingClientRect();
      return { height: Math.round(rect.height), width: Math.round(rect.width) };
    };

    return {
      rail: size('.tool-rail'),
      dock: size('.tool-dock'),
      inspector: size('.inspector-slot'),
    };
  });

  expect(geometry).not.toMatchObject({
    rail: { width: 72 },
    dock: { height: 210 },
    inspector: { width: 330 },
  });
});

test('终审回归：Market 首个 KPI 使用固定 C2 画布色', async ({ page }) => {
  await openRoute(page, ROUTES[2]);
  expect(await computedSurface(page, '.market-kpi-row > div:first-child')).toEqual({
    backgroundColor: 'rgb(227, 232, 235)',
    backgroundImage: 'none',
    boxShadow: 'none',
  });
});

test('终审回归：Strategy 机会列表表头使用固定 C2 节点色', async ({ page }) => {
  await openRoute(page, ROUTES[3]);
  expect(await computedSurface(page, '.opportunity-list > header')).toEqual({
    backgroundColor: 'rgb(240, 238, 233)',
    backgroundImage: 'none',
    boxShadow: 'none',
  });
});

test('终审回归：Poster 首个拆解卡使用固定 C2 节点色', async ({ page }) => {
  await openRoute(page, ROUTES[9]);
  expect(await computedSurface(page, '.poster-breakdown-grid > article:first-child')).toEqual({
    backgroundColor: 'rgb(240, 238, 233)',
    backgroundImage: 'none',
    boxShadow: 'none',
  });
});

test('终审回归：Decision Studio 保持最大 14px 圆角且无阴影', async ({ page }) => {
  await openRoute(page, ROUTES[0]);
  await page.locator('.tool-rail').getByRole('button', { name: '人工决策' }).click();

  const studio = page.locator('.decision-studio');
  await expect(studio).toBeVisible();
  expect(await studio.evaluate((element) => {
    const style = getComputedStyle(element);
    return { borderRadius: style.borderRadius, boxShadow: style.boxShadow };
  })).toEqual({ borderRadius: '14px', boxShadow: 'none' });
});

test('终审回归：普通工作台键盘焦点使用 C2 primary', async ({ page }) => {
  await openRoute(page, ROUTES[0]);
  const evidenceButton = page.getByRole('button', { name: '证据库' });
  await evidenceButton.focus();

  const focusStyle = await evidenceButton.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      outlineColor: style.outlineColor,
      outlineStyle: style.outlineStyle,
      outlineWidth: style.outlineWidth,
    };
  });
  expect(focusStyle.outlineColor).toBe('rgb(52, 92, 125)');
  expect(focusStyle.outlineStyle).not.toBe('none');
  expect(Number.parseFloat(focusStyle.outlineWidth)).toBeGreaterThanOrEqual(2);
});

test('Decision Studio 使用 C2 大区与主操作语法', async ({ page }) => {
  await openRoute(page, ROUTES[0]);
  await page.locator('.tool-rail').getByRole('button', { name: '人工决策' }).click();

  const studio = page.locator('.decision-studio');
  await expect(studio).toBeVisible();
  const styles = await studio.evaluate((root) => {
    const computed = (selector?: string) => {
      const element = selector ? root.querySelector(selector) : root;
      if (!element) throw new Error(`Missing ${selector}`);
      const style = getComputedStyle(element);
      return {
        backgroundColor: style.backgroundColor,
        backgroundImage: style.backgroundImage,
        boxShadow: style.boxShadow,
      };
    };

    return {
      studio: computed(),
      header: computed('.decision-studio__header'),
      footer: computed('.decision-studio__footer'),
      stageNav: computed('.decision-stage-nav'),
      panel: computed('.decision-panel'),
      primary: computed('.decision-primary'),
    };
  });

  expect(styles.studio).toMatchObject({
    backgroundColor: 'rgb(230, 226, 218)',
    backgroundImage: 'none',
  });
  expect(styles.header).toMatchObject({
    backgroundColor: 'rgb(217, 225, 232)',
    backgroundImage: 'none',
  });
  expect(styles.footer).toMatchObject({
    backgroundColor: 'rgb(217, 225, 232)',
    backgroundImage: 'none',
  });
  expect(styles.stageNav).toMatchObject({
    backgroundColor: 'rgb(215, 225, 220)',
    backgroundImage: 'none',
  });
  expect(styles.panel).toMatchObject({
    backgroundColor: 'rgb(227, 232, 235)',
    backgroundImage: 'none',
  });
  expect(styles.primary).toEqual({
    backgroundColor: 'rgb(52, 92, 125)',
    backgroundImage: 'none',
    boxShadow: 'none',
  });
});

test('详情命令栏与历史概念资产不使用玻璃效果', async ({ page }) => {
  await page.route('**/api/workbench/workspaces/*/nodes/concept-a/detail', async (route) => {
    const response = await route.fetch();
    const payload = await response.json() as { node: { data: { status: string } } };
    payload.node.data.status = 'stale';
    await route.fulfill({ response, json: payload });
  });
  await openRoute(page, ROUTES[6]);

  const topbar = await page.locator('.detail-topbar').evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      backdropFilter: style.backdropFilter,
      backgroundImage: style.backgroundImage,
    };
  });
  expect.soft(topbar).toEqual({ backdropFilter: 'none', backgroundImage: 'none' });

  const assetNote = page.locator('.concept-asset-note');
  await expect(assetNote).toHaveText('保留上次成功资产 · 本轮未生成');
  expect.soft(await assetNote.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      backdropFilter: style.backdropFilter,
      backgroundColor: style.backgroundColor,
      backgroundImage: style.backgroundImage,
      boxShadow: style.boxShadow,
    };
  })).toEqual({
    backdropFilter: 'none',
    backgroundColor: 'rgb(240, 238, 233)',
    backgroundImage: 'none',
    boxShadow: 'none',
  });
});

test('采集主操作与星图外围控件使用可读 C2 状态', async ({ page }) => {
  await openRoute(page, ROUTES[1]);

  const computed = (selector: string, pseudo?: string) => page.locator(selector).first().evaluate((element, pseudoElement) => {
    const style = getComputedStyle(element, pseudoElement || undefined);
    return {
      backgroundColor: style.backgroundColor,
      backgroundImage: style.backgroundImage,
      borderColor: style.borderColor,
      boxShadow: style.boxShadow,
      color: style.color,
      opacity: style.opacity,
    };
  }, pseudo);

  const primary = page.locator('.collection-console--culture .collection-primary-action').first();
  await expect(primary).toHaveText(/^(立即运行|正在运行)$/);
  expect.soft(await computed('.collection-console--culture .collection-primary-action')).toMatchObject({
    backgroundColor: 'rgb(52, 92, 125)',
    backgroundImage: 'none',
    borderColor: 'rgb(52, 92, 125)',
    boxShadow: 'none',
    color: 'rgb(247, 248, 248)',
  });
  await primary.hover();
  expect.soft(await computed('.collection-console--culture .collection-primary-action')).toMatchObject({
    backgroundColor: 'rgb(52, 92, 125)',
    backgroundImage: 'none',
    borderColor: 'rgb(52, 92, 125)',
    boxShadow: 'none',
    color: 'rgb(247, 248, 248)',
  });

  expect.soft(await computed('.constellation-search')).toMatchObject({
    backgroundColor: 'rgb(240, 238, 233)',
    backgroundImage: 'none',
    borderColor: 'rgb(196, 200, 199)',
    boxShadow: 'none',
    color: 'rgb(32, 38, 44)',
  });
  expect.soft(await computed('.constellation-search input')).toMatchObject({
    backgroundColor: 'rgb(240, 238, 233)',
    backgroundImage: 'none',
    color: 'rgb(32, 38, 44)',
  });
  expect.soft(await computed('.constellation-search input', '::placeholder')).toMatchObject({
    color: 'rgb(98, 105, 112)',
    opacity: '1',
  });

  const zoom = page.getByRole('button', { name: '放大星图' });
  await zoom.hover();
  expect.soft(await computed('.constellation-controls button:hover')).toMatchObject({
    backgroundColor: 'rgb(203, 217, 230)',
    backgroundImage: 'none',
    borderColor: 'rgb(52, 92, 125)',
    boxShadow: 'none',
    color: 'rgb(32, 38, 44)',
  });

  const source = page.locator('.constellation-source-links a').first();
  await source.hover();
  expect.soft(await computed('.constellation-source-links a:hover')).toMatchObject({
    backgroundColor: 'rgb(203, 217, 230)',
    backgroundImage: 'none',
    borderColor: 'rgb(52, 92, 125)',
    boxShadow: 'none',
    color: 'rgb(32, 38, 44)',
  });
});

test('概念画廊使用 C2 卡片、按钮与当前标记', async ({ page }) => {
  await openRoute(page, ROUTES[5]);

  const computed = (selector: string, pseudo?: string) => page.locator(selector).first().evaluate((element, pseudoElement) => {
    const style = getComputedStyle(element, pseudoElement || undefined);
    return {
      backgroundColor: style.backgroundColor,
      backgroundImage: style.backgroundImage,
      borderColor: style.borderColor,
      boxShadow: style.boxShadow,
      color: style.color,
    };
  }, pseudo);

  expect.soft(await computed('.concept-gallery button')).toMatchObject({
    backgroundColor: 'rgb(240, 238, 233)',
    backgroundImage: 'none',
    borderColor: 'rgb(196, 200, 199)',
    boxShadow: 'none',
    color: 'rgb(32, 38, 44)',
  });
  const galleryButton = page.locator('.concept-gallery button').first();
  await galleryButton.hover();
  expect.soft(await computed('.concept-gallery button:hover')).toMatchObject({
    backgroundColor: 'rgb(203, 217, 230)',
    backgroundImage: 'none',
    borderColor: 'rgb(52, 92, 125)',
    boxShadow: 'none',
    color: 'rgb(32, 38, 44)',
  });
  expect.soft(await computed('.concept-gallery article.is-active')).toMatchObject({
    backgroundColor: 'rgb(203, 217, 230)',
    backgroundImage: 'none',
    borderColor: 'rgb(52, 92, 125)',
    boxShadow: 'none',
    color: 'rgb(32, 38, 44)',
  });
  expect.soft(await computed('.concept-gallery article.is-active', '::before')).toMatchObject({
    backgroundColor: 'rgb(52, 92, 125)',
    backgroundImage: 'none',
    boxShadow: 'none',
    color: 'rgb(247, 248, 248)',
  });
});

test('桌面工作区采用 C2 的命令栏、工具栏、底部抽屉和右侧 Inspector', async ({ page }) => {
  await openRoute(page, ROUTES[0]);

  const bounds = await page.locator('.workbench-shell--instrument').evaluate((shell) => {
    const rect = (selector: string) => {
      const element = shell.querySelector(selector);
      if (!element) throw new Error(`Missing ${selector}`);
      return element.getBoundingClientRect().toJSON();
    };

    return {
      command: rect('.app-bar'),
      rail: rect('.tool-rail'),
      canvas: rect('.flow-stage'),
      dock: rect('.tool-dock'),
      inspector: rect('.inspector-slot'),
    };
  });

  expect(bounds.command.height).toBe(60);
  expect(bounds.rail.width).toBe(72);
  expect(bounds.canvas.x).toBe(bounds.rail.right);
  expect(bounds.canvas.right).toBe(1440);
  expect(bounds.dock.height).toBe(210);
  expect(bounds.dock.x).toBe(bounds.rail.right);
  expect(bounds.dock.right).toBe(1440);
  expect(bounds.dock.y).toBe(bounds.canvas.y + bounds.canvas.height);
  expect(bounds.inspector.width).toBe(330);
  expect(bounds.inspector.right).toBe(1440);
});

test('桌面 C2 Dock、节点动作和 Inspector 不泄漏旧主题色', async ({ page }) => {
  await openRoute(page, ROUTES[0]);

  const computed = (selector: string) => page.locator(selector).first().evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      backgroundColor: style.backgroundColor,
      backgroundImage: style.backgroundImage,
      borderColor: style.borderColor,
      boxShadow: style.boxShadow,
      color: style.color,
    };
  });

  expect(await computed('.inspector-slot .inspector-icon')).toMatchObject({
    backgroundColor: 'rgb(52, 92, 125)',
    backgroundImage: 'none',
    boxShadow: 'none',
    color: 'rgb(240, 238, 233)',
  });

  await page.getByRole('button', { name: '方案资产', exact: true }).click();
  const asset = page.locator('.asset-dock__list > button').first();
  await asset.hover();
  expect(await computed('.asset-dock')).toMatchObject({
    backgroundColor: 'rgb(215, 225, 220)',
    backgroundImage: 'none',
    boxShadow: 'none',
    color: 'rgb(32, 38, 44)',
  });
  expect(await computed('.asset-dock .dock-heading')).toMatchObject({
    backgroundColor: 'rgb(215, 225, 220)',
    backgroundImage: 'none',
    borderColor: 'rgb(196, 200, 199)',
    boxShadow: 'none',
  });
  expect(await computed('.asset-dock .dock-heading b')).toMatchObject({
    backgroundColor: 'rgb(240, 238, 233)',
    backgroundImage: 'none',
    borderColor: 'rgb(196, 200, 199)',
    boxShadow: 'none',
  });
  expect(await computed('.asset-dock__list > button:hover')).toMatchObject({
    backgroundColor: 'rgb(203, 217, 230)',
    backgroundImage: 'none',
    borderColor: 'rgb(52, 92, 125)',
    boxShadow: 'none',
    color: 'rgb(32, 38, 44)',
  });
  expect(await computed('.asset-dock__list > button.is-active strong')).toMatchObject({
    color: 'rgb(32, 38, 44)',
  });

  await page.getByRole('button', { name: '节点历史', exact: true }).click();
  expect(await computed('.history-dock')).toMatchObject({
    backgroundColor: 'rgb(215, 225, 220)',
    backgroundImage: 'none',
    boxShadow: 'none',
    color: 'rgb(32, 38, 44)',
  });
  expect(await computed('.history-dock .dock-heading')).toMatchObject({
    backgroundColor: 'rgb(215, 225, 220)',
    backgroundImage: 'none',
    borderColor: 'rgb(196, 200, 199)',
    boxShadow: 'none',
  });
  expect(await computed('.history-dock__subject')).toMatchObject({
    backgroundColor: 'rgb(240, 238, 233)',
    backgroundImage: 'none',
    borderColor: 'rgb(196, 200, 199)',
    boxShadow: 'none',
  });
});

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
  await expect(cultureConsole.locator('.collection-candidates')).toContainText(
    '完成出处、字段证据和文化边界核验后才进入正式图谱',
  );
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
  await expect(
    marketConsole.locator('.collection-platform-matrix').getByText('等待授权', { exact: true }),
  ).toHaveCount(4);
  await expect(marketConsole).toContainText('失败轮不覆盖已核验快照');
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

test('Windows 基准环境：核心工作台与任务书视觉基线', async ({ page }, testInfo: TestInfo) => {
  test.skip(process.platform !== 'win32', '权威像素基线固定在 Windows Chromium；其他平台运行全部功能门。');
  await openRoute(page, ROUTES[0]);
  await expect(page).toHaveScreenshot(`workbench-${testInfo.project.name}.png`, {
    fullPage: false,
    mask: [page.locator('.research-monitor')],
    maskColor: '#f5f5f7',
  });

  await openRoute(page, ROUTES[4]);
  await expect(page).toHaveScreenshot(`brief-${testInfo.project.name}.png`, { fullPage: false });
});
