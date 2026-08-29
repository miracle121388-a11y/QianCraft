---
name: QianCraft
description: Evidence-led creative intelligence workbench in a monochrome precision-instrument system
colors:
  white: "#ffffff"
  canvas-gray: "#f5f5f7"
  panel-gray: "#fbfbfd"
  raised-gray: "#f0f0f2"
  rule: "#dedee3"
  rule-strong: "#b8b8be"
  secondary-text: "#515154"
  tertiary-text: "#6e6e73"
  graphite: "#1d1d1f"
  black: "#000000"
  near-black: "#111113"
  star-canvas: "#070708"
  star-control: "#171719"
  selection-soft: "#ededf0"
  cached-gray: "#707076"
  warning-gray: "#4a4a4f"
typography:
  detail-title:
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Noto Sans SC Variable", "Noto Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "clamp(32px, 3.5vw, 46px)"
    fontWeight: 520
    lineHeight: 1.15
    letterSpacing: "-0.035em"
    fontFeature: "liga 0"
  decision-title:
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Noto Sans SC Variable", "Noto Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "clamp(28px, 2.4vw, 34px)"
    fontWeight: 520
    lineHeight: 1.18
    letterSpacing: "-0.03em"
    fontFeature: "liga 0"
  section-title:
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Noto Sans SC Variable", "Noto Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "22px"
    fontWeight: 520
    lineHeight: 1.25
    letterSpacing: "-0.025em"
    fontFeature: "liga 0"
  panel-title:
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Noto Sans SC Variable", "Noto Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "19px"
    fontWeight: 620
    lineHeight: 1.3
    letterSpacing: "-0.025em"
    fontFeature: "liga 0"
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Noto Sans SC Variable", "Noto Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.65
    letterSpacing: "normal"
    fontFeature: "liga 0"
  command:
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Noto Sans SC Variable", "Noto Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "13px"
    fontWeight: 560
    lineHeight: 1.45
    letterSpacing: "normal"
    fontFeature: "liga 0"
  label:
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Noto Sans SC Variable", "Noto Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "12px"
    fontWeight: 560
    lineHeight: 1.45
    letterSpacing: "normal"
    fontFeature: "liga 0"
  micro:
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Noto Sans SC Variable", "Noto Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: "normal"
    fontFeature: "liga 0"
rounded:
  brand: "9px"
  input: "10px"
  control: "11px"
  image: "12px"
  container: "14px"
  dialog: "16px"
  card: "18px"
  pill: "9999px"
spacing:
  space-4: "4px"
  space-8: "8px"
  space-10: "10px"
  space-12: "12px"
  space-16: "16px"
  space-20: "20px"
  space-24: "24px"
  space-32: "32px"
  space-40: "40px"
  space-48: "48px"
  space-56: "56px"
components:
  button-primary:
    backgroundColor: "{colors.black}"
    textColor: "{colors.white}"
    typography: "{typography.command}"
    rounded: "{rounded.pill}"
    padding: "0 15px"
    height: "36px"
  button-secondary:
    backgroundColor: "{colors.white}"
    textColor: "{colors.graphite}"
    typography: "{typography.command}"
    rounded: "{rounded.pill}"
    padding: "0 15px"
    height: "36px"
  mobile-run:
    backgroundColor: "{colors.black}"
    textColor: "{colors.white}"
    rounded: "{rounded.image}"
    size: "44px"
  tool-rail-button:
    backgroundColor: "transparent"
    textColor: "{colors.tertiary-text}"
    rounded: "{rounded.control}"
    size: "38px"
  tool-rail-button-active:
    backgroundColor: "{colors.white}"
    textColor: "{colors.black}"
    rounded: "{rounded.control}"
    size: "38px"
  input-field:
    backgroundColor: "{colors.canvas-gray}"
    textColor: "{colors.graphite}"
    typography: "{typography.body}"
    rounded: "{rounded.input}"
    padding: "10px 12px"
    height: "40px"
  flow-node:
    backgroundColor: "{colors.white}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.container}"
    width: "300px"
    height: "68px"
  flow-node-wide:
    backgroundColor: "{colors.white}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.container}"
    width: "320px"
    height: "68px"
  inspector:
    backgroundColor: "{colors.white}"
    textColor: "{colors.graphite}"
    width: "336px"
  constellation-canvas:
    backgroundColor: "{colors.star-canvas}"
    textColor: "{colors.white}"
    rounded: "{rounded.dialog}"
  collection-console:
    backgroundColor: "{colors.white}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.dialog}"
---

# Design System: QianCraft

## Overview

**Creative North Star: "Monochrome Precision Instrument / 黑白精密工具"**

QianCraft 0.9.0 是一台已完成本地质量门验收的证据型创作工作仪器，模式为 **Operate**，方向种子为 `a403e052`。白色工作面、浅冷灰层级、石墨文字、细中性分隔线与纯黑关键状态构成系统 chrome；界面通过对比、结构和可逆上下文表达层级，不借助暖纸材质、蓝色强调或营销式视觉姿态。本地 0.9.0 尚未部署，受保护线上实例仍为 0.8.0。

核心体验仍是稳定的节点画布，但文化与市场两条素材入口已升级为持续维护工作面。文化页用黑色关系画布呈现可搜索、可选点的知识星图，右侧白色 Inspector 保留地域、工艺、边界和来源；桌面直接拖动、滚轮缩放并支持键盘，手机默认让页面滚动，显式进入“操作星图”后才接管单指平移与双指缩放。黑色只属于这块真实关系画布，不扩散为页面主题或营销背景。

持续采集控制面把正式知识、待核验候选、历史市场快照和当次运行状态分开呈现；断线或心跳过期会使旧在线状态失效，部分来源失败显示 `degraded`，授权缺失显示 `blocked`。市场页先展示 378 条历史快照、时间窗与平台分布，再按需展开运行控制。文化事实、市场时间边界、权利状态、机器建议与人工决策的差异始终可见，现阶段只到 `DesignPackage`、工厂询价/首样简报与概念海报。

**Key Characteristics:**

- 纯白工作面、冷灰深度、石墨文字与纯黑动作形成无色差干扰的专业工具环境。
- 桌面由 60px 命令栏、56px 工具轨、情境 Dock、主节点画布与 336px Inspector 构成。
- 黑色知识星图是由关系、记录、分类和来源驱动的唯一深色画布；工具栏、选择与证据 Inspector 仍遵守黑白精密工具语法。
- 持续采集控制面同时表达排程、心跳、最近尝试/成功、候选审核、部分失败、授权阻断与事件历史，不用旧成功掩盖断线。
- 节点是稳定的 68px 索引，不因选择而展开；细节进入绑定 Inspector 或独立详情页。
- 系统/SF-like 无衬线与 Noto Sans SC 中文 fallback 承担全部产品 UI；技术 ID 使用等宽 fallback。
- 10–16px 的克制圆角、1px 细线与只用于真实浮层的低强度阴影维持精密感。
- 760px 及以下保留 56px 顶栏与工具轨、72×56 阶段入口、44×44 Run 和可逆覆盖面板。
- 拖拽证据同时提供点击/键盘“添加到画布”路径；画布语义为中文，图谱、Workspace 与 Decision Studio 都有完整焦点闭环。
- 文化正式库维持 22 条记录/32 个来源并使用候选人工门；市场 378 条历史快照先于实时控制出现，当前实时采集因开关和四平台授权缺失保持 `blocked`。

**0.8.1 migration.** 0.7.x 的“暖纸仪器台账”、暖色表面和蓝/靛蓝交互色仅是历史迁移来源，不再是现行规范。代码中的 `--lovable-*` 名称只作为兼容别名指向 `--qc-*` 黑白冷灰令牌，不能按旧名字恢复暖色含义。

**0.9.0 continuous-evidence hardening.** 视觉判断已固化为 Playwright 桌面/手机路由门、axe、星图手势与搜索、控制面断线/阻断、forced-colors、44px 目标和视觉快照；最终为 Python 53 passed、前端单测 5 passed、Playwright 35 passed / 1 intentionally skipped，并通过 typecheck、lint、production build、Ruff、shell syntax、lockfile 与 diff 检查。自动门是回归证据，不是完整 WCAG 认证。详细流程见 `docs/frontend_quality_workflow.md`。

## Colors

系统色板严格无彩：黑色负责确定性，灰阶负责深度与阅读层级，白色负责工作空间。色彩不承担系统状态；状态由文字、明度、轮廓和形状共同表达。

### Primary

- **Precision Black** (`black`): 唯一高强度主动作、选中边线、键盘焦点、活动阶段和需要锁定的关键上下文。
- **Instrument Graphite** (`graphite`): 主文本、深色信息面和绝大多数高对比内容；不得与纯黑主动作争夺层级。

### Neutral

- **Working White** (`white`): 页面、命令栏、节点、Dock、Inspector、Decision Studio 与详情页的主要工作面。
- **Canvas Gray** (`canvas-gray`): 主画布、输入、列表 hover 和次级内容区的第一层冷灰深度。
- **Panel Gray** (`panel-gray`) 与 **Raised Gray** (`raised-gray`): 更细的面板/只读区层级、禁用状态和风险边界；不产生暖色偏移。
- **Hairline Rule** (`rule`) 与 **Strong Rule** (`rule-strong`): 普通 1px 分隔、hover/选中前的较强边界和结构缝线。
- **Secondary Text** (`secondary-text`) 与 **Tertiary Text** (`tertiary-text`): 说明、元数据、标签和非关键状态文案；关键操作与风险说明不得降到 tertiary。
- **Near Black** (`near-black`) 与 **Selection Soft** (`selection-soft`): 兼容性近黑和极浅选中底；当前节点与主要选中态仍以纯黑 keyline 为准。
- **Star Canvas** (`star-canvas`) 与 **Star Control** (`star-control`): 只服务文化关系星图的深色底面与控件面；仍是无彩系统，不允许扩散到普通详情、导航、卡片或营销区。
- **Cached Gray** (`cached-gray`) 与 **Warning Gray** (`warning-gray`): 缓存和警告的无彩状态材料，必须与文字或轮廓形状一起出现。

**The No Chromatic Chrome Rule.** 米色、暖纸色、蓝色、靛蓝和任何文化色都不能进入系统 chrome、焦点、选择、按钮或状态结构。

**The One Black Action Rule.** 每个任务区域只有一个纯黑主动作；其他动作保持白底、中性线和石墨文字。

**The State Has Shape Rule.** success 用实心圆，cached 用中灰圆，warning/stale 用空心圆，error 用黑色方点，running 用黑色旋转扇形；旁边始终保留可读状态文字。

**The Source Color Exception Rule.** 产品、证据和概念图像可保留来源色；容器、标题、标签、边线和操作控件必须回到黑白灰系统。

**The Black Relation Canvas Exception Rule.** 黑色底面只用于需要空间关系阅读和直接操控的文化星图；它不能成为全站深色主题、装饰背景或营销姿态。

## Typography

**UI Family:** system/SF-like sans stack，中文由 Noto Sans SC Variable / Noto Sans SC 承接。

**Technical Family:** SFMono-Regular、Cascadia Code、Consolas、monospace，仅用于节点 ID、运行 ID、字段名和 JSON。

**Character:** 字体像系统级专业工具而不是品牌海报。层级依赖字号、留白和 400–620 的有限字重，标题保持紧凑字距，正文保持长时间操作所需的清晰行高。

### Hierarchy

- **Detail Title**（520，`clamp(32px, 3.5vw, 46px)`，1.15）: 节点详情页主标题；手机端收至 28px。
- **Decision Title**（520，`clamp(28px, 2.4vw, 34px)`，1.18）: Human Decision Studio 当前任务句；手机端为 24px。
- **Section Title**（520，22px）: 详情区、编辑器、Brief 上下文与主要内容分段。
- **Panel Title**（620，19px）: Dock、Inspector 和紧凑面板标题。
- **Body**（400，14–16px，1.6–1.7）: 证据摘要、说明和可编辑内容；连续阅读控制在约 72–76ch。
- **Command**（480–620，13px）: 顶栏阶段、按钮和短命令。
- **Label / Micro**（400–560，11–12px）: 状态、元数据、字段标签和审计信息；不可替代的技术短码可使用 11px，操作文案不小于 12px。

**The Sans Instrument Rule.** 产品 UI 只使用系统/SF-like/Noto Sans SC 无衬线链；不得重新引入展示衬线或营销式字体对。

**The Controlled Weight Rule.** 正文以 400 为基线，结构标题以 520 为基线，短关键标签和品牌锁定最多使用 620–650；不以 700–900 黑重代替层级。

**The Legible Metadata Rule.** 11px 只承载短状态、ID 或次级元数据；长说明、操作和风险边界必须使用至少 12–14px 并保持足够行高。

## Layout

桌面工作台以 60px 白色命令栏覆盖顶部；其下四列依次为 56px 浅灰工具轨、可选 260px 情境 Dock、弹性主画布和可选 336px Inspector。Dock 与 Inspector 关闭时列宽归零，主画布立即回收空间；两侧同时开启且视口不超过 1280px 时压缩为 232px 与 310px，画布仍保持弹性。桌面工作台最低结构宽度为 1080px。

主工作台画布是最大区域。标准节点宽 300px，Visual、Concept 与 Poster 等宽节点为 320px；节点头最小高 68px，选择前后宽高与坐标完全相同。空白画布用主键或单指直接拖动平移，`Shift + 拖动` 执行框选，滚轮/捏合缩放；拖动节点只改变节点坐标，不带动画布。画布控制、图例、运行监视器和上下文提示贴边悬浮，不遮挡当前路径。

文化星图在桌面以 `minmax(0, 1fr) + 350px` 组织黑色关系画布与白色证据 Inspector，最小高 700px；1120px 以下 Inspector 收至 310px，900px 以下转为上下单列，760px 以下关系画布最小高 570px并贴合页面边缘。桌面可拖动、滚轮/按钮缩放和键盘平移；移动默认 `touch-action: pan-y pinch-zoom` 以保护页面滚动，只有显式“操作星图”模式改为 `touch-action: none` 并接管单指平移、双指缩放。退出模式后立即归还页面手势。

Human Decision Studio 桌面最大约 1408 × 876px；阶段导航在左、内容在右、操作栏持续可达。980px 以下占满视口，680px 以下阶段导航改为 54px 横向条、内容单列。保存是唯一主动作；桌面次动作在同一组内并排，移动端保存占第一行，两项次动作在第二行等分。

760px 及以下，顶栏固定为 56px，并按 48px 品牌入口、弹性 Workspace、72px 阶段入口和 52px 动作槽组织；Run 本体为 44×44px。工作区只保留 56px 工具轨与画布，工具按钮为 44×44px。Dock 从左侧覆盖，宽度不超过 `min(304px, viewport − 56px)`；Inspector 从右侧覆盖，宽度不超过 `min(342px, viewport − 56px)`。二者都必须可关闭、恢复焦点且不把画布永久挤出视口。

**The Canvas First Rule.** 先保护当前节点、关系线和运行上下文，再决定 Dock 或 Inspector 是否常驻。

**The Direct Manipulation Rule.** Workbench 主画布的主键或单指拖动空白区域必须直接平移；框选显式使用 Shift，滚轮/捏合负责缩放，节点拖动只移动节点。

**The Scroll-before-Gesture Rule.** 文化星图在紧凑触屏上先保护页面纵向滚动；只有用户明确进入“操作星图”后才接管单指平移和双指缩放，完成后必须可逆退出。

**The Equivalent Input Rule.** 任何拖拽触发的创建动作都必须同时提供点击与键盘路径；拖拽是效率增强，不是进入工作流的唯一门。

**The Stable Geometry Rule.** 选择只能改变黑色对比、keyline 与 Inspector 绑定，不得改变节点尺寸、坐标或关系线布局。

**The Reversible Edge Rule.** Dock、Inspector、Decision Studio 和详情关联条都是可逆上下文；关闭后回到原任务与原触发点。

**The 44px Compact Rule.** 760px 及以下的 Run、工具轨按钮、画布控制、下拉/summary、面板关闭、保存、下载、筛选与次动作命中区不得小于 44×44px；正文内联引用可按内联目标例外保持紧凑。

## Elevation & Depth

系统平面默认无投影。节点、Dock 列表、Inspector 内容、详情容器、采集控制面和表单通过白/冷灰色差、1px 细线和少量 inset keyline 建立深度。drop shadow 只在真正脱离文档流的浮层中出现：主画布控制和上下文卡使用约 8% 黑影，知识星图内的浮动工具条使用 24–28% 黑影以从黑底分离，popover 使用约 14% 黑影，桌面 Decision Studio 使用 24% 黑影；移动端 Dock/Inspector 使用方向性 14% 黑影。移动端全屏 Decision Studio 清除圆角和阴影。

### Shadow Vocabulary

- **Inset Edge Soft** (`rgb(0 0 0 / 12%) 0 0 0 0.5px inset`): 兼容性细边与轻量结构，不作为抬升效果。
- **Inset Edge Strong** (`rgb(0 0 0 / 18%) 0 0 0 0.5px inset`): 选中或锁定边缘；节点当前实现另加纯黑 0.5px inset keyline。
- **Floating Instrument** (`0 10px 30px rgb(0 0 0 / 8%)`): React Flow 控制、minimap、画布上下文、图例和监视器。
- **Star Toolbar** (`0 10px 30px rgb(0 0 0 / 28%)`): 仅知识星图内部的搜索、筛选、视图控制与操作说明，证明这些控件浮于关系画布之上。
- **Popover** (`0 20px 60px rgb(0 0 0 / 14%)`): Workspace 与移动阶段菜单等临时选择面板。
- **Decision Modal** (`0 34px 100px rgb(0 0 0 / 24%)`): 仅桌面 Decision Studio；移动全屏时为 none。
- **Dock Overlay** (`14px 0 36px rgb(0 0 0 / 14%)`) 与 **Inspector Overlay** (`-14px 0 36px rgb(0 0 0 / 14%)`): 仅 760px 以下可逆边缘覆盖层。

节点选择以 160ms `ease` 更新边线、背景和 inset keyline，工作台列宽以 180ms `ease` 调整。`prefers-reduced-motion: reduce` 将 JS 画布定位时长归零，停止 running/loading 动画并关闭工作台、节点、Dock 与 Inspector 的过渡，同时保留静态状态形状和进度结果；不得用全局 `0.01ms` 规则破坏必要反馈。

**The Flat Working Plane Rule.** 普通工作表面不得使用 drop shadow；层级优先由灰阶、细线和留白承担。

**The Overlay Proof Rule.** 阴影必须证明对象真的覆盖了下层任务；覆盖关系结束，阴影也必须消失。

## Shapes

形状语言紧凑、近似系统控件：品牌记号为 9px，输入为 10px，工具控件为 11px，图片与移动 Run 为 12px，节点和常规容器为 14px，主要详情容器与 Decision Studio 为 16px，独立大卡最多 18px。按钮和短徽章可以使用完全胶囊；证据行、节点、面板和长文本容器不能胶囊化。

边界通常为 1px 中性线，选中节点增加纯黑边与 0.5px inset keyline，活动阶段使用 2px 黑色底线。图标采用 Lucide 风格的单色线性 SVG，常规 16–21px，并必须配合可读标签或 `aria-label`。

**The Compact Radius Rule.** 10/11/12/14/16/18px 分别服务于字段、工具控件、图片/移动动作、节点、主要容器和少量独立卡；不得回到 24px 暖卡或大面积软胶囊。

**The Purposeful Pill Rule.** Pill 只属于按钮、模式切换、短状态和数量徽章；工作内容本身保持清晰的矩形工具几何。

## Components

组件共同遵守“白面、灰层、黑动作”：默认安静，hover 只改变灰阶，focus 与 selected 直接进入黑色，不通过颜色主题换挡。

### Command Bar & Phase Navigation

- **Desktop:** 60px 白色命令栏；品牌区 174px，Workspace 区 176–230px，阶段区弹性，动作靠右。
- **Active phase:** 文字转纯黑、字重 620，底部显示 2px 黑线；hover 只使用 Canvas Gray。
- **Mobile:** 56px 顶栏保留 Workspace、72×56 当前阶段入口和 44×44 黑色 Run；阶段菜单项至少 44px，高亮项黑底白字。

### Tool Rail

- **Desktop:** 56px 列；按钮 38×38px、11px 圆角，默认 tertiary 图标，hover 为白底黑图标。
- **Active:** 白底、黑图标与 1px inset 线，不改变按钮尺寸。
- **Mobile:** 轨宽保持 56px，按钮增至 44×44px；Dock 和 Inspector 的触发状态与 `aria-pressed` 同步。

### Contextual Docks & Inspector

- **Dock:** 证据、资产和历史共享同一 260px 插槽，列表靠 1px 横线、冷灰区块与间距组织；任何时刻只出现一个 Dock。
- **Evidence parity:** 可拖拽文化/市场证据必须有可见“添加到画布”按钮；手机端按钮保持 44×44px，成功后以 `role=status` 中文消息确认。
- **Inspector:** 桌面列宽 336px，含 44px 工具条、节点标题、七个可滚动页签和内容区；选中节点后绑定，关闭后画布收回空间。
- **Compact overlays:** Dock 从 56px 工具轨右侧进入，Inspector 从右侧进入；都有显式关闭按钮、方向性阴影和焦点归还。

### Flow Nodes

- **Rest:** 标准 300px，宽节点 320px，最小高 68px，14px 圆角、白底和细灰边；只保留节点类型、标题、人工版本与文字状态。
- **Selected:** 几何与坐标完全不变，只切换纯黑边、纯黑 0.5px inset keyline、黑色 handle 和绑定 Inspector。
- **Content boundary:** 摘要、字段和操作不在画布节点内展开；它们进入 Inspector 或独立详情页。
- **Direct manipulation:** 空白区域的 grab/grabbing 反馈对应画布平移；节点自身保持可拖动。主键平移优先，框选显式使用 Shift，避免同一手势产生两种结果。
- **Keyboard semantics:** React Flow 的选择、移动与 live announcement 使用中文；节点组件保持 memoized，稳定回调/配置避免无关重渲染。

### Buttons

- **Primary:** 纯黑底、白字；桌面通常高 36px，移动关键动作高 44px。每个任务区最多一个。
- **Secondary:** 白底、细灰边、石墨字；hover 仅转 Canvas Gray 与 Strong Rule。
- **Disabled:** Raised Gray 底、tertiary 字与 0.72 opacity，继续保留不可用语义。
- **Focus:** 2px 纯黑 outline 与 2px offset，不能换回蓝色 focus ring。

### Inputs / Fields

- **Style:** Canvas Gray 底、默认透明边、10px 圆角；标签在字段上方，placeholder 只作提示。
- **Focus:** 纯黑边与 1px 黑色 ring；浏览器键盘焦点同时保持 2px 外轮廓。
- **Error / Disabled:** 配合文字说明、图形状态和字段关联，不只改变颜色或透明度。
- **Compact text entry:** 760px 以下输入、选择器和 textarea 使用至少 16px 字号，避免移动浏览器自动缩放破坏任务上下文。

### Status

- **Success / Cached / Warning / Error / Running:** 分别使用实心黑圆、中灰圆、空心石墨圆、黑色方点与黑色扇形，并保留中文状态文字。
- **Evidence semantics:** `live`、snapshot/cache、stale、warning 与 error 不得合并；发起过运行不能被写成 live。
- **Collection semantics:** `scheduled / running / healthy / degraded / blocked / failed / paused / interrupted` 使用同一文字加形状语法。部分来源失败必须是 `degraded`，授权或实时开关缺失必须是 `blocked`，不能被正常排程或历史数据掩盖。
- **Connection truth:** 12 秒轮询失败、心跳超过 45 秒或调度线程不在线时，旧在线状态立即失效，连接状态改为中断/离线，写操作禁用并保留重新连接入口。

### Decision Studio

- **Desktop:** 白色 16px 容器、左侧阶段导航、右侧滚动内容和底部操作栏；黑色 Save 是唯一主动作。
- **Mobile:** 全屏、无圆角无阴影；54px 横向阶段条，Save 独占第一行，“恢复系统建议 / 取消”在第二行等分。
- **Accessibility:** `role="dialog"`、`aria-modal="true"`、初始焦点、Escape 关闭、可见焦点与关闭后恢复焦点都是组件组成部分。

### Node Detail & Culture Constellation

- **Node detail:** 白色页面、冷灰内容面和统一 16px 容器；详情主标题、关联节点、编辑器与审核边界沿同一内容轴。
- **Locked context:** 深石墨面只用于 Brief 锁定上下文、Visual provider 或明确的数据分区，不扩散为导航主题。
- **Culture constellation:** 黑色关系画布以“贵州在地文化”为中心，连接分类、22 条正式记录与来源星点；搜索、分类筛选、选点、来源连线和右侧证据 Inspector 是同一任务。桌面支持拖动、滚轮/按钮缩放与键盘操作；移动默认保持页面滚动，显式操作模式才启用单指平移和双指缩放。
- **Selection:** 搜索只剩一个匹配时自动聚焦；普通、选中、分类、来源与中心节点在 forced-colors 中使用不同系统角色，而不是被压成同一前景色。

### Continuous Collection Console

- **Structure:** 顶部连接/调度状态和说明，其后依次为正式记录/来源/候选/心跳概览、独立采集通道、候选审核、事件历史。文化候选只可标记“可结构化”或排除，正式入图仍需字段证据审核。
- **Lane controls:** 每条通道显示排程间隔、最近尝试、最近成功、下一次运行、连续失败与状态；暂停、恢复、立即运行均服从真实连接和总开关，不以禁用控件隐藏原因。
- **Degraded truth:** 文化来源只要有一项失败就显示 `degraded` 并累加失败，不能用“部分成功”写成健康；断线会使最后成功的 UI 快照失效。
- **Market order:** 378 条历史样本、发布/检索时间窗和四平台分布先出现；“持续采集与授权”在可展开区域中显示实时开关、运行时与 xhs/dy/bili/wb 授权阻断，不覆盖上方历史证据。
- **7×24 boundary:** 调度只在 Tool API/容器单副本、持久卷、重启策略、网络和必要授权持续成立时工作；它不是跨副本分布式队列。

### Product Imagery

- **Allowed:** 项目自有且来源可追溯的产品 hero、Concept A/B/C 和 1800×2400 concept poster；保留真实比例、alt、用途和来源状态。
- **Missing / failed:** 缺图像 provider 或本轮失败时显示诚实 warning，并明确“保留上次成功资产 · 本轮未生成”。
- **Forbidden:** `reference_only` 馆藏像素、无来源缩略图、遗留 `og.png` 或外部参考图不能冒充产品内容。

**The Context-before-Density Rule.** 默认只显示完成当前任务所需的信息；证据详情、历史和人工配置保持一跳可达，而不是永久挤压画布。

**The Provenance-before-Imagery Rule.** 图像只有在来源、用途与权利边界可说明时才进入产品界面；缺图必须使用诚实空态。

**The Evidence-before-Control Rule.** 市场页先让用户理解历史样本、时间窗和平台分布，再展开实时采集控制；操作能力不能压住证据口径。

**The Honest Recency Rule.** 旧成功、历史快照和排程存在都不能证明当前在线；轮询、心跳、来源完整性和授权状态必须分别表达。

### Quality Gates

- 所有十个产品路由在 1440×960 与 390×844 运行 axe、唯一 `h1`、图片完整性、alt 与横向溢出检查。
- 手机可见主要交互目标至少 44×44px；Windows forced-colors 必须保留至少 2px 的可见焦点。
- 知识星图必须通过搜索聚焦、选点、按钮/滚轮缩放、桌面拖动/键盘、移动显式操作模式双指缩放与退出后页面滚动测试；forced-colors 必须区分中心、普通与选中节点。
- 采集控制面必须通过初次连接失败、轮询断线后旧状态失效、部分来源 `degraded`、四平台 `blocked` 和写操作禁用测试。
- 图谱、Workspace 与 Decision Studio 必须通过弹层内 axe、焦点圈、Escape 关闭和焦点归还测试。
- 工作台与 Brief 各保留桌面/手机 Windows Chromium 像素基线；只有人工目视确认后的有意变化才能更新快照。
- 当前本地验证为 Python 53 passed、前端单测 5 passed、Playwright 35 passed / 1 intentionally skipped；typecheck、lint、production build、Ruff、shell syntax、lockfile 与 diff 检查通过。
- 自动化通过不等于无障碍认证；真实屏幕阅读器、真实触屏手势与大规模图谱性能仍属于人工/专项验收。

## Do's and Don'ts

### Do:

- Do 使用白色、冷灰、石墨和纯黑建立全部系统层级，并让纯黑主动作保持稀缺。
- Do 保持 60px 桌面命令栏、56px 工具轨、情境 Dock、主画布和 336px Inspector 的工作台骨架。
- Do 让空白画布可用主键/单指直接平移，并保留 Shift 框选、滚轮/捏合缩放和独立节点拖动。
- Do 把黑色关系画布严格限定在可搜索、可选点、可检查来源的文化星图，并让右侧证据 Inspector 保持白色工作面。
- Do 在移动端默认保留文化页纵向滚动，只有用户显式进入“操作星图”后才接管单指平移与双指缩放。
- Do 为所有拖拽创建动作保留点击与键盘等价路径，并让弹层形成可逆焦点闭环。
- Do 保持节点选择前后的几何和坐标一致，只改变黑色 keyline、handle 与 Inspector 绑定。
- Do 在移动端保留 72×56 阶段入口、44×44 Run、44×44 工具控件及可逆 Dock/Inspector。
- Do 让状态同时具有文字、明度与形状，并严格区分 live、cache、stale、warning 和 error。
- Do 让采集控制面区分正式知识、候选、历史快照、最近成功、心跳、`degraded`、`blocked` 和断线，并在市场页先展示 378 条历史证据及时间窗。
- Do 只展示有来源记录的产品/概念图，并保留 alt、节点关系、生成状态和权利边界。
- Do 把 DesignPackage、工厂询价/首样简报和概念海报明确标为量产前材料。

### Don't:

- Don't 在当前工作台恢复米色、暖纸色、蓝色、靛蓝、彩虹渐变或任何彩色系统 chrome。
- Don't 为选择、焦点、运行、成功、警告或错误重新引入彩色语义；使用已定义的黑白灰文字与形状系统。
- Don't 把文化星图的黑底扩散为普通详情页、全站深色主题、装饰网格或营销 hero。
- Don't 让主键拖动同时承担画布平移和框选；框选必须保留 Shift 这一显式修饰键。
- Don't 在移动文化星图默认状态抢占页面滚动，也不要隐藏“操作星图 / 完成”的显式模式边界。
- Don't 把 axe 或视觉快照通过写成完整 WCAG 认证，也不要为让测试变绿而隐藏真实控件或关闭规则。
- Don't 让选中节点扩张、位移、抬升或展开详情，也不要以装饰动效打断关系线阅读。
- Don't 在普通节点、卡片、输入或桌面面板上使用 drop shadow；投影只属于真正覆盖下层任务的浮层。
- Don't 把 pill 用在节点、证据行、长文本或大型容器，也不要恢复 24px 暖卡语言。
- Don't 隐藏缓存时间、运行失败、缺失 provider、下游 stale、机器建议或人工改写来源。
- Don't 把部分来源成功写成 `healthy`，不要在断线后保留旧“在线”，也不要把候选链接自动晋级为正式文化事实。
- Don't 把 378 条历史市场快照、排程存在或曾经授权描述为正在 7×24 实时产出；当前市场实时通道因开关和四平台授权缺失保持 `blocked`。
- Don't 使用 `reference_only` 像素、无来源图像或遗留社交分享图填充产品界面。
- Don't 从当前概念包声称生产发布、工厂下单、商业图稿批准、DFM、合规、社区授权或制造就绪。
