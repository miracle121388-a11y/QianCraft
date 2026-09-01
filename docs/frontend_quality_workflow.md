# QianCraft 前端质量工作流

> 适用版本：0.10.0 及以后
>
> 当前 C2 验收范围：1440×960 电脑端；功能门跨 Windows/macOS/Linux，像素基线固定为 Windows Chromium
>
> 本文是本地开发与验收标准，不代表部署、WCAG 认证、手机/平板适配或生产发布。

## 1. 质量目标

QianCraft 是结果优先的证据工具，不是官网。前端质量按以下顺序判断：

1. 首页是否先展示真实两库计数、当天设计和自动化，而不是中间工作流。
2. 文化、形态、设计与运行状态能否逐条追溯，错误时是否拒绝占位成功。
3. 自由组合与设计版本编辑是否直接、可逆，旧版本是否保留。
4. 高级画布、节点、Dock、Inspector 与弹层是否仍能在 `/workflow` 操作。
5. Tonal Focus 固定色块是否准确承担区域、选中、焦点和状态职责。
6. 当前目标视口是否通过语义、交互、静态和像素门。

0.10.0 保留旧 C2 的 desktop-only 视觉基线，同时给结果优先主界面提供窄屏布局。窄屏 CSS 存在不等于已经完成真实 mobile/tablet 产品验收；当前权威 UI 门仍是 Windows desktop Chromium。

## 2. 外部基准

本工作流只采用官方或第一方资料作为实现基准：

- [WCAG 2.2 新增成功准则](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/)：拖拽操作必须有不依赖拖拽的等价路径；焦点、目标尺寸与认证等新准则进入审计范围。
- [React Flow Accessibility](https://reactflow.dev/learn/advanced-use/accessibility)：节点键盘操作、ARIA 文案和可聚焦语义属于画布组件本身；[React Flow Performance](https://reactflow.dev/learn/advanced-use/performance)要求避免无关重渲染并稳定节点组件。
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)、[Accessibility Testing](https://playwright.dev/docs/accessibility-testing) 与 [Visual Comparisons](https://playwright.dev/docs/test-snapshots)：从用户可见语义测试、隔离测试状态，并把 axe 与像素回归作为互补门槛。
- [web.dev INP](https://web.dev/articles/optimize-inp) 与 [CLS](https://web.dev/articles/optimize-cls)：长任务、布局跳动和迟到的图片尺寸会直接破坏工具操作；节点组件保持稳定几何，非首屏图片异步解码/懒加载。
- [Apple HIG: Focus and Selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection/) 与 [Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)：借鉴清晰焦点、选择和工具栏秩序，不复制官网排版或营销叙事。

## 3. C2 固定视觉合同

结果优先 Studio 与旧工作台共享以下计算样式令牌；几何要求按产品层级分别判断：

| Role | Value | Required surface |
|---|---:|---|
| shell | `#E6E2DA` | 应用外壳 |
| command | `#D9E1E8` | Studio 86px 顶栏 / 旧工作台 60px command bar |
| rail | `#D7E1DC` | Studio 224px 一级导航 / 旧工作台 72px rail 与 210px Dock |
| canvas | `#E3E8EB` | React Flow / 详情主工作面 |
| inspector | `#E7DDD4` | 330px Inspector |
| node | `#F0EEE9` | 节点、字段、次操作 |
| selected | `#CBD9E6` | 选中/活动面 |
| primary | `#345C7D` | 主动作、选中边、焦点 |
| text / secondary | `#20262C` / `#626970`; Studio compact secondary `#565E65` | 正文与辅助信息；Studio 小字在全部浅色表面保持至少 4.5:1 |
| rule | `#C4C8C7` | 边线和分隔 |
| success / warning / danger / neutral | `#637E6A` / `#B1844C` / `#9A6757` / `#7B8086` | 状态标记，必须配合文字与形状 |

必须检查：

- Studio 的 224px 标注导航、真实事实卡、结果卡、运行状态和每页唯一主动作。
- `/workflow` 的 60px command、72px rail、210px bottom Dock、330px right Inspector 桌面几何。
- selected 面 + primary 边线/handle；选择前后节点尺寸、坐标和拓扑不变。
- 每个任务区只有一个 primary 主动作；次操作使用 node/rule/text。
- `live/cache/stale/warning/error/degraded/blocked/offline` 文字、时间边界、原因和可恢复路径未被隐藏。
- 文化关系星图内部 `#070708` 深色画布是唯一功能性深色例外；外围搜索、控件、图例和证据 Inspector 使用 C2。

明确禁止：

- 大面积纯白或近白页面/面板。
- gradient、mesh gradient、玻璃、`backdrop-filter`、光晕、霓虹和高饱和环境色。
- 没有导航、区域、选择或状态职责的装饰色、缩略图和网格。
- 普通卡片阴影、选中节点抬升/扩张、以颜色单独表达状态。
- 把批准构图中的示意人物、时间、缩略图、文件名、数字或拓扑复制为产品事实。

## 4. 自动质量门

在 `web/` 运行：

```powershell
# 首次准备 Chromium
pnpm exec playwright install chromium

# 日常静态与单元门
pnpm test
pnpm typecheck
pnpm lint
pnpm build

# 当前 C2 电脑端完整 UI 门
pnpm exec playwright test --project=desktop-chromium

# 只有未来重新获得 mobile/tablet 授权并完成相应实现时，才运行双项目总门
pnpm test:ui
pnpm quality
```

0.10.0 的 `desktop-chromium` 在 1440×960 定义 32 项：31 项功能门在支持 Chromium 的系统执行，最后 1 项旧工作台像素门只在 Windows 执行。覆盖：

- 新 Studio 六个一级路由的真实 API 载入、22/10/378 计数、每日结果数量、axe A/AA/2.2 AA、唯一 `h1` 和横向溢出；运行中心受限高度的阻断列表是可命名、可聚焦、可键盘滚动的区域。
- `/workflow` 与九个 `/nodes/*` 路由的 axe、唯一 `h1`、破图、缺失 `alt`、文档/主内容横向溢出。
- 真实 C2 五色表面、60/72/210/330 几何、Asset/History Dock、节点动作、Inspector、Decision Studio、九个详情页、collection primary、星图外围控件和 concept gallery 的计算样式。
- 证据拖拽与“添加到画布”点击/键盘等价路径、中文画布语义、Workspace/Decision Studio/图谱的焦点圈、Escape 关闭与焦点归还。
- 工作台指针平移、节点键盘移动、Windows forced-colors 焦点与星图层级。
- 知识星图搜索聚焦、选点、按钮/真实滚轮缩放、拖动画布与键盘平移。
- 持续采集的正式知识/候选/历史快照分层、授权阻断、输入保留、轮询断线后旧在线状态失效与写操作禁用。
- 云端授权浏览器卡片只在服务端报告入口与连接状态时出现，并明确区分“浏览器已连接”、启用平台登录/本轮采集和 dy 暂停状态。
- 两张 Windows Chromium 电脑端视觉基线：workbench 与 Brief。

0.10.0 合并态的本地静态、单元、构建与 macOS 浏览器门已经实际执行；部署源提交 `91534b0` 的 GitHub Actions 运行 `33521833733` 已再次完成 Windows 浏览器与跨平台 Python 复验：

- `pnpm --dir web test`：5/5。
- `pnpm --dir web typecheck`：通过。
- `pnpm --dir web lint`：通过。
- `pnpm --dir web build`：Vinext 五阶段 production build 通过。
- `pnpm --dir web audit --audit-level=high`：完整依赖（含开发工具）0 个已知漏洞。
- macOS `pnpm --dir web exec playwright test --project=desktop-chromium`：31 passed / 1 个 Windows 权威像素门按设计 skipped。
- Windows CI `pnpm --dir web exec playwright test --project=desktop-chromium`：32/32 通过（其中 1 项权威像素门）。

合并后的 0.10.0 Python 本地与 Ubuntu/macOS/Windows CI 均为 98/98，Web 单测为 5/5，macOS desktop-chromium 为 31 passed / 1 skipped，Windows desktop-chromium 为 32/32。合并前本地实时链路 91/91、团队 Studio 分支 83/83，以及 0.9.2 的 77/77、Windows 31/31 都只代表各自分支或旧版本，不能冒充本次结果。

失败时报告写入 `web/.playwright-report/`，截图、axe 上下文和 trace 写入 `web/.playwright-results/`；两者不进 Git。

## 5. 视觉基线更新纪律

只有确认变化有意且已经人工看过目标视口时，才更新对应项目：

```powershell
# 当前 desktop-only C2 只允许更新 desktop project
pnpm exec playwright test -g "核心工作台与任务书视觉基线" --project=desktop-chromium --update-snapshots
```

不要为 desktop-only 任务运行会同时覆盖 mobile 的 `pnpm test:ui:update`。更新后必须逐张查看目标 PNG，并确认：

- 五区色块和 60/72/210/330 几何正确，画布保持最大工作面。
- 没有大面积纯白、渐变、玻璃、光晕、旧主题色或内容裁切。
- 选中态、焦点和唯一主动作使用 selected/primary，节点几何不变。
- 文化星图深色只限内部关系舞台，外围回到 C2。
- 市场页先出现 378 条历史样本、时间窗和平台分布，实时控制没有压住证据口径。
- 来源图像只在内容内部保留自身颜色，容器和控制仍属于 C2。

Task 5 只更新并目视复核两张 desktop 快照。两张 mobile snapshot 从 Task 5 起点到终点 SHA-256 字节不变，但 workbench mobile 在 Task 5 开始前已相对 Git modified；字节不变只证明本次未触碰，不能证明 C2 mobile 通过。

像素基线与操作系统、浏览器版本和字体栅格有关；不能用另一平台的差异直接覆盖 Windows 基线。

## 6. 人工确认清单

当前 desktop-only C2 人工门以 1440×960 为准：

- Workbench：command/rail/canvas/Dock/Inspector 分区清楚；真实 9 nodes / 10 edges；当前焦点链可读且不被 Inspector 遮挡。
- Decision Studio：七阶段、长中文字段、唯一主动作和底部操作区无裁切/重叠。
- Culture：外围 C2 与内部深色星图边界清楚；搜索、分类、缩放、选点和证据 Inspector 可读。
- Market：378 条历史证据、115/14/101/148 分布、时间边界先于实时控制；不写成实时趋势。
- Brief：标题、7 条引用、输入/下游、审核门和长中文字段可读。
- 全局：0 gradient、0 backdrop-filter、0 document overflow；状态语义、引用、权利与生产前边界可见。

未来如重新开展 mobile/tablet C2，需另行设计并实际检查目标视口、44px 目标、页面滚动/星图手势、抽屉、safe area、焦点归还、真实触屏与 mobile snapshots；旧基线不能替代该工作。

## 7. 当前边界

- axe 只能发现一部分无障碍问题；自动门通过不等于 WCAG 认证，仍需真实屏幕阅读器与残障用户测试。
- 当前没有把 Lighthouse、真实用户 INP 或超大图谱压力测试设为阻断门；节点数量和数据规模显著增长时需要单独基线。
- 视觉快照使用 `guizhou-miao-demo` 的本地真实 HTTP 数据，不能替代认证后线上复验。
- 受保护线上 0.10.0 当前部署 `6a96ec9f40c09e36c3ebb590` 已切换默认 Studio 入口，并保留 `/workflow` 高级工作台与同源授权浏览器。认证后主页、一级页、动态设计页、9 个旧节点页及相应 API/PNG 已远端验收为 200；这不扩大本文档的 desktop-only 视觉承诺。
- 本流程止于本地产品前端质量，不授权部署、商业图稿批准、工厂下单或制造/合规就绪声明。
