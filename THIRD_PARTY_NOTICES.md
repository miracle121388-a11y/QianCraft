# Third-party notices

QianCraft 的 `app/`、`scripts/`、`tests/`、`web/` 与自有数据编排层为独立实现。外部源码包通过适配器或明确的包依赖使用，未删除其版权声明。

| 本地源码包 | 发现位置 | 上游许可 | 在 QianCraft 中的处理 |
|---|---|---|---|
| LightRAG | `local_culture/LightRAG-main` | MIT | 作为可替换知识图谱运行时；保留原 LICENSE |
| MediaCrawler | `market-intel_agent/MediaCrawler-main` | NON-COMMERCIAL LEARNING LICENSE 1.1 | 仅作为显式开启的本地学习/研究适配器；不得直接用于商业抓取或大规模抓取 |
| GPT Researcher | `researcher_agent/gpt-researcher-main` | 源码包内 LICENSE 为 Apache-2.0；`pyproject.toml` 元数据存在 MIT 标注差异 | 不修改上游；按源码包 LICENSE 与 NOTICE 要求从严处理 |
| XYFlow / React Flow | `flow/xyflow-main`；Web 使用 `@xyflow/react@12.11.5` | MIT，Copyright © 2019–2025 webkid GmbH | 保留上传源码包的 LICENSE；QianCraft 仅在 `web/` 产品层定义节点、状态、交互与视觉系统 |
| Noto Sans SC / Noto Serif SC | Web 使用 `@fontsource-variable/noto-sans-sc@5.3.0`、`@fontsource-variable/noto-serif-sc@5.3.0` | SIL Open Font License 1.1 | 通过 Fontsource 自托管可变字体与 unicode-range 子集；不调用外部字体 CDN，包内 LICENSE 保持随依赖安装 |

商业化前必须完成两项工作：取得 MediaCrawler 权利人的商业书面授权，或替换为具有合适商业许可/官方数据授权的采集实现；同时由法务复核全部第三方依赖及平台数据使用条款。
