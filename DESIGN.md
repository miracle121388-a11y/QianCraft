---
name: QianCraft
description: Evidence-led Creative Instrument Workbench in a warm parchment visual system
colors:
  interaction-indigo: "#3451b2"
  parchment: "#fcfbf8"
  warm-sand: "#f7f4ed"
  linen-border: "#eceae4"
  stone: "#d4d3d0"
  dim-gray: "#5f5f5d"
  faint-text: "#85847f"
  charcoal: "#1c1c1c"
  ink: "#030303"
  culture-indigo: "#17283f"
  culture-teal: "#16745f"
  culture-rust: "#a8654f"
  culture-violet: "#6d6f9f"
  status-success: "#45a17b"
  status-cached: "#6f8498"
  status-warning: "#b7791f"
  status-danger: "#bd4a4a"
typography:
  display:
    fontFamily: "Camera Plain Variable, Noto Sans SC Variable, Noto Sans SC, Inter Variable, DM Sans, Microsoft YaHei, sans-serif"
    fontSize: "60px"
    fontWeight: 480
    lineHeight: 1.04
    letterSpacing: "-0.035em"
    fontFeature: "liga 0"
  heading-large:
    fontFamily: "Camera Plain Variable, Noto Sans SC Variable, Noto Sans SC, Inter Variable, DM Sans, Microsoft YaHei, sans-serif"
    fontSize: "48px"
    fontWeight: 480
    lineHeight: 1.08
    letterSpacing: "-0.03em"
    fontFeature: "liga 0"
  heading:
    fontFamily: "Camera Plain Variable, Noto Sans SC Variable, Noto Sans SC, Inter Variable, DM Sans, Microsoft YaHei, sans-serif"
    fontSize: "36px"
    fontWeight: 480
    lineHeight: 1.12
    letterSpacing: "-0.025em"
    fontFeature: "liga 0"
  heading-small:
    fontFamily: "Camera Plain Variable, Noto Sans SC Variable, Noto Sans SC, Inter Variable, DM Sans, Microsoft YaHei, sans-serif"
    fontSize: "20px"
    fontWeight: 480
    lineHeight: 1.2
    letterSpacing: "-0.025em"
    fontFeature: "liga 0"
  subheading:
    fontFamily: "Camera Plain Variable, Noto Sans SC Variable, Noto Sans SC, Inter Variable, DM Sans, Microsoft YaHei, sans-serif"
    fontSize: "18px"
    fontWeight: 480
    lineHeight: 1.35
    letterSpacing: "normal"
    fontFeature: "liga 0"
  body:
    fontFamily: "Camera Plain Variable, Noto Sans SC Variable, Noto Sans SC, Inter Variable, DM Sans, Microsoft YaHei, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
    fontFeature: "liga 0"
  caption:
    fontFamily: "Camera Plain Variable, Noto Sans SC Variable, Noto Sans SC, Inter Variable, DM Sans, Microsoft YaHei, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: "normal"
    fontFeature: "liga 0"
rounded:
  input: "8px"
  image: "12px"
  container: "16px"
  warm-card: "24px"
  pill: "9999px"
spacing:
  space-4: "4px"
  space-6: "6px"
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
  space-73: "73px"
  space-80: "80px"
  space-144: "144px"
  space-160: "160px"
components:
  button-primary:
    backgroundColor: "rgba(0, 0, 0, 0.88)"
    textColor: "{colors.parchment}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "36px"
  button-secondary:
    backgroundColor: "{colors.parchment}"
    textColor: "{colors.charcoal}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "36px"
  tool-rail-button:
    backgroundColor: "transparent"
    textColor: "{colors.dim-gray}"
    rounded: "{rounded.pill}"
    size: "40px"
  tool-rail-button-active:
    backgroundColor: "color-mix(in srgb, #3451b2 9%, #fcfbf8)"
    textColor: "{colors.interaction-indigo}"
    rounded: "{rounded.pill}"
    size: "40px"
  input-field:
    backgroundColor: "{colors.warm-sand}"
    textColor: "{colors.charcoal}"
    typography: "{typography.body}"
    rounded: "{rounded.input}"
    padding: "10px 12px"
  flow-node:
    backgroundColor: "{colors.parchment}"
    textColor: "{colors.charcoal}"
    rounded: "{rounded.container}"
    width: "300px"
  warm-card:
    backgroundColor: "{colors.warm-sand}"
    textColor: "{colors.charcoal}"
    rounded: "{rounded.warm-card}"
    padding: "24px"
  inspector:
    backgroundColor: "{colors.parchment}"
    textColor: "{colors.charcoal}"
    width: "320px"
---

# Design System: QianCraft

## Overview

**Creative North Star: "Warm Instrument Ledger / 暖纸仪器台账"**

QianCraft 是把文化证据、市场观察、人工决策和设计节点放到同一条可追溯链路上的专业创作仪器，不是营销首页，也不是替用户给出不可审计答案的自动生成器。暖羊皮纸、温砂色和炭黑文字让工作台接近一册正在被使用的研究台账；系统 chrome 安静退后，让当前节点、来源边界和下一步动作成为视觉中心。

复杂度沿工作台边缘按需揭示：56px 阶段命令栏与 64px 工具轨稳定定位，主画布持续占据最大面积，情境 Dock 与 320px Inspector 只在任务需要时出现。Indigo 负责选择、焦点和路径；贵州文化色负责内容与身份；状态、时间、权利和人工/系统来源同时以文字与颜色表达。

材质语言温暖但精确：普通表面不投下阴影，只用 0.5px inset edge、纸色差与语义圆角建立层级。RICOUI Design 只提供系统结构清晰度的参考，不提供可复制的代码、资产、文案或品牌表达。

**Key Characteristics:**

- 羊皮纸画布、温砂表面、亚麻边线和炭黑文字构成低噪声暖色工作环境。
- 56px 阶段命令栏、64px 工具轨、情境 Dock、主画布与 320px Inspector 构成稳定仪器框架。
- Indigo 只表达操作、选择与焦点；贵州文化色停留在内容、节点身份和概念素材。
- 标题字重 480、正文 400；按钮与徽章为 pill，输入 8px、图片 12px、容器 16px、暖面卡 24px。
- 桌面保留工作上下文；移动端以可逆覆盖层和至少 44px 触控目标维持可操作性。

## Colors

系统以暖中性色承担绝大多数面积；interaction indigo 是唯一全局操作色，文化色、状态色和彩虹品牌环境各守自己的范围。

### Primary

- **Interaction Indigo** (`interaction-indigo`): 主路径、选中态、活动阶段、可操作链接和键盘焦点的唯一全局交互色。

### Secondary

- **Guizhou Indigo** (`culture-indigo`): 文化内容、节点身份和深色概念材料。
- **Loom Teal** (`culture-teal`): 文化关系、运行态和已验证内容中的局部语义。
- **Dyed Rust** (`culture-rust`): 工艺、材料或文化风险提示中的内容强调。
- **Archive Violet** (`culture-violet`): 设计节点和概念方向的身份色；不得扩散到全局 chrome。

### Tertiary

- **Verified Green** (`status-success`): 已完成、已验证或可继续的状态。
- **Snapshot Slate** (`status-cached`): 缓存或历史证据快照，必须与“实时”明确区分。
- **Pending Amber** (`status-warning`): 待更新、待确认和警告。
- **Failure Red** (`status-danger`): 失败、错误和阻断状态。

### Neutral

- **Parchment** (`parchment`): 页面、命令栏、节点、Inspector 和决策面板的主底色。
- **Warm Sand** (`warm-sand`): 主画布、工具轨、Dock 分区、输入区和暖面容器。
- **Linen Border** (`linen-border`) 与 **Stone** (`stone`): 普通 1px 边界、hover 边界和弱分隔。
- **Dim Gray** (`dim-gray`) 与 **Faint Text** (`faint-text`): 次要说明、元数据和短标签；关键动作不使用弱灰。
- **Charcoal** (`charcoal`) 与 **Ink** (`ink`): 主文本、深色主按钮和极少量锁定上下文面。

### Brand Environment

- **Rainbow Hero Gradient** (`lovable-hero-gradient`): 仅登记为 QianCraft 品牌环境 token，供未来经批准的营销或品牌首屏使用；当前 Creative Instrument Workbench 不渲染、不裁切也不派生成 UI 强调色。

**The Functional Indigo Rule.** Interaction Indigo 只用于可操作、已选择、主路径和键盘焦点；同一视口不以 Indigo 装饰非交互内容。

**The Culture Stays in Content Rule.** 靛青、锈色、青绿和紫罗兰只进入文化记录、节点身份、状态或概念素材，不染色全局导航与工作台底色。

**The State Is Evidence Rule.** 成功、缓存、待更新、警告与错误必须保留各自的语义色和文字标签，不能只靠颜色传达。

**The Gradient Boundary Rule.** Rainbow Hero Gradient 是品牌环境而不是工作台 token；在当前工具界面中的任何使用都属于系统漂移。

## Typography

**Preferred UI Family:** Camera Plain Variable

**Current CJK Runtime:** Noto Sans SC Variable / Noto Sans SC
**Fallbacks:** Inter Variable、DM Sans、Microsoft YaHei、sans-serif

**Character:** Camera Plain Variable 是首选家族名称和拉丁字符方向；当前实际自托管中文由 Noto Sans SC fallback 承担。所有界面角色保持同一无衬线家族链，不另设装饰性衬线层；`font-feature-settings: "liga" 0` 保持中文、节点 ID 和技术字段的形态稳定。

### Hierarchy

- **Display**（480，60px，1.04）: 仅供未来品牌环境或极少量展示级标题；当前工作台不使用。
- **Heading Large**（480，48px，1.08）: 大型详情或经批准的品牌标题。
- **Heading**（480，36px，1.12）: 节点详情主标题与重要决策任务句。
- **Heading Small**（480，20px，1.2）: Dock、Inspector、详情容器与决策区标题。
- **Subheading**（480，18px，1.35）: 解释性副标题和局部任务标题。
- **Body**（400，16px，1.6）: 摘要、证据说明和编辑内容；连续阅读宽度约 68ch。
- **Caption**（400，14px，1.45）: 控件、阶段、字段标签和元数据；需要强调时最多使用 strong 600。

**The Honest Camera Rule.** 文档和 CSS 可以把 Camera Plain Variable 列为首选名称，但不能声称当前中文由 Camera Plain 渲染；中文事实来源是 Noto Sans SC fallback。

**The 480/400 Rule.** 标题统一 480，正文统一 400，只有状态、主按钮或短关键值使用 600；不以 700–900 的黑重制造层级。

## Layout

桌面工作台保持四列仪器框架：顶部 56px 命令栏，下方依次为 64px 工具轨、可选 248px 情境 Dock、弹性主画布和可选 320px Inspector。证据、资产与历史共享同一 Dock 插槽，任何时刻只显示一个。1280px 以下同时开启两侧面板时，Dock 收至 230px、Inspector 收至 306px，主画布仍保有弹性宽度。

主画布以 24px 点阵和细关系线组织节点；非选中节点只保留 68px 头部，选中节点展开正文与动作并上移 4px。300px 是标准节点宽度，320px 用于视觉生成和概念节点。画布上下文位于左上，控件左下，图例与小地图靠右下，均不得遮挡选中节点的主操作。

Decision Studio 在宽屏上是居中的最大 1380px × 900px 覆盖层，左侧 218px 阶段导航、右侧滚动内容、底部持久操作栏；980px 以下占满视口，680px 以下阶段导航改为 54px 高的水平可滚动条，内容改单列，主保存动作固定在底部。节点详情页最大内容宽度 1280px，主内容、关联节点和页脚沿同一轴对齐。

760px 及以下，工作台仅保留 54px 布局轨和弹性画布，轨内按钮仍为至少 44px 触控目标；Dock 从左侧轨后以不超过 300px 的覆盖层进入，Inspector 从右侧以不超过 336px 的覆盖层进入，二者都可原路关闭。详情顶栏变为两层粘性工具条，四个主要动作均为 44px 高；双栏和多栏内容统一折为单列，关联节点保持水平滚动。

**The Canvas First Rule.** 任何桌面或移动布局都先保护节点画布和当前任务，再决定外围面板能否常驻。

**The Reversible Edge Rule.** Dock、Inspector、Decision Studio 和详情关联条都是可逆上下文；打开必须有明确关闭方式，关闭后返回原任务与焦点。

**The 44px Touch Rule.** 760px 及以下的图标按钮、顶栏动作和关键保存/取消动作，命中区域不得小于 44 × 44px。

## Elevation & Depth

普通表面没有 drop shadow。羊皮纸节点、温砂卡、输入、工具栏和 Decision Studio 使用 0.5px inset edge，把边界压入材质而不是让对象漂浮；主层级来自纸色差、边线和留白。选中节点仍可上移 4px，但只切换 Indigo 边与较强 inset edge，不增加投影。Decision Studio 依靠半透明 charcoal backdrop 说明阻塞关系。

真正覆盖画布的移动端 Dock 与 Inspector 可以保留单向、低强度 drop shadow，帮助用户理解它们来自哪一侧；该例外只属于可逆 viewport overlay，不能复用到普通卡片、节点、按钮或桌面对话框。节点选择以 160ms `ease` 变化，列宽以 180ms `ease` 变化；`prefers-reduced-motion: reduce` 时布局和节点过渡关闭，运行状态脉冲改为静态语义标记。

### Shadow Vocabulary

- **Inset Edge Strong** (`oklch(0 0 0 / 0.25) 0 0 0 0.5px inset`): 选中节点与 Decision Studio 的结构边缘，不产生投影。
- **Inset Edge Soft** (`oklch(0 0 0 / 0.16) 0 0 0 0.5px inset`): 普通按钮、输入、节点、暖面容器和详情表面。
- **Compact Dock Overlay** (`14px 0 30px rgba(18, 24, 32, 0.16)`): 仅移动端左侧可逆 Dock。
- **Compact Inspector Overlay** (`-14px 0 30px rgba(18, 24, 32, 0.16)`): 仅移动端右侧可逆 Inspector。

**The Inset Surface Rule.** 普通表面只能使用 inset edge；任何非 overlay 的 drop shadow 都是设计系统违例。

**The Overlay Exception Rule.** 单向 drop shadow 只服务于移动端可逆外围面板，关闭后必须消失且不得留下布局位移。

## Shapes

圆角是语义尺度而不是装饰偏好：输入与字段为 8px，图像和缩略图为 12px，节点、详情容器和 Decision Studio 为 16px，独立暖面卡为 24px，按钮、徽章、工具轨控件和短状态标签使用 9999px pill。圆角越大，容器越独立；嵌套容器不得层层使用 24px。

边框通常为 1px 亚麻线；活动阶段使用 2px Indigo 底线，活动工具使用 2–3px inset keyline。Lucide 线性 SVG 是控制图标的默认语言，常规尺寸 14–21px，图标必须与可读标签或 `aria-label` 配对。

**The Semantic Radius Rule.** 8/12/16/24/pill 分别对应字段、图像、容器、暖面卡和动作/徽章，不按视觉心情混用。

**The Purposeful Pill Rule.** Pill 只属于按钮、徽章、工具轨控件和短状态；长文本容器、证据卡和节点不能胶囊化。

## Components

组件的共同气质是“温暖、克制、可操作”：默认状态像纸上工具，交互、选择与警告在需要时立即清晰。

### Command Bar

- **Structure:** 桌面固定 56px 高，羊皮纸底、亚麻底线；品牌 174px、工作区命令 150–220px、阶段导航弹性居中、动作靠右。
- **Active stage:** 文字由 dim gray 转 charcoal，并在底部出现 2px Indigo 线；hover 只增加 warm sand 底。
- **Mobile:** 只保留品牌和工作区命令；阶段与运行操作转移到画布、工具轨或详情动作区。

### Tool Rail

- **Shape:** 桌面按钮 40 × 40px pill；移动端命中区至少 44 × 44px。
- **Default / Hover:** Dim gray 图标；hover 使用 parchment 底，不抬升。
- **Active:** Indigo 图标、9% Indigo 与 parchment 混合底、2px 左侧 inset keyline；`aria-pressed` 与视觉状态同步。

### Contextual Docks & Inspector

- **Dock:** 证据、资产与历史共享 248px 插槽，warm sand / parchment 表面和亚麻分隔；列表靠线与间距而不是投影组织。
- **Inspector:** 桌面 320px；36px 工具条、82px 节点头、七列页签和滚动内容。选择节点时自动绑定，关闭后画布恢复完整宽度。
- **Overlay:** 移动端 Dock 与 Inspector 覆盖画布，可使用方向性 overlay shadow；关闭按钮和触发按钮必须形成可恢复焦点对。

### Flow Nodes

- **Rest:** 标准宽 300px、16px 容器圆角、parchment 底、亚麻边与 soft inset edge；未选中时折叠正文与动作，只保留节点身份、标题、人工版本和文字状态。
- **Selected:** Indigo 边、strong inset edge、上移 4px并展开摘要/字段/动作；不增加 drop shadow。
- **States:** `success`、`cached`、`warning/stale`、`error`、`running` 同时显示状态点和中文标签；运行脉冲在减少动态偏好下静止。

### Buttons & Badges

- **Primary:** 88% black 底、parchment 字、pill，高 36px；每个任务区最多一个高强度主动作。
- **Secondary:** Parchment 底、亚麻边、soft inset edge 与 charcoal 字；hover 仅转 warm sand 与 stone 边。
- **Badges:** 短状态、版本和数量使用 pill；颜色必须搭配文字，不依赖纯色点。
- **Mobile:** 主按钮、取消和图标按钮命中区至少 44px。

### Inputs / Fields

- **Style:** Warm sand 底、亚麻边、8px 圆角、soft inset edge；标签在字段上方，不依赖 placeholder。
- **Focus:** 2px Indigo 70% 混色 outline 与 2px offset；浏览器键盘焦点保持可见。
- **Error / Disabled:** 使用文字说明、语义色和字段关联；不能只把边框变红或仅降低透明度。

### Images & Warm Cards

- **Images:** 产品 hero、Concept A/B/C 和 poster 缩略图使用 12px 圆角，保留真实比例、alt、节点关系和来源边界。
- **Warm cards:** 可独立阅读的大型证据/说明卡使用 warm sand、24px 圆角、24px 内边距与 soft inset edge；容器内的小行项目回到线与间距。
- **Evidence rows:** 文化与市场证据默认使用真实标题、来源类型、权利状态和代码原生图标，不虚构缩略图填空。

### Decision Studio & Node Detail

- **Decision Studio:** 桌面 16px 容器圆角与 strong inset edge，无 drop shadow；移动端全屏无圆角，阶段导航水平滚动，保存和取消保持底部可达。
- **Accessibility:** `role="dialog"`、`aria-modal="true"`、初始焦点、Tab 焦点圈、Escape 关闭和关闭后恢复焦点都是组件组成部分。
- **Node detail:** 最大宽度 1280px；标题区、关联节点、编辑器和审核上下文沿统一轴。深 charcoal 面只用于“锁定上下文”或图像管线，不返回全局 chrome。

### Product Imagery

- **Allowed:** 只显示项目拥有且可追溯的 Concept A/B/C、产品 hero 和正式 concept poster；使用真实节点记录、明确 alt 文本与已登记来源。
- **Forbidden sources:** 不把 approved comp、`reference_only` 馆藏像素、无来源的 plush alternate 或遗留 `og.png` 当作工作台内容。
- **Brand gradient:** Rainbow Hero Gradient 不替代任何产品图，也不作为工作台背景、节点边、按钮或状态色。

**The Context-before-Density Rule.** 默认只显示完成当前任务所需的信息；详情、历史和人工配置通过一跳进入，而不是永久挤压主画布。

**The Provenance-before-Imagery Rule.** 一张图只有在来源、用途和权利边界可说明时才进入界面；缺图必须显示诚实空态，不能用参考图或 invented thumbnail 补位。

## Do's and Don'ts

### Do:

- Do 让 Interaction Indigo 只承担主路径、选择、焦点和可操作链接，并在同一视口保持稀缺。
- Do 用 parchment / warm sand 色差、亚麻线和 inset edge 组织高密度证据；让主画布始终是最大区域。
- Do 按 8px 输入、12px 图片、16px 容器、24px 暖面卡和 pill 动作/徽章使用圆角。
- Do 同时显示状态色与状态文字，明确 live、snapshot/cache、stale、warning 和 error 的差别。
- Do 为图标控件使用 Lucide SVG、可读标签或 `aria-label`，并维护至少 44px 触控区域与可见键盘焦点。
- Do 只使用有项目来源记录的产品图和概念图，保留 alt、节点关系、权利状态与用途边界。
- Do 把 RICOUI Design 仅视为结构清晰度参考，重新建立 QianCraft 自己的内容、色彩、组件和交互语义。

### Don't:

- Don't 把贵州靛青、锈色、青绿或紫罗兰铺到全局顶栏、工具轨、按钮体系或页面底色。
- Don't 在普通表面使用 drop shadow、玻璃拟态、硬偏移阴影或无语义的多层圆角；普通表面只能有 inset edge。
- Don't 把 pill 用在长文本、节点、证据卡或大型容器；pill 只属于动作、工具和短状态。
- Don't 在当前工作台使用 Rainbow Hero Gradient；它只是登记中的品牌环境 token。
- Don't 隐藏失败、缺少图像 provider、缓存时间、下游 stale、机器建议或人工改写来源。
- Don't 使用 approved comp 的 invented thumbnails/content、`reference_only` 像素、无来源 plush alternate 或遗留 `og.png` 填充产品界面。
- Don't 复制 RICOUI Design 的代码、资产、文案或品牌表达，也不要从当前概念包声称量产、DFM、合规、社区授权或工厂下单就绪。
