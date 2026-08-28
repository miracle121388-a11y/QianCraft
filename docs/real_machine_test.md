# QianCraft 实机验收记录

验收日期：2026-08-29（Asia/Shanghai）

最新完整业务运行：`20260828T060200Z-e44240e3`（运行号使用 UTC）；五个组件依次为 `live / cache / live / live / live`。Culture 使用本地 612 实体/697 关系图，Strategy 实际调用 `deepseek-v4-flash`，市场层没有再次访问平台，而是消费保存的 378 条历史真实平台快照，因此四路在该清单中均诚实标为 `cache`。Design Agent 随后以同一运行的 `designer_handoff.json` 重算并用项目原创产品主视觉完成最终海报，运行清单的设计与渲染状态已同步更新。

四个平台在逐平台授权 Smoke Test 中都至少成功过一次：小红书 `live/20`、抖音 `live/14`、B站 `live/20`、微博 `live/16`。最新授权正式复核证据为 `market_evidence_20260827T222055Z.json`；同一次四平台复核中，小红书 `live/authorized/115`、B站 `live/authorized/101`、微博 `live/authorized/148`，抖音本次未产出新内容，使用 `cache/missing/14` 的历史真实快照。合计 364 条当轮实时记录、14 条历史真实平台记录，再加 12 条不参与平台榜的公开核验基线，共 390 条证据记录。随后单独重试抖音仍未产出新内容，没有把缓存误报为实时成功。

本轮新增 Creative Intelligence Workbench 实机验收：本地 Python API 与 Web 前端真实连通，默认工作区为 `guizhou-miao-demo`，包含 9 个节点实例、10 条连线和严格 7 类节点。验证覆盖 Workspace 持久化、Brief v2、节点运行、下游 stale、Concept Use / Duplicate / Regenerate / Generate More、Poster 可逆编辑与 1800 × 2400 PNG 浏览器导出。验收产生的临时工作区已删除，默认工作区恢复为任务书 v1、Concept A 和最新实机运行号；本轮随后生成并接入 Concept B/C 两套审阅后的项目视觉。

0.5.2 排版实机验收覆盖 1280 × 720 工作台、文化、市场和海报详情页，以及 390 × 844 海报详情：Noto Sans/Serif SC 均随站点自托管，7–10px 硬编码字号清零，默认画布改为 0.82 阅读比例；手机页 `scrollWidth=390`、无横向溢出，控制台 warning/error 为 0。Zeabur 线上九个页面与九个详情 API 均为 200，129 条引用缺失为 0，字体 WOFF2 抽查为 200。

0.6.0 人工决策验收在隔离工作区实际完成七阶段操作：新增苗族蜡染记录、把四平台缩为三平台、将文化适配权重从 20 精确改为 35 并即时重排 8 条机会、把第三候选改为 OPP-007、修改目标人群和三种产品形态、加入 V009 研究参照并改为竖版画幅、将 Concept B 设为当前方向、移出 Concept C、采用工坊拆解主题并隐藏工艺板块。保存后版本由 v1→v2→v3，服务端将 115% 正向输入归一化为 `culture_fit=0.304348`，Brief/Visual/Concept/Poster 全部变为 `stale`；默认工作区未被验收数据污染，临时工作区已删除。详情页的人工决策深链接也已重载验证，能保留工作区 ID 并直接打开对应阶段。

0.7.0 前端验收把工作台从展示型 Demo 收敛为暖纸色 Creative Instrument：56px 五阶段导航、64px 工具轨、按任务切换的证据/资产/历史 Dock、React Flow 主画布和 320px Inspector 形成稳定工具骨架。0.7.1 进一步把用户提供的 Lovable DTCG 色彩关系锁定到工作台、Decision Studio 和节点详情全部 chrome：Parchment / Warm Sand 承担主次表面，Linen / Stone 承担两级边界，Dim Gray / Charcoal 承担文字，Interaction Indigo 只承担链接、选中、路径与焦点；Hero 渐变继续只登记。0.7.2 逐页删除装饰性中英双标题、重复摘要、重复状态、节点 ID 和默认展开的机器字段，把运行信息与方法 JSON 收入按需层，并修正移动端决策双栏、文化图谱裁切、编辑器溢出、BOM 固定宽表格与海报重复覆盖。0.7.3 固定全部画布节点的横向几何尺寸，选中时不再膨胀或位移，详情与操作由 Inspector 和独立展示页承接；同时移除详情页遗留的装饰性双轴网格。桌面 1440 × 960 与手机 390 × 844 实测节点均保持 62px 渲染高度、`transform:none` 且页面无横向溢出，Inspector 的完整页面/运行/从此运行入口可达。核心对比度为 16.47:1、6.18:1、5.83:1 和 6.84:1。

0.8.0 把本轮验收重点从“页面能展示”改为“动作确实执行”。Culture / Market / Strategy 的运行入口统一创建服务端持久化严格任务，返回任务号并由页面轮询；刷新页面后已实测恢复同一运行，API 重启则把未完成轮次标为 interrupted。每轮研究写入独立 raw/derived/outputs，只有文化、策划和四个平台全部为本轮 `live` 才晋级；普通节点动作不再读取旧 JSON 后伪造 success。Brief 已从当前 DecisionProfile 实际生成并保存 DesignPackage，Poster 已在服务端重新渲染 1800 × 2400 PNG；未配置图像 provider 时，Concept B 保留上次成功资产并明确标注“本轮未生成”。

严格任务从网页实际发起了三轮。`20260828T195153Z-ef72a358` 如实返回 `failed_no_fallback`；其中文化与策划 live、市场 cache，四平台均未晋级。`20260828T200911Z-b71cc7d1` 暴露研究函数错误地继续调用 Design Agent，导致不支持的 OPP-009 异常遮住了市场审计；该耦合已修复并增加回归。修复后的 `20260828T202303Z-2bae17ff` 用 9 分 41 秒完成，返回文化 live、策划 live、市场 cache，xhs/dy/bili/wb 均 unavailable，最终 `failed_no_fallback`；运行目录完整保存 8 项研究产物、四平台详情与 `strict_result.json`，没有 DesignPackage，也没有覆盖当前工作区。页面随后显示“实时链路未通过”，三个研究节点不再卡在 running。

## 环境

- Windows / PowerShell
- CPython 3.13.9
- `uv` 0.10.9
- 主虚拟环境：`.venv`
- MediaCrawler 隔离环境：`market-intel_agent/MediaCrawler-main/.venv-qiancraft`
- DeepSeek 目标模型：`deepseek-v4-flash`

## 验收结果

| 项目 | 结果 | 证据 |
|---|---|---|
| DeepSeek API | 通过 | `/models` 实际返回 3 个模型，目标模型存在；密钥未回显 |
| LightRAG | 通过 | 本地图实际索引 612 个实体、697 条关系；“贵州苗绣”节点查询返回关联边 |
| GPT Researcher | 通过 | external-context writer 实际调用目标模型并输出合法 JSON；最新完整业务运行经证据锁后得到 8 条机会 |
| MediaCrawler | 授权复核 3/4 实时通过 | 小红书 115、B站 101、微博 148 条均完成登录、搜索、规范化与保存；抖音两次均未产出新内容，保留 14 条历史真实快照并标 `cache` |
| Workbench 严格后台研究 | 通过（按失败口径） | 修复后任务 `20260828T202303Z-2bae17ff` 实际从网页启动并回调完成：culture/strategist live，market cache，四平台 unavailable，状态 `failed_no_fallback`。8 项研究产物与失败审计落盘、设计未被误调用、工作区未晋级；这证明失败会被完整保存而不是伪造成可用结果 |
| 四平台统一与热度 | 通过 | 四个快照共 378 条真实平台记录；统一榜单样本数为 378，Top 10 依次为冰箱贴、徽章、盲盒、包挂、伴手礼、潮玩、香氛、挂件、首饰、毛绒，Top 5 为前五项；本轮重算分数范围 36.6–57.3，均在 0–100 内 |
| Visual Reference Pack | 通过 | 12 条官方/权威馆藏参考、5 个 Pattern Primitive、3 组无伪造 HEX 的颜色关系；全部未明权利图片标为 `reference_only` |
| Opportunity Score | 通过 | 8–12 条机会均有六项正向分、文化风险和可解释综合分；20/20/20/15/15/10 加权后扣 20% 风险 |
| LightRAG 二次核验 | 通过 | 高分候选实际重载本地图并逐项查询；输出 `verified/warning/rejected`，拒绝项不能进入设计交接 |
| Designer Handoff | 通过 | 仅 Top 3，当前为 OPP-006、OPP-002、OPP-004，均为 `verified`；JSON 为设计阶段唯一机器输入，`next_owner=QianCraft Design Agent` |
| Design Agent 接口 | 通过 | 正式链路实际从文件重载 DesignerHandoff 并核对 SHA-256；网页 Brief 也实际执行运行 `20260828T201228Z-e646561b`，选择 OPP-006、保存 DesignPackage/Markdown/RenderManifest/海报并回写工作区。自动选案现在只从已有真实产品生成器可执行的候选中选择；人工明确选择无生成器的机会仍直接报错，不套用通用兜底 |
| 产品与工厂拆解 | 通过 | 输出“针格模块”互动冰箱贴概念样；5 项尺寸、5 项 BOM、1 组原创网格应用、6 步装配、6 项质检、3+3 审核门和 5 个工厂待确认问题完整，`mass_production_ready=false` |
| 设计海报 | 通过 | 1800 × 2400 PNG 含文化元素/风格、成品主视觉、爆炸拆解、尺寸、BOM 与工艺；本地精确中文排版，海报和主视觉 SHA-256 均入清单，`reference_only_images_used=false` |
| Workbench 数据契约 | 通过 | Bootstrap 返回 9 个实例、10 条边、7 种节点类型及 ResearchRuntime；Workspace、job、研究产物和设计运行写入 `data/runtime/`，仓库基线只用于初始化。New/Rename/Save、Decision v2、Brief v3、概念复制和海报渲染均完成真实 HTTP 往返 |
| 人工决策数据契约 | 通过 | `schema_version=1.1`；Bootstrap 返回 22 文化/4 平台/10 品类/8 机会/12 视觉参照/3 概念，DecisionProfile 保存、权重归一化、人工排序、版本递增与非法 ID 拒绝均完成验证 |
| 九节点独立展示页 | 通过 | 文化、市场、策略、任务书、视觉、A/B/C 与海报逐页实际打开；引用分别为 28/39/15/7/8/8/8/8/8，合计 129 条且缺失为 0；所有页面无破图、无横向溢出、无“载入失败”，运行/从此运行/导出入口按能力可达 |
| 外部引用可达性 | 分层通过 | 扫描数据层 454 个唯一公开 URL：442 个直接 GET 可达；12 个因目标站连接或站点防护未直接返回，分别来自贵州日报/人民网转载链、全国人大和中国丝绸博物馆等真实官方页面，经搜索索引复核仍存在。未把暂时不可直连写成“来源不存在” |
| Workspace 与节点运行 | 通过 | 隔离 HTTP 实测 New/Rename/Save、Decision v2、Brief v3、独立 Design Agent、Concept 复制/单体重生成和 Poster 服务端渲染；缺 provider 的 Concept 为 warning 且保留旧资产，研究节点直接普通 POST 返回 409，防止旧文件伪装本轮结果。节点状态和仅下游 stale 均持久化到经过校验的 JSON |
| Workbench 浏览器交互 | 通过 | 顶部“实时运行”从页面实际发起 202 后台任务；刷新后同一 job 自动续接，运行中入口禁止重复创建。五阶段导航、Dock、画布、Inspector、九个详情页、Design Agent、Concept warning 和 Poster 实际渲染均已浏览器点击；失败后从服务端 Bootstrap 恢复节点状态，不把研究节点永久卡在 running |
| 七阶段人工交互 | 通过 | 浏览器实际完成文化、平台、权重、机会、任务书、视觉、方案与海报调整；保存后节点显示 HUMAN v3、人工分与系统分并列、下游 stale，展示页可深链返回对应决策阶段 |
| 中文排版、令牌与响应式 | 通过 | 0.7.3 保留暖纸色系统与单一中文标签，并把 9 个画布实例统一为稳定横条；1440 × 960 实测全部节点渲染高度为 62px，切换选择前后尺寸不变、`transform:none`，Inspector 仍绑定正确节点并提供完整页面/运行/从此运行。390 × 844 无页面横向溢出；0.7.2 已完成的手机端文化图谱、任务书、三套概念 BOM、海报和决策表单复核继续有效 |
| Workbench production server | 通过 | Vinext 五阶段构建后以 `127.0.0.1:3000` 启动 production server；页面、真实 API、A/B/C 资产与 Flow Map 均重新验收，React Flow 合法最小 attribution 保留 |
| Zeabur 线上实例 | 通过（分层验收） | 0.6.0 曾完成认证后首页、Bootstrap、9 个节点页/详情 API 与独立 Culture 公网验收；0.7.3 部署 `6a91df9a13d3d467215e7737` 为 `RUNNING`，远端日志确认 `qiancraft-0.7.3` 安装及容器启动，公网 `/healthz` 为 200、匿名入口为 401。本轮执行环境没有站点凭证，因此 0.7.3 的认证后页面/API 结论仅保留为待凭证复验，不以本地结果替代 |
| 概念视觉 A/B/C | 通过 | A 使用项目原创主视觉；B/C 由内置图像生成能力按任务书制作并完成目视复核，版本化 PNG、提示摘要与 SHA-256 均落盘；未请求复制具名神圣纹样或馆藏参考像素 |
| 图像生成边界 | 预期 warning | 独立 Images API 未配置；同一 DeepSeek 服务的 `/images/generations` 实测 HTTP 404。现有 A/B/C 可展示，但 Regenerate 与 Generate More 不会把项目资产冒充为一次新 API 结果 |
| 离线回退 | 通过 | 生成 8 条证据规则机会；设计段继续运行，无主视觉时本地几何海报诚实标为 `cache` |
| 自动测试 | 通过 | Python `pytest` 46/46；Workbench TypeScript 5/5；新增覆盖研究段不调用 Design Agent、仅凭研究产物晋级、部分实时记录保留、无生成器自动选案、严格预检、当前决策 DesignPackage、真实 Poster 与失败状态回归 |
| 静态检查与构建 | 通过 | `ruff check app tests scripts/probe_market_platforms.py`、TypeScript no-emit、ESLint 与 Vinext 五阶段 production build 均无错误；脚本入口的显式 `sys.path` bootstrap 不纳入 E402 检查 |
| 最终契约与凭证 | 通过 | 策略、视觉、交接、设计、渲染、热度和运行清单均可重新载入；13 个输出路径存在、四路市场状态完整、输入及海报摘要一致；自有交付层 API Key 模式扫描 0 命中 |

## 可复现命令

```powershell
.\.venv\Scripts\python.exe scripts\check_environment.py --probe-mediacrawler --probe-api
.\.venv\Scripts\python.exe scripts\run_demo.py --mode demo
.\.venv\Scripts\python.exe scripts\run_demo.py --mode auto
.\.venv\Scripts\python.exe scripts\run_demo.py --mode live
# 用当前原创产品主视觉运行完整设计段：
.\.venv\Scripts\python.exe scripts\run_demo.py --mode auto --design-hero data\design\assets\huaxi_grid_magnet_hero_v1.png
# 只重跑 Designer Handoff 之后的设计和海报，并同步清单：
.\.venv\Scripts\python.exe scripts\run_design_agent.py --hero-image data\design\assets\huaxi_grid_magnet_hero_v1.png --update-run-manifest
# 不打开浏览器的四平台状态探针：
.\.venv\Scripts\python.exe scripts\probe_market_platforms.py
# 用户准备好逐平台登录时才执行，平台依次改为 xhs/dy/bili/wb：
.\.venv\Scripts\python.exe scripts\probe_market_platforms.py --platform xhs --method cdp --authorize
# 四个平台完成授权后的正式小规模复核：
.\.venv\Scripts\python.exe scripts\probe_market_platforms.py --platform all --method cdp --formal --authorize
.\.venv\Scripts\python.exe -m pytest
uv run ruff check app tests

# 启动本地 Workbench（自动协调 API 与前端）：
.\.venv\Scripts\python.exe scripts\run_web_tool.py

# 前端独立验收：
cd web
pnpm test
pnpm typecheck
pnpm lint
pnpm build
pnpm start:local
```

## 已识别边界

1. MediaCrawler 的上游 `pyproject.toml` 使用单数 `author`，不能通过当前 PEP 621 editable build；隔离环境改按上游 `requirements.txt` 安装并直接调用源码入口，未修改上游文件。
2. MediaCrawler 的许可证限制为非商业学习/研究。本次只复用了用户本人完成的四个平台独立 CDP 会话；商业实抓仍需另行确认上游许可、平台条款和账号权限。
3. GPT Researcher 首次模型尝试曾返回空内容，上游重试后成功；QianCraft 仍保留项目级直连 DeepSeek 降级路径，并会在组件元数据中明确标注引擎。
4. 市场缓存来自公开、可点击来源。没有披露的社交互动指标全部为 0；真实互动分、机构信号分与 Derived Viral Score 分开，不把推测值冒充观测值。
5. 实机曾发现两类文化核验缺陷并已修复：禁用语句中的其他地域被误作来源主张，以及“花溪挑花 + 剑河迷宫核心图案”的跨支系串线。两者均新增回归测试。
6. 首次集成 Design Agent 时，单纯按综合分可能把鸟/蝶等高敏感母题优先视觉化；现已把 verified、文化敏感度、产品具体度和分数组成确定性选案顺序，并增加“有安全替代项时必须留置高敏感母题”的回归测试。
7. 正式输出共 13 个路径：原 8 项加 DesignPackage JSON/Markdown、PosterRenderRequest、设计海报和 DesignRenderManifest。流水线现在进入概念视觉与工厂首样简报，但仍在量产发布前停止。
8. 一次 CDP 授权通常可以复用本机浏览器资料，但不是永久授权；平台会话过期、主动退出、风控或资料目录被清理时需要本人重新登录。本轮抖音失败只证明当次搜索没有内容产物，不能据此把登录态断言为永久失效。
9. 当前海报、尺寸和 BOM 只支持展示、报价和首样沟通；花溪社区确认、材料/结构实测、DFM、适用标准测试和商业授权未完成，不能据此宣称可直接量产。
10. 当前四个平台的 378 条记录是历史真实快照。本轮 Workbench 确实重新访问了平台，但修复后严格任务没有获得可晋级记录，因此界面与工作区继续显示 `cache`；不能把曾经授权或“发起过请求”等同于本轮 live。
11. 独立图像生成自动化服务尚未配置。A/B/C 当前都有可展示项目资产，其中 B/C 来自此前内置图像生成与人工目视复核；这不代表 DeepSeek 支持图片。Regenerate / Generate More 会真实调用独立 provider，未配置时保留旧成功资产并明确 warning，不会制造新成功记录。
12. Workbench 已部署为受 Basic Auth 保护的远端产品验证环境；Vinext 与 Python API 在容器内仍只绑定回环地址，运行态由持久卷承载，密钥由部署变量注入。精简云端镜像没有 MediaCrawler/LightRAG/GPT Researcher 上游运行时，因此严格研究会预检阻断；完整实爬应在有本人授权浏览器的本机运行。如需多人正式使用，仍应补用户级账户、权限审计、备份、任务队列和密钥轮换流程。
13. 本轮使用上传的 React Flow 源码核对集成版本和能力边界，但没有改写其源码、许可证或版权通知；产品界面统一使用 QianCraft 自有名称和业务语言。
