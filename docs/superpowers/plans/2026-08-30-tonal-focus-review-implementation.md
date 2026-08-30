# QianCraft Tonal Focus Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改变 QianCraft 后端、真实数据与现有功能接口的前提下，把工作台、Human Decision Studio 和九个节点详情重构为已批准的 C2 “Tonal Focus Review”，并交付可本地运行、可在桌面与手机浏览器验收的首版网站。

**Architecture:** 保留现有 `workbench.tsx`、React Flow、详情组件和 API 调用，把新的视觉世界放进一个由根布局最后加载的 `tonal-focus.css`，只在语义或可测试性需要时修改少量 JSX。现有 `globals.css` 继续作为结构与兼容基线，新主题通过 C2 令牌、桌面网格和响应式覆盖层收口，避免重新实现已经通过测试的业务逻辑。

**Tech Stack:** Next.js 16、React 19、TypeScript 5.9、React Flow 12、原生 CSS、Node test、Playwright、axe-core。

**Spec:** `docs/superpowers/specs/2026-08-30-tonal-focus-review-design.md`

## Global Constraints

- 保留全部现有 HTTP API、工作区持久化、九个真实节点、十条真实连线、节点动作、引用、深链、Decision Studio、文化关系图和持续采集状态。
- 不新增前端依赖，不修改 Python 后端，不复制构图中的虚构缩略图、时间、人名、标签或拓扑。
- 颜色固定为 shell `#E6E2DA`、command `#D9E1E8`、rail/evidence `#D7E1DC`、canvas `#E3E8EB`、Inspector `#E7DDD4`、node `#F0EEE9`、selected `#CBD9E6`、primary/focus `#345C7D`、text `#20262C`、secondary `#626970`、rule `#C4C8C7`。
- 不使用渐变、玻璃、模糊光晕、霓虹、高饱和环境色、民族纹样装饰或营销首屏；文化关系图是唯一功能性深色画布例外。
- 移动端可见交互目标至少 44×44px，页面不得横向溢出，弹层关闭后恢复焦点，状态不能只依赖颜色。
- 当前工作树包含用户已有未提交修改；执行期间不得运行 `git add`、`git commit`、`git reset` 或覆盖无关文件。

---

### Task 1: 建立可测试的 C2 主题契约

**Files:**
- Create: `web/app/tonal-focus.css`
- Modify: `web/app/layout.tsx`
- Modify: `web/tests/ui/ui-quality.spec.ts`

**Interfaces:**
- Consumes: 现有 `.workbench-shell--instrument`、`.app-bar`、`.tool-rail`、`.flow-stage`、`.tool-dock` 和 `.inspector-slot` DOM 类名。
- Produces: `--qc-shell`、`--qc-command`、`--qc-rail`、`--qc-canvas-tonal`、`--qc-inspector`、`--qc-node`、`--qc-selected`、`--qc-primary` 等全局 C2 CSS 变量；根布局最后加载的主题样式。

- [ ] **Step 1: 写入会失败的主题语义测试**

在 `web/tests/ui/ui-quality.spec.ts` 增加精确的首屏色块测试：

```ts
test('工作台应用 Tonal Focus Review 功能色块', async ({ page }) => {
  await openRoute(page, ROUTES[0]);
  const colors = await page.evaluate(() => {
    const color = (selector: string) => getComputedStyle(document.querySelector(selector)!).backgroundColor;
    return {
      shell: color('.workbench-shell--instrument'),
      command: color('.workbench-shell--instrument .app-bar'),
      rail: color('.workbench-shell--instrument .tool-rail'),
      canvas: color('.workbench-shell--instrument .flow-stage'),
      inspector: color('.workbench-shell--instrument .inspector-slot'),
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
```

- [ ] **Step 2: 运行单项测试并确认旧主题失败**

Run: `pnpm --dir web exec playwright test -g "Tonal Focus Review 功能色块" --project=desktop-chromium`

Expected: FAIL；当前 shell、command、rail、canvas、Inspector 仍返回白/冷灰的 Monochrome 颜色。

- [ ] **Step 3: 创建最小主题文件并在根布局最后导入**

在 `web/app/tonal-focus.css` 先建立唯一事实源：

```css
:root {
  --qc-shell: #e6e2da;
  --qc-command: #d9e1e8;
  --qc-rail: #d7e1dc;
  --qc-canvas-tonal: #e3e8eb;
  --qc-inspector: #e7ddd4;
  --qc-node: #f0eee9;
  --qc-selected: #cbd9e6;
  --qc-primary: #345c7d;
  --qc-text: #20262c;
  --qc-text-secondary: #626970;
  --qc-rule: #c4c8c7;
  --qc-success: #637e6a;
  --qc-warning: #b1844c;
  --qc-danger: #9a6757;
  --qc-neutral: #7b8086;
}

.workbench-shell--instrument { color: var(--qc-text); background: var(--qc-shell); }
.workbench-shell--instrument .app-bar { background: var(--qc-command); }
.workbench-shell--instrument .tool-rail { background: var(--qc-rail); }
.workbench-shell--instrument .flow-stage { background: var(--qc-canvas-tonal); }
.workbench-shell--instrument .inspector-slot { background: var(--qc-inspector); }
```

在 `web/app/layout.tsx` 的 `./globals.css` 后加入 `import './tonal-focus.css';`，并把 `impeccableDirectionContract` 与 `data-impeccable-contract` 更新为 C2 的 palette、story 与批准构图 SHA，不改变 metadata 或页面数据。

- [ ] **Step 4: 运行单项测试并确认通过**

Run: `pnpm --dir web exec playwright test -g "Tonal Focus Review 功能色块" --project=desktop-chromium`

Expected: PASS；五个大区均为固定 C2 色值。

---

### Task 2: 实现桌面 Focus Review 工作区

**Files:**
- Modify: `web/app/tonal-focus.css`
- Modify: `web/tests/ui/ui-quality.spec.ts`

**Interfaces:**
- Consumes: `activeDock` 产生的 `.workbench-grid--dock-open`、`showInspector` 产生的 `.workbench-grid--inspector-open`，以及现有关闭按钮和焦点恢复逻辑。
- Produces: 60px command bar、72px rail、210px lower context drawer、330px right Inspector；选择节点时不改变 `.flow-node` 几何。

- [ ] **Step 1: 写入会失败的桌面构图测试**

```ts
test('桌面工作区采用 C2 的命令栏、工具栏、底部抽屉和右侧 Inspector', async ({ page }) => {
  await openRoute(page, ROUTES[0]);
  const boxes = await page.evaluate(() => {
    const box = (selector: string) => document.querySelector(selector)!.getBoundingClientRect().toJSON();
    return { command: box('.app-bar'), rail: box('.tool-rail'), canvas: box('.flow-stage'), dock: box('.tool-dock'), inspector: box('.inspector-slot') };
  });
  expect(Math.round(boxes.command.height)).toBe(60);
  expect(Math.round(boxes.rail.width)).toBe(72);
  expect(Math.round(boxes.dock.height)).toBe(210);
  expect(Math.round(boxes.dock.y)).toBe(Math.round(boxes.canvas.y + boxes.canvas.height));
  expect(Math.round(boxes.inspector.width)).toBe(330);
  expect(Math.round(boxes.inspector.x + boxes.inspector.width)).toBe(1440);
});
```

- [ ] **Step 2: 运行单项测试并确认现有横向 Dock 失败**

Run: `pnpm --dir web exec playwright test -g "桌面工作区采用 C2" --project=desktop-chromium`

Expected: FAIL；现有 rail 为 56px，Dock 在左侧且 Inspector 为旧宽度。

- [ ] **Step 3: 用 CSS Grid 与绝对 Inspector 完成布局**

在 `web/app/tonal-focus.css` 加入：

```css
.workbench-shell--instrument .workbench-grid {
  position: relative;
  display: grid;
  grid-template: minmax(0, 1fr) 0 / 72px minmax(0, 1fr);
  grid-template-areas: "rail canvas" "rail dock";
  height: calc(100dvh - 60px);
  background: var(--qc-shell);
}
.workbench-shell--instrument .workbench-grid--dock-open {
  grid-template-rows: minmax(0, 1fr) 210px;
}
.workbench-shell--instrument .tool-rail { grid-area: rail; width: 72px; }
.workbench-shell--instrument .flow-stage { grid-area: canvas; min-width: 0; min-height: 0; }
.workbench-shell--instrument .tool-dock { grid-area: dock; display: none; min-width: 0; border-top: 1px solid var(--qc-rule); }
.workbench-shell--instrument .tool-dock.is-open { display: block; }
.workbench-shell--instrument .inspector-slot {
  position: absolute;
  z-index: 14;
  top: 0;
  right: 0;
  bottom: 0;
  display: none;
  width: 330px;
  border-left: 1px solid var(--qc-rule);
  box-shadow: -18px 0 40px rgb(65 70 72 / 10%);
}
.workbench-shell--instrument .inspector-slot.is-open { display: flex; }
```

把 app bar、phase switcher、workspace popover、canvas controls、MiniMap、context、legend、research monitor、nodes、selected node、handles、Dock 和 Inspector 的边框、背景、文字、状态和主动作映射到 C2 变量。节点固定 `background: var(--qc-node)`，选中节点固定 `background: var(--qc-selected)` 与 `border-color: var(--qc-primary)`；所有 `background-image` 为 `none`。

- [ ] **Step 4: 让底部证据内容适配 210px 横向工作面**

通过现有 `.knowledge-center`、`.culture-list`、`.market-ranking`、`.asset-dock` 和 `.history-dock` 类名建立横向滚动/多列布局；不删内容、不改变按钮事件：

```css
.workbench-shell--instrument .tool-dock > * { height: 100%; overflow: auto; }
.workbench-shell--instrument .tool-dock .knowledge-center { display: grid; grid-template-columns: minmax(220px, .72fr) minmax(420px, 1.5fr); }
.workbench-shell--instrument .tool-dock .culture-list,
.workbench-shell--instrument .tool-dock .market-ranking { grid-auto-flow: column; grid-auto-columns: minmax(220px, 1fr); overflow-x: auto; }
```

- [ ] **Step 5: 运行桌面构图、节点操作和焦点测试**

Run: `pnpm --dir web exec playwright test -g "桌面工作区采用 C2|工作台提供拖拽等价路径|画布支持指针平移" --project=desktop-chromium`

Expected: PASS；Dock 位于画布下方，Inspector 在右侧覆盖，画布操作和焦点链不回退。

---

### Task 3: 统一 Decision Studio 与九个详情页

**Files:**
- Modify: `web/app/tonal-focus.css`
- Modify: `web/tests/ui/ui-quality.spec.ts`

**Interfaces:**
- Consumes: 现有 `.decision-studio`、`.decision-stage-nav`、`.decision-panel`、`.node-detail-page`、`.detail-*`、`.collection-console-*`、`.constellation-*` 类名。
- Produces: 共享 C2 表单、按钮、状态、详情背景与焦点语法；文化关系图内部仍为深色功能画布。

- [ ] **Step 1: 扩展路由循环的视觉契约断言并确认失败**

在现有 `ROUTES` 循环内增加大区背景断言；工作台检查 shell，节点详情检查页面与 topbar：

```ts
const tonal = await page.evaluate(({ surface }) => {
  const root = document.querySelector(surface)!;
  const style = getComputedStyle(root);
  return { background: style.backgroundColor, image: style.backgroundImage };
}, route);
expect(tonal.image).toBe('none');
expect(tonal.background).not.toBe('rgb(255, 255, 255)');
```

Run: `pnpm --dir web exec playwright test -g "满足可访问性、溢出与资源门槛" --project=desktop-chromium`

Expected: FAIL；现有详情根面仍为纯白。

- [ ] **Step 2: 映射共享页面与控件令牌**

```css
.decision-studio,
.node-detail-page { color: var(--qc-text); background: var(--qc-shell); }
.decision-studio__header,
.decision-studio__footer,
.detail-topbar { border-color: var(--qc-rule); background: var(--qc-command); }
.decision-stage-nav,
.detail-side-rail { background: var(--qc-rail); }
.decision-panel,
.detail-main,
.detail-section { background: var(--qc-canvas-tonal); }
.primary-button,
.decision-primary,
.detail-primary,
.detail-run-button { border-color: var(--qc-primary); color: #f7f8f8; background: var(--qc-primary); }
```

继续覆盖输入框、次按钮、tabs、cards、table、空状态和 `success/cached/stale/warning/error/blocked`，使用低饱和状态色并保留文本/图标。`.constellation-stage` 的深色内部背景不改，只把外围 toolbar 和 inspector 映射到 C2。

- [ ] **Step 3: 运行十路由 axe/溢出/资源门和 Decision Studio 焦点门**

Run: `pnpm --dir web exec playwright test -g "满足可访问性、溢出与资源门槛|工作台提供拖拽等价路径" --project=desktop-chromium`

Expected: PASS；十个路由无 axe 违规、破图、缺失 alt 或横向溢出，Decision Studio Escape 与焦点归还仍通过。

---

### Task 4: 收口平板与手机覆盖层

**Files:**
- Modify: `web/app/tonal-focus.css`
- Modify: `web/tests/ui/ui-quality.spec.ts`

**Interfaces:**
- Consumes: 现有 mobile phase command、Dock/Inspector close buttons、`activeDock`/`showInspector` 状态和 culture constellation 显式操作模式。
- Produces: 761–1279px 可逆覆盖层与 <=760px 全高抽屉；44px 目标、无水平溢出、页面默认可滚动。

- [ ] **Step 1: 写入手机覆盖层测试并确认失败**

```ts
test('手机工作台把证据与 Inspector 作为可逆全高抽屉', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile-chromium');
  await openRoute(page, ROUTES[0]);
  await page.getByRole('button', { name: '证据库' }).click();
  const dock = page.locator('.tool-dock');
  await expect(dock).toBeVisible();
  expect(await dock.evaluate((element) => getComputedStyle(element).position)).toBe('fixed');
  await page.getByRole('button', { name: '关闭上下文工具面板' }).click();
  await expect(dock).toBeHidden();
  await expect(page.getByRole('button', { name: '证据库' })).toBeFocused();
});
```

Run: `pnpm --dir web exec playwright test -g "手机工作台把证据" --project=mobile-chromium`

Expected: FAIL；旧主题的默认状态或覆盖层位置不符合新契约。

- [ ] **Step 2: 增加两个响应式断点**

```css
@media (max-width: 1279px) {
  .workbench-shell--instrument .tool-dock,
  .workbench-shell--instrument .inspector-slot { position: fixed; z-index: 50; top: 60px; bottom: 0; }
  .workbench-shell--instrument .tool-dock { left: 72px; width: min(560px, calc(100vw - 72px)); }
  .workbench-shell--instrument .inspector-slot { right: 0; width: min(360px, calc(100vw - 72px)); }
  .workbench-shell--instrument .workbench-grid--dock-open { grid-template-rows: minmax(0, 1fr); }
}

@media (max-width: 760px) {
  .workbench-shell--instrument { min-width: 0; }
  .workbench-shell--instrument .app-bar { height: 56px; }
  .workbench-shell--instrument .workbench-grid { grid-template: minmax(0, 1fr) / 56px minmax(0, 1fr); height: calc(100dvh - 56px); }
  .workbench-shell--instrument .tool-rail { width: 56px; }
  .workbench-shell--instrument .tool-dock,
  .workbench-shell--instrument .inspector-slot { top: 56px; left: 56px; right: 0; width: auto; }
  .workbench-shell--instrument button,
  .workbench-shell--instrument summary { min-height: 44px; }
}
```

补齐移动 toolbar、滚动、safe-area、长中文换行和 reduced-motion/forced-colors 规则；不改变星图现有 `pan-y` 与“操作星图”模式。

- [ ] **Step 3: 运行手机布局、44px、星图手势和焦点测试**

Run: `pnpm --dir web exec playwright test --project=mobile-chromium`

Expected: 所有手机项目通过；文档/主内容 overflow 为 0，所有可见目标 >=43.5px，星图默认页面滚动和显式单指/双指模式通过。

---

### Task 5: 完成静态检查与有限视觉验收

**Files:**
- Modify after visual review: `web/tests/ui/ui-quality.spec.ts-snapshots/workbench-desktop-chromium-win32.png`
- Modify after visual review: `web/tests/ui/ui-quality.spec.ts-snapshots/workbench-mobile-chromium-mobile-chromium-win32.png`
- Modify after visual review: existing Brief desktop/mobile snapshots selected by Playwright

**Interfaces:**
- Consumes: Tasks 1–4 的主题、布局和响应式行为。
- Produces: 可重复的前端单测/类型/Lint/构建结果与经目视确认的 Windows Chromium 视觉基线。

- [ ] **Step 1: 运行不更新快照的快速质量门**

Run:

```powershell
pnpm --dir web test
pnpm --dir web typecheck
pnpm --dir web lint
pnpm --dir web build
```

Expected: Node tests 5/5、TypeScript 0 errors、ESLint 0 errors、Vinext production build 完成。

- [ ] **Step 2: 运行完整 Playwright 并只记录有意像素差异**

Run: `pnpm --dir web test:ui`

Expected: 交互、axe、溢出、资源和 44px 断言通过；只有工作台/Brief 的既有视觉快照因批准的主题变化失败。

- [ ] **Step 3: 在浏览器中做一次桌面/手机联合目视检查**

同时查看 1440×960 与 390×844：确认五个 C2 大区、真实九节点/十连线、底部证据抽屉、右侧 Inspector、Human Decision Studio、文化详情、市场详情和 Brief；浏览器控制台不得出现未处理异常，网络请求不得包含密钥。

- [ ] **Step 4: 一次性修复目视检查发现的问题并复验一次**

只修改 `web/app/tonal-focus.css` 或确有语义必要的现有 JSX；修复所有已发现的裁切、对比度、重叠、换行和命中区问题，然后重新运行相关 Playwright 项目。遵守 Impeccable 的两轮封顶，不开启无边界抛光循环。

- [ ] **Step 5: 更新并逐张查看四张 Windows 视觉基线**

Run: `pnpm --dir web test:ui:update`

Expected: 更新工作台与 Brief 的桌面/手机快照；逐张查看后再运行 `pnpm --dir web test:ui`，最终保持现有 35 passed / 1 intentionally skipped 或因新增两项测试得到对应增加后的通过数。

---

### Task 6: 同步正式设计记录与工作流

**Files:**
- Modify: `DESIGN.md`
- Modify: `.impeccable/surfaces/web-app-workbench-tsx.md`
- Modify: `docs/frontend_quality_workflow.md`
- Modify: `WORKFLOW.md`

**Interfaces:**
- Consumes: 最终运行代码、实际截图、测试计数和已批准的 C2 sidecar。
- Produces: 与实际网站一致的项目级设计系统、质量门和追加式工作流记录。

- [ ] **Step 1: 用最终代码替换过期 Monochrome 设计说明**

在 `DESIGN.md` 和 surface record 中记录 C2 颜色、60/72/210/330 布局、选中态、状态语法、响应式覆盖层、深色关系图例外和非字面构图边界。不要删除历史视觉探索文件。

- [ ] **Step 2: 更新前端质量流程中的视觉检查口径**

把 `docs/frontend_quality_workflow.md` 里“黑/白/冷灰/纯黑”的检查改为 Tonal Focus Review 的固定色块、主动作和禁止项；保留所有 axe、手势、焦点、44px、forced-colors 和快照纪律。

- [ ] **Step 3: 在 WORKFLOW 顶部追加实现日志并同步当前状态**

新增“C2 Tonal Focus Review 可运行首版”条目，写明变更原因、实际命令与准确通过数量、浏览器目视结果、未部署/未连接四平台/非量产边界和全部涉及文件。把当前状态从“实现尚未开始”改为“本地首版已实现”，但只有测试真实完成后才能写通过。

- [ ] **Step 4: 运行最终回归与文件一致性检查**

Run:

```powershell
pnpm --dir web quality
git diff --check -- web/app/layout.tsx web/app/tonal-focus.css web/tests/ui/ui-quality.spec.ts DESIGN.md PRODUCT.md .impeccable/surfaces/web-app-workbench-tsx.md docs/frontend_quality_workflow.md WORKFLOW.md
```

Expected: 全部前端门通过；diff 无空白错误；受跟踪文件的长 `sk-` 凭证安全模式扫描为 0 命中。最终在 `http://127.0.0.1:3000/` 保持 API 与网站运行，供用户直接查看。
