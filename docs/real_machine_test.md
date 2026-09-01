# QianCraft 实机验收记录

验收日期：2026-09-01（Asia/Shanghai）

0.9.1 完整复验使用当前 Windows 工作区重新导入 LightRAG 1.5.7、GPT Researcher 0.14.7 与 MediaCrawler 隔离运行时；MediaCrawler 可导入 `bili,dy,ks,tieba,wb,xhs,zhihu`。当前机器与 Zeabur 服务器均已安全配置 LLM 凭证，DeepSeek `/models` 返回 200、3 个模型且目标 `deepseek-v4-flash` 存在；独立 Images API 与四平台授权会话仍未配置，因此没有把图片重生成或平台抓取写成当轮 live。正式 `20260828T060200Z-e44240e3` 保留此前真实 DeepSeek 业务运行证据。独立 `auto` 验收运行 `20260829T144536Z-2e6f3e5b` 实际得到 `culture=live / market=cache / strategist=cache / design=live / poster=live`，消费提交随附的 378 条派生平台证据并生成 13 项隔离产物；清单路径全部为仓库相对路径且文件存在。

同轮重新从正式 `DesignerHandoff` 运行 Design Agent 与 Poster Renderer，更新仓库默认 1800×2400 海报及摘要；BOM 标题按实际 5 项显示。8 个正式 JSON 契约、13 个清单路径、交接/海报 SHA-256、12 条视觉参考、5 个结构原语、8 条机会、Top 3、5 项 BOM、6 步装配、6 项质检、378 条热度样本与 Top 10 均通过审计，`mass_production_ready=false`、`reference_only_images_used=false`。正式运行清单及新生成的设计/渲染路径改为仓库相对路径，不再依赖旧机器盘符。

最新完整业务运行：`20260828T060200Z-e44240e3`（运行号使用 UTC）；五个组件依次为 `live / cache / live / live / live`。Culture 使用本地 612 实体/697 关系图，Strategy 实际调用 `deepseek-v4-flash`，市场层没有再次访问平台，而是消费保存的 378 条历史真实平台快照，因此四路在该清单中均诚实标为 `cache`。Design Agent 随后以同一运行的 `designer_handoff.json` 重算并用项目原创产品主视觉完成最终海报，运行清单的设计与渲染状态已同步更新。

四个平台在逐平台授权 Smoke Test 中都至少成功过一次：小红书 `live/20`、抖音 `live/14`、B站 `live/20`、微博 `live/16`。最新授权正式复核证据为 `market_evidence_20260827T222055Z.json`；同一次四平台复核中，小红书 `live/authorized/115`、B站 `live/authorized/101`、微博 `live/authorized/148`，抖音本次未产出新内容，使用 `cache/missing/14` 的历史真实快照。合计 364 条当轮实时记录、14 条历史真实平台记录，再加 12 条不参与平台榜的公开核验基线，共 390 条证据记录。随后单独重试抖音仍未产出新内容，没有把缓存误报为实时成功。

本轮新增 Creative Intelligence Workbench 实机验收：本地 Python API 与 Web 前端真实连通，默认工作区为 `guizhou-miao-demo`，包含 9 个节点实例、10 条连线和严格 7 类节点。验证覆盖 Workspace 持久化、Brief v2、节点运行、下游 stale、Concept Use / Duplicate / Regenerate / Generate More、Poster 可逆编辑与 1800 × 2400 PNG 浏览器导出。验收产生的临时工作区已删除，默认工作区恢复为任务书 v1、Concept A 和最新实机运行号；本轮随后生成并接入 Concept B/C 两套审阅后的项目视觉。

0.5.2 排版实机验收覆盖 1280 × 720 工作台、文化、市场和海报详情页，以及 390 × 844 海报详情：Noto Sans/Serif SC 均随站点自托管，7–10px 硬编码字号清零，默认画布改为 0.82 阅读比例；手机页 `scrollWidth=390`、无横向溢出，控制台 warning/error 为 0。Zeabur 线上九个页面与九个详情 API 均为 200，129 条引用缺失为 0，字体 WOFF2 抽查为 200。

0.6.0 人工决策验收在隔离工作区实际完成七阶段操作：新增苗族蜡染记录、把四平台缩为三平台、将文化适配权重从 20 精确改为 35 并即时重排 8 条机会、把第三候选改为 OPP-007、修改目标人群和三种产品形态、加入 V009 研究参照并改为竖版画幅、将 Concept B 设为当前方向、移出 Concept C、采用工坊拆解主题并隐藏工艺板块。保存后版本由 v1→v2→v3，服务端将 115% 正向输入归一化为 `culture_fit=0.304348`，Brief/Visual/Concept/Poster 全部变为 `stale`；默认工作区未被验收数据污染，临时工作区已删除。详情页的人工决策深链接也已重载验证，能保留工作区 ID 并直接打开对应阶段。

0.7.0 前端验收把工作台从展示型 Demo 收敛为暖纸色 Creative Instrument：56px 五阶段导航、64px 工具轨、按任务切换的证据/资产/历史 Dock、React Flow 主画布和 320px Inspector 形成稳定工具骨架。0.7.1 进一步把用户提供的 Lovable DTCG 色彩关系锁定到工作台、Decision Studio 和节点详情全部 chrome：Parchment / Warm Sand 承担主次表面，Linen / Stone 承担两级边界，Dim Gray / Charcoal 承担文字，Interaction Indigo 只承担链接、选中、路径与焦点；Hero 渐变继续只登记。0.7.2 逐页删除装饰性中英双标题、重复摘要、重复状态、节点 ID 和默认展开的机器字段，把运行信息与方法 JSON 收入按需层，并修正移动端决策双栏、文化图谱裁切、编辑器溢出、BOM 固定宽表格与海报重复覆盖。0.7.3 固定全部画布节点的横向几何尺寸，选中时不再膨胀或位移，详情与操作由 Inspector 和独立展示页承接；同时移除详情页遗留的装饰性双轴网格。桌面 1440 × 960 与手机 390 × 844 实测节点均保持 62px 渲染高度、`transform:none` 且页面无横向溢出，Inspector 的完整页面/运行/从此运行入口可达。核心对比度为 16.47:1、6.18:1、5.83:1 和 6.84:1。

0.8.0 把本轮验收重点从“页面能展示”改为“动作确实执行”。Culture / Market / Strategy 的运行入口统一创建服务端持久化严格任务，返回任务号并由页面轮询；刷新页面后已实测恢复同一运行，API 重启则把未完成轮次标为 interrupted。每轮研究写入独立 raw/derived/outputs，只有文化、策划和四个平台全部为本轮 `live` 才晋级；普通节点动作不再读取旧 JSON 后伪造 success。Brief 已从当前 DecisionProfile 实际生成并保存 DesignPackage，Poster 已在服务端重新渲染 1800 × 2400 PNG；未配置图像 provider 时，Concept B 保留上次成功资产并明确标注“本轮未生成”。

严格任务从网页实际发起了三轮。`20260828T195153Z-ef72a358` 如实返回 `failed_no_fallback`；其中文化与策划 live、市场 cache，四平台均未晋级。`20260828T200911Z-b71cc7d1` 暴露研究函数错误地继续调用 Design Agent，导致不支持的 OPP-009 异常遮住了市场审计；该耦合已修复并增加回归。修复后的 `20260828T202303Z-2bae17ff` 用 9 分 41 秒完成，返回文化 live、策划 live、市场 cache，xhs/dy/bili/wb 均 unavailable，最终 `failed_no_fallback`；运行目录完整保存 8 项研究产物、四平台详情与 `strict_result.json`，没有 DesignPackage，也没有覆盖当前工作区。页面随后显示“实时链路未通过”，三个研究节点不再卡在 running。

0.9.0 新增持续素材采集实机验收。Tool API 启动后 `/api/health` 返回调度线程在线、真实心跳与总开关；文化通道实际巡检 4 个登记来源，最终 4/4 可达、没有把通用导航写入候选，正式图谱仍保持 22 条记录/32 个来源。此前发现的 10 个同域链接经人工审核排除 9 个通用导航，保留 1 条真实待核验候选；候选没有自动晋级。市场通道两次预检均因 `MEDIACRAWLER_LIVE_ENABLED=false` 和四平台当前未连接授权浏览器而 `blocked`，没有启动伪研究任务，也没有改写 378 条历史快照。

前端使用 Playwright CLI 重新截取全部 10 个桌面路由，并重点复核 390×844 的文化星图与市场页。知识星图真实完成鼠标拖动、滚轮缩放、键盘平移、搜索聚焦；移动自动化真实滚动详情容器，并通过 CDP 单/双触点验证显式操作模式下的单指平移与捏合缩放，退出后恢复 `touch-action: pan-y pinch-zoom`。断线拦截验证 12 秒轮询失败后立即改为“采集控制面连接中断”、心跳显示中断且写操作禁用；forced-colors 下中心、普通节点与选中节点保持不同系统色。市场首屏先显示 378、四平台样本量、发布范围与检索日期，完整采集控制台折叠在后。

2026-08-31 对当前 0.9.1 再次完整验收：Python 58/58、Workbench TypeScript 5/5、desktop-chromium 31/31，Ruff、锁文件、typecheck、ESLint、Vinext 五阶段 production build 与启动脚本语法均通过。真实 Playwright CLI 会话加载隔离工作区，打开 Human Decision Studio、Delivery、Inspector 与 Poster 详情，控制台为 0 error / 0 warning；C2 本轮没有运行 mobile project。Zeabur 部署 `6a958619be05255ec5e261f7` 为 `RUNNING`，公网健康与匿名鉴权、服务器内认证后的首页/九详情页面、健康/Bootstrap/九详情/DesignPackage API、正式资产、持久卷、调度心跳和 LLM 模型探针均通过。隔离远端工作区实际完成保存、Decision v2、Design Agent、DesignPackage、Poster v2 和九详情页后已清理；严格研究按真实前置条件返回 422。

2026-09-01 的 0.9.2 发布前复验改用统一 Conda Python 3.13 环境：Python 77/77、Workbench TypeScript 5/5、macOS desktop-chromium 30 passed / 1 Windows 像素门按设计 skipped，Ruff、锁文件、typecheck、零 warning ESLint、Vinext 8.2.2 五阶段 production build 与启动脚本语法通过。完整 `pnpm audit` 和本地 Python `pip-audit` 均为 0 个已知漏洞。新增回归覆盖图像 provider 真实状态、无图形会话预检、空覆盖变量自动识别、私网/DNS/rebinding/重定向 SSRF 拒绝、Nginx 安全头/限流、Docker 上下文，以及运行态 ZIP 的 SHA-256 校验、路径穿越拒绝和原子恢复回滚。线上 0.9.2 在本段记录时尚未发布，因此不把本地结果写成远端通过。

同日发布收口：GitHub Actions 运行 `33417318879` 在 Ubuntu/macOS/Windows 全部通过，Windows desktop-chromium 为 31/31，4 个 Job 的 annotation 均为 0。Zeabur 部署 `6a95b5a29ed7d65609e27bf6` 实际构建并运行 `qiancraft-0.9.2`；公网健康 200、匿名门禁 401、认证后九路由/九 API、DesignPackage 与 4 项图像全为 200。隔离工作区真实完成 Design Agent、DesignPackage 和 322,090 字节海报；Regenerate/Generate More 在无 provider 时为 warning，严格研究为 422，临时数据已清理。Nginx 安全头、80 请求突发中的 38 个 429、非 root worker、ext4 持久卷和发布后可验证 ZIP 快照均通过；运行日志严重错误行为 0。

同日 0.10.0 把此前缺失的云端机器条件补齐。Docker 实际安装 LightRAG 1.5.7、GPT Researcher 0.14.7 与独立 MediaCrawler Python 环境，并启动 Xvfb、Openbox、Chromium、x11vnc 与 websockify；CDP 9222、VNC 5900、noVNC 6080 均只监听回环，公网 `/browser-auth/` 继续受 Basic Auth 保护。浏览器 profile 与 LightRAG 索引写入持久卷，普通运行态 ZIP 强制排除 profile。发布前本地实际通过 Python 80/80、Web 5/5、desktop-chromium 30 passed / 1 skipped、Ruff、锁、typecheck、lint、production build、Python/pnpm 依赖审计和 POSIX 启动脚本语法。

Zeabur 0.10.0 运行态实测不是“文件存在”口径：LightRAG 在持久卷建立 612 实体/697 关系索引并查询出 100 条主题边；GPT Researcher 使用 `deepseek-v4-flash` 返回指定 JSON，`engine=GPT Researcher external-context writer` 且未走项目直连降级；MediaCrawler 主入口和依赖检查通过；配置后的图像 provider 生成有效 1024×1024 PNG。研究预检、CDP/noVNC 和三个运行时已 ready，但四平台真实登录/搜索仍必须由维护者本人完成后逐平台判定，因此此处没有提前把 378 条历史快照改写为当轮 live。

用户完成云端四平台登录后，小规模真实探针得到小红书 20、抖音 14、B站 20、微博 16。探针首次揭示 `MEDIACRAWLER_PYTHON` 被通用路径解析解引用成 `/usr/bin/python3.11`，与已安装依赖的 `/opt/mediacrawler-venv/bin/python` 不同；现已保留虚拟环境入口，并让构建、启动、严格预检三处实际导入 `httpx` 与 CDP 管理器。部署 `6a964d01fff9450cc032d1ba` 的严格任务 `20260901T041626Z-3deaef24` 得到 culture/strategist live、xhs 60、bili 55、wb 65、dy 0，最终 `failed_no_fallback` 且未晋级。可见抖音搜索页显示登录提示而无安全验证，证明本轮缺口是抖音搜索会话未被平台接受，不是解释器、CDP 或全局浏览器故障。

部署 `6a96589cfff9450cc032d417` 新增抖音 DOM-ready 导航和共享页面精确清理：上游完整资源 `load` 不再造成 30 秒假超时，每轮只关闭自己创建的页面，不关闭持久 Chromium 或用户原有标签。当前本地 Python 85/85、Ruff、POSIX 语法和差异检查通过；远端构建、启动、解释器路径、预检和健康检查均通过。完整严格成功仍须抖音重新认证后复跑，不能把三平台正式结果与先前抖音探针拼成同一轮。

用户随后明确暂停抖音，不再处理交互验证码。最终部署 `6a96bdf25158a7aaa4e62007` 把本轮启用集合固定为 xhs / bili / wb；API、工作区晋级门和市场控制台都按同一精确集合判定，并保留 dy 适配器与历史数据但不参与任务。六关键词严格任务 `20260901T121642Z-e1a435ff` 在同一隔离运行中得到 xhs 113、bili 110、wb 149 条规范化实时记录，文化、市场与策划三个组件均为 `live`，最终 `live_verified` 并回写工作区；没有混入抖音历史、旧探针或 378 条仓库基线。任务结束后 CDP 页面恢复为原有 4 个，市场调度重新启用且线程、心跳、下次运行均正常。

0.10.0 本地实机把默认入口改为双库驱动 Studio。实际 API 返回文化 22 条/来源 32 条、产品形态 10 种/历史平台样本 378 条，并由启动补跑生成当天 3 个文化与形态均不重复的结构概念设计。首页、两库、自由组合、全部设计、运行中心、动态设计详情/编辑和 PNG 均经真实 HTTP 返回 200；非法文化 ID 返回 422。隔离 HTTP 验收完成手动组合 201、编辑重生成 V2 200，V1/V2 SHA-256 不同且两张 PNG 同时保留；本地查看新生成图确认 CJK 字体正常。当前本地 0.10.0 已完成 83/83 Python、5/5 Web 单测及静态/构建/依赖门；32 项 Windows desktop UI 与 Zeabur 远端结果仍须以本轮推送后的实际记录为准，本段不提前冒充线上通过。

同日完成团队 Studio 与本地 Zeabur 实时链路的合并验收。空白隔离运行目录冷启动后，设计归档会在每日补跑期间自动刷新，不再永久停留在 0 项；当前 Zeabur 和浏览器验收集合显式固定为 xhs/bili/wb，dy 保持暂停，通用 Demo 仍保留四平台历史基线；旧节点详情的工作台返回入口统一指向 `/workflow`。隔离 HTTP 实测 `/api/health` 同时确认两个调度器在线，22/10/378 与当日 3 项一致；手动组合 201、详情 200、编辑 V2 200、PNG 200，版本 SHA 不同且非法文化 ID 为 422。合并态本地通过 Python 98/98、Web 5/5、macOS desktop-chromium 31 passed / 1 个 Windows 像素门 skipped，以及静态、构建和依赖审计；Zeabur 仍是合并前部署，不能据此宣称 Studio 已上线。

## 环境

- macOS / zsh（本轮）与 Windows / PowerShell（既有权威像素基线）
- Conda `qiancraft` / CPython 3.13.15
- `uv` 0.12.7（只在 Conda 环境中执行锁文件检查）
- 主虚拟环境：Conda `qiancraft`，由 `environment.yml` 创建
- 团队 Studio 分支的历史实现记录为项目 `.venv` / CPython 3.12.13、Ruff 0.16.5、uv 0.12.8、Node.js 22.23.2、pnpm 11.19.0；合并后的本地验证仍统一使用仓库规定的 Conda 环境
- MediaCrawler：0.9.1 Windows 历史验收使用独立 `.venv-qiancraft`；本地标准使用独立 Conda 环境，Zeabur 0.10.0 使用 `/opt/mediacrawler-venv`，均由 `MEDIACRAWLER_PYTHON` 显式指向解释器
- DeepSeek 目标模型：`deepseek-v4-flash`

## 验收结果

| 项目 | 结果 | 证据 |
|---|---|---|
| DeepSeek API | 通过 | 当前 Windows 与 Zeabur 均通过安全环境变量读取凭证；`/models` 返回 200、3 个模型，目标 `deepseek-v4-flash` 存在。没有输出或写入密钥 |
| LightRAG | 通过 | 本地与 Zeabur 均实际索引 612 个实体、697 条关系；云端“贵州苗绣”查询返回 100 条关联边，索引位于持久卷 |
| GPT Researcher | 通过 | 0.14.7 在 Zeabur 实际调用 `deepseek-v4-flash`，返回指定 JSON，外部上下文 writer 成功且未走项目直连降级 |
| MediaCrawler | 当前三平台严格实采通过；抖音暂停 | 云端解释器固定为 `/opt/mediacrawler-venv/bin/python`，源码、`httpx`、CDP 管理器、托管 Chromium 均实测。最终启用 xhs/bili/wb，严格任务规范化记录为 113/110/149；dy 不启动、不参与晋级，适配代码与历史证据保留 |
| Workbench 严格后台研究 | 通过 | 云端任务 `20260901T121642Z-e1a435ff` 实际完成 culture/market/strategist live，且配置中启用的 xhs/bili/wb 全部 live，最终 `live_verified` 并原子晋级工作区；清单不含 dy，也未拼接旧探针或缓存 |
| Studio 双库与每日设计 | 本地通过；远端待发布 | API 实取文化 22/来源 32、形态 10/历史样本 378，并公开文化证据三分项、组合五分项、代表原记录、样本窗与边界。启动补跑产生当天 3 个去重设计；普通同日运行复用批次，明确重跑创建新批次并 supersede 旧批次。手动组合与 V2 编辑实际写出不同 SHA 的 1440×960 PNG，旧稿谱系和下载地址保留；零样本或来源/渲染器门不满足时明确失败 |
| 四平台统一与热度 | 通过 | 四个快照共 378 条真实平台记录；统一榜单样本数为 378，Top 10 依次为冰箱贴、徽章、盲盒、包挂、伴手礼、潮玩、香氛、挂件、首饰、毛绒，Top 5 为前五项；本轮重算分数范围 36.6–57.3，均在 0–100 内 |
| Visual Reference Pack | 通过 | 12 条官方/权威馆藏参考、5 个 Pattern Primitive、3 组无伪造 HEX 的颜色关系；全部未明权利图片标为 `reference_only` |
| Opportunity Score | 通过 | 当前正式文件为 8 条证据规则基线，`generated_opportunities_accepted=0`；全部具备六项正向分、文化风险和可解释综合分，20/20/20/15/15/10 加权后扣 20% 风险。历史模型候选数量不等于当前正式接受数 |
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
| 持续采集调度与候选门 | 通过 | 线上调度线程、心跳与总开关保持在线；文化候选仍经人工门。市场通道已在三平台严格成功后恢复启用，下一轮按 4 小时排期；浏览器连接仍不等于授权，只有本轮配置中启用的平台全部 live 才晋级 |
| 知识星图与采集控制面 | 当前桌面通过 | C2 desktop-chromium 覆盖星图搜索、选点、按钮/滚轮缩放、拖动/键盘、断线旧状态、历史/实时信息顺序、forced-colors 与焦点门；此前手机触摸结果只保留为历史基线，本轮没有执行 mobile project |
| 七阶段人工交互 | 通过 | 浏览器实际完成文化、平台、权重、机会、任务书、视觉、方案与海报调整；保存后节点显示 HUMAN v3、人工分与系统分并列、下游 stale，展示页可深链返回对应决策阶段 |
| 中文排版、令牌与响应式 | 当前桌面通过 | Studio 与旧 C2 使用暖矿物、雾蓝、灰绿、暖陶与浅石固定功能色块；旧工作台保留 60/72/210/330 电脑端几何、稳定九节点和深色文化星图例外。macOS 1440×960 当前为 31 passed / 1 个 Windows 像素门 skipped；mobile/tablet 沿用既有实现，但不属于本轮验收承诺 |
| Workbench production server | 通过 | Vinext 五阶段构建后以 `127.0.0.1:3000` 启动 production server；页面、真实 API、A/B/C 资产与 Flow Map 均重新验收，React Flow 合法最小 attribution 保留 |
| Zeabur 线上实例 | 通过 | 0.10.0 当前部署 `6a96bdf25158a7aaa4e62007`；公网 `/healthz` 200。容器内解释器路径、三运行时、CDP/noVNC、持久卷、0700 profile、图像 provider、三平台预检与严格晋级均已实测；浏览器进程和 API/Web worker 以 `www-data` 运行，登录资料不进入运行态 ZIP |
| 概念视觉 A/B/C | 通过 | A 使用项目原创主视觉；B/C 由内置图像生成能力按任务书制作并完成目视复核，版本化 PNG、提示摘要与 SHA-256 均落盘；未请求复制具名神圣纹样或馆藏参考像素 |
| 图像生成边界 | 通过 | Zeabur 独立图像 provider 已安全配置并实际生成 1024×1024 PNG；其他环境缺配置时仍保持 warning，不把旧 A/B/C 资产冒充新结果 |
| 离线回退 | 通过 | 生成 8 条证据规则机会；设计段继续运行，无主视觉时本地几何海报诚实标为 `cache` |
| 自动测试 | 本地通过；跨平台待本轮 CI | Python `pytest` 98/98、Workbench TypeScript 5/5；macOS desktop-chromium 31 passed / 1 个 Windows 像素门按设计 skipped。32 项 Windows 门等待本轮 GitHub Actions，不沿用旧 CI |
| 静态检查与构建 | 本地通过 | Conda 内 Ruff、`uv lock --check`、TypeScript no-emit、零 warning ESLint、Vinext 五阶段 production build、完整 `pnpm audit`、Python `pip-audit --local`、`sh -n deploy/start-zeabur.sh` 与 `git diff --check` 均通过；两类依赖审计为 0 个已知漏洞，跨平台结果等待本轮 CI |
| 最终契约与凭证 | 通过 | 策略、视觉、交接、设计、渲染、热度和运行清单均可重新载入；13 个输出路径存在、四路市场状态完整、输入及海报摘要一致；自有交付层 API Key 模式扫描 0 命中 |

## 可复现命令

```powershell
conda run --no-capture-output -n qiancraft python scripts\check_environment.py --probe-mediacrawler --probe-api
conda run --no-capture-output -n qiancraft python scripts\run_demo.py --mode demo
conda run --no-capture-output -n qiancraft python scripts\run_demo.py --mode auto
conda run --no-capture-output -n qiancraft python scripts\run_demo.py --mode live
# 用当前原创产品主视觉运行完整设计段：
conda run --no-capture-output -n qiancraft python scripts\run_demo.py --mode auto --design-hero data\design\assets\huaxi_grid_magnet_hero_v1.png
# 只重跑 Designer Handoff 之后的设计和海报，并同步清单：
conda run --no-capture-output -n qiancraft python scripts\run_design_agent.py --hero-image data\design\assets\huaxi_grid_magnet_hero_v1.png --update-run-manifest
# 不打开浏览器的配置平台状态探针：
conda run --no-capture-output -n qiancraft python scripts\probe_market_platforms.py
# 用户准备好逐平台登录时才执行；当前启用 xhs/bili/wb，dy 仅在以后恢复时单独授权：
conda run --no-capture-output -n qiancraft python scripts\probe_market_platforms.py --platform xhs --method cdp --authorize
# 配置中的启用平台完成授权后的正式小规模复核：
conda run --no-capture-output -n qiancraft python scripts\probe_market_platforms.py --platform all --method cdp --formal --authorize
conda run --no-capture-output -n qiancraft python -m pytest
conda run --no-capture-output -n qiancraft ruff check .
conda run --no-capture-output -n qiancraft python -m pip_audit --local

# 启动本地 Workbench（自动协调 API 与前端）：
conda run --no-capture-output -n qiancraft python scripts\run_web_tool.py

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
2. MediaCrawler 的许可证限制为非商业学习/研究。本次只复用了用户本人完成的平台 CDP 会话，当前启用小红书、B站和微博；商业实抓仍需另行确认上游许可、平台条款和账号权限。
3. GPT Researcher 首次模型尝试曾返回空内容，上游重试后成功；QianCraft 仍保留项目级直连 DeepSeek 降级路径，并会在组件元数据中明确标注引擎。
4. 市场缓存来自公开、可点击来源。没有披露的社交互动指标全部为 0；真实互动分、机构信号分与 Derived Viral Score 分开，不把推测值冒充观测值。
5. 实机曾发现两类文化核验缺陷并已修复：禁用语句中的其他地域被误作来源主张，以及“花溪挑花 + 剑河迷宫核心图案”的跨支系串线。两者均新增回归测试。
6. 首次集成 Design Agent 时，单纯按综合分可能把鸟/蝶等高敏感母题优先视觉化；现已把 verified、文化敏感度、产品具体度和分数组成确定性选案顺序，并增加“有安全替代项时必须留置高敏感母题”的回归测试。
7. 正式输出共 13 个路径：原 8 项加 DesignPackage JSON/Markdown、PosterRenderRequest、设计海报和 DesignRenderManifest。流水线现在进入概念视觉与工厂首样简报，但仍在量产发布前停止。
8. 一次 CDP 授权通常可以复用浏览器资料，但不是永久授权；平台会话过期、主动退出、风控或资料目录被清理时需要本人重新登录。抖音因交互验证码由用户明确暂停，当前任务不会访问它；恢复时仍须本人授权并重新完成严格验证。
9. 当前海报、尺寸和 BOM 只支持展示、报价和首样沟通；花溪社区确认、材料/结构实测、DFM、适用标准测试和商业授权未完成，不能据此宣称可直接量产。
10. 仓库四平台的 378 条记录仍是历史真实快照，不会被改写成本轮数据。线上工作区已由三平台严格任务晋级 372 条当轮规范化实时记录；两套口径必须分开，不能相加或把暂停的抖音写成本轮 live。
11. 独立图像生成服务已在 Zeabur 配置并通过真实 PNG 探针。A/B/C 既有资产仍与每次新调用分开记录；任何环境缺配置或调用失败时都保留旧成功资产并明确 warning，不制造新成功记录。
12. Workbench 已部署为受 Basic Auth 保护的远端产品验证环境；Vinext、Python API、CDP、VNC 与 noVNC 上游都只绑定回环，运行态由持久卷承载，密钥由部署变量注入。0.10.0 包含 MediaCrawler/LightRAG/GPT Researcher 和托管授权浏览器，但异地定时备份、用户级账户、权限审计、分布式任务队列、外部告警和密钥轮换仍是多人正式运营条件。普通 ZIP 不备份平台登录 profile，恢复或卷丢失后须本人重新登录。
13. 本轮使用上传的 React Flow 源码核对集成版本和能力边界，但没有改写其源码、许可证或版权通知；产品界面统一使用 QianCraft 自有名称和业务语言。
14. 0.9.0 引入的持续采集依赖 Tool API 单副本持续运行、持久卷、平台重启策略、网络和用户授权；它不是跨副本分布式队列。线上 0.10.0 的机器条件、线程、心跳与持久卷已验收，但只有配置中启用的平台每轮全部实际产出才是 `live_verified`，不能因浏览器在线就宣称每轮都会持续产出。
15. 0.10.0 的每日 Studio 设计同样依赖单副本常驻进程和持久卷；其 PNG 是带来源、评分和版本的结构概念稿，不是图像模型商品摄影、量产工程图或生产放行。市场库当前 378 条是历史真实快照，自动设计按时运行不等于配置中的实时平台每轮都已成功采集。
