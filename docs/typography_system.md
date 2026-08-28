# QianCraft 界面令牌、中文排版与画布比例

## 目标

QianCraft 是高密度创作工具，不是官网，也不是静态展示 Demo。本轮界面系统同时解决三件事：让当前任务可读、让复杂证据按需出现、让桌面与手机端都可以完成真实操作。完整可执行规范见根目录 [`DESIGN.md`](../DESIGN.md)，产品定位见 [`PRODUCT.md`](../PRODUCT.md)。

## 参考与转译原则

- Flipbook 提供“大标题、有限层级、暖纸张、视觉优先”的早期排版启发。
- RICOUI Design 提供“全局导航 / 情境工具 / 主工作区 / Inspector”之间的结构清晰度参考。
- 用户提供的 warm parchment token set 提供当前画布、表面、边、文字、间距、圆角和阴影基线。

项目没有复制这些参考的代码、品牌资产或文案。QianCraft 只保留与真实工作台相符的系统原则，并继续使用自身节点、证据、状态和文化内容色。

## 令牌文件

原始 CSS 变量位于 [`web/app/variables.css`](../web/app/variables.css)，通过 `web/app/globals.css` 统一映射：

| 语义 | Token | 值 |
|---|---|---:|
| 页面画布 | `--lovable-parchment` | `#fcfbf8` |
| 次级表面 | `--lovable-warm-sand` | `#f7f4ed` |
| 发丝线 | `--lovable-linen-border` | `#eceae4` |
| 禁用/强分隔 | `--lovable-stone` | `#d4d3d0` |
| 辅助文字 | `--lovable-dim-gray` | `#5f5f5d` |
| 主文字 | `--lovable-charcoal` | `#1c1c1c` |
| 最高强调 | `--lovable-ink` | `#030303` |
| 链接/选择/焦点 | `--lovable-indigo-accent` | `#3451b2` |

附带的 prismatic gradient 作为品牌环境 token 保留，但当前 Workbench 不使用：规范明确要求它只出现在 Hero 或紧凑发送控件，而 QianCraft 当前页面是操作工作台，不是营销 Hero。

## 字体与字号

- `Camera Plain Variable` 保留为用户令牌中的首选家族名；当前项目没有获得或打包其字体文件，因此不会伪装成已经加载。
- 实际中文界面由自托管 `Noto Sans SC Variable` 承担，回退至 Noto Sans SC、Microsoft YaHei 和系统 sans-serif。
- Noto Serif SC 仅保留给经审核的文化叙事与证据阅读，不再用于高频 chrome、按钮或节点操作。
- 字体关闭标准连字；中文不强制套用负字距，主要标题才使用约 `-0.025em` 的紧凑字距。

当前主阶梯：

| 层级 | 尺寸 / 行高 / 字重 | 用途 |
|---|---|---|
| Caption | 14px / 1.5 / 400 | 标签、字段说明、短元数据 |
| Body | 16px / 1.5 / 400 | 解释、摘要、可编辑内容 |
| Subheading | 18px / 1.38 / 400 | 重点说明和导语 |
| Heading small | 20px / 1.25 / 480 | Dock、Inspector 和内容区标题 |
| Heading | 36px / 1.1 / 480 | 节点详情主标题与决策任务句 |

11–13px 仅允许用于极短的节点代码、版本、状态或画布级微标签，不能承载完整事实、主要动作或长段说明。

## 间距、形状与深度

- 紧凑组件使用 6–8px 间距，字段与卡片使用 16–24px 内边距。
- 输入为 8px，图片为 12px，主容器为 16px，暖面内容卡可到 24px。
- 主要按钮、顶栏动作和状态徽标使用 pill；节点、Dock、Inspector 与对话框仍按容器语义使用 16px，避免把整个工作台做成泡泡墙。
- 普通表面仅用 linen 边或 0.5px inset edge。Drop shadow 不用于普通卡片；覆盖层依靠遮罩和边界建立层级。
- 主动作使用接近黑色的 charcoal pill；`#3451b2` 只用于链接、选择、阶段指示和键盘焦点，不铺满全局 chrome。

## 画布与响应式比例

桌面：

- 56px 顶部阶段命令栏。
- 64px 工具轨。
- 可选 248px 证据 / 资产 / 历史 Dock。
- 弹性 React Flow 主画布。
- 可选 320px Inspector。
- 标准节点 300px，视觉与概念宽节点 320px；默认视口从策略到任务书保持可读，并允许用户平移、缩放和 Fit View。

760px 及以下：

- 顶部只保留品牌与工作区；主画布继续是默认内容。
- 工具轨为 54px，按钮命中区至少 44 × 44px。
- Dock 与 Inspector 变为可逆左右覆盖层，不永久挤压画布。
- 打开时聚焦当前节点；Decision Studio 采用水平阶段条和底部持久保存动作。
- 节点详情折为单列，顶栏动作至少 44px 高，关联节点可横向触控滚动且不显示笨重原生滚动条。

## 可访问性与验收基线

- Human Decision Studio 具备初始焦点、Tab 焦点闭环、Escape 关闭和关闭后焦点恢复。
- 选择、缓存、待更新、警告和错误都同时使用文字与颜色，不只依赖色彩。
- 当前浏览器验收覆盖 1440 × 900 工作台、决策工作室、节点详情，以及 390 × 844 三类对应页面。
- 暖纸色切换后专项复核锁定上下文对比度；深色证据面板仍使用 charcoal / parchment 组合。
- 当前自动基线为 Python 37/37、Workbench TypeScript 5/5；TypeScript、ESLint、Ruff 与 Vinext 五阶段生产构建均需在发布前通过。
