# QianCraft 工作流程与持续更新记录

> 文档性质：项目级唯一工作流说明、当前状态快照与追加式更新台账  
> 当前版本：0.4.0  
> 最后维护：2026-08-28  
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
| 产品名称 | QianCraft｜黔艺前策 |
| 产品阶段 | 概念视觉与工厂首样简报；在量产发布前停止 |
| 本地工具工作台 | `web/` + `app/tool_api.py`；逐条查看文化/市场记录和来源、复算 8 条机会、自动或人工组装 Designer Handoff、编辑方案并真实触发设计规格与本地首样结构图生成；默认 `http://localhost:3000/`，API 为 `127.0.0.1:8787` |
| GitHub 展示 | 300 行项目 README；原创横版 SVG 首屏、4 个真实静态徽章、成果海报、Mermaid 架构、快速开始、可信边界、路线图与许可证说明 |
| 默认主题 | 贵州苗绣 |
| 默认目标市场 | 18–30 岁年轻消费者 |
| 文化知识图谱 | 22 条结构化文化记录、32 条文化/伦理/法律/馆藏视觉来源 |
| 苗绣检索 | 同时保留花溪挑花、剑河锡绣、松桃苗绣与雷山工艺差异 |
| 视觉参考包 | 12 条权威参考、5 个 Pattern Primitive、3 组无伪造 HEX 的文字色彩关系；默认 `reference_only` |
| 市场研究层 | 12 条结构化市场信号、12 条公开可追溯来源 |
| 市场状态 | 最新 demo 运行未访问平台，四平台均为 unavailable，当前运行只有 12 条公开核验基线；历史派生快照 `market_evidence_20260827T225613Z.json` 可核验 378 条社交记录（xhs 115、dy 14、bili 101、wb 148），但当前克隆缺少对应 `data/market/raw/*.jsonl`，因此工作台明确标记为“历史派生快照”，不标成当前实时抓取 |
| 产品形态榜 | 当前 `product_form_hotness.json` 已被 demo 刷新为空榜，不能把历史 Top 10 冒充当前榜单；历史 378 条记录仍可在工作台逐条查看，重新形成榜单必须完成一次严格实时运行或显式选择历史快照重新派生 |
| 对标案例 | 8 条 |
| LightRAG 实机图 | 612 个实体、697 条关系；“贵州苗绣”节点查询通过 |
| 策划输出 | 最新 demo 运行 `20260828T031637Z-fb206d5d` 含 8 条 Opportunity Signals；本轮 `generated_opportunities_accepted=0`，即 8 条全部来自代码内证据规则基线，随后真实执行六维评分与二次核验；Top 3 为 OPP-006、OPP-004、OPP-002 |
| Design Agent | 自动模式从 Top 3 中选择 OPP-006，缩窄为“针格模块｜花溪挑花互动冰箱贴（概念样）”；工具支持人工从 8 条机会中选择 1–3 条、指定主机会、编辑交接/产品字段并生成带输入 SHA 的独立运行；没有匹配生成器时直接报错，不套用通用兜底模板 |
| 工厂首样拆解 | 5 项原型尺寸、5 项 BOM、1 组原创网格应用、6 步装配、6 项质检、3 个文化门、3 个工程门与 5 个工厂问题；不宣称量产就绪 |
| 设计海报 | 1800 × 2400；原创生成式成品/爆炸主视觉 + 本地精确中文排版；未使用 `reference_only` 馆藏像素 |
| API | 当前本机未配置 `LLM_API_KEY`；历史记录中的 DeepSeek 探针通过不代表本次会话可用。严格研究入口因此处于 BLOCKED，不会使用规则基线兜底 |
| MediaCrawler | 当前克隆未安装 `.venv-qiancraft`、`MEDIACRAWLER_LIVE_ENABLED=false`，且原始四平台 JSONL 不存在；历史派生快照可查，但本机实时抓取未就绪 |
| 自动测试 | 22/22 通过 |
| 静态检查 | `ruff check app scripts tests` 通过 |
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

本地工具工作流在上述正式流水线之外增加一层可审计交互，不改写事实源：

```text
真实文件 → Tool API 实时计数/分页读取 → Web 工作台逐条核验
       └→ 机会分数按正式权重复算 → 系统 Top 3 或人工选择 1–3 条
                                      └→ 落盘 DesignerHandoff 草稿 + SHA-256
                                             └→ Design Agent 匹配真实生成器
                                                    ├→ 有匹配：DesignPackage + 本地首样结构图 + 独立运行记录
                                                    └→ 无匹配：明确失败，不套通用模板
```

工具的“严格实时研究”先检查 LLM、MediaCrawler 开关/运行时与 LightRAG；未就绪时阻断。即使预检通过，运行后也必须确认文化、市场、策划和四个平台全部为 `live`，否则该轮只保留失败审计，不晋级为可用结果。

## 3. 运行模式与降级

| 模式 | 文化层 | 市场层 | 策划层 | 设计与海报 | 使用场景 |
|---|---|---|---|---|---|
| `demo` | 结构化图谱 | 公开核验基线；四平台真实快照存在时只标 `cache` | 本地证据规则 | Design Agent 本地运行；无主视觉时几何海报标 `cache` | 离线验收、开发和稳定演示 |
| `auto` | 尝试 LightRAG live，允许明确回退 | 仅在显式开关及授权登录态齐备时逐平台抓取 | 尝试 GPT Researcher + DeepSeek，允许明确回退 | 原创主视觉存在时海报标 `live` | 默认实机运行 |
| `live` | 上游失败报错 | 未授权时仍使用合规缓存；授权失败写清状态 | 模型失败报错 | 保持同一证据锁与量产前门禁 | 严格集成测试 |
| `tool-strict` | 必须 live | 四平台必须全部 live，任何 cache/unavailable 均失败 | 必须 live 且模型建议通过契约 | 只消费本轮通过的文件交接；无生成器即失败 | Web 工具中的“严格实时研究” |

组件统一状态为 `live|cache|unavailable`，登录状态为 `authorized|missing|expired`，不能互相冒充。当前项目没有使用 mock 数据。

## 4. 目录和职责

| 路径 | 职责 | 更新注意事项 |
|---|---|---|
| `app/config.py` | 模式、路径、API、Cookie 与安全配置 | 新增环境变量时同步 `.env.example`、README 和本文件 |
| `app/schemas.py` | 全系统唯一数据契约 | 字段改变必须补迁移、测试和输出兼容说明 |
| `app/adapters/` | 隔离三个上游运行时 | 产品层不得依赖上游内部对象；凭证不得出现在命令行和日志 |
| `app/strategist/` | 唯一策划师、固定任务提示与证据锁 | 不允许生成最终设计；文化/市场事实不可被模型覆盖 |
| `app/designer/` | Design Agent、设计包 Markdown 与精确文字海报排版 | 只消费已落盘交接；不得使用 reference-only 像素或宣称量产就绪 |
| `app/pipeline.py` | 端到端编排、原子输出和运行清单 | 新步骤必须说明顺序、失败策略与状态字段 |
| `app/tool_api.py` | 本地工具 API、真实计数、分页来源查询、严格预检、工作区持久化与设计运行 | 只绑定回环地址；不得向前端返回凭证；历史、当前、live、cache 和规则基线必须分开标注 |
| `data/culture/` | 文化图谱、视觉参考和 LightRAG 存储 | 事实先写结构化图谱；视觉图像权利与来源分开记录 |
| `data/market/` | 核验基线、`raw/` 原始抓取、`derived/` 派生证据 | 未披露互动数保持为 0；原始与派生不可混写 |
| `data/design/assets/` | 原创生成式成品/爆炸主视觉 | 不保存馆藏参考图像；每项正式使用资产必须进入渲染摘要 |
| `data/benchmark/` | 对标案例 | 案例只提供方法启发，不直接变成产品答案 |
| `data/demo_cache/` | 明确标注的稳定回退 | 缓存更新时间和生成模式必须可追踪 |
| `data/outputs/` | 最新13项正式结果 | JSON 是机器契约；Markdown 从同一对象渲染；海报与输入摘要可复核 |
| `data/tool_workspace/` | 人工选择、机会/设计覆盖字段、独立 DesignerHandoff 草稿与工具生成历史 | 每次设计运行单独保存输入 SHA、主机会、引擎、是否使用图像生成和输出路径；不得覆盖历史运行 |
| `scripts/` | 正式流水线、工具 API/一键启动、环境探针、四平台 Smoke Test 与显式授权入口 | 登录和工具启动命令变化同步维护本文件“标准命令” |
| `tests/` | 数据、证据、降级与端到端契约 | 修复缺陷时优先增加回归测试 |
| `docs/` | 专题说明与阶段性产品材料 | 本文件保留总览，专题细节链接到 docs |
| `docs/assets/` | GitHub README 等文档专用视觉资产 | 只放项目自有或已获许可素材；保持相对路径与无障碍文本 |
| `web/` | QianCraft 本地工具前端：审计、信息仓库、机会池、人工选择/编辑、设计生成与运行记录 | 使用 Vinext/React/Sites 构建；页面不得硬编码事实计数，不把历史/cache 写成 live，不使用 `reference_only` 馆藏像素 |
| 三个上游源码目录 | 许可证审计和可替换运行时 | 不删除版权信息；非必要不直接修改上游 |

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

## 6. 凭证、许可证与文化合规

- `api.txt` 与 `.env` 已被 `.gitignore` 排除；任何文档、输出、异常和日志不得回显密钥。
- `scripts/check_environment.py --install-api` 只把本地 API 配置写入被忽略的 `.env`。
- MediaCrawler Cookie 通过隔离子进程环境传递，启动后立即从环境中移除，不进入进程命令行。
- 二维码或 CDP 登录只能由用户显式运行 `scripts/probe_market_platforms.py --authorize`；旧 `authorize_xhs.py` 只作兼容。普通策略运行默认不弹出浏览器。
- CDP 优先连接用户自己的本机浏览器端口；项目不绕过验证码、风控、访问控制或平台登录机制。
- MediaCrawler 使用独立 `.venv-qiancraft`，避免固定依赖版本污染主环境。
- MediaCrawler 的上游许可证限制为非商业学习/研究。商业化前必须取得书面授权，或换成具备适当许可及平台授权的数据实现。
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
```

工作台默认为 `http://localhost:3000/`，本地 API 为 `http://127.0.0.1:8787/`。也可以分别运行 `scripts/run_tool.py` 与 `web` 目录中的 `pnpm dev`。交付前执行 `cd web; pnpm build`。工具会持久化人工选择与独立设计运行，但严格实时研究仍要求完整上游配置；缺项时阻断，不走兜底。

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
uvx ruff check app scripts tests
```

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
- [ ] 本文件的当前状态、受影响章节和更新日志已经同步维护。
- [ ] 最终回复指出本文件的位置和本次新增日志。

## 9. 更新日志

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

- 四平台授权资料均已建立；最近正式复核中 xhs/bili/wb 为 live，dy 仅能复用 14 条历史真实快照。后续复测仍必须按每次实际结果写 `live/cache/unavailable`，不能因曾经授权而固定写 live。
- 当前 378 条真实平台快照已经形成 Top 10 / Top 5，可作为下一阶段候选品类输入，但样本规模、关键词和时间窗都有限，不能据此直接定案或宣称全平台趋势。
- MediaCrawler 仍缺少商业使用许可；现阶段只可在符合上游许可证和平台条款的非商业学习/研究场景使用。
- 文化图谱虽有权威公开来源，具体村寨的纹样名称、可公开范围、授权意愿与收益方式仍需田野核验。
- 当前已把 OPP-006 收敛为一个花溪互动冰箱贴概念并形成完整展示海报，但其数纱网格转译、地域/工艺表述、署名、收益与撤回机制仍需具体合作社区或保护单位确认。
- 当前尺寸、公差、BOM、装配和质检是工厂报价/首样输入，不是量产工程定稿。下一阶段应优先完成社区共审、用户测试、磁体封装/吸附力、卡合循环、绣线耐磨、跌落与适用标准验证，再决定 DFM、模具、成本和 SKU 扩展。

专题文档：

- [`docs/architecture.md`](docs/architecture.md)
- [`docs/design_agent.md`](docs/design_agent.md)
- [`docs/knowledge_graph.md`](docs/knowledge_graph.md)
- [`docs/market_intelligence.md`](docs/market_intelligence.md)
- [`docs/real_machine_test.md`](docs/real_machine_test.md)
- [`docs/product_direction.md`](docs/product_direction.md)
