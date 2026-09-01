# QianCraft 持续素材采集

> 适用版本：0.10.0 及以后
> 范围：文化知识来源巡检、配置化市场平台增量采集，以及两条通道的运行控制面。

## 1. “持续更新”的准确含义

QianCraft 的持续采集由 Tool API 进程内的持久化调度器执行。只要 API 容器持续运行、平台在异常退出后负责重启，并且 `data/runtime/` 使用持久卷，两条通道就会按各自间隔持续复检。它不是无人监管地自动改写事实：

- **文化通道**检查已登记公开来源的可达性和内容指纹，发现同域相关文章后只写入候选队列。候选必须经过出处、字段证据与文化边界审核，才能进入正式知识图谱。
- **市场通道**先检查 MediaCrawler、实时采集开关和配置中启用平台的授权状态。当前 Zeabur 启用 xhs / bili / wb，dy 因交互验证码暂停；只有本轮全部启用平台及文化、策划组件均为 `live`，结果才可晋级。
- 22 条正式文化记录、32 个登记来源、378 条历史平台快照和新候选是不同事实层。候选不计入正式记录，历史快照不冒充实时趋势。

“7×24 小时”因此是一个有运行条件的运维承诺，而不是页面文案：API 进程、持久卷、主机重启策略、网络、上游许可和用户授权缺一不可。

## 2. 默认排程

| 通道 | 默认间隔 | 自动动作 | 成功条件 |
|---|---:|---|---|
| `culture_watch` | 360 分钟 | 每轮最多巡检 4 个登记来源，使用 ETag / Last-Modified / SHA-256 识别变化并发现同域候选 | 本轮所有被巡检来源都成功；任一来源失败即 `degraded`，连续失败不清零 |
| `market_refresh` | 240 分钟 | 复检运行时与启用平台授权；条件齐备时启动隔离严格研究任务并轮询 | 任务返回 `live_verified`；阻断、部分 live、cache 或 unavailable 均不晋级 |

间隔可在文化图谱页和市场热度页调整，允许值为 60、120、240、360、720、1440 分钟。每条通道和整个调度器都可独立暂停；立即运行也经过同一真实性门。

## 3. 状态语义

| 状态 | 含义 |
|---|---|
| `scheduled` | 已排程，等待下次运行 |
| `running` | 当前轮正在执行 |
| `healthy` | 当前轮满足该通道全部成功条件 |
| `degraded` | 已执行但存在来源失败或结果未满足完整晋级条件 |
| `blocked` | 授权、开关或运行时缺失，任务没有被伪启动 |
| `failed` | 执行发生未恢复错误 |
| `paused` | 通道或总调度器被暂停 |
| `interrupted` | API 进程重启时发现旧任务未完成；旧任务不会被补写成成功 |

前端每 12 秒读取状态。连续轮询失败会立即显示“采集控制面连接中断”，保留最后同步时间并禁用写操作；心跳超过 45 秒也按离线处理，不继续显示旧的“在线”。

## 4. 文化候选审核

文化来源巡检只发现满足以下条件的同域页面：路径像文章/详情页、链接标题具备实际语义、内容命中非遗/贵州/工艺等限定词，并排除通用导航、媒体文件和已登记 URL。0.9.2 同时拒绝本机、私网、链路本地、云元数据和保留地址；输入、DNS 结果和 HTTP 重定向逐次校验，实际 TCP 连接钉住当次已校验的公网地址且不使用环境代理，防止 DNS rebinding 或代理绕行访问内部服务。候选状态为：

1. `pending_review`：只证明“被发现”，不证明内容真实或适合入图。
2. `ready_to_structure`：人工已核对来源，可进入字段级结构化；仍不是正式记录。
3. `rejected`：不相关、不可信或不适合纳入；保留审计事件。

正式入图仍需更新 `data/culture/knowledge_graph.json` 的记录、`source_refs` 与 `field_sources`，并运行文化图谱测试。调度器永远不绕过这一步。

## 5. 市场授权与真实性门

0.10.0 的 Zeabur 单容器同时运行持久化 Chromium、Xvfb 与 noVNC。Chromium 的 CDP 和 VNC 端口都只监听 `127.0.0.1`；唯一公网入口是继续受站点 Basic Auth 保护的 `/browser-auth/`。首次正式采集按以下顺序授权：

1. 登录 QianCraft，进入“市场热度 → 平台增量采集”，点击“打开授权页”。
2. 由维护者本人完成配置中启用平台的登录或扫码验证。当前 Zeabur 需要小红书、B站和微博；抖音卡片显示“已暂停”，不参与采集或晋级。不要把 Cookie 复制到页面、仓库或聊天。
3. 回到市场控制面点击“立即运行”，或在主工作台启动“实时运行”。本轮会逐个验证启用平台的登录和搜索；只有这些平台均返回真实记录才会继续晋级。

浏览器端口可连接只表示运行时存在，不等于启用平台已经登录。平台会话可能因平台策略、异地 IP、验证码或有效期失效，每轮仍以 `login_ok / search_ok / sample_size` 的实际结果为准。浏览器资料写入持久卷的 `/app/data/runtime/browser-profile`，权限为 `0700`；普通运行态 ZIP 明确排除该目录，恢复或卷丢失后必须重新授权。

本地开发仍可使用同一显式探针：

```powershell
# 查看非交互预检，不打开登录窗口
conda run --no-capture-output -n qiancraft python scripts\probe_market_platforms.py

# 用户在场时逐平台授权；当前 Zeabur 启用 xhs / bili / wb，dy 可在恢复后单独探测
conda run --no-capture-output -n qiancraft python scripts\probe_market_platforms.py --platform xhs --method cdp --authorize

# 配置中的平台授权完成后做正式小规模复核
conda run --no-capture-output -n qiancraft python scripts\probe_market_platforms.py --platform all --method cdp --formal --authorize
```

Zeabur 镜像已把 `MEDIACRAWLER_LIVE_ENABLED=true`、CDP 连接和独立 MediaCrawler Python 环境设为生产默认值。本地仍需自行显式开启。调度器不会把授权 Cookie 写进仓库、命令行、日志或 API 响应，也不会用 378 条历史记录给失败的新一轮兜底。

## 6. 配置与 API

```dotenv
QIANCRAFT_CONTINUOUS_COLLECTION=true
QIANCRAFT_CULTURE_WATCH_MINUTES=360
QIANCRAFT_MARKET_REFRESH_MINUTES=240
QIANCRAFT_BROWSER_SESSION_ENABLED=true
QIANCRAFT_BROWSER_PROFILE_DIR=/app/data/runtime/browser-profile
QIANCRAFT_BROWSER_AUTH_URL=/browser-auth/vnc.html?autoconnect=1&resize=scale&path=browser-auth/websockify
LIGHTRAG_STORAGE_DIR=/app/data/runtime/lightrag_storage
MEDIACRAWLER_PYTHON=/opt/mediacrawler-venv/bin/python
MEDIACRAWLER_PLATFORMS=xhs,bili,wb
```

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/api/collection/status` | 调度器、两条通道、心跳、预检和真实计数 |
| `GET` | `/api/collection/events?limit=80` | 最近运行、阻断、失败与审核事件 |
| `GET` | `/api/collection/candidates` | 文化候选队列 |
| `PUT` | `/api/collection/schedule` | 暂停/恢复、修改通道间隔 |
| `POST` | `/api/collection/run` | 将指定通道排为立即运行 |
| `POST` | `/api/collection/candidates` | 人工加入公开来源候选 |
| `POST` | `/api/collection/candidates/{id}/review` | 审核候选状态 |

状态、事件、候选与来源指纹位于 `data/runtime/tool_workspace/collection/`。它们必须随 `/app/data/runtime` 持久卷保存，但不进入 Git。

## 7. 部署和巡检

- `/healthz` 由 Nginx 转发真实 `/api/health`；响应包含调度线程在线状态、心跳新鲜度和总开关。线程死亡或心跳超过 45 秒时 API 返回 503，镜像 HEALTHCHECK 随之失败，交给已配置的容器重启策略恢复，不再返回静态假 200。
- `deploy/start-zeabur.sh` 同时监控 Tool API、Vinext、Nginx、Xvfb、Openbox、Chromium、x11vnc 与 websockify；任一必需子进程退出时容器以失败结束，交给平台重启。
- 0.10.0 镜像包含 LightRAG、GPT Researcher 与隔离 MediaCrawler Python 环境。部署 `6a96bdf25158a7aaa4e62007` 的严格任务 `20260901T121642Z-e1a435ff` 实际得到 xhs 113、bili 110、wb 149 条规范化 live 记录，三组件同为 live 并晋级工作区；dy 明确暂停且不在清单中。378 条四平台仓库基线仍保持历史口径，没有被本轮运行覆盖。
- 生产排程必须配置持久卷、异常重启、日志/告警和备份。单个容器内线程不是跨副本分布式调度器；部署多个 API 副本前必须增加唯一领导者或外部队列，避免重复采集。
- 定期查看连续失败、最后成功时间、候选积压和平台授权过期。`healthy` 只说明当前轮满足技术条件，不等于候选内容已获得文化审核或商业授权。

## 8. 验证

```powershell
conda run --no-capture-output -n qiancraft python -m pytest tests/test_collection.py tests/test_tool_api.py -q
conda run --no-capture-output -n qiancraft ruff check app tests

cd web
pnpm typecheck
pnpm lint
pnpm test
pnpm test:ui
pnpm build
```

前端门必须覆盖桌面与手机的真实计数、候选分层、授权阻断、断线旧状态、星图触控/键盘路径和 forced-colors。通过自动门不代表上游平台始终可用，也不代表 WCAG、制造或商业合规认证。
