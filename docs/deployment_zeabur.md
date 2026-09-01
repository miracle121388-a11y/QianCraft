# Zeabur 生产部署

QianCraft 采用单服务容器部署：公网请求先进入 Nginx，网页与 API 分别转发到容器内的 Vinext 和 Python 进程。站点默认启用 HTTP Basic Auth，`/healthz` 仅用于平台健康检查。

## 已上线实例

- 入口：<https://qiancraft-studio-2026.zeabur.app>
- 区域：California 专用服务器
- 拓扑：Nginx（公网端口）→ Vinext `127.0.0.1:3000` / Tool API `127.0.0.1:8787`
- 访问控制：除 `/healthz` 外统一启用 Basic Auth；凭证由项目维护者单独分发。
- 持久化：Zeabur Volume `qiancraft-runtime` 挂载到 `/app/data/runtime`。
- 网络防护：0.10.0 模板关闭 Nginx 版本回显，为 API 设置 12 req/s、burst 40 的单 IP 限流，并下发 HSTS、CSP、Permissions-Policy、X-Content-Type-Options、Referrer-Policy 与 X-Frame-Options；CDP、VNC、noVNC 上游均只监听回环，`/browser-auth/` 继续位于站点 Basic Auth 之后。

2026-08-28 的发布验收覆盖匿名 401、健康检查 200、认证后首页/API/九个节点详情页 200、引用解析、节点独立运行和运行目录挂载状态。0.5.2 部署 `6a91944713d3d467215e63e3` 进一步验证两套 Noto 中文字体 CSS 与 WOFF2 为 200，并把持久化默认视口迁移为 `x=20, y=210, zoom=0.82`。0.6.0 部署 `6a91a4a7db37f2e6ddbc0c40` 在同一受保护实例增加七阶段人工决策、DecisionProfile 1.1 与节点展示页深链接；线上容器报告应用版本 0.6.0，默认工作区已无损持久化迁移为 Schema 1.1，Decision Catalog 为 22 条文化记录、4 个平台、8 条机会、12 条视觉参考和 3 个概念，九个节点 API 与九个前端详情页均返回 200，非法决策 ID 返回 422。

2026-08-29 的最终 0.7.0 部署 `6a91ccc4ac2577a93d22028e` 把暖纸色 Creative Instrument Workbench、五阶段导航、上下文证据/资产/历史 Dock、React Flow 主画布、320px Inspector、移动端覆盖层和焦点闭环发布到同一实例。远端 Vinext 五阶段构建和 Docker 镜像构建通过，安装日志确认 `qiancraft-0.7.0`，部署状态为 `RUNNING`；公网 `/healthz` 返回 200、匿名 `/` 返回 401。当前执行环境没有站点 Basic Auth 凭证，因此本轮没有把本地九页/九 API 结果冒充为 0.7.0 的认证公网结果；完整业务与响应式交互已在本地生产构建中验收。该实例始终是受保护的产品验证环境，不承担无需登录的公众营销站职责。

同日的 0.7.1 部署 `6a91d1a613d3d467215e74b8` 把用户给定的 Parchment / Warm Sand / Linen / Stone / Dim Gray / Charcoal / Interaction Indigo 关系锁定到工作台、Human Decision Studio 与节点详情全表面；清除旧冷灰、纯白操作面和亮蓝主控残留，小字统一使用可达 AA 的 Dim Gray，主动作保持 Charcoal，Indigo 仅承担选择、焦点和路径。远端部署状态为 `RUNNING`，公网 `/healthz` 为 200、匿名 `/` 为 401；当前环境仍没有 Basic Auth 站点凭证，因此没有声称完成 0.7.1 认证后公网 UI/API 复验。

0.7.2 部署 `6a91d9ffdb37f2e6ddbc152e` 完成全页面信息降噪与移动端布局修复：工作台、Inspector、人工决策及九个节点详情统一使用单一中文栏目名，删除重复状态/摘要/节点 ID 和装饰性英文眉题；原始运行信息与方法字段改为按需展开。390px 下文化关系图、任务书编辑器、BOM、海报和人工决策表单均不再被桌面列宽裁切。远端 Vinext 五阶段构建及镜像构建通过，安装日志确认 `qiancraft-0.7.2`，部署状态为 `RUNNING`；公网 `/healthz` 为 200、匿名 `/` 为 401。当前环境仍没有站点 Basic Auth 凭证，因此认证后公网页面/API 继续如实保留为待凭证复验。

0.7.3 部署 `6a91df9a13d3d467215e7737` 把九个画布实例统一为稳定横向索引条：节点在 Rest / Selected 间不再展开、缩放或位移，选择只切换 Indigo keyline 与极浅纸面色差，摘要、字段和操作由 Inspector 或独立展示页承接。Inspector“操作”新增可见的完整页面入口，原有运行与从此运行保持可达；非画布详情页的遗留装饰网格被移除。远端构建日志确认 `qiancraft-0.7.3` 安装成功，部署状态为 `RUNNING`，公网 `/healthz` 为 200、匿名 `/` 为 401。当前环境仍没有站点 Basic Auth 凭证，因此未声称完成 0.7.3 认证后公网 UI/API 复验。

0.8.0 部署 `6a91f49bac2577a93d22048d` 将持久化严格研究任务、刷新续接、真实 Design Agent、服务端海报渲染和无假回退语义发布到同一实例。第一次 0.8.0 部署 `6a91f23f13d3d467215e790c` 已完成 Python 与 Vinext 构建，但发布包中的 `start-zeabur.sh` 被转换为 CRLF，Linux 容器无法执行；随后先用 `6a91f39a13d3d467215e7928` 恢复已验证的 0.7.3，再在 Docker 构建阶段规范化脚本行尾并重新发布。最终构建日志确认 `qiancraft-0.8.0` 与 Vinext 五阶段完成，运行日志确认 Tool API 和 Vinext 分别监听容器回环地址；部署状态为 `RUNNING`，公网 `/healthz` 为 200、匿名 `/` 为 401。当前环境没有站点 Basic Auth 凭证，因此没有声称完成 0.8.0 认证后公网业务 UI/API 复验。

2026-08-31 的 0.9.1 部署 `6a958619be05255ec5e261f7` 已在同一受保护实例进入 `RUNNING`。远端冷构建完成 Vinext 五阶段并安装 `qiancraft-0.9.1`；公网 `/healthz` 为 200，匿名 `/` 与 `/api/health` 均为 401。容器内使用现有服务器凭证完成统一入口验收：首页、九个节点路由、健康/Bootstrap、九个详情 API、DesignPackage 和四项正式 PNG 资产全部为 200；服务器直报应用版本 0.9.1。`/app/data/runtime` 实际挂载为 ext4 持久卷，默认工作区仍为 9 个节点/10 条边，22 条文化记录、378 条历史市场样本和 8 条机会均可读取。

2026-09-01 的 0.9.2 部署 `6a95b5a29ed7d65609e27bf6` 已进入 `RUNNING`，远端构建日志确认 Vinext 五阶段完成并安装 `qiancraft-0.9.2`。公网 `/healthz` 为 200，匿名首页/API 为 401，认证后首页、九路由、九详情 API、DesignPackage 和四项实际图像均为 200。Nginx 实际下发 HSTS、CSP、Permissions-Policy 等安全头；80 个并发 API 请求实测得到 42 个 200 和 38 个 429，突发后健康检查仍为 200。Tool API、Vinext 与 Nginx worker 以 `www-data` 运行，仅 Nginx master 保留 root；持久卷仍为 `/dev/vda3` ext4。

0.9.2 线上隔离工作区实际完成创建、Design Agent、DesignPackage 和 322,090 字节 PNG 海报。未配置图像 provider 时，Regenerate 与 Generate More 均按契约返回 `warning`；严格研究因无图形会话、缺 MediaCrawler/LightRAG 运行时及四平台授权返回 422。隔离工作区与设计目录已精确清理，默认工作区复核为 9 节点/10 边。发布前 0.9.1 运行态和发布后 0.9.2 ZIP 快照均已校验并复制到 Zeabur 持久卷之外、权限受控的本机目录；这仍不等于定时异地备份或已完成恢复演练。

同轮远端创建隔离验收工作区，实际完成 New → Rename/Save/Load → Decision v2 → Design Agent → DesignPackage → Poster v2 → 九节点详情与两张新 PNG 读取；创建返回 201，其余业务动作返回 200，严格实时研究因缺少上游运行时与四平台授权按契约返回 422。临时工作区、设计运行和生成资产随后按精确 ID 从持久卷清理，默认工作区未被污染。调度器在线、心跳新鲜、总开关开启且 `/api/health` 为 healthy；上线后的首轮文化巡检探测 4 个来源，其中 3 个正常、1 个失败，通道诚实标为 `degraded` 并只新增 1 条待人工审核候选，正式图谱仍为 22 条/32 个来源。市场通道因 7 项真实前置条件缺失保持 `blocked`。DeepSeek `/models` 从服务器返回 200，当前目标模型存在；独立图像 provider 仍未配置。

2026-09-01 的 0.10.0 最终部署 `6a96415cbe05255ec5e2854f` 把 LightRAG 1.5.7、GPT Researcher 0.14.7、隔离 MediaCrawler、Chromium/Xvfb/Openbox、x11vnc/noVNC/websockify 与现有 API/Web/Nginx 合并到同一服务。容器内实际确认两个上游 Python 包、三份源码、两份运行时就绪标记、CDP 9222、noVNC 6080、`0700` 浏览器资料目录和 ext4 持久卷全部可用；严格研究机器预检与图像 provider 均为 ready。LightRAG 实际在持久卷建立 612 实体/697 关系索引并查询 100 条主题边；GPT Researcher 实际使用 `deepseek-v4-flash` 返回有效 JSON，未走项目直连降级。图像 provider 在同一服务器实际生成有效 1024×1024 PNG。

公网继续保持 `/healthz` 200、匿名首页 401、匿名 `/browser-auth/vnc.html` 401；noVNC 只有通过站点鉴权后才能访问。浏览器入口连接成功只证明云端运行时存在，平台真实登录和搜索仍由 xhs/dy/bili/wb 每轮结果判定。平台 Cookie 不写入 Secret、仓库、命令或普通运行态快照；它们只保存在权限受限的持久浏览器资料中。

最终发布后使用现有站点 Secret 做不回显值的认证复核：首页、健康 API、Bootstrap 与 noVNC 均为 200，默认工作区为 9 节点/10 边。运行态 ZIP 含 24 个文件、4,525,180 个未压缩字节，排除 `browser-profile/`；服务器与本地 Conda 双重校验通过，卷外副本 SHA-256 为 `95338942…66a5`。严格研究 `20260901T030939Z-research` 已证明 culture/strategist live 与失败不晋级门有效；由于四平台当轮均 unavailable，market 仍为 cache，378 条历史快照没有被覆盖。

用户随后在受保护云端桌面完成四平台登录，小规模实采依次得到 xhs 20、dy 14、bili 20、wb 16。首次真实调用暴露 `Path.resolve()` 把 `/opt/mediacrawler-venv/bin/python` 解引用为 `/usr/bin/python3.11`，导致 CDP 模块缺少 `httpx`；部署 `6a964d01fff9450cc032d1ba` 改为保留虚拟环境入口，并让构建、启动和严格预检实际导入 `httpx` 与 `CDPBrowserManager`。严格任务 `20260901T041626Z-3deaef24` 取得 culture/strategist live，xhs 60、bili 55、wb 65，但 dy 0，因此如实为 `failed_no_fallback`，没有晋级。

部署 `6a96589cfff9450cc032d417` 进一步让抖音首页在 DOM ready 后继续，并让每轮 CDP 只关闭本轮新建页面、保留共享浏览器。用户随后决定暂不处理抖音交互验证码。当前最终部署 `6a96bdf25158a7aaa4e62007` 将运行集合固定为 `xhs,bili,wb`，UI/API 明确显示 dy 已暂停，并把严格晋级契约改为“配置中启用的平台必须且只能全部 live”。任务 `20260901T121642Z-e1a435ff` 实际得到 xhs 113、bili 110、wb 149 条规范化 live 记录，文化、市场、策划均为 live，状态为 `live_verified` 且已回写线上工作区；公网 `/healthz=200`。

本次代码合并进一步把默认入口改为双库驱动、结果优先的 Studio，并增加独立每日设计调度器、Top 3 批次、自由组合、设计详情与版本编辑；这些变更尚未重新部署。只有实际部署完成并验证 `/healthz` 的两个调度线程、两库计数、当日设计与 PNG 后，才可把上述能力记录为线上可用。

## 必需配置

- 服务端口：使用平台注入的 `PORT`。
- 持久卷：挂载到 `/app/data/runtime`。
- `QIANCRAFT_WEB_USERNAME`、`QIANCRAFT_WEB_PASSWORD`：站点入口凭证。
- `LLM_API_KEY`：策划与设计模型凭证。
- `LLM_BASE_URL`、`LLM_MODEL`：模型接口与名称。
- `ALLOW_API_TXT_FALLBACK=false`：生产环境禁止读取本地密钥文件。
- `QIANCRAFT_CONTINUOUS_COLLECTION=true`：启动持续采集调度器。
- `QIANCRAFT_CULTURE_WATCH_MINUTES=360`：文化来源巡检间隔。
- `QIANCRAFT_MARKET_REFRESH_MINUTES=240`：启用平台增量复检间隔。
- `QIANCRAFT_DAILY_DESIGN_ENABLED=true`：启动每日设计调度器。
- `QIANCRAFT_DAILY_DESIGN_HOUR=7`、`QIANCRAFT_DAILY_DESIGN_MINUTE=0`：`Asia/Shanghai` 每日执行时间。
- `QIANCRAFT_RUNTIME_ROOT=/app/data/runtime`：快照脚本统一运行态根目录；镜像已内置该默认值。
- `QIANCRAFT_BROWSER_SESSION_ENABLED=true`：启用云端持久授权浏览器。
- `QIANCRAFT_BROWSER_PROFILE_DIR=/app/data/runtime/browser-profile`：平台登录资料目录，权限 `0700`。
- `QIANCRAFT_BROWSER_AUTH_URL=/browser-auth/vnc.html?autoconnect=1&resize=scale&path=browser-auth/websockify`：前端只返回同源受保护入口。
- `LIGHTRAG_STORAGE_DIR=/app/data/runtime/lightrag_storage`：LightRAG 持久索引目录。
- `MEDIACRAWLER_PYTHON=/opt/mediacrawler-venv/bin/python`：必须保留虚拟环境入口本身，不能解析为其指向的系统 Python。
- `MEDIACRAWLER_PLATFORMS=xhs,bili,wb`：当前 Zeabur 启用集合；dy 暂停但适配代码与历史基线保留。
- `MEDIACRAWLER_LIVE_ENABLED=true`、`MEDIACRAWLER_LOGIN_METHOD=cdp`、`MEDIACRAWLER_CDP_CONNECT_EXISTING=true`：生产镜像使用托管 Chromium；真实登录仍按平台逐轮验证。

图像服务通过 Zeabur Secret 配置 `IMAGE_PROVIDER`、`IMAGE_API_KEY`、`IMAGE_BASE_URL` 与 `IMAGE_MODEL`；当前实例已完成真实生成探针。其他环境未配置时，工作台仍保留已有 A/B/C 方案并明确显示 warning，不伪造新生成结果。

## 数据边界

`/app/data/runtime/workbench` 保存旧高级画布、任务书、概念版本、研究晋级产物、DesignPackage 和海报；`/app/data/runtime/tool_workspace` 保存严格研究 `job.json`、隔离 raw/derived/outputs、旧版工具设计运行，`collection/` 下的采集配置/心跳/事件/候选，以及 `studio/` 下的每日排程、事件、批次、设计版本和 PNG；`/app/data/runtime/lightrag_storage` 保存文化索引；`/app/data/runtime/browser-profile` 只保存托管浏览器资料。文化图谱、市场/形态证据和官方设计包随镜像只读发布，运行态不会覆盖证据基线；研究任务刷新后可按任务号续接，容器重启前未完成的任务会明确标为 interrupted，每日调度器则会在当天无产出时补跑。

单容器、单 Tool API 副本可以按上述持久卷和平台重启策略持续调度；它不是分布式任务队列。扩到多个 API 副本前必须加入唯一领导者、分布式锁或外部队列，否则每个副本都会运行自己的排程。仓库已提供带路径/数量/体积/SHA-256 校验的手工快照与原子恢复工具，并在恢复时保留旧运行目录。生产仍需把快照复制到独立卷或站外存储，并为心跳、连续失败、候选积压与授权过期配置外部告警；同卷快照和页面“在线”都不能代替异地备份与平台级监控。

当前线上容器已具备三个上游运行时和受保护浏览器，不再因缺运行时返回 422。启用平台的实时采集仍受本人登录态、平台风控与当轮搜索产物约束；机器预检通过后会启动真实任务，任何启用平台没有获得本轮有效记录都只保留失败审计，不会用 378 条历史快照冒充 live，也不会晋级到工作区。暂停平台不会被暗中访问，也不会被计入成功范围。

## 本地构建

```bash
docker build -t qiancraft:0.10.0 .
docker run --rm -p 8080:8080 \
  -e QIANCRAFT_WEB_USERNAME=qiancraft \
  -e QIANCRAFT_WEB_PASSWORD='<set-in-secret-manager>' \
  -e LLM_API_KEY='<set-in-secret-manager>' \
  -v qiancraft-runtime:/app/data/runtime \
  qiancraft:0.10.0
```

生产密钥只应通过 Zeabur 的变量管理界面注入，不写入 Dockerfile、仓库或部署日志。

## 运行态备份与恢复

Zeabur 镜像内已包含快照脚本。权威备份和恢复都应在维护窗口先停止 Tool API 写入；无法停机时创建的在线备份只能视为尽力快照。脚本会在发布 ZIP 前自校验，并应把 `/tmp/qiancraft-runtime.zip` 立即复制到独立受控存储。恢复须从维护 shell 执行带双重确认的命令：

```bash
/opt/venv/bin/python /app/scripts/runtime_snapshot.py backup \
  --runtime-root /app/data/runtime --output /tmp/qiancraft-runtime.zip
/opt/venv/bin/python /app/scripts/runtime_snapshot.py verify \
  /tmp/qiancraft-runtime.zip
/opt/venv/bin/python /app/scripts/runtime_snapshot.py restore \
  /tmp/qiancraft-runtime.zip --runtime-root /app/data/runtime \
  --confirm-service-stopped --confirm RESTORE_QIANCRAFT_RUNTIME
```

快照清单不记录 Secret，并强制拒绝包含 `browser-profile/` 的归档；但运行态仍可能包含研究输入和审核记录，备份本身按敏感项目数据管理。恢复成功后保留时间戳命名的 `runtime.pre-restore-*` 回滚目录，确认新状态无误后再由维护者单独处理；平台浏览器资料不随 ZIP 恢复，恢复后必须重新授权。

Zeabur CLI 上传会跳过点号目录；Dockerfile 因此会在远端构建阶段确保存在不含密钥的 `.openai/hosting.json`。实际 D1/R2 绑定仍以部署环境配置为准，不能把该占位清单当作生产凭证或数据配置。0.7.1 继续使用隔离发布副本，只保留当前市场快照，并仅在副本中对随镜像发布的展示 PNG 做无尺寸变化压缩；工作区原始高清资产不改动，PNG 尺寸和必要的文本/物理尺寸元数据块得到保留。当前副本为 87 个文件、5,694,056 字节，敏感路径和长 `sk-` 模式扫描均为 0 命中。首次上传在对象存储连接层被远端重置且未触发部署；同一已扫描副本第二次上传成功，随后远端构建与发布完成。

0.7.2 同样使用隔离发布副本：71 个文件、8,893,000 字节，敏感文件名与长 `sk-` 模式均为 0 命中；不包含 `api.txt`、环境文件、Cookies、上游源码或运行态工作区。只在发布副本内对 6 张随镜像提供的 PNG 做 128 色自适应压缩，尺寸与海报 DPI 信息保持不变，项目源高清图没有改写。线上持久卷继续保留既有工作区。

0.7.3 使用新的隔离副本 `.zeabur-stage-073`：72 个文件、19,313,856 字节，敏感文件名与长 `sk-` 模式均为 0 命中；不包含 `api.txt`、环境文件、Cookies、上游源码、测试或运行态工作区。本轮没有改写或压缩源图，线上持久卷继续保留既有工作区。首次上传未建立部署记录，同一已扫描副本第二次上传成功。

0.8.0 使用隔离副本 `.zeabur-stage-080`：74 个文件、19,435,606 字节，敏感文件名与长 `sk-` 模式均为 0 命中；不包含 `api.txt`、环境文件、Cookies、上游源码、测试、本地运行态或用户未跟踪文件。本轮没有改写源图，线上持久卷继续保留既有工作区。鉴于 Zeabur 上传链路会改变 shell 脚本行尾，Dockerfile 在复制启动脚本后显式移除 CRLF，再设置可执行权限；最终 0.8.0 容器已用该路径启动。

0.9.1 使用隔离副本 `.zeabur-stage-091`：79 个文件、19,597,854 字节；敏感路径、长 `sk-` 模式和必需文件检查分别为 0 命中、0 命中和 0 缺失。不包含 `.env`、`api.txt`、Cookies、上游源码、测试、本地运行态或原始采集数据。依赖下载曾发生一次自动重试，但构建、镜像上传和发布最终完整通过；未改写项目源图或线上持久数据。

0.9.2 使用临时隔离发布目录：115 个文件、27,938,032 字节；必需文件缺失、符号链接、禁止路径、私钥、长 `sk-` 和长 Authorization 值均为 0。副本不含 `.env`、`api.txt`、Cookies、本地运行态、原始平台数据、上游源码、测试或 Playwright 产物；远端实际上传的 Docker context 为约 27.95 MB。

0.10.0 使用临时隔离发布目录：1,353 个文件、约 74 MiB；实际交付三份上游源码但排除上游测试/evals、原始平台数据、本地运行态、浏览器 profile、`.env`、`api.txt`、Cookies 与 Playwright 产物。长 API Key/私钥模式、敏感文件名与符号链接均为 0。部署 `6a9639c0be05255ec5e2833a` 因 Zeabur CLI 不上传 `.env.example` 失败，`6a963bd7be05255ec5e283d2` 复现同一问题并伴随 Docker Hub 代理 DNS 瞬断；移除镜像对示例文件的无必要依赖后，`6a963cd7be05255ec5e28416` 完成首轮 0.10.0 运行。最终部署 `6a96415cbe05255ec5e2854f` 再补托管 CDP 复用与 Chromium 跨容器 stale lock 清理，且不触碰登录数据库。

三平台收口发布使用 1,121 文件、49,984 KiB 的隔离目录，符号链接、浏览器 profile、长 API Key/私钥模式均为 0；唯一命名为 secret 的文件是 LightRAG 上游 Kubernetes 模板，实际凭证模式仍为 0。部署 `6a96bdf25158a7aaa4e62007` 的四个关键运行文件与本地 SHA-256 完全一致。任务结束后在线快照自校验为 118 文件、18,890,725 未压缩字节、4,100,550 字节 ZIP，`containsBrowserAuthorization=false`；该 `/tmp` 校验件不是异地持久备份，既有卷外备份策略仍需继续执行。
