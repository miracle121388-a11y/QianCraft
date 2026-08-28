# QianCraft Workbench asset manifest

Audited 2026-08-29 against the archived 1440 × 900 spatial comp, the final warm-parchment implementation, its design contract, current asset routes, and the shipping rasters. This is an implementation inventory, not a license or manufacturing-readiness claim.

## Reuse

| Asset | Intended use | Provenance status |
| --- | --- | --- |
| `/assets/official/product-hero.png` → `data/design/assets/huaxi_grid_magnet_hero_v1.png` (1024 × 1536, SHA-256 `87f6f9e6…8ea7`) | Concept A thumbnail/hero in canvas, Asset Dock, Decision Studio, node detail and poster export. This is the one real product asset approved as the comp input. | Project-owned generated concept asset. Exact prompt is in `data/outputs/poster_render_request.json`; path/hash and `reference_only_images_used: false` are in `data/outputs/design_render_manifest.json`. The prompt is embedded in the PNG. `web/public/product-hero.png` is a byte-identical static duplicate; do not present it as a separate asset. |
| `/assets/workbench/guizhou-miao-demo/concept-b-v1.png` and `concept-c-v1.png` → `data/workbench/generated/guizhou-miao-demo/` (1254 × 1254) | Existing Concept B/C thumbnails and detail imagery wherever the real workspace nodes request them. | Project-owned generated concept assets. Exact prompts, timestamps, refreshed SHA-256 hashes and cultural boundary are recorded in `concept-visual-manifest.json`; workspace records repeat the hashes. Both PNGs carry embedded prompts. |
| `/assets/official/design-poster.png` → `data/outputs/design_poster.png` (1800 × 2400, SHA-256 `7e951e4e…b8e5`) | Existing poster node/detail/download only. | Project-owned compositor output using the approved hero. `data/outputs/design_render_manifest.json` records engine, poster/hero hashes, exact-text composition and no reference-only pixels. Origin metadata is embedded. The formerly stale `web/public/design-poster.png` has been replaced with this byte-identical official poster. |

## Produce

**Empty — no new raster assets are required for this implementation.** The canvas grid, seams, node icons, status marks, evidence rows and empty states should remain DOM/CSS/Lucide UI. The brief expressly rejects the comp's invented evidence thumbnails, and existing Concept A/B/C plus the poster cover all image-bearing product states.

## Do not use

| Asset/reference | Reason |
| --- | --- |
| `.impeccable/mocks/workbench-creative-instrument.png` and its invented thumbnails/content | Archived spatial exploration only; its cool graphite/cobalt treatment was superseded by the user-supplied warm-parchment token system. Never ship it, crop it into the UI, or use it as a background. Its invented names, dates, evidence imagery and thumbnails are explicitly non-literal. |
| `reference_only` museum/cultural-source pixels | Research reference only. Do not copy, train on, thumbnail, texture-map or imply commercial artwork rights from them. Textual provenance, titles and rights labels may be shown from real data. |
| `data/design/assets/needle_layer_plush_hero_v1.png` | Unreferenced alternate plush-product visual; it conflicts with the selected modular-magnet concept and has no located prompt/hash sidecar. |
| `web/public/og.png` | Keep only for the existing social metadata route. Do not reuse it inside the Creative Instrument Workbench: its ornate dark-green/red campaign world conflicts with the approved parchment/warm-sand/charcoal/interaction-indigo operating surface. The PNG now embeds an honest legacy-origin note because its original generation parameters were not recorded. |

## Provenance gaps and missing needs

- The post-update provenance scan reports **0 missing** across `web/public` (3), `data/workbench/generated/guizhou-miao-demo` (2), and `data/outputs` (1). The production hero under `data/design/assets` is embedded; the unrelated plush alternate remains without origin and is excluded from the Docker release context.
- No origin record was found for `data/design/assets/needle_layer_plush_hero_v1.png`; it is explicitly non-shipping and non-product.
- The requested path `data/workbench/data/outputs` does not exist. Current canonical locations are `data/workbench/generated/guizhou-miao-demo/` for B/C, `data/design/assets/` for Concept A, and `data/outputs/` for the poster. Do not create a parallel asset tree.
- No evidence thumbnails are missing. Use real titles, source type, rights/status and compact code-native icons rather than manufacturing substitute imagery.
