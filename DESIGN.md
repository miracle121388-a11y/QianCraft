---
name: QianCraft
description: Evidence-led creative intelligence workbench using the Tonal Focus Review system
direction:
  name: "Tonal Focus Review"
  mode: "Operate"
  approvedMock: ".impeccable/mocks/tonal-focus-review.png"
  approvedMockSha256: "131cd5bedadd5be42888ace5d946ebaa2d4c3f3dc935e29393fd1127ebf7ffeb"
  implementationScope: "desktop 1440x960"
colors:
  shell: "#E6E2DA"
  command: "#D9E1E8"
  rail: "#D7E1DC"
  canvas: "#E3E8EB"
  inspector: "#E7DDD4"
  node: "#F0EEE9"
  selected: "#CBD9E6"
  primary: "#345C7D"
  text: "#20262C"
  textSecondary: "#626970"
  rule: "#C4C8C7"
  success: "#637E6A"
  warning: "#B1844C"
  danger: "#9A6757"
  neutral: "#7B8086"
  starCanvasException: "#070708"
typography:
  uiFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Noto Sans SC Variable", "Noto Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif'
  technicalFamily: 'SFMono-Regular, Cascadia Code, Consolas, monospace'
  detailTitle: "clamp(32px, 3.5vw, 46px) / 1.15 / 520"
  decisionTitle: "clamp(28px, 2.4vw, 34px) / 1.18 / 520"
  sectionTitle: "22px / 1.25 / 520"
  panelTitle: "19px / 1.3 / 620"
  body: "14-16px / 1.6-1.7 / 400"
  command: "13px / 1.45 / 560"
  label: "12px / 1.45 / 560"
  micro: "11px / 1.45 / 400"
spacing:
  base: "4px"
  scale: ["4px", "8px", "10px", "12px", "16px", "20px", "24px", "32px", "40px", "48px", "56px"]
radii:
  input: "10px"
  control: "11px"
  image: "12px"
  node: "14px"
  container: "14px"
  card: "14px"
  pill: "9999px"
desktopGeometry:
  commandBar: "60px"
  toolRail: "72px"
  evidenceDock: "210px"
  inspector: "330px"
---

# Design System: QianCraft

## 1. Current direction

**Creative North Star: “Tonal Focus Review / 低饱和聚焦评审”**

QianCraft 0.9.2 的电脑端延续 C2 Tonal Focus Review。它仍是高密度证据工具，不是营销官网：暖矿物外壳承接整体环境，雾蓝命令栏与画布、灰绿工具/证据区、暖陶 Inspector 通过固定色块定位任务；低饱和深灰蓝只承担选中、焦点和主动作。简约来自减少无意义修饰，而不是把工作区清空成大面积纯白。

本轮只承诺 **1440×960 电脑端**。30 项功能门在 macOS Chromium 已通过，Windows CI 承担同一功能集与两张权威像素基线；既有 mobile/tablet 行为仍留在原组件和样式中，但没有把手机/平板写成当前 C2 已适配或已验证。

批准构图为 `.impeccable/mocks/tonal-focus-review.png`，SHA-256 为 `131cd5bedadd5be42888ace5d946ebaa2d4c3f3dc935e29393fd1127ebf7ffeb`。它只冻结区域比例、色块关系、聚焦节奏和工作台构图，不是产品数据资产，也不是逐像素实现稿。

### Product facts that visual work must preserve

- 工作台继续读取真实 HTTP API、Workspace Schema 1.1、9 个默认节点实例和 10 条真实连线。
- 文化层继续展示 22 条正式记录、32 个登记来源与独立人工候选门；市场层继续展示 378 条带时间边界的历史真实快照。
- 策略层继续展示 8 条机会、Top 3、六维量分、引用与机器/人工并列决策；不得用视觉层改写事实或评分。
- `live / cache / stale / warning / error / blocked / degraded` 必须保持诚实语义。排程存在、曾经成功或历史快照都不能冒充当前在线。
- 产品阶段止于 `DesignPackage`、工厂询价/首样简报与概念海报；不代表生产发布、工厂下单、商业图稿批准、DFM、制造或合规就绪。

## 2. Color system

### Fixed C2 surfaces

| Role | Token | Value | Use |
|---|---|---:|---|
| Warm mineral shell | `--qc-shell` | `#E6E2DA` | 应用外壳与五区之间的环境底色 |
| Mist-blue command | `--qc-command` | `#D9E1E8` | 60px 命令栏、Decision Studio 顶/底区 |
| Gray-green rail | `--qc-rail` | `#D7E1DC` | 72px 工具轨、210px 证据 Dock、阶段轨 |
| Mist-blue canvas | `--qc-canvas-tonal` | `#E3E8EB` | React Flow 主画布、详情主工作区 |
| Warm-clay Inspector | `--qc-inspector` | `#E7DDD4` | 330px Inspector 与审核语境 |
| Light-stone node | `--qc-node` | `#F0EEE9` | 节点、字段、次按钮、紧凑工作面 |
| Selected surface | `--qc-selected` | `#CBD9E6` | 当前节点、当前资产、活动页签与 hover |
| Primary / focus | `--qc-primary` | `#345C7D` | 唯一主动作、选中边线、当前路径与焦点 |
| Primary text | `--qc-text` | `#20262C` | 标题、正文、关键字段 |
| Secondary text | `--qc-text-secondary` | `#626970` | 元数据、辅助说明，不承载关键风险边界 |
| Rule | `--qc-rule` | `#C4C8C7` | 1px 分隔与输入/卡片边界 |
| Success | `--qc-success` | `#637E6A` | 已成功且仍有效的状态标记 |
| Warning | `--qc-warning` | `#B1844C` | stale、warning、degraded、paused |
| Danger | `--qc-danger` | `#9A6757` | error、failed、blocked |
| Neutral | `--qc-neutral` | `#7B8086` | cache、idle 与中性状态 |

### Selection and action rules

- 节点或资产被选中时使用 `#CBD9E6` 面、`#345C7D` 边线/handle，并保持原尺寸、坐标和连线布局。
- 每个任务区只保留一个 `#345C7D` 主动作；前景使用当前实现的近白 `#F7F8F8`，但不得把近白扩展为大面积页面或面板。
- 次操作使用浅石面、规则线和主文字；hover 可以进入 selected 面，但不能增加光晕、渐变或装饰色。
- 可见键盘焦点使用清晰的 primary outline。颜色不是唯一语义，控件名称、状态文字、边线和形状必须同时存在。

### Status grammar

- `live / success / healthy / completed`：success 实心标记 + 明确中文状态。
- `cache / cached / idle`：neutral 实心或中性标记 + 缓存时间/来源说明。
- `stale / warning / degraded / paused`：warning 空心标记 + 原因和下一步。
- `error / failed`：danger 实心或方形标记 + 错误说明和可恢复路径。
- `blocked`：danger 空心标记 + 实时开关、运行时或授权缺项；不得被历史证据或正常排程覆盖。
- `running`：保留动画时也必须有静态文字；reduced motion 下停止连续动画而不移除状态结果。

### Dark culture-constellation exception

文化关系星图内部继续使用既有 `#070708` 深色功能画布和白色关系点/线。这是为了在空间关系中检索、选点、缩放和平移的任务性例外：

- 只允许 `.constellation-stage`、其 SVG、节点与 hit area 保持深色。
- 搜索、筛选、工具栏、说明、图例、控制和证据 Inspector 使用 C2 node/canvas/rule/text 语法。
- 深色不得扩散到普通详情页、导航、卡片、营销背景、装饰星空或无意义网格。

### Forbidden treatments

- 大面积纯白或近白工作面。
- 渐变、mesh gradient、玻璃、`backdrop-filter`、霓虹、光晕和装饰性环境光。
- 高饱和彩色 chrome、无业务含义的彩色分区、彩虹状态或旧亮蓝主题。
- 以投影堆叠普通卡片；电脑端只有真实覆盖画布的 Inspector 可使用克制阴影，Decision Studio 与普通卡片均无阴影，关闭覆盖关系后阴影必须消失。
- 把来源图像的内容色扩散到按钮、边线、导航或状态系统。

## 3. Typography, spacing and shape

产品 UI 继续使用 system/SF-like/Noto Sans SC 无衬线链。节点 ID、运行 ID、字段名和 JSON 才使用 SFMono/Cascadia/Consolas 等宽链。C2 不改变既有字体资源和中文回退契约。

- Detail title：520，`clamp(32px, 3.5vw, 46px)`，行高 1.15。
- Decision title：520，`clamp(28px, 2.4vw, 34px)`，行高 1.18。
- Section / panel title：22px/19px，520/620。
- 正文：14–16px，400，行高 1.6–1.7；连续阅读控制在约 72–76ch。
- 命令/标签/元数据：13/12/11px；11px 只用于短 ID 或次级元数据，不承载操作和风险说明。
- 间距以 4px 为基准，常用 8/12/16/20/24/32px；C2 通过色块和留白建立层级，不增加装饰分隔。
- 字段/控件/图像/节点/容器使用 10/11/12/14px 紧凑圆角，普通表面不得超过 14px；pill 只作为短按钮和状态徽章的语义例外。

## 4. Desktop layout

1440×960 工作台采用五区：

1. 顶部 `60px` command bar，横向承载品牌、Workspace、阶段和唯一主动作。
2. command 下方左侧 `72px` tool rail，承载证据、资产、历史和 Inspector 触发器。
3. rail 右侧为弹性 React Flow 主画布，使用雾蓝 canvas；真实节点/连线和当前焦点链优先。
4. Dock 打开时在画布底部占 `210px`，从 rail 右缘铺到 viewport 右缘；证据、资产和历史复用同一插槽并独立滚动。
5. Inspector 打开时以 `330px` 固定宽度贴右覆盖画布/Dock，使用暖陶面；关闭后不继续占据或拦截工作区。

空白画布继续支持主键拖动平移、`Shift + 拖动` 框选、滚轮缩放；节点拖动只移动节点。证据拖拽继续提供可见“添加到画布”点击/键盘路径。Dock、Inspector、Workspace 和 Decision Studio 都是可逆上下文，关闭后应回到原任务和触发点。

Task 4 曾实现的 tablet/mobile C2 覆盖层已完整撤销。本文件不为 760px 以下新增 C2 几何承诺；现有移动组件行为可以继续存在，但必须等后续获得授权、实现并运行 mobile/real-device 验收后才能写成当前 C2 能力。

## 5. Components

### Command bar and tool rail

- 命令栏使用 command 面；活动阶段以 primary 文字/底线定位，不改变几何。
- 工具轨使用 rail 面；默认图标为 secondary text，hover 使用 node 面，active 使用 primary 面 + node 前景。
- Workspace/phase popover 使用 canvas/node/rule，不恢复旧白/黑主题或玻璃模糊。

### Flow nodes and edges

- 普通节点使用 node 面、rule 边线与 text；选择只切换 selected/primary。
- 关系线默认 rule，选中路径为 primary；MiniMap、controls、context、legend 和 monitor 使用 node/rule，并清除渐变和光晕。
- 摘要、字段和操作进入 Inspector 或独立详情页，不因选中而展开节点。

### Dock and Inspector

- Evidence/Asset/History Dock 根面与 sticky heading 使用 rail；列表项使用 node 或透明面，活动项使用 selected/primary。
- 证据正式库、候选、历史市场快照、实时控制和运行事件保持分层；市场证据在运维控制之前出现。
- Inspector 使用暖陶根面；字段与只读卡使用 node，primary action 使用 primary；七个页签和标题不改变 API 或工作区数据。

### Decision Studio and node details

- Decision Studio 使用 shell 环境、command header/footer、rail stage nav、canvas panel 与 node fields；保存人工决策是唯一主动作。
- 九个详情页共享 shell/canvas/node/inspector/rule/text 语法，真实 `.detail-editor`、引用台账、排名、机会、概念、海报、BOM 和 collection console 均纳入 C2。
- 详情 topbar 和旧概念资产提示不得使用 `backdrop-filter` 或玻璃效果。
- 文化星图内部深色画布保持例外，外围控件和右侧证据区遵守 C2。

### Product imagery and citations

- 只允许项目自有、来源可追溯的产品 hero、Concept A/B/C 与 1800×2400 概念海报进入产品图像位；保留 alt、用途、生成状态和权利边界。
- `reference_only` 馆藏像素、无来源缩略图、模型构图中的示意人物/时间/文件名/缩略图都不得冒充产品内容。
- 每个事实、机会、视觉参考和设计结果继续通过引用台账/原始链接可追溯；缺失 provider 或本轮失败时显示诚实 warning，并区分“保留上次成功资产”与“本轮未生成”。

## 6. Accessibility and interaction

- 桌面质量门继续覆盖 axe A/AA/2.2 AA 规则、唯一 `h1`、图片完整性/alt、横向溢出、拖拽等价路径、中文画布语义、弹层焦点、forced-colors、键盘和视觉快照。
- Culture Graph、Workspace 与 Decision Studio 保持可访问名称/描述、初始焦点、Tab 焦点圈、Escape 关闭和触发器焦点归还。
- 知识星图桌面路径继续覆盖搜索聚焦、选点、按钮/滚轮缩放、拖动画布和键盘平移；forced-colors 下中心、普通与选中节点不能合并成同一视觉角色。
- 自动 axe、forced-colors 和像素回归只能证明已覆盖的自动门，不等于完整 WCAG 认证；真实屏幕阅读器、残障用户、真实触屏设备和跨平台字体仍需专项验证。
- 本轮 C2 最终验证仅为 desktop-chromium 1440×960；旧 mobile 自动门和快照不能冒充 C2 移动验收。

## 7. Validation and change discipline

- 当前 C2 电脑端门：前端单测 5/5，macOS desktop-chromium 30 passed / 1 Windows 像素门 skipped，typecheck、零 warning lint 与 Vinext production build 通过；两张电脑端像素基线只由 Windows CI 执行。
- 两张 mobile snapshot 从 Task 5 起点到终点字节不变，但本轮没有运行 mobile project，因此它们不是当前 C2 通过证据。
- 像素基线只可在目标 Windows Chromium、相同字体环境中，由人工确认变化有意后更新。不得用另一平台的抗锯齿差异覆盖现有基线。
- 0.9.1 C2 已发布到受 Basic Auth 保护的 Zeabur 实例；0.9.2 在远端发布验收完成前只算本地候选。当前 C2 仍只承诺 desktop-chromium，不能把发布成功扩写为 mobile/tablet 设计验收。

## 8. Do / Don’t

### Do

- 使用固定 C2 色块表达区域职责，让主画布和当前焦点链保持最高任务优先级。
- 保持 60/72/210/330 电脑端几何、真实九节点/十连线、共享 Decision/详情语法和深色文化星图例外。
- 让状态同时具有文字、颜色、轮廓或形状，并区分实时、缓存、过期、警告、失败和阻断。
- 保持引用、历史时间窗、权利状态、人工改写和生产前边界可见。
- 把批准构图作为非字面比例/色块参考，只消费真实 API、中文内容和现有工作流。

### Don’t

- 不恢复 Monochrome 的大面积白/冷灰/纯黑产品级语法，也不恢复暖纸旧主题或亮蓝系统色。
- 不添加渐变、玻璃、backdrop blur、光晕、装饰网格、高饱和环境色或无意义缩略图。
- 不让选中节点扩张、位移、抬升或展开详情；不让拖拽成为唯一输入路径。
- 不把黑色星图例外扩散成全站深色主题。
- 不把 378 条历史快照、排程或曾经授权写成当前四平台实时产出。
- 不把 desktop-only C2 写成 mobile/tablet 已适配、已通过或已在真实设备验证。
- 不从当前概念包声称生产发布、工厂下单、商业图稿批准、社区授权完成或制造/合规就绪。
