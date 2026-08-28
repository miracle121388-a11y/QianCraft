# QianCraft 工作流程与持续更新记录

> 文档性质：项目级唯一工作流说明、当前状态快照与追加式更新台账  
> 当前版本：0.8.0
> 最后维护：2026-08-29
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
| 产品名称 | QianCraft Creative Intelligence Workbench｜文化文创智能工作台 |
| 产品阶段 | 概念视觉与工厂首样简报；在量产发布前停止 |
| 产品工作台 | `web/` + `app/tool_api.py` + `app/workbench.py`；暖纸色 Creative Instrument 工具骨架由 56px 五阶段导航、64px 工具轨、按需 248px 证据/资产/历史 Dock、React Flow 主画布和 320px Inspector 组成，手机端把 Dock/Inspector 变为可逆覆盖层；默认 9 个实例覆盖 7 类业务节点，七阶段 Human Decision Studio 贯通文化、市场、机会/量分、任务书、视觉、概念与海报；每个节点均有专用展示页、引用台账、独立运行/从此运行/编辑保存/JSON 导出。0.7.3 把九个画布实例固定为稳定横向索引条；0.8.0 将顶部、节点页和“从此运行”的研究动作统一接入持久化严格后台任务，页面刷新会自动续接轮询，只有文化、策划和 xhs/dy/bili/wb 四平台全部为本轮 `live` 才晋级。Brief 实际运行 Design Agent 并落盘 DesignPackage，Poster 实际服务端渲染 1800×2400 PNG；缺图像 provider 时 Concept 只保留上次成功资产并明确 warning。默认本地站点 `http://localhost:3000/`，API 为 `127.0.0.1:8787` |
| GitHub 展示 | 项目 README 包含原创横版 SVG 首屏、真实状态徽章、在线实例、成果海报、A/B/C 三方向视觉、Workbench 快速开始、Mermaid 架构、可信边界、路线图与许可证说明 |
| 默认主题 | 贵州苗绣 |
| 默认目标市场 | 18–30 岁年轻消费者 |
| 文化知识图谱 | 22 条结构化文化记录、32 条文化/伦理/法律/馆藏视觉来源 |
| 苗绣检索 | 同时保留花溪挑花、剑河锡绣、松桃苗绣与雷山工艺差异 |
| 视觉参考包 | 12 条权威参考、5 个 Pattern Primitive、3 组无伪造 HEX 的文字色彩关系；默认 `reference_only` |
| 市场研究层 | 12 条结构化市场信号、12 条公开可追溯来源 |
| 市场状态 | 当前 Windows 基线保留 378 条历史真实快照（xhs 115、dy 14、bili 101、wb 148）与 12 条不进榜公开核验记录。0.8.0 网页严格任务确实重新访问平台；最终轮 `20260828T202303Z-2bae17ff` 的 xhs/dy/bili/wb 均未产出可晋级实时内容，market=`cache`、整轮=`failed_no_fallback`，因此没有覆盖基线，也没有把“发起过爬取”写成 live |
| 产品形态榜 | `product_form_hotness.json` 已由 378 条历史真实平台快照恢复：Top 10 为冰箱贴、徽章、盲盒、包挂、伴手礼、潮玩、香氛、挂件、首饰、毛绒；Top 5 为前五项。该榜只代表有限历史样本，不代表当前全平台实时趋势 |
| 对标案例 | 8 条 |
| LightRAG 实机图 | 612 个实体、697 条关系；“贵州苗绣”节点查询通过 |
| 策划输出 | 当前正式输出来自实机运行 `20260828T060200Z-e44240e3`：DeepSeek `deepseek-v4-flash` 实际生成 8 条 Opportunity Signals，随后执行证据白名单、六维评分与 LightRAG 二次核验；Top 3 为 OPP-006、OPP-002、OPP-004 |
| Design Agent | 自动模式从 Top 3 中选择 OPP-006，缩窄为“针格模块｜花溪挑花互动冰箱贴（概念样）”；工具支持人工从 8 条机会中选择 1–3 条、指定主机会、编辑交接/产品字段并生成带输入 SHA 的独立运行；没有匹配生成器时直接报错，不套用通用兜底模板 |
| 工厂首样拆解 | 5 项原型尺寸、5 项 BOM、1 组原创网格应用、6 步装配、6 项质检、3 个文化门、3 个工程门与 5 个工厂问题；不宣称量产就绪 |
| 设计海报 | 1800 × 2400；原创生成式成品/爆炸主视觉 + 本地精确中文排版；未使用 `reference_only` 馆藏像素 |
| Workbench Workspace | 默认 `guizhou-miao-demo` 以仓库基线初始化，后续写入 `data/runtime/workbench/`；Workspace Schema 1.1 保存 9 个节点、10 条连线、视口、当前 Concept、任务书、A/B/C、`DecisionProfile`、机器/人工并列的 `decision_output`、研究任务和设计运行引用。New / Save / Load / Rename / Save decisions 使用同一 JSON 校验与原子写入；研究晋级时保留仍有效的人工 ID，对消失的机会/品类只做带审计记录的补齐；源证据与运行态分离，页面操作不会覆盖仓库基线 |
| 图像生成适配 | Concept A 使用项目原创主视觉；Concept B/C 已通过内置图像生成能力制作、目视复核、SHA-256 登记并存入项目。独立 OpenAI-compatible Images API 自动化边界仍未配置，因此 Visual Generation 与单概念重生成继续诚实返回 `warning`，不会把内置资产冒充为 DeepSeek 新调用 |
| API | 本机与 Zeabur 服务端 LLM Key 均通过私密环境变量配置且不回显；探针确认 DeepSeek 可达、返回 3 个模型且 `deepseek-v4-flash` 可用。`POST /api/research/run` 返回 202 和持久化任务号，`GET /api/research/jobs/{id}` 提供回调轮询，API 重启会把未完成任务标为 interrupted 而不是成功；研究段与 Design Agent 已解耦，研究必须先完整保存组件/平台状态，设计再消费晋级后的交接。对同一服务的 `/images/generations` 实测为 HTTP 404，确认该密钥只承担文本模型链路 |
| 线上发布 | 0.8.0 受保护实例 `https://qiancraft-studio-2026.zeabur.app` 部署在 Zeabur California 专用服务器；部署 `6a91f49bac2577a93d22048d` 为 `RUNNING`，构建日志确认 Vinext 五阶段完成、`qiancraft-0.8.0` 安装成功，运行日志确认 Tool API 与 Vinext 分别监听容器回环地址。Nginx 统一 Basic Auth，`/healthz` 免鉴权，`/app/data/runtime` 挂载持久卷；公网健康检查为 200、匿名入口为 401。本轮执行环境没有站点凭证，0.8.0 认证后页面/API 保留待凭证复验 |
| MediaCrawler | 隔离运行时存在并可导入 xhs/dy/bili/wb；正式探针与网页严格任务均实际访问过平台。非正式探针现写入隔离目录，不再覆盖 canonical raw/derived；单平台达到时间上限时，若已保存至少 5 条有效内容则终止继续翻页并以“本轮部分 live”保留，否则为 `unavailable`。任何平台不是 live 时整轮不晋级，378 条历史快照继续保持 cache |
| 自动测试 | Python 46/46、Workbench TypeScript 5/5 通过 |
| 静态检查 | `ruff check app tests scripts/probe_market_platforms.py`、Web typecheck、ESLint、Vinext 五阶段 production build、`uv lock --check` 与 `git diff --check` 通过；九个节点页面共 129 条引用解析缺失为 0，454 个唯一外链实测 442 个直接返回、12 个因目标站连接/站点防护未直接返回但经官方搜索索引复核仍为真实页面。1440 × 960 与 390 × 844 页面无横向溢出，图片无破损；0.8.0 发布包 74 个文件、19,435,606 字节，敏感文件名与长 `sk-` 模式均为 0 命中 |
| 凭证检查 | 交付目录未发现 `sk-` 密钥泄漏 |

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

Creative Intelligence Workbench 在上述正式流水线之外增加一层可审计交互，不改写事实源：

```text
真实文件 / RunManifest / DesignPackage
       │
       └→ Tool API：Bootstrap + Workspace JSON + 节点详情 + 节点动作
                  │
                  ├→ Strict Research Job：202 后台任务 → 持久化 job.json → 前端轮询/刷新续接
                  │          ├→ 每轮独立 outputs/raw/derived，不读取 demo fallback
                  │          └→ 文化 + 策划 + xhs/dy/bili/wb 全部 live 才原子晋级
                  ├→ 证据中心：22 条文化记录 / 32 来源 / 四平台 378 快照 / Top 10
                  ├→ React Flow：Culture + Market → Strategy → Brief → Visual → A/B/C → Poster
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
| `auto` | 尝试 LightRAG live，允许明确回退 | 仅在显式开关及授权登录态齐备时逐平台抓取 | 尝试 GPT Researcher + DeepSeek，允许明确回退 | 原创主视觉存在时海报标 `live` | 默认实机运行 |
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
| `app/tool_api.py` | 工具 API、真实计数、分页来源查询、节点专用详情、七阶段人工决策写入、严格预检、202 后台研究任务/轮询/中断恢复、设计运行与资产路由 | 本地或容器内只绑定回环地址并由受保护代理转发；不得向前端返回凭证；job 异常必须脱敏并持久化；历史、当前、live、cache、系统推荐和人工选择必须分开标注 |
| `app/workbench.py` | 7 类节点注册、默认贵州苗绣链路、Workspace Schema 1.1 校验/兼容迁移/原子保存、DecisionProfile 校验/人工排序/下游 stale、研究晋级、Concept 动作、真实 Poster 渲染、文化/市场/馆藏/平台记录引用目录与详情组装 | 只有隔离运行中的文化/市场/策划和四平台全部 live 才可晋级；人工选择只在新结果中 ID 消失时带审计补齐。节点类型、状态、连线、引用、Concept 与资产路径均须服务端校验；馆藏 `reference_only` 不得改写为可用像素 |
| `data/culture/` | 文化图谱、视觉参考和 LightRAG 存储 | 事实先写结构化图谱；视觉图像权利与来源分开记录 |
| `data/market/` | 核验基线、`raw/` 原始抓取、`derived/` 派生证据 | 未披露互动数保持为 0；原始与派生不可混写 |
| `data/design/assets/` | 原创生成式成品/爆炸主视觉 | 不保存馆藏参考图像；每项正式使用资产必须进入渲染摘要 |
| `data/benchmark/` | 对标案例 | 案例只提供方法启发，不直接变成产品答案 |
| `data/demo_cache/` | 明确标注的稳定回退 | 缓存更新时间和生成模式必须可追踪 |
| `data/outputs/` | 最新13项正式结果 | JSON 是机器契约；Markdown 从同一对象渲染；海报与输入摘要可复核 |
| `data/tool_workspace/` | 仓库随附的旧版工具基线与可审计示例 | 作为只读初始化/历史证据；新运行不再写入该目录 |
| `data/workbench/` | 仓库随附的 Workspace Schema 1.1 与 A/B/C 概念视觉基线 | 作为首次启动模板；浏览器写入不得覆盖该目录 |
| `data/runtime/workbench/` | 实际 Workspace、研究晋级产物、DesignPackage、概念版本与海报 | 被 Git 忽略并在容器挂载持久卷；每个工作区/运行使用受校验目录，JSON 原子写入，不保存 Base64 或凭证 |
| `data/runtime/tool_workspace/` | 严格研究 `job.json`、每轮隔离 raw/derived/outputs 与旧版工具的实际设计运行 | 后台任务、失败审计和设计运行都保留独立 ID；非正式平台探针另写隔离目录，不覆盖 canonical 证据 |
| `scripts/` | 正式流水线、工具 API/一键启动、环境探针、四平台 Smoke Test 与显式授权入口 | 登录和工具启动命令变化同步维护本文件“标准命令” |
| `tests/` | 数据、证据、降级与端到端契约 | 修复缺陷时优先增加回归测试 |
| `docs/` | 专题说明与阶段性产品材料，包含人工决策契约、排版令牌、画布比例和视觉验收基线 | 本文件保留总览，专题细节链接到 docs |
| `docs/assets/` | GitHub README 等文档专用视觉资产 | 只放项目自有或已获许可素材；保持相对路径与无障碍文本 |
| `PRODUCT.md`、`DESIGN.md` | 产品意图、核心工作流与长期设计宪法 | 产品角色、信息优先级、视觉令牌或交互原则改变时同步维护；不得让文档与实际 CSS/组件漂移 |
| `.impeccable/` | 机器可读设计契约、界面简报、成品截图与资产来源记录 | Detector 每轮最多运行一次；截图只作审阅证据，不把外部参考资产混入正式产品素材 |
| `web/` | 暖纸色 Creative Intelligence Workbench、五阶段导航、上下文 Dock、七阶段 Human Decision Studio、React Flow 节点、9 个动态详情页、证据台账、Inspector、API Client、Workspace UI、Canvas PNG 导出与自托管中文排版系统 | 使用 Vinext/React/Sites 构建；颜色/间距/圆角/阴影优先引用 `variables.css` 令牌；页面不得硬编码事实计数，不把历史/cache 写成 live，不使用 `reference_only` 馆藏像素；内部跳转必须保留 workspace 与 decision 参数；手机端核心触控目标至少 44px，覆盖层必须转移并归还焦点，范围滑杆必须同时提供可精确输入的数值控件 |
| `Dockerfile`、`deploy/` | Zeabur 单容器构建、Nginx 鉴权/反代、Vinext 与 Tool API 进程编排、健康检查 | Basic Auth 哈希只在启动时生成；worker 仅可读哈希文件；`/healthz` 之外不得绕过鉴权；运行态写入挂载卷 |
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
- MediaCrawler 使用独立 `.venv-qiancraft`，避免固定依赖版本污染主环境。
- MediaCrawler 的上游许可证限制为非商业学习/研究。商业化前必须取得书面授权，或换成具备适当许可及平台授权的数据实现。
- XYFlow / React Flow 以 `@xyflow/react@12.11.5` 进入 Web 依赖，上传源码与 MIT LICENSE 保留在 `flow/xyflow-main/`；产品 UI 不需要展示供应链叙事，但仓库内归属和许可证不得删除。
- 上游许可证差异和处理方式以 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 为准。
- 文化转译遵循共同创作、明确署名、透明授权、公平收益和持续知情同意原则。

## 7. 标准环境与命令

### 7.1 主运行时

```powershell
uv venv --python 3.13
uv pip install -e ".[test]"
uv pip install -e ".\local_culture\LightRAG-main"
uv pip install -e ".\researcher_agent\gpt-researcher-main"
```

### 7.2 MediaCrawler 隔离运行时

```powershell
uv venv --python 3.13 ".\market-intel_agent\MediaCrawler-main\.venv-qiancraft"
uv pip install --python ".\market-intel_agent\MediaCrawler-main\.venv-qiancraft\Scripts\python.exe" -r ".\market-intel_agent\MediaCrawler-main\requirements.txt"
```

上游 `pyproject.toml` 当前使用不符合 PEP 621 校验的单数 `author` 字段，因此不做 editable install；QianCraft 直接调用源码入口。

### 7.3 本地工具工作台

```powershell
# 首次安装前端依赖
cd web
pnpm install
cd ..

# 同时启动本地真实数据 API 与 Web 工作台
.\.venv\Scripts\python.exe scripts\run_web_tool.py

# 或分开启动，便于调试
.\.venv\Scripts\python.exe scripts\run_tool.py
cd web
pnpm dev

# Workbench 前端验收
pnpm test
pnpm typecheck
pnpm lint
pnpm build
pnpm start:local
```

工作台默认为 `http://localhost:3000/`，本地 API 为 `http://127.0.0.1:8787/`。前端只通过 HTTP 使用真实 Python 数据；Workspace、研究任务、设计运行与生成资产写入被 Git 忽略的 `data/runtime/`，`data/workbench/` 和 `data/tool_workspace/` 仅作首次初始化/历史基线。工作台会持久化节点坐标、视口、任务书版本、DecisionProfile 版本、人工量分输出、当前采用方向、海报编排、后台任务和运行状态。五阶段导航负责聚焦链路，工具轨按需打开证据/资产/历史 Dock，节点选择联动画布与 Inspector；手机端外周面板变成可关闭覆盖层，打开时转移焦点，Escape 关闭后归还触发器。Human Decision Studio 可从顶部、工具轨、证据 Dock、画布、Inspector 或任一节点详情页进入；URL 使用 `?workspace=<id>&decision=<stage>` 恢复上下文。图像服务缺项时 Visual Generation 与单 Concept 操作明确进入 `warning`，不会用占位图冒充新生成。严格实时研究要求完整上游配置；缺项时阻断，不走兜底，运行中刷新页面会从服务端任务号续接。

### 7.4 安装 API 与探针

```powershell
.\.venv\Scripts\python.exe scripts\check_environment.py --install-api --probe-api
.\.venv\Scripts\python.exe scripts\check_environment.py --probe-mediacrawler
```

### 7.5 运行与验收

```powershell
.\.venv\Scripts\python.exe scripts\run_demo.py --mode demo
.\.venv\Scripts\python.exe scripts\run_demo.py --mode auto
.\.venv\Scripts\python.exe scripts\run_demo.py --mode live
# 接入项目内原创主视觉并运行完整链路
.\.venv\Scripts\python.exe scripts\run_demo.py --mode auto --design-hero data\design\assets\huaxi_grid_magnet_hero_v1.png
# 只重跑 Designer Handoff 后的设计与海报，并同步运行清单
.\.venv\Scripts\python.exe scripts\run_design_agent.py --hero-image data\design\assets\huaxi_grid_magnet_hero_v1.png --update-run-manifest
.\.venv\Scripts\python.exe -m pytest
uv run ruff check app tests
```

网页“实时运行”会调用 `POST /api/research/run`；状态由 `GET /api/research/jobs/{jobId}` 返回。它是长任务，不应通过重复 POST 轮询。只有返回 `live_verified` 后，工作台才继续执行 Brief/Design Agent 与 Poster。

### 7.6 四平台探测与用户显式授权

```powershell
# 无交互状态探针，不打开浏览器
.\.venv\Scripts\python.exe scripts\probe_market_platforms.py

# 首次授权逐个平台执行，依次把 platform 改成 xhs、dy、bili、wb
.\.venv\Scripts\python.exe scripts\probe_market_platforms.py --platform xhs --method cdp --authorize

# 四平台授权后统一复核正式小规模抓取
.\.venv\Scripts\python.exe scripts\probe_market_platforms.py --platform all --method cdp --formal --authorize
```

可把 `cdp` 换成 `qrcode`；Cookie 模式使用四个独立环境变量。只有用户确认平台条款、上游许可和用途后才执行。单平台只有实际登录、搜索并保存至少 5 条带 ID 和互动字段的真实结果后才是 `live/authorized`；历史真实快照只能是 `cache`，没有快照则是 `unavailable`。

### 7.7 容器与 Zeabur 发布验收

```powershell
# 本地存在 Docker 时可先构建同一生产镜像
docker build -t qiancraft:0.8.0 .

# Zeabur CLI 在已选择项目/环境/服务后上传精简发布目录
npx --yes zeabur@latest deploy --service-id <service-id> --environment-id <environment-id> --interactive=false

# 发布后同时验证免鉴权健康检查和受保护入口
Invoke-WebRequest https://qiancraft-studio-2026.zeabur.app/healthz -UseBasicParsing
Invoke-WebRequest https://qiancraft-studio-2026.zeabur.app/ -UseBasicParsing
```

生产发布使用 `.dockerignore` 排除原始平台数据、上游源码、测试缓存与本地密钥；部署变量由 Zeabur Secret 管理，不使用 `variable list` 等可能回显值的命令。发布成功必须继续以认证请求检查 Bootstrap、九个节点详情、静态资源与至少一个独立节点动作，单看平台“RUNNING”状态不算验收完成。完整拓扑见 [`docs/deployment_zeabur.md`](docs/deployment_zeabur.md)。

## 8. 每次更新的完成定义

一次更新只有在以下条件全部满足时才能交付：

- [ ] 改动符合用户授权范围，没有顺手扩大到无关系统。
- [ ] 相关数据契约、目录、配置和降级逻辑保持一致。
- [ ] 文化与市场事实都有来源，推断被明确标注。
- [ ] 没有删除或隐藏第三方许可证和版权信息。
- [ ] 凭证没有进入代码、数据、文档、日志或输出。
- [ ] 已运行与风险相称的测试、静态检查或实机探针。
- [ ] 正式输出需要更新时，已生成新的 JSON、Markdown 和 RunManifest。
- [ ] 涉及 Design Agent 时，已核对交接 SHA-256、证据编号、量产状态、参考像素声明、海报尺寸与渲染摘要。
- [ ] 涉及 Workbench 时，已核对 7 类节点契约、9 个默认实例的详情页、引用解析/缺失审计、Workspace Schema 1.1 与旧数据兼容、DecisionProfile 版本/ID 白名单/权重归一化、系统分和人工分并列、节点阶段深链、下游 stale 传播、严格研究 202/轮询/刷新续接/全 live 晋级门、Brief 实际 DesignPackage、Concept 旧资产标识、Poster 实际渲染和真实 API 错误态。
- [ ] 涉及前端排版时，已核对用户暖纸色令牌与实际组件一致、中文字体实际加载、画布可读比例、1440px 桌面及 390px 手机工作台/Decision Studio/节点详情、页面级横向溢出、44px 触控目标、可访问名称与覆盖层焦点闭环。
- [ ] 涉及上线时，已核对匿名鉴权、健康检查、认证后页面/API、持久卷目录、运行日志和部署域名；不能只依据平台状态声明完成。
- [ ] 本文件的当前状态、受影响章节和更新日志已经同步维护。
- [ ] 最终回复指出本文件的位置和本次新增日志。

## 9. 更新日志

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

- Human Decision Studio 已让文化、市场、机会、量分、任务书、视觉、概念和海报具备人工可变输入；下一步可在不改事实层的前提下增加 DecisionProfile 命名版本、差异对比、撤销/重做、多人批注和方案分支合并。
- Workbench 的研究任务、Design Agent、DesignPackage 和 Poster 已形成可持久化本地闭环，刷新页面可续接研究轮询；独立图像自动化服务仍未配置。后续若要实际生成新的 Concept，需由用户提供兼容 Images API 的服务地址、模型和密钥并重新实测；旧成功资产必须继续和本轮结果分开标注。
- 当前 Zeabur 实例已通过 Nginx Basic Auth、回环 API、Secret 变量与持久卷形成受保护产品验证环境；若扩大为多人正式使用，仍需补用户级身份、权限审计、备份恢复、口令轮换、对象存储、任务队列和更细粒度限流。
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
- [`docs/human_decision_workflow.md`](docs/human_decision_workflow.md)
- [`docs/knowledge_graph.md`](docs/knowledge_graph.md)
- [`docs/market_intelligence.md`](docs/market_intelligence.md)
- [`docs/real_machine_test.md`](docs/real_machine_test.md)
- [`docs/typography_system.md`](docs/typography_system.md)
- [`docs/product_direction.md`](docs/product_direction.md)
