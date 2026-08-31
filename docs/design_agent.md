# QianCraft Design Agent

## 目标与边界

Design Agent 把策划阶段的 `data/outputs/designer_handoff.json` 转成一个可展示、可追溯、可供工厂报价和首样讨论的概念设计包。它输出成品形象、文化元素与风格、产品结构、尺寸、BOM、图案应用、装配、质检和艺术化海报，但不宣称已经量产定稿、取得商业文化授权或完成产品合规。

当前授权边界是 `concept_visual_and_prototype_brief`，流程在 `production_release` 前停止。工厂可据此评估首样与报价，不能把它直接当作开模图、生产工程图、合规证书或采购订单。

## 接口

```text
DesignerHandoff JSON
        │ Pydantic 校验 + 文件 SHA-256
        ▼
Design Agent
        ├── 只从 Top 3 中选择主机会
        ├── 优先 verified、具体产品形态和较低文化敏感度
        ├── 将多地域方向缩窄为单一地域首样
        ├── 生成文化转译、产品和制造拆解
        └── 输出 PosterRenderRequest
                    │
                    ├── 可选原创生成式成品主视觉
                    └── 本地精确文字排版器
                              ▼
                    1800 × 2400 设计海报 + RenderManifest
```

输入文件必须能由 `DesignerHandoff` 契约重新载入，且 `ready=true`。Design Agent 在 `DesignInputContract.source_sha256` 中记录输入文件摘要；主机会编号必须存在于输入 Top 3，文化和市场证据编号必须来自输入白名单。

## 当前首版方案

最新实机方案为“针格模块｜花溪挑花互动冰箱贴（概念样）”。系统从 OPP-006 的多支系收藏方向中只选取花溪单一首样，用原创数纱十字网格表达针脚方向和重复秩序，不复制完整馆藏纹样。OPP-002 的鸟纹、蝶纹与祖源相关可能性在社区确认前不自动视觉化；OPP-004 保留为后续独立变体。

首样包当前包含：

- 76 × 76 × 8 mm 圆角框体和 58 × 58 mm 可替换织物面板，全部尺寸与公差均标为首样目标。
- 5 项 BOM、1 组原创图案应用、6 步装配、6 项质检、包装与安全合规提示。
- 3 个文化审核门、3 个工程审核门和 5 个工厂待确认问题。
- 成品主视觉、前/侧/背视关系、爆炸拆解、材料表和工艺路径合成在一张 1800 × 2400 竖版海报中。

## 正式输出

| 文件 | 作用 |
|---|---|
| `data/outputs/design_specification.json` | DesignPackage 机器事实源 |
| `data/outputs/design_specification.md` | 从同一 DesignPackage 自动渲染的人读版本 |
| `data/outputs/poster_render_request.json` | 成品视觉与海报面板需求、精确文案和生成提示词 |
| `data/outputs/design_poster.png` | 最终艺术化设计海报 |
| `data/outputs/design_render_manifest.json` | 海报和主视觉路径、SHA-256、画布与像素使用声明 |

主流水线总计输出 13 个正式路径，并把 `design_agent` 与 `poster_renderer` 的 `live|cache|unavailable` 状态写入 `run_manifest.json`。

## 视觉生成与排版

成品主视觉可由生成式图像工具生成，但必须只接收文字化结构原语，不得接收 `reference_only` 馆藏图片、描摹底图或完整传统纹样。当前 `huaxi_grid_magnet_hero_v1.png` 是基于原创抽象网格、材料和结构描述生成的无文字资产；完整实际提示词保存在 `poster_render_request.json` 的 `image_prompt` 字段。

中文标题、尺寸、BOM 和工艺说明全部由 `app/designer/poster.py` 在本地精确绘制，避免生成式图像中文字失真。`DesignRenderManifest.reference_only_images_used=false` 是强制验收项，海报与主视觉分别记录 SHA-256。

## 运行

完整流水线使用本地主视觉：

```powershell
conda run --no-capture-output -n qiancraft python scripts\run_demo.py --mode auto --design-hero data\design\assets\huaxi_grid_magnet_hero_v1.png
```

只重跑 Design Agent，并同步已有运行清单：

```powershell
conda run --no-capture-output -n qiancraft python scripts\run_design_agent.py --hero-image data\design\assets\huaxi_grid_magnet_hero_v1.png --update-run-manifest
```

不传 `--hero-image` 时，系统仍会用本地几何占位视觉生成完整海报，并把渲染状态诚实标为 `cache`。

## 工厂与商业化前门禁

- 社区或保护单位确认地域、工艺表述、原创网格转译、参与者署名、收益、返修和撤回机制。
- 工程方确认磁体等级与封装、目标吸附力、卡合结构、拆装循环、绣线耐磨、跌落和儿童小部件风险。
- 根据实际销售年龄和地区完成材料、标签、包装及适用标准测试。
- 用实物线卡和材料样确认颜色；不得把展示色误称为传统标准色。
- 量产前另行形成工程图、DFM、成本、模具、供应链、合规与授权签署文件。
