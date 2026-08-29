# QianCraft 统一架构

## 产品边界

QianCraft 是贵州非遗文创的“证据到概念设计系统”，不是通用搜索器，也不是自动量产发布器。它把文化检索、市场采集、策略研究与节点画布收敛在一套自有接口后面：LightRAG 负责本地知识图谱运行，MediaCrawler 只负责合规授权数据的采集，GPT Researcher 只负责基于给定上下文形成策略，XYFlow 只提供画布运行时；QianCraft 自有 Design Agent 和 Workbench 定义业务节点、证据状态、编辑语义与设计交付。

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
                                                                                     │
                                                                                     ▼
                                                              QianCraft Creative Intelligence Workbench
                                                               ├─> 7 类业务节点 / 9 个默认实例
                                                               ├─> 7 阶段人工决策 / 版本化 DecisionProfile
                                                               ├─> Inspector / 版本 / stale 传播
                                                               └─> Workspace JSON / 可编辑海报 PNG
```

流水线现在越过 Designer Handoff，形成一个选定方向的概念造型、首样尺寸、BOM、图案应用、装配、质检和展示海报；它在 `production_release` 前停止。所有尺寸、公差与材料都是报价/首样假设，不是开模图或量产工程定稿；社区授权、工程验证、产品合规与商业发布仍需后续人工关口。

## 目录职责

```text
QianCraft/
├── app/
│   ├── adapters/              # 上游隔离层；不向产品层泄漏各项目内部对象
│   ├── strategist/            # 唯一策划师、证据锁和固定任务提示
│   ├── designer/              # 设计选案、制造拆解、Markdown 与海报排版
│   ├── collection.py          # 持久化文化巡检、候选队列与市场增量调度器
│   ├── workbench.py           # 7 类节点、工作区 JSON、版本与运行语义
│   ├── config.py              # 模式、路径、凭证、隔离运行时配置
│   ├── pipeline.py            # 并行取证、顺序策划、原子化输出
│   └── schemas.py             # 跨模块唯一数据契约
├── data/
│   ├── culture/               # 文化记录、来源和 LightRAG 持久化图
│   ├── market/                # 经核验基线、raw 原始抓取与 derived 派生证据
│   ├── design/assets/         # 原创生成式产品主视觉，不存馆藏参考像素
│   ├── benchmark/             # 可迁移案例，不直接等同于设计答案
│   ├── demo_cache/            # 明确标注的回退结果
│   ├── workbench/             # 画布工作区与生成视觉资产
│   └── outputs/               # 策略、交接、设计包、海报与运行清单
├── docs/                      # 架构、图谱、测试和下一阶段产品方向
├── scripts/                   # 唯一命令行入口与环境探针
├── tests/                     # 契约、证据、降级和输出测试
├── web/                       # 黑白工具工作台、知识星图、采集控制面与 9 个节点详情页
├── deploy/                    # Nginx 鉴权/反代与 Zeabur 进程编排
├── Dockerfile                # Vinext + Python + Nginx 单服务生产镜像
├── flow/xyflow-main/          # 节点画布源码审计边界与原许可证
├── local_culture/             # 未改名的 LightRAG 上游源码与原许可证
├── market-intel_agent/        # 未改名的 MediaCrawler 上游源码与原许可证
└── researcher_agent/          # 未改名的 GPT Researcher 上游源码与原许可证
```

保留外部源码目录是许可证、供应链审计和未来升级所需的来源边界。品牌入口、业务命名、提示词、节点类型、状态机、数据结构、知识图谱和输出格式都属于根目录的 QianCraft 自有层。

## Creative Intelligence Workbench

Workbench 桌面使用命令栏、工具轨、按需 Dock、可缩放/平移的空间画布和 Inspector；移动端把外周面板变为可逆覆盖层，不把桌面三栏机械缩小。画布支持空白区直接平移、节点拖动、键盘移动和 Flow Map 直达。每张节点卡的“查看展示页”和双击动作会进入 `/nodes/{nodeId}?workspace={workspaceId}`；详情页按文化、市场、量分、任务书、视觉、概念与海报采用不同信息结构，同时保留独立运行、从此处运行、保存、导出和相邻节点跳转。文化页以自定义 SVG 星图呈现 22 条记录、32 个来源和分类引力点，支持搜索聚焦、节点选择、桌面滚轮/拖动、键盘平移，以及触屏显式操作模式下的单指平移和双指缩放；默认触屏手势仍允许页面纵向滚动。前端不导入 Python 模块，所有事实读取、编辑保存与节点运行都经过 `app/tool_api.py` 的 HTTP API；API 地址可由 `NEXT_PUBLIC_QIANCRAFT_API_URL` 配置，但密钥只留在服务端。

人工决策工作台覆盖文化选材、市场范围、评分与候选、设计意图、视觉方向、方案比较和海报呈现七个阶段。`guided` 系统建议与 `manual` 人工配置分开标识；系统原分、事实记录和引用保持只读，人工只保存 ID、权重、取舍和设计意图。保存后建立 `DecisionProfile` 新版本，并把任务书及视觉、概念、海报统一标记为 `stale`。完整字段与失效语义见 [`human_decision_workflow.md`](human_decision_workflow.md)。

视觉层采用自托管 `Noto Sans SC Variable` 正文与 `Noto Serif SC Variable` 标题，把界面文字收敛到 11–17px 的共享阶梯；默认画布缩放为 0.82，节点聚焦为 0.82–1.05。该比例让首屏优先读清当前策略与任务书，而不是把九节点同时缩成不可读缩略图。调研依据、令牌与响应式验收见 [`typography_system.md`](typography_system.md)。

默认工作区含 9 个节点实例、覆盖且只允许 7 种业务类型：`CultureGraphNode`、`MarketRadarNode`、`StrategyNode`、`DesignBriefNode`、`VisualGenerationNode`、`ConceptNode` 与 `PosterBoardNode`。三个 `ConceptNode` 分别代表 A/B/C；节点状态限定为 `idle / running / success / warning / error / cached / stale`。

工作区 JSON 位于 `data/workbench/workspaces/`，当前契约为 `schema_version: 1.1`，持久化 `nodes / edges / viewport / selected_node_id / selected_concept_id / brief_version / decision_profile / decision_output / metadata`。任务书保存会递增版本并只把可达下游标为 `stale`；不会自动执行、自动花费 API 或反向改写事实。New、Save、Load、Rename 与人工决策都经过同一校验器，连线端点、节点类型、状态或决策 ID 不合法时拒绝写盘。

## 持续采集控制面

`app/collection.py` 在 Tool API 进程内维护两条持久化通道。`culture_watch` 轮换巡检已登记文化来源，使用 HTTP 条件请求与内容哈希识别变化，只把同域相关文章写入候选队列；正式图谱仍要求人工完成字段级证据映射。`market_refresh` 先检查实时开关、MediaCrawler 和四平台授权，条件齐备才启动现有严格研究任务，且只接受 `live_verified`。调度配置、心跳、事件、候选和来源指纹写入 `data/runtime/tool_workspace/collection/`，不会覆盖仓库文化/市场基线。

前端每 12 秒读取控制面；请求失败立即显示连接中断并禁用写操作，心跳超过 45 秒也视为离线。文化批次必须本轮所有来源成功才是 `healthy`，部分失败为 `degraded` 且连续失败不清零。市场历史证据先于折叠运维台展示，避免把 378 条历史快照与新一轮授权状态混在一起。完整运行条件、状态和 API 见 [`continuous_collection.md`](continuous_collection.md)。

主要接口如下：

| 接口 | 作用 |
|---|---|
| `GET /api/workbench/bootstrap` | 一次取得工作区、22 条文化摘要、四平台状态、Top 10、人工决策目录与图像服务状态 |
| `GET /api/collection/status` | 调度心跳、两条通道、文化真实计数、候选计数和市场预检 |
| `GET /api/collection/events`、`GET /api/collection/candidates` | 持久化运行审计与文化候选队列 |
| `PUT /api/collection/schedule`、`POST /api/collection/run` | 暂停/恢复、修改间隔或立即排队；不绕过真实性门 |
| `GET/PUT /api/workbench/workspaces/{id}` | 读取或原子保存完整画布 |
| `POST /api/workbench/workspaces` | 从贵州苗绣默认链路创建新工作区 |
| `POST .../{id}/decisions` | 校验并保存完整 DecisionProfile，计算人工排序并传播下游 stale |
| `GET .../{id}/nodes/{node_id}/detail` | 返回节点专用结构、上下游关系、完整引用对象与缺失引用审计 |
| `POST .../{id}/brief` | 保存版本化 Design Brief 并传播 stale |
| `POST .../{id}/active-concept` | 切换 A/B/C 当前方向并标记海报待刷新 |
| `POST .../{id}/nodes/{node_id}/run` | 读取当前事实源刷新节点；视觉节点仅在真实 provider 就绪时生成 |

图像适配器只接受独立的 `IMAGE_PROVIDER / IMAGE_API_KEY / IMAGE_BASE_URL / IMAGE_MODEL`。缺项时 Visual Generation Node 为 `warning`，内置 A/B/C 项目资产仍可作为 `success` 概念证据展示，但不会被说成当次 API 新生成。默认工作区会从版本化文件恢复 B/C 及其 SHA-256；可编辑海报由浏览器 Canvas 按标题、文案、板块显示与顺序实时导出 1800 × 2400 PNG，页脚始终保留概念/首样边界。

生产环境采用一个容器：Nginx 在平台注入的端口统一处理 Basic Auth 和安全响应头，把 `/api`、`/assets` 转到回环地址的 Tool API，把其他请求转到回环地址的 Vinext；`/healthz` 单独免鉴权并转发真实 `/api/health`。启动脚本监控 Tool API、Vinext 与 Nginx，任一子进程退出就让容器失败；调度线程死亡或心跳超过 45 秒时健康 API 返回 503，Docker HEALTHCHECK 也失败，由已配置的平台重启策略恢复。`/app/data/runtime` 是唯一运行态持久卷，镜像内文化/市场证据只作为基线读取。该结构能在单副本持续调度，但不是分布式队列；多 API 副本前需增加唯一领导者。部署细节见 [`deployment_zeabur.md`](deployment_zeabur.md)。

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
