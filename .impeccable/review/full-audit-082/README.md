# QianCraft 0.8.2 全页面交互与视觉验收

验收日期：2026-08-29  
视口：桌面 1440×960；手机 390×844  
范围：工作台 `/` 与 9 个节点详情页；页面首屏、详情页底部、工作台关键覆盖状态和真实指针/键盘交互。

## 截图索引

| 页面 | 桌面 | 手机 |
|---|---|---|
| 工作台 | [首屏](after/desktop/workbench.png) | [首屏](after/mobile/workbench.png) · [拖动后](after/mobile/workbench-panned.png) |
| 文化图谱 | [首屏](after/desktop/culture.png) · [底部](after/desktop/culture-bottom.png) | [首屏](after/mobile/culture.png) · [底部](after/mobile/culture-bottom.png) |
| 市场雷达 | [首屏](after/desktop/market.png) · [底部](after/desktop/market-bottom.png) | [首屏](after/mobile/market.png) · [底部](after/mobile/market-bottom.png) |
| 机会策略 | [首屏](after/desktop/strategy.png) · [底部](after/desktop/strategy-bottom.png) | [首屏](after/mobile/strategy.png) · [底部](after/mobile/strategy-bottom.png) |
| 设计任务书 | [首屏](after/desktop/brief.png) · [底部](after/desktop/brief-bottom.png) | [首屏](after/mobile/brief.png) · [底部](after/mobile/brief-bottom.png) |
| 视觉方向 | [首屏](after/desktop/visual.png) · [底部](after/desktop/visual-bottom.png) | [首屏](after/mobile/visual.png) · [底部](after/mobile/visual-bottom.png) |
| Concept A | [首屏](after/desktop/concept-a.png) · [底部](after/desktop/concept-a-bottom.png) | [首屏](after/mobile/concept-a.png) · [底部](after/mobile/concept-a-bottom.png) |
| Concept B | [首屏](after/desktop/concept-b.png) · [底部](after/desktop/concept-b-bottom.png) | [首屏](after/mobile/concept-b.png) · [底部](after/mobile/concept-b-bottom.png) |
| Concept C | [首屏](after/desktop/concept-c.png) · [底部](after/desktop/concept-c-bottom.png) | [首屏](after/mobile/concept-c.png) · [底部](after/mobile/concept-c-bottom.png) |
| Poster | [首屏](after/desktop/poster.png) · [底部](after/desktop/poster-bottom.png) | [首屏](after/mobile/poster.png) · [底部](after/mobile/poster-bottom.png) |

工作台状态：

- 桌面：[Workspace](after/desktop/workbench-workspace.png) · [Dock](after/desktop/workbench-dock.png) · [Inspector](after/desktop/workbench-inspector.png) · [Decision Studio](after/desktop/workbench-decision.png)
- 手机：[Workspace](after/mobile/workbench-workspace.png) · [阶段菜单](after/mobile/workbench-phase.png) · [Dock](after/mobile/workbench-dock.png) · [Inspector](after/mobile/workbench-inspector.png) · [Decision Studio](after/mobile/workbench-decision.png)

## 发现与修复

- 空白画布原先只允许中键/右键平移，主键拖动被框选占用。现改为主键/单指直接平移，`Shift + 拖动` 保留框选，滚轮/捏合继续缩放，节点仍可独立拖动。
- 手机 Workspace 菜单原先从 `x=-34` 越出屏幕；现稳定在 `x=56…348`，所有菜单控件为 44px 高。
- React Flow 缩放控制、详情页保存/下载/筛选/操作、运行信息与方法说明等主要手机触控项统一到至少 44px。
- Poster 详情的长工厂阶段值曾令内部滚动容器从 375px 溢出到 394px；现所有 10 个手机页面均为 `scrollWidth === clientWidth`。
- 首屏之外还发现旧版绿色标签/引用边线、深蓝海报拆解卡、红色步骤点与偏蓝页脚文字；现全部回到冷灰、石墨与黑。原始产品图、证据图、A/B/C 与项目海报作为内容资产保留来源色。

## 实机结果

- 桌面画布平移：`translate(20px, 210px)` → `translate(180px, 165px)`；缩放：`0.82` → `0.984`；阶段“交付”能定位并选中 `poster`。
- 手机画布平移、节点拖动均成功；节点双击深链到 `/nodes/brief?workspace=guizhou-miao-demo`。
- 手机阶段菜单选择“交付”后自动关闭并选中 `poster`；Dock 和 Inspector 均可用 Escape 关闭，焦点分别归还“证据库”和 `brief` 节点。
- 10/10 桌面页面与 10/10 手机页面：破图 0、内部横向溢出 0、全滚动范围彩色系统 chrome 0。
- 手机主要 `button / select / summary / detail-download` 扫描：小于 44px 的可操作项 0；React Flow 法定 attribution 与正文内联引用按内联目标例外保留。
- `pnpm test` 5/5、`pnpm typecheck`、ESLint、Vinext 五阶段 production build 与 `git diff --check` 通过。

边界：本轮只更新本地前端、设计契约与验收证据，没有部署；线上受保护实例仍是 0.8.0。当前设计产物仍只到概念展示、DesignPackage、工厂询价/首样简报与概念海报。
