# QianCraft 最终完整 Codex 提示词
## —— 从知识与市场洞察，到策划、视觉设计与可编辑工作台的全链路实现

你现在在 **Codex** 中直接修改当前 QianCraft 项目。

本提示词是 QianCraft 当前阶段的**最终总任务说明**。  
请以当前仓库真实结构、已有代码、`WORKFLOW.md` 和现有正式产物为准，直接在当前项目中完成整合、补齐、运行和验证。

---

# 0. 总目标

QianCraft 的产品定位是：

> **一个面向贵州非遗与在地文化文创创新的 AI 创意智能工作台。**

它不是单纯的知识库，也不是单纯的爬虫、策划工具或图片生成器。

最终产品要把以下完整链路装进同一张可视化无限画布：

```text
贵州文化知识图谱
        +
互联网爆款文创市场数据
        ↓
GPT Researcher 策划师
        ↓
产品机会与设计前 Brief
        ↓
视觉设计 Agent
        ↓
产品 Concept / 效果图 / 场景图
        ↓
文化创意海报 / Design Board
```

用户可以：

```text
查看每一步
编辑每一步
重新运行某一步
从某一步继续向下生成
复制一个分支
比较不同 Concept
回到上游修改
重新生成下游
最终输出一张完整设计展示板
```

---

# 1. 开始前必须读取现有项目

任何修改前，先完整读取：

```text
WORKFLOW.md
AGENTS.md
README.md
docs/architecture.md
docs/knowledge_graph.md
docs/real_machine_test.md
docs/product_direction.md
```

检查现有正式输出：

```text
data/outputs/pre_design_strategy.json
data/outputs/pre_design_strategy.md
data/outputs/run_manifest.json
data/outputs/designer_handoff.json
data/outputs/designer_handoff.md
data/outputs/visual_reference_pack.json
data/outputs/visual_reference_pack.md
data/market/
data/culture/
data/benchmark/
```

如果部分文件当前不存在：

```text
不要停止
不要凭空假设
根据现有项目真实状态补齐
```

---

# 2. 当前已有核心技术底座

当前仓库已经包含或已经解压：

```text
1. LightRAG
   → 贵州非遗与在地文化知识图谱 / 文化知识底座

2. MediaCrawler
   → 市场调研 / 社交平台数据抓取

3. GPT Researcher
   → 系统中唯一策划师 / Strategist

4. React Flow / XYFlow 源码
   → QianCraft Workbench 无限画布底座
```

不要重新替换这些核心组件。

不要大面积魔改第三方核心源码。

统一采用：

```text
QianCraft 自己的 Adapter / API / Schema / UI
        ↓
第三方底层能力
```

必须保留第三方：

```text
LICENSE
NOTICE
copyright
THIRD_PARTY_NOTICES
```

---

# 3. QianCraft 当前最终架构

整个系统只保留三类智能核心：

```text
A. Culture Knowledge
   LightRAG
   = 提前构建好的贵州文化数据库 / 知识图谱

B. Market Intelligence
   MediaCrawler
   = 四平台真实市场抓取与爆款形态判断

C. Strategist
   GPT Researcher
   = 汇总文化 + 市场 + 案例，完成策划
```

后半段再接：

```text
D. Visual Designer
   = 根据 Designer Handoff 生成产品视觉 Concept

E. Poster / Design Board
   = 将文化来源、设计逻辑、产品视觉与市场依据组合成最终展示板
```

不要新增：

```text
Culture Agent
Trend Agent
Knowledge Agent
Curator Agent
Ranking Agent
Verification Agent
Orchestrator Agent
```

这些都不要。

---

# 4. 第一阶段：文化知识图谱

文化层使用：

```text
LightRAG
+
QianCraft 结构化 Culture Knowledge
```

目标：

> 形成稳定、可追溯、可检索、可服务设计的 Culture DNA。

---

# 5. Culture DNA 必须覆盖

至少：

```text
文化名称
地域
民族
历史
核心故事 / 神话
精神内涵
图腾
符号
纹样
色彩
材料
工艺
器物
使用场景
节庆 / 仪式
文化禁忌
支系差异
非遗保护信息
代表性传承人
既有文创
现代转译方式
可现代化元素
不适合随意商业化元素
```

---

# 6. Culture DNA 三个重点维度

## Visual DNA

```text
图形
轮廓
纹样
对称性
重复规律
构图
色彩
材料
工艺质感
```

## Semantic DNA

```text
生命
祖源
守护
祝福
身份
自然
迁徙
情绪意义
```

## Cultural Boundary

```text
哪些可以现代转译
哪些需要谨慎
哪些不能混用
哪些具有祭祀 / 仪式含义
哪些涉及支系身份
哪些涉及具体传承人作品
```

---

# 7. 文化知识必须证据可追溯

每个重要字段尽可能保留：

```text
culture_id
source_refs
field_sources
source_url
source_title
source_type
publisher
retrieved_at
```

现有原则继续保持：

```text
不得自动填补田野资料空白
不得混淆支系
不得把不同地区苗绣泛化为一个“苗绣风格”
```

对于贵州苗绣 Demo，必须继续区分：

```text
花溪挑花
剑河锡绣
松桃苗绣
雷山苗绣
```

---

# 8. 知识图谱自动维护

不要增加新 Agent。

在现有脚本 / Pipeline 中增加轻量自动治理：

```text
实体标准化
别名合并
重复实体检测
实体类型约束
关系类型约束
无证据节点检测
低质量节点检测
孤立节点检测
冲突检测
知识健康报告
```

建议允许的主要实体类型：

```text
Culture
Region
EthnicGroup
Craft
Pattern
Symbol
Story
Material
Color
Object
Person
```

关系类型尽量标准化：

```text
LOCATED_IN
BELONGS_TO
USES_CRAFT
USES_MATERIAL
HAS_PATTERN
HAS_SYMBOL
HAS_STORY
SYMBOLIZES
USED_IN
VARIANT_OF
DERIVED_FROM
```

不要让 LLM 无限创造关系名称。

---

# 9. 第二阶段：四平台 Market Intelligence

MediaCrawler 必须支持四个平台：

```text
1. 小红书 xhs
2. 抖音 dy
3. B站 bili
4. 微博 wb
```

本阶段目标非常简单：

> **判断互联网上哪些文创产品“形式 / 形态 / 品类”更受欢迎、更有卖点、更可能火。**

不要把这一层搞成复杂商业分析系统。

---

# 10. 四平台必须真实跑通

目标：

```text
xhs = live verified
dy = live verified
bili = live verified
wb = live verified
```

“理论支持”不算跑通。

必须至少：

```text
正常登录
正常关键词搜索
正常返回真实内容
真实结果落盘
```

每个平台先完成：

```text
5-20 条 Smoke Test
```

之后正式 MVP：

```text
每个平台 50-150 条高相关内容
```

总量：

```text
约 200-600 条即可
```

不要追求大规模抓取。

---

# 11. 登录方式

只使用 MediaCrawler 正常能力：

```text
二维码登录
或
CDP 复用用户本人已登录 Chrome
```

允许：

```text
用户本人扫码
正常登录态
正常 Cookie / Session 复用
```

不要实现：

```text
破解验证码
账号攻击
Cookie 窃取
绕过访问控制
复杂反爬破解
```

如果需要人工扫码：

```text
Codex 先完成所有代码
最后明确提示用户逐个平台授权
```

---

# 12. 市场关键词池

统一一套即可。

## 泛文创

```text
非遗文创
博物馆文创
国风文创
新中式文创
城市文创
景区文创
文创设计
```

## 产品形态

```text
文创冰箱贴
文创徽章
文创包挂
文创挂件
文创丝巾
文创首饰
文创毛绒
文创潮玩
文创香氛
文创盲盒
文创伴手礼
文创帆布袋
文创家居摆件
```

## 非遗相关

```text
苗绣文创
民族文创
非遗包挂
非遗首饰
非遗冰箱贴
传统纹样文创
```

---

# 13. 四平台统一数据结构

统一：

```json
{
  "platform": "xhs|dy|bili|wb",
  "post_id": "",
  "title": "",
  "content": "",
  "url": "",
  "published_at": "",
  "likes": 0,
  "favorites": 0,
  "comments": 0,
  "shares": 0,
  "views": 0,
  "product_form": "",
  "search_keyword": "",
  "retrieved_at": ""
}
```

拿不到的字段：

```text
null 或 0
```

禁止伪造。

---

# 14. 市场层只做必要清洗

只做：

```text
去重
空内容过滤
明显垃圾广告过滤
重复转发过滤
字段统一
时间统一
产品形态识别
```

不要复杂 NLP Pipeline。

不要复杂人群画像。

不要复杂价格建模。

不要销量预测。

---

# 15. 产品形态识别

市场层最重要的业务输出：

# Product Form

例如：

```text
包挂
冰箱贴
徽章
毛绒挂件
首饰
丝巾
潮玩
香氛
盲盒
帆布袋
伴手礼
家居摆件
```

可以通过：

```text
关键词规则
+
简单 LLM 分类
```

完成。

不要新建 Agent。

---

# 16. Platform Hot Score

不同平台绝对数据不能直接横向比较。

必须先在平台内部归一化：

```text
platform_hot_score: 0-100
```

只和本平台样本比。

可用：

```text
percentile
或
简单归一化
```

平台侧可稍微差异化：

### 小红书

```text
收藏
点赞
评论
```

### 抖音

```text
点赞
评论
分享
播放（如果可得）
```

### B站

```text
播放
点赞
收藏
评论
```

### 微博

```text
点赞
评论
转发
```

不要把公式设计得过复杂。

---

# 17. Cross-platform Hot Score

最终按产品形态聚合。

每个 Product Form 计算：

```text
各平台平均热度
高热帖子比例
出现次数
平台覆盖数
近期性
```

形成：

```text
cross_platform_hot_score: 0-100
```

最终生成：

```text
Top 10 Hot Product Forms
Top 5 Priority Product Forms
```

这是 GPT Researcher 最重要的市场输入。

---

# 18. 市场正式输出

必须存在：

```text
data/market/raw/xhs.jsonl
data/market/raw/dy.jsonl
data/market/raw/bili.jsonl
data/market/raw/wb.jsonl

data/market/derived/product_form_hotness.json
```

其中：

```text
product_form_hotness.json
```

至少：

```json
{
  "generated_at": "",
  "platforms": ["xhs", "dy", "bili", "wb"],
  "total_sample_size": 0,
  "ranking": [],
  "priority_product_forms": []
}
```

---

# 19. Market Evidence 分级

市场来源统一标记：

```text
social_signal
institutional_signal
media_signal
product_signal
```

保留：

```text
market_evidence_quality: 0-100
```

只作为内部排序与解释，不宣称为统计预测。

---

# 20. 第三阶段：GPT Researcher Strategist

GPT Researcher 是系统中唯一真正的策划师。

它不再主要负责“上网找文化”。

它主要读取：

```text
Culture DNA
Trend DNA
product_form_hotness.json
Benchmark Cases
Visual Reference Pack
LightRAG 相关知识
```

然后进行：

```text
总结
对比
交叉分析
机会判断
产品方向策划
设计前约束整理
```

---

# 21. 策划师 Cross-Matching

至少分析：

```text
文化视觉元素 × 热门产品形态
文化精神寓意 × 消费情绪价值
传统色彩 × 当前视觉趋势
传统材料 × 当前材料趋势
传统工艺 × 当代产品形式
文化故事 × 社交传播卖点
文化使用场景 × 当代生活场景
Benchmark × 贵州文化可借鉴方式
```

---

# 22. Opportunity Signals

保留完整 Opportunity Signals。

每条至少：

```json
{
  "opportunity_id": "",
  "culture_element": "",
  "culture_meaning": "",
  "trend_element": "",
  "market_signal": "",
  "match_reason": "",
  "potential_product_categories": [],
  "target_audience": [],
  "design_keywords": [],
  "cultural_constraints": [],
  "evidence_refs": [],
  "confidence_score": 0
}
```

每条必须至少：

```text
1 个 Cxxx
+
1 个 Mxxx
```

---

# 23. Opportunity Score

每条机会增加：

```text
culture_fit
market_pull
visual_potential
novelty
social_shareability
product_feasibility
cultural_risk
overall_score
```

建议正向权重：

```text
culture_fit          20%
market_pull          20%
visual_potential     20%
novelty              15%
social_shareability  15%
product_feasibility  10%
```

`cultural_risk` 作为惩罚项。

不要声称这是机器学习预测模型。

它只是：

> QianCraft 内部可解释的机会排序方法。

---

# 24. Top 3

完整报告保留全部 Opportunity。

但 Designer Handoff 只接收：

```text
Top 3 Priority Opportunities
```

Top 3 是：

> 三个最高优先级“设计机会空间”

不是三个最终产品。

---

# 25. LightRAG 二次验证

不要新增 Verification Agent。

直接在 Strategist 中：

```text
初步 Opportunity
        ↓
高分候选
        ↓
重新 Query LightRAG
        ↓
检查：
地域
支系
文化边界
禁忌
已有转译
证据完整性
        ↓
verified / warning / rejected
```

每个 Top Opportunity 增加：

```json
{
  "verification": {
    "status": "verified|warning|rejected",
    "queries": [],
    "culture_evidence_refs": [],
    "conflicts": [],
    "warnings": [],
    "verification_notes": ""
  }
}
```

rejected 不得进入 Designer Handoff。

---

# 26. Visual Reference Pack

必须生成：

```text
data/outputs/visual_reference_pack.json
data/outputs/visual_reference_pack.md
```

目标：

> 让视觉设计 Agent 看到真实文化视觉来源，而不是只读“蝴蝶纹”“鸟纹”几个词。

至少：

```text
花溪挑花
剑河锡绣
松桃苗绣
雷山苗绣
蝴蝶纹
鸟纹
龙纹
传统服饰局部
针法 / 绣线层次
锡 / 银等材料视觉
```

每条：

```json
{
  "reference_id": "V001",
  "culture_id": "Cxxx",
  "name": "",
  "type": "",
  "region": "",
  "ethnic_group": "",
  "image_url": "",
  "local_path": "",
  "source_ref": "",
  "visual_features": [],
  "extractable_features": [],
  "design_notes": [],
  "cultural_risk": "",
  "reference_only": true
}
```

---

# 27. Designer Handoff

最终机器接口必须是：

```text
data/outputs/designer_handoff.json
```

它是下一阶段视觉设计 Agent 的：

# Single Source of Truth

同时自动生成：

```text
designer_handoff.md
```

Markdown 必须从 JSON 渲染，不要人工维护两套不同内容。

---

# 28. Designer Handoff 顶层结构

```json
{
  "project": {},
  "design_mission": {},
  "culture_context": {},
  "market_context": {},
  "priority_opportunities": [],
  "visual_reference_pack": {},
  "hard_constraints": {},
  "soft_direction": {},
  "creative_brief": "",
  "output_requirements": {},
  "evidence_refs": []
}
```

JSON 负责硬约束。

`creative_brief` 负责自然语言设计语境。

---

# 29. creative_brief

长度：

```text
150-350 中文字
```

必须综合：

```text
文化精神
目标用户
现代场景
市场趋势
产品气质
视觉态度
```

原则：

```text
不做传统纹样贴图
不做泛化民族风
强调现代转译
强调年轻、日常、传播性
保留文化来源
```

---

# 30. 第四阶段：React Flow Workbench

当前已经解压 React Flow / XYFlow ZIP。

本轮要把它纳入 QianCraft，作为：

# QianCraft Creative Intelligence Workbench

如果直接本地引用源码容易：

```text
可本地引用
```

如果会导致 monorepo / workspace 复杂：

```text
保留源码目录作为 vendor/reference
使用标准 @xyflow/react
```

优先：

```text
最快跑通
最少侵入
最好维护
```

---

# 31. 工作台最终布局

固定三栏：

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ QianCraft Workbench                                                     │
├─────────────────┬──────────────────────────────────────┬─────────────────┤
│ Knowledge Center│        Infinite Canvas               │ Inspector       │
│                 │        React Flow / XYFlow           │                 │
│ 市场雷达        │                                      │ 当前节点        │
│ 文化知识图谱    │                                      │ 参数            │
│                 │                                      │ 输入            │
│                 │                                      │ Prompt          │
│                 │                                      │ 来源            │
│                 │                                      │ 历史版本        │
│                 │                                      │ Run / Re-run    │
└─────────────────┴──────────────────────────────────────┴─────────────────┘
```

---

# 32. Knowledge Center

只两个栏目：

## A. 市场雷达

显示：

```text
XHS
DY
BILI
WB
```

状态：

```text
LIVE / CACHE / ERROR
```

以及：

```text
Top Product Forms
Cross-platform Hot Score
代表帖子
更新时间
```

## B. 文化知识

显示：

```text
主题
实体数量
关系数量
关键文化节点
```

支持：

```text
打开图谱
搜索文化
```

点击文化实体后 Inspector 展示：

```text
名称
类型
地域
支系
文化含义
视觉特征
材料
工艺
来源
可现代化方向
文化边界
参考图片
```

---

# 33. 中央 Canvas 只做 7 类主节点

第一版只做：

```text
1. CultureGraphNode
2. MarketRadarNode
3. StrategyNode
4. DesignBriefNode
5. VisualGenerationNode
6. ConceptNode
7. PosterBoardNode
```

不要增加几十种通用节点。

---

# 34. 所有 Node 统一状态

```text
idle
running
success
warning
error
cached
stale
```

每个可执行 Node 至少：

```text
Run
Re-run
Run from here
```

---

# 35. 下游 stale

上游修改后：

```text
只把依赖下游标 stale
```

不要自动重跑整条链。

例如：

```text
Design Brief 修改
↓
Visual Generation = stale
Concept = stale
Poster = stale
```

用户主动：

```text
Run from here
```

才重新运行。

---

# 36. CultureGraphNode

显示摘要：

```text
CULTURAL KNOWLEDGE
贵州苗绣
612 Entities
697 Relations

Key Elements
...
```

支持：

```text
Explore Graph
Refresh
```

完整图谱在 Drawer / Modal / Overlay 打开。

不要塞满 Node。

---

# 37. MarketRadarNode

显示：

```text
MARKET INTELLIGENCE

XHS  LIVE
DY   LIVE
BILI LIVE
WB   LIVE

Top Forms
1. xxx
2. xxx
3. xxx
```

数据必须来自真实 `product_form_hotness.json`。

---

# 38. StrategyNode

显示：

```text
Opportunity Signals 数量
Top 3
Score
Verification
```

点击某机会：

Inspector 展示：

```text
Culture Basis
Market Basis
Benchmark
Score Breakdown
Verification
Warnings
Sources
```

支持：

```text
Pin
Exclude
```

即可。

不要复杂排序编辑。

---

# 39. DesignBriefNode

读取：

```text
designer_handoff.json
```

必须可编辑：

```text
target_user
product_direction
must_keep
can_modernize
avoid
design_keywords
material_direction
color_direction
output_requirements
creative_brief
```

保存后：

```text
version + 1
下游 stale
```

不允许修改 Culture / Market 原始事实。

---

# 40. 第五阶段：Visual Generation

VisualGenerationNode 作为：

> 视觉设计 Agent / 图像模型入口

不要把 Provider 写死。

统一：

```text
IMAGE_PROVIDER
IMAGE_API_KEY
IMAGE_BASE_URL
IMAGE_MODEL
```

建立：

```text
image_generation_adapter
```

如果已有图像生成能力：

```text
直接接
```

如果没有：

```text
先完成 Adapter 和 UI
provider missing 时明确显示
```

---

# 41. VisualGenerationNode 输入

```text
Designer Handoff
Visual Reference Pack
Selected Opportunity
Product Form
Style
Material
Color
Reference Images
Additional Prompt
```

默认生成：

```text
Concept A
Concept B
Concept C
```

并在 React Flow 中自动创建：

```text
3 个 ConceptNode
```

---

# 42. ConceptNode

必须直接显示图片。

至少支持：

```text
Edit
Regenerate
Duplicate
Use
Generate More
```

一个 Concept 可包含：

```text
concept_image
product_render
detail_image
usage_scene
```

版本不能覆盖旧图：

```text
v1
v2
v3
```

支持：

```text
Set as active
```

---

# 43. 第六阶段：Poster / Design Board

PosterBoardNode 输入：

```text
Active Concept
Culture Context
Market Context
Design Brief
Visual References
```

最终组合：

```text
产品名称
产品主视觉
文化来源
原始视觉参考
文化元素提取
现代转译逻辑
产品细节
使用场景
市场依据
设计关键词
文化边界
```

---

# 44. Poster Board 必须可编辑

不要只生成一张死图。

第一版：

```text
固定模板 + 可编辑内容
```

支持：

```text
修改标题
修改文案
替换图片
显示 / 隐藏 section
调整简单顺序
```

最终：

```text
Export PNG
```

PDF 只有容易稳定实现才做。

---

# 45. 不要做 Figma / Photoshop

本轮不要实现：

```text
自由矢量绘图
复杂图层系统
Bezier
复杂 Mask
专业排版引擎
实时多人协作
```

QianCraft 是：

> AI Creative Workbench

不是重做设计软件。

---

# 46. Inspector

右侧统一 Inspector。

根据 Node Type 显示：

```text
Node Info
Inputs
Parameters
Outputs
Sources
Run History
Actions
```

不要跳转多个传统页面。

---

# 47. Workspace Persistence

保存：

```text
nodes
edges
viewport
selected concept
node versions
workflow metadata
```

第一版：

```text
JSON
```

例如：

```text
data/workbench/workspaces/{workspace_id}.json
```

支持：

```text
New
Save
Load
Rename
```

---

# 48. 前后端连接

前端不能直接 import Python 模块。

所有节点通过 HTTP API 调现有后端。

统一最小 API，例如：

```text
POST /api/workbench/culture/run
POST /api/workbench/market/run
POST /api/workbench/strategy/run
POST /api/workbench/design-brief/save
POST /api/workbench/visual/generate
POST /api/workbench/poster/render

GET /api/workbench/workspaces/{id}
PUT /api/workbench/workspaces/{id}
```

如果已有 API：

```text
直接复用
```

---

# 49. 长任务

MediaCrawler / GPT Researcher / Image Generation：

```text
不能卡住 UI
```

Node 状态：

```text
Searching...
Analyzing...
Generating...
Done
```

轮询即可。

现有 SSE / WebSocket 有的话复用。

---

# 50. 默认贵州苗绣 Demo

启动后默认可载入：

```text
贵州苗绣 Demo
```

Canvas：

```text
Culture        Market
    \          /
      Strategy
         |
    Design Brief
         |
 Visual Generation
   /      |      \
 A        B       C
          |
        Poster
```

Fit View 后一眼看懂全链路。

---

# 51. 产品视觉风格

不要做成：

```text
Dify
n8n
后台管理系统
```

目标：

# Creative AI Workbench

参考感觉：

```text
Figma
Weave
Krea Nodes
Linear
Notion
```

风格：

```text
中性背景
大量留白
圆角卡片
弱阴影
细线
图片优先
状态清晰
信息密度高但不拥挤
```

---

# 52. 推荐 Workbench 目录

根据真实项目调整。

如果已有 frontend：

```text
直接新增 /workbench 路由
```

不要再造第二套前端。

如果没有前端，可新增：

```text
workbench/
├── src/
│   ├── components/
│   │   ├── canvas/
│   │   ├── knowledge/
│   │   ├── inspector/
│   │   └── common/
│   ├── nodes/
│   │   ├── CultureGraphNode.tsx
│   │   ├── MarketRadarNode.tsx
│   │   ├── StrategyNode.tsx
│   │   ├── DesignBriefNode.tsx
│   │   ├── VisualGenerationNode.tsx
│   │   ├── ConceptNode.tsx
│   │   └── PosterBoardNode.tsx
│   ├── api/
│   ├── store/
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
```

---

# 53. API Client

所有 Node 不自行 fetch。

统一：

```text
api.runCulture()
api.runMarket()
api.runStrategy()
api.saveDesignBrief()
api.generateVisual()
api.renderPoster()
```

集中在：

```text
api/client.ts
```

---

# 54. 图片资产

不要把 Base64 塞进 Workspace。

只保存：

```text
asset_id
path
url
```

Workspace 保存引用。

---

# 55. P0 / P1

## P0 必须完成

```text
React Flow Canvas
Knowledge Center
Inspector
7 个主 Node
四平台市场数据可显示
文化图谱可查看
Strategy Top 3
Design Brief 可编辑
Node Run / Re-run
stale propagation
Workspace Save / Load
Visual Generation Adapter
Concept 图片显示
Poster Board Layout
贵州苗绣 Demo
```

## P1 时间允许

```text
Undo/Redo
Reference Card
拖知识到 Canvas
Concept Version UI
Poster PNG Export
Node Group
Workflow History
```

不要让 P1 阻塞 P0。

---

# 56. 测试

继续保证现有：

```text
Python tests
Pydantic
Ruff
Evidence
Credential scan
```

前端增加至少：

```text
build
typecheck
lint
```

工作台至少测试：

```text
Workbench render
Node registry
Edge validation
Workspace serialization
Workspace loading
Design Brief editing
stale propagation
Node run status
API mapping
Concept creation
Poster input validation
```

---

# 57. RunManifest

继续保留。

必须记录：

```text
culture = live/cache
xhs = live/cache/error
dy = live/cache/error
bili = live/cache/error
wb = live/cache/error
strategist = live/cache
visual = live/cache/placeholder
poster = live/cache
```

禁止把 cache / placeholder 冒充 live。

---

# 58. 安全与许可证

MediaCrawler 当前仍是：

```text
非商业学习 / 研究
```

比赛 Demo 可以用于研究验证。

商业化前：

```text
必须获得适当授权
或替换采集实现
```

继续保留：

```text
THIRD_PARTY_NOTICES.md
React Flow LICENSE
LightRAG LICENSE
GPT Researcher LICENSE
MediaCrawler LICENSE
```

---

# 59. WORKFLOW.md 必须同步维护

本轮完成后必须更新：

```text
当前状态
完整端到端流程
知识图谱
四平台市场
产品形态热度
Strategist
Top 3
Designer Handoff
Visual Generation
React Flow Workbench
7 个 Node
Workspace
Poster Board
测试结果
运行命令
限制
```

并在更新日志顶部追加：

```text
变更
原因
验证
边界
涉及文件
```

历史日志不得删除。

---

# 60. 最终完整链路

本轮完成后，QianCraft 正式链路应为：

```text
贵州非遗 / 在地文化资料
        ↓
LightRAG Knowledge Graph
        ↓
Culture DNA
        │
        ├──────────────────────────┐
        │                          │
四平台 MediaCrawler                │
xhs / dy / bili / wb               │
        ↓                          │
Product Form Hotness               │
        ↓                          │
Trend DNA ─────────────────────────┤
                                   ↓
                         GPT Researcher
                           Strategist
                                   ↓
                         Opportunity Signals
                                   ↓
                         Opportunity Score
                                   ↓
                               TOP 3
                                   ↓
                         LightRAG 二次验证
                                   ↓
                         Designer Handoff
                         JSON + Creative Brief
                                   ↓
                         Visual Generation
                                   ↓
                         Concept A / B / C
                                   ↓
                         Refine / Regenerate
                                   ↓
                         Poster / Design Board
                                   ↓
                         Export / Present
```

全部在：

# QianCraft Creative Intelligence Workbench

同一张 React Flow 无限画布中可视化。

---

# 61. 现在直接执行

不要再给我新架构建议。

请直接：

```text
1. 读取 WORKFLOW / AGENTS / README
2. 扫描当前真实目录
3. 检查四个上游项目
4. 检查 React Flow 解压源码
5. 选择最稳 React Flow 接入方式
6. 补齐四平台市场 live 路径
7. 补齐产品形态热度输出
8. 补齐 Visual Reference Pack
9. 补齐 Opportunity Score / Top 3 / 二次验证
10. 补齐 Designer Handoff
11. 建立 Workbench
12. 完成 7 类 Node
13. 接现有后端
14. 接 Visual Generation Adapter
15. 完成 Concept 分支
16. 完成 Poster Board
17. 完成 Workspace Save / Load
18. 跑贵州苗绣完整 Demo
19. 修复所有阻塞问题
20. 前后端测试
21. 更新 README
22. 更新 WORKFLOW
```

---

# 62. 遇到需要人工授权时

如果需要：

```text
小红书扫码
抖音扫码
B站扫码
微博扫码
Chrome CDP 确认
图像 API Key
```

先完成所有不依赖人工操作的代码。

然后明确告诉我：

```text
现在请执行第 1 个授权动作：
……
```

不要因为等待登录阻塞全部开发。

---

# 63. 最终完成定义

只有以下全部满足才算完成：

- [ ] Culture Knowledge 可真实读取
- [ ] 小红书 live verified
- [ ] 抖音 live verified
- [ ] B站 live verified
- [ ] 微博 live verified
- [ ] product_form_hotness.json 生成
- [ ] Culture DNA 证据可追溯
- [ ] Opportunity Score 完成
- [ ] Top 3 完成
- [ ] Top 3 LightRAG 二次验证完成
- [ ] Visual Reference Pack 完成
- [ ] designer_handoff.json 完成
- [ ] creative_brief 完成
- [ ] React Flow Workbench 完成
- [ ] Knowledge Center 完成
- [ ] Inspector 完成
- [ ] 7 个主 Node 完成
- [ ] Node Run / Re-run 完成
- [ ] stale propagation 完成
- [ ] Workspace Save / Load 完成
- [ ] Visual Generation 可运行或明确 provider missing
- [ ] Concept A/B/C 可显示
- [ ] Concept 可编辑 / Regenerate
- [ ] Poster Board 可展示
- [ ] 贵州苗绣 Demo 跑通
- [ ] 前端 build/typecheck/lint 通过
- [ ] 后端测试通过
- [ ] 凭证扫描通过
- [ ] WORKFLOW.md 更新完成

---

# 64. 最终只汇报

```text
1. 当前完整链路是否跑通
2. React Flow 如何接入
3. Workbench 启动方式
4. 四个平台分别是 live / cache / error
5. 市场总样本数
6. Top 10 产品形态
7. Top 3 策划机会
8. Culture / Market / Strategy 是否真实接入
9. Designer Handoff 是否完成
10. Visual Generation 当前状态
11. Concept A/B/C 是否可生成
12. Poster Board 是否完成
13. Workspace Save / Load 是否完成
14. 前端测试结果
15. 后端测试结果
16. WORKFLOW.md 新日志位置
17. 仍需要我进行什么人工授权
```

不要输出冗长技术散文。

---

# 65. 最终产品定义

QianCraft 最终不是：

```text
一个知识库
一个爬虫
一个策划脚本
一个图片生成器
```

而是：

# **QianCraft Creative Intelligence Workbench**

用户看到的是：

```text
Know
↓
Discover
↓
Strategize
↓
Design
↓
Refine
↓
Present
```

所有过程：

> **在同一张无限画布中可视化、可编辑、可操作、可回溯。**

这就是最终目标。
