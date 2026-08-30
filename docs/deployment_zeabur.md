# Zeabur 生产部署

QianCraft 采用单服务容器部署：公网请求先进入 Nginx，网页与 API 分别转发到容器内的 Vinext 和 Python 进程。站点默认启用 HTTP Basic Auth，`/healthz` 仅用于平台健康检查。

## 已上线实例

- 入口：<https://qiancraft-studio-2026.zeabur.app>
- 区域：California 专用服务器
- 拓扑：Nginx（公网端口）→ Vinext `127.0.0.1:3000` / Tool API `127.0.0.1:8787`
- 访问控制：除 `/healthz` 外统一启用 Basic Auth；凭证由项目维护者单独分发。
- 持久化：Zeabur Volume `qiancraft-runtime` 挂载到 `/app/data/runtime`。

2026-08-28 的发布验收覆盖匿名 401、健康检查 200、认证后首页/API/九个节点详情页 200、引用解析、节点独立运行和运行目录挂载状态。0.5.2 部署 `6a91944713d3d467215e63e3` 进一步验证两套 Noto 中文字体 CSS 与 WOFF2 为 200，并把持久化默认视口迁移为 `x=20, y=210, zoom=0.82`。0.6.0 部署 `6a91a4a7db37f2e6ddbc0c40` 在同一受保护实例增加七阶段人工决策、DecisionProfile 1.1 与节点展示页深链接；线上容器报告应用版本 0.6.0，默认工作区已无损持久化迁移为 Schema 1.1，Decision Catalog 为 22 条文化记录、4 个平台、8 条机会、12 条视觉参考和 3 个概念，九个节点 API 与九个前端详情页均返回 200，非法决策 ID 返回 422。

2026-08-29 的最终 0.7.0 部署 `6a91ccc4ac2577a93d22028e` 把暖纸色 Creative Instrument Workbench、五阶段导航、上下文证据/资产/历史 Dock、React Flow 主画布、320px Inspector、移动端覆盖层和焦点闭环发布到同一实例。远端 Vinext 五阶段构建和 Docker 镜像构建通过，安装日志确认 `qiancraft-0.7.0`，部署状态为 `RUNNING`；公网 `/healthz` 返回 200、匿名 `/` 返回 401。当前执行环境没有站点 Basic Auth 凭证，因此本轮没有把本地九页/九 API 结果冒充为 0.7.0 的认证公网结果；完整业务与响应式交互已在本地生产构建中验收。该实例始终是受保护的产品验证环境，不承担无需登录的公众营销站职责。

同日的 0.7.1 部署 `6a91d1a613d3d467215e74b8` 把用户给定的 Parchment / Warm Sand / Linen / Stone / Dim Gray / Charcoal / Interaction Indigo 关系锁定到工作台、Human Decision Studio 与节点详情全表面；清除旧冷灰、纯白操作面和亮蓝主控残留，小字统一使用可达 AA 的 Dim Gray，主动作保持 Charcoal，Indigo 仅承担选择、焦点和路径。远端部署状态为 `RUNNING`，公网 `/healthz` 为 200、匿名 `/` 为 401；当前环境仍没有 Basic Auth 站点凭证，因此没有声称完成 0.7.1 认证后公网 UI/API 复验。

0.7.2 部署 `6a91d9ffdb37f2e6ddbc152e` 完成全页面信息降噪与移动端布局修复：工作台、Inspector、人工决策及九个节点详情统一使用单一中文栏目名，删除重复状态/摘要/节点 ID 和装饰性英文眉题；原始运行信息与方法字段改为按需展开。390px 下文化关系图、任务书编辑器、BOM、海报和人工决策表单均不再被桌面列宽裁切。远端 Vinext 五阶段构建及镜像构建通过，安装日志确认 `qiancraft-0.7.2`，部署状态为 `RUNNING`；公网 `/healthz` 为 200、匿名 `/` 为 401。当前环境仍没有站点 Basic Auth 凭证，因此认证后公网页面/API 继续如实保留为待凭证复验。

0.7.3 部署 `6a91df9a13d3d467215e7737` 把九个画布实例统一为稳定横向索引条：节点在 Rest / Selected 间不再展开、缩放或位移，选择只切换 Indigo keyline 与极浅纸面色差，摘要、字段和操作由 Inspector 或独立展示页承接。Inspector“操作”新增可见的完整页面入口，原有运行与从此运行保持可达；非画布详情页的遗留装饰网格被移除。远端构建日志确认 `qiancraft-0.7.3` 安装成功，部署状态为 `RUNNING`，公网 `/healthz` 为 200、匿名 `/` 为 401。当前环境仍没有站点 Basic Auth 凭证，因此未声称完成 0.7.3 认证后公网 UI/API 复验。

0.8.0 部署 `6a91f49bac2577a93d22048d` 将持久化严格研究任务、刷新续接、真实 Design Agent、服务端海报渲染和无假回退语义发布到同一实例。第一次 0.8.0 部署 `6a91f23f13d3d467215e790c` 已完成 Python 与 Vinext 构建，但发布包中的 `start-zeabur.sh` 被转换为 CRLF，Linux 容器无法执行；随后先用 `6a91f39a13d3d467215e7928` 恢复已验证的 0.7.3，再在 Docker 构建阶段规范化脚本行尾并重新发布。最终构建日志确认 `qiancraft-0.8.0` 与 Vinext 五阶段完成，运行日志确认 Tool API 和 Vinext 分别监听容器回环地址；部署状态为 `RUNNING`，公网 `/healthz` 为 200、匿名 `/` 为 401。当前环境没有站点 Basic Auth 凭证，因此没有声称完成 0.8.0 认证后公网业务 UI/API 复验。

0.9.1 当前只完成本地实现与验收，**尚未部署**。它延续 0.9.0 的进程内持续采集调度器、知识星图、文化候选审核、市场增量控制面和真实健康检查，并完成提交前链路加固：Nginx 的 `/healthz` 转发 `/api/health`，响应包含调度线程、心跳新鲜度和总开关；线程死亡或心跳超过 45 秒返回 503，Docker HEALTHCHECK 随之失败；`start-zeabur.sh` 同时监控 Tool API、Vinext 与 Nginx，任一子进程退出即让容器失败。上述故障恢复仍依赖部署平台实际启用重启策略。不能把本地 0.9.1 截图或测试结果写成线上已升级；受保护实例仍以 0.8.0 为准。

## 必需配置

- 服务端口：使用平台注入的 `PORT`。
- 持久卷：挂载到 `/app/data/runtime`。
- `QIANCRAFT_WEB_USERNAME`、`QIANCRAFT_WEB_PASSWORD`：站点入口凭证。
- `LLM_API_KEY`：策划与设计模型凭证。
- `LLM_BASE_URL`、`LLM_MODEL`：模型接口与名称。
- `ALLOW_API_TXT_FALLBACK=false`：生产环境禁止读取本地密钥文件。
- `QIANCRAFT_CONTINUOUS_COLLECTION=true`：启动持续采集调度器。
- `QIANCRAFT_CULTURE_WATCH_MINUTES=360`：文化来源巡检间隔。
- `QIANCRAFT_MARKET_REFRESH_MINUTES=240`：四平台增量复检间隔。

图像服务必须单独配置 `IMAGE_PROVIDER`、`IMAGE_API_KEY`、`IMAGE_BASE_URL` 与 `IMAGE_MODEL`；未配置时，工作台保留已有 A/B/C 方案并明确显示 warning，不伪造新生成结果。

## 数据边界

`/app/data/runtime/workbench` 保存画布、任务书、概念版本、研究晋级产物、DesignPackage 和海报；`/app/data/runtime/tool_workspace` 保存严格研究 `job.json`、隔离 raw/derived/outputs、旧版工具设计运行，以及 `collection/` 下的排程配置、心跳、事件、候选与来源指纹。文化图谱、市场证据和官方设计包随镜像只读发布，运行态不会覆盖证据基线；页面刷新后可按任务号续接，容器重启前未完成的任务会明确标为 interrupted。

单容器、单 Tool API 副本可以按上述持久卷和平台重启策略持续调度；它不是分布式任务队列。扩到多个 API 副本前必须加入唯一领导者、分布式锁或外部队列，否则每个副本都会运行自己的排程。生产还需为心跳、连续失败、候选积压与授权过期配置外部告警和备份；页面显示“在线”不能代替平台级监控。

当前线上容器面向产品工作台和设计验证。四平台实时采集仍受平台登录态、授权用途、MediaCrawler 源码与独立浏览器运行时约束；精简云端镜像不包含这些上游运行时，因此严格研究会在预检阶段明确阻断，不会用 378 条历史快照冒充本轮 live。完整实爬应在用户已授权浏览器的本机运行，再由核验门晋级到对应工作区。

## 本地构建

```bash
docker build -t qiancraft:0.9.1 .
docker run --rm -p 8080:8080 \
  -e QIANCRAFT_WEB_USERNAME=qiancraft \
  -e QIANCRAFT_WEB_PASSWORD='<set-in-secret-manager>' \
  -e LLM_API_KEY='<set-in-secret-manager>' \
  -v qiancraft-runtime:/app/data/runtime \
  qiancraft:0.9.1
```

生产密钥只应通过 Zeabur 的变量管理界面注入，不写入 Dockerfile、仓库或部署日志。

Zeabur CLI 上传会跳过点号目录；Dockerfile 因此会在远端构建阶段确保存在不含密钥的 `.openai/hosting.json`。实际 D1/R2 绑定仍以部署环境配置为准，不能把该占位清单当作生产凭证或数据配置。0.7.1 继续使用隔离发布副本，只保留当前市场快照，并仅在副本中对随镜像发布的展示 PNG 做无尺寸变化压缩；工作区原始高清资产不改动，PNG 尺寸和必要的文本/物理尺寸元数据块得到保留。当前副本为 87 个文件、5,694,056 字节，敏感路径和长 `sk-` 模式扫描均为 0 命中。首次上传在对象存储连接层被远端重置且未触发部署；同一已扫描副本第二次上传成功，随后远端构建与发布完成。

0.7.2 同样使用隔离发布副本：71 个文件、8,893,000 字节，敏感文件名与长 `sk-` 模式均为 0 命中；不包含 `api.txt`、环境文件、Cookies、上游源码或运行态工作区。只在发布副本内对 6 张随镜像提供的 PNG 做 128 色自适应压缩，尺寸与海报 DPI 信息保持不变，项目源高清图没有改写。线上持久卷继续保留既有工作区。

0.7.3 使用新的隔离副本 `.zeabur-stage-073`：72 个文件、19,313,856 字节，敏感文件名与长 `sk-` 模式均为 0 命中；不包含 `api.txt`、环境文件、Cookies、上游源码、测试或运行态工作区。本轮没有改写或压缩源图，线上持久卷继续保留既有工作区。首次上传未建立部署记录，同一已扫描副本第二次上传成功。

0.8.0 使用隔离副本 `.zeabur-stage-080`：74 个文件、19,435,606 字节，敏感文件名与长 `sk-` 模式均为 0 命中；不包含 `api.txt`、环境文件、Cookies、上游源码、测试、本地运行态或用户未跟踪文件。本轮没有改写源图，线上持久卷继续保留既有工作区。鉴于 Zeabur 上传链路会改变 shell 脚本行尾，Dockerfile 在复制启动脚本后显式移除 CRLF，再设置可执行权限；最终 0.8.0 容器已用该路径启动。
