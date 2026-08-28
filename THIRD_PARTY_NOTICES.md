# Third-party notices

QianCraft 的 `app/`、`scripts/`、`tests/` 与自有数据编排层为独立实现。三个上游源码包仅通过适配器调用，未复制进 QianCraft 自有模块，也未删除其版权声明。

| 本地源码包 | 发现位置 | 上游许可 | 在 QianCraft 中的处理 |
|---|---|---|---|
| LightRAG | `local_culture/LightRAG-main` | MIT | 作为可替换知识图谱运行时；保留原 LICENSE |
| MediaCrawler | `market-intel_agent/MediaCrawler-main` | NON-COMMERCIAL LEARNING LICENSE 1.1 | 仅作为显式开启的本地学习/研究适配器；不得直接用于商业抓取或大规模抓取 |
| GPT Researcher | `researcher_agent/gpt-researcher-main` | 源码包内 LICENSE 为 Apache-2.0；`pyproject.toml` 元数据存在 MIT 标注差异 | 不修改上游；按源码包 LICENSE 与 NOTICE 要求从严处理 |

商业化前必须完成两项工作：取得 MediaCrawler 权利人的商业书面授权，或替换为具有合适商业许可/官方数据授权的采集实现；同时由法务复核全部第三方依赖及平台数据使用条款。

