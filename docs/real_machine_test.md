# QianCraft 实机验收记录

验收日期：2026-08-28（Asia/Shanghai）

最新完整业务运行：`20260827T225611Z-4f2a77ae`（运行号使用 UTC）；五个组件依次为 `live / cache / live / live / live`。市场层没有再次访问平台，而是消费本轮保存的 378 条真实平台快照，因此四路在该清单中均诚实标为 `cache`。Design Agent 随后以同一运行的 `designer_handoff.json` 重算并用原创产品主视觉完成最终海报，运行清单的设计与渲染状态已同步更新。

四个平台在逐平台授权 Smoke Test 中都至少成功过一次：小红书 `live/20`、抖音 `live/14`、B站 `live/20`、微博 `live/16`。最新授权正式复核证据为 `market_evidence_20260827T222055Z.json`；同一次四平台复核中，小红书 `live/authorized/115`、B站 `live/authorized/101`、微博 `live/authorized/148`，抖音本次未产出新内容，使用 `cache/missing/14` 的历史真实快照。合计 364 条当轮实时记录、14 条历史真实平台记录，再加 12 条不参与平台榜的公开核验基线，共 390 条证据记录。随后单独重试抖音仍未产出新内容，没有把缓存误报为实时成功。

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
| 四平台统一与热度 | 通过 | 四个快照共 378 条真实平台记录；统一榜单样本数为 378，Top 10 依次为冰箱贴、徽章、盲盒、包挂、伴手礼、潮玩、香氛、挂件、首饰、毛绒，Top 5 为前五项；分数范围 36.6–57.4，均在 0–100 内 |
| Visual Reference Pack | 通过 | 12 条官方/权威馆藏参考、5 个 Pattern Primitive、3 组无伪造 HEX 的颜色关系；全部未明权利图片标为 `reference_only` |
| Opportunity Score | 通过 | 8–12 条机会均有六项正向分、文化风险和可解释综合分；20/20/20/15/15/10 加权后扣 20% 风险 |
| LightRAG 二次核验 | 通过 | 高分候选实际重载本地图并逐项查询；输出 `verified/warning/rejected`，拒绝项不能进入设计交接 |
| Designer Handoff | 通过 | 仅 Top 3，当前为 OPP-006、OPP-002、OPP-004，均为 `verified`；JSON 为设计阶段唯一机器输入，`next_owner=QianCraft Design Agent` |
| Design Agent 接口 | 通过 | 实际从文件重载 DesignerHandoff，输入 SHA-256 与当前文件一致；选择 OPP-006 并缩窄为花溪单一原型，OPP-002 高敏感动植物母题在社区确认前自动留置 |
| 产品与工厂拆解 | 通过 | 输出“针格模块”互动冰箱贴概念样；5 项尺寸、5 项 BOM、1 组原创网格应用、6 步装配、6 项质检、3+3 审核门和 5 个工厂待确认问题完整，`mass_production_ready=false` |
| 设计海报 | 通过 | 1800 × 2400 PNG 含文化元素/风格、成品主视觉、爆炸拆解、尺寸、BOM 与工艺；本地精确中文排版，海报和主视觉 SHA-256 均入清单，`reference_only_images_used=false` |
| 离线回退 | 通过 | 生成 8 条证据规则机会；设计段继续运行，无主视觉时本地几何海报诚实标为 `cache` |
| 自动测试 | 通过 | `pytest` 19/19；新增 DesignPackage、输入/渲染摘要、13 路输出和高敏感母题留置回归 |
| 静态检查 | 通过 | `ruff check app scripts tests` 无错误 |
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
uvx ruff check app scripts tests
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
