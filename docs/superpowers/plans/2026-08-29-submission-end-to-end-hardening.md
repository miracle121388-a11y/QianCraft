# QianCraft 提交前端到端加固实施计划

> 日期：2026-08-29
> 范围：仅覆盖已获授权的文化研究、机会策略、`DesignPackage`、工厂询价/首样 brief 与概念海报；不进入量产发布、下单、商业定稿或制造/合规就绪声明。

## 目标

在当前 Windows 工作区中，从全新隔离输出目录实际执行 QianCraft 的主链路，修复会让“表面成功但没有调用预期组件”或“新克隆后数据退化”的问题，并以测试、API、Web 构建及产物审计共同证明最终概念产品可生成、可读取、可追溯。

## 任务 1：修正显式运行模式语义

**文件**

- 修改：`app/config.py`
- 测试：`tests/test_demo_pipeline.py`

**先写失败测试**

新增 `test_explicit_run_modes_override_environment_defaults`，验证：

```python
demo -> (live_mode=False, demo_mode=True)
auto -> (live_mode=True, demo_mode=True)
live -> (live_mode=True, demo_mode=False)
```

测试必须先在当前实现上因 `auto` 仍保留环境默认值而失败。随后将 `Settings.with_mode("auto")` 改为显式 `replace(self, live_mode=True, demo_mode=True)`，确保命令行选择 `auto` 时先尝试 LightRAG、DeepSeek/GPT Researcher 与获准的平台采集，再诚实回退缓存。

**验证**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_demo_pipeline.py -k explicit_run_modes -q
```

## 任务 2：让提交包可使用已提交的市场派生快照

**文件**

- 修改：`app/adapters/media_crawler_adapter.py`
- 测试：`tests/test_demo_pipeline.py`

**先写失败测试**

新增异步测试：在临时目录中不创建 `market/raw/*.jsonl`，只复制仓库内 `data/market/derived/latest.json`，调用 `MediaCrawlerAdapter.research()`，要求返回 `cache` 状态、378 条平台样本、四个平台计数和非空热度排名。当前实现只看被 `.gitignore` 排除的 raw 文件，因此测试应先得到 0 条并失败。

**最小实现**

`_load_platform_snapshot(platform)` 优先读取 `market_raw_dir/{platform}.jsonl`；文件不存在或没有有效记录时，读取 `market_derived_dir/latest.json` 的 `records`，只筛选当前平台后走同一校验、清洗和上限逻辑。若两者都不存在，继续返回空列表，保留现有“诚实不可用”行为。

**验证**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_demo_pipeline.py -k "derived_snapshot or market_fallback" -q
```

## 任务 3：修正概念海报 BOM 数量文案

**文件**

- 修改：`app/designer/poster.py`
- 测试：`tests/test_demo_pipeline.py`

**先写失败测试**

新增测试调用 `poster._bom_section_title(total_items, limit=6)`：5 项显示 `BOM / 首样规格（共5项）`，8 项显示 `BOM / 首样规格（前6项，完整表见JSON）`。当前没有该函数，测试应先失败。

**最小实现**

增加纯函数 `_bom_section_title`，海报渲染处按 `len(design_package.bill_of_materials)` 生成标题；列表仍最多显示 6 项，不改版式。

**验证**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_demo_pipeline.py -k bom_title -q
```

## 任务 4：恢复可复现的 Python 静态检查

**文件**

- 修改：`pyproject.toml`
- 修改：`uv.lock`
- 最小修复：`app/collection.py`、`app/tool_api.py`、`app/workbench.py`、`scripts/probe_market_platforms.py`

将 Ruff 作为 `test` 可选依赖固定到兼容的 `0.16.x`，更新锁文件。逐条最小修正当前 9 个诊断：导入顺序、现代 `datetime.fromisoformat`、冗余 `noqa`、`re.IGNORECASE`、重复分支和刻意保留的异常类型说明。不做无关重构。

**验证**

```powershell
.\.venv\Scripts\python.exe -m ruff check app tests scripts/probe_market_platforms.py
.\.venv\Scripts\python.exe -m pytest -q
```

## 任务 5：验证可选在线/上游组件的真实边界

**文件**

- 可能更新：`WORKFLOW.md`（仅记录实测状态，不写入任何密钥或 Cookie）

在 `.venv` 中按仓库说明安装或探测 LightRAG 与 GPT Researcher；为 MediaCrawler 检查隔离运行时和导入能力。无密钥时执行 `auto`，确认组件确实被尝试后以明确原因回退，而不是假装 live 成功。DeepSeek 与独立图像 API 只检查配置是否存在，不输出值；没有凭证时不声称真实调用成功。

**验证**

```powershell
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe -m app.main --mode auto
```

正式数据目录若会覆盖历史 live 证据，则改用 `dataclasses.replace` 指向 `data/runtime/submission-final/` 的隔离输出目录。

## 任务 6：验证 Tool API、Web 工作台与最终产品

**文件**

- 仅在测试暴露问题时修改 `app/tool_api.py`、`web/src/**` 或对应测试。

依次执行 Python Tool API 测试、Web 单元测试、类型检查、Lint、生产构建和 Playwright 端到端测试。启动本地 API 后检查健康端点、工作台 bootstrap、策略节点与设计节点结果可读取。对隔离运行生成的 13 个 manifest 输出逐一检查存在性和 Pydantic schema；核对 PNG 尺寸、SHA-256、精确文本合成标记、`mass_production_ready=false` 与参考图像素不可直接生产边界。

**验证**

```powershell
pnpm --dir web test
pnpm --dir web typecheck
pnpm --dir web lint
pnpm --dir web build
pnpm --dir web exec playwright test
```

## 任务 7：同步工作流与最终回归

**文件**

- 修改：`WORKFLOW.md`

在 `更新日志` 顶部新增本次提交前验收条目，包含：三处根因修复、依赖/环境实际状态、完整验证命令及结果、生成产物位置、仍受缺失凭证/登录态/平台授权限制的边界和全部影响文件。同步版本、最后维护日期、测试数量与当前状态；历史条目只追加纠正说明，不删除或静默改写。

最终重新运行 Python 全测、Ruff、Web 全套和隔离端到端流水线；只有所有必需检查真实通过且最终海报存在时才宣告完成。
