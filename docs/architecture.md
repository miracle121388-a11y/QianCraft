# QianCraft 统一架构

## 产品边界

QianCraft 0.10.0 是“双库驱动的自动文创设计系统”，不是通用搜索器、营销官网或自动量产发布器。默认产品面只呈现两座持续维护的材料库、每日设计结果和运行状态；评分与工作流在用户检查或修改某个结果时才逐层出现。LightRAG、MediaCrawler、GPT Researcher 与 XYFlow 继续作为隔离的高级研究能力，主路径由 QianCraft 自有 Studio Engine、调度器、Tool API 和结果界面控制。

```text
公开文化来源 ──culture_watch──> 待审核候选 ──人工字段核验──┐
                                                              ▼
                                         在地文化库（22 记录 / 32 来源）
                                                              │
                                                              ├──────────┐
                                                              │          │
授权平台采集 ──market_refresh──> 归一化历史/实时证据 ──> 产品形态库     │
                                         （10 形态 / 378 历史样本）      │
                                                              │          ▼
                                                              └─> StudioEngine
                                                                    ├─> 220 个组合评分
                                                                    ├─> 来源/样本/渲染器门
                                                                    ├─> 每日最多 Top 3
                                                                    ├─> 自由组合
                                                                    └─> 版本化 1440×960 PNG
                                                                              │
                                        ┌─────────────────────────────────────┼──────────────────┐
                                        ▼                                     ▼                  ▼
                              今日设计 / 全部设计                      设计详情与谱系          运行中心
                                                                              │
                                                                              ▼
                                                            五阶段结果工作流编辑器（V2+）

高级研究分支：LightRAG + MediaCrawler + GPT Researcher + Design Agent
                                └─> 原 9 节点 Workbench（/workflow）
```

Studio 主链直接生成带评分、来源、版本、SHA-256 和生产边界的结构概念板；高级研究链仍可越过 Designer Handoff 形成 DesignPackage、首样尺寸、BOM、装配、质检和展示海报。两条链都在 `production_release` 前停止。所有尺寸、公差与材料都是报价/首样假设，不是开模图或量产工程定稿；社区授权、工程验证、产品合规与商业发布仍需后续人工关口。

## 目录职责

```text
QianCraft/
├── app/
│   ├── adapters/              # 上游隔离层；不向产品层泄漏各项目内部对象
│   ├── strategist/            # 唯一策划师、证据锁和固定任务提示
│   ├── designer/              # 设计选案、制造拆解、Markdown 与海报排版
│   ├── collection.py          # 持久化文化巡检、候选队列与市场增量调度器
│   ├── studio.py              # 双库读取、组合评分、PNG 生成、版本与每日调度器
│   ├── workbench.py           # 7 类节点、工作区 JSON、版本与运行语义
│   ├── tool_api.py            # Studio、采集和旧 Workbench 的统一 HTTP API
│   ├── config.py              # 模式、路径、凭证、隔离运行时配置
│   ├── pipeline.py            # 并行取证、顺序策划、原子化输出
│   └── schemas.py             # 跨模块唯一数据契约
├── data/
│   ├── culture/               # 文化记录、来源和 LightRAG 持久化图
│   ├── market/                # 经核验基线、raw 原始抓取与 derived 派生证据
│   ├── design/assets/         # 原创生成式产品主视觉，不存馆藏参考像素
│   ├── benchmark/             # 可迁移案例，不直接等同于设计答案
│   ├── demo_cache/            # 明确标注的回退结果
│   ├── runtime/               # 被忽略的采集、Studio 设计和 Workbench 持久运行态
│   ├── workbench/             # 随仓库发布的旧工作台基线与生成视觉资产
│   └── outputs/               # 策略、交接、设计包、海报与运行清单
├── docs/                      # 架构、图谱、测试和下一阶段产品方向
├── scripts/                   # 命令行、环境探针与运行态快照/恢复入口
├── tests/                     # 契约、证据、安全、恢复、降级和输出测试
├── web/                       # 结果优先 Studio、双库、设计编辑、运行中心与旧 Workbench
├── deploy/                    # Nginx 鉴权/反代与 Zeabur 进程编排
├── Dockerfile                # Vinext + Python + Nginx 单服务生产镜像
├── flow/xyflow-main/          # 节点画布源码审计边界与原许可证
├── local_culture/             # 未改名的 LightRAG 上游源码与原许可证
├── market-intel_agent/        # 未改名的 MediaCrawler 上游源码与原许可证
└── researcher_agent/          # 未改名的 GPT Researcher 上游源码与原许可证
```

保留外部源码目录是许可证、供应链审计和未来升级所需的来源边界。品牌入口、业务命名、提示词、节点类型、状态机、数据结构、知识图谱和输出格式都属于根目录的 QianCraft 自有层。

## 结果优先 Studio

`app/studio.py` 的 `StudioEngine` 是主产品链的事实处理层。它只读取正式文化图谱和产品形态榜，生成完整笛卡尔组合并公开计算 `combo-score-v1`：文化证据 25%、形态热度 25%、品类兼容 25%、转译空间 15%、边界安全 10%。文化来源少于 2、没有可转译元素、形态样本为 0 或没有显式渲染器的组合直接淘汰。每日选择器再执行文化与形态去重；不足 3 个时输出更少，不调用通用兜底。

`StudioStore` 把排程、状态、事件、批次、设计版本和 PNG 写到 `data/runtime/tool_workspace/studio/`。每日批次先完整生成全部文件，再一次性写入设计索引；明确重跑会把旧批次标为 `superseded`，而不是删除。人工编辑始终产生新版本并保留前一版本摘要。`StudioScheduler` 使用 `Asia/Shanghai` 时区、持久化每日时间和启动补跑；健康接口检查实际线程、心跳与开关。

前端的一级路由为 `/`、`/libraries/culture`、`/libraries/forms`、`/create`、`/designs` 和 `/operations`。结果详情 `/designs/{id}` 展示 PNG、来源、评分与谱系；只有 `/designs/{id}/edit` 才展开文化、形态、融合、视觉和生产前验证五阶段。前端不保存事实，也不重算分数。

主要 Studio 接口：

| 接口 | 作用 |
|---|---|
| `GET /api/studio/overview` | 今日设计、两库真实计数和两个调度器状态 |
| `GET /api/studio/libraries/culture` | 已核验文化记录、来源和转译边界 |
| `GET /api/studio/libraries/forms` | 产品形态、样本、平台覆盖和代表原记录 |
| `GET /api/studio/combinations` | 可复现组合分数与门槛 |
| `POST /api/studio/combinations` | 自由组合并实际写入设计与 PNG |
| `GET/PUT /api/studio/designs/{id}` | 读取设计或生成下一版本 |
| `POST /api/studio/designs/{id}/regenerate` | 显式生成下一版本 |
| `GET/PUT/POST /api/studio/automation/*` | 状态、事件、排程和立即重跑 |

## 高级 Creative Intelligence Workbench

Workbench 现在位于 `/workflow`。桌面继续使用命令栏、工具轨、按需 Dock、可缩放/平移的空间画布和 Inspector；它承担深入研究和原七阶段决策，不再是默认首页。画布支持空白区直接平移、节点拖动、键盘移动和 Flow Map 直达。每张节点卡的“查看展示页”和双击动作会进入 `/nodes/{nodeId}?workspace={workspaceId}`；详情页按文化、市场、量分、任务书、视觉、概念与海报采用不同信息结构。前端不导入 Python 模块，所有事实读取、编辑保存与节点运行都经过 `app/tool_api.py` 的 HTTP API；密钥只留在服务端。

人工决策工作台覆盖文化选材、市场范围、评分与候选、设计意图、视觉方向、方案比较和海报呈现七个阶段。`guided` 系统建议与 `manual` 人工配置分开标识；系统原分、事实记录和引用保持只读，人工只保存 ID、权重、取舍和设计意图。保存后建立 `DecisionProfile` 新版本，并把任务书及视觉、概念、海报统一标记为 `stale`。完整字段与失效语义见 [`human_decision_workflow.md`](human_decision_workflow.md)。

视觉层采用自托管 `Noto Sans SC Variable` 正文与 `Noto Serif SC Variable` 标题，把界面文字收敛到 11–17px 的共享阶梯；默认画布缩放为 0.82，节点聚焦为 0.82–1.05。该比例让首屏优先读清当前策略与任务书，而不是把九节点同时缩成不可读缩略图。调研依据、令牌与响应式验收见 [`typography_system.md`](typography_system.md)。

默认工作区含 9 个节点实例、覆盖且只允许 7 种业务类型：`CultureGraphNode`、`MarketRadarNode`、`StrategyNode`、`DesignBriefNode`、`VisualGenerationNode`、`ConceptNode` 与 `PosterBoardNode`。三个 `ConceptNode` 分别代表 A/B/C；节点状态限定为 `idle / running / success / warning / error / cached / stale`。

工作区 JSON 位于 `data/workbench/workspaces/`，当前契约为 `schema_version: 1.1`，持久化 `nodes / edges / viewport / selected_node_id / selected_concept_id / brief_version / decision_profile / decision_output / metadata`。任务书保存会递增版本并只把可达下游标为 `stale`；不会自动执行、自动花费 API 或反向改写事实。New、Save、Load、Rename 与人工决策都经过同一校验器，连线端点、节点类型、状态或决策 ID 不合法时拒绝写盘。

## 持续采集控制面

`app/collection.py` 在 Tool API 进程内维护两条持久化通道。`culture_watch` 轮换巡检已登记文化来源，使用 HTTP 条件请求与内容哈希识别变化，只把同域相关文章写入候选队列；请求前及每次重定向后都会拒绝本机、私网、链路本地、云元数据、保留地址和解析到这些地址的域名。正式图谱仍要求人工完成字段级证据映射。`market_refresh` 先检查实时开关、MediaCrawler 和四平台授权，条件齐备才启动现有严格研究任务，且只接受 `live_verified`。调度配置、心跳、事件、候选和来源指纹写入 `data/runtime/tool_workspace/collection/`，不会覆盖仓库文化/市场基线。

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

生产环境采用一个容器：Nginx 在平台注入的端口统一处理 Basic Auth、API 单 IP 限流、HSTS/CSP/Permissions-Policy 等安全头，把 `/api`、`/assets` 转到回环地址的 Tool API，把其他请求转到回环地址的 Vinext；`/healthz` 单独免鉴权并转发真实 `/api/health`。启动脚本监控 Tool API、Vinext 与 Nginx，任一子进程退出就让容器失败；调度线程死亡或心跳超过 45 秒时健康 API 返回 503，Docker HEALTHCHECK 也失败，由已配置的平台重启策略恢复。`/app/data/runtime` 是唯一运行态持久卷，镜像内文化/市场证据只作为基线读取；`scripts/runtime_snapshot.py` 可创建自校验 ZIP、拒绝危险路径并原子恢复/保留回滚目录。该结构能在单副本持续调度，但不是分布式队列；多 API 副本前需增加唯一领导者，生产备份仍需复制到独立存储。部署细节见 [`deployment_zeabur.md`](deployment_zeabur.md)。

## 运行和降级

| 模式 | LightRAG | MediaCrawler | Strategist | Design / Poster |
|---|---|---|---|---|
| `demo` | 读取结构化图谱，不启动上游 | 公开核验缓存，`login_state` 如实记录 | 证据规则基线 | Design Agent 本地运行；无主视觉时海报几何回退为 `cache` |
| `auto` | 尝试真实本地图运行 | 仅在显式开启且具备 Cookie/QR/CDP 授权时抓取 | 尝试 GPT Researcher + DeepSeek，允许明确回退 | Design Agent 本地运行；原创主视觉存在时海报为 `live` |
| `live` | 外部运行失败即报错 | 未授权时保留缓存；授权抓取失败写明原因 | 模型失败即报错 | 同一证据锁与渲染契约；不因模式放宽文化或量产门禁 |

每个组件都返回 `live`、`cache` 或 `unavailable` 状态；四个市场平台还在 RunManifest 的 `market_platforms` 下独立记录 `authorized|missing|expired`、登录/搜索是否成功和样本量。某一路失败不会阻断其他平台。缓存不会被写成实时数据，未披露的互动指标不会被推算。

市场 Adapter 仍只有一个：它按 `xhs / dy / bili / wb` 依次隔离调用同一 MediaCrawler 运行时，将平台字段归一化为 MarketPost，然后在平台内部计算百分位热度，并按产品形态汇总 Top 10 / Top 5。详细公式见 [`market_intelligence.md`](market_intelligence.md)。

## 证据锁

策划师只能提出机会假设，不能覆盖 Culture DNA、Trend DNA 和 Benchmark Case。模型产出的每个 Opportunity Signal 必须同时包含一个现存 `Cxxx` 文化证据和一个现存 `Mxxx` 市场证据；不存在的编号、单边证据和不符合数据契约的项目会被拒绝。随后用本地基线补足至少八条机会。当前正式文件的 `generated_opportunities_accepted=0`，因此当前 8 条全部是证据规则基线，不得写成模型新生成。

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
- 主项目统一使用 Conda `qiancraft`；MediaCrawler 使用独立 Conda 环境并由 `MEDIACRAWLER_PYTHON` 指向解释器，避免其固定依赖版本污染主运行时。
- MediaCrawler 当前许可证只允许非商业学习/研究；商业化必须取得授权或替换数据采集实现。
- 祭祀、丧葬、祖源、支系身份、完整服饰构图、秘密知识和具体传承人作品进入概念设计前必须再次获得相应社区确认。

## Design Agent 接口与下一阶段边界

`data/outputs/designer_handoff.json` 仍是策划到设计之间唯一机器事实源；Design Agent 消费后生成 `design_specification.json`、同源 Markdown、`poster_render_request.json`、`design_poster.png` 和 `design_render_manifest.json`。具体字段、运行命令和工厂门禁见 [`design_agent.md`](design_agent.md)。

下一阶段应基于当前单一概念开展社区共审、用户测试、工厂 DFM 与材料/结构首样；通过后才能形成工程图、成本与模具方案、供应链确认、适用标准测试和商业授权。当前海报是完整的展示与沟通资产，不是可直接投产的最终 SKU 或商用版权结论。
