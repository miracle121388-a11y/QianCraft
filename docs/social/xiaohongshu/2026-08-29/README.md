# QianCraft 小红书发布包｜2026-08-29

## 直接发布

1. 复制 [`post.md`](post.md) 中的标题、正文和话题。
2. 按下面顺序上传 `slides/` 中的 8 张 1080×1440 PNG：
   - `01-cover.png`：封面
   - `02-problem.png`：为什么先不画图
   - `03-workflow.png`：五段可审计链路
   - `04-culture.png`：文化证据与地域差异
   - `05-market.png`：四平台历史样本与口径
   - `06-human.png`：七阶段人工决策
   - `07-concepts.png`：A / B / C 概念方向
   - `08-boundary.png`：当前成果、边界与互动收尾
3. 发布前只需在小红书预览页检查平台裁切；核心文字均已留在安全边距内。

## 口径与素材边界

- 所有数字来自当前 QianCraft 0.9.1 项目状态：22 条结构化文化记录、32 条登记来源、378 条四平台历史真实快照、8 条机会、7 个可人工调整阶段、5 项 BOM、6 步装配、6 项质检。
- `378` 明确标注为有限的历史快照，不表述为当前全平台实时趋势，也不作“爆款保证”。
- 概念方向明确标注为概念视觉/概念样，不表述为量产实拍、商业文化授权或制造/合规完成。
- 发布包只使用 QianCraft 自有界面截图、原创概念资产和本轮生成的原创封面场景；没有使用 `reference_only` 馆藏像素。

## 封面主视觉生成记录

- 模式：内置 `image_gen`，以项目原创 `data/design/assets/huaxi_grid_magnet_hero_v1.png` 作为参考图。
- 最终提示词：

```text
Use case: product-mockup
Asset type: Xiaohongshu vertical carousel cover background, 3:4 portrait
Input images: Image 1 is a project-owned concept-product reference; use it only to preserve the product's recognizable design language
Primary request: create a new high-end editorial tabletop photograph of the QianCraft concept magnet in a contemporary design studio, clearly a concept visualization rather than a mass-produced object
Scene/backdrop: cool neutral white and light-gray creative worktable, a few restrained material swatches and a navy thread spool, a cropped monochrome node-workflow screen softly out of focus in the far background; no readable UI text
Subject: one rounded-square dark indigo magnet standing at a slight three-quarter angle, with a tactile navy woven grid panel and restrained ivory and red cross-stitch-like geometric marks inspired by counted-thread order; preserve the overall proportions, dark frame, woven texture, and modular product character from Image 1, but do not copy or invent a complete traditional motif
Style/medium: photorealistic premium product editorial, natural real material texture, subtle imperfections, contemporary Chinese design-magazine sensibility
Composition/framing: 3:4 portrait; product in the lower-right half, generous clean negative space across the upper-left third for later typography; no cropping of the product
Lighting/mood: soft north-window daylight, calm, precise, tactile, thoughtful
Color palette: cool white, light gray, graphite, deep indigo, tiny restrained red and ivory accents
Materials/textures: matte polymer frame, real woven thread texture, uncoated paper, soft fabric swatches
Constraints: no text, no letters, no logos, no watermark; no people; no museum images; no costumes; no ethnic stereotypes; no sacred or ancestor motifs; no factory, packaging, compliance, or mass-production cues; keep the result clearly conceptual and original
Avoid: beige vintage styling, ornate folk decoration, glossy commercial packshot, excessive props, extra products, duplicated objects, illegible pseudo-text
```

## 可复现源文件

- `carousel.html`：8 张卡片的确定性文字排版与图片组合源。
- `assets/cover-concept-visual.png`：内置图像生成得到的无字封面场景。
- `slides/`：可直接上传的最终 PNG。
