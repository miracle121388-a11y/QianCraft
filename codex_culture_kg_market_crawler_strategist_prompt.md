# Codex：文化知识图谱 + 市场爬虫 + GPT Researcher 策划系统提示词

你现在在 **Codex** 中直接执行开发任务。

当前项目根目录下已经有三个解压好的独立项目文件夹：

1. GPT Researcher
2. MediaCrawler
3. LightRAG

请先自动识别这三个目录的实际名称与位置，不要假设它们一定叫固定文件名。

我们的真实架构不是“三个独立 Agent”。

而是三部分：

```text
① 文化知识底座
   = 我们提前构建好的文化数据库 / 知识图谱
   = 主要由 LightRAG 承担

② 市场调研模块
   = MediaCrawler
   = 负责抓取社交媒体上的爆款文创与市场趋势

③ 策划师 Agent
   = GPT Researcher
   = 负责读取前面两部分的结果
   = 进行总结、对比、推理、策划
   = 最终生成进入产品设计前的完整策划 Brief
```

因此整个系统的核心关系是：

```text
                    用户输入文化主题
                           │
                           ▼
              ┌──────────────────────┐
              │   文化知识图谱 / 数据库 │
              │      LightRAG        │
              └─────────┬────────────┘
                        │
                 Culture Knowledge
                        │
                        │
                        ▼
              ┌──────────────────────┐
              │   策划师 GPT Researcher │
              │                      │
              │  汇总 + 对比 + 推理     │
              │  文化 × 市场融合策划     │
              └─────────┬────────────┘
                        ▲
                        │
                  Market Research
                        │
              ┌─────────┴────────────┐
              │     MediaCrawler     │
              │  社媒爆款 / 趋势调研   │
              └──────────────────────┘
                        │
                        ▼
            Pre-Design Strategy Brief
                        │
                        ▼
                  下一阶段产品设计
```

本次开发到这里结束。

**不要实现真正的设计师 Agent。**
**不要生成最终产品图。**
**不要做 ComfyUI。**
**不要继续拆更多 Agent。**
**不要重新设计复杂的多 Agent 系统。**

---

# 一、总体目标

我们希望系统完成下面这条链：

```text
输入一个贵州文化主题
例如：贵州苗绣
        ↓
从文化知识图谱中提取与该主题相关的文化知识
        ↓
MediaCrawler 搜集当前市场上爆款文创、流行品类、视觉风格、消费者偏好
        ↓
把文化知识 + 市场趋势统一整理
        ↓
交给 GPT Researcher
        ↓
GPT Researcher 进行深度总结、交叉分析、产品机会发现
        ↓
输出完整 Pre-Design Strategy Brief
        ↓
交给下一阶段设计
```

这里最重要的是：

> **GPT Researcher 不再主要负责“自己去网上研究文化”。**

它在当前架构中的核心角色是：

> **策划师 / Strategist**

它主要读取：

```text
文化知识图谱
+
市场调研结果
+
成功案例
```

然后做：

```text
总结
对比
交叉分析
机会判断
策划
```

---

# 二、先检查三个项目

开始写代码前，先扫描当前根目录。

识别：

```text
GPT Researcher 实际目录
MediaCrawler 实际目录
LightRAG 实际目录
```

检查三个项目的：

```text
README
启动方式
依赖
配置文件
API / CLI
```

不要大规模修改第三方源码。

优先采用：

```text
我们自己的 Python 代码
        ↓
Adapter / Wrapper
        ↓
第三方项目
```

如果移动目录会破坏原项目，就不要移动。

---

# 三、只建立一个极简自有目录

不要复杂化。

创建：

```text
app/
├── strategist/
│   ├── strategist.py
│   └── prompt.md
│
├── adapters/
│   ├── media_crawler_adapter.py
│   ├── lightrag_adapter.py
│   └── gpt_researcher_adapter.py
│
├── schemas.py
├── pipeline.py
└── config.py

data/
├── culture/
├── market/
├── benchmark/
├── outputs/
└── demo_cache/

scripts/
├── run_demo.py
└── check_environment.py

tests/
└── test_demo_pipeline.py
```

不要再拆更多 Agent 目录。

---

# 四、第一部分：文化知识底座

文化研究不是实时临时搜索。

我们希望提前构建一个：

> **贵州非遗与在地文化知识库 / 知识图谱**

底层使用：

> LightRAG

它不是 Agent。

它只是系统的文化知识底座。

---

# 五、文化知识库至少包含的内容

针对贵州非遗与在地文化，知识库至少要覆盖：

```text
1. 文化名称
2. 地域
3. 民族
4. 历史源流
5. 神话故事
6. 文化叙事
7. 精神内涵
8. 图腾
9. 符号
10. 纹样
11. 色彩
12. 材质
13. 工艺
14. 代表器物
15. 使用场景
16. 节庆与仪式
17. 文化禁忌
18. 支系差异
19. 非遗保护信息
20. 代表性传承人
21. 既有文创产品
22. 已有现代转译方式
23. 可现代化的文化元素
24. 不适合随意商业化的文化元素
```

---

# 六、文化知识图谱要能输出什么

当输入：

```text
贵州苗绣
```

系统应通过 LightRAG 返回类似：

```json
{
  "culture_name": "贵州苗绣",
  "region": [],
  "ethnic_groups": [],
  "history": [],
  "core_stories": [],
  "core_values": [],
  "symbols": [],
  "patterns": [],
  "colors": [],
  "materials": [],
  "crafts": [],
  "objects": [],
  "visual_features": [],
  "emotional_meanings": [],
  "cultural_taboos": [],
  "modernizable_elements": [],
  "non_transferable_elements": [],
  "existing_cultural_products": [],
  "source_refs": []
}
```

这可以统一称为：

# Culture DNA

---

# 七、Culture DNA 最重要的三部分

## 7.1 Visual DNA

```text
图形
纹样
色彩
材质
工艺
造型
构图
```

## 7.2 Semantic DNA

```text
生命
守护
祝福
祖源
自然
身份
……
```

## 7.3 Cultural Boundary

```text
哪些可以现代转译
哪些必须谨慎
哪些不能乱用
哪些存在祭祀 / 仪式含义
```

这些信息最终直接传给 GPT Researcher。

---

# 八、文化知识库必须保留来源

每条重要文化信息尽量保留：

```text
source_id
source_url
source_title
source_type
publisher
retrieved_at
```

因为后面 GPT Researcher 的策划判断必须尽可能可追溯。

---

# 九、第二部分：市场调研模块

市场调研不是 Agent。

它就是：

> MediaCrawler

它负责：

> 从社交媒体中抓取当前已经爆款或正在流行的文创产品、品类、风格和消费偏好。

---

# 十、MediaCrawler 主要抓取平台

优先：

```text
小红书
抖音
B站
微博
```

48 小时 MVP：

> 至少真实跑通一个平台。

其他平台保留接口即可。

---

# 十一、市场调研关键词体系

不要只搜索“文创”。

建立关键词组合。

## 产品词

```text
文创
非遗文创
博物馆文创
城市文创
景区文创
冰箱贴
徽章
包挂
挂件
手机挂饰
丝巾
首饰
耳饰
项链
香氛
潮玩
毛绒
盲盒
茶具
摆件
帆布袋
伴手礼
```

## 风格词

```text
国风
新中式
东方美学
轻国风
非遗
传统纹样
民族风
年轻化国风
```

## 爆款信号词

```text
爆款
断货
抢不到
种草
必买
出圈
收藏
限定
联名
```

---

# 十二、MediaCrawler 抓取字段

至少保留：

```json
{
  "platform": "",
  "post_id": "",
  "title": "",
  "content": "",
  "author": "",
  "published_at": "",
  "url": "",
  "likes": 0,
  "favorites": 0,
  "comments": 0,
  "shares": 0,
  "tags": [],
  "search_keyword": ""
}
```

拿不到的字段允许为空。

---

# 十三、市场数据清洗

不要新增清洗 Agent。

直接在 Adapter / Pipeline 内做。

至少：

```text
去重
空文本过滤
明显营销垃圾过滤
字段统一
时间统一
重复帖子过滤
异常互动数据过滤
```

---

# 十四、市场数据要形成 Trend Summary

不能把几千条帖子直接交给 GPT Researcher。

先进行简单结构化处理。

形成：

# Trend DNA

至少：

```json
{
  "time_window": "",
  "platforms": [],
  "sample_size": 0,
  "hot_categories": [],
  "rising_categories": [],
  "hot_styles": [],
  "hot_colors": [],
  "hot_materials": [],
  "target_audiences": [],
  "price_ranges": [],
  "usage_scenarios": [],
  "emotional_values": [],
  "viral_mechanisms": [],
  "visual_patterns": [],
  "saturated_categories": [],
  "white_space_opportunities": [],
  "representative_cases": [],
  "source_refs": []
}
```

---

# 十五、爆款评分

实现一个简单可解释的 Viral Score。

例如：

```text
Viral Score
=
互动量
+ 收藏
+ 评论
+ 新鲜度
+ 同类内容出现频率
```

归一化：

```text
0-100
```

每个代表案例可以输出：

```json
{
  "viral_score": 89,
  "viral_reasons": [
    "收藏量高",
    "互动率高",
    "近期多个类似产品同时出现"
  ]
}
```

不需要构建真实商业级预测模型。

---

# 十六、Benchmark Cases

从 MediaCrawler 的高热度结果中，顺便整理：

> 已有成功文创案例

可以包括：

```text
故宫
敦煌
三星堆
河南博物院
苏州博物馆
地方非遗品牌
热门景区文创
```

统一结构：

```json
{
  "brand_or_institution": "",
  "culture_source": "",
  "product_category": "",
  "design_idea": "",
  "visual_style": "",
  "innovation_point": "",
  "market_signal": "",
  "why_it_worked": [],
  "source_refs": []
}
```

这些可以：

```text
保存到 data/benchmark/
+
写入 LightRAG
```

供 GPT Researcher 查询。

---

# 十七、第三部分：策划师

真正的 Agent 只有这里。

名称：

> Strategist Agent / 策划师

底层：

> GPT Researcher

它不是简单总结器。

它是整个系统的策划大脑。

---

# 十八、GPT Researcher 在这里的角色

它需要同时读取：

```text
Culture DNA
+
Trend DNA
+
Benchmark Cases
+
LightRAG 中的相关知识
```

然后完成：

```text
文化理解
市场理解
案例理解
交叉分析
机会判断
产品方向策划
设计前约束整理
```

---

# 十九、策划师必须做的 Cross-Matching

至少分析：

```text
1. 文化视觉元素 × 热门产品品类

2. 文化精神寓意 × 当前消费者情绪价值

3. 传统色彩 × 当前视觉趋势

4. 传统材质 × 当前材料趋势

5. 传统工艺 × 可现代化产品形式

6. 文化故事 × 社交媒体传播卖点

7. 文化使用场景 × 当代生活场景

8. 既有成功案例 × 贵州文化可借鉴方式
```

---

# 二十、策划师要先生成 Opportunity Signals

至少输出 8 个。

结构：

```json
{
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

这里只输出：

> 值得探索的机会。

不是最终设计。

---

# 二十一、策划师最终输出

生成：

```text
data/outputs/pre_design_strategy.json
data/outputs/pre_design_strategy.md
```

---

# 二十二、最终 JSON

至少：

```json
{
  "project": {},
  "culture_dna": {},
  "trend_dna": {},
  "benchmark_cases": [],
  "opportunity_signals": [],
  "recommended_product_categories": [],
  "design_keywords": [],
  "cultural_constraints": [],
  "evidence_summary": {},
  "handoff_to_designer": {}
}
```

---

# 二十三、最终 Markdown

固定结构：

```text
# 贵州文化文创前策划报告

## 1. 研究对象

## 2. 文化底座告诉了我们什么
- 核心故事
- 精神内涵
- 视觉元素
- 色彩
- 材料
- 工艺
- 文化边界

## 3. 市场调研告诉了我们什么
- 当前热门产品
- 上升品类
- 年轻消费者偏好
- 风格趋势
- 情绪价值
- 社交传播规律

## 4. 当前成功文创案例
- 哪些案例做得好
- 为什么成功
- 有什么可以借鉴

## 5. Culture × Trend 交叉分析

## 6. 最值得探索的 8-15 个机会

## 7. 推荐进入下一阶段的产品类别
这里只给方向，不形成最终设计

## 8. 设计关键词

## 9. 设计必须遵守的文化边界

## 10. 数据与来源

## 11. 给下一阶段设计的 Handoff
```

---

# 二十四、Designer Handoff

必须生成：

```json
{
  "handoff_to_designer": {
    "ready": true,
    "culture_dna": {},
    "trend_dna": {},
    "benchmark_cases": [],
    "priority_opportunities": [],
    "recommended_product_categories": [],
    "design_keywords": [],
    "must_keep": [],
    "can_modernize": [],
    "avoid": [],
    "source_refs": []
  }
}
```

到此结束。

---

# 二十五、整个系统不要再扩

最终系统只有：

```text
                用户
                 │
                 ▼
        ┌──────────────────┐
        │  Culture Knowledge │
        │   LightRAG KG      │
        └────────┬─────────┘
                 │
          Culture DNA
                 │
                 ▼
        ┌──────────────────┐
        │   GPT Researcher   │
        │   策划师 Agent      │
        │                  │
        │ 汇总 / 对比 / 推理   │
        │ 产品机会 / 前置策划   │
        └────────┬─────────┘
                 ▲
                 │
           Trend DNA
                 │
        ┌────────┴─────────┐
        │   MediaCrawler    │
        │   市场调研模块      │
        └──────────────────┘
                 │
                 ▼
        Pre-Design Strategy Brief
                 │
                 ▼
             下一阶段设计
```

不要新增：

```text
Culture Agent
Trend Agent
Knowledge Agent
Curator Agent
Analyst Agent
Orchestrator Agent
```

这些都不要。

---

# 二十六、Demo 模式

时间只有 48 小时。

必须支持：

```text
LIVE_MODE
DEMO_MODE
```

预先准备：

```text
data/demo_cache/
├── culture_dna.json
├── trend_dna.json
├── benchmark_cases.json
└── pre_design_strategy.json
```

当：

```text
MediaCrawler 登录失败
Cookie 失效
平台限制
GPT Researcher API 超时
LightRAG 暂时不可用
```

可以 fallback。

日志标清：

```text
live
cache
mock
```

不要把 mock 冒充成实时数据。

---

# 二十七、第一个 Demo 固定做“贵州苗绣”

输入：

```json
{
  "topic": "贵州苗绣",
  "region": "贵州",
  "target_market": "18-30岁年轻消费者",
  "goal": "寻找具有爆款潜力的文创产品机会"
}
```

最低要求：

## Culture DNA

必须出现：

```text
苗绣
蝴蝶妈妈
鸟纹
龙纹
传统色彩
材料
工艺
生命 / 祖源 / 守护等寓意
文化边界
```

## Trend DNA

必须出现：

```text
当前热门文创品类
年轻消费者偏好
视觉趋势
材料趋势
社交传播规律
爆款案例
```

## GPT Researcher

至少：

```text
8 个 Opportunity Signals
3-8 个重点产品类别
一套完整 Design Handoff
```

---

# 二十八、运行入口

最终必须让我可以用：

```bash
python scripts/run_demo.py
```

完成：

```text
读取文化知识图谱
↓
运行 MediaCrawler 市场调研
↓
生成 Culture DNA + Trend DNA
↓
调用 GPT Researcher 策划
↓
生成最终 Pre-Design Strategy Brief
```

如果 Live 模式失败：

```text
自动 fallback Demo Cache
```

---

# 二十九、配置

创建：

```text
.env.example
```

至少：

```text
LIVE_MODE=
DEMO_MODE=

LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=

EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=
EMBEDDING_MODEL=

GPT_RESEARCHER_PATH=
MEDIACRAWLER_PATH=
LIGHTRAG_PATH=
LIGHTRAG_BASE_URL=
```

不要提交真实 Key。

---

# 三十、验收标准

只检查：

- [ ] 找到 GPT Researcher
- [ ] 找到 MediaCrawler
- [ ] 找到 LightRAG
- [ ] LightRAG 能返回 Culture DNA
- [ ] MediaCrawler 能返回 Trend DNA 或 fallback
- [ ] GPT Researcher 能同时读取 Culture DNA + Trend DNA + Benchmark Cases
- [ ] GPT Researcher 能形成至少 8 个 Opportunity Signals
- [ ] GPT Researcher 能形成完整 Pre-Design Strategy Brief
- [ ] 能生成 Designer Handoff
- [ ] 贵州苗绣 Demo 一条命令跑通

除此之外不要增加复杂架构。

---

# 三十一、现在直接执行

请按顺序：

```text
1. 扫描当前目录
2. 找到三个第三方项目
3. 创建极简 app/ 目录
4. 完成三个 Adapter
5. 接通 LightRAG 文化知识查询
6. 接通 MediaCrawler 市场调研
7. 把 GPT Researcher 改造成策划师入口
8. 建立 Demo Cache
9. 用贵州苗绣跑完整流程
10. 生成最终 JSON + Markdown
11. 修复所有阻塞 Demo 的错误
```

不要只给方案。

直接修改项目并运行测试。

遇到 API Key、Cookie 等暂时缺失项时：

```text
先完成所有可完成代码
+
使用 Demo Cache
+
最后明确告诉我还需要补什么
```

最终只汇报：

```text
1. LightRAG 文化知识库是否跑通
2. MediaCrawler 市场调研是否跑通
3. GPT Researcher 策划师是否跑通
4. 贵州苗绣 Demo 怎么运行
5. 输出文件在哪里
6. 还缺哪些 Key / Cookie
7. 下一阶段 Designer 读取哪个文件
```
