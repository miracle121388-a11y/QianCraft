# QianCraft 工作流程与持续更新记录

> 文档性质：项目级唯一工作流说明、当前状态快照与追加式更新台账
> 当前版本：0.10.0
> 最后维护：2026-09-01
> 维护状态：强制持续维护

## 0. 维护契约

本文件不是一次性交付说明。以后每一次对 QianCraft 的有效更新，都必须在同一轮工作中同步维护本文件，然后才能视为完成。

以下变化均触发维护：

- 新增、删除、移动或重命名文件和目录。
- 修改运行流程、模块职责、数据契约、提示词或输出格式。
- 新增或修订文化记录、市场信号、来源、对标案例及文化边界。
- 修改模型、API、运行模式、环境变量、依赖、安装方式或安全策略。
- 修复缺陷、改变降级逻辑、调整证据校验或测试口径。
- 完成新的实机运行、测试、数据审计或产品方向判断。

每次维护必须完成四件事：

1. 更新顶部“最后维护”日期；若形成稳定里程碑，同时更新版本号。
2. 修改受影响的“当前状态”“工作流程”“目录职责”“命令”或“边界”章节。
3. 在“更新日志”最上方追加一条记录，写清变更、原因、验证、边界和涉及文件。
4. 运行与改动风险相称的验证，并把真实结果写入日志；不得把未执行的检查写成通过。

历史日志只追加、不回写、不删除。发现历史记录有误时，新建一条“勘误”说明原记录及修正原因。

## 1. 当前状态快照

| 项目 | 当前状态 |
|---|---|
| 产品名称 | QianCraft｜双库驱动的自动文创设计工具 |
| 产品阶段 | 概念视觉与工厂首样简报；在量产发布前停止 |
| 产品工作台 | 本地 0.10.0 主入口由 `app/studio.py` + `app/tool_api.py` + `web/app/studio-*` 驱动：首页展示两库真实计数、每日最多 Top 3 与自动化；一级入口为文化库、形态库、自由组合、全部设计和运行中心；设计详情显示 PNG、来源、评分、批次、SHA 与可下载历史版本，只有编辑结果时才出现文化/形态/融合/视觉/生产前验证五阶段。旧 9 节点/10 连线 Workbench 保留在 `/workflow`。默认本地站点 `http://localhost:3000/`，API 为 `127.0.0.1:8787`；本轮因 3000 被其他服务占用而实际运行在 `http://localhost:3001/`。受保护线上仍为已验收 0.9.2，0.10.0 发布结果待本轮实际部署后更新 |
| GitHub 展示 | 项目 README 包含原创横版 SVG 首屏、真实状态徽章、在线实例、成果海报、A/B/C 三方向视觉、Workbench 快速开始、Mermaid 架构、可信边界、路线图与许可证说明 |
| 小红书发布包 | `docs/social/xiaohongshu/2026-08-29/` 提供可直接复制的中文标题/正文/话题、8 张 1080×1440 轮播 PNG、可复现 HTML 排版源与素材/口径说明。当前传播核心为“让贵州非遗不只被看见，也被真正理解；让传统有出处、创新有根，并以被尊重的方式走进当代生活”。封面场景使用项目原创概念图作为参考重新生成，并明确标注概念视觉；全部页面区分历史快照、推断、概念样与量产/授权/合规边界，没有使用 `reference_only` 馆藏像素 |
| 默认主题 | 贵州苗绣 |
| 默认目标市场 | 18–30 岁年轻消费者 |
| 文化知识图谱 | 22 条已核验结构化记录、32 条文化/伦理/法律/馆藏视觉来源；来源巡检与正式知识分层，当前另有 1 条真实 `pending_review` 候选，候选须人工核验后才能进入结构化图谱 |
| 苗绣检索 | 同时保留花溪挑花、剑河锡绣、松桃苗绣与雷山工艺差异 |
| 视觉参考包 | 12 条权威参考、5 个 Pattern Primitive、3 组无伪造 HEX 的文字色彩关系；默认 `reference_only` |
| 市场研究层 | 12 条结构化市场信号、12 条公开可追溯来源 |
| 市场状态 | 当前 Windows 基线保留 378 条历史真实快照（xhs 115、dy 14、bili 101、wb 148）与 12 条不进榜公开核验记录。0.9.0 的市场刷新通道已具备持久调度、退避、立即运行与状态审计，但当前 `MEDIACRAWLER_LIVE_ENABLED=false` 且四平台没有已连接授权浏览器，所以真实状态为 `blocked`；没有创建假任务、没有改写 378 条历史证据，也没有把“已排期”写成实时产出 |
| 产品形态榜 | `product_form_hotness.json` 已由 378 条历史真实平台快照恢复：Top 10 为冰箱贴、徽章、盲盒、包挂、伴手礼、潮玩、香氛、挂件、首饰、毛绒；Top 5 为前五项。该榜只代表有限历史样本，不代表当前全平台实时趋势 |
| Studio 组合与设计 | 正式双库形成 22 × 10 = 220 个候选；文化证据分公开为来源充分度 50% + 地域具体度 20% + 可转译字段完整度 30%，`combo-score-v1` 再按文化证据/形态热度/品类兼容/转译空间/边界安全 25/25/25/15/10 计算。少于 2 条可解析来源、存在缺失来源、无可转译元素、形态无可点击代表原记录、样本为 0 或无显式渲染器的组合直接淘汰；每日最多选择 3 个文化与形态均不重复的结果。10 种形态均有明确本地结构渲染器，每次实际生成 1440×960 PNG、版本、批次与 SHA-256；编辑生成 V2+ 时保留旧稿及其组合、文案、分数、时间与下载地址，不冒充图像模型或量产图 |
| Studio 自动化 | `StudioScheduler` 与采集调度器在同一 Tool API 内独立运行；默认 `Asia/Shanghai` 07:00，排程/状态/事件/设计/PNG 持久化到 `data/runtime/tool_workspace/studio/`。启动发现当天无设计时补跑；普通同日轮次幂等，明确立即重跑才生成新批次并标记旧批次 superseded。`/api/health` 只有两个调度线程与心跳都正常才返回 200 |
| 对标案例 | 8 条 |
| LightRAG 实机图 | 612 个实体、697 条关系；“贵州苗绣”节点查询通过 |
| 策划输出 | 当前正式输出来自实机运行 `20260828T060200Z-e44240e3`。该轮实际调用 GPT Researcher / DeepSeek，但清单中的 `generated_opportunities_accepted=0`：模型建议没有通过证据契约，当前 8 条 Opportunity Signals 全部来自可复现的本地证据规则基线，再经六维评分与 LightRAG 二次核验；Top 3 为 OPP-006、OPP-002、OPP-004。历史日志中“DeepSeek 实际生成当前 8 条”的说法不准确，本轮以追加勘误修正 |
| Design Agent | 自动模式从 Top 3 中选择 OPP-006，缩窄为“针格模块｜花溪挑花互动冰箱贴（概念样）”；工具支持人工从 8 条机会中选择 1–3 条、指定主机会、编辑交接/产品字段并生成带输入 SHA 的独立运行；没有匹配生成器时直接报错，不套用通用兜底模板 |
| 工厂首样拆解 | 5 项原型尺寸、5 项 BOM、1 组原创网格应用、6 步装配、6 项质检、3 个文化门、3 个工程门与 5 个工厂问题；不宣称量产就绪 |
| 设计海报 | 1800 × 2400；原创生成式成品/爆炸主视觉 + 本地精确中文排版；未使用 `reference_only` 馆藏像素 |
| 0.9.1 提交前复验 | 独立运行 `20260829T144536Z-2e6f3e5b`：`culture_knowledge=live`、`market_research=cache`、`strategist=cache`、`design_agent=live`、`poster_renderer=live`；消费提交随附的 378 条派生平台证据，生成 8 条机会、Top 3、DesignPackage、13 项产物与 1800×2400 海报，全部清单路径为仓库相对路径且文件存在。正式仓库产物随后从既有真实 DeepSeek `DesignerHandoff` 重跑设计/海报阶段，保留历史策划证据并更新 BOM 5 项标题、摘要与可迁移清单路径 |
| Workbench Workspace | 默认 `guizhou-miao-demo` 以仓库基线初始化，后续写入 `data/runtime/workbench/`；Workspace Schema 1.1 保存 9 个节点、10 条连线、视口、当前 Concept、任务书、A/B/C、`DecisionProfile`、机器/人工并列的 `decision_output`、研究任务和设计运行引用。New / Save / Load / Rename / Save decisions 使用同一 JSON 校验与原子写入；研究晋级时保留仍有效的人工 ID，对消失的机会/品类只做带审计记录的补齐；源证据与运行态分离，页面操作不会覆盖仓库基线 |
| 图像生成适配 | `ImageGenerationAdapter` 保留 OpenAI-compatible `/images/generations` 与 Qwen Image 3.0 同步契约；此前 Qwen `qwen-image-3.0-pro` 三次同步实机生成及其否决/未选版本是历史可审计证据。当前本机与 Zeabur 均未配置独立图像 provider，因此 Regenerate / Generate More 会保留已有 A/B/C 并显示 warning，不会把旧资产写成新成功。批准的 `.impeccable/mocks/tonal-focus-review.png`（SHA-256 `131cd5be…ffeb`）只作为 C2 电脑端非字面比例、色块与聚焦参考；它不是产品数据资产或逐像素事实源 |
| API | 0.10.0 新增 Studio overview、两库、组合、设计 CRUD/重生成、自动排程与事件接口，以及 `/assets/studio/{designId}/v{version}.png`。健康响应增加应用版本并同时检查采集与每日设计调度器。现有严格研究、采集、Workbench 和资产接口保持兼容。独立图像 provider 与四平台授权状态未改变；Studio PNG 使用本地显式结构渲染器，不依赖或冒充该 provider |
| 线上发布 | 受保护实例 `https://qiancraft-studio-2026.zeabur.app` 当前已验收版本仍为 0.9.2、部署 `6a95b5a29ed7d65609e27bf6`。0.10.0 必须在 GitHub CI、实际 Zeabur 部署、健康版本、两个调度器、两库、今日设计、PNG 读取与匿名门禁均验证后才能改写为已上线；本行当前不提前声称完成 |
| MediaCrawler | 独立 Python 3.13 环境按上游 requirements 完整安装，探针实际导入 `bili,dy,ks,tieba,wb,xhs,zhihu`。市场通道默认每 240 分钟预检一次，只有实时开关、运行时与用户授权全部成立才创建严格任务；当前实时开关关闭且四平台无已连接授权，本轮没有登录或抓取，378 条历史快照继续诚实保持 cache |
| 自动测试 | 0.10.0 本地 Python 83/83、Web 单测 5/5；新增 6 项 Studio 后端回归和一项六一级路由真实 API/axe 门。Windows desktop UI 门当前定义为 32 项，必须由本轮 GitHub Actions 实际执行后再记录远端结果，不能沿用 0.9.2 的 77/31 数字 |
| 静态检查 | 0.10.0 本地 Ruff、`uv lock --check`、Web typecheck、ESLint、Vinext production build、完整 `pnpm audit`、Python `pip-audit --local`、`bash -n deploy/start-zeabur.sh`、`git diff --check` 与依赖单版本检查均通过；本轮改动文件长 `sk-` 模式为 0 命中。远端跨平台结果仍以本轮 GitHub Actions 为准 |
| 运行态恢复 | `scripts/runtime_snapshot.py` 对 `data/runtime` 生成带 SHA-256 清单的 ZIP，发布前自校验；恢复前校验路径、大小、文件数和摘要，要求服务已停止及显式确认，并保留时间戳回滚目录。本轮发布前 0.9.1 运行态以 tar + 外部 SHA-256 校验，发布后 0.9.2 在 Zeabur 实际生成含 5 个文件/57,741 字节的 ZIP 快照并通过服务器和本地双重校验；两份均已复制到持久卷之外的权限受控目录。它不等同于定时异地备份、自动保留策略或已完成恢复演练 |
| 凭证检查 | 本机 LLM 凭证只存在于被 Git 忽略的 `.env`，站点 Basic Auth 与服务器 LLM 凭证只存在于 Zeabur Secret；当前没有独立图像凭证。本轮对 QianCraft 自有受跟踪文件执行安全独立长 `sk-` 扫描为 0 命中。全仓扫描另检出 2 个既有、未改动的 extracted-upstream 示例字面量，分别位于 LightRAG 的完整 Docker Compose 示例和非官方示例脚本；它们不在本轮改动内且按上游边界不改写。扫描没有读取 `.env` 或 Secret 值，文档与最终交接不复述任何字面量、Cookie、API Key 或授权会话值 |

当前正式产物：

- [`data/outputs/pre_design_strategy.json`](data/outputs/pre_design_strategy.json)
- [`data/outputs/pre_design_strategy.md`](data/outputs/pre_design_strategy.md)
- [`data/outputs/visual_reference_pack.json`](data/outputs/visual_reference_pack.json)
- [`data/outputs/visual_reference_pack.md`](data/outputs/visual_reference_pack.md)
- [`data/outputs/designer_handoff.json`](data/outputs/designer_handoff.json)（下一阶段机器唯一事实源）
- [`data/outputs/designer_handoff.md`](data/outputs/designer_handoff.md)
- [`data/market/derived/product_form_hotness.json`](data/market/derived/product_form_hotness.json)
- [`data/outputs/design_specification.json`](data/outputs/design_specification.json)（概念设计与工厂首样机器事实源）
- [`data/outputs/design_specification.md`](data/outputs/design_specification.md)
- [`data/outputs/poster_render_request.json`](data/outputs/poster_render_request.json)
- [`data/outputs/design_poster.png`](data/outputs/design_poster.png)
- [`data/outputs/design_render_manifest.json`](data/outputs/design_render_manifest.json)
- [`data/outputs/run_manifest.json`](data/outputs/run_manifest.json)

## 2. 端到端工作流程

0.10.0 的默认产品主链先维护材料、再产出结果，工作流只在用户干预设计时出现：

```text
Culture Scheduler ──> 候选审核 ──> 22 条正式文化内容 ─┐
                                                         ├─> StudioEngine：220 个组合
Market Scheduler ──> 授权/归一化 ──> 10 种产品形态 ───┘         ├─ 25/25/25/15/10 评分
                                                                  ├─ 来源/样本/渲染器门
                                                                  └─ 文化与形态去重
                                                                            │
                                            ┌───────────────────────────────┴────────────────────────┐
                                            ▼                                                        ▼
                                每日北京时间 07:00 最多 Top 3                              用户自由组合 1–3 × 1–3
                                            └───────────────────────────────┬────────────────────────┘
                                                                            ▼
                                                1440×960 PNG + 评分 + 来源 + 批次 + SHA-256
                                                                            │
                                                ┌───────────────────────────┴──────────────────────┐
                                                ▼                                                  ▼
                                      默认只审阅结果和依据                              看中结果后进入五阶段编辑
                                                                                         └─> 保存新版本 V2+
```

`StudioScheduler` 与采集调度器都由 Tool API 启动，状态写入持久卷。启动补跑、同日幂等、明确重跑新批次和无合格组合时的空结果都由后端控制；前端不硬编码两库数量、分数或设计。当前结构概念板使用显式本地形态渲染器，不依赖独立图像 provider，也不声称是生成式商品效果图或量产工程图。

以下是仍保留在 `/workflow` 的高级研究与 DesignPackage 流程：

```text
用户请求 DemoRequest
        │
        ├──> Settings：解析 .env、运行模式、上游路径与安全开关
        │
        ├──> LightRAGAdapter
        │       ├── 读取贵州结构化图谱
        │       ├── 检索主题及苗绣支系记录
        │       ├── 生成证据锁定的 CultureDNA
        │       ├── 生成 Visual Reference Pack（馆藏参考/结构原语/颜色关系）
        │       └── live 时建立/重载 LightRAG 本地图并探测节点
        │
        ├──> MediaCrawlerAdapter
        │       ├── 读取公开核验市场基线
        │       ├── live 且用户明确授权时依次走 xhs/dy/bili/wb Cookie / QR / CDP
        │       ├── 四平台共用关键词池；每平台约50–150条，总量约200–600条
        │       ├── 统一字段、清洗、去重、反垃圾与产品形态识别
        │       ├── 平台内百分位热度 → 跨平台产品形态 Top 10 / Top 5
        │       └── 形成 TrendDNA + 四路独立状态；失败平台明确为 cache/unavailable
        │
        ├──> BenchmarkCase：载入可迁移案例
        │
        └──> Strategist（系统中唯一策划师）
                ├── GPT Researcher 只接收锁定后的本地上下文
                ├── DeepSeek 提出设计前机会假设
                ├── 拒绝不存在、单边或不合约的证据引用
                ├── 本地基线保证至少 8 条机会
                ├── 六维正向评分、文化风险扣分与证据完整度排序
                ├── 高分候选重新 Query LightRAG
                ├── warning 扣分、rejected 排除
                └── 只把 Top 3 输出为 DesignerHandoff
                              │
                              ├── PreDesignStrategy JSON/Markdown
                              ├── Visual Reference Pack JSON/Markdown
                              ├── Designer Handoff JSON/Markdown
                              │
                              └──> Design Agent
                                      ├── 从文件重载 DesignerHandoff 并记录 SHA-256
                                      ├── 选择 verified、具体且较低敏感的单一主方向
                                      ├── 生成文化转译、成品形态、尺寸、BOM、图案、装配与质检
                                      ├── 写 DesignPackage JSON/Markdown + PosterRenderRequest
                                      └──> Poster Renderer
                                              ├── 可选原创生成式成品/爆炸主视觉
                                              ├── 本地精确中文、尺寸、BOM 与工艺排版
                                              ├── 写 1800×2400 PNG + RenderManifest
                                              └── 更新 RunManifest（五组件、四平台状态与13个正式路径）
```

Culture DNA 与 Trend DNA 可并行取得；Strategist 必须在两者、Visual Reference Pack 和 Benchmark Case 完整后运行；Design Agent 必须在 Designer Handoff 原子落盘后重新从文件读取。生成模型不得反向改写文化事实、视觉权利状态或市场原始记录，也不得把参考图像像素带入概念视觉。

0.9.0 在正式流水线之前增加可持续素材入口，但不绕过事实与授权门：

```text
Tool API 启动 / 容器持续运行
        └→ Collection Scheduler（持久配置、心跳、退避、事件）
                ├→ culture_watch（默认 360 分钟）
                │       ├→ 条件请求 / 指纹去重 / 同域候选发现
                │       ├→ 全部来源成功 = healthy；部分失败 = degraded
                │       └→ pending_review → 人工审核 → 结构化图谱（不自动晋级）
                └→ market_refresh（默认 240 分钟）
                        ├→ 实时开关、MediaCrawler 运行时与四平台授权预检
                        ├→ 条件不齐 = blocked + 事件 + 下次调度
                        └→ 条件齐备才创建严格研究任务；仅 live_verified 晋级
```

所谓 7×24 是“调度与状态持续运行”，前提是 Tool API/容器单副本常驻、`data/runtime` 持久卷、进程重启策略、网络和平台授权持续有效；它不是无条件保证每轮都有新素材，也不是跨副本分布式队列。文化候选必须人工核验，市场平台未授权时必须诚实阻断。

高级 Creative Intelligence Workbench 在上述正式流水线之外增加一层可审计交互，不改写事实源：

```text
真实文件 / RunManifest / DesignPackage
       │
       └→ Tool API：Bootstrap + Workspace JSON + 节点详情 + 节点动作
                  │
                  ├→ Strict Research Job：202 后台任务 → 持久化 job.json → 前端轮询/刷新续接
                  │          ├→ 每轮独立 outputs/raw/derived，不读取 demo fallback
                  │          └→ 文化 + 策划 + xhs/dy/bili/wb 全部 live 才原子晋级
                  ├→ 持续采集控制：真实心跳 / 调度暂停 / 立即运行 / 事件 / 候选审核 / 授权阻断
                  ├→ 证据中心：22 条正式文化记录 / 32 来源 / 待核验候选 / 四平台 378 历史快照 / Top 10
                  ├→ React Flow：Culture + Market → Strategy → Brief → Visual → A/B/C → Poster
                  ├→ Culture Constellation：黑色关系画布、搜索/选点、桌面拖动与移动显式触摸模式
                  ├→ Inspector：概览 / 输入 / 配置 / 结果 / 证据 / 记录 / 操作
                  ├→ Node Detail：9 个独立展示页 + 引用解析 + 相邻节点 + 独立运行/保存/导出
                  ├→ Human Decision Studio：文化选择 → 平台/品类 → 机会 → 权重/风险 → 任务书 → 视觉/概念 → 海报
                  │          ├→ Guided 保留系统推荐；Manual 保存人的选择与版本
                  │          └→ 系统分与人工重排分并列，事实、来源与原始互动保持只读
                  ├→ Brief 保存：版本 +1，仅将可达下游标记 stale
                  ├→ Brief 运行：从当前人工选择重建 Handoff → DesignPackage → 结构海报落盘
                  ├→ Concept：Edit / Duplicate / Regenerate / Use / Generate More
                  └→ Poster：标题、文案、图片来源、板块显隐/顺序 → 服务端 1800×2400 PNG
```

工作台前端不直接导入 Python，只通过 HTTP API 读取事实、保存工作区和运行节点。`/api/workbench/workspaces/{workspaceId}/nodes/{nodeId}/detail` 按节点类型返回专用内容与解析后的引用对象；文化页展示关系与 22 条记录，市场页展示 378 条历史快照派生榜和代表原记录，策略页展示机会及六维量分，设计页继续贯通任务书、视觉方向、文化转译、BOM 与海报。`POST /api/workbench/workspaces/{workspaceId}/decisions` 校验并保存 `DecisionProfile`，按选中范围重算人工排序、立即刷新 Culture/Market/Strategy 节点，并把 Brief 之后的依赖节点标为 stale；保存选择本身不会静默调用模型。每个节点详情通过 `workspace` 与 `decision` 查询参数深链到对应编辑阶段。节点动作使用异步 `fetch` 并即时显示 `running`；图像服务或其他调用失败时变为 `error/warning`，不会锁死界面。

“严格实时研究”先检查 LLM、MediaCrawler 授权/运行时与 LightRAG，然后以 202 后台任务执行；任务状态和结果写入独立 `job.json`，刷新或离开页面后仍可续接。研究流水线只运行到 `designer_handoff.json`，不让下游设计异常吞掉真实平台状态；即使预检通过，运行后也必须确认文化、市场、策划和四个平台全部为 `live`，否则该轮只保留失败审计，不晋级、不覆盖旧证据。晋级后前端才依次运行 Brief/Design Agent、Visual/Concept 与 Poster；没有真实生成器或图像 provider 的步骤保持 warning/error。

## 3. 运行模式与降级

| 模式 | 文化层 | 市场层 | 策划层 | 设计与海报 | 使用场景 |
|---|---|---|---|---|---|
| `demo` | 结构化图谱 | 公开核验基线；四平台真实快照存在时只标 `cache` | 本地证据规则 | Design Agent 本地运行；无主视觉时几何海报标 `cache` | 离线验收、开发和稳定演示 |
| `auto` | 尝试 LightRAG live，允许明确回退 | 仅在显式开关及授权登录态齐备时逐平台抓取；无 raw 时读取提交随附 `derived/latest.json` | 尝试 GPT Researcher + DeepSeek，允许明确回退 | 原创主视觉存在时海报标 `live` | 默认实机运行；显式 `--mode auto` 始终覆盖环境中的 demo/live 默认值 |
| `live` | 上游失败报错 | 未授权时仍使用合规缓存；授权失败写清状态 | 模型失败报错 | 保持同一证据锁与量产前门禁 | 严格集成测试 |
| `tool-strict` | 必须 live | 四平台必须全部 live，任何 cache/unavailable 均失败 | 必须 live 且模型建议通过契约；先在研究边界落盘 | 研究晋级后由工作台继续运行；无生成器或 provider 即 warning/error | Web 工具中的“严格实时研究” |

组件统一状态为 `live|cache|unavailable`，登录状态为 `authorized|missing|expired`，不能互相冒充。当前项目没有使用 mock 数据。

## 4. 目录和职责

| 路径 | 职责 | 更新注意事项 |
|---|---|---|
| `app/config.py` | 模式、路径、API、Cookie 与安全配置 | 新增环境变量时同步 `.env.example`、README 和本文件 |
| `app/schemas.py` | 全系统唯一数据契约 | 字段改变必须补迁移、测试和输出兼容说明 |
| `app/adapters/` | 隔离文化、市场、研究与图像生成运行时 | 产品层不得依赖外部实现内部对象；凭证不得出现在命令行和日志 |
| `app/strategist/` | 唯一策划师、固定任务提示与证据锁 | 不允许生成最终设计；文化/市场事实不可被模型覆盖 |
| `app/designer/` | Design Agent、设计包 Markdown 与精确文字海报排版 | 只消费已落盘交接；不得使用 reference-only 像素或宣称量产就绪 |
| `app/pipeline.py` | 端到端编排、原子输出和运行清单 | 新步骤必须说明顺序、失败策略与状态字段 |
| `app/collection.py` | 文化来源巡检、市场严格任务预检、持久调度/心跳/退避、候选/指纹/事件、公共页面抓取与人工审核门 | 只有全部已探测文化来源成功才是 healthy，部分失败必须 degraded；候选不得自动写入正式图谱；市场缺开关、运行时或授权必须 blocked，不创建假任务。公共 URL 的输入、DNS 解析结果和每次重定向都必须拒绝本机、私网、链路本地与内部域名；TCP 连接钉住已校验公网地址且不使用环境代理，防止 SSRF 与 DNS rebinding |
| `app/tool_api.py` | 工具 API、真实计数、采集状态/事件/候选/配置/动作、真实健康心跳、分页来源查询、节点专用详情、七阶段人工决策写入、严格预检、202 后台研究任务/轮询/中断恢复、设计运行与资产路由 | 本地或容器内只绑定回环地址并由受保护代理转发；不得向前端返回凭证；job 异常必须脱敏并持久化；历史、当前、live、cache、系统推荐和人工选择必须分开标注；客户端断开不得把 BrokenPipe 误写为第二次响应 |
| `app/workbench.py` | 7 类节点注册、默认贵州苗绣链路、Workspace Schema 1.1 校验/兼容迁移/原子保存、DecisionProfile 校验/人工排序/下游 stale、研究晋级、Concept 动作、真实 Poster 渲染、文化/市场/馆藏/平台记录引用目录与详情组装 | 只有隔离运行中的文化/市场/策划和四平台全部 live 才可晋级；人工选择只在新结果中 ID 消失时带审计补齐。节点类型、状态、连线、引用、Concept 与资产路径均须服务端校验；馆藏 `reference_only` 不得改写为可用像素 |
| `data/culture/` | 文化图谱、视觉参考和 LightRAG 存储 | 事实先写结构化图谱；视觉图像权利与来源分开记录 |
| `data/market/` | 核验基线、`raw/` 原始抓取、`derived/` 派生证据 | 未披露互动数保持为 0；原始与派生不可混写 |
| `data/design/assets/` | 原创生成式成品/爆炸主视觉 | 不保存馆藏参考图像；每项正式使用资产必须进入渲染摘要 |
| `data/benchmark/` | 对标案例 | 案例只提供方法启发，不直接变成产品答案 |
| `data/demo_cache/` | 明确标注的稳定回退 | 缓存更新时间和生成模式必须可追踪 |
| `data/outputs/` | 最新13项正式结果 | JSON 是机器契约；Markdown 从同一对象渲染；海报与输入摘要可复核；项目内清单路径使用仓库相对路径，移动工作区后不依赖旧机器盘符 |
| `data/tool_workspace/` | 仓库随附的旧版工具基线与可审计示例 | 作为只读初始化/历史证据；新运行不再写入该目录 |
| `data/workbench/` | 仓库随附的 Workspace Schema 1.1 与 A/B/C 概念视觉基线 | 作为首次启动模板；浏览器写入不得覆盖该目录 |
| `data/runtime/workbench/` | 实际 Workspace、研究晋级产物、DesignPackage、概念版本与海报 | 被 Git 忽略并在容器挂载持久卷；每个工作区/运行使用受校验目录，JSON 原子写入，不保存 Base64 或凭证 |
| `data/runtime/tool_workspace/` | 严格研究 `job.json`、每轮隔离 raw/derived/outputs、旧版工具设计运行与 `collection/` 的调度配置/状态/事件/候选/指纹 | 后台任务、失败审计和设计运行都保留独立 ID；容器必须挂载持久卷；非正式平台探针另写隔离目录，不覆盖 canonical 证据 |
| `scripts/` | 正式流水线、工具 API/一键启动、环境探针、四平台 Smoke Test、显式授权入口与 `runtime_snapshot.py` 运行态快照/校验/恢复工具 | 登录和工具启动命令变化同步维护本文件“标准命令”；恢复必须停服务、显式确认并保留回滚目录，快照须复制到独立存储 |
| `tests/` | 数据、证据、采集调度/候选门、SSRF、部署安全、运行态恢复、路径可迁移与端到端契约 | 修复缺陷时优先增加回归测试；授权缺失、部分来源失败、重启恢复、显式模式、私网 URL/重定向和随附缓存必须有明确断言 |
| `docs/` | 专题说明与阶段性产品材料，包含人工决策契约、排版令牌、画布比例、视觉验收基线和 `frontend_quality_workflow.md` 自动/人工前端门 | 本文件保留总览，专题细节链接到 docs；自动 axe 与像素基线不得写成完整无障碍认证 |
| `docs/social/` | 面向外部渠道的经核验内容包、发布顺序、确定性排版源和渠道专用视觉 | 只使用项目自有或已获许可素材；数据状态、文化来源、概念/量产边界与生成图身份必须在正文和图片中保持一致；实际发布由用户在目标平台预览确认 |
| `docs/assets/` | GitHub README 等文档专用视觉资产 | 只放项目自有或已获许可素材；保持相对路径与无障碍文本 |
| `PRODUCT.md`、`DESIGN.md` | 产品意图、核心工作流与长期设计宪法 | 产品角色、信息优先级、视觉令牌或交互原则改变时同步维护；不得让文档与实际 CSS/组件漂移 |
| `.impeccable/` | 机器可读设计契约、界面简报、成品截图与资产来源记录 | Detector 每轮最多运行一次；截图只作审阅证据，不把外部参考资产混入正式产品素材 |
| `web/` | Tonal Focus Review 电脑端工作台、五阶段导航、60px command、72px tool rail、210px bottom Dock、330px right Inspector、七阶段 Human Decision Studio、可拖动/缩放 React Flow 画布、深色文化知识星图例外、持续采集控制面、9 个动态详情页、证据台账、API Client、Workspace UI、Canvas PNG 导出、自托管中文排版系统与 Playwright/axe/视觉回归门 | C2 使用固定暖矿物/雾蓝/灰绿/暖陶/浅石/低饱和蓝令牌；禁止大面积纯白、渐变、玻璃、光晕与装饰色。页面不得把历史/cache/排期写成 live；市场历史证据优先于运维控制；断线必须使旧在线状态失效；拖拽必须有点击/键盘等价路径。当前 C2 只承诺电脑端，mobile/tablet 沿用既有代码但未纳入本轮适配与验收 |
| `web/tests/ui/` | 工作台与九个详情路由的 Playwright 质量门、axe、C2 计算样式/几何、工作台/星图/弹层核心交互、采集断线与恢复、forced-colors 与视觉基线 | macOS 本轮 30 passed / 1 个 Windows 像素门按平台跳过；功能断言必须跨平台，像素基线固定 Windows Chromium 并由 CI 执行。测试必须从用户可见语义定位，不得通过隐藏控件、禁用规则或无审阅更新快照来消除失败 |
| `Dockerfile`、`deploy/` | Zeabur 单容器构建、Nginx 鉴权/反代、限流/安全响应头、Vinext、Tool API 与采集调度进程编排、真实健康检查 | Basic Auth 哈希只在启动时生成；`/healthz` 代理真实 API 心跳，线程死亡/心跳超过 45 秒返回 503，镜像 HEALTHCHECK 随之失败；API 使用共享限流区，响应包含 HSTS/CSP/Permissions-Policy；启动脚本任一 API/Web/Nginx 子进程退出即失败；运行态必须写入持久卷，当前只支持单副本调度 |
| `.github/workflows/quality.yml` | Ubuntu/macOS/Windows Python 回归、Linux Ruff/锁/依赖审计、Windows Web 构建/依赖/Playwright 像素门 | 使用最小只读权限、并发取消和 Conda `qiancraft` 环境；CI 通过才可视为跨平台交付门完成 |
| 四个外部源码目录（含 `flow/xyflow-main/`） | 许可证审计和可替换运行时 | 不删除版权信息；非必要不直接修改；产品节点、状态和视觉留在 QianCraft 自有层 |

## 5. 数据与证据规则

### 5.1 文化图谱

- 每条 `CultureRecord` 必须有唯一 `culture_id`。
- 每条记录必须有 `source_refs`，每个事实字段通过 `field_sources` 指向来源。
- `field_sources` 中的编号必须是该记录 `source_refs` 的子集。
- 苗绣不是单一风格；地域、支系、材料和针法差异必须保留。
- 祖源、神话、仪式、丧葬、支系身份、完整服饰构图、秘密知识和具体传承人作品必须进入人工/社区复核队列。
- 大模型不得自动填补田野资料空白。

### 5.2 市场信号

- 每条信号必须链接一个现存 `Mxxx` 来源。
- 证据类型只允许 `social_signal`、`institutional_signal`、`media_signal`、`product_signal`。
- 没有来源披露时，点赞、收藏、评论和分享必须为 0。
- 销量、订单、金额和用户调查只按来源原文口径记录，不外推平台全量结论。
- `real_engagement_score` 只来自授权抓取的真实互动；`institutional_signal_score` 只表达机构证据；`derived_viral_score` 是项目内推导排序值，三者不可混称。
- xhs/dy/bili/wb 使用同一 23 词全集；正式默认取 6 词、每词一页，单平台保留 50–150 条为目标并硬限制最多 150 条，四平台总目标 200–600 条。
- 统一帖子保留 `platform/post_id/title/content/url/published_at/likes/favorites/comments/shares/views/product_form/search_keyword/retrieved_at`；平台缺失字段只能为 0 或空，不得推测。
- Platform Hot Score 只在同平台内对实际可用指标和近期性做百分位加权；不同平台绝对互动数不得直接横比。
- Cross-platform Hot Score = 60%覆盖平台平均热度 + 15%形态出现次数百分位 + 15%平台覆盖率 + 10%近期性；对外只称“跨平台市场热度与爆款潜力信号”。
- 产品形态榜只使用本次真实抓取或其历史真实快照，公开研究基线不进入榜单；最终最多 Top 10，`priority_product_forms` 最多 5 项。
- 规范化平台快照写 `data/market/raw/{xhs,dy,bili,wb}.jsonl`，上游原始文件写 `raw/_upstream/`，清洗/评分/榜单只写 `derived/`；RunManifest 必须记录实际路径与四平台独立状态。

### 5.3 策划机会

- 每个生成型 Opportunity Signal 必须同时引用至少一个 `Cxxx` 和一个 `Mxxx`。
- 引用必须存在于当次 Culture DNA、Trend DNA 或 Benchmark Case 的允许列表。
- 机会必须包含六项正向分、文化风险、综合分和原因；综合分按 20/20/20/15/15/10 加权后扣除 20% 文化风险。
- 高分候选必须通过 LightRAG 二次核验；`warning` 扣分，`rejected` 归零并排除，Top 3 才能进入 Designer Handoff。
- 证据编号合法不等于语义成立；地域否定语句不算来源主张，但把剑河“锡绣/迷宫式核心图案”等专属词串到花溪、松桃、雷山会被硬拒绝。
- 姜央、洪水、射日月、古歌、史诗等与祖源/祭祀同属高敏感叙事，缺少社区复核或禁用边界时警告或拒绝。
- 机会只描述值得探索的关系、品类空间与待验证问题，不输出最终造型、尺寸、SKU 或打样结论。

### 5.4 视觉参考

- Visual Reference Pack 每条必须记录 `visual_id`、地域、工艺、文化语境、来源页、图片直链、权利状态和不可直接复制项。
- 版权或商品化权利未明确开放时统一为 `reference_only`；页面可访问不等于可下载、训练、复制或商用。
- Pattern Primitive 只抽取结构、节奏、主次、叙事或材料关系，不矢量化完整传统纹样。
- 未做实物色卡测量时不得输出 HEX；颜色只能按权威来源文字和材料关系描述。

### 5.5 设计、制造拆解与海报

- 正式流水线使用 `designer_handoff.json`，工具人工流程使用每次独立落盘的 `designer_handoff_draft.json`；Design Agent 必须从文件重载 Pydantic 契约并记录 SHA-256，不得复用未落盘的内存旁路。
- 自动主机会必须来自系统 Top 3；工具人工模式可以从当前 8 条非 rejected 机会中选择 1–3 条并指定主机会，但证据编号、原始评分与核验状态保持锁定。`warning` 机会若被人工选入，必须在设计包中保留文化复核警告。
- Design Agent 只有在机会产品形态匹配已实现的毛绒/织物、模块收藏品或溯源档案生成器时才运行；没有匹配生成器时直接失败，不得套用通用“安全方案”冒充针对性设计。
- 多地域或多支系机会进入首样前必须缩窄到一个明确地域/工艺方向，不得在同一概念中拼接专属工艺与完整纹样。
- `DesignPackage` 必须同时保留输入白名单中的 `Cxxx` 与 `Mxxx`，并包含文化转译、首样尺寸、至少 5 项 BOM、图案应用、至少 5 步装配、至少 5 项质检、文化与工程审核门。
- `reference_images_used_as_pixels` 与 `mass_production_ready` 必须为 false。馆藏图片、传承人作品和未授权图像不得作为生成输入、贴图、描摹底图或训练素材。
- 生成式主视觉只负责无文字产品/爆炸资产；准确中文、尺寸、BOM、工艺和边界必须由本地排版器绘制。
- `DesignRenderManifest` 必须记录设计 ID、主视觉与海报路径及 SHA-256、画布、渲染引擎和 reference-only 像素声明。
- 当前产物只供展示、工厂报价和首样沟通。生产工程图、DFM、模具、成本、供应链、材料测试、适用标准、商业文化授权与下单均属于下一阶段。

### 5.6 Workbench、Concept 与可编辑 Poster

- 中央画布只允许 `CultureGraphNode / MarketRadarNode / StrategyNode / DesignBriefNode / VisualGenerationNode / ConceptNode / PosterBoardNode` 七类业务节点；默认三个 Concept 是同一类型的不同实例。
- 工作画布必须遵守直接操控契约：主键或单指拖动空白区域平移，`Shift + 拖动` 框选，滚轮/捏合缩放，节点拖动只移动节点；移动端主要画布控制和菜单命中区不得小于 44px。
- 文化/市场证据的拖拽创建必须同时提供可见点击按钮与键盘路径；React Flow 选择/移动提示必须使用当前中文产品语境，不能把拖拽当作进入画布的唯一方式。
- Culture Graph、Workspace 与 Human Decision Studio 等 modal 必须有可访问名称/描述、初始焦点、Tab 焦点圈、Escape 关闭和触发器焦点归还；可滚动详情必须能由键盘进入。
- `prefers-reduced-motion` 只去除动画旅行和连续运动，不得通过全局极短时长抹掉必要状态；`prefers-contrast` 与 Windows forced-colors 下必须保留可见焦点、选中态和状态形状。
- Workspace Schema 1.1 必须保存 nodes、edges、viewport、selected concept、node versions、workflow metadata、`metadata.decision_profile` 与 `metadata.decision_output`；不得把 Base64 图像写进 JSON。
- `DecisionProfile` 必须区分 `guided/manual`，并可保存文化记录、市场平台/产品形态、1–3 个机会、六维权重、文化风险扣分、设计意图、视觉参考/风格/尺寸、概念比较组/当前方向和海报主题/板块；所有 ID 必须来自服务端 `decisionCatalog`。
- 人工权重允许用任意正数表达相对偏好，服务端统一归一化后再算分；原始 `systemScore`、人工 `manualScore`、权重贡献与风险扣分必须并列保存，禁止覆盖系统量分或伪装为新的事实。
- 状态只允许 `idle / running / success / warning / error / cached / stale`。上游编辑只把依赖图中可达的下游标为 stale，不自动执行、不自动消费 API。
- 保存人工决策后，Culture/Market/Strategy 节点立即反映所选范围；Brief、Visual、Concept 与 Poster 标记 stale 并等待用户分别重跑。概念生成只消费比较组，当前采用方向必须属于比较组。
- Design Brief、Concept 文本、视觉参数与 Poster 内容可以编辑；文化事实、证据编号、市场原始互动与权利状态不可在 Inspector 或 Decision Studio 中改写。
- Concept 的 Edit、Duplicate、Regenerate、Use 与 Generate More 都必须保留版本或建立独立节点；图像 provider 缺失时明确 warning，不得把占位图或旧图标成新生成。
- Culture / Market / Strategy 的普通“运行”和“从此运行”必须调用同一个严格后台研究任务；不得仅重读静态 JSON 后把节点改成 success。研究任务返回 202、持久化任务号和可轮询状态，页面刷新必须能恢复正在执行的任务。
- 严格研究每轮使用独立 raw/derived/outputs；探针、失败轮次和正式结果不可互相覆盖。达到平台时限时只能保留已写盘且通过最低记录校验的真实部分结果，并明确说明停止继续翻页；没有有效记录时必须 unavailable。
- Brief 运行必须实际写出带输入 SHA 的 DesignerHandoff、DesignPackage、RenderManifest 与海报；Poster 运行必须重新渲染文件。旧资产可在新生成失败时继续展示，但 UI 必须标明“保留上次成功资产 · 本轮未生成”。
- Poster Board 第一版只做固定模板、标题/文案、当前 Concept 图片来源、板块显隐和简单顺序；导出 PNG 必须保留“概念/首样沟通、非量产定稿”边界。
- Web 只通过 `app/tool_api.py` 的 HTTP API 读取和写入；API 继续只绑定回环地址，浏览器端不得读取 `.env`、`api.txt` 或 Cookie。节点页返回 Decision Studio 时必须保留 workspace 和阶段深链，不得落回错误工作区。

## 6. 凭证、许可证与文化合规

- `api.txt` 与 `.env` 已被 `.gitignore` 排除；任何文档、输出、异常和日志不得回显密钥。
- `scripts/check_environment.py --install-api` 只把本地 API 配置写入被忽略的 `.env`。
- MediaCrawler Cookie 通过隔离子进程环境传递，启动后立即从环境中移除，不进入进程命令行。
- 二维码或 CDP 登录只能由用户显式运行 `scripts/probe_market_platforms.py --authorize`；旧 `authorize_xhs.py` 只作兼容。普通策略运行默认不弹出浏览器。
- CDP 优先连接用户自己的本机浏览器端口；项目不绕过验证码、风控、访问控制或平台登录机制。
- MediaCrawler 使用独立 Conda 环境，避免固定依赖版本污染 QianCraft 主环境；通过 `MEDIACRAWLER_PYTHON` 显式指定解释器。
- MediaCrawler 的上游许可证限制为非商业学习/研究。商业化前必须取得书面授权，或换成具备适当许可及平台授权的数据实现。
- XYFlow / React Flow 以 `@xyflow/react@12.11.5` 进入 Web 依赖，上传源码与 MIT LICENSE 保留在 `flow/xyflow-main/`；产品 UI 不需要展示供应链叙事，但仓库内归属和许可证不得删除。
- 上游许可证差异和处理方式以 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 为准。
- 文化转译遵循共同创作、明确署名、透明授权、公平收益和持续知情同意原则。

## 7. 标准环境与命令

### 7.1 主运行时

```bash
conda env create -f environment.yml
# 已存在环境时同步依赖
conda env update -n qiancraft -f environment.yml --prune
# 只有需要严格研究时才安装对应上游；仍在同一 Conda 环境内执行
conda run -n qiancraft python -m pip install -e "./local_culture/LightRAG-main"
conda run -n qiancraft python -m pip install -e "./researcher_agent/gpt-researcher-main"
```

### 7.2 MediaCrawler 隔离运行时

```bash
conda create -n qiancraft-mediacrawler python=3.13 pip -y
conda run -n qiancraft-mediacrawler python -m pip install -r market-intel_agent/MediaCrawler-main/requirements.txt
conda run -n qiancraft-mediacrawler python -c "import sys; print(sys.executable)"
```

把最后一条命令输出的绝对解释器路径写入被 Git 忽略的 `.env` 的 `MEDIACRAWLER_PYTHON`；不得提交该环境、Cookie 或授权会话。上游 `pyproject.toml` 当前使用不符合 PEP 621 校验的单数 `author` 字段，因此不做 editable install；QianCraft 直接调用源码入口。

### 7.3 本地工具工作台

```bash
# 首次安装前端依赖
cd web
pnpm install
pnpm exec playwright install chromium
cd ..

# 同时启动本地真实数据 API 与 Web 工作台
conda run --no-capture-output -n qiancraft python scripts/run_web_tool.py

# 或分开启动，便于调试
conda run --no-capture-output -n qiancraft python scripts/run_tool.py
cd web
pnpm dev

# Workbench 前端验收
pnpm test
pnpm typecheck
pnpm lint
pnpm test:ui
pnpm build
pnpm quality
pnpm start:local
```

当前 C2 电脑端验收使用 `pnpm exec playwright test --project=desktop-chromium`，由 `web/playwright.config.ts` 启动 Tool API，并在 1440×960 定义 32 项：新增一项循环验证 Studio 六个一级路由、真实 22/10/378 计数与 axe，旧 Windows 像素基线仍只由 Windows Chromium/CI 执行。本轮本地没有冒充执行该跨平台门，推送后以新的 GitHub Actions 结果为准。`pnpm test:ui` 仍保留历史 desktop/mobile 双项目入口，但只有获得对应响应式授权、完成实现并准备复验时才运行。详细口径见 [`docs/frontend_quality_workflow.md`](docs/frontend_quality_workflow.md)。

工作台默认为 `http://localhost:3000/`，本地 API 为 `http://127.0.0.1:8787/`；端口冲突时可由启动脚本显式改到 3001，本轮实际使用后者。前端只通过 HTTP 使用真实 Python 数据；Workspace、研究任务、采集调度/事件/候选、设计运行与生成资产写入被 Git 忽略的 `data/runtime/`，`data/workbench/` 和 `data/tool_workspace/` 仅作首次初始化/历史基线。Tool API 启动时同时启动持续采集与每日设计两个调度器；文化默认每 360 分钟巡检登记来源，市场默认每 240 分钟做严格授权预检，每日设计默认在 `Asia/Shanghai` 07:00 运行并在冷启动缺少当日产物时补跑。条件缺失时阻断，不走兜底；后台轮询、心跳、下次运行和连续失败在页面上保持可见。严格实时研究要求完整上游配置，运行中刷新页面从服务端任务号续接。

### 7.4 安装 API 与探针

```bash
conda run --no-capture-output -n qiancraft python scripts/check_environment.py --install-api --probe-api
conda run --no-capture-output -n qiancraft python scripts/check_environment.py --probe-mediacrawler
```

### 7.5 运行与验收

```bash
conda run --no-capture-output -n qiancraft python scripts/run_demo.py --mode demo
conda run --no-capture-output -n qiancraft python scripts/run_demo.py --mode auto
conda run --no-capture-output -n qiancraft python scripts/run_demo.py --mode live
# 接入项目内原创主视觉并运行完整链路
conda run --no-capture-output -n qiancraft python scripts/run_demo.py --mode auto --design-hero data/design/assets/huaxi_grid_magnet_hero_v1.png
# 只重跑 Designer Handoff 后的设计与海报，并同步运行清单
conda run --no-capture-output -n qiancraft python scripts/run_design_agent.py --hero-image data/design/assets/huaxi_grid_magnet_hero_v1.png --update-run-manifest
conda run --no-capture-output -n qiancraft python -m pytest
conda run --no-capture-output -n qiancraft ruff check .
conda run --no-capture-output -n qiancraft uv lock --check
conda run --no-capture-output -n qiancraft python -m pip_audit
pnpm --dir web audit --audit-level=high
```

网页“实时运行”会调用 `POST /api/research/run`；状态由 `GET /api/research/jobs/{jobId}` 返回。它是长任务，不应通过重复 POST 轮询。只有返回 `live_verified` 后，工作台才继续执行 Brief/Design Agent 与 Poster。

### 7.6 四平台探测与用户显式授权

```bash
# 无交互状态探针，不打开浏览器
conda run --no-capture-output -n qiancraft python scripts/probe_market_platforms.py

# 首次授权逐个平台执行，依次把 platform 改成 xhs、dy、bili、wb
conda run --no-capture-output -n qiancraft python scripts/probe_market_platforms.py --platform xhs --method cdp --authorize

# 四平台授权后统一复核正式小规模抓取
conda run --no-capture-output -n qiancraft python scripts/probe_market_platforms.py --platform all --method cdp --formal --authorize
```

可把 `cdp` 换成 `qrcode`；Cookie 模式使用四个独立环境变量。只有用户确认平台条款、上游许可和用途后才执行。单平台只有实际登录、搜索并保存至少 5 条带 ID 和互动字段的真实结果后才是 `live/authorized`；历史真实快照只能是 `cache`，没有快照则是 `unavailable`。

### 7.7 容器与 Zeabur 发布验收

```bash
# 本地存在 Docker 时可先构建同一生产镜像
docker build -t qiancraft:0.10.0 .

# Zeabur CLI 在已选择项目/环境/服务后上传精简发布目录
npx --yes zeabur@latest deploy --service-id <service-id> --environment-id <environment-id> --interactive=false

# 发布后同时验证免鉴权健康检查和受保护入口；认证值只从本机安全环境读取
curl --fail --silent --show-error https://qiancraft-studio-2026.zeabur.app/healthz
curl --silent --output /dev/null --write-out '%{http_code}\n' https://qiancraft-studio-2026.zeabur.app/
```

生产发布使用 `.dockerignore` 排除原始平台数据、上游源码、测试缓存与本地密钥；部署变量由 Zeabur Secret 管理，不使用 `variable list` 等可能回显值的命令。发布成功必须继续以认证请求检查 Bootstrap、九个节点详情、静态资源与至少一个独立节点动作，单看平台“RUNNING”状态不算验收完成。完整拓扑见 [`docs/deployment_zeabur.md`](docs/deployment_zeabur.md)。

### 7.8 运行态快照与恢复

```bash
# 快照写到持久卷外，并在发布前完成清单/摘要自校验
conda run --no-capture-output -n qiancraft python scripts/runtime_snapshot.py backup --output /safe-independent-storage/qiancraft-runtime.zip
conda run --no-capture-output -n qiancraft python scripts/runtime_snapshot.py verify /safe-independent-storage/qiancraft-runtime.zip

# 仅在 Tool API 已停止时恢复；命令会保留时间戳回滚目录
conda run --no-capture-output -n qiancraft python scripts/runtime_snapshot.py restore /safe-independent-storage/qiancraft-runtime.zip --confirm-service-stopped --confirm RESTORE_QIANCRAFT_RUNTIME
```

`/safe-independent-storage/` 是占位路径，必须替换为 Zeabur 持久卷之外、访问受控的真实存储。快照工具不是自动异地备份服务；发布前/后快照、复制、保留周期和恢复演练仍须由运维流程执行。

## 8. 每次更新的完成定义

一次更新只有在以下条件全部满足时才能交付：

- [ ] 改动符合用户授权范围，没有顺手扩大到无关系统。
- [ ] 相关数据契约、目录、配置和降级逻辑保持一致。
- [ ] 文化与市场事实都有来源，推断被明确标注。
- [ ] 没有删除或隐藏第三方许可证和版权信息。
- [ ] 凭证没有进入代码、数据、文档、日志或输出。
- [ ] 已运行与风险相称的测试、静态检查或实机探针。
- [ ] 依赖或运行时变化已运行 Python/Web 漏洞审计、锁文件和 peer 检查；推送后确认 GitHub Actions 跨平台门真实通过。
- [ ] 涉及公网输入或代理抓取时，已覆盖初始 URL、DNS 解析、DNS rebinding、环境代理和重定向的私网/本机拒绝；不得仅依赖字符串前缀。
- [ ] 涉及运行态格式、容器或上线时，已创建并校验持久卷快照，复制到独立存储，并记录恢复边界；未完成异地复制时不得写成生产备份已完成。
- [ ] 正式输出需要更新时，已生成新的 JSON、Markdown 和 RunManifest。
- [ ] 涉及 Design Agent 时，已核对交接 SHA-256、证据编号、量产状态、参考像素声明、海报尺寸与渲染摘要。
- [ ] 涉及 Workbench 时，已核对 7 类节点契约、9 个默认实例的详情页、引用解析/缺失审计、Workspace Schema 1.1 与旧数据兼容、DecisionProfile 版本/ID 白名单/权重归一化、系统分和人工分并列、节点阶段深链、下游 stale 传播、严格研究 202/轮询/刷新续接/全 live 晋级门、Brief 实际 DesignPackage、Concept 旧资产标识、Poster 实际渲染和真实 API 错误态。
- [ ] 涉及持续采集时，已核对持久配置/状态/事件/候选/指纹、真实心跳、下次运行、退避、API 重启 interrupted、文化全部成功与部分失败的 healthy/degraded 区分、候选人工晋级门、市场实时开关/运行时/四平台授权阻断，以及只有 `live_verified` 才覆盖正式证据；不得把排期、预检、历史快照或部分成功写成实时产出。
- [ ] 涉及 Studio 时，已核对两库数量来自实际文件、文化引用可解析、形态代表原记录可点击、评分公式/分项/样本窗公开、无证据或无渲染器时明确拒绝、每日 Top 3 去重、同日幂等/明确重跑 superseded、自由组合 1–3 × 1–3、编辑 V2+ 保留旧 PNG/谱系、生成资产 SHA，以及 `massProductionReady=false` 的生产边界。
- [ ] 涉及前端排版或交互时，已按用户授权范围运行目标 Playwright project，并核对 Tonal Focus Review 固定色值、60/72/210/330 电脑端几何、没有大面积纯白/渐变/玻璃/光晕/装饰色、黑色只作为真实关系画布例外、系统中文字体回退、画布可读比例、页面溢出、拖拽等价路径、知识星图、断线语义、可访问名称与焦点闭环。若范围包含 mobile/tablet，才另行补 44px、手势、抽屉、safe area、目标视口与真实设备门；未授权/未运行的范围不得写成通过。
- [ ] 涉及视觉基线时，已逐张人工查看获批目标项目的快照后再决定是否更新；desktop-only 任务只更新/验收 desktop，不运行会覆盖 mobile 的总更新命令。axe 与像素回归只作为门槛证据，不写成完整 WCAG 认证。
- [ ] 涉及上线时，已核对匿名鉴权、健康检查、认证后页面/API、持久卷目录、运行日志和部署域名；不能只依据平台状态声明完成。
- [ ] 本文件的当前状态、受影响章节和更新日志已经同步维护。
- [ ] 最终回复指出本文件的位置和本次新增日志。

## 9. 更新日志

### 2026-09-01｜0.10.0｜Studio 小字号对比度跨表面修正

变更：

- 把 Studio 专用次级文字从旧工作台的 `#626970` 调整为 `#565E65`；主色、表面、功能分区和旧 Workbench 令牌均保持不变。

原因：

- 第二次 0.10.0 GitHub Actions 运行 `33509679761` 中，Ubuntu/macOS/Windows Python 全部通过，Windows 旧 31 项门也全部通过；新增 Studio axe 用例发现 `#626970` 在 rail/shell/command 等浅色表面上的小字号对比度只有约 4.16–4.31:1。新值在 Studio 使用的最不利 selected 表面仍为约 4.59:1，在其他浅色表面为约 4.93–5.69:1。

验证：

- 失败仅为新增六路由门的 `color-contrast`，列出的导航、页眉、说明和设计标签都由同一 Studio 变量控制；其余 31/31 Windows 用例实际通过。修改后将重跑本地静态/构建门与新的完整 GitHub Actions。

边界：

- 本次修正不声称完整 WCAG 认证；axe 只覆盖自动可发现问题，真实屏幕阅读器和用户测试仍是正式无障碍验收的后续工作。

涉及文件：

- `web/app/studio.css`、`web/app/layout.tsx`
- `DESIGN.md`、`docs/frontend_quality_workflow.md`、`WORKFLOW.md`

### 2026-09-01｜0.10.0｜每日调度回归门消除跨平台竞态

变更：

- 调整每日调度器回归测试的完成条件：同时等待 3 个设计原子落盘和持久状态从 `running` 转为 `healthy`，再断言心跳与最终状态；不改变产品调度、生成顺序或成功口径。

原因：

- 首次 0.10.0 GitHub Actions 运行 `33509223628` 中，macOS/Windows Python 通过，Ubuntu 在 PNG 已落盘但状态文件尚未完成最后一次原子更新的毫秒窗口读取到 `running`，形成测试时序竞态。产品随后会正确进入 `healthy`，但测试不应把“文件出现”等同于整轮事务完成。

验证：

- 失败日志精确定位在 `test_scheduler_catches_up_today_and_keeps_a_fresh_heartbeat` 的最终状态断言；修复后将先在本地重复执行该用例与全套门，再以新的 GitHub Actions 跨平台结果为准。

边界：

- 本次不放宽业务断言：仍必须在 5 秒内同时满足 3 个当日设计、`healthy` 状态和新鲜心跳；若调度确实卡在 `running`，测试仍会失败。

涉及文件：

- `tests/test_studio.py`
- `WORKFLOW.md`

### 2026-09-01｜0.10.0｜双库驱动、结果优先的每日设计 Studio

变更：

- 把默认首页从中间工作流改为结果优先 Studio：一级展示今日设计、22 条在地文化、10 种产品形态/378 条历史样本、自动化状态；提供文化库、形态库、自由组合、全部设计、设计详情与运行中心，旧高级 Workbench 保留在 `/workflow`。
- 新增真实双库组合与设计引擎：220 个候选使用公开的文化证据分和 `combo-score-v1`，先经过来源、代表原记录、样本、转译字段和显式形态渲染器硬门，再每日选文化/形态均不重复的 Top 3；10 个形态渲染器实际写出 1440×960 PNG、批次、版本与 SHA-256。
- 新增 `StudioScheduler`：北京时间 07:00、启动补跑、同日幂等、明确立即重跑、旧批次 superseded、持久心跳/事件/排程；与采集调度器共同进入 `/api/health`。自由组合允许 1–3 条文化 × 1–3 个形态，编辑器允许替换内容/形态、改融合文稿与视觉参数并生成 V2+，旧稿及组合、分数、时间、SHA 和下载地址均保留。
- 删除 Studio 层任何假数据口径：数量、样本、来源、分数、设计和运行状态全部由实际 API 返回；缺少合格组合或 CJK 字体时明确失败，不套通用设计、空记录或乱码字体兜底。结构图明确标注为本地结构概念稿、`imageGenerationUsed=false`、`massProductionReady=false`。

原因：

- 产品核心是持续维护“在地文化内容 + 爆款产品形态”两套原始材料并自动形成可审阅的设计结果。默认展示中间节点会遮住材料与产出，也无法回答数字、评分和设计是否真实；工作流应只在用户看中设计并需要介入时出现。

验证：

- 本地 `pytest` 83/83、Workbench TypeScript 5/5；Ruff、`uv lock --check`、TypeScript no-emit、ESLint、Vinext 五阶段 production build、完整 `pnpm audit`、`pip-audit --local`、启动脚本语法、`git diff --check` 与 React/React DOM/React Flow 单版本检查均通过，依赖审计为 0 个已知漏洞。
- 独立 HTTP 实测完成手动组合 201、编辑生成 V2 200，V1/V2 SHA 不同且旧新 PNG 均可读取；本地主进程健康响应为 0.10.0，采集/每日设计双调度器在线，文化 22/来源 32、形态 10/样本 378、当日活跃设计 3，六个一级路由、动态设计/编辑路由和 PNG 均为 200，非法文化 ID 为 422。
- 新增 6 项 Studio 后端回归，覆盖真实两库、Top 3 去重、幂等/重跑、自由组合/V2、零样本拒绝与启动补跑；Windows desktop UI 门增加一项六路由真实 API/axe 检查，总数定义为 32，须由本轮 GitHub Actions 实际执行后再追加远端结果。

边界：

- 378 是已保存的历史真实平台快照，不是今日实时销量；当前四平台授权/云端上游采集条件仍未满足，市场通道必须继续显示 `blocked`，不能用每日设计成功掩盖采集阻断。
- Studio 当前输出是可追溯的结构概念稿，不是生成式商品摄影、量产工程图或商业艺术批准。自动化依赖单副本常驻进程、持久卷、网络与平台重启策略；多副本前仍需分布式锁或外部队列。
- 本日志只记录已完成的本地实现与验证；GitHub Actions 和 Zeabur 0.10.0 的部署号、远端鉴权、持久化与业务 API 结果将在实际完成后另行追加，当前不提前声称上线。

涉及文件：

- `app/studio.py`、`app/tool_api.py`、`app/designer/poster.py`、`tests/test_studio.py`、`tests/test_collection.py`
- `web/app/studio-*`、`web/app/page.tsx`、`web/app/create/`、`web/app/designs/`、`web/app/libraries/`、`web/app/operations/`、`web/app/workflow/`、`web/tests/ui/ui-quality.spec.ts`
- `.env.example`、`.github/workflows/quality.yml`、`Dockerfile`、`pyproject.toml`、`uv.lock`、`web/package.json`
- `README.md`、`PRODUCT.md`、`DESIGN.md`、`docs/architecture.md`、`docs/continuous_collection.md`、`docs/deployment_zeabur.md`、`docs/frontend_quality_workflow.md`、`docs/real_machine_test.md`、`WORKFLOW.md`

### 2026-09-01｜0.9.2｜GitHub 跨平台门与 Zeabur 上线验收

变更：

- 以功能源提交 `84e0a41` 生成 115 文件/27,938,032 字节的隔离发布包，完成敏感路径、私钥、长凭证、符号链接、禁止目录与必需文件审计；部署 Zeabur 0.9.2 `6a95b5a29ed7d65609e27bf6`。
- 完成线上匿名/认证入口、九路由/九详情 API、DesignPackage、图像资产、调度心跳、安全响应头、429 限流、非 root worker、ext4 持久卷与运行日志验收。隔离工作区真实生成 DesignPackage 和海报，然后精确清理。
- 同步 README、产品/设计契约、持续采集、前端质量、Zeabur 部署、实机记录与本工作流的线上 0.9.2 事实。

原因：

- 用户要求项目达到真实可用；发布成功必须同时有跨平台质量门、真实远端业务动作、鉴权/安全/持久化验收和可恢复运行态，不能只根据平台 `RUNNING` 声明完成。

验证：

- GitHub Actions [运行 `33417318879`](https://github.com/miracle121388-a11y/QianCraft/actions/runs/33417318879) 完成 Ubuntu/macOS/Windows Python 77/77、Linux Ruff/锁/依赖审计和 Windows Web/构建/31 项 Playwright；4 个 Job 全部 success，annotation 均为 0。
- 远端构建日志确认 Vinext 五阶段和 `qiancraft-0.9.2`。公网 `/healthz=200`、匿名首页/API=401；认证后首页、九路由、九详情 API、DesignPackage 和 4 项图像全为 200。数据为 9 节点/10 边、22 文化/32 来源、378 历史市场样本、8 机会、12 视觉参考和 3 概念。
- 隔离远端工作区创建 201，Design Agent 201，DesignPackage 200，322,090 字节 PNG 200；无图像 provider 时 Regenerate/Generate More 均为 `warning`，严格研究为 422。临时工作区清理后缺失，默认工作区仍为 9/10 且停在 `production_release_and_factory_order` 之前。
- 公网实际下发 HSTS/CSP/Permissions-Policy/X-Content-Type-Options/Referrer-Policy/X-Frame-Options；80 个 API 突发请求为 42×200 + 38×429，之后健康仍为 200。Tool API、Vinext 和 Nginx worker UID 为 33，Nginx master UID 为 0；上线后严重运行错误日志为 0 行。
- 发布前 tar 快照与发布后 ZIP 快照均通过 SHA-256 校验并复制到持久卷外的本机受控目录；发布后快照内含 5 文件/57,741 字节，服务器与 Conda 本地校验均通过。

边界：

- 独立图像 provider 仍未配置；云端仍无 MediaCrawler/LightRAG/GPT Researcher 上游运行时和四平台授权会话。这两项需新的合法 provider/Secret、上游许可和用户授权，当前 warning/422 是正确产品行为，不是待伪造的成功。
- 站点仍是共享 Basic Auth、单 API 副本的受保护验证环境；本机卷外快照不等于定时异地备份、自动保留策略、外部告警或已完成恢复演练。本轮仍停在 DesignPackage、工厂报价/首样简报和概念海报，没有生产放行、工厂下单、商业艺术批准或制造/合规就绪声明。

涉及文件：

- `README.md`、`qiancraft.egg-info/PKG-INFO`、`PRODUCT.md`、`DESIGN.md`
- `docs/continuous_collection.md`、`docs/frontend_quality_workflow.md`、`docs/deployment_zeabur.md`、`docs/real_machine_test.md`
- `WORKFLOW.md`

### 2026-09-01｜0.9.2｜Docker 发布上下文收敛

变更：

- 修正 `.dockerignore` 中 `web/output` 被误写为 `web/outputs` 的遗漏；明确排除约 5 MB 的 Playwright 截图/记录、Web 测试、GitHub 配置、本地包元数据、工作流文档和其他不参与镜像构建的文件。`scripts/` 只重新纳入 Dockerfile 实际复制的 `runtime_snapshot.py`。
- 在部署回归中固定上述排除项和快照脚本重新纳入规则，防止后续发布再次把本地质量产物或无关文件带入构建上下文。

原因：

- 远端部署前的上下文审计发现单复数路径错误会无谓增加上传体积和构建输入面。镜像内容虽不受影响，但真实发布包应最小化且可回归。

验证：

- 修复前本地 `web/output` 为约 4.8 MB、`.playwright-cli` 与 `web/tests` 另约 0.6 MB；新增测试与最终 GitHub Actions 将验证排除契约。Zeabur 发布尚未触发。

边界：

- 本次不删除仓库内的验收截图或测试，只从 Docker 构建上下文排除；正式数据、A/B/C 资产、海报、应用源码和运行态快照工具仍会进入镜像。

涉及文件：

- `.dockerignore`
- `tests/test_deployment.py`
- `WORKFLOW.md`

### 2026-09-01｜0.9.2｜GitHub Actions 弃用参数清理

变更：

- 第二次 Actions 运行 `33416007068` 的四个 Job 全部通过，但 setup-miniconda v4 对两处 `auto-activate-base` 产生 6 条弃用注解；按运行器提示替换为 `auto-activate: false`。所有命令本来就显式使用 `conda run -n qiancraft`，因此不依赖 shell 自动激活，行为保持不变。

原因：

- 已通过但带弃用注解的工作流会积累升级风险，不能作为无维护债务的最终质量门。本轮目标是把 CI 配置收敛到当前 action 接口。

验证：

- 运行 `33416007068` 实际通过 Ubuntu/macOS/Windows Python 76/76、Linux Ruff/锁/依赖审计，以及 Windows Web 单测、类型、ESLint、构建、依赖审计、31 项 Playwright（含权威像素基线）和 shell/diff 门；唯一注解就是上述弃用参数。替换后的 YAML 通过本地解析与 `git diff --check`，最终无弃用参数的远端运行结果待推送确认。

边界：

- 本次只清理 CI action 输入，不改变产品代码、依赖、数据或外部服务状态；Zeabur 0.9.2 仍未发布。

涉及文件：

- `.github/workflows/quality.yml`
- `WORKFLOW.md`

### 2026-09-01｜0.9.2｜GitHub Actions 运行器上下文修复

变更：

- 首次推送后的 Actions 运行 `33415813772` 在工作流解析阶段失败且没有创建 Job。定位为 job 级 `env` 使用了只在 runner/step 阶段可用的 `runner.temp`；将临时 Tool Workspace 变量下移到 Windows Playwright step，其他 CI 拓扑和命令不变。

原因：

- 本地 YAML 解析只能证明语法有效，不能证明 GitHub 表达式上下文在对应层级可用。必须以实际 Actions 运行结果为准，不能把零 Job 的解析失败写成跨平台质量门通过。

验证：

- 首次运行的确定事实为 `failure / jobs=[]`，无测试被执行；修复后的 YAML 通过本地解析与 `git diff --check`。新的远端运行结果将在推送后核对，未完成前仍不声明 CI 通过。

边界：

- 本次只修复 CI 配置作用域，不改变产品运行逻辑、数据、视觉或外部能力边界；Zeabur 0.9.2 仍未发布。

涉及文件：

- `.github/workflows/quality.yml`
- `WORKFLOW.md`

### 2026-09-01｜0.9.2｜跨平台质量门、安全基线与可恢复运行态

变更：

- 修正严格研究预检把交互采集硬编码为 Windows 的缺陷：现在 Windows、macOS 及具有图形会话的 Linux 可进入显式授权流程，无图形会话的 Zeabur 容器继续诚实返回 422；空兼容开关恢复自动检测，显式 `false` 仍可强制关闭。旧版设计状态接口改为读取真实图像 provider 状态。
- 为文化公共页面采集补齐 SSRF 防护：输入 URL、DNS 解析得到的全部地址及每次重定向目标都拒绝本机、私网、链路本地、保留地址和内部域名；实际 TCP 连接固定使用当次已校验的地址并禁用环境代理，新增 DNS rebinding 回归，避免重新解析、代理或跳转绕过。
- 修正市场页陈旧文案、四平台断言范围和采集按钮运行态竞态；内部页面跳转统一使用前端路由。Playwright 功能断言改为跨平台，Windows Chromium 像素基线只在 Windows 执行，macOS 不再因缺少 Windows 快照误报失败。
- 新增 Conda `qiancraft` 标准环境和 GitHub Actions：Python 在 Ubuntu/macOS/Windows 全量回归，Linux 执行 Ruff、锁文件和 Python 依赖审计，Windows 执行 Web 单测、类型、ESLint、构建、依赖审计与像素门。前端升级至 Next 16.3.3、React 19.2.8、Vite 8.2.2、Wrangler 4.127.1 等兼容版本，清除初始扫描的 7 个生产/10 个全量 high 漏洞；ESLint 保留兼容的 9.39.4。
- Nginx 新增 HSTS、CSP、Permissions-Policy、隐藏版本和 API 429 限流；部署测试校验 Basic Auth 健康例外、哈希口令/未配置拒绝、镜像快照工具与非 root 运行。新增 `runtime_snapshot.py`：ZIP 内含 SHA-256 清单，创建前自校验，恢复拒绝路径穿越/符号链接/超限归档，要求停服务和双重显式确认并保留回滚目录。
- 勘误：0.9.1 当前状态及部分历史叙述把正式 8 条机会写成“DeepSeek 实际生成”。实际运行清单为 `generated_opportunities_accepted=0`；GPT Researcher / DeepSeek 确实被调用，但其建议未通过证据契约，当前 8 条均来自本地证据规则基线。历史日志按契约不回写，以本条追加纠正。
- 本地版本统一为 0.9.2；README、产品/设计说明、架构、持续采集、前端质量、Zeabur 部署和实机记录同步当前事实。此条记录时线上仍为 0.9.1，0.9.2 发布结果将另行追加，避免把待执行部署写成完成。

原因：

- 全面审计发现跨平台门把 macOS 合法交互环境误判为不可用、CI 缺失、公共抓取存在 DNS/重定向型 SSRF 风险、Nginx 缺少关键浏览器安全头和限流、依赖存在已知高危漏洞、运行态没有可验证恢复工具，且文档对机会来源存在事实性误述。这些问题会直接影响真实可用性、安全性和交付可信度。

验证：

- Conda `qiancraft`（Python 3.13）本轮实测 `pytest` 76/76、Ruff、`uv lock --check`、`pip-audit`、`bash -n deploy/start-zeabur.sh` 与 `git diff --check` 全部通过；Python 依赖为零已知漏洞。
- Web 本轮实测单元测试 5/5、typecheck、ESLint、peer 检查、Vinext 生产构建和 `pnpm audit --audit-level=high` 全部通过，Web 依赖为零已知漏洞。macOS `desktop-chromium` 为 30 passed / 1 个 Windows 像素基线按设计跳过。
- 新增回归覆盖私网/本机/IPv6/内部域名、DNS 私网解析与 rebinding、私网重定向、跨平台交互检测、显式关闭、旧版 provider 状态、Nginx 安全头/限流、Docker 快照工具和快照创建/校验/恢复/回滚/路径穿越拒绝。
- GitHub Actions 与 Zeabur 0.9.2 在本条记录时尚未执行，不将其写成通过；推送、CI、部署及认证后的线上业务验收完成后追加独立日志。

边界：

- 当前仍未配置独立 `IMAGE_*` provider；已有 A/B/C、DesignPackage 和海报可用，Regenerate / Generate More 必须 warning，不会伪造新图成功。
- Zeabur 仍未配置 MediaCrawler/LightRAG/GPT Researcher 上游运行时及四平台授权会话；严格研究保持 422，378 条市场数据仍是历史快照。启用须解决非商业上游许可、平台条款、合规授权、长期会话和队列/超时，Cookie 或密钥不得进入仓库。
- Nginx 仍使用共享 Basic Auth，适合作为受保护内部验证环境，不等于多用户生产身份系统。快照工具不等于自动异地备份；独立存储、保留策略、告警和恢复演练仍是上线运营责任。
- 项目继续停在 DesignPackage、工厂报价/首样简报与概念海报，不包含生产发布、工厂下单、商业艺术批准或制造/合规就绪声明。

涉及文件：

- 后端/安全/恢复：`app/collection.py`、`app/tool_api.py`、`scripts/runtime_snapshot.py`、`tests/test_collection.py`、`tests/test_tool_api.py`、`tests/test_deployment.py`、`tests/test_runtime_snapshot.py`、`Dockerfile`、`deploy/nginx.conf.template`、`.env.example`。
- 运行与质量门：`environment.yml`、`.github/workflows/quality.yml`、`pyproject.toml`、`uv.lock`、`app/__init__.py`、`qiancraft.egg-info/`、`web/package.json`、`web/pnpm-lock.yaml`、`web/playwright.config.ts`、`web/tests/ui/ui-quality.spec.ts`、`web/app/workbench.tsx`、`web/app/node-detail.tsx`。
- 文档：`README.md`、`PRODUCT.md`、`DESIGN.md`、`docs/architecture.md`、`docs/continuous_collection.md`、`docs/deployment_zeabur.md`、`docs/frontend_quality_workflow.md`、`docs/real_machine_test.md`、`WORKFLOW.md`。

### 2026-08-31｜0.9.1｜完整回归、真实远端功能验收与 Zeabur 上线

变更：

- 在未改动产品运行源码的前提下重新盘点当前 Git、Python/Web 依赖、Docker/Nginx/Zeabur 拓扑、服务器变量存在性与线上 0.8.0 基线；确认当前提交与 `origin/main` 一致，工作树起点干净，现有 Basic Auth、LLM Secret 与持久卷可复用。
- 从已扫描的 0.8 发布模板构建隔离 `.zeabur-stage-091`，覆盖当前 0.9.1 运行文件并补入持续采集与 C2 新文件；最终 79 个文件、19,597,854 字节，敏感路径、长 `sk-` 模式和必需文件检查分别为 0、0、0。通过 Zeabur 冷构建发布部署 `6a958619be05255ec5e261f7`，当前为 `RUNNING`，旧 0.8.0 在新版本就绪前持续服务并于切换后正常移除。
- 在服务器统一 Nginx 入口内使用现有 Secret 完成认证验收，并创建隔离远端工作区真实执行 New、Rename/Save/Load、Decision v2、Design Agent、DesignPackage、Poster v2、九节点详情和生成 PNG 读取；临时工作区、设计运行与生成目录随后按精确 ID 清理，默认工作区和正式资产未被测试污染。
- 同步 README、产品/设计记录、Zeabur 部署说明、实机验收和本工作流：把线上版本、测试数量、C2 desktop-only 范围、当前图像/实时采集边界和可复现 Ruff 命令更新为实际状态。普通 `uv run ruff` 会落到系统 Ruff 0.14.13；标准命令现固定为 `uv run --extra test ruff check .`，使用锁定的 Ruff 0.16.5。

原因：

- 用户要求在项目再次更新后详细跑通全部链路，让立即使用的用户可从网页进入，并把当前版本部署到服务器。必须同时证明构建成功、真实业务动作可执行、持久化与鉴权没有退化，且不能把未配置的外部图像或平台授权能力包装成已上线。

验证：

- 环境探针：CPython 3.13.9；Pydantic、HTTPX、JSON Repair、NumPy、LightRAG、GPT Researcher 与 MediaCrawler 隔离运行时可用，MediaCrawler 成功导入 `bili,dy,ks,tieba,wb,xhs,zhihu`；DeepSeek `/models` 本机与服务器均为 200、返回 3 个模型且目标 `deepseek-v4-flash` 存在。
- 后端与静态门：`.venv\Scripts\python.exe -m pytest -q` 为 58/58；`uv run --extra test ruff check .`、`uv lock --check` 与 `bash -n deploy/start-zeabur.sh` 均退出 0。
- Web 门：`pnpm test` 为 5/5，typecheck、ESLint、Vinext 五阶段 production build 均退出 0；`pnpm exec playwright test --project=desktop-chromium` 为 31/31，覆盖工作台与九个详情路由、C2 几何/精确表面、axe、焦点、交互、断线与两张电脑端视觉快照。额外 Playwright CLI 实操完成工作区、Decision Studio、Delivery、Inspector 与 Poster 详情，浏览器控制台为 0 error / 0 warning。
- 本地真实 HTTP 隔离工作区完成 New/Rename/Save、9 节点/10 边、Design Agent 运行 `20260831T134054Z-305fabee`、Poster v2、DesignPackage、九详情与两项资产 200；严格研究因授权/运行时前置条件缺失返回 422，临时文件随后清理。当前 Windows 没有 Docker 可执行文件，因此本地只验证应用层生产构建；Linux/Docker 拓扑由 Zeabur 远端实际构建与运行补齐。
- 远端构建日志确认 Vinext 五阶段完成并安装 `qiancraft-0.9.1`；部署为 `RUNNING`。公网 `/healthz` 为 200，匿名 `/` 与 `/api/health` 为 401；认证后首页、九路由、健康/Bootstrap、九详情、DesignPackage 与四项正式 PNG 资产全部为 200。应用版本为 0.9.1，`/app/data/runtime` 实际挂载 `/dev/vda3` ext4，调度器 `online=true / heartbeatFresh=true / enabled=true / healthy`。
- 远端隔离工作区 `workspace-d093fe03` 的 Create 201、Save/Load/Decision/Poster/DesignPackage/九详情均 200，Design Agent 201，两个 322,090 字节 PNG 均为 `image/png`/200，严格研究预检为 422；清理后工作区文件、`design_runs` 与 `generated` 目录均不存在，工作区列表只保留 `guizhou-miao-demo`。默认 Bootstrap 仍为 9 节点/10 边、22 条文化记录、378 条历史市场样本和 8 条机会。
- 上线后的调度首轮真实运行：文化探测 4 个登记来源，3 个正常、1 个失败，状态 `degraded`，只新增 1 条 `pending_review` 候选且正式图谱保持 22 条/32 来源；市场因 7 项运行时/授权条件缺失为 `blocked`。这是预期诚实降级，不是伪实时成功。
- 文档收口：6 个变更文档的相对 Markdown 链接缺失为 0，长 `sk-` 与凭证赋值模式命中文件均为 0；`git diff --check` 退出 0，仅输出 Windows 工作树预期的 LF→CRLF 提示。

边界：

- 当前本机与服务器均未配置独立 `IMAGE_*` provider；现有 A/B/C、DesignPackage 和海报可用，但 Regenerate / Generate More 会保留旧资产并显示 warning。此前 Qwen Image 3.0 成功记录是历史证据，不代表当前 provider 已连接。
- 精简云端镜像不含 MediaCrawler、LightRAG、GPT Researcher 上游运行时，四平台也没有已连接的授权浏览器；严格实时研究保持预检阻断，378 条数据仍是有时间边界的历史真实快照。若要服务器实爬，必须另行解决上游许可、合规授权、长期会话、队列和超时，不能上传本机 Cookie。
- C2 本轮只验收 desktop-chromium 1440×960；没有运行或宣称 mobile/tablet C2。线上仍是共享 Basic Auth 的受保护产品验证环境，不是多用户正式账户系统；扩大使用前需补用户级身份、权限审计、备份恢复、告警、口令轮换、队列和限流。
- 本轮继续停在 DesignPackage、工厂报价/首样简报与概念海报；没有授权生产发布、工厂下单、商业艺术批准或制造/合规就绪声明。

涉及文件：

- `README.md`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/deployment_zeabur.md`
- `docs/real_machine_test.md`
- `WORKFLOW.md`
- 外部部署：Zeabur deployment `6a958619be05255ec5e261f7`；本地忽略的发布副本 `.zeabur-stage-091/`

### 2026-08-30｜现场演示全链路验收与 GitHub 交付

变更：

- 按评委现场展示标准重新验收稳定 Demo：在临时目录跑通文化知识、市场证据、机会策略、Designer Handoff、Design Agent、13 项产物与 1800×2400 海报；本地 Tool API 返回健康，默认 Workspace 为 9 节点/10 连线，9 个节点详情接口与 4 个关键图片/海报资源均为 200。
- 在真实电脑端浏览器逐页打开文化、市场、策略、任务书、视觉、Concept A/B/C 与海报，全部加载真实标题且破图为 0；Human Decision Studio 的 7 个阶段、可用保存动作、关闭恢复与控制台零错误均通过。
- 用户随后授权把当前完整项目版本推送至 GitHub；提交范围为当前 75 个项目文件，包含本轮前端、后端、测试、文档、正式产物和设计审阅输入。远端为 `origin/main`，推送前本地与远端共同基点为 `919ceaa`，没有擅自创建 PR 或改写远端历史。

原因：

- 当前目标是现场稳定展示，而不是依赖四平台临时授权或外部 API 时延。此次以项目自带的离线 Demo 与现有真实/历史证据验证基本产品效果，再把同一已验收工作树交付到远端仓库。

验证：

- `python -m pytest -q`：58/58；`pytest tests/test_demo_pipeline.py -q`：25/25；Ruff 与 `python -m uv lock --check` 均退出 0。
- `pnpm --dir web test`：5/5；typecheck、ESLint 与 Vinext 五阶段 production build 均退出 0；`desktop-chromium`：31/31。
- 推送候选扫描：75 个文件；`.env` 候选 0、待提交长 `sk-` 凭证 0、50 MiB 以上文件 0。被忽略的本机凭证、Cookie 与授权会话未读取、未暂存、未记录。

边界：

- 现场应使用稳定 Demo、378 条有时间边界的历史市场样本、现有 A/B/C 与海报；不建议现场点击“严格实时全链路”。四平台 live、完整外部模型重跑、mobile/tablet C2、0.9.1 线上部署、生产发布与量产/合规仍不属于此次 GitHub 推送结论。
- GitHub 推送只交付源码、受跟踪产物与文档，不等同于 Zeabur 部署或线上版本切换；本条所在提交即本次远端交付版本。

涉及文件：

- 当前工作树 75 个待提交项目文件，重点包括 `app/`、`scripts/`、`tests/`、`web/`、`data/outputs/`、`docs/`、`.impeccable/`、`README.md`、`DESIGN.md`、`PRODUCT.md`、`WORKFLOW.md`、`pyproject.toml` 与 `uv.lock`。

### 2026-08-30｜C2 终审修复：桌面几何门、精确表面、形状与焦点

变更：

- 先增加 6 项浏览器回归，并在生产样式未改时记录 6/6 真实失败；随后把 60/72/210/330 完整工作台几何门从 761px 收紧到 1280px，使 1024px 不再误入电脑端固定布局。
- 用窄选择器固定 Market 首个 KPI 为 canvas、Strategy 机会标题和 Poster 首张拆解卡为 node；把 Decision Studio 收到 14px 且去除阴影，同时保留真实覆盖画布的 Inspector 阴影；普通模式工作台焦点改用 C2 `#345C7D`，forced-colors 继续用系统 `Highlight`。
- `DESIGN.md` 和 Impeccable surface record 已统一到 10–14px、普通卡片/Decision Studio 无阴影、仅重叠 Inspector 可投影的边界；未改变 API、数据、组件逻辑或 mobile 样式/快照。

原因：

- 终审发现宽屏固定几何过早作用于 1024px、三个语义表面被旧选择器/内联透明值穿透、Decision Studio 仍是 16px 和大阴影，且工作台普通焦点被 globals 后置黑色覆盖；设计记录仍保留 16/18px 的旧口径。

验证：

- RED：`pnpm --dir web exec playwright test --project=desktop-chromium --grep "终审回归"` 为 6 failed；实际分别观察到 1024px 的 72/210/330 固定几何、Market `rgb(0, 0, 0)`、Strategy `rgb(29, 29, 31)`、Poster `rgb(245, 245, 247)`、Decision Studio 16px 与 `rgba(0, 0, 0, 0.24) 0px 34px 100px 0px`、工作台焦点黑色。
- GREEN：同一聚焦命令 6/6；`pnpm --dir web test` 5/5，`pnpm --dir web typecheck`、`pnpm --dir web lint`、`pnpm --dir web build` 均退出 0；完整 `desktop-chromium` 31/31。
- 两张 desktop snapshot 未更新且终审后 SHA-256 仍为 workbench `79B85C6F…91556`、Brief `78F839DB…BF84`；两张 mobile snapshot 未运行、未更新且 SHA-256 仍为 workbench `6DE68F26…71EC`、Brief `FB62FF2E…60A`。
- 终审指定文件 `git diff --check` 退出 0（只有 Windows LF→CRLF 提示）。安全独立长 `sk-` 扫描未读取 `.env`、未打印匹配内容：QianCraft 自有受跟踪范围为 0 命中；全仓受跟踪范围退出 1，定位到 2 个既有、未改动的 extracted-upstream 示例文件（`local_culture/LightRAG-main/env.docker-compose-full` 与 `local_culture/LightRAG-main/examples/unofficial-sample/lightrag_llamaindex_litellm_opik_demo.py`），按上游边界保留并作为已知关注项记录。

边界：

- 本轮没有运行 mobile project、没有更新任何 mobile/desktop snapshot、没有改依赖、API、数据逻辑或发布状态；1024px 仅作为电脑端完整几何的负向保护，不是新的 tablet/mobile 验收。线上仍为 0.8.0，C2 仍只在本地完成。

涉及文件：

- `web/app/tonal-focus.css`
- `web/tests/ui/ui-quality.spec.ts`
- `DESIGN.md`
- `.impeccable/surfaces/web-app-workbench-tsx.md`
- `.superpowers/sdd/2026-08-30-tonal-focus-review-implementation/final-fix-report.md`
- `WORKFLOW.md`

### 2026-08-30｜C2 收口：纠正模型与图像服务当前约束

变更：

- 纠正“当前已知约束”中两条沿用旧环境状态的说明：本机被忽略的 `.env` 已配置 DeepSeek 与 Qwen Image 3.0，独立图像自动化服务不再是“未配置”，DeepSeek 也不再是“等待凭证”。
- 当前边界改为与状态表一致：DeepSeek 探针和三次 Qwen Image 3.0 同步生成已经实测成功，但配置完成后仍未重跑完整 Research → Strategy → Design → Poster 流水线；既有正式运行证据、旧成功资产和后续新运行必须继续分开标注。

原因：

- C2 电脑端文档审查发现第 11 节仍保留凭证配置前的旧约束，与本文件当前状态表冲突。此次用追加更正记录保留历史，同时让“当前约束”反映实际环境。

验证：

- 对照本文件“API”“图像生成适配”当前状态、`app/config.py` 的环境变量契约和 Task 6 独立审查结论逐项核对；未读取或输出 `.env`、API Key、Cookie 或授权会话值。
- 更正后重新执行目标文档 `git diff --check` 与前端最终回归；结果见本条之后的实际验收记录。

边界：

- 配置与独立探针/生图成功不等于完整产品流水线已在本轮重新运行，也不改变四平台授权、实时开关、378 条历史市场快照、C2 未部署或 mobile/tablet 未验收的状态。

涉及文件：

- `WORKFLOW.md`

### 2026-08-30｜C2 Tonal Focus Review 电脑端可运行首版

变更：

- 将批准构图 `.impeccable/mocks/tonal-focus-review.png`（SHA-256 `131cd5be…ffeb`）转成可运行的本地电脑端 C2：新增最后加载的 `web/app/tonal-focus.css`，固定暖矿物外壳、雾蓝 command/canvas、灰绿 rail/Dock、暖陶 Inspector、浅石节点、低饱和蓝 selected/primary 与四类低饱和状态色；批准构图只作为非字面比例、色块和聚焦参考，没有复制示意人物、时间、文件名、缩略图、数字或拓扑。
- 工作台在 1440×960 使用 60px command、72px rail、210px bottom Dock、330px right Inspector；真实 9 节点/10 连线、API、Workspace、拖拽等价路径和状态语义保持不变。Decision Studio、九个详情页、持续采集控制面与星图外围控件统一为 C2；文化关系星图内部 `#070708` 深色功能画布继续作为唯一例外。
- 用户中途把范围缩小为“只实现电脑端，不需要手机端”；Task 4 曾新增的平板/手机覆盖层、样式和测试增量已完整撤销，Tasks 1–3 的电脑端实现保留。本轮没有把既有 mobile 行为写成 C2 已适配。
- Task 5 在人工目视 Workbench、Decision、Culture、Market、Brief 后只更新两张 desktop Windows Chromium 快照；两张 mobile snapshot 从 Task 5 起点到终点 SHA-256 字节不变（workbench `6DE68F26…71EC`，Brief `FB62FF2E…60A`），但 workbench mobile 在起点前已相对 Git modified，且本轮没有运行 mobile project，因此不能据此推导 C2 mobile 通过。
- 正式设计宪法、Impeccable surface record、前端质量工作流与当前状态已同步到 Tonal Focus Review desktop-only 事实；版本保持 0.9.1，未单独改动版本文件。

原因：

- 用户批准 C2 后要求先得到可运行网站，并明确否定过度纯白、渐变、玻璃、光晕和无意义装饰色；随后又将本轮交付限定为电脑端。此次收口需要让运行代码、批准构图、正式设计记录、测试口径和 WORKFLOW 同时反映最终授权范围，避免旧 Monochrome 记录或历史 mobile 基线与实际交付漂移。

验证：

- `pnpm --dir web test`：5/5；`pnpm --dir web typecheck`：退出 0；`pnpm --dir web lint`：退出 0；`pnpm --dir web build`：Vinext client references、server references、RSC、client、SSR 五阶段完成，退出 0。
- `pnpm --dir web exec playwright test --project=desktop-chromium`：25/25，退出 0，用时约 1.3 分钟；只运行 1440×960 desktop project，覆盖十路由、C2 计算样式/几何、交互、axe、forced-colors、断线/阻断和两张 desktop 快照。
- brief 指定的 `git diff --check` 文件集合退出 0；仅有 Windows LF→CRLF 提示，无 whitespace error。
- 对全部 Git 跟踪文件执行边界化的长 `sk-` 凭证安全模式扫描，命中 0；扫描没有读取 `.env`，也没有输出任何 Key、Cookie 或授权值。
- Python 58/58 是此前 Qwen 原生适配轮次的既有结果，本轮没有修改后端且未重跑 Python、Ruff 或锁文件；历史桌面/手机 35 passed / 1 intentionally skipped 是 C2 前基线，不作为本轮结果。

边界：

- 当前只可声明 C2 电脑端首版在本地通过；mobile/tablet C2 未适配、未运行 Playwright、未做真实触屏或对应快照验收。若未来恢复响应式工作，须重新获得用户授权并从实现、自动门和真实设备一起复验。
- 自动 axe、forced-colors 与有限视觉 QA 不等于完整 WCAG 认证；真实屏幕阅读器、残障用户、跨平台字体与大规模图谱性能仍需专项验证。
- 四平台实时开关与授权状态未改变，378 条仍是带时间边界的历史快照；C2 未部署，受保护线上实例仍为 0.8.0。
- 产品仍止于 DesignPackage、工厂询价/首样简报和概念海报；没有生产发布、工厂下单、商业图稿批准、社区授权完成或制造/合规就绪声明。

涉及文件：

- 电脑端实现/测试：`web/app/layout.tsx`、`web/app/tonal-focus.css`、`web/tests/ui/ui-quality.spec.ts`、两张 desktop Windows Chromium 快照。
- 正式记录：`DESIGN.md`、`.impeccable/surfaces/web-app-workbench-tsx.md`、`docs/frontend_quality_workflow.md`、`WORKFLOW.md`。
- 已批准输入与实施记录：`.impeccable/mocks/tonal-focus-review.{json,png}`、`.impeccable/workbench-brief.md`、`PRODUCT.md`、`docs/superpowers/specs/2026-08-30-tonal-focus-review-design.md`、`docs/superpowers/plans/2026-08-30-tonal-focus-review-implementation.md`。

### 2026-08-30｜C2 Tonal Focus Review 实施计划完成

变更：

- 用户审阅并以“继续”批准 C2 前端设计规格；规格状态更新为已批准。
- 新增逐任务实施计划，把首版拆为主题契约、桌面 Focus Review 布局、Decision Studio/九详情统一、平板/手机覆盖层、有限视觉验收和正式设计/工作流同步六个可独立验证的任务。
- 实现路径固定为新建一个由根布局最后加载的 `web/app/tonal-focus.css`，复用现有 `workbench.tsx`、React Flow、详情组件和 API。计划明确不新增依赖、不修改 Python 后端、不重写已通过的业务逻辑，并保留当前脏工作树中的用户修改。

原因：

- 将已批准的设计规格转换为可直接执行、先失败再实现且具备明确验收命令的代码步骤，避免演示版为换肤而引入不必要架构或破坏真实功能。

验证：

- 计划已对照设计规格完成覆盖自检，包含固定色值、60/72/210/330 桌面比例、十路由、移动端 44px/溢出、焦点/手势、reduced-motion/forced-colors、真实状态和浏览器目视门。
- 计划占位符扫描为 0，路径、类名、测试命令和跨任务接口与当前仓库实际文件一致。本轮只新增计划和更新文档，没有修改前端运行代码，因此没有重写既有 Web/Python 通过记录。

边界：

- 可运行 C2 网站尚未产出；执行必须在下一阶段实际修改代码、运行完整前端质量门并完成浏览器目视后才能宣告完成。
- 当前工作树已有大量用户修改，计划明确禁止自动暂存、提交、重置或覆盖无关文件。四平台实时授权、线上 0.8.0 与量产/合规边界均未改变。

涉及文件：

- `docs/superpowers/specs/2026-08-30-tonal-focus-review-design.md`
- `docs/superpowers/plans/2026-08-30-tonal-focus-review-implementation.md`
- `WORKFLOW.md`

### 2026-08-30｜C2 Tonal Focus Review 获批与实现规格冻结

变更：

- 用户明确选择第三轮 C2 “Tonal Focus Review”，并要求先做出可运行网站供后续现场调试；对应 sidecar 改为 `approved=true`，保留用户批准语句，第三轮其余两版和前两轮探索继续保持未批准状态。
- 将工作台 brief 与产品体验方向同步为低饱和功能色块：60px 雾蓝命令栏、72px 灰绿工具栏、雾蓝画布、约 210px 上下文证据抽屉、330px 暖陶 Inspector、浅石节点和深灰蓝主动作/选中态。大面积纯白、渐变、玻璃、光晕、高饱和环境色和无意义装饰被明确排除。
- 新增前端重构设计规格，冻结真实数据与接口边界、桌面/平板/手机布局、组件责任、状态语义、可访问性和验证门。首版实现复用现有业务逻辑与 API，不复制生成图中的虚构内容，也不新增前端依赖。

原因：

- C2 已解决用户提出的“不要纯白，但颜色不要绚目；简约来自减少无意义修饰”的核心要求。代码开始前需要把用户批准的视觉构图转换为可验证的产品规则，避免实现过程中重新漂移或把生成模型的示意内容当作事实。

验证：

- `tonal-focus-review.json` 可被 JSON 解析，`approved=true`，登记 SHA-256 仍为 `131cd5be…ffeb`；同轮另外两份 Tonal sidecar 继续为 `approved=false`。
- 设计规格已完成占位符、范围矛盾、非目标、响应式、可访问性和验收项自检；本轮只更新审批与文档，没有修改前端运行代码，因此没有把 Web/Python 测试写成新通过记录。

边界：

- C2 PNG 只用于比例、区域层级和色块参考；其中的局部缩略图、文字、时间、人名与拓扑是非字面内容。正式实现必须继续读取真实九节点、十连线、22 条文化记录、378 条历史市场样本、8 条机会、引用与诚实状态。
- 前端代码尚未开始修改；下一步须在用户审阅本规格后编写实施计划，再进入实现与浏览器验证。当前四平台实时授权仍未连接，线上实例仍为 0.8.0，本轮没有部署或更改生产边界。

涉及文件：

- `.impeccable/mocks/tonal-focus-review.json`
- `.impeccable/workbench-brief.md`
- `PRODUCT.md`
- `docs/superpowers/specs/2026-08-30-tonal-focus-review-design.md`
- `WORKFLOW.md`

### 2026-08-30｜低饱和功能色块修订与第三轮构图门

变更：

- 用户指出第二轮 Apple 式界面虽然简约，但过度依赖纯白，缺少必要的基础色块；本轮不改变已经确认的专业工具结构，只把“简约”重新定义为减少无意义修饰，而不是删除颜色。
- 固定第三轮色彩语义：暖矿物 `#E6E2DA` 作为应用外壳，雾蓝灰 `#D9E1E8` 作为命令栏，灰绿 `#D7E1DC` 作为证据/素材区，雾蓝 `#E3E8EB` 作为节点画布，暖陶灰 `#E7DDD4` 作为 Inspector，浅石色 `#F0EEE9` 作为节点，选中面 `#CBD9E6` 与深灰蓝 `#345C7D` 只表达选中、焦点和主动作。状态色限制为低饱和橄榄、赭黄、陶土与中性灰，不使用渐变、玻璃、光晕、纹样或装饰色。
- 使用 Qwen Image 3.0 重新生成 Tonal Quiet Canvas、Tonal Column Workspace、Tonal Focus Review 三张 1664×928 构图；布局沿用上一轮三种结构，变量只剩色块层级和信息聚焦。三份 sidecar 与 PNG 都登记完整实际提示词，当前继续保持 `approved=false`。

原因：

- 用户需要“有颜色但不炫目”的简约界面：基础区域必须通过克制色块形成温度、层级和定位，但任何颜色都必须承担导航、区域、选择或状态语义，不能变成没有意义的装饰。

验证：

- Qwen `qwen-image-3.0-pro` 三次同步实机调用均成功；三张最终 PNG 均为 1664×928、Pillow 可读取并已逐张目视检查。画面均使用低饱和实色色块，没有深色主题、Mesh Gradient、玻璃、霓虹或高饱和彩色噪声。
- 写入提示词元数据后，三张最终 PNG 的 SHA-256 分别为 `f44325d2…a4e6`、`c2cc51b9…6d2c`、`131cd5be…ffeb`；`embed-prompt.mjs --scan` 实测 3 张 raster、0 缺失。

边界：

- 构图中的局部文件名、时间、人名、缩略图、数值、英文标签和节点连接是生成模型的非字面示意，不能进入正式实现。前端必须使用仓库真实中文数据、9 节点/10 连线、引用证据、诚实状态和已有接口；C2 底部三张示意缩略图尤其不得当作真实文化证据。
- 本轮仍未修改前端代码、设计系统或测试快照，也没有重跑 Python/Web 测试；必须等待用户选择 A2 / B2 / C2 后，才写设计规格、实施计划并开始 TDD 重构。

涉及文件：

- `.impeccable/mocks/tonal-quiet-canvas.{json,png}`
- `.impeccable/mocks/tonal-column-workspace.{json,png}`
- `.impeccable/mocks/tonal-focus-review.{json,png}`
- `WORKFLOW.md`

### 2026-08-30｜Apple 式浅色工具界面重选与第二轮构图门

变更：

- 用户明确否决首轮 Mesh Gradient + Glassmorphism 的深色配色；首轮 Signal Horizon、Evidence Lens、Prism Stage 不删除、不伪装成已选方案，三份 sidecar 继续保持 `approved=false`，只作为可审计的历史探索。
- 用户确认以 Apple Developer / App Store Connect 的清晰、克制和精密层级为主，融合 Freeform 的开放画布感；新的固定视觉策略为浅色 Restrained：`#F5F5F7` 画布、`#FFFFFF` 工作面、`#1D1D1F` 石墨文字、`#6E6E73` 次级文字、`#D2D2D7` 细线与仅用于主动作/焦点的 `#0071E3`。明确排除深色主题、Mesh Gradient、玻璃、霓虹、彩色环境光和大面积阴影。
- 运行 Impeccable direction seed `bbd71e4c`；外部 roll 服务不可达，因此本轮为无挑战者/无质量板的 degraded seed，且用户已钉住的 familiar/canon 方向优先于随机分配。随后使用 Qwen Image 3.0 分别生成 Quiet Canvas、Column Workspace、Focus Review 三张 1664×928 高保真构图，三版只改变信息结构，不改变视觉世界或真实功能边界。
- 为三张 PNG 写入逐版 JSON sidecar，并使用 Impeccable metadata 工具把完整实际提示词嵌入 PNG `impeccable:prompt` tEXt chunk；所有 sidecar 当前均为 `approved=false`，等待用户选择后再进入前端实现。

原因：

- 用户认为首轮深色渐变与玻璃配色不好看，希望改成更朴素、大气、接近 Apple 专业工具的视觉。整套前端视觉世界必须随用户审美反馈替换，不能在已被否决的方向上继续微调。

验证：

- Qwen `qwen-image-3.0-pro` 三次同步实机调用均成功；Quiet Canvas、Column Workspace、Focus Review 均为 1664×928 PNG、Pillow 可读取并已逐张目视检查，没有深色主题、Mesh Gradient、玻璃或霓虹回流。
- 写入提示词元数据后，三张最终 PNG 的 SHA-256 分别为 `83a3bd68…b819`、`57622954…c2a3`、`88812fda…e88e`；`embed-prompt.mjs --scan` 实测 3 张 raster、0 缺失。三份 JSON sidecar 均保存完整提示词、模型、方向种子、文件路径、最终 SHA-256 与未审批状态。

边界：

- 三张构图仍是非字面设计参考，模型生成的局部人名、时间、英文标签、状态和节点拓扑不能当作项目事实；实现必须使用仓库真实 9 节点/10 连线、22 条文化记录、378 条历史市场样本、8 条机会、真实状态与现有中文接口。
- 本轮没有修改任何前端代码、设计系统、测试快照或产品功能；也没有重新运行 Python/Web 测试，因为 API 适配器和运行代码未变。必须等待用户选择 A / B / C，之后才写设计规格、实施计划并开始 TDD 重构。

涉及文件：

- `.impeccable/mocks/apple-quiet-canvas.{json,png}`
- `.impeccable/mocks/apple-column-workspace.{json,png}`
- `.impeccable/mocks/apple-focus-review.{json,png}`
- `WORKFLOW.md`

### 2026-08-30｜Qwen Image 3.0 原生适配与“极光证据雷达”构图门

变更：

- 为 `ImageGenerationAdapter` 增加最小 `dashscope-native` 分支：北京 Workspace Host 继续由 `.env` 注入，代码只拼接官方同步 `services/aigc/multimodal-generation/generation` 路径；请求改用单轮 `messages/content/text`、`qwen-image-3.0-pro`、`width*height`、`n=1`、提示词扩写和无水印参数，响应从 `output.choices[0].message.content[0].image` 取 24 小时临时 URL 并立即下载。原 OpenAI-compatible `data[0].b64_json/url` 路径保持不变，没有新增 SDK 或依赖。
- 先写并实际观察 Qwen 原生契约测试失败，再做最小实现使其通过；测试在 HTTP 边界使用完整官方响应结构，断言真实本地 PNG 和手工推导的端点/负载，避免把测试写成源码文本检查。
- 使用本机受忽略凭证完成 DeepSeek 模型探针和三次 Qwen Image 3.0 实机生成；新增 Signal Horizon、Evidence Lens、Prism Stage 三张 1664×928 “Mesh Gradient + Glassmorphism / 极光证据雷达”高保真构图，以及逐版提示词、模型、文件路径和 SHA-256 sidecar。三版均保持 22 条文化证据、378 条市场样本、8 条机会、九节点证据链、Human Decision v2、Dock/Canvas/Inspector 与生产前边界的真实产品语义。

原因：

- 用户已在本机保存 DeepSeek 与千问凭证，并要求直接接入；现有图像适配器只支持 OpenAI-compatible `/images/generations`，与 Qwen Image 3.0 的 DashScope 原生协议不兼容。前端重构采用 Impeccable 构图门，必须先提供三个可比较的高保真方案并取得用户审批，避免直接在旧 CSS 上盲改。

验证：

- TDD 红灯实际为旧适配器读取不到 `data[0]`；绿灯后 `tests/test_workbench.py` 19/19 通过，完整 `pytest -q` 58/58 通过，`ruff check app/adapters/image_generation_adapter.py tests/test_workbench.py` 通过。
- `scripts/check_environment.py --probe-api` 使用项目 `.venv` 实测 DeepSeek 可达、返回 3 个模型且 `deepseek-v4-flash` 可用；默认系统 Python 缺 `json_repair` 的首轮探针在网络前失败，经定位后复用项目运行时，没有修改或污染全局 Python。
- Qwen `qwen-image-3.0-pro` 三次同步调用均成功，最终 PNG 均为 1664×928、Pillow 可读取，SHA-256 分别为 `d152762f…e795`、`0b5647fc…8557`、`fca9dd00…c28f`；三张图已逐张目视检查。全部受 Git 跟踪文件长 `sk-` 模式命中 0，密钥未进入命令、补丁、日志、源码或文档。

边界：

- 三张图是用于选择布局与视觉语言的非字面构图，模型生成的小图、局部文字和内容不能直接当作事实或生产资产；实现必须使用仓库真实数据、真实组件、可访问语义与既有接口。当前三个 sidecar 均为 `approved=false`，前端代码尚未开始重构，必须等待用户选择 A / B / C。
- 本轮只验证 DeepSeek 模型目录与 Qwen 生图链路，没有重新运行完整 Research → Strategy → Design → Poster 流水线；`LIVE_MODE=false`、`DEMO_MODE=true` 与四平台未授权状态不变，378 条市场记录仍是历史 cache。产品仍止于 DesignPackage、工厂询价/首样简报和概念海报，不代表商业图稿批准、工厂下单、量产或合规就绪。

涉及文件：

- `app/adapters/image_generation_adapter.py`
- `tests/test_workbench.py`
- `.impeccable/mocks/aurora-evidence-radar-signal-horizon.{json,png}`
- `.impeccable/mocks/aurora-evidence-radar-evidence-lens.{json,png}`
- `.impeccable/mocks/aurora-evidence-radar-prism-stage.{json,png}`
- `.env`（本机、被 Git 忽略）
- `WORKFLOW.md`

### 2026-08-29｜社媒文案精简｜贵州非遗传播核心前置

变更：

- 将小红书标题由“做非遗文创，先别急着画图”改为“让贵州非遗被看见，也被真正理解”，正文从技术链路说明收紧为使命、实践方式、针格模块概念样与阶段边界四个部分；发布话题由 9 个收敛为 6 个，更突出贵州非遗、贵州苗绣、文化传播与非遗文创。
- 明确 QianCraft 的传播核心：让贵州非遗不只被看见，也被真正理解；尊重地域和工艺差异，让出处被尊重、创新有根，并让非遗以被尊重的方式进入当代生活。正文用“来自哪里、属于哪种地域和工艺、谁参与决定、能否这样使用”四个直白问题解释项目方法，删除不影响理解的运行数字和技术术语。
- 同步修改轮播封面与收尾页：封面改为“让贵州非遗 / 被看见，也被理解”，收尾改为“传播的不只是图案，而是它背后的文化”，并把地域、技艺、人与故事作为最终记忆点；重新渲染 `01-cover.png` 与 `08-boundary.png`，中间六张证据与产品说明保持不变。

原因：

- 用户反馈原介绍仍偏复杂，希望读者更容易看懂，并明确写出项目为了传播贵州非遗文化的核心精神。此次只优化传播表达，不改变文化事实、市场口径、产品设计或生产前边界。

验证：

- 使用现有 Playwright/Chromium 重新渲染封面与收尾页，并对两张最终图目视复核；标题、核心精神、概念视觉声明、产品图和边界列表均可读，没有核心文字裁切。
- 再次逐页加载全部 8 张轮播源：每页只有 1 个活动画布，尺寸均为 `1080×1440`，破图 0，最终 PNG 数量为 8。
- 新版 `post.md` 为 578 个文件字符、40 行，标题回读为“让贵州非遗被看见，也被真正理解”；发布包 Markdown/HTML 未发现行尾空白，敏感模式扫描未发现长 `sk-`、Cookie 赋值或 API Key 赋值。没有修改运行代码或事实数据，因此没有重复 Python/Web 全量测试。

边界：

- “核心精神”是 QianCraft 的项目使命与传播主张，不是新增的文化史事实；具体地域、工艺、纹样公开范围、社区参与和商品化授权仍以证据与后续共审为准。
- 本轮没有登录或发布小红书；封面和 A/B/C 继续是概念视觉，不是量产实拍。针格模块仍只用于概念展示、报价与首样沟通，不代表量产、商业文化授权或制造/合规完成。

涉及文件：

- `docs/social/xiaohongshu/2026-08-29/post.md`
- `docs/social/xiaohongshu/2026-08-29/carousel.html`
- `docs/social/xiaohongshu/2026-08-29/slides/01-cover.png`
- `docs/social/xiaohongshu/2026-08-29/slides/08-boundary.png`
- `WORKFLOW.md`

### 2026-08-29｜0.9.1｜DeepSeek 与 Qwen 3.0 本地安全录入准备

变更：

- 新建被 Git 忽略的本机 `.env`，预填 DeepSeek 文本服务的 Base URL/模型，以及北京地域百炼 Workspace 的 Qwen Image 3.0 Host、`dashscope-native` provider 和 `qwen-image-3.0-pro` 模型；两项 Key 均保持空白，等待用户只在本机编辑器录入。
- 关闭 `api.txt` 兼容回退，避免同一机器上旧凭证覆盖当前显式配置。聊天中出现的既有明文凭证没有复制到命令、补丁、日志、源码或文档。

原因：

- 用户希望接入 DeepSeek 文本 API 与千问生图 API；项目安全约束禁止把聊天中的明文凭证继续传入工具调用，因此先完成可审计的非敏感配置和本机录入入口。

验证：

- `git check-ignore .env` 确认本机配置文件被忽略；安全解析仅输出变量是否存在和非敏感配置，结果为 `LLM_API_KEY=false`、`IMAGE_API_KEY=false`、DeepSeek Base URL/模型与 Qwen provider/Host/模型均符合预期。

边界：

- 当前仍未录入新凭证、未调用 DeepSeek 或 Qwen、未验证模型权限或费用状态。现有 `ImageGenerationAdapter` 仍按 OpenAI-compatible `/images/generations` 契约实现；Qwen 3.0 原生协议适配与实机生成必须在用户完成本机凭证录入后另行实现和验证。
- 本条不改变文化、市场、策划、DesignPackage、海报或生产前边界，也不代表前端 Mesh Gradient + Glassmorphism 重构已经完成。

涉及文件：

- `.env`（本机、被 Git 忽略）、`WORKFLOW.md`

### 2026-08-29｜社媒发布包｜QianCraft 小红书图文内容组合

变更：

- 新增 `docs/social/xiaohongshu/2026-08-29/` 发布包：`post.md` 提供可直接复制的小红书标题、正文与 9 个话题；`slides/` 提供按发布顺序命名的 8 张 1080×1440 PNG；`carousel.html` 保留确定性中文排版、数据卡、产品图、文化/市场/人工决策界面截图和边界页的可复现组合源；`README.md` 记录发布顺序、数字口径、素材边界和生成提示词。
- 笔记以“做非遗文创，先别急着画图”为入口，依次解释设计风险、文化证据、四平台历史样本、机会策略、七阶段人工决策、A/B/C 概念方向和当前阶段边界；正文与图片统一使用 22 条文化记录、32 条登记来源、378 条历史真实快照、8 条机会、7 个人工阶段、5 项 BOM、6 步装配、6 项质检和 1800×2400 海报的当前事实。
- 使用内置图像生成能力，以项目自有 `huaxi_grid_magnet_hero_v1.png` 为参考制作一张无字、冷中性设计工作台封面场景；最终卡片把它标为“概念视觉 / 非量产实拍”，没有使用馆藏图、民族服饰、神圣/祖源母题、品牌标识或 `reference_only` 像素。其余图片复用项目自有概念资产与已验收工作台截图。

原因：

- 用户需要一套关于 QianCraft 项目的小红书“文本 + 图片”内容组合，可直接复制正文并按顺序上传图片。传播重点需要让非技术读者先理解项目为什么强调证据和人工判断，同时避免把历史市场样本、AI 概念视觉或工厂首样简报写成实时趋势、量产实拍或商业/合规完成。

验证：

- 使用项目现有 Playwright 运行时和已安装 Chromium Headless Shell 实际渲染 8 个页面；逐页检查均只有 1 个活动画布、页面尺寸 `1080×1440`、破图 0，最终目录恰有 8 张 PNG。
- 对 8 张最终图逐张目视复核；首轮后针对第 2/4/5 张标题断句和第 6 张底部信息密度做定向调整并重新渲染。最终封面、数字卡、界面截图、A/B/C 对比、海报缩略图、页码与阶段边界均可读，没有裁切核心文字。
- 数字和边界逐项回查当前 `WORKFLOW.md`、README、DesignPackage 与正式海报状态；发布包文本敏感模式扫描未发现长 `sk-`、Cookie 赋值或 API Key 赋值。此次没有修改运行代码、数据契约或产品资产事实，因此没有重复 Python/Web 全量测试，也不把已有测试基线冒充本轮重跑。

边界：

- 本轮只生成并校验可发布物料，没有登录小红书、创建草稿或实际发布；平台客户端的最终裁切、封面取景和账号侧预览仍由用户发布前确认。
- 封面和 A/B/C 均是概念视觉，不是量产实拍。当前交付仍只到概念展示、工厂报价与首样沟通；没有量产定稿、工厂下单、商业文化授权、社区共审完成或制造/合规就绪声明。
- 378 条记录继续只代表有限历史真实快照，不是当前四平台实时趋势或爆款保证；文化登记来源和馆藏链接只用于证据与研究引用，不等于商品图稿授权。

涉及文件：

- `docs/social/xiaohongshu/2026-08-29/post.md`
- `docs/social/xiaohongshu/2026-08-29/README.md`
- `docs/social/xiaohongshu/2026-08-29/carousel.html`
- `docs/social/xiaohongshu/2026-08-29/assets/cover-concept-visual.png`
- `docs/social/xiaohongshu/2026-08-29/slides/*.png`
- `WORKFLOW.md`

### 2026-08-29｜0.9.1｜提交前端到端验收、可迁移产物与最终海报收口

变更：

- 修复显式 `--mode auto` 仍受 `.env.example` 的 `LIVE_MODE=false` 影响、未尝试 live 组件的问题；`Settings.with_mode("auto")` 现在固定为 live-first 且允许明确降级。新增回归覆盖 demo/auto/live 三种显式语义。
- 修复新工作区缺少被 Git 忽略的 `data/market/raw/*.jsonl` 时，已提交的 378 条真实派生快照无法进入流水线、榜单被降成 0 样本的问题。MediaCrawler Adapter 先读 raw，缺失时读取 `data/market/derived/latest.json` 并继续按平台过滤、校验和去重；没有 raw/derived 时仍诚实返回 unavailable。
- 新增项目产物路径序列化规则：项目根内写仓库相对路径，外部临时目录保留绝对路径；流水线、市场适配器、Design Agent、Poster Renderer、独立设计脚本和严格研究晋级共用同一边界。正式 `run_manifest.json` 的 13 个路径、市场派生路径与新生成的设计/渲染路径不再依赖旧机器盘符。
- 修复海报 BOM 标题硬编码“前6项”的错误；5 项 BOM 现在显示“共5项”，超过 6 项时才显示“前6项，完整表见JSON”。从既有真实 DeepSeek `DesignerHandoff` 重跑正式 Design Agent 与 Poster Renderer，更新 DesignPackage、PosterRenderRequest、1800×2400 海报、RenderManifest 和 RunManifest，没有重写历史文化/市场/策划事实。
- 将 Ruff 0.16.5 声明为测试依赖，`ruff check .` 明确排除 `local_culture/`、`market-intel_agent/`、`researcher_agent/` 三份保留许可证的只读上游源码；修复 QianCraft 自有层实际诊断。Playwright 增加可选 `QIANCRAFT_CHROMIUM_EXECUTABLE_PATH`，用于下载受限环境复用本机 Chrome；工作台视觉快照遮罩随凭证/运行环境变化的研究前置状态，布局和交互仍完整比较。
- 本地版本统一提升到 0.9.1，刷新 Python/Web 版本、uv 锁、包元数据、README、产品/设计记录、实机验收和本工作流；保留线上 0.8.0 未部署状态。新增提交前实施计划 `docs/superpowers/plans/2026-08-29-submission-end-to-end-hardening.md`。

原因：

- 提交前逐步实跑发现：显式 auto 实际没有进入 live-first、提交随附的派生市场证据在 fresh clone 不会被消费、海报文字与实际 BOM 数量不一致、正式清单仍带上一台电脑路径、Ruff 会误扫上游工程、视觉基线依赖本机凭证状态。上述问题会分别造成链路假降级、0 样本输出、交付文案错误、产物不可定位、静态检查不可复现和无意义截图失败。

验证：

- 环境探针：Python 3.13.9；LightRAG、GPT Researcher、MediaCrawler 三份上游入口正常；MediaCrawler 隔离环境完整安装并实际导入 `bili,dy,ks,tieba,wb,xhs,zhihu`。LightRAG 本地图实际加载 612 个实体、697 条关系并查询成功。当前机器 `LLM_API_KEY` 明确为 missing，GPT Researcher 只验证导入/前置阻断，没有伪造模型调用。
- 最终独立 auto 运行 `20260829T144536Z-2e6f3e5b`：`culture_knowledge=live`、`market_research=cache`、`strategist=cache`、`design_agent=live`、`poster_renderer=live`；8 条机会、13 项输出，所有清单路径为仓库相对路径且文件存在。市场使用 378 条提交随附历史快照（xhs 115、dy 14、bili 101、wb 148），未访问平台。
- 正式产物审计：8 个 Pydantic JSON 契约可重载；13 个 RunManifest 路径与市场派生文件存在；8 条机会、Top 3、12 条视觉参考、5 个 Pattern Primitive、OPP-006、5 项尺寸、5 项 BOM、6 步装配、6 项质检、378 样本和 Top 10 均符合契约。交接 SHA-256、海报 SHA-256 和 1800×2400 请求/实图尺寸一致；`mass_production_ready=false`、`reference_images_used_as_pixels=false`、`reference_only_images_used=false`。正式海报已按原始分辨率目视复核。
- 质量门：Python `pytest` 57/57；`ruff check .` 与 `uv lock --check` 通过。Web 单测 5/5、TypeScript no-emit、ESLint、Vinext 五阶段 production build 通过。Playwright 使用本机 Chrome 完整运行 36 个桌面/手机实例，35 passed / 1 intentionally skipped；Tool API 健康、Bootstrap、9 个节点详情、采集状态和正式资产请求均为 200。
- 安全与差异：项目自有跟踪文件长 `sk-` 模式扫描为 0；没有把 API Key、Cookie 或授权会话写入代码、文档、命令、日志或产物。

边界：

- 当前机器没有 LLM Key，所以本轮不能声称重新验证 DeepSeek/GPT Researcher live；正式 2026-08-28 输出继续保留此前真实 DeepSeek 证据，本轮独立 auto 清单明确标为 strategist cache。取得凭证后仍需单独做 live 集成复核。
- 独立 Images API 未配置，本轮只使用已经登记 SHA-256、经过目视复核的项目原创主视觉重排海报；没有把旧资产冒充新的图片 API 调用。四平台实时开关关闭且没有已连接授权，本轮未登录、未抓取，历史 378 条记录只标 cache。MediaCrawler 仍受非商业学习/研究许可证与平台条款约束。
- 0.9.1 未发布，线上仍是受保护的 0.8.0。本轮严格停在 DesignPackage、工厂报价/首样简报与概念海报；没有生产发布、工厂下单、商业艺术批准或制造/合规就绪声明。

涉及文件：

- 运行与契约：`app/__init__.py`、`app/config.py`、`app/pipeline.py`、`app/adapters/media_crawler_adapter.py`、`app/designer/agent.py`、`app/designer/poster.py`、`app/workbench.py`、`scripts/run_design_agent.py`、`tests/test_demo_pipeline.py`。
- 自有静态修复与依赖：`app/collection.py`、`app/tool_api.py`、`scripts/probe_market_platforms.py`、`pyproject.toml`、`uv.lock`、`qiancraft.egg-info/`。
- 正式交付：`data/outputs/design_specification.json`、`data/outputs/design_specification.md`、`data/outputs/poster_render_request.json`、`data/outputs/design_poster.png`、`data/outputs/design_render_manifest.json`、`data/outputs/run_manifest.json`。
- 前端与文档：`web/package.json`、`web/playwright.config.ts`、`web/tests/ui/ui-quality.spec.ts`、移动工作台视觉快照、`README.md`、`PRODUCT.md`、`DESIGN.md`、`docs/continuous_collection.md`、`docs/deployment_zeabur.md`、`docs/frontend_quality_workflow.md`、`docs/real_machine_test.md`、提交前实施计划与 `WORKFLOW.md`。

### 2026-08-29｜0.9.0｜知识星图、持续采集调度与双控制面

变更：

- 新增 `app/collection.py` 持续采集服务，把文化来源巡检与市场严格刷新拆成两条持久通道；配置、状态、真实心跳、下次运行、连续失败/退避、事件、候选、已见指纹和运行号写入 `data/runtime/tool_workspace/collection/`。文化通道使用条件请求、内容指纹与严格文章过滤发现同域资料，只进入 `pending_review`/`ready_to_structure`/`rejected` 候选门；只有全部已探测来源成功才是 healthy，部分失败为 degraded。市场通道先检查实时开关、MediaCrawler 运行时与 xhs/dy/bili/wb 授权，缺项即 blocked，只有最终 `live_verified` 才允许晋级。
- `app/tool_api.py` 增加 collection 状态、事件、候选、配置、暂停/恢复/立即运行与审核 API，启动时自动启动调度线程，`/api/health` 返回真实调度心跳；线程死亡或心跳超过 45 秒时返回 503，Docker HEALTHCHECK 随之失败，交给已配置的平台重启策略恢复。客户端提前断开时安全吞掉 BrokenPipe/ConnectionReset，不产生第二次错误响应。Nginx `/healthz` 代理真实 API 健康，启动脚本同时监督 API、Web 与 Nginx，任一子进程退出即失败；新增环境变量说明与单副本/持久卷边界。
- 文化节点由普通关系列表升级为可搜索、分类过滤、选点检查证据的黑色知识星图，保持白/冷灰/石墨/纯黑的工具 chrome。桌面支持按钮/滚轮缩放、鼠标拖动与键盘平移；手机默认 `pan-y pinch-zoom` 保留整页滚动，显式进入“操作星图”后支持单指平移和双指缩放，退出即归还页面手势。工作台原 React Flow 画布的拖动、框选、缩放和节点移动保持有效。
- 文化与市场详情接入持续采集控制面：真实在线/中断、计划、上次尝试/成功、候选审核、平台授权矩阵、事件和错误均可见；12 秒轮询失败会使旧在线状态失效、禁用写操作并提供至少 44px 的重新连接按钮。新增候选只在服务端确认成功后清空表单，断线/拒绝时保留 URL 与标题供重试。市场页把 378 条历史证据、发布/检索时间窗和四平台样本量放在运行控制之前，实时控制默认折叠，避免用运维状态遮住证据。
- 全部页面继续使用黑白精密工具视觉；修正星图 forced-colors 分层、reduced-motion、可访问状态、候选空标题、节点阶段标签、手机触控目标与时间本地化。重新截取 10 个桌面路由和文化/市场手机关键状态，截图保存在 `web/output/playwright/`；同步 README、产品/设计契约、持续采集、架构、知识图谱、市场、部署、实机和前端质量文档，版本提升到 0.9.0。

原因：

- 用户明确要求知识库、知识图谱和爬虫两个界面更好看，知识图谱采用优秀星图/网络图体验，并让素材收集从固定的二十余条静态录入变成可持续更新、7×24 可维护的前两个项目环节。实现参考 Sigma 的大图交互分层、Kumu 的力导向/固定节点思路，以及 Airflow/Temporal 的计划、暂停、下次运行、历史和阻断可观测模式，但保持 QianCraft 的证据门、授权门和工具型信息密度，没有复制官网式外观。

验证：

- `uv run pytest -q`：53 passed；新增回归证明调度线程死亡或心跳过期时 `/api/health` 为 503。`uv run ruff check app tests scripts/probe_market_platforms.py`、`uv lock --check`、`bash -n deploy/start-zeabur.sh` 与 `git diff --check`：通过。
- `pnpm typecheck`、`pnpm lint`、`pnpm test`（5 passed）与 Vinext 五阶段 `pnpm build`：通过。`pnpm exec playwright test tests/ui/ui-quality.spec.ts`：35 passed、1 skipped；覆盖 1440×960 / 390×844 的全部 10 个路由、星图桌面真实滚轮/拖动/键盘、移动真实页面滚动/单触点平移/双触点缩放、工作台平移/节点移动、候选失败输入保留、44px、断线/首次失败恢复、授权阻断、forced-colors、axe、溢出和视觉基线。
- Playwright CLI 人工验收：桌面 10 个路由均截图，文化/市场手机关键状态复核；知识星图实际完成搜索、选点、拖动、滚轮/按钮缩放与手机显式操作模式，浏览器控制台 0 error / 0 warning。最新 `desktop-culture.png`、`desktop-market.png` 与 `mobile-culture-top.png` 已在最终 CSS/交互之后重拍并目视通过。
- 文化真实运行实际探测 4 个登记来源，4/4 可达；严格过滤没有把通用导航写入正式图谱，9 条噪声候选已拒绝，保留 1 条真实待核验候选，正式图谱仍为 22 条/32 来源。市场真实预检两次均因 `MEDIACRAWLER_LIVE_ENABLED=false` 和四平台无授权浏览器进入 blocked，没有创建假研究任务，也没有覆盖 378 条历史快照。
- 独立 Impeccable finish review 逐轮阻断真实问题：第一轮发现移动触摸、断线假在线、文化部分成功、市场证据顺序和 forced-colors；第二轮发现 44px、最终测试时序、文档和时间格式；第三轮发现调度线程失效仍回 200，以及星图自动覆盖过述。上述问题均已修正并在最终代码上重跑完整质量门；第四位全新 reviewer 只读复核健康 503、真实星图动作、候选失败输入保留、文档与 15 张最终截图，结论为 `verdict: ship`、Critical/Major 均为 0。

边界：

- 本轮完成的是“持续调度、真实状态、候选门和可操作界面”。7×24 成立的前提是 Tool API/容器单副本常驻、`data/runtime` 持久卷、平台重启策略、网络与授权登录态持续有效；当前实现不是分布式队列，也不保证每轮都有新增资料。文化候选仍须人工核验，不自动成为文化事实。
- 当前市场实时通道被明确阻断，378 只是带时间边界的历史真实快照，不能宣称四平台正在 7×24 持续产出。用户完成平台条款确认、授权和实时开关配置后，调度器才会创建严格任务。
- 0.9.0 只完成本地实现与验收，未执行发布；线上仍是 0.8.0。本轮没有越过 DesignPackage、工厂询价/首样简报和概念海报边界，没有下单、量产发布、商业艺术批准或制造/合规就绪声明。

涉及文件：

- 后端/部署：`app/collection.py`、`app/tool_api.py`、`app/workbench.py`、`tests/test_collection.py`、`.env.example`、`Dockerfile`、`deploy/nginx.conf.template`、`deploy/start-zeabur.sh`、版本与锁文件。
- 前端/测试：`web/app/collection-console.tsx`、`web/app/culture-constellation.tsx`、`web/app/node-detail.tsx`、`web/app/workbench-api.ts`、`web/app/workbench-model.ts`、`web/app/globals.css`、`web/app/variables.css`、`web/app/icon.svg`、`web/tests/ui/ui-quality.spec.ts`、`web/output/playwright/`。
- 文档：`README.md`、`PRODUCT.md`、`DESIGN.md`、`.impeccable/design.json`、`.impeccable/surfaces/web-app-workbench-tsx.md`、`docs/continuous_collection.md`、`docs/architecture.md`、`docs/knowledge_graph.md`、`docs/market_intelligence.md`、`docs/deployment_zeabur.md`、`docs/real_machine_test.md`、`docs/frontend_quality_workflow.md`、`WORKFLOW.md`。

### 2026-08-29｜0.8.3｜官方前端质量门、无障碍硬化与自动视觉回归

变更：

- 按用户要求在线调研高质量前端工作流，只采用 W3C WCAG 2.2、React Flow、Playwright、web.dev 与 Apple HIG 的官方/第一方资料，把结论整理为 `docs/frontend_quality_workflow.md`。同时通过官方 Skill Installer 安装用户本地 curated `playwright` Skill；安装器明确它从下一轮任务起可用，本轮没有伪装成已调用该 Skill，也没有复制外部网站视觉。
- 为全部可拖拽文化/市场证据增加可见“添加到画布”按钮和中文 `role=status` 反馈，共享与 drop 相同的节点创建逻辑，满足不依赖拖拽的点击/键盘路径。React Flow 的选择、移动、取消和 live announcement 改为中文；工作台补唯一隐藏 `h1`，toast 区分 status/alert，连线配置和回调稳定化，七类自定义节点 memoized。
- Culture Graph、Workspace 与 Human Decision Studio 统一为有名称/描述的 modal 语义，补初始焦点、Tab 焦点圈、Escape 关闭和触发器焦点归还；可滚动文化详情可由键盘进入。修复文化记录索引按钮内嵌链接的 nested-interactive DOM，并把 Decision Studio 平台/产品形态选中态和市场/策略次级文字收回黑白高对比。
- 移除全局 `0.01ms` reduced-motion 清除方式：JS 画布定位在减少动态时直接归零，running/loading 使用静态替代，工作台/Dock/Inspector 只关闭相关过渡。增加 `prefers-contrast` 与 Windows forced-colors 规则；手机表单为至少 16px，新增证据按钮为 44×44px。非首屏图片使用 lazy/async，主图异步解码并保持高优先级。
- 引入 `@playwright/test` 与 `@axe-core/playwright`，新增 Windows Chromium 桌面 1440×960、手机 390×844 两项目。28 项门覆盖 `/` 与九个节点详情的 axe A/AA/2.2 AA、唯一 `h1`、破图/alt、文档/主区溢出、手机 44px、证据输入等价、中文画布语义、三类弹层焦点、桌面指针平移、桌面/手机节点键盘移动、forced-colors 与四张像素基线；`pnpm quality` 串联 typecheck、lint、单元、UI 与 build。
- 同步更新 `PRODUCT.md`、`DESIGN.md`、Impeccable surface brief/机器设计契约、标准命令、目录职责、完成定义和当前状态；前端版本提升到 0.8.3。Playwright 报告/结果目录加入 Git 与 ESLint 排除，Vite watcher 忽略测试产物和快照目录，避免报告生成触发开发服务器无意义重载。

原因：

- 用户要求继续检索优秀前端工作流、Skill 与实践，并实际使用它们把当前黑白工具界面提升到可持续的高完成度。0.8.2 已证明页面在两个核心视口下外观成立，但仍缺少每次改动都能重跑的语义、交互和视觉质量门；本轮因此不再凭感觉加装饰，而是把“工具性、直接操控、黑白克制、跨端可完成、焦点可逆”变成可执行约束。

验证：

- `pnpm typecheck`、ESLint、Workbench TypeScript 5/5、Playwright 28/28 与 Vinext 五阶段 production build 通过；`.impeccable/design.json` 经 JSON 解析，`git diff --check` 通过。
- Playwright 最终对 10 个路由 × 2 个项目全部通过 axe A/AA/2.2 AA 规则、唯一 `h1`、破图 0、缺失 alt 0、文档/主区横向溢出 0；390px 可见主要触控目标小于 44px 为 0。三类 modal 的 axe、焦点圈、Escape 与焦点归还通过，桌面指针平移、两项目节点键盘移动与 forced-colors 焦点通过。
- 自动门第一次真实发现并阻断了选中市场项、Culture 索引 nested-interactive、Workspace form/dialog role、移动图谱滚动区与 Decision Studio 选中态对比问题；逐项修复后才形成最终 28/28，没有禁用 axe 规则或隐藏控件绕过失败。
- 四张 Windows Chromium 基线（工作台/Brief × 桌面/手机）已逐张人工目视；系统 chrome 只见白、冷灰、石墨和黑，工作台保持高密度工具结构，手机保留单任务视野而不是机械缩小桌面多栏。
- 应用内真实浏览器最终在 1440×960 复核：6 个 draggable 证据对应 6 个添加按钮，点击后节点由 9→10；主键拖动空白画布使视口从 `translate(-199.976px, 125.931px) scale(0.98)` 变为 `translate(-349.976px, 0.930732px) scale(0.98)`；Culture Graph、Workspace 与 Human Decision Studio 均打开可见、焦点进入内部、Escape 关闭并归还各自触发器。
- 本轮未修改 Python、API、文化/市场数据或研究链路，因此没有重复 Python 46/46、ruff、外部平台探针与在线引用检查；这些仍按既有基线记录，不冒充本轮重跑。

边界：

- axe 只能自动发现部分无障碍问题，28/28 不是 WCAG 认证；真实屏幕阅读器、残障用户、真实触屏设备与大规模图谱性能仍需专项验证。移动自动化覆盖节点键盘移动和 44px，单指画布平移沿用 0.8.2 应用内浏览器真实手势通过证据。
- 像素快照固定 Windows Chromium、字体与演示工作区；其他操作系统的抗锯齿差异不能直接覆盖基线。视觉更新必须先人工查看，再使用 `pnpm test:ui:update`。
- 本轮是本地前端、测试与设计契约更新，没有部署 0.8.3；当前受保护线上实例仍为 0.8.0，不能写成线上发布或认证后远端复验。用户本地安装的 `playwright` Skill 也不属于仓库交付物。
- 未修改 22 条文化事实、378 条历史市场快照、机会评分、Workspace Schema、DesignPackage、概念图与海报内容；仍止于概念视觉、工厂询价/首样简报和概念海报，不授权生产发布、工厂下单、商业图稿批准或制造/合规就绪声明。

涉及文件：

- `web/app/workbench.tsx`、`web/app/workbench-nodes.tsx`、`web/app/decision-studio.tsx`、`web/app/node-detail.tsx`、`web/app/globals.css`
- `web/package.json`、`web/pnpm-lock.yaml`、`web/playwright.config.ts`、`web/vite.config.ts`、`web/.gitignore`
- `web/tests/ui/ui-quality.spec.ts`、`web/tests/ui/ui-quality.spec.ts-snapshots/`
- `docs/frontend_quality_workflow.md`、`PRODUCT.md`、`DESIGN.md`
- `.impeccable/design.json`、`.impeccable/surfaces/web-app-workbench-tsx.md`、`WORKFLOW.md`

### 2026-08-29｜0.8.2｜全页面截图审计、可拖动画布与深层黑白收口

变更：

- 将 React Flow 空白画布从“主键拖动框选、仅中/右键平移”改为主键/单指直接平移；`Shift + 拖动` 继续承担框选，滚轮/捏合继续缩放，节点拖动仍只移动节点。画布增加可读交互说明和 grab/grabbing 反馈，没有改变 9 个节点、10 条边、Workspace Schema 或保存逻辑。
- 修复 390px Workspace 菜单从 `x=-34` 越出屏幕的问题，菜单现稳定落在 `x=56…348`；React Flow 缩放控制、详情保存/下载/筛选/操作、运行信息和方法说明等主要手机控件统一到至少 44px。
- 逐页深入到内部滚动容器后，修复 Poster 长工厂阶段值造成的 375→394px 横向溢出，并清除首屏之外残留的绿色标签/引用边线、深蓝海报拆解卡、红色步骤点、偏蓝页脚文字以及旧加载/通知状态色。系统 chrome 全部回到白、冷灰、石墨和黑；产品/证据/概念/海报栅格图继续按内容色例外保留来源颜色。
- 为工作台与全部 9 个节点详情分别保存桌面/手机首屏和详情底部截图，并补充 Workspace、阶段菜单、Dock、Inspector、Decision Studio 与画布拖动后的关键状态，共 48 张最终验收图；`.impeccable/review/full-audit-082/README.md` 提供逐页索引、缺陷、实机数值、验证和边界。
- 同步更新 `PRODUCT.md`、`DESIGN.md`、Impeccable surface brief 与机器设计契约，明确直接操控手势、移动触控范围与“内容色不等于系统色”的长期规则。

勘误：

- 0.8.1 日志中的“可见系统 chrome 无彩色值”只覆盖当时抽样的首屏视口，没有审计 9 个详情页的完整内部滚动范围，因此不能等同于全页面无彩。本条保留原日志不改写，并记录 0.8.2 实际发现、修复和重新验证的深层遗留色。

原因：

- 用户要求把所有页面截图后重新判断是否真正达到黑白、克制、类似 Apple 精度但仍为高密度工具的目标，并明确指出工作台画板应可拖动。此次因此从首屏审美扩展到完整路由、内部滚动、实际手势、移动触点、覆盖层焦点和错误/加载状态，而不是只再调一轮颜色。

验证：

- `pnpm test` 5/5、`pnpm typecheck`、ESLint、Vinext 五阶段 production build 与 `git diff --check` 通过；`.impeccable/design.json` 另经 JSON 解析验证。本轮没有改 Python、API、文化/市场数据或研究链路，因此没有重复 Python 46/46 和外部平台探针。
- 应用内浏览器在 1440×960 与 390×844 实测 `/`、`culture`、`market`、`strategy`、`brief`、`visual`、`concept-a/b/c`、`poster`：10/10 桌面页面与 10/10 手机页面均为破图 0、内部 `scrollWidth === clientWidth`、全滚动范围彩色系统 chrome 0。手机主要 `button/select/summary/detail-download` 小于 44px 的可操作项为 0；React Flow attribution 与正文内联引用按内联目标例外保留紧凑尺寸。
- 桌面画布实际从 `translate(20px, 210px) scale(0.82)` 拖到 `translate(180px, 165px) scale(0.82)`，Zoom In 到 `0.984`；“交付”阶段能选中 `poster`。手机空白画布平移与节点拖动分别成功，节点双击进入 `/nodes/brief?workspace=guizhou-miao-demo`，移动阶段菜单选“交付”后自动关闭并选中 `poster`。
- 手机 Dock 与 Inspector 均可用 Escape 关闭，焦点分别归还“证据库”和 `brief` 节点；Decision Studio 的 Escape 关闭后焦点归还“人工决策”。Workspace 菜单 4 个控件均为 44px，且不再裁切。
- 48 张最终截图已人工目视抽查所有首屏、全部底部与关键工作台状态；文化图谱关系网格是实际关系画布的既定例外，不授权装饰网格扩散。

边界：

- 本轮是本地前端、设计契约与验收证据更新，没有部署 0.8.2；当前受保护线上实例仍是 0.8.0，不能把本地验收写成线上发布或认证后远端复验。
- 未修改文化事实、378 条历史市场快照、机会评分、API、Workspace 数据、DesignPackage、概念图或海报内容。来源图片保留色彩仅属于内容例外，不允许彩色系统 chrome 回流。
- 当前产物仍只用于概念展示、DesignPackage、工厂询价/首样简报与概念海报；未授权生产发布、工厂下单、商业图稿批准或制造/合规就绪声明。

涉及文件：

- `web/app/workbench.tsx`、`web/app/globals.css`
- `PRODUCT.md`、`DESIGN.md`、`.impeccable/design.json`、`.impeccable/surfaces/web-app-workbench-tsx.md`
- `.impeccable/review/full-audit-082/README.md`、`.impeccable/review/full-audit-082/before/`、`.impeccable/review/full-audit-082/after/`、`WORKFLOW.md`

### 2026-08-29｜0.8.1｜黑白精密工具界面重构

变更：

- 将工作台从暖纸、米色与蓝/靛蓝交互色全面重构为用户钉定的 `Monochrome Precision Instrument`（Operate mode，方向种子 `a403e052`）：白色承担工作面、冷中性灰承担层级、石墨承担正文、纯黑承担选中态和唯一主动作。桌面命令栏调整为 60px，工具轨调整为 56px，Dock/Inspector 稳定为 260px/336px；节点选中只改变黑色对比与 keyline，不改变横条几何。原始产品、证据和概念图片可以保留来源色，界面 chrome、焦点与状态结构保持无彩色。
- 把同一黑白视觉语言覆盖到工作台、工具 Dock、Inspector、React Flow 节点/连线/小地图、Human Decision Studio、九类节点详情、文化图谱、市场/策略/任务书/视觉/概念/海报状态和浏览器表面；字体改为 system/SF-like/Noto Sans SC 回退，使用细中性边线、克制语义圆角和仅限覆盖层的低强度阴影。文化图谱的关系网格因真实关系画布保留，不扩散为装饰背景。
- 修复终审指出的三项移动/动作层级问题：390px 顶栏增加 72×56 当前阶段选择器和右上 44×44 黑色 Run；工具轨固定 56px且所有工具按钮为 44×44；Decision Studio 将“恢复系统建议/取消”按内容宽度分组，黑色保存保持唯一主动作，手机端保存为整行 44px、两个次动作并列为 44px。
- 将长期偏好和已 ship 的设计系统同步写入 `PRODUCT.md`、`DESIGN.md`、Impeccable surface brief 与内嵌布局契约；重拍桌面/手机工作台、阶段菜单、Decision Studio 和节点详情验收图。没有把界面改成营销官网，也没有删除任何操作、证据、引用或失败边界。

原因：

- 用户明确否定原米色/蓝色配色，要求采用类似 Apple 的黑白精确感，但同时强调这是高密度工具而不是官网。此次因此只借用克制、留白、字重和材质精度，不引入营销首屏、巨幅标语、产品展示叙事或装饰动画。

验证：

- `pnpm test` 5/5、`pnpm typecheck`、ESLint 与 Vinext 五阶段 production build 通过；production server bundle 包含方向契约 `a403e052`。本轮没有改 Python、API、文化/市场数据或研究链路，因此未重复执行 Python 46/46 与外部平台探针。
- 使用应用内浏览器复核 1440×960 与 390×844 的工作台、Decision Studio、Brief 详情；全部 `document.scrollWidth === clientWidth`。可见颜色审计在这些视图均为 0 个彩色系统 chrome；移动端阶段入口为 72×56、Run 为 44×44、工具轨为 56px、六个轨道按钮均为 44×44、阶段菜单项均为 44px，决策页主/次动作分别为 370×44 与 181×44。
- Impeccable 检测器仅报告一项 advisory：Culture Graph 的网格背景；该处是实际关系画布，按 craft-floor 例外保留。独立 finish reviewer 首轮提出三项修复，复拍后逐项由 0/1 提升为 1/1，最终 disposition 为 `ship`。
- `git diff --check` 无空白错误，仅显示工作树现有 LF/CRLF 规范化提示；桌面与手机最终截图均非空且已人工目视确认。

边界：

- 本轮是本地前端与设计文档更新，没有部署 0.8.1；当前受保护线上实例仍是 0.8.0，不能把本地视觉验收写成线上发布或认证后远端复验。
- 文化事实、市场缓存口径、机会评分、API 行为、Workspace 数据、DesignPackage 与海报内容均未改变；来源图片保留自身颜色不等于允许彩色 chrome 回流。
- 当前尺寸、BOM、DesignPackage 与海报仍只用于概念展示、工厂报价和首样沟通；未授权生产发布、工厂下单、商业图稿批准或制造/合规就绪声明。

涉及文件：

- `web/app/variables.css`、`web/app/globals.css`、`web/app/layout.tsx`、`web/app/workbench.tsx`、`web/app/decision-studio.tsx`
- `PRODUCT.md`、`DESIGN.md`、`.impeccable/design.json`、`.impeccable/surfaces/web-app-workbench-tsx.md`、`.impeccable/review/desktop.png`、`.impeccable/review/desktop-decision.png`、`.impeccable/review/desktop-detail.png`
- `.impeccable/review/mobile.png`、`.impeccable/review/mobile-phase.png`、`.impeccable/review/mobile-decision.png`、`.impeccable/review/mobile-detail.png`、`WORKFLOW.md`

### 2026-08-29｜0.8.0｜真实运行闭环、后台续接与全链路功能验收

变更：

- 全面审计工作台顶部动作、九个节点页、Inspector、API 路由、研究/设计/海报落盘与引用资产；删除 Culture/Market/Strategy 通过重读静态 JSON 假装本轮成功的路径。三个研究节点现在统一启动严格服务端任务，返回 202 与持久化任务号，由前端轮询；刷新页面可续接同一任务，API 重启会把未完成轮次标为 interrupted。
- 将严格研究与 Design Agent 解耦：研究流水线只写 Culture/Market/Strategy、Visual Reference Pack、DesignerHandoff、热度榜与 RunManifest；无论下游设计是否支持新机会，四平台状态都会先完整保存。只有三个研究组件和 xhs/dy/bili/wb 全部为本轮 live 才能晋级，失败轮次只写审计，不回写旧工作区。
- 把运行态从仓库基线迁到 `data/runtime/workbench/` 与 `data/runtime/tool_workspace/`；每轮研究使用隔离 raw/derived/outputs，非正式平台探针使用独立目录，不再覆盖 canonical 快照。MediaCrawler 到达时限后只在已有至少 5 条有效落盘记录时保留“部分 live”，否则保持 unavailable。
- Brief 运行实际从当前 DecisionProfile 重建 DesignerHandoff、核对 SHA、生成 DesignPackage/Markdown/RenderManifest 与 1800×2400 海报并回写节点；Poster 运行实际重新渲染服务端 PNG。自动选案只在已有真实产品生成器的候选中选择，人工点选无生成器方向仍报错。Concept 无图像 provider 时保留上次成功图，并显式标明“本轮未生成”。
- 前端增加真实任务监视器、刷新续接、重复提交阻断、严格失败平台回传和失败后的 Bootstrap 状态恢复；研究失败后节点不再永久停留 running。九个详情页、设计包/资产路由与同源 API 代理继续可独立操作。版本统一提升到 0.8.0。

原因：

- 用户明确要求逐项检查“是否真实可用”，要求点击后实际生成、自动回调、全自动爬取并打通所有链路，而不是使用兜底、旧缓存或展示状态伪装成完成。本轮因此把验收标准从视觉可达提升为真实副作用、持久化、失败语义和可恢复性。

验证：

- 环境探针确认 Python 3.13.9、DeepSeek API、`deepseek-v4-flash`、LightRAG/GPT Researcher/MediaCrawler 运行时可达，密钥未回显。四平台独立实机探针实际得到 xhs live/20、bili live/20、wb live/16；dy 本轮无内容产物并使用 14 条历史 cache，因此探针未伪报 4/4 成功。
- 网页先后实际发起三次严格任务。最终修复轮 `20260828T202303Z-2bae17ff` 用 9 分 41 秒完成：culture/strategist live、market cache、xhs/dy/bili/wb unavailable，返回 `failed_no_fallback`；隔离目录保存 8 项研究产物、四平台详情与 `strict_result.json`，不含 DesignPackage，当前工作区仍绑定原已核验基线。页面刷新续接同一任务，终态监视器正确显示失败，三个研究节点恢复而非卡住。
- 隔离 HTTP 功能验收实际完成 New/Rename/Save、Decision v2、Brief v3、Design Agent、Concept 复制/重生成 warning 与 Poster 渲染；正式工作区的设计运行 `20260828T201228Z-e646561b` 选择 OPP-006 并保存 DesignPackage，服务端海报为 1800×2400、305,202 字节。研究节点普通 POST 返回 409，证明旧文件不能冒充本轮成功。
- 九个详情页逐页打开，文化/市场/策略/任务书/视觉/A/B/C/海报引用数为 28/39/15/7/8/8/8/8/8，合计 129、缺失 0；无破图、无横向溢出。数据层 454 个唯一外链中 442 个直接可达，12 个受目标站连接/防护影响但经官方索引复核为真实页面。
- `uv run pytest` 46/46、`uv run ruff check app tests scripts/probe_market_platforms.py`、Workbench TypeScript 5/5、TypeScript no-emit、ESLint、Vinext 五阶段 production build 与 `git diff --check` 通过。桌面九页及 390×844 的 Brief/Concept/Poster/主工作台复核无页面横向溢出。
- 0.8.0 隔离发布包 `.zeabur-stage-080` 为 74 个文件、19,435,606 字节，不包含 `api.txt`、环境文件、Cookies、上游源码、测试或本地运行态；敏感文件名与长 `sk-` 模式均为 0 命中。首次部署 `6a91f23f13d3d467215e790c` 完成构建但因上传过程把 `start-zeabur.sh` 转成 CRLF 而无法启动；先用 `6a91f39a13d3d467215e7928` 恢复 0.7.3 服务，再在 Docker 构建时规范化脚本行尾。最终部署 `6a91f49bac2577a93d22048d` 为 `RUNNING`，日志确认 `qiancraft-0.8.0`、Tool API 与 Vinext 均启动，公网 `/healthz` 为 200、匿名 `/` 为 401。

边界：

- 最终严格任务没有获得四平台本轮 live，因此没有可晋级的新实时市场集；378 条记录仍是带时间边界的历史真实快照。平台会话、风控、限流和当次搜索产物会变化，一次授权不等于永久成功。
- 独立 Images API 仍未配置，DeepSeek 图片端点实测 404；A/B/C 旧项目资产可展示，但本轮不把它们标成新生成。精简 Zeabur 镜像不包含三上游运行时，云端严格任务会在预检阻断；完整实爬需在用户授权的本机环境执行。
- DesignPackage、尺寸、BOM 与海报仍只用于概念展示、工厂报价和首样沟通，`mass_production_ready=false`；本轮未授权生产发布、工厂订单、商业图稿批准或制造/合规就绪声明。

涉及文件：

- `.gitignore`、`Dockerfile`、`README.md`、`WORKFLOW.md`、`pyproject.toml`、`uv.lock`、`app/__init__.py`
- `app/pipeline.py`、`app/tool_api.py`、`app/workbench.py`、`app/adapters/media_crawler_adapter.py`、`app/designer/agent.py`
- `scripts/probe_market_platforms.py`、`tests/test_demo_pipeline.py`、`tests/test_tool_api.py`、`tests/test_workbench.py`
- `web/app/workbench.tsx`、`web/app/node-detail.tsx`、`web/app/workbench-api.ts`、`web/app/workbench-model.ts`、`web/app/globals.css`、`web/app/variables.css`、`web/vite.config.ts`、`web/package.json`
- `data/market/derived/latest.json`、`data/market/derived/product_form_hotness.json`、`data/workbench/workspaces/guizhou-miao-demo.json`、`docs/real_machine_test.md`、`docs/deployment_zeabur.md`

### 2026-08-29｜0.7.3｜稳定横条节点、Inspector 渐进披露与上线

变更：

- 把九个 React Flow 实例从“选中后展开卡片”改为固定横向索引条：删除节点内部摘要、统计、预览和三按钮 footer 的画布渲染，Rest / Selected 使用同一几何尺寸与位置；选择只切换 Indigo keyline、3% 纸面色差、状态手柄和 Inspector 绑定。
- 把被移出的能力收回到正确层级：Inspector“操作”新增带 Lucide 图标的“打开完整页面”，保留运行节点、从此运行、方案采用/复制/重生成和海报导出；节点双击深链与九类独立展示页不变。节点增加可访问名称和 `aria-current="step"`，状态仍同时使用文字与颜色。
- 同步修订设计宪法、Impeccable 机器规范、工作台简报和内嵌方向契约；删除非画布节点详情页遗留的装饰性双轴网格，真实 React Flow 画布点阵不受影响。版本统一升级为 0.7.3。

原因：

- 用户在实机页面中指出选中节点会从横条骤变为方块，破坏关系线阅读和工具感，并要求继续消除“太 AI / 太 Demo”的视觉特征。本轮采用“画布只表达拓扑与状态，Inspector 承担详情与操作”的渐进披露边界。

验证：

- 1440 × 960 实测九个节点的渲染高度唯一值为 62px；从 Design Brief 切换到 Visual 节点后，原节点与新选中节点仍分别为 62px，全部 `transform:none`，Inspector 标题正确绑定，页面无横向溢出，“打开完整页面”可见。
- 通过 Inspector 实际打开 `/nodes/visual?workspace=guizhou-miao-demo`，标题为“概念方向 A / B / C”，页面含 8 条外部引用链接且无横向溢出；Human Decision Studio 实测为 1408 × 876、7 个阶段、无页面横向溢出。390 × 844 下九个节点继续保持 62px 横条，文档无横向溢出。
- `uv run pytest -q` 37/37、`uv run ruff check app tests`、`pnpm test` 5/5、`pnpm typecheck`、`pnpm lint`、Vinext 五阶段 `pnpm build`、`uv lock --check`、DTCG JSON 解析和 `git diff --check` 通过。Impeccable 单次检测指出非画布详情页遗留装饰网格；对应规则已删除。
- 隔离发布副本 `.zeabur-stage-073` 为 72 个文件、19,313,856 字节，敏感文件名与长 `sk-` 模式均为 0 命中。首次上传未建立部署记录，同一已扫描副本重试成功；Zeabur 部署 `6a91df9a13d3d467215e7737` 为 `RUNNING`，构建日志确认 `qiancraft-0.7.3`，公网 `/healthz` 为 200、匿名 `/` 为 401。

边界：

- 本轮没有修改 22 条文化事实、32 个来源、378 条历史平台快照、机会评分、DesignPackage、文化风险或 `reference_only` 像素边界；只调整前端信息分层、节点语义和版本/部署文档。项目仍停在概念视觉、工厂询价/首样简报与展示海报阶段，不代表商业图稿批准、工厂下单、量产工程或合规就绪。
- 当前会话没有站点 Basic Auth 凭证，因此没有声称完成 0.7.3 认证后公网页面/API 复验；完整画布、Inspector、详情页、人工决策和响应式验收来自本地真实 HTTP 服务，线上只确认远端构建、运行状态、免鉴权健康检查与匿名门禁。
- 独立图像自动化服务仍未配置；已有 A/B/C 项目视觉可展示，重新生成继续诚实提示需要独立服务。

涉及文件：

- `web/app/workbench-nodes.tsx`、`web/app/workbench.tsx`、`web/app/globals.css`、`web/app/layout.tsx`、`web/package.json`
- `DESIGN.md`、`.impeccable/design.json`、`.impeccable/workbench-brief.md`
- `README.md`、`docs/real_machine_test.md`、`docs/deployment_zeabur.md`
- `app/__init__.py`、`pyproject.toml`、`uv.lock`、`qiancraft.egg-info/PKG-INFO`、`WORKFLOW.md`

### 2026-08-29｜0.7.2｜全页面信息降噪、移动端修复与逐页实机收口

变更：

- 按工作台、人工决策与九个节点详情逐页实图检查，删除 `Knowledge Center`、`CULTURE DNA`、`MARKET RADAR`、`INSPECTOR`、`STATUS`、`SUMMARY`、`NODE ID` 等装饰性中英重复或机器眉题；节点操作、Inspector 七个页签、证据/资产/历史 Dock、生成动作和加载态统一为单一中文表达。持久卷中旧版视觉节点摘要即使仍含 `Concept A / B / C` 或 `Images API`，展示层也会稳定归一为中文，不强行改写用户工作区 JSON。
- 重构信息层级：Inspector 只保留一次状态和一次摘要，运行 ID 从默认页脚移除；节点详情把工作区/运行编号收进“运行信息”，市场方法 JSON 收进“字段说明”，视觉服务不再默认暴露环境变量缺项。Decision Studio 删除七段重复说明与英文眉题，桌面弹窗扩大到安全边距并建立明确 dialog 层，背景 Inspector 不再穿透形成双关闭按钮。
- 完成 390px 真实布局修复：Decision Studio 从错误的 184px+内容双栏改为水平阶段条加全宽表单；文化关系图转换为双列触控卡；任务书与概念编辑器收回容器宽度；三套概念 BOM 从 900px 固定表格改为带字段标签的分组记录；海报不再在已有成品图上重复叠标题。主要控件与正文提高到可读字号，11px 以下只剩画布归因等不可替代内容。
- 保留 Parchment / Warm Sand / Linen / Charcoal 的暖纸仪器台账视觉，不增加渐变、装饰卡片或虚构缩略图。版本统一升级为 0.7.2，并同步设计宪法、Impeccable 机器规范、工作台简报、排版专题、README、实机与部署文档。

原因：

- 用户在真实页面中指出界面仍存在文字过多、不必要中英对照、小字、弹层层级和“太 AI / 太 Demo”的问题，并要求逐页用实图模型检查。本轮以“单一标签、任务优先、机器信息渐进披露、手机真实可操作”为收口标准，不再仅凭组件代码判断完成。

验证：

- `uv run pytest -q` 37/37、`uv run ruff check app tests`、`pnpm test` 5/5、`pnpm typecheck`、`pnpm lint`、Vinext 五阶段 `pnpm build`、`uv lock --check`、JSON 解析与 `git diff --check` 通过。
- 1440 × 900 实测工作台、人工决策和文化/市场/策略/任务书/视觉/A/B/C/海报九个详情页；九页均无视口外内容，人工决策 dialog 为 1408 × 876 且背景 Inspector 控件不可穿透。390 × 844 再测同一范围，九页文档 `scrollWidth` 均为 390px；文化图谱、任务书编辑器、三套 BOM 和海报容器都在可视宽度内，Decision Studio 内容宽度为完整 390px。
- Impeccable 最终检测无阻断项；唯一 advisory 是 `globals.css` 中的双轴网格背景，该网格仅用于实际 React Flow/关系画布，符合检测器给出的保留边界。
- 隔离发布副本为 71 个文件、8,893,000 字节，敏感文件名与长 `sk-` 模式均为 0 命中；只在副本中压缩 6 张发布 PNG，源高清资产未修改。Zeabur 部署 `6a91d9ffdb37f2e6ddbc152e` 为 `RUNNING`，远端确认 `qiancraft-0.7.2` 与 Vinext 构建完成；公网 `/healthz` 为 200，匿名 `/` 为 401。

边界：

- 本轮没有修改 22 条文化事实、32 个来源、378 条历史平台快照、机会评分、文化风险或 `reference_only` 像素边界；只调整界面表达与默认视觉节点摘要。项目仍停在概念视觉、工厂询价/首样简报与展示海报阶段，不代表商业图稿批准、工厂下单、量产工程或合规就绪。
- 当前会话没有站点 Basic Auth 凭证，因此没有声称完成 0.7.2 认证后公网页面/API 复验；完整页面、交互与响应式验收来自本地真实 HTTP 服务，线上只确认远端构建、运行状态、免鉴权健康检查与匿名门禁。
- 独立图像自动化服务仍未配置；已有 A/B/C 项目视觉可展示，重新生成继续诚实提示需要独立服务，不把旧图或项目内置资产冒充为一次新调用。

涉及文件：

- `web/app/workbench.tsx`、`web/app/workbench-nodes.tsx`、`web/app/workbench-model.ts`、`web/app/decision-studio.tsx`、`web/app/node-detail.tsx`、`web/app/globals.css`、`web/package.json`
- `app/__init__.py`、`app/workbench.py`、`data/workbench/workspaces/guizhou-miao-demo.json`
- `DESIGN.md`、`.impeccable/design.json`、`.impeccable/workbench-brief.md`、`docs/typography_system.md`
- `README.md`、`docs/real_machine_test.md`、`docs/deployment_zeabur.md`、`pyproject.toml`、`uv.lock`、`qiancraft.egg-info/PKG-INFO`、`WORKFLOW.md`

### 2026-08-29｜0.7.1｜全表面暖纸色关系锁定

变更：

- 将用户给定的 Lovable 暖纸色关系从“局部 token 覆盖”升级为完整产品色彩系统：Parchment 统一页面、顶栏、节点和主面板，Warm Sand 统一画布、工具轨、输入与次级内容面，Linen / Stone 统一两级边界，Charcoal 统一主文字与主动作；清除工作台、Human Decision Studio 和节点详情中残留的纯白操作面、冷灰 chrome 与亮蓝主控。
- Interaction Indigo 只保留在链接、选中、当前路径、图标焦点和键盘焦点；Human Decision 模式主选择和全局主动作改为 Charcoal。贵州靛青、锈色、青绿、紫罗兰以及成功/快照/警告/错误色继续只在内容身份和语义状态中使用，不扩散到全局界面。
- 新增 `lovable-faint-gray`、Indigo soft 和 Parchment glass 语义变量；`faint-text` 与 Dim Gray 共用 `#5f5f5d`，避免 9–14px 元数据使用 3.62:1 的旧浅灰。同步更新设计宪法、Impeccable 机器规范、工作台简报、排版专题、README 徽章和 0.7.1 版本。
- 更新桌面与手机最终截图，并将同一前端发布到现有 Zeabur 受保护实例；没有改变节点契约、文化图谱、市场证据、评分、Workspace、API 行为或生产前边界。

原因：

- 用户强调主体色彩搭配本身必须贴近其提供的参考系统。审计确认 0.7.0 虽已使用暖纸色外层，但内部仍混有 RICOUI 结构研究阶段留下的冷灰、纯白、亮蓝和旧深色，导致页面看起来像多套系统叠加；本轮以用户提供的明确色值和角色为唯一全局配色事实源。

验证：

- `uv run pytest -q` 37/37、`uv run ruff check app tests`、`pnpm test` 5/5、`pnpm typecheck`、`pnpm lint`、Vinext 五阶段 `pnpm build` 与 `git diff --check` 通过。
- 浏览器在 1440 × 900 复核工作台、Human Decision Studio 和 Brief 节点详情，在 390 × 844 复核同三类界面；桌面与手机 `scrollWidth` 均等于视口宽度。移动端决策模式、关闭、恢复、取消、保存六个控件以及详情页四个动作均实测为 44px。
- 核心对比度实测：Charcoal / Parchment 16.47:1、Dim Gray / Parchment 6.18:1、Dim Gray / Warm Sand 5.83:1、Indigo / Parchment 6.84:1；辅助小字不再使用旧 3.62:1 Faint Gray。
- 隔离发布副本为 87 个文件、5,694,056 字节，敏感路径与长 `sk-` 模式均为 0 命中。第一次上传在对象存储连接层被远端重置且未触发部署；同一副本第二次上传成功，部署 `6a91d1a613d3d467215e74b8` 为 `RUNNING`。公网 `/healthz` 为 200，匿名 `/` 为 401。

边界：

- 用户提供的暖纸色 token 是本轮配色事实源；RICOUI 只用于理解工具结构和信息层级，没有复制其代码、资产、文案、品牌或像素页面。Hero gradient 仍只登记，不进入当前工具界面。
- 当前会话没有站点 Basic Auth 凭证，因此没有声称完成 0.7.1 认证后公网页面/API 复验；完整 UI、响应式与交互在本地真实 HTTP 环境完成，线上只验证部署状态、免鉴权健康检查和匿名门禁。
- 本轮没有修改 22 条文化事实、378 条历史平台快照的 `cache` 口径、机会量分或 `reference_only` 像素边界。独立 Images API 仍未配置；产品继续停在概念视觉、工厂询价/首样简报与展示海报阶段，不代表商业图稿批准、工厂下单、量产工程或合规就绪。

涉及文件：

- `web/app/variables.css`、`web/app/globals.css`、`web/package.json`
- `DESIGN.md`、`.impeccable/design.json`、`.impeccable/workbench-brief.md`、`.impeccable/review/`
- `README.md`、`docs/typography_system.md`、`docs/deployment_zeabur.md`
- `app/__init__.py`、`pyproject.toml`、`uv.lock`、`qiancraft.egg-info/PKG-INFO`、`WORKFLOW.md`

### 2026-08-29｜0.7.0｜暖纸色 Creative Instrument Workbench 与全端收口

变更：

- 将展示感偏重、信息密度失衡的旧工作台重构为真正的 Creative Instrument：顶部五阶段负责链路定位，64px 工具轨按需打开证据、方案资产和节点历史，React Flow 保持主画布地位，320px Inspector 只显示当前节点上下文；默认链路仍为 9 个节点、10 条边和严格 7 类节点，没有改写业务契约。
- 七阶段 Human Decision Studio、九个节点展示页和已有独立操作全部接入新工具骨架。阶段点击聚焦节点，资产点击联动画布与 Inspector，手机端 Dock/Inspector 改为覆盖层；打开后焦点进入面板，Escape 关闭后回到原触发器。详情页四个图标动作补齐可访问名称，移动端决策模式、恢复系统建议、取消和保存入口均保留，核心触控目标至少 44px。
- 将用户提供的 Lovable 暖纸色 DTCG 令牌转成 `web/app/variables.css` 普通 CSS 变量并映射到现有组件：parchment、warm sand、linen border、stone、dim gray、charcoal、ink、interaction indigo、字体、字重、字号、间距、圆角和内阴影均有唯一来源。清除了用户粘贴片段中的重复 `@import`、HTML 实体和转义符；Hero 渐变只登记为设计令牌，没有把营销式渐变滥用到操作工作台。
- 字体契约如实区分设计意图与可交付资源：Camera Plain 保留在字体栈首位，但仓库没有冒充已打包该字体；实际中文由自托管 Noto Sans SC / Noto Serif SC 可变字体覆盖。新增 `PRODUCT.md`、`DESIGN.md`、`.impeccable/design.json`、界面简报、资产来源记录和桌面/手机成品截图，使长期产品意图、视觉宪法与代码令牌一致。
- 版本统一升级到 0.7.0。隔离 Zeabur 发布副本只含产品运行必需文件和当前证据快照；仅发布副本中的 PNG 做无尺寸变化压缩，源高清资产未改动，必要 PNG 文本/物理尺寸元数据块保留。最终副本为 86 个文件、5,589,358 字节，敏感路径与长 `sk-` 模式均为 0 命中。

原因：

- 用户连续指出旧前端“太 AI、太 Demo、太复杂”，随后进一步明确它不是官网而是工具，并要求参考高完成度工作台、`design.ricoui.com/brands` 的克制结构，以及本轮提供的暖纸色设计令牌。此次收口把这些反馈统一为“安静但不空、专业但可操作、画布优先且上下文按需出现”的产品原则。

验证：

- `uv run pytest -q` 37/37、`uv run ruff check app tests`、`pnpm test` 5/5、`pnpm typecheck`、`pnpm lint`、Vinext 五阶段 `pnpm build` 与 `git diff --check` 通过；本地九个节点展示页和九个节点 API 均为 200。
- 浏览器在 1440 × 900 实际复核工作台、Decision Studio 和节点详情，在 390 × 844 复核相同三类界面；暖纸色层级、画布比例、覆盖层、详情 Locked Context 和 A/B/C 视觉均完成目视检查。最终手机 Decision Studio 截图为 `.impeccable/review/mobile-decision-warm-final.png`。
- 390px 视口逐项测得系统建议、人工配置、关闭、恢复系统建议、取消和保存按钮高度均为 44px；详情页四个动作高度均为 44px且具有独立 `aria-label`。Decision Studio、Dock、Inspector 均完成打开聚焦、Escape 关闭和焦点归还实测；Impeccable 最终只读复核结论为 PASS。
- Zeabur 远端重新执行 Vinext 五阶段构建与 Docker 构建，安装日志确认 `qiancraft-0.7.0`；最终部署 `6a91ccc4ac2577a93d22028e` 为 `RUNNING`。公网 `/healthz` 为 200、匿名 `/` 为 401；当前会话没有站点凭证，因此未声称完成本轮认证后公网 UI/API 复验。

边界：

- RICOUI 等网站只用于观察工具结构、层级与交互节奏，没有复制其代码、品牌、资产或像素页面；本轮暖纸色令牌来自用户提供的设计系统输入。Camera Plain 没有随项目分发，Hero 渐变也没有被当作工作台默认背景。
- 0.7.0 没有改变文化图谱事实、378 条历史平台快照的 `cache` 口径、机会评分证据锁或 `reference_only` 像素边界。独立 Images API 仍未配置，Regenerate / Generate More 继续诚实显示 warning。
- 线上实例仍由共享 Basic Auth 保护；当前执行环境没有站点口令，不读取或输出 Zeabur Secret，因此认证后的 0.7.0 页面/API 需在持有凭证的会话复验。产品仍停在概念视觉、工厂询价/首样简报与展示海报阶段，不代表商业图稿批准、工厂下单、量产工程或合规就绪。

涉及文件：

- `web/app/variables.css`、`web/app/globals.css`、`web/app/layout.tsx`、`web/app/workbench.tsx`、`web/app/decision-studio.tsx`、`web/app/node-detail.tsx`、`web/app/workbench-nodes.tsx`
- `PRODUCT.md`、`DESIGN.md`、`.impeccable/`、`README.md`、`docs/typography_system.md`、`docs/architecture.md`、`docs/real_machine_test.md`、`docs/deployment_zeabur.md`
- `Dockerfile`、`.dockerignore`、`deploy/`、`app/__init__.py`、`pyproject.toml`、`uv.lock`、`web/package.json`、`WORKFLOW.md`

### 2026-08-28｜0.6.0｜七阶段人工决策与全链路可变配置

变更：

- 在原有 9 节点链路上增加 Human Decision Studio，把人工参与拆成七个可独立进入的阶段：文化记录选择、市场平台/产品形态选择、1–3 条机会组合、六维权重与文化风险扣分、目标人群/产品/价格/场景/材料意图、视觉参考/风格/画幅与概念比较、海报主题/板块/备注。顶部、知识中心、画布节点、Inspector 和九个节点详情页均可进入；深链保留 workspace 与阶段。
- Workspace 升级到 Schema 1.1，新增可版本化 `metadata.decision_profile` 与 `metadata.decision_output`。系统推荐分保持只读，人工权重在服务端归一化后生成独立 `manualScore`、维度贡献和风险扣分；文化事实、来源、市场原始互动与视觉权利状态不被人工选择覆盖。
- 新增 `POST /api/workbench/workspaces/{workspaceId}/decisions`、Decision Catalog 和完整校验。选择只允许引用 22 条文化记录、4 个平台、8 条机会、12 条视觉参考与已有概念；保存后立即刷新 Culture/Market/Strategy，Brief/Visual/Concept/Poster 标记 stale，等待用户分别运行，不会静默消费模型 API。
- 概念比较组与当前采用方向成为显式输入；概念生成只消费被选比较组。设计意图、视觉方向、海报板块与人工备注均进入下游节点展示，节点增加 `HUMAN vN` 状态提示。
- 新增专用前端 `decision-studio.tsx` 与完整响应式样式；范围滑杆同时提供精确数值输入，解决自动化与键盘难以准确编辑权重的问题。补充人工决策专题、架构、实机、部署和 README 说明，版本统一升级到 0.6.0。
- 默认工作区 JSON 写入 guided v1 基线；旧持久化工作区读取时运行兼容迁移，线上默认工作区通过原 API PUT 无损持久化为 Schema 1.1。事实文件、节点数量、连线与既有 A/B/C 视觉未被迁移改写。

原因：

- 用户指出当前知识图谱、爆款样本和量分都由系统预选，链路缺少人主动改变方向的空间，并要求每个栏目都能进行一定程度的独立优化与人工交互。本次把机器建议从“唯一答案”改为“可审计起点”，同时保留证据锁和生产前边界。

验证：

- `uv run pytest -q` 37/37、`uv run ruff check app tests`、`pnpm test` 5/5、`pnpm typecheck`、`pnpm lint`、Vinext 五阶段 `pnpm build` 与 `git diff --check` 全部通过；新增回归覆盖默认/非法 DecisionProfile、权重归一化、人工排序、下游 stale、选择切换与浏览器端量分计算。
- 在 1280×720 本地真实网页中创建隔离验收工作区并逐段实操：增加文化记录、减少平台、替换机会、输入目标人群与三类产品、增加视觉参考、改画幅/风格、切换 Concept B、缩减比较组、改海报主题/板块/备注；保存 v2 后节点显示 `HUMAN v2` 和下游 stale。随后把文化权重精确改为 35，界面总权重显示 115%，人工排序即时变化，保存 v3 后服务端归一化为 0.304348。Brief 详情页及 `?workspace=...&decision=brief` 回链复验通过；临时工作区随后删除，默认工作区未被本地验收污染。
- 本地 Bootstrap 实测为 Schema 1.1 / guided v1，Decision Catalog 为 22 条文化记录、4 个平台、8 条机会、12 条视觉参考、3 个概念。默认 A/B/C 概念资产和海报继续可读；独立 Images API 缺失时仍保持 warning。
- Zeabur 首两次 27 MB 上传在远端对象存储连接处中断；精简仅用于发布的历史快照并对展示 PNG 做无尺寸变化的索引色压缩后，最终副本为 81 个文件、9,230,275 字节，敏感路径与长 `sk-` 模式均为 0 命中。第三次上传成功，部署 `6a91a4a7db37f2e6ddbc0c40` 完成 Docker 构建并为 `RUNNING`，容器内应用版本为 0.6.0。
- 公网 `/healthz` 返回 200、匿名 `/` 返回 401。通过 Zeabur 容器回环实测线上 Bootstrap、无损 Workspace 1.1 持久化、九个节点详情 API、九个 Vinext 节点页全部为 200；Decision Catalog 数量与本地一致，非法文化 ID 决策请求返回 422。

边界：

- 人工选择是策略与设计参数，不会把推断提升为文化或市场事实；高敏感母题、具体社区许可、署名、收益与撤回机制仍需人工/社区复核。
- 独立 OpenAI-compatible Images API 仍未配置，现有 A/B/C 已审阅视觉可继续展示；Regenerate / Generate More 不会伪造新图。七阶段配置不会扩大到商业图稿批准、工厂下单、生产工程或合规就绪。
- Zeabur 仍是共享 Basic Auth 的受保护验证环境。本轮通过公网匿名门禁与容器回环完成线上代码验收，没有读取、输出或轮换站点口令；扩大多人使用前仍需用户级身份、审计、备份与口令轮换。
- 发布包只携带当前市场快照而非全部历史派生归档；本地历史证据没有删除。发布用 PNG 的原始尺寸和内容路径不变，工作区内高清源文件也未改动。

涉及文件：

- `app/workbench.py`、`app/tool_api.py`、`tests/test_workbench.py`
- `web/app/decision-studio.tsx`、`web/app/workbench.tsx`、`web/app/workbench-api.ts`、`web/app/workbench-model.ts`、`web/app/workbench-model.test.ts`、`web/app/workbench-nodes.tsx`、`web/app/node-detail.tsx`、`web/app/globals.css`
- `data/workbench/workspaces/guizhou-miao-demo.json`
- `docs/human_decision_workflow.md`、`docs/architecture.md`、`docs/real_machine_test.md`、`docs/deployment_zeabur.md`
- `README.md`、`pyproject.toml`、`app/__init__.py`、`uv.lock`、`web/package.json`、`WORKFLOW.md`

### 2026-08-28｜0.5.2｜Flipbook 式编辑排版与画布比例重构

变更：

- 调研并实测 Flipbook 官方页面在 1280 × 720 下的排版比例：首标题 40/42px、二级标题约 26.4/29.6px、正文 20/27.6px、中央提示约 23.3px、辅助说明约 12.48px；提取“大字、低密度、视觉优先、暖纸色、有限层级”原则，并针对中文证据工作台重新设计，没有复制对方品牌、资产或像素页面。
- 引入并自托管 `Noto Sans SC Variable` 与 `Noto Serif SC Variable` 5.3.0，把正文/控件和标题/关键数字分工；建立 11/12/13/14/15/16/17px 七级共享令牌，将原有 7–13px 的 184 处零散声明和 51 处字体栈统一收口，清除所有 7–10px 硬编码字号，补齐 OFL-1.1 第三方通知。
- 将界面从冷灰“工程缩略图”改为暖纸色编辑界面：品牌与面板标题使用中文衬线，正文使用中文无衬线；标准节点宽度调整为 324px、视觉类节点 356px，1280px 桌面三栏调整为 280px / 自适应 / 400px，Inspector 七个标签完整显示。
- 默认工作区视口从 0.54 改为 0.82，单节点聚焦范围改为 0.82–1.05；线上持久化 `guizhou-miao-demo` 同步迁移到 `x=20, y=210, zoom=0.82`，避免新镜像默认值被旧工作区覆盖。
- 九个详情页延续大标题、舒展正文和证据优先层级；390 × 844 下动作区、标题、元数据和产品阶段卡依序堆叠且无横向溢出。补充排版系统、架构、实机、部署、README、版本、锁文件和许可说明，并发布 0.5.2。

原因：

- 用户指出当前字体大小、比例、形式和字形严重影响观感，并要求先调研 Flipbook 再优化。代码审计确认旧样式有大量 7–10px 文字，同时默认画布 `zoom=0.54` 会继续缩小节点内容；问题来自字体、字号令牌、画布比例和信息密度共同失衡，不能靠局部放大一个标题解决。

验证：

- 本地浏览器在 1280 × 720 实际检查工作台、文化图谱、市场雷达和海报详情；默认首屏能读清策略与任务书，文化详情标题约 58px，Inspector 七标签可见。390 × 844 海报详情 `scrollWidth=390`，无横向溢出；浏览器控制台 warning/error 为 0。
- `uv run pytest` 33/33、Workbench TypeScript 3/3、`uv run ruff check app tests`、`pnpm typecheck`、`pnpm lint`、Vinext 五阶段 `pnpm build` 与 `git diff --check` 均通过；源码扫描确认不再存在 7–10px 硬编码字号。
- 精简 0.5.2 发布目录为 122 个文件、27,161,865 bytes；`.env`、`api.txt`、原始平台数据、工具运行态、Workspace 运行态和 `node_modules` 命中 0，长 `sk-` 模式命中 0。Zeabur 部署 `6a91944713d3d467215e63e3` 完成并进入 `RUNNING`。
- 公网 `/healthz` 为 200、匿名 `/` 为 401、认证首页与 API 为 200；线上 Workspace 返回 9 节点、10 边和新视口 20/210/0.82。九个节点详情 API 与九个页面全部为 200，合计解析 129 条引用、缺失 0；两份 CSS 均可加载 Noto Sans/Serif 声明，抽查 WOFF2 为 200。最终运行日志 102 行中记录 83 条 200、1 条预期匿名 401，未发现 crit/fatal/traceback/exception 或 5xx。

边界：

- Flipbook 只作为公开设计原则与比例研究对象，不是运行依赖；QianCraft 没有使用其名称作为产品品牌，也没有复制其代码、图像、布局像素或视觉资产。
- Noto 字体由 Fontsource 按 `unicode-range` 自托管并遵循 SIL OFL-1.1；这解决加载、中文覆盖与层级一致性，不等于所有操作系统或浏览器会产生完全相同的字形栅格。
- 工作台仍是面向桌面的空间画布；手机端保证独立节点详情可阅读和操作，不承诺在 390px 内同时展开证据中心、无限画布和 Inspector 三栏。
- 本轮只调整前端呈现、默认视口和相关文档，没有改变文化事实、市场缓存口径、机会评分或设计生产边界；仍停在概念视觉、工厂询价/首样简报和展示海报阶段。

涉及文件：

- `web/app/globals.css`、`web/app/layout.tsx`、`web/app/workbench.tsx`、`web/package.json`、`web/pnpm-lock.yaml`
- `app/workbench.py`、`data/workbench/workspaces/guizhou-miao-demo.json`
- `README.md`、`THIRD_PARTY_NOTICES.md`、`docs/typography_system.md`、`docs/architecture.md`、`docs/deployment_zeabur.md`、`docs/real_machine_test.md`、`WORKFLOW.md`
- `pyproject.toml`、`uv.lock`、`app/__init__.py`、`qiancraft.egg-info/PKG-INFO`

### 2026-08-28｜0.5.1｜九节点证据展示页与 Zeabur 受保护上线

变更：

- 为默认 9 个节点实例增加统一动态路由 `/nodes/{nodeId}?workspace={workspaceId}`；节点卡“查看展示页”、画布双击与详情页相邻节点导航均保留当前工作区。文化、市场、策略、任务书、视觉、A/B/C 概念和海报分别使用专用信息结构，而不是复用一个通用 JSON 面板。
- 新增节点详情 API 与证据目录：解析文化 `Cxxx`、市场 `Mxxx`、视觉参考 `Vxxx` 和平台历史记录 `MPL-xxx`，返回发布/检索日期、发布者、权利状态、支持项、原始链接和缺失引用审计；修复公开核验来源编号被派生平台记录覆盖的问题，并把当前设计实际使用的 `V001 reference_only` 纳入视觉、概念与海报页。
- 完成详情页产品化视觉：文化关系板与 22 条记录索引、四平台 378 条历史样本 KPI/Top 10/代表原记录、八条机会与六维量分、可编辑任务书、A/B/C 视觉提示与独立入口、概念成品/BOM/文化转译、可编辑完整海报和统一引用台账；页面提供 Run、Run from here、保存、复制/激活/重生成、DesignPackage 与详情 JSON 导出等独立操作。
- 增加 Zeabur 单容器生产拓扑：Nginx 统一 Basic Auth 与反向代理，Vinext、Tool API 只监听容器回环地址，`/healthz` 免鉴权；运行工作区和设计工具目录写入 `/app/data/runtime` 持久卷，密钥只由服务端环境变量注入。修复 CLI 跳过点号目录导致的 Sites hosting 清单缺失，以及自定义 Nginx worker 用户与 0600 口令哈希文件不一致两项远端构建/启动差异。
- 将正式站点元数据指向 `https://qiancraft-studio-2026.zeabur.app`，README 增加受保护在线实例、九节点展示页和公开 URL 配置说明；同步补齐架构、Zeabur 部署、实机验收与本工作流文档。

原因：

- 用户要求每一个工作流节点都能进入对应的专业展示页，知识图谱、爆款原记录、机会量分和设计结果均可独立查看/操作并提供原始引用，随后把完整产品优化上线，而不是只交付本地画布或断开后端的静态页面。

验证：

- `uv run pytest` 33/33 通过；新增回归覆盖 22 条文化记录、378 条市场样本、八条机会、引用全部解析、`M007` 保持公开市场来源类型及 `V001` 进入设计视觉证据。
- Workbench TypeScript 测试 3/3、`pnpm typecheck`、ESLint 和 Vinext 五阶段 production build 全部通过；`uv run ruff check app tests` 与 `git diff --check` 通过。
- 本地 API 逐一请求 9 个详情接口：Culture / Market / Strategy 分别解析 28 / 39 / 15 条引用，Brief 为 7 条，Visual / A / B / C / Poster 各为 8 条，缺失均为 0；本地 production 页面状态为 200。浏览器实际检查工作台节点入口以及文化、市场、海报代表页，文字层级、关系/榜单/海报、编辑器和引用内容均正常显示。
- Zeabur Linux 构建器完成 Python `qiancraft-0.5.1` 安装、Vinext 五阶段构建、441 MB 生产镜像和最终部署 `6a91567913d3d467215e4e7f`；服务状态为 `RUNNING`。
- 公网验收：`/healthz` 为 200，匿名 `/` 为 401，认证 `/` 与 `/api/health` 为 200；Bootstrap 返回 `guizhou-miao-demo`、9 节点、10 边、7 类型和 378 条市场样本。9 个页面与 9 个详情 API 全部为 200，引用缺失均为 0；Concept A/B/C 与海报四项正式资产全部为 200；独立 POST Culture 节点运行后状态为 `success`。
- 精简发布目录共 148 个文件，未包含 `.env`、`api.txt`，长 API Key 与站点口令模式扫描命中 0；远端运行日志中的实际验收请求均为 200，未见最终部署的 500/crit。

边界：

- 四平台 115/14/101/148、合计 378 条仍是带时间边界的历史真实快照，线上明确显示 `cache`，本轮没有重新登录或访问平台，不能解释为当前全网实时趋势。
- DeepSeek 文本 API 已配置在服务端，但独立 Images API 仍未配置；现有 A/B/C 项目资产可展示，Regenerate / Generate More 会如实显示 warning，不伪造新图像调用。
- `reference_only` 馆藏页只用于研究引用，原始链接和权利说明不等于商品图稿授权；任何社区确认、文化授权、材料结构实测、DFM 与法规测试仍需后续完成。
- 在线实例是共享 Basic Auth 的受保护产品验证环境，不是正式多用户账号系统；对外扩大使用前仍需补用户级权限、审计、备份、口令轮换和更细粒度限流。
- 本轮停在概念视觉、工厂询价/首样简报和展示海报，没有授权工厂下单、量产发布、商业美术定稿或制造/合规就绪声明。

涉及文件：

- `app/workbench.py`、`app/tool_api.py`、`tests/test_workbench.py`
- `web/app/node-detail.tsx`、`web/app/nodes/[nodeId]/page.tsx`、`web/app/workbench.tsx`、`web/app/workbench-nodes.tsx`、`web/app/workbench-api.ts`、`web/app/workbench-model.ts`、`web/app/globals.css`、`web/app/layout.tsx`、`web/vite.config.ts`、`web/.env.example`
- `Dockerfile`、`.dockerignore`、`.gitignore`、`deploy/nginx.conf.template`、`deploy/start-zeabur.sh`、`.env.example`
- `README.md`、`docs/architecture.md`、`docs/deployment_zeabur.md`、`docs/real_machine_test.md`、`WORKFLOW.md`
- `pyproject.toml`、`uv.lock`、`qiancraft.egg-info/PKG-INFO`、`qiancraft.egg-info/SOURCES.txt`

### 2026-08-28｜0.5.0｜Creative Intelligence Workbench 与空间化设计链路

变更：

- 将现有文化图谱、四平台市场快照、机会策略、Designer Handoff、DesignPackage 与海报产物接入统一工作台；默认 `guizhou-miao-demo` 包含 9 个实例、10 条连线，并严格覆盖 Culture Graph、Market Radar、Strategy、Design Brief、Visual Generation、Concept 与 Poster Board 7 类节点。
- 建立固定三栏产品界面：左侧 Knowledge Center 使用真实的 22 条文化记录、四平台状态和 Top 10，中间为可缩放/平移/小地图/点阵背景的空间画布，右侧 Inspector 提供 Info、Inputs、Parameters、Outputs、Sources、History、Actions。
- 增加画布 Flow Map，一键聚焦文化、市场、策略、任务书、视觉、A/B/C 与海报节点；缩短顶栏副标以避免 1280 像素视口截断，并提供 `NEXT_PUBLIC_QIANCRAFT_API_URL` 网站 API 地址配置入口，公开变量不承载密钥。
- 新增 Workspace New / Save / Load / Rename、节点 Run / Re-run / Run from here、任务书版本控制、仅下游 `stale` 传播、Concept Edit / Use / Duplicate / Regenerate / Generate More，以及可逆的 Poster 标题、字幕、区块显隐、顺序调整和 1800 × 2400 PNG 导出。
- 新增 OpenAI-compatible Images API 独立适配边界和安全配置项；没有自动化图像服务配置时返回可见 `warning`。在用户追加要求后，使用内置图像生成能力完成并目视复核 Concept B 轻量礼赠版与 Concept C 系列收藏版，以版本化 PNG、SHA-256 和提示摘要作为项目资产接入；不冒充 DeepSeek 图像调用。
- 产品界面、文案和信息架构统一为 QianCraft；React Flow 源码目录保持原样，Web 使用与其一致的 `@xyflow/react@12.11.5` 依赖，MIT 归属同步记录在第三方通知中；实机发现未经相应授权不能隐藏运行时 attribution 后，已移除隐藏选项并保留合法最小归属标记。
- 补充 Python/TypeScript 回归、Workbench API 与模型、架构/README/实机说明，并将项目版本提升到 0.5.0。

原因：

- 用户要求以最终总提示词为准，将已经完成的证据链和 Design Agent 接成可编辑、可保存、可继续生成的高完成度创意工作台，并为下一轮视觉精修和真实图像服务接入留足空间。

验证：

- `pytest -q` 32/32 通过；覆盖 7 类节点、默认 9 节点/10 连线、内置概念资产重载、保存重载、Brief 版本与 stale、非法边、Use、Duplicate、Regenerate、Generate More 和缺自动化图像服务时不伪造输出。
- Workbench TypeScript 测试 3/3 通过；Run from here 依赖顺序、下游 stale 和 Poster 区块可逆性均有回归。
- `uvx ruff check app scripts tests`、`pnpm typecheck`、ESLint 与 Vinext 五阶段 production build 全部通过。
- 本机 HTTP 实测完成 Bootstrap、临时 Workspace、Brief v2、节点运行、Concept 切换/复制/单体重生成/新增方向；临时验收工作区随后删除，默认工作区复原为 Concept A、任务书 v1、A/B/C 三套视觉和 9 节点/10 连线，并绑定最新实机运行号。
- 浏览器实测完成三栏布局、文化关系图浮层、节点 Inspector、Concept 参数编辑面板、New Workspace 对话框和 1800 × 2400 PNG 导出提示；前后端均使用真实本地接口。
- 最终网站浏览器实测点击 Flow Map 的 Concept B：画布在 420 ms 内聚焦该节点，B 产品图与 Inspector 同步显示；1280 × 720 截图中品牌副标、A/B/C、海报链路和右栏均正常排布。
- 完成 Vinext production server 实机启动并绑定 `127.0.0.1:3000`；production 页面、7 类节点、A/B/C 图片、Flow Map、合法 attribution 与 `127.0.0.1:8787` API 联动均通过。
- 环境探针确认 DeepSeek API 可达、返回 3 个模型且 `deepseek-v4-flash` 存在；随后完成 `20260828T060200Z-e44240e3` 全链路实机运行，Culture / Strategy / Design / Poster 为 live，Market 为 378 条历史快照 cache，API Key 未回显。DeepSeek `/images/generations` 实测 HTTP 404，独立图像自动化界面与 API 均如实显示 warning。
- Concept B/C PNG 均实际落盘并经浏览器重新载入：三条 Concept 节点均为 `success/v1` 且有可访问图像；B/C SHA-256 分别为 `099e2081…4135` 与 `33b6fae9…cb6a`。
- 最终 production 审计：页面 200、API 绑定最新运行号、9 节点/10 边/7 类型、3/3 Concept 图片和 B/C 资产均为 200；仅保留 1 个默认工作区，长 `sk-` 密钥文件命中 0，`git diff --check` 通过，构建缓存已清理。

边界：

- 本轮没有重新访问四个平台；115/14/101/148 与合计 378 条均为历史真实快照，状态是 `cache`，不是当前实时趋势。
- 当前没有独立图像提供商配置，所以 B/C 是本轮审阅后入库的项目资产，一键 Regenerate / Generate More 仍不会自动出图；这些概念图没有被说成 DeepSeek 生成，也没有请求复制具名神圣纹样或馆藏参考像素。
- 工作台依赖绑定在回环地址的 Python API、本地证据和私密配置，当前是明确的本地产品形态；没有发布一个断开后端的云端空壳。
- 产物仍只到概念视觉、报价/首样简报和展示海报；没有授权工厂下单、量产发布、商业美术审批或制造/合规就绪声明。
- 没有改写上传的 React Flow 源码、许可证或版权通知。

涉及文件：

- `app/workbench.py`、`app/tool_api.py`、`app/config.py`、`app/adapters/image_generation_adapter.py`
- `web/app/workbench.tsx`、`web/app/workbench-api.ts`、`web/app/workbench-model.ts`、`web/app/workbench-model.test.ts`、`web/app/workbench-nodes.tsx`、`web/app/globals.css`、`web/app/layout.tsx`
- `web/package.json`、`web/pnpm-lock.yaml`、`web/tsconfig.json`、`web/.gitignore`、`web/.env.example`
- `tests/test_workbench.py`、`data/workbench/workspaces/guizhou-miao-demo.json`
- `data/workbench/generated/guizhou-miao-demo/concept-b-v1.png`、`concept-c-v1.png`、`concept-visual-manifest.json`
- `data/outputs/pre_design_strategy.*`、`designer_handoff.*`、`design_specification.*`、`poster_render_request.json`、`design_poster.png`、`design_render_manifest.json`、`run_manifest.json`
- `data/demo_cache/pre_design_strategy.json`、`data/market/derived/latest.json`、`product_form_hotness.json`、`market_evidence_20260828T060206Z.json`
- `.env.example`、`pyproject.toml`、`README.md`、`THIRD_PARTY_NOTICES.md`、`docs/architecture.md`、`docs/real_machine_test.md`、`WORKFLOW.md`

### 2026-08-28｜GitHub 正式归并｜main 提交与推送完成

变更：

- 将上一条“GitHub 最新结果合并”形成正式提交 `99b44b4`（`feat: reconcile local evidence with auditable workbench`），并成功推送到 `origin/main`。
- 提交共纳入 20 个文件：本机较新的正式策略/设计/海报结果、`market_evidence_20260828T033015Z.json`、工具 API 的 raw 文件动态审计兼容修复、对应回归测试、Ruff 整理以及 README/WORKFLOW 状态同步。
- GitHub `main` 现同时包含提交 `86d7585` 的可审计 Web 工具工作台，以及本机 378 条历史真实快照形成的派生证据、Top 10 / Top 5 和最新正式设计结果。

原因：

- 用户要求尽快完成合并；上一轮只完成本地快进与冲突归并，本轮补齐正式提交和远端推送。

验证：

- 推送前重新执行 `git fetch --prune origin`，确认远端没有新增分叉提交。
- `pytest` 22/22、`uvx ruff check app scripts tests` 与 `pnpm build` 均通过；Vinext 五阶段构建完成。
- 对待提交代码、文档和输出执行密钥模式扫描，`sk-` 长密钥命中为 0；`git diff --cached --check` 通过。
- `git push origin main` 成功：远端由 `86d7585` 前进到 `99b44b4`。

边界：

- `data/market/raw/*.jsonl` 继续按项目安全策略留在本机且不进入 Git；GitHub 中保存的是脱敏后的历史派生证据，因此新鲜克隆会如实报告 raw 文件缺失，而不会冒充当前实时抓取。
- 合并前安全快照 `stash@{0}` 继续保留，未删除；本轮没有发布 Web 站点、没有访问四个平台或重新调用外部模型。

涉及文件：

- 上一提交 `99b44b4` 中的 20 个代码、测试、文档、派生数据与正式输出文件
- `WORKFLOW.md`

### 2026-08-28｜GitHub 最新结果合并｜工具工作台与本机实测状态归并

变更：

- 从 GitHub `origin/main` 获取最新提交 `86d7585`，将本地 `main` 从 `b4eb9ac` 快进到该提交；纳入可审计工具 API、五段式 Web 工作台、人工选择/编辑、独立设计运行、无通用兜底生成器以及对应测试和工作区产物。
- 合并前把本机未提交成果保存为可恢复 Git stash；快进后重新叠加，并逐项解决 `WORKFLOW.md` 与 13 项正式结果、Demo 缓存和市场派生文件的重叠。
- 远端代码和 Web 工作台采用 GitHub 最新实现；正式业务结果保留本机较新的 `20260828T033015Z-b570c979` 运行、原创主视觉海报、四平台原始 JSONL、378 条历史真实快照及对应 Top 10 / Top 5，没有用远端新鲜克隆环境的空榜覆盖本机证据。
- 归并两边追加式工作流历史：保留 GitHub 端的工具工作台、Web 前端和新鲜克隆验收记录，同时恢复本机“项目离线启动与当前产品形态复核”记录；当前状态改为描述本机合并后的真实环境。
- 修复 GitHub 新测试对“raw 文件必定缺失”的环境假设：工具 API 现在按 xhs/dy/bili/wb 四个实际 JSONL 计算存在数和完整性，回归测试同时适用于新鲜克隆与保留实测快照的工作区；顺带按当前 Ruff 规则整理远端新增文件。

原因：

- 用户要求合并 GitHub 最新结果；远端新增实现与本机未提交的较新实测数据存在同名文件重叠，需要在不丢失任一侧成果的前提下完成合并。

验证：

- `git fetch --prune origin` 与 `git merge --ff-only origin/main` 成功；本地 `HEAD` 已指向 `86d7585`，远端新增的工具 API、脚本、测试、`web/` 和 `data/tool_workspace/` 均已落地。
- `scripts/check_environment.py --probe-api --probe-mediacrawler` 通过：Python 3.13.9、三个上游入口、MediaCrawler 隔离运行时与平台导入正常；DeepSeek 可达且目标模型存在，密钥值未输出。
- `pytest` 22/22 通过；`uvx ruff check app scripts tests` 通过。
- 工具审计实测返回当前运行号 `20260828T033015Z-b570c979`、市场记录 378、raw 文件 4/4 完整、当前市场状态 `cache`；没有把历史文件标成当轮实时抓取。
- `pnpm install --frozen-lockfile` 通过供应链策略检查并按锁文件安装 479 个包；`pnpm build` 通过 Vinext 的 client references、server references、RSC、client 与 SSR 五阶段构建。
- `git diff --check` 通过；冲突标记扫描为 0，最终工作树不存在未合并路径。

边界：

- 本次只把 GitHub 最新结果合入当前本地工作区，没有发布网站、没有重新访问四个平台、没有重新调用外部模型，也没有推送本机重新叠加的运行结果。
- `stash@{0}` 暂时保留为合并前安全快照，待用户确认无需回退后再决定是否清理；它不参与运行，也不会进入提交。
- 当前产品仍停在概念视觉、工厂报价与首样沟通阶段，不代表量产、商业文化授权或制造合规就绪。

涉及文件：

- `app/tool_api.py`、`app/designer/agent.py`、`app/designer/poster.py`
- `scripts/run_tool.py`、`scripts/run_web_tool.py`、`tests/test_tool_api.py`
- `web/`、`data/tool_workspace/`
- `README.md`、`WORKFLOW.md`
- `data/demo_cache/pre_design_strategy.json`、`data/market/derived/`、`data/outputs/`

### 2026-08-28｜0.4.0｜项目离线启动与当前产品形态复核

变更：

- 按项目快速开始入口，以 `demo` 模式接入现有原创主视觉 `huaxi_grid_magnet_hero_v1.png`，实际完成一次文化、市场、策划、Design Agent 与海报渲染的端到端启动；新运行号为 `20260828T033015Z-b570c979`。
- 本次运行生成 8 条 Opportunity Signals，Top 3 仍为 OPP-006、OPP-002、OPP-004；Design Agent 继续选择 OPP-006，并保持“针格模块｜花溪挑花互动冰箱贴（概念样）”这一单一花溪方向。
- 刷新 13 项正式输出、最新市场派生文件与 Demo 缓存；五组件状态为 `cache / cache / cache / live / live`，四平台分别复用 xhs 115、dy 14、bili 101、wb 148 条历史真实快照。
- 复核当前交付形态：QianCraft 是一次运行、文件落盘的 Python CLI 研究原型，不是常驻 Web 服务；主要可视成果为 1800 × 2400 概念海报，机器交付为 JSON，说明与工厂首样简报为 Markdown。
- 同步 README 的当前运行基线，明确区分本次离线可重复启动与最近一次 LightRAG / DeepSeek 外部运行时完整验收，避免把 Demo 缓存状态描述成 live。

原因：

- 用户要求启动项目并了解当前项目形式；需要以实际启动结果回答，同时保持运行清单、展示文档与项目级工作流台账一致。

验证：

- `.\.venv\Scripts\python.exe scripts\run_demo.py --mode demo --design-hero data\design\assets\huaxi_grid_magnet_hero_v1.png` 退出码 0；完成 8 条机会信号并写出运行清单。
- 回读 `run_manifest.json`：13 个声明输出全部存在；组件状态为 culture `cache`、market `cache`、strategist `cache`、design `live`、poster `live`；四平台样本合计 378 条。
- 回读并目视检查 `design_poster.png`：尺寸 1800 × 2400，主视觉、文化说明、尺寸用料、五件爆炸拆解、六步工艺和 BOM 区域完整可读。
- `pytest` 19/19 通过；`ruff check app scripts tests` 通过。

边界：

- 本次为不调用外部 API、不启动浏览器的离线 Demo；没有重新访问 LightRAG 服务、DeepSeek 或四个平台，因此不能把前三个组件或平台数据表述为本轮 live。
- 该命令是一次性批处理，完成后进程正常退出；仓库当前没有自研 Web/桌面交互前端或需要持续监听的应用服务器。
- 当前海报、尺寸、材料与制造拆解仍只用于概念展示、工厂报价和首样沟通；不代表生产工程定稿、商业文化授权、平台全量趋势或量产/合规就绪。

涉及文件：

- `README.md`、`WORKFLOW.md`
- `data/demo_cache/pre_design_strategy.json`
- `data/market/derived/latest.json`、`data/market/derived/product_form_hotness.json`、`data/market/derived/market_evidence_20260828T033015Z.json`
- `data/outputs/pre_design_strategy.json`、`data/outputs/pre_design_strategy.md`
- `data/outputs/designer_handoff.json`、`data/outputs/designer_handoff.md`
- `data/outputs/design_specification.json`、`data/outputs/design_specification.md`
- `data/outputs/poster_render_request.json`、`data/outputs/design_poster.png`
- `data/outputs/design_render_manifest.json`、`data/outputs/run_manifest.json`

### 2026-08-28｜可审计工具工作台｜真实来源、人工介入与无兜底生成

变更：

- 将原只读展示首页改造成五段式本地工具工作台：总览、来源仓库、机会池、设计工作台与运行记录；每一层都可以回看真实输入、证据 URL、状态和产物关系。
- 新增只绑定回环地址的 `app/tool_api.py` 与 `scripts/run_tool.py`，把文化记录、历史/当前市场记录、8 条机会、评分复算、设计谱系、运行状态和本地图片作为结构化接口提供给前端。
- 新增持久化工作区：默认自动选择当前评分最高的 Top 3；用户也可选择 1–3 条机会、指定主机会，并修改标题、为什么是现在、产品形态、关键词和设计简报。原始证据、原始分数及核验状态保持只读。
- 设计生成改为显式操作：每次把当时的手工修改写入独立 Designer Handoff 草稿并计算 SHA-256，再生成独立设计规格、结构渲染图、清单和运行记录。手工主机会真实决定生成器；没有已实现生成器的品类直接报错，不套通用模板。
- 新增严格研究入口：执行前先检查 LLM Key、四平台实抓开关和 MediaCrawler 隔离环境，执行后只接受全部组件与平台都为 `live` 的结果；任一条件不足就拒绝运行，不回退到 demo、cache 或公开基线。
- 补充真实数据审计：22 条文化记录在当前图谱中确实存在；378 条平台记录只存在于历史派生快照，克隆仓库中没有对应 raw JSONL，不能称为当前实时抓取；8 条机会确实存在且分数可复算，但均来自代码中的证据规则基线，本轮模型生成接受数为 0。
- 明示设计谱系：当前“针格模块”由 `OPP-006` 进入 Design Agent 后收窄到花溪挑花单一区域，再形成磁吸拼图概念；工具中同时展示这一收窄过程，不再让下游设计看起来凭空出现。
- 新增 `scripts/run_web_tool.py`，可同时启动本地 API 和前端；保持本地运行，不做公网发布。

原因：

- 用户明确要求把 QianCraft 从对外展示页改为可操作工具，并要求所有数字、评分、机会、设计输入和生成结果都可检查、可介入且禁止兜底伪装。

验证：

- `pytest` 22/22 通过；新增覆盖真实计数、8 条评分逐项复算、手工选择 `OPP-002` 生成对应软偶方向，以及未实现生成器时必须失败。
- `pnpm build` 通过，Vinext 的 client references、server references、RSC、client 与 SSR 五阶段全部完成。
- 本地 API 健康检查通过；文化记录返回 22 条，历史小红书记录返回 115 条并支持分页，总历史平台记录为 378 条。
- 严格研究接口在当前缺少 LLM Key、平台实抓开关和 MediaCrawler 环境时返回 422，并逐项报告阻断原因，没有启动任何假运行。
- 真实创建工具设计运行 `20260828T035811Z-design`：主机会为 `OPP-006`，产物包含当次草稿哈希、设计规格、1800×2400 结构渲染图、渲染清单和运行清单；`image_generation_used=false` 如实记录未调用图像模型。

边界：

- 当前机器尚未配置本轮严格研究所需的 LLM Key、四平台实时抓取和 MediaCrawler 隔离环境，因此工具可以查阅历史证据，但不能宣称已经重新实时抓取。
- 当前没有可从网页调用的图像生成服务；“AI 视觉图”按钮保持禁用并展示缺失原因。现有结构渲染图是真实由本地设计生成器创建的 SVG/PNG 产物，但不是图像模型效果图，也不是工厂可直接生产的工程图。
- `OPP-004` 等没有对应产品生成器的机会只能参与研究与编辑，点击生成会明确失败；新增生成器后才能产出对应设计。
- 本轮未发布公网，工具只在 `localhost` 使用；文化授权、社区共创、工艺测试和量产工程仍需线下流程。

涉及文件：

- `app/tool_api.py`、`app/designer/agent.py`、`app/designer/poster.py`
- `scripts/run_tool.py`、`scripts/run_web_tool.py`
- `web/app/page.tsx`、`web/app/workbench.tsx`、`web/app/globals.css`
- `tests/test_tool_api.py`
- `data/tool_workspace/`
- `WORKFLOW.md`

### 2026-08-28｜本地 Web 前端｜QianCraft 证据链与设计成果展示站

变更：

- 新增 `web/` 前端工程，使用 Vinext、React、Vite 与 Sites 本地开发流程；站点默认通过 `http://localhost:3000/` 访问。
- 首页形成六个产品级区域：价值主张与真实数据概览、四段证据链、Top 3 机会方向、针格模块设计与 BOM、五组件运行状态以及边界声明。
- 展示数据从当前正式产物核对：22 条文化记录、378 条仓库历史真实快照、13 项正式产物；Top 3 为 OPP-006 / OPP-004 / OPP-002，分数 83.4 / 79.6 / 79.2。
- 展示已有原创产品主视觉与完整概念海报，没有引入 `reference_only` 馆藏像素；新增深墨绿、暖白、朱砂与金色的站点分享预览图 `web/public/og.png`。
- 在 `pnpm-workspace.yaml` 中对脚手架已锁定的 `esbuild`、`sharp`、`unrs-resolver` 和 `workerd` 依赖构建脚本作显式精确允许，保持依赖安装可重复，没有开启宽泛脚本放行。

原因：

- 用户明确要求为现有 QianCraft 制作前端网页，并通过 localhost 在本地打开；原仓库只有命令行流水线与 PNG 产物，没有 Web 入口。

验证：

- `pnpm install` 通过，四个精确允许的原生依赖脚本完成。
- `pnpm build` 通过，Vinext 的 client references、server references、RSC、client 与 SSR 五阶段均构建成功。
- 开发服务在 `http://localhost:3000/` 启动，轻量 HTTP 健康检查返回 200。
- 社交预览图经目视检查，站点标题“QianCraft｜黔艺前策”与副文案完整正确，未出现多余文字或馆藏素材。

边界：

- 本轮按用户要求保持本地运行，未发布到公网；网页是当前本地产物的只读展示层，尚未连接后端任务队列，不会从浏览器触发 Python 策划流水线。
- 页面继续保留研究原型、cache/live 真实状态、量产前停止、馆藏参考图禁用和社区复核边界。

### 2026-08-28｜本地启动验收｜新鲜克隆环境的离线 Demo

变更：

- 从 GitHub 克隆项目后，使用 Python 3.12.13 在 `.venv` 中安装根项目及测试依赖，未安装或启动 LightRAG、GPT Researcher 与 MediaCrawler 的可选外部运行时。
- 执行 `scripts/run_demo.py --mode demo`，刷新 13 项正式输出及 demo/market 派生缓存；新运行编号为 `20260828T031637Z-fb206d5d`。
- 本轮没有访问四个市场平台；四平台如实记录为 `unavailable`，文化、市场、策划与海报层的离线来源标记为 `cache`。

原因：

- 用户要求拉取并启动项目；优先使用不需要 API 凭证、平台登录或浏览器交互的 demo 模式完成安全可重复的首次启动。

验证：

- `.venv/bin/python -m pytest` 通过，19/19 项测试成功。
- `.venv/bin/python scripts/run_demo.py --mode demo` 成功退出，生成 8 条机会信号、Top 3 Designer Handoff、Design Specification、1800 × 2400 海报与 RunManifest。

边界：

- 这是离线研究原型启动，不代表 LightRAG、DeepSeek 或四平台实时数据已接入；未创建 `.env`，未请求用户凭证，未打开浏览器授权。
- 本次运行刷新了 `data/outputs/`、`data/demo_cache/pre_design_strategy.json`、`data/market/derived/latest.json`、`data/market/derived/product_form_hotness.json`，并新增 `data/market/derived/market_evidence_20260828T031637Z.json`。

### 2026-08-28｜README 展示层｜GitHub 首屏、成果证明与可信开源叙事

变更：

- 参考 FastAPI、uv、Supabase 与 LangChain 等成熟开源项目的 README 信息架构，将旧版偏操作手册式 README 重构为 GitHub 项目展示页：首屏价值主张和状态、核心能力、真实成果、三步快速开始、Mermaid 架构、组件与模式、进阶安装、正式输出、可信边界、验证、文档地图、路线图、参与方式与许可证说明。
- 新增项目自有横版 SVG 首屏 `docs/assets/qiancraft-readme-hero.svg`，沿用深靛、暖白和红色的设计系统，以原创抽象数纱网格表达 Culture DNA → Trend DNA → Design Agent → Factory Brief；不使用馆藏图片或完整传统纹样。
- 在 README 首屏加入版本、Python、测试和研究原型 4 个静态徽章；没有虚构 CI、下载量、用户数、许可证或生产就绪状态。
- 把 22 条文化记录、32 条来源、378 条真实平台快照、13 个正式输出和最新运行号等可核验事实前置；嵌入现有概念海报，并直接链接设计规格、渲染请求与摘要。
- 将 LightRAG/GPT Researcher、MediaCrawler 隔离环境和四平台显式授权下沉到折叠区，使首次访问者先理解产品价值，进阶使用者仍能获得完整可复制命令。
- 明确披露 MediaCrawler 非商业限制、QianCraft 自有代码层尚无独立公开许可证、当前没有 CI/贡献指南/安全入口，以及概念样不等于量产或商业文化授权；相应缺口进入路线图。

原因：

- 用户要求参考顶尖开源项目，为 QianCraft 设计一份适合 GitHub 展示的优秀 README；重点不是增加宣传口号，而是让首次访问者快速理解产品价值、看到真实产物、成功运行，并能识别证据、文化、数据和许可证边界。

验证：

- 使用无头 Chrome 将 1200 × 420 SVG 首屏渲染为原尺寸 QA 图，目视确认中英文、层级、网格、色彩、圆角和标签无裁切、重叠或缺字。
- 自动解析 README 的 Markdown 与 HTML 引用：共 32 个链接/资源引用，本地缺失 0；代码围栏闭合，SVG 通过 XML 解析，4 个徽章、1 个 Mermaid、2 个折叠区、14 个二级章节均存在。
- 从正式 JSON 回读并核对 README 数据：文化记录 22、来源 32、市场样本 378、Manifest 输出 13、运行号 `20260827T225611Z-4f2a77ae`；README 未出现绝对 Windows 路径或长 `sk-` 凭证模式。
- `uv run python scripts/run_demo.py --help` 通过，确认新版快速开始引用的主入口及 `--mode / --design-hero` 参数存在；未重跑完整 Demo，以免覆盖当前正式实机输出。
- `pytest` 19/19 通过；`ruff check app scripts tests` 通过。README 为 300 行、14,774 字节，横幅和现有设计海报路径均存在。

边界：

- 当前工作目录不是 Git 仓库且没有可识别的远程地址，因此本轮只完成本地 GitHub-ready README，没有创建仓库、提交、推送或观察远程 GitHub 最终页面。
- 徽章是与当前状态一致的静态徽章；后续版本、Python 基线或测试数变化时必须随 WORKFLOW 同步更新。尚未配置 GitHub Actions，不能把静态测试徽章解读为持续集成状态。
- Shields.io 徽章需要网络才能加载；标题、替代文本、正文、SVG 和产品海报均为仓库内内容，离线时不影响核心说明。
- README 诚实披露 QianCraft 自有代码层尚未声明独立公开许可证；在用户确定许可证前，不添加开源许可证徽章或额外授权措辞。

涉及文件：

- `README.md`
- `docs/assets/qiancraft-readme-hero.svg`
- `WORKFLOW.md`

### 2026-08-28｜0.4.0｜Design Agent、工厂首样拆解与艺术海报

变更：

- 新增 `DesignInputContract / DesignPackage / ManufacturingBrief / PosterRenderRequest / DesignRenderManifest` 等契约，把原有 `designer_handoff.json` 从预留接口升级为实际运行的文件级输入；记录输入 SHA-256，并强制主机会来自交接 Top 3。
- 新增 QianCraft Design Agent。选案依次考虑文化复核状态、高敏感母题、产品具体度与综合分；将 OPP-006 多支系收藏方向缩窄为“针格模块｜花溪挑花互动冰箱贴（概念样）”，OPP-002 鸟/蝶等母题在社区核验前留置，OPP-004 保留为后续独立变体。
- 生成完整的概念设计与工厂首样简报：5 项原型尺寸、5 项 BOM、1 组原创数纱网格应用、6 步装配、6 项质检、包装与安全合规、3 个文化审核门、3 个工程审核门和 5 个工厂待确认问题。
- 使用内置图像生成模式制作原创、无文字的成品与爆炸主视觉 `huaxi_grid_magnet_hero_v1.png`。生成只接收文字化数纱结构、材料与零件关系，明确排除馆藏图像、完整传统纹样、动植物/祖源/神圣母题、服饰与外露磁体；逐字提示词固化在 `poster_render_request.json`。
- 新增本地精确文字海报排版器，把成品视觉、文化元素/风格、尺寸/用料、五件爆炸拆解、六步工艺与 BOM 合成为 1800 × 2400 PNG；主视觉与海报 SHA-256、画布和 reference-only 像素声明写入 RenderManifest。
- 主流水线在 Designer Handoff 落盘后重新读取该文件并运行设计段；正式输出由 8 路增至 13 路，RunManifest 由 3 个组件扩展为文化、市场、策划、Design Agent 和海报渲染 5 个组件。
- 新增 `scripts/run_design_agent.py` 独立入口和 `run_demo.py --design-hero`；同步更新 README、架构、实机报告、Agent 边界与本工作流，并新增 Design Agent 专题文档。

原因：

- 用户要求补齐核心公共链路中的设计 Agent，把既有 JSON 交接作为输入，输出兼具贵州文化元素、成品形象、材料/图案/结构拆解、工厂加工信息与艺术展示效果的完整设计海报，同时确保接口可实际运行。

验证：

- 最新完整 `auto` 运行号为 `20260827T225611Z-4f2a77ae`：`culture_knowledge=live`、`market_research=cache`、`strategist=live`、`design_agent=live`、`poster_renderer=live`；市场段只消费已保存的 378 条真实快照，没有把缓存标成实时访问。
- `scripts/run_design_agent.py --hero-image data\design\assets\huaxi_grid_magnet_hero_v1.png --update-run-manifest` 实测通过；Design Agent 从文件选择 OPP-006，13 个清单路径全部存在。
- 交接文件实际 SHA-256 与 `DesignInputContract.source_sha256` 一致；海报实际 SHA-256 与 RenderManifest 一致；主视觉与海报均记录摘要，`reference_images_used_as_pixels=false`、`reference_only_images_used=false`、`mass_production_ready=false`。
- 最终设计契约复核为 5 项尺寸、5 项 BOM、1 个图案应用、6 步装配、6 项质检、3 个文化门、3 个工程门和 5 个工厂问题；海报尺寸为 1800 × 2400，原始分辨率目视复核无裁切、错位或不可读正文。
- `pytest` 19/19 通过；`ruff check app scripts tests` 通过；新增回归确保在安全替代项存在时不自动选择鸟、蝶、祖源等高敏感母题。
- 自有代码、脚本、测试、文档和正式输出的长 `sk-` 模式扫描为 0 命中；旧阶段边界、旧测试计数与旧输出数量已从当前状态和专题说明中清除，历史追加日志保持不回写。

边界：

- 当前方案是展示、工厂报价与结构首样输入，不是生产工程图、开模文件、合规证书、采购订单或商业授权；不得据此宣称可直接量产。
- 花溪具体合作社区/保护单位仍需确认原创数纱网格的商品化边界、地域/工艺表述、参与者署名、收益、返修与撤回机制。
- 工厂仍需验证磁体等级和封闭结构、吸附力、卡合循环、绣线耐磨、跌落与小部件风险；最终销售年龄和地区确定后再选择适用材料、标签、包装和测试标准。
- 生成式主视觉是原创概念呈现，不替代结构工程验证；展示用深靛、红、暖白关系不是传统标准色，量产色必须由实物线卡和共同评审确认。

涉及文件：

- `app/schemas.py`、`app/config.py`、`app/pipeline.py`、`app/strategist/strategist.py`
- `app/designer/`、`scripts/run_demo.py`、`scripts/run_design_agent.py`
- `data/design/assets/huaxi_grid_magnet_hero_v1.png`、`data/outputs/`
- `tests/test_demo_pipeline.py`、`pyproject.toml`、`app/__init__.py`
- `README.md`、`AGENTS.md`、`docs/architecture.md`、`docs/design_agent.md`、`docs/real_machine_test.md`、`docs/product_direction.md`、`WORKFLOW.md`

### 2026-08-28｜0.3.1｜四平台授权实测、真实榜单与安全收口

变更：

- 使用用户本人已完成的四个平台 CDP 授权执行正式小规模复核；为每个平台分别核验登录、关键词搜索、规范化记录与落盘结果，没有用缓存冒充当轮实时结果。
- 正式复核取得小红书 115、B站 101、微博 148 条当轮实时记录；抖音没有生成新内容文件，自动使用既有 14 条历史真实快照，随后单平台重试仍为同一结果。
- 用四个平台共 378 条真实快照重建 `product_form_hotness.json`：Top 10 为冰箱贴、徽章、盲盒、包挂、伴手礼、潮玩、香氛、挂件、首饰、毛绒；优先 Top 5 为前五项。
- 运行完整 `auto` 链路生成新策略、视觉参考、Designer Handoff 与 RunManifest；市场访问开关保持关闭，完整链路只读已保存快照，避免对平台重复施压。
- 交互式 MediaCrawler 子进程的标准输出与错误输出改为丢弃，避免上游运行细节或会话材料进入终端日志；无交互失败仍保留经过脱敏的有限诊断。
- 将离线市场回退测试改用 pytest 临时 raw/derived 目录，避免本机真实快照污染“无缓存”测试前提；同步更新 README、实机报告和本工作流当前状态。

原因：

- 用户确认四个平台授权完成并要求立即检验；检验必须回答授权是否实际可复用，同时保留失败平台的真实状态，并把本轮更新持续写入工作流程文档。

验证：

- 四个平台逐一授权 Smoke Test 均曾实时成功：xhs=`live/20`、dy=`live/14`、bili=`live/20`、wb=`live/16`；证明四路本人授权路径和保存会话都至少实际可用过一次。
- `scripts/probe_market_platforms.py --platform all --method cdp --formal --authorize` 实测：xhs=`live/authorized/115`、dy=`cache/missing/14`、bili=`live/authorized/101`、wb=`live/authorized/148`，达到 3/4 live；证据固化于 `data/market/derived/market_evidence_20260827T222055Z.json`。
- `scripts/probe_market_platforms.py --platform dy --method cdp --authorize` 随后单独复测仍提示上游完成但没有内容产物，继续使用 14 条历史真实快照；未再连续请求，避免放大风控或限流。
- 四个规范化快照审计均可由 `MarketPost` 契约读取：xhs 115、dy 14、bili 101、wb 148，共 378 条；统一榜单 `total_sample_size=378`、Top 10 完整、Top 5 完整、跨平台分数为 36.6–57.4。
- `scripts/run_demo.py --mode auto` 通过，运行号 `20260827T222346Z-f95d90e0`；文化层 `live`、市场层 `cache`、策划层 `live`，LightRAG 为 612 实体/697 关系，DeepSeek 生成 11 条合约机会并交接 Top 3。
- `pytest` 18/18 与 `ruff check app scripts tests` 已在安全及测试隔离修订后通过；最终契约、8 路输出与密钥模式扫描在本日志完成前再次复核。

边界：

- 本轮只能声明 3/4 平台当轮实时成功；抖音的 14 条记录是真实历史快照，但不是本次实时结果。其失败可能来自会话、搜索产物、平台风控或限流，当前证据不足以唯一归因。
- CDP 浏览器资料可在后续运行中复用，但平台登录并非永久授权；退出登录、Cookie 过期、风控或资料目录清理后需本人重新登录。
- 378 条是本次小规模研究样本，不代表四个平台全量市场；跨平台热度是解释性信号，不是销量、价格或爆款预测。
- MediaCrawler 仍受非商业学习/研究许可证与各平台条款约束；流水线继续停在 Designer Handoff，未进入最终设计、SKU、打样或量产。

涉及文件：

- `app/adapters/media_crawler_adapter.py`、`tests/test_demo_pipeline.py`
- `data/market/raw/`、`data/market/derived/`、`data/outputs/`、`data/demo_cache/`
- `README.md`、`docs/real_machine_test.md`、`WORKFLOW.md`

### 2026-08-28｜0.3.0｜四平台真实市场适配与产品形态热度榜

变更：

- 在现有 `MediaCrawlerAdapter` 内把单一小红书路径扩展为 `xhs / dy / bili / wb` 四平台；没有新增 Agent，也没有改动 LightRAG 文化图谱、视觉参考或 Designer Handoff 主逻辑。
- 建立四平台统一关键词池与统一 MarketPost 字段，补充 `views / product_form / retrieved_at / platform_hot_score`；按上游真实字段分别适配小红书、抖音、B站和微博，缺失值保持 0/空。
- 为四个平台建立相互隔离的运行、失败和历史快照降级路径；只有实际搜索并保存真实记录才标 `live`，历史真实记录只标 `cache`，没有真实快照时标 `unavailable`。
- 实现产品形态规则分类、同平台正值百分位热度和跨平台聚合；跨平台公式固定为 60%平台内平均热度、15%出现次数百分位、15%平台覆盖率、10%近期性，输出 Top 10 和最多 5 个 `priority_product_forms`。
- 新增 `data/market/derived/product_form_hotness.json`；规范化成功快照约定为 `data/market/raw/{platform}.jsonl`，上游原始数据放在 `raw/_upstream/`，但在没有真实记录时不创建空文件。
- TrendDNA 增加 `hot_product_forms / priority_product_forms`；RunManifest 增加四个平台各自的登录、搜索、样本和路径状态，正式输出由 7 路增至 8 路。
- 新增 `scripts/probe_market_platforms.py`，同时承担无交互状态探针、逐平台本人授权 Smoke Test 和授权后的正式小规模复核；旧小红书脚本继续兼容。
- 新增四平台字段、缺失指标、双层热度、产品形态聚合、Top 5、四路 Manifest 回归覆盖；同步更新配置、README、架构、市场公式和实机报告。

原因：

- 用户以最新四平台专项提示词为准，要求把此前爆款搜索模块最终修订为小红书、抖音、B站、微博同步推进，并继续维护项目工作流台账。

验证：

- `scripts/check_environment.py --probe-mediacrawler` 通过：主环境与三个上游入口存在，MediaCrawler 隔离环境实际导入 `bili,dy,ks,tieba,wb,xhs,zhihu`。
- `scripts/probe_market_platforms.py` 无交互实测完成：本机没有 9222 CDP 授权会话，xhs/dy/bili/wb 四路均真实报告 `unavailable / missing / 0`，命令以退出码 2 表示尚未达到 4/4 live。
- 最新正式运行 `20260827T213304Z-266d29ef` 通过：文化层 `live`、市场聚合层 `cache`、策划层 `live`；GPT Researcher + DeepSeek 仍生成 12 条合约机会，四平台状态独立写入 Manifest，8 个输出路径均存在。
- 当前 `product_form_hotness.json` 合法记录四平台集合，但因没有授权真实样本，`total_sample_size=0`、`ranking=[]`、`priority_product_forms=[]`；未用 12 条公开研究基线伪造排名。
- `pytest` 18/18 通过；`ruff check app scripts tests` 通过；四平台字段夹具、缺失值、Platform/Cross-platform Hot Score 0–100、产品形态聚合、Top 5 上限和四路 Manifest 均有回归验证。
- 最终契约复核通过：策略、视觉参考、Designer Handoff、RunManifest、产品形态榜五个 JSON 均可由 Pydantic 重新载入，8 个清单路径存在；第三方许可证存在，自有代码、文档和输出的 API Key 模式扫描为 0 命中。

边界：

- xhs、dy、bili、wb 的真实 Smoke Test 和正式约 200–600 条抓取仍需用户本人逐平台扫码/浏览器授权；当前不能声明任何平台 live，也没有可报告的真实 Top 10 / Top 5。
- 平台热度只在本批次或同一历史快照内部比较；跨平台分数是解释性市场信号，不是销量、价格或“AI 爆款预测”。
- MediaCrawler 仍受非商业学习/研究许可证和各平台条款约束；商业化前必须另行取得授权或替换采集实现。
- 本轮停在 Designer Handoff，未开始最终视觉设计、SKU、打样或量产判断。

涉及文件：

- `app/config.py`、`app/schemas.py`、`app/pipeline.py`
- `app/adapters/media_crawler_adapter.py`、`app/strategist/strategist.py`
- `scripts/probe_market_platforms.py`、`scripts/authorize_xhs.py`、`scripts/run_demo.py`
- `tests/test_demo_pipeline.py`、`.env.example`、`pyproject.toml`
- `data/market/derived/`、`data/outputs/`
- `README.md`、`docs/architecture.md`、`docs/market_intelligence.md`、`docs/real_machine_test.md`、`WORKFLOW.md`

### 2026-08-28｜0.2.0｜第一阶段收口：真实授权、视觉证据、评分核验与 Top 3 交接

变更：

- 将第二份阶段提示拆成运行契约并落地到现有 Adapter / Strategist / Pipeline / Schema；没有新增代理，也没有越过 Designer Handoff 生成最终设计。
- 为 MediaCrawler 接通小红书 Cookie、二维码和 CDP 三种用户授权路径；普通运行默认不弹窗，新增 `scripts/authorize_xhs.py` 作为显式授权入口。
- 建立 22 个 XHS 关键词全集，默认 6×20 并优先覆盖花溪、剑河、松桃、雷山，配置硬限制为 100–500 条；原始数据写 `data/market/raw/`，清洗、证据分型和评分写 `data/market/derived/`。
- 市场证据统一为 `social_signal / institutional_signal / media_signal / product_signal`，并拆分 `real_engagement_score / institutional_signal_score / derived_viral_score`；RunManifest 增加 `status`、`login_state`、关键词、raw/derived 路径和样本数。
- 在文化图谱增加 4 条权威馆藏视觉来源，总来源由 28 增至 32；新增 12 条 Visual Reference、5 个 Pattern Primitive、3 组无伪造 HEX 的颜色关系。全部权利未明图片均为 `reference_only`。
- 为每条机会增加文化契合、市场拉力、新颖度、视觉潜力、社交传播、产品可行性、文化风险与综合分；使用 20/20/20/15/15/10 权重并扣除 20% 风险。
- 高分候选重新进入 LightRAG Adapter，检查证据、地域/支系、禁忌、高敏感叙事和现代转译；`warning` 扣分，`rejected` 归零且不得进入 Top 3。
- 实机发现并修复两类语义缺陷：将“不得与某地混用”的否定约束误判为地域主张；把剑河“迷宫式核心图案”拼到花溪挑花仍通过编号检查。两类缺陷均加入回归测试。
- 重构 Designer Handoff 为明确的 11 组字段，只保留通过门槛的 Top 3；Creative Brief 限定 150–350 字，`designer_handoff.json` 为下一阶段机器唯一事实源，Markdown 自动渲染。
- 正式输出从 3 项扩展为 7 项：策略、视觉参考、设计交接各自 JSON/Markdown，加 RunManifest；同步更新 README、架构、知识图谱、实机报告和产品方向。

原因：

- 用户要求根据第二份提示词完成第一阶段架构收口，并继续维护项目级工作流程文档，为下一阶段视觉设计保留充分空间。

验证：

- `scripts/check_environment.py --probe-mediacrawler --probe-api` 通过：Python 3.13.9，三个上游运行时可导入，DeepSeek 返回 3 个模型且 `deepseek-v4-flash` 可用，密钥未回显。
- 最新正式运行 `20260827T205936Z-a5984efd`：文化层 `live`、市场层 `cache`、策划层 `live`；LightRAG 为 612 实体/697 关系，GPT Researcher + DeepSeek 输出 12 条合约机会。
- 最新 Top 3 为 `OPP-010` 支系差异系列收藏、`OPP-002` 花溪挑花互动模块、`OPP-004` 松桃可追溯手作体验；三项均为 `verified / LightRAG local KG`。
- 市场清单为 `status=cache / login_state=missing / live_post_count=0 / cache_post_count=12`，没有把缺失登录态或公开缓存写成实时抓取。
- `pytest` 16/16 通过；`ruff check app scripts tests` 通过；编译、Pydantic 交接门禁、视觉来源覆盖、无 HEX、JSON→Markdown 一致性和 7 路输出均通过。
- 最终契约复核通过：4 个核心 JSON 均可由 Pydantic 重新载入，Top 3 无 rejected，12 条视觉参考完整，7 个清单路径实际存在；自有代码、输出和文档的 API Key 模式扫描为 0 命中。

边界：

- 真实 XHS 帖子仍需用户显式运行授权命令并完成扫码/CDP 登录；当前没有授权会话，因此不是 live 市场样本。
- MediaCrawler 上游许可证限制非商业学习/研究；商业使用前还需书面许可、平台条款和账号权限确认。
- 权威馆藏图片只作参考，未获得馆方与相关社区授权前不得复制、训练或商用。
- Top 3 是概念设计输入，不是最终产品、SKU、尺寸、效果图或量产结论；社区授权、用户研究和材料试验仍是下一阶段门槛。

涉及文件：

- `app/config.py`、`app/schemas.py`、`app/pipeline.py`
- `app/adapters/lightrag_adapter.py`、`app/adapters/media_crawler_adapter.py`、`app/adapters/mediacrawler_runner.py`
- `app/strategist/strategist.py`、`app/strategist/prompt.md`
- `scripts/authorize_xhs.py`、`scripts/run_demo.py`
- `data/culture/knowledge_graph.json`、`data/culture/visual_references.json`
- `data/market/derived/`、`data/outputs/`、`data/demo_cache/pre_design_strategy.json`
- `tests/test_demo_pipeline.py`、`.env.example`
- `README.md`、`docs/architecture.md`、`docs/knowledge_graph.md`、`docs/real_machine_test.md`、`docs/product_direction.md`、`WORKFLOW.md`

### 2026-08-28｜0.1.0｜建立持续工作流文档

变更：

- 新增根目录 `WORKFLOW.md`，将系统工作流、目录职责、数据证据规则、凭证与许可证边界、标准命令和完成定义集中为唯一维护入口。
- 新增根目录 `AGENTS.md`，要求以后任何 Codex/代理在修改项目之前先读取本文件，并在完成前同步当前状态和追加日志。
- 在 README 的进一步资料中加入本工作流文档。

原因：

- 用户要求全面记录本次更新，并在后续每一次更新中持续维护同一文档。

验证：

- 检查文档内部链接、当前计数、运行状态和命令与现有项目一致。
- 确认 README 与 `AGENTS.md` 均指向根目录 `WORKFLOW.md`。

边界：

- 本次只新增项目治理与维护文档，没有改变运行代码、知识图谱、市场数据或正式策略输出。

涉及文件：

- `WORKFLOW.md`
- `AGENTS.md`
- `README.md`

### 2026-08-28｜0.1.0｜三上游统一、图谱建设与实机验收

变更：

- 建立 QianCraft 自有产品层：`config.py`、`schemas.py`、三个 adapter、单一 Strategist、Pipeline、CLI、测试和固定策划提示。
- 将 LightRAG、MediaCrawler、GPT Researcher 隔离在自有接口之后；保留上游目录及原许可证。
- 建成 22 条贵州非遗与在地文化记录、28 条权威来源及所有记录的字段级证据映射。
- 建成 12 条公开核验市场信号、12 条来源和 8 条 Benchmark Case。
- 建立文化边界：地域/支系识别、社区核验、传承人授权、工艺透明、共同署名与公平收益。
- 加入证据锁：生成机会必须同时具有现存文化和市场编号；不合约结果被拒绝，本地规则保证不少于 8 条机会。
- 安装主 Python 3.13 环境、LightRAG 1.5.7、GPT Researcher 0.14.7 和 MediaCrawler 隔离环境。
- 将用户 DeepSeek Key 安全安装到被忽略的 `.env`；确认 `deepseek-v4-flash` 可用。
- 生成 11 章节 Markdown、完整 JSON、Designer Handoff 和逐组件 RunManifest。
- 新增架构、知识图谱、实机验收和下一阶段产品方向文档。

原因：

- 将三个开源项目转化为统一、可审计、可继续设计的贵州文化产品前策系统，并补齐原先为空的知识图谱。

验证：

- LightRAG 真实索引并查询 612 个实体、697 条关系。
- GPT Researcher external-context writer 真实调用 `deepseek-v4-flash`，最终接受 12 条跨域机会。
- MediaCrawler 隔离环境成功导入 `bili, dy, ks, tieba, wb, xhs, zhihu`；因无授权 Cookie 未抓取。
- DeepSeek `/models` 探针返回 3 个模型，目标模型存在。
- Pytest 5/5、Ruff、编译、Pydantic 最终契约、跨域证据白名单和密钥扫描全部通过。

边界：

- 市场组件正式运行状态为 `cache`，不能描述为社交平台 live 抓取。
- MediaCrawler 当前不得直接进入商业抓取。
- 最新输出是设计前策略，不包含最终产品设计。

涉及文件：

- `app/`、`scripts/`、`tests/`
- `data/culture/knowledge_graph.json`
- `data/market/verified_signals.json`
- `data/benchmark/cases.json`
- `data/outputs/`、`data/demo_cache/`
- `.env.example`、`.gitignore`、`pyproject.toml`
- `README.md`、`THIRD_PARTY_NOTICES.md`、`docs/`

## 10. 后续日志模板

复制下面模板到“更新日志”顶部，并删除所有占位说明：

```markdown
### YYYY-MM-DD｜版本或阶段｜简短标题

变更：

- 做了什么；列出用户可观察结果。

原因：

- 为什么需要本次更新；对应哪个请求、缺陷或证据变化。

验证：

- 实际执行的命令及结果；未执行的项目必须说明。

边界：

- 尚未完成、没有授权、仍需人工确认或不能据此推断的内容。

涉及文件：

- 路径列表。
```

## 11. 当前已知约束与下一步空间

- C2 Tonal Focus Review 当前只实现并验收 1440×960 电脑端：前端单测 5/5、`desktop-chromium` 31/31、typecheck、lint 与 production build 通过。用户取消手机/平板适配后，Task 4 增量已完整撤销；两张 mobile snapshot 仅在 Task 5 中从起点到终点保持字节不变，且没有做 C2 mobile 复验。后续任何 mobile/tablet 结论都必须重新获得授权、实现并运行对应自动/真实设备门。自动检查也不能替代真实屏幕阅读器、残障用户、跨平台字体渲染与超大图谱性能测试。
- Human Decision Studio 已让文化、市场、机会、量分、任务书、视觉、概念和海报具备人工可变输入；下一步可在不改事实层的前提下增加 DecisionProfile 命名版本、差异对比、撤销/重做、多人批注和方案分支合并。
- Workbench 的研究任务、Design Agent、DesignPackage 和 Poster 已形成可持久化本地/远端闭环，刷新页面可续接研究轮询；0.9.2 远端隔离工作区已真实完成 Design Agent、DesignPackage 与 322,090 字节 Poster 后精确清理。此前 Qwen Image 3.0 三次同步实机生成是历史证据，当前本机与服务器的独立图像 provider 均未配置；后续新 Concept 必须按当次实际运行结果标注，旧成功资产继续与新结果分开记录。
- 本机被忽略的 `.env` 已配置 `LLM_API_KEY`，DeepSeek 探针可达并确认目标模型可用；但本轮只完成独立探针，没有重新执行完整 DeepSeek/GPT Researcher 策划流水线。正式产物继续保留既有真实模型运行证据，独立 auto 验收的 strategist cache 结论也不被此次配置状态追溯改写；正式 live 结论仍须来自新的完整集成运行。
- 当前 Zeabur 0.9.2 实例已通过 Nginx Basic Auth、回环 API、Secret 变量、安全响应头、429 限流、非 root worker、ext4 持久卷、可校验快照、真实健康检查与远端业务动作验收，调度器线程在线且心跳新鲜；若扩大为多人正式使用，仍需补用户级身份、权限审计、定时异地备份/恢复演练、外部告警、口令轮换、对象存储和分布式任务队列。
- 四平台授权资料均曾建立，但会话不是永久有效。0.8.0 最终严格轮的 xhs/dy/bili/wb 均为 unavailable，整轮没有晋级；较早正式复核中 xhs/bili/wb 为 live、dy 复用 14 条历史快照。后续每次仍必须按实际结果写 `live/cache/unavailable`，不能因曾经授权或启动过浏览器而固定写 live。
- 精简 Zeabur 镜像只发布 QianCraft 产品层与证据基线，不包含 MediaCrawler、LightRAG 和 GPT Researcher 上游源码/运行时；云端“实时运行”会如实预检阻断。若未来需要服务器实爬，必须另行解决平台授权浏览器、许可、队列、超时与长期会话，而不能复制本机 Cookie 到镜像。
- 当前 378 条真实平台快照已经形成 Top 10 / Top 5，可作为下一阶段候选品类输入，但样本规模、关键词和时间窗都有限，不能据此直接定案或宣称全平台趋势。
- MediaCrawler 仍缺少商业使用许可；现阶段只可在符合上游许可证和平台条款的非商业学习/研究场景使用。
- 文化图谱虽有权威公开来源，具体村寨的纹样名称、可公开范围、授权意愿与收益方式仍需田野核验。
- 当前已把 OPP-006 收敛为一个花溪互动冰箱贴概念并形成完整展示海报，但其数纱网格转译、地域/工艺表述、署名、收益与撤回机制仍需具体合作社区或保护单位确认。
- 当前尺寸、公差、BOM、装配和质检是工厂报价/首样输入，不是量产工程定稿。下一阶段应优先完成社区共审、用户测试、磁体封装/吸附力、卡合循环、绣线耐磨、跌落与适用标准验证，再决定 DFM、模具、成本和 SKU 扩展。

专题文档：

- [`PRODUCT.md`](PRODUCT.md)
- [`DESIGN.md`](DESIGN.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/design_agent.md`](docs/design_agent.md)
- [`docs/frontend_quality_workflow.md`](docs/frontend_quality_workflow.md)
- [`docs/human_decision_workflow.md`](docs/human_decision_workflow.md)
- [`docs/knowledge_graph.md`](docs/knowledge_graph.md)
- [`docs/market_intelligence.md`](docs/market_intelligence.md)
- [`docs/real_machine_test.md`](docs/real_machine_test.md)
- [`docs/typography_system.md`](docs/typography_system.md)
- [`docs/product_direction.md`](docs/product_direction.md)
