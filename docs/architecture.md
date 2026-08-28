# QianCraft 统一架构

## 产品边界

QianCraft 是贵州非遗文创的“证据到概念设计系统”，不是通用搜索器，也不是自动量产发布器。它把三个上游能力收敛在一套自有接口后面：LightRAG 负责本地知识图谱运行，MediaCrawler 只负责合规授权数据的采集，GPT Researcher 只负责基于给定上下文形成策略；QianCraft 自有 Design Agent 再把 Designer Handoff 转成一个可展示、可供报价和首样讨论的概念设计包。

```text
data/culture/knowledge_graph.json
          │
          ▼
LightRAGAdapter ──> CultureDNA + VisualReferencePack ─────────┐
                                                              │
verified market evidence ─────────────────────────────────────┤
          │                                                   ├─> Strategist
authorized MediaCrawler/xhs+dy+bili+wb (optional)              │      ├─> 机会六维加权 - 文化风险
          └─> 统一MarketPost ─> 平台内热度 ─> 产品形态榜 ───────┘      ├─> LightRAG 二次核验
                                                                      └─> Top 3 DesignerHandoff
                                                                                   │
                                                                                   ▼
                                                                         DesignAgent
                                                                           ├─> DesignPackage
                                                                           ├─> 工厂首样拆解
                                                                           └─> PosterRenderRequest
                                                                                     │
                                                           原创产品主视觉（可选）────┤
                                                                                     ▼
                                                                         精确文字海报排版器
                                                                                     │
                                                                                     ▼
                                                                          DesignPoster + Manifest
```

流水线现在越过 Designer Handoff，形成一个选定方向的概念造型、首样尺寸、BOM、图案应用、装配、质检和展示海报；它在 `production_release` 前停止。所有尺寸、公差与材料都是报价/首样假设，不是开模图或量产工程定稿；社区授权、工程验证、产品合规与商业发布仍需后续人工关口。

## 目录职责

```text
QianCraft/
├── app/
│   ├── adapters/              # 上游隔离层；不向产品层泄漏各项目内部对象
│   ├── strategist/            # 唯一策划师、证据锁和固定任务提示
│   ├── designer/              # 设计选案、制造拆解、Markdown 与海报排版
│   ├── config.py              # 模式、路径、凭证、隔离运行时配置
│   ├── pipeline.py            # 并行取证、顺序策划、原子化输出
│   └── schemas.py             # 跨模块唯一数据契约
├── data/
│   ├── culture/               # 文化记录、来源和 LightRAG 持久化图
│   ├── market/                # 经核验基线、raw 原始抓取与 derived 派生证据
│   ├── design/assets/         # 原创生成式产品主视觉，不存馆藏参考像素
│   ├── benchmark/             # 可迁移案例，不直接等同于设计答案
│   ├── demo_cache/            # 明确标注的回退结果
│   └── outputs/               # 策略、交接、设计包、海报与运行清单
├── docs/                      # 架构、图谱、测试和下一阶段产品方向
├── scripts/                   # 唯一命令行入口与环境探针
├── tests/                     # 契约、证据、降级和输出测试
├── local_culture/             # 未改名的 LightRAG 上游源码与原许可证
├── market-intel_agent/        # 未改名的 MediaCrawler 上游源码与原许可证
└── researcher_agent/          # 未改名的 GPT Researcher 上游源码与原许可证
```

保留上游目录不是产品“拼装痕迹”，而是许可证、供应链审计和未来升级所需的来源边界。品牌入口、业务命名、提示词、数据结构、知识图谱和输出格式都属于根目录的 QianCraft 自有层。

## 运行和降级

| 模式 | LightRAG | MediaCrawler | Strategist | Design / Poster |
|---|---|---|---|---|
| `demo` | 读取结构化图谱，不启动上游 | 公开核验缓存，`login_state` 如实记录 | 证据规则基线 | Design Agent 本地运行；无主视觉时海报几何回退为 `cache` |
| `auto` | 尝试真实本地图运行 | 仅在显式开启且具备 Cookie/QR/CDP 授权时抓取 | 尝试 GPT Researcher + DeepSeek，允许明确回退 | Design Agent 本地运行；原创主视觉存在时海报为 `live` |
| `live` | 外部运行失败即报错 | 未授权时保留缓存；授权抓取失败写明原因 | 模型失败即报错 | 同一证据锁与渲染契约；不因模式放宽文化或量产门禁 |

每个组件都返回 `live`、`cache` 或 `unavailable` 状态；四个市场平台还在 RunManifest 的 `market_platforms` 下独立记录 `authorized|missing|expired`、登录/搜索是否成功和样本量。某一路失败不会阻断其他平台。缓存不会被写成实时数据，未披露的互动指标不会被推算。

市场 Adapter 仍只有一个：它按 `xhs / dy / bili / wb` 依次隔离调用同一 MediaCrawler 运行时，将平台字段归一化为 MarketPost，然后在平台内部计算百分位热度，并按产品形态汇总 Top 10 / Top 5。详细公式见 [`market_intelligence.md`](market_intelligence.md)。

## 证据锁

策划师只能提出机会假设，不能覆盖 Culture DNA、Trend DNA 和 Benchmark Case。模型产出的每个 Opportunity Signal 必须同时包含一个现存 `Cxxx` 文化证据和一个现存 `Mxxx` 市场证据；不存在的编号、单边证据和不符合数据契约的项目会被拒绝。随后用本地基线补足至少八条机会。

每条机会再计算 `culture_fit / market_pull / novelty / visual_potential / social_shareability / product_feasibility / cultural_risk / overall_score`。正向权重为 20/20/20/15/15/10，文化风险按 20% 扣分。排序同时考虑综合分、证据完整度和风险。

高分候选会重新进入现有 `LightRAGAdapter`，检查文化证据、地域与支系、禁忌、高敏感叙事、现代转译和跨支系专属工艺词。结果只能是 `verified`、`warning` 或 `rejected`；警告扣分，拒绝项综合分归零且不能进入 Top 3。模型把剑河“锡绣/迷宫式核心图案”串到花溪等情况会被硬拒绝。

## 视觉参考层

`data/culture/visual_references.json` 保存 12 条官方/权威馆藏参考，覆盖花溪、剑河、松桃、雷山、蝴蝶、鸟、龙、服装、针法纹理及银/锡材料关系。每条都保留地域、工艺、文化语境、页面 URL、图片直链、证据编号和权利说明。版权未明确开放的图像统一为 `reference_only`，不下载、不复制为商品图稿。

Pattern Primitive 只抽取网格、排列、主次、叙事节奏和材料层次；Color Palette 只采用来源文字与颜色关系，未测色时禁止生成 HEX。

## Design Agent 证据锁与渲染

`designer_handoff.json` 是 Design Agent 的机器输入。代理先用 Pydantic 验证文件，再记录完整 SHA-256；它只能从输入 Top 3 选择主机会，且最终 `DesignPackage` 必须同时保留现存 `Cxxx` 与 `Mxxx` 证据。当前选择策略优先 `verified`、具体产品形态和较低文化敏感度，并把跨地域集合方向缩窄到单一地域首样。

`DesignPackage` 固定包含文化元素及转译规则、成品形态与风格、至少三项首样尺寸、至少五项 BOM、图案应用、至少五步装配与质检、包装、安全合规、工厂待确认问题、文化审核门和工程审核门。契约硬性禁止 `reference_images_used_as_pixels=true` 和 `mass_production_ready=true`。

海报采用两层渲染：可选的原创生成式资产只提供无文字的产品与爆炸视图；标题、尺寸、BOM、工艺与边界由 Pillow 本地精确排版。最终 `DesignRenderManifest` 同时记录输入资产与海报 SHA-256、画布、引擎以及是否使用 reference-only 像素。

## 安全与合规

- API Key 只从被忽略的 `.env` 或本地 `api.txt` 读取，日志、异常和最终输出都会掩码。
- MediaCrawler Cookie 不进入命令行参数，而通过隔离子进程环境传递并在进程启动后立即移除。
- 二维码/CDP 只通过 `scripts/probe_market_platforms.py --authorize`（旧小红书脚本继续兼容）由用户显式启动；普通 demo/live 策略运行不会擅自弹出登录窗口。
- 四平台使用同一 23 词全集，正式默认各取 6 词；每平台约 50–150 条、总量约 200–600 条，单平台硬上限 150。规范化快照、上游原始文件与派生榜单分层保存。
- MediaCrawler 使用独立虚拟环境，避免其固定依赖版本污染主运行时。
- MediaCrawler 当前许可证只允许非商业学习/研究；商业化必须取得授权或替换数据采集实现。
- 祭祀、丧葬、祖源、支系身份、完整服饰构图、秘密知识和具体传承人作品进入概念设计前必须再次获得相应社区确认。

## Design Agent 接口与下一阶段边界

`data/outputs/designer_handoff.json` 仍是策划到设计之间唯一机器事实源；Design Agent 消费后生成 `design_specification.json`、同源 Markdown、`poster_render_request.json`、`design_poster.png` 和 `design_render_manifest.json`。具体字段、运行命令和工厂门禁见 [`design_agent.md`](design_agent.md)。

下一阶段应基于当前单一概念开展社区共审、用户测试、工厂 DFM 与材料/结构首样；通过后才能形成工程图、成本与模具方案、供应链确认、适用标准测试和商业授权。当前海报是完整的展示与沟通资产，不是可直接投产的最终 SKU 或商用版权结论。
