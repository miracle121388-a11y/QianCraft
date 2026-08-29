# QianCraft 前端质量工作流

> 适用版本：0.9.0 及以后  
> 适用范围：`web/` 工作台、九个节点详情、Human Decision Studio 与覆盖层  
> 本文是本地开发与验收标准，不代表部署、WCAG 认证或生产发布。

## 1. 质量目标

QianCraft 是工具，不是官网。前端质量按以下顺序判断：

1. 当前任务、证据状态和下一步动作是否明确。
2. 画布、节点、Dock、Inspector 与弹层是否能直接、可逆地操作。
3. 桌面和手机是否都能完成同一核心任务，而不是把桌面界面机械缩小。
4. 黑、白、冷灰系统 chrome 是否稳定；来源图片可保留内容色。
5. 事实、缓存、失败、人工决策和生产前边界是否没有被视觉包装掩盖。

## 2. 外部基准

本工作流只采用官方或第一方资料作为实现基准：

- [WCAG 2.2 新增成功准则](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/)：拖拽操作必须有不依赖拖拽的等价路径；焦点、目标尺寸与认证等新准则进入审计范围。QianCraft 在最低标准之上继续保留移动端 44×44px 项目门槛。
- [React Flow Accessibility](https://reactflow.dev/learn/advanced-use/accessibility)：节点键盘操作、ARIA 文案和可聚焦语义属于画布组件本身；[React Flow Performance](https://reactflow.dev/learn/advanced-use/performance)要求避免无关重渲染并稳定节点组件。
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)、[Accessibility Testing](https://playwright.dev/docs/accessibility-testing) 与 [Visual Comparisons](https://playwright.dev/docs/test-snapshots)：从用户可见语义测试、隔离测试状态，并把 axe 与像素回归作为互补门槛。
- [web.dev INP](https://web.dev/articles/optimize-inp) 与 [CLS](https://web.dev/articles/optimize-cls)：长任务、布局跳动和迟到的图片尺寸会直接破坏工具操作；节点组件保持稳定几何，非首屏图片异步解码/懒加载。
- [Apple HIG: Focus and Selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection/) 与 [Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)：借鉴其清晰焦点、选择和工具栏秩序，不复制官网排版或营销叙事。

## 3. 自动质量门

在 `web/` 运行：

```powershell
# 首次准备 Chromium
pnpm exec playwright install chromium

# 日常快速检查
pnpm typecheck
pnpm lint
pnpm test

# 自动启动本地 API 与 Web，执行桌面/手机 UI 门槛
pnpm test:ui

# 完整前端门槛
pnpm quality
```

`pnpm test:ui` 当前覆盖 1440×960 桌面 Chromium 与 390×844 移动 Chromium；0.9.0 完整运行实际为 35 项通过，另有 1 项移动项目的有意跳过（断线语义只在桌面 Chromium 重复验证一次）：

- `/` 与九个 `/nodes/*` 路由各自检查 WCAG A/AA/2.2 AA axe 规则、唯一 `h1`、破图、缺失 `alt`、文档/主内容横向溢出。
- 手机检查可见主要按钮、选择器、summary、下载动作和 `role=button` 的 44×44px 命中区。
- 工作台检查证据拖拽与“添加到画布”点击/键盘等价路径、中文画布语义、图谱/Workspace/Decision Studio 的焦点圈、Escape 关闭与焦点归还。
- 检查桌面指针平移、桌面/手机节点键盘移动、Windows forced-colors 焦点轮廓。
- 知识星图检查搜索聚焦、选点、按钮/真实滚轮缩放、桌面拖动与键盘平移；移动项目真实滚动详情容器，并以 CDP touch point 验证显式操作模式的单指平移、双指缩放及退出后恢复 `pan-y`。
- 持续采集检查正式知识/候选/历史快照分层、四平台授权阻断、候选提交失败后输入保留，以及 12 秒轮询断线后旧“在线”状态立即失效、写操作禁用。
- forced-colors 除工作台焦点外，还验证星图中心文字与底面、普通记录与选中记录保持不同系统色。
- 对工作台和 Brief 在桌面/手机保存四张 Windows Chromium 视觉基线。

0.9.0 同轮完整验证还包括 Python 53 passed、前端单测 5 passed，以及 typecheck、lint、Vinext production build、Ruff、`bash -n deploy/start-zeabur.sh`、`uv lock --check` 和 `git diff --check` 通过；这些结果是本地代码与运行契约证据，不等于 0.9.0 已部署。受保护线上实例仍为 0.8.0。

失败时报告写入 `web/.playwright-report/`，截图、axe 上下文和 trace 写入 `web/.playwright-results/`；两者不进 Git。

## 4. 视觉基线更新纪律

只有确认变更是有意且已经人工看过时，才运行：

```powershell
pnpm test:ui:update
```

更新后必须逐张查看 `web/tests/ui/ui-quality.spec.ts-snapshots/`，至少确认：

- 没有米色、暖纸色、蓝/靛蓝系统 chrome 回流。
- 选中态、焦点和唯一主动作仍为黑色高对比语法。
- 节点选择前后几何不变，画布仍是最大工作面。
- 390px 下没有桌面多栏的机械缩小，也没有水平溢出或被裁掉的关键动作。
- 图片颜色只存在于来源内容，图片外框、按钮和状态仍为无彩系统。
- 文化星图在手机上默认不会困住页面滚动，“操作星图”入口可见，进入后单指/双指说明准确，初始选中标签可读。
- 市场页首屏先看到 378 条历史样本、时间窗和平台分布；完整采集控制面可展开但不压住证据理解。

路由或信息架构发生较大变化时，另用 Playwright CLI 把全部 10 个桌面路由和关键移动状态保存到 `web/output/playwright/` 并逐张目视。该目录是本地审阅产物，不代替像素基线或线上复验。

像素基线与操作系统、浏览器版本和字体渲染有关；不能用另一平台生成的像素差异直接覆盖 Windows 基线。

## 5. 人工确认清单

自动门通过后，对有交互或信息架构变化的更新再做一次有限人工确认：

- 320、390、768、1024、1440px 各看一个代表状态；路由结构变化时复查全部十个路由。
- 主键拖动空白画布、节点拖动、Shift 框选和滚轮缩放不互相抢手势；知识星图手机默认允许页面纵向滚动，显式操作模式才接管单指平移与双指缩放。
- 键盘依次进入命令栏、工具轨、Dock、画布节点、Inspector 与弹层；焦点始终可见。
- 图谱、Workspace、Decision Studio 打开后焦点进入内部，Tab 不逃逸，Escape 后回到触发器。
- 开启减少动态与 Windows 高对比模式，确认状态和选中态不只依赖动画、透明度或颜色。
- 核查 live/cache/stale/warning/error、文化边界和生产前声明，没有因排版收口而被隐藏。

## 6. 当前边界

- axe 只能发现一部分无障碍问题；自动门通过不等于 WCAG 认证，仍需真实屏幕阅读器与残障用户测试。
- 自动化已经覆盖知识星图的合成双触点缩放与 44px 门槛，但 CDP 触点不能替代真实手机上的手掌误触、浏览器地址栏变化和辅助技术复核。
- 当前没有把 Lighthouse、真实用户 INP 或超大图谱压力测试设为阻断门；节点数量和数据规模显著增长时需要单独做性能基线。
- 视觉快照使用 `guizhou-miao-demo` 的本地真实 HTTP 数据，不能替代线上认证后复验。
- 本流程止于本地产品前端质量，不授权部署、商业图稿批准、工厂下单或制造/合规就绪声明。
