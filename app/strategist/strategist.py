from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from app.adapters.gpt_researcher_adapter import GPTResearcherAdapter
from app.adapters.lightrag_adapter import LightRAGAdapter
from app.config import Settings
from app.schemas import (
    BenchmarkCase,
    ComponentStatus,
    CultureDNA,
    DemoRequest,
    DesignerHandoff,
    OpportunitySignal,
    PreDesignStrategy,
    PriorityOpportunity,
    TrendDNA,
    VisualReferencePack,
)


def _ordered_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        clean = str(value).strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


class Strategist:
    """The only synthesis agent in QianCraft.

    The LLM may propose hypotheses, but it cannot replace the curated Culture DNA,
    Trend DNA, benchmark records, or their source identifiers.
    """

    def __init__(self, settings: Settings, culture_adapter: LightRAGAdapter):
        self.settings = settings
        self.culture_adapter = culture_adapter
        self.runtime = GPTResearcherAdapter(settings)
        self.prompt = (Path(__file__).with_name("prompt.md")).read_text(encoding="utf-8")

    async def create_strategy(
        self,
        request: DemoRequest,
        culture_dna: CultureDNA,
        trend_dna: TrendDNA,
        benchmarks: list[BenchmarkCase],
        visual_pack: VisualReferencePack,
    ) -> tuple[PreDesignStrategy, ComponentStatus]:
        baseline = _baseline_opportunities(request)
        generated: dict[str, Any] = {}
        runtime_metadata: dict[str, Any] = {
            "engine": "QianCraft evidence-locked strategy baseline",
            "model": "none",
        }
        status = ComponentStatus(
            component="strategist",
            mode="cache",
            engine=runtime_metadata["engine"],
            ok=True,
            detail="离线证据规则生成 8 条跨域机会；没有把缓存标记为实时模型结果。",
        )

        if self.settings.live_mode:
            context = {
                "project": request.model_dump(),
                "culture_dna": culture_dna.model_dump(mode="json"),
                "trend_dna": trend_dna.model_dump(mode="json"),
                "benchmark_cases": [case.model_dump(mode="json") for case in benchmarks],
            }
            try:
                generated, runtime_metadata = await self.runtime.generate(
                    query=f"{request.topic}：{request.goal}",
                    context=context,
                    prompt=self.prompt,
                )
                status = ComponentStatus(
                    component="strategist",
                    mode="live",
                    engine=str(runtime_metadata.get("engine", "GPT Researcher")),
                    ok=True,
                    detail=(
                        f"已调用 {runtime_metadata.get('model', self.settings.llm_model)}；"
                        "生成建议经过证据编号白名单和 Pydantic 契约校验。"
                    ),
                )
            except Exception as exc:
                if not self.settings.demo_mode:
                    raise
                runtime_metadata = {
                    "engine": "QianCraft evidence-locked strategy baseline",
                    "model": "none",
                    "fallback_reason": _safe_error(exc),
                }
                status.detail = f"策划运行时不可用，使用证据规则基线：{_safe_error(exc)}"

        allowed_refs = _allowed_evidence_refs(culture_dna, trend_dna, benchmarks)
        opportunities, generated_accepted = _validated_opportunities(
            generated, allowed_refs, baseline
        )
        _score_opportunities(opportunities, trend_dna)
        verification_map = await self.culture_adapter.verify_opportunities(opportunities)
        for opportunity in opportunities:
            opportunity.verification = verification_map[opportunity.opportunity_id]
            if opportunity.verification.status == "rejected":
                opportunity.overall_score = 0
                opportunity.reason += "；文化二次核验拒绝，不能进入设计交接。"
            elif opportunity.verification.status == "warning":
                opportunity.overall_score = round(max(0, opportunity.overall_score - 5), 1)
                opportunity.reason += "；文化二次核验有警告，综合分扣5分。"
        opportunities.sort(key=_opportunity_rank_key, reverse=True)
        priority = [
            opportunity
            for opportunity in opportunities
            if opportunity.verification.status != "rejected"
        ][:3]
        if len(priority) != 3:
            raise ValueError("通过文化证据门槛的机会不足3条，不能生成 Designer Handoff")

        recommendations = _ordered_unique(
            [
                *_string_list(generated.get("recommended_product_categories")),
                "可替换绣片的随身挂饰与科技生活配件",
                "可把玩、可集齐的小型互动收藏品",
                "真实绣线与软性材料结合的触感生活品",
                "带工艺溯源的首饰、包袋与穿戴配件",
                "支系学习卡与非仪式纹样共创体验套件",
            ]
        )[:8]
        design_keywords = _ordered_unique(
            [
                *_string_list(generated.get("design_keywords")),
                "支系可辨",
                "真实触感",
                "模块化",
                "可追溯",
                "日常高频",
                "共创署名",
                "可维修升级",
                "系列收藏",
            ]
        )[:16]

        handoff_notes = generated.get("handoff_notes")
        if not isinstance(handoff_notes, dict):
            handoff_notes = {}
        boundary = culture_dna.cultural_boundary
        must_keep = _ordered_unique(
            [
                *boundary.get("must_keep", []),
                *_string_list(handoff_notes.get("must_keep")),
                "任何产品叙事都同时标注贵州具体地域、苗族支系、针法和材料来源",
                "真实手工、机器生产和授权衍生必须明确区分",
            ]
        )
        can_modernize = _ordered_unique(
            [*culture_dna.modernizable_elements, *_string_list(handoff_notes.get("can_modernize"))]
        )
        avoid = _ordered_unique(
            [
                *culture_dna.non_transferable_elements,
                *boundary.get("avoid", []),
                *_string_list(handoff_notes.get("avoid")),
                "把多地、多支系纹样混称为一种抽象的‘苗绣风’",
                "未经许可复制传承人完整作品，或声称并不存在的传承人联名",
            ]
        )
        constraints = _ordered_unique(
            [
                *_string_list(generated.get("cultural_constraints")),
                *must_keep,
                *boundary.get("review_required", []),
                *avoid,
            ]
        )

        evidence_summary = _evidence_summary(generated, culture_dna, trend_dna)
        source_ids = sorted(allowed_refs | set(visual_pack.source_refs))
        creative_brief = _creative_brief(request, priority)
        handoff = DesignerHandoff(
            ready=True,
            project={
                **request.model_dump(),
                "stage": "designer_handoff",
                "next_stage": "concept_visual_and_prototype_brief",
                "stop_before": "production_release",
            },
            design_mission={
                "objective": (
                    "把通过文化与市场证据门槛的机会交给QianCraft Design Agent，"
                    "形成可展示概念视觉与工厂首样/报价输入。"
                ),
                "audience": request.target_market,
                "success_criteria": [
                    "具体地域和支系可辨",
                    "产品关系可被用户理解",
                    "材料与工艺声明真实",
                    "保留社区复核与后续共创空间",
                ],
            },
            culture_context={
                "culture_name": culture_dna.culture_name,
                "regions": culture_dna.region,
                "branch_differences": culture_dna.branch_differences,
                "visual_dna": culture_dna.visual_dna,
                "semantic_dna": culture_dna.semantic_dna,
                "review_required": boundary.get("review_required", []),
            },
            market_context={
                "source_status": trend_dna.retrieval.get("market_source", {}),
                "platform_statuses": trend_dna.retrieval.get("market_platforms", {}),
                "hot_product_forms": [
                    item.model_dump(mode="json") for item in trend_dna.hot_product_forms
                ],
                "priority_product_forms": trend_dna.priority_product_forms,
                "hot_categories": trend_dna.hot_categories,
                "rising_categories": trend_dna.rising_categories,
                "viral_mechanisms": trend_dna.viral_mechanisms,
                "white_space_opportunities": trend_dna.white_space_opportunities,
                "evidence_model": {
                    "types": [
                        "social_signal",
                        "institutional_signal",
                        "media_signal",
                        "product_signal",
                    ],
                    "scores": [
                        "real_engagement_score",
                        "institutional_signal_score",
                        "derived_viral_score",
                    ],
                },
            },
            priority_opportunities=[
                _to_priority(index, item) for index, item in enumerate(priority, 1)
            ],
            visual_reference_pack=visual_pack,
            hard_constraints=_ordered_unique([*must_keep, *avoid]),
            soft_direction=_ordered_unique([*can_modernize, *design_keywords])[:24],
            creative_brief=creative_brief,
            output_requirements={
                "next_owner": "QianCraft Design Agent",
                "input_file": "data/outputs/designer_handoff.json",
                "deliverables": [
                    "从Top 3中选择一个已核验且文化风险可控的首版方向",
                    "输出文化元素、风格、成品主视觉与原创图案转译规则",
                    "输出BOM、首样尺寸、公差、装配、QC、安全与工厂开放问题",
                    "输出艺术海报和机器可读设计规格，并公开文化/工程审核门",
                ],
                "prohibited": [
                    "直接复制馆藏完整纹样或服装",
                    "把首样尺寸冒充最终量产工程图或合规认证",
                    "把 reference_only 图片作为可商用素材",
                    "虚构授权、传承人联名、销量、互动量或标准色值",
                ],
            },
            evidence_refs=source_ids,
        )
        strategy = PreDesignStrategy(
            project={
                **request.model_dump(),
                "stage": "design_strategy_only",
                "stop_before": "final_product_design",
            },
            culture_dna=culture_dna,
            trend_dna=trend_dna,
            benchmark_cases=benchmarks,
            opportunity_signals=opportunities,
            recommended_product_categories=recommendations,
            design_keywords=design_keywords,
            cultural_constraints=constraints,
            evidence_summary=evidence_summary,
            handoff_to_designer=handoff,
            metadata={
                "strategist_runtime": runtime_metadata,
                "evidence_lock": True,
                "allowed_evidence_refs": source_ids,
                "generated_opportunities_accepted": generated_accepted,
                "opportunity_scoring": {
                    "weights": {
                        "culture_fit": 0.20,
                        "market_pull": 0.20,
                        "novelty": 0.20,
                        "visual_potential": 0.15,
                        "social_shareability": 0.15,
                        "product_feasibility": 0.10,
                        "cultural_risk_penalty": 0.20,
                    },
                    "ranked_opportunity_ids": [item.opportunity_id for item in opportunities],
                    "designer_top3_ids": [item.opportunity_id for item in priority],
                },
                "secondary_verification": {
                    "engine": "LightRAG adapter",
                    "candidate_count": sum(
                        item.verification.retrieval_mode != "candidate_gate"
                        for item in opportunities
                    ),
                    "status_counts": {
                        state: sum(
                            item.verification.status == state for item in opportunities
                        )
                        for state in ("verified", "warning", "rejected")
                    },
                },
                "final_design_generated": False,
            },
        )
        status.detail += (
            f" 已评分 {len(opportunities)} 条机会，LightRAG 二次核验高分候选，"
            "仅将通过门槛的 Top 3 交给设计阶段。"
        )
        return strategy, status


def _baseline_opportunities(request: DemoRequest) -> list[OpportunitySignal]:
    audience = [request.target_market]
    return [
        OpportunitySignal(
            culture_element="蝴蝶妈妈、枫木与祖源叙事",
            culture_meaning="关联生命起源、亲缘记忆与延续；属于高敏感叙事，不能只当装饰。",
            trend_element="日常高频随身挂饰与可替换模块",
            market_signal="手机壳、挂饰等高频科技生活配件已出现苗绣联动和日常化方向。",
            match_reason="可探索‘随身携带的家族记忆’这一关系，但图形、命名和使用语境须由对应社区核验。",
            potential_product_categories=["随身挂饰", "科技生活配件", "可替换穿戴模块"],
            target_audience=audience,
            design_keywords=["生命叙事", "陪伴", "模块化", "可追溯"],
            cultural_constraints=["祖源与神话释义必须由具体支系/社区核验", "不拆用祭祀或完整服饰语境中的受限图样"],
            evidence_refs=["C004", "C009", "M003"],
            confidence_score=82,
        ),
        OpportunitySignal(
            culture_element="鸟纹、蝶纹与动植物复合构图",
            culture_meaning="在苗绣叙事中可承载生命繁衍、自然关系与吉祥愿望，但不同地区释义并不相同。",
            trend_element="可互动、可把玩、可集齐的小型收藏形态",
            market_signal="博物馆文创持续出现互动冰箱贴、毛绒与爆款母题的跨品类延展。",
            match_reason="用动作、层次和系列关系讲清母题，而不是把纹样压成无出处的平面贴图。",
            potential_product_categories=["互动收藏品", "毛绒与绣片复合产品", "桌面小物"],
            target_audience=audience,
            design_keywords=["复合动植物", "立体层次", "可把玩", "系列叙事"],
            cultural_constraints=["每一母题绑定地域、支系与来源说明", "不得声称所有鸟蝶纹都有同一固定寓意"],
            evidence_refs=["C004", "C005", "M001", "M005"],
            confidence_score=90,
        ),
        OpportunitySignal(
            culture_element="花溪挑花的数纱、十字结构与反面挑绣",
            culture_meaning="以经纬计数形成秩序感，体现熟练技艺和地方辨识度。",
            trend_element="系列编号、成套收藏与轻量个性化",
            market_signal="限定、成对和跨馆收集正在强化小型文创的收藏动机。",
            match_reason="挑花的网格秩序适合探索可组合系统，让消费者识别技法而非只识别图案。",
            potential_product_categories=["可组合首饰", "文具与卡片系统", "包袋织物模块"],
            target_audience=audience,
            design_keywords=["数纱秩序", "几何", "双面", "可组合"],
            cultural_constraints=["明确标注花溪苗族挑花，不泛称贵州苗绣", "真实手工与数字化转译分开标识"],
            evidence_refs=["C001", "C005", "M007"],
            confidence_score=88,
        ),
        OpportunitySignal(
            culture_element="剑河锡绣的金属锡线与迷宫式几何纹",
            culture_meaning="材料与工艺共同构成清晰的地方身份，不应被简化成普通银色印花。",
            trend_element="金属感科技配件、反光细节与材料对比",
            market_signal="科技生活配件与非遗合作显示传统工艺进入高频数码场景的可能。",
            match_reason="可探索软织物与冷金属的材料张力，以及可维修替换的局部工艺模块。",
            potential_product_categories=["科技生活配件", "夜间反光穿戴", "小型首饰"],
            target_audience=audience,
            design_keywords=["锡线", "迷宫几何", "冷暖材质", "可维修"],
            cultural_constraints=["不能用银色塑料替代却宣称锡绣", "材料供应和工艺过程需与剑河社区共同确认"],
            evidence_refs=["C002", "C009", "M003"],
            confidence_score=86,
        ),
        OpportunitySignal(
            culture_element="松桃苗绣的针法体系与苗画叙事",
            culture_meaning="既是审美语言也是社区记忆和女性知识传承的载体。",
            trend_element="带作者信息、工时和故事卡的联名小批量产品",
            market_signal="松桃共创项目和品牌联动证明‘设计赋能 + 文化署名’比匿名挪用更可信。",
            match_reason="把传承关系、针法与设计贡献放入产品体验，为后续视觉方案保留多种形态。",
            potential_product_categories=["联名穿戴配件", "家居织物", "故事型礼赠"],
            target_audience=audience,
            design_keywords=["苗画", "针法档案", "共同署名", "小批量"],
            cultural_constraints=["不得复制具体传承人作品作为公共素材", "授权范围、署名与收益方式进入设计合同"],
            evidence_refs=["C003", "C008", "C009", "M003"],
            confidence_score=89,
        ),
        OpportunitySignal(
            culture_element="花溪、剑河、松桃、雷山等支系差异",
            culture_meaning="差异本身是知识，不是需要被抹平的风格噪声。",
            trend_element="可替换、可集齐并带学习线索的收藏系统",
            market_signal="系列化与跨地点收集机制已经成为文博文创的传播和复购抓手。",
            match_reason="把每一支系做成可持续扩展的独立单元，可同时支持收藏、教育和后续设计迭代。",
            potential_product_categories=["支系绣片收藏系统", "互动学习卡", "旅行收集物"],
            target_audience=audience,
            design_keywords=["一地一档", "可替换", "学习型收藏", "长期扩展"],
            cultural_constraints=["不混搭成虚构的统一苗绣纹样", "每个单元上线前由对应地区主体审核"],
            evidence_refs=["C001", "C002", "C003", "C005", "C006", "M007"],
            confidence_score=94,
        ),
        OpportunitySignal(
            culture_element="绣线、辫绣、破线绣等可触摸的工艺层次",
            culture_meaning="触感来自实际材料、针法与劳动时间，是文化价值的一部分。",
            trend_element="毛绒、软触感与真实刺绣结合的情绪陪伴产品",
            market_signal="贵州博物馆新品和青年消费研究均显示触感、萌化和情绪价值的产品潜力。",
            match_reason="将‘触摸才理解的技艺’作为体验起点，可在毛绒、家居或随身物之间继续探索。",
            potential_product_categories=["触感随身物", "毛绒与真绣复合产品", "软性家居"],
            target_audience=audience,
            design_keywords=["绣线触感", "针法层次", "陪伴", "耐用"],
            cultural_constraints=["只有实际使用对应工艺才可标注其名称", "避免用低质机器绣冒充传承人手作"],
            evidence_refs=["C003", "C006", "M001", "M008"],
            confidence_score=91,
        ),
        OpportunitySignal(
            culture_element="苗绣的女性传承网络、学习过程与可穿戴记忆",
            culture_meaning="价值不仅在成品纹样，也在社区关系、知识传递与劳动主体。",
            trend_element="可追溯体验套件、二维码档案与持续回访内容",
            market_signal="订单型非遗产业、体验消费和消费者对真实来源的关注，为过程型产品留下空间。",
            match_reason="可把一次购买转为对针法、作者和地域的持续学习，并验证更公平的价值分配。",
            potential_product_categories=["非仪式纹样体验套件", "溯源礼盒", "工艺学习订阅"],
            target_audience=audience,
            design_keywords=["过程可见", "作者可见", "工时可见", "持续学习"],
            cultural_constraints=["体验内容由社区选择可公开部分", "不收录秘密、祭祀或未经许可的知识", "建立明确收益回流机制"],
            evidence_refs=["C003", "C009", "C010", "M004"],
            confidence_score=87,
        ),
    ]


def _allowed_evidence_refs(
    culture_dna: CultureDNA,
    trend_dna: TrendDNA,
    benchmarks: list[BenchmarkCase],
) -> set[str]:
    refs = {source.source_id for source in culture_dna.source_refs}
    refs.update(source.source_id for source in trend_dna.source_refs)
    refs.update(ref for case in benchmarks for ref in case.source_refs)
    return {ref for ref in refs if ref.startswith(("C", "M"))}


def _validated_opportunities(
    generated: dict[str, Any],
    allowed_refs: set[str],
    baseline: list[OpportunitySignal],
) -> tuple[list[OpportunitySignal], int]:
    accepted: list[OpportunitySignal] = []
    raw_items = generated.get("opportunity_signals", [])
    if isinstance(raw_items, list):
        for raw in raw_items[:12]:
            if not isinstance(raw, dict):
                continue
            refs = [ref for ref in _string_list(raw.get("evidence_refs")) if ref in allowed_refs]
            if not any(ref.startswith("C") for ref in refs) or not any(
                ref.startswith("M") for ref in refs
            ):
                continue
            candidate = dict(raw)
            candidate["evidence_refs"] = refs
            try:
                accepted.append(OpportunitySignal.model_validate(candidate))
            except (TypeError, ValueError):
                continue

    generated_accepted = len(accepted)
    seen = {(item.culture_element, item.trend_element) for item in accepted}
    for item in baseline:
        key = (item.culture_element, item.trend_element)
        if key not in seen:
            accepted.append(item)
            seen.add(key)
        if len(accepted) >= 8:
            break
    return accepted[:12], min(generated_accepted, 12)


def _score_opportunities(
    opportunities: list[OpportunitySignal], trend_dna: TrendDNA
) -> None:
    market_scores: dict[str, float] = {
        post.source_ref: post.derived_viral_score
        for post in trend_dna.representative_cases
        if post.source_ref
    }
    interactive_terms = (
        "互动",
        "把玩",
        "可替换",
        "可集齐",
        "系列",
        "二维码",
        "随身",
        "触感",
    )
    novelty_terms = (
        "支系",
        "一地一档",
        "可维修",
        "可追溯",
        "真实绣线",
        "过程",
        "共创",
        "学习",
    )
    visual_terms = (
        "纹",
        "绣",
        "几何",
        "金属",
        "触感",
        "立体",
        "色",
        "材料",
        "针法",
    )
    sensitive_terms = ("祖源", "祖先", "蝴蝶妈妈", "鹡宇", "祭祀", "宗教", "完整服饰")

    for index, item in enumerate(opportunities, 1):
        item.opportunity_id = f"OPP-{index:03d}"
        text = " ".join(
            [
                item.culture_element,
                item.culture_meaning,
                item.trend_element,
                item.match_reason,
                *item.potential_product_categories,
                *item.design_keywords,
                *item.cultural_constraints,
            ]
        )
        culture_refs = {ref for ref in item.evidence_refs if ref.startswith("C")}
        market_refs = {ref for ref in item.evidence_refs if ref.startswith("M")}
        cited_market_scores = [market_scores.get(ref, 62.0) for ref in market_refs]

        item.culture_fit = _clamp(
            round(0.68 * item.confidence_score + 18 + 4 * min(len(culture_refs), 4))
        )
        item.market_pull = _clamp(
            round(
                (sum(cited_market_scores) / len(cited_market_scores))
                + 6 * min(len(market_refs), 3)
            )
            if cited_market_scores
            else 35
        )
        item.novelty = _clamp(
            56
            + 6 * sum(term in text for term in novelty_terms)
            + 3 * min(len(item.potential_product_categories), 3)
        )
        item.visual_potential = _clamp(
            52
            + 5 * sum(term in text for term in visual_terms)
            + 2 * min(len(item.design_keywords), 6)
        )
        item.social_shareability = _clamp(
            48
            + 7 * sum(term in text for term in interactive_terms)
            + 3 * min(len(item.potential_product_categories), 3)
        )
        complex_terms = ("科技", "手机壳", "金属", "订阅", "跨工艺")
        simple_terms = ("挂饰", "文具", "卡", "首饰", "绣片", "礼赠")
        item.product_feasibility = _clamp(
            72
            + 4 * sum(term in text for term in simple_terms)
            - 5 * sum(term in text for term in complex_terms)
        )

        region_count = sum(term in text for term in ("花溪", "剑河", "松桃", "雷山", "台江", "施秉"))
        risk = 12 + 12 * sum(term in text for term in sensitive_terms)
        if region_count > 1:
            risk += 10
        if any(term in text for term in ("核验", "社区", "不混", "不拆", "分开标识", "授权")):
            risk -= 14
        if len(item.cultural_constraints) >= 2:
            risk -= 5
        item.cultural_risk = _clamp(risk)

        weighted_positive = (
            0.20 * item.culture_fit
            + 0.20 * item.market_pull
            + 0.20 * item.novelty
            + 0.15 * item.visual_potential
            + 0.15 * item.social_shareability
            + 0.10 * item.product_feasibility
        )
        item.overall_score = round(
            max(0, min(100, weighted_positive - 0.20 * item.cultural_risk)), 1
        )
        item.reason = (
            f"文化契合{item.culture_fit}、市场拉力{item.market_pull}、新颖度{item.novelty}、"
            f"视觉潜力{item.visual_potential}、社交传播{item.social_shareability}、"
            f"产品可行性{item.product_feasibility}，按20/20/20/15/15/10加权后，"
            f"再扣除文化风险{item.cultural_risk}×20%。"
        )


def _clamp(value: int) -> int:
    return max(0, min(100, int(value)))


def _opportunity_rank_key(item: OpportunitySignal) -> tuple[float, int, int]:
    evidence_completeness = sum(ref.startswith("C") for ref in item.evidence_refs) + sum(
        ref.startswith("M") for ref in item.evidence_refs
    )
    return (item.overall_score, evidence_completeness, -item.cultural_risk)


def _to_priority(rank: int, item: OpportunitySignal) -> PriorityOpportunity:
    return PriorityOpportunity(
        rank=rank,
        opportunity_id=item.opportunity_id,
        title=f"{item.culture_element} × {item.trend_element}",
        culture_element=item.culture_element,
        trend_element=item.trend_element,
        why_now=item.match_reason,
        potential_product_categories=item.potential_product_categories,
        design_keywords=item.design_keywords,
        cultural_constraints=item.cultural_constraints,
        score_breakdown={
            "culture_fit": item.culture_fit,
            "market_pull": item.market_pull,
            "novelty": item.novelty,
            "visual_potential": item.visual_potential,
            "social_shareability": item.social_shareability,
            "product_feasibility": item.product_feasibility,
            "cultural_risk": item.cultural_risk,
        },
        overall_score=item.overall_score,
        verification=item.verification,
        evidence_refs=item.evidence_refs,
    )


def _creative_brief(
    request: DemoRequest, priority: list[OpportunitySignal]
) -> str:
    names = "、".join(item.culture_element for item in priority)
    return (
        f"面向{request.target_market}，围绕{names}三个已通过证据门槛的方向，探索一组能进入日常高频场景、"
        "又能让地域与支系差异被看见的贵州苗绣概念。视觉上从数纱秩序、真实绣线触感、金属与织物层次、"
        "可替换和可收集关系出发，不直接复制馆藏完整纹样，也不先锁定造型、尺寸或SKU。每个方向须同时说明"
        "文化出处、市场假设、材料真实性、互动逻辑及待社区复核点；所有参考图仅用于研究。下一步以多方案草图"
        "和低保真材料实验比较用户理解度、制作可行性与合作边界，为后续共同设计保留充分选择空间。"
    )


def _evidence_summary(
    generated: dict[str, Any], culture_dna: CultureDNA, trend_dna: TrendDNA
) -> dict[str, Any]:
    raw = generated.get("evidence_summary")
    if not isinstance(raw, dict):
        raw = {}
    return {
        "strong_evidence": _ordered_unique(
            [
                *_string_list(raw.get("strong_evidence")),
                f"文化图谱命中 {culture_dna.retrieval.get('records_matched', 0)} 条贵州苗绣及支系记录。",
                f"市场层汇总 {trend_dna.sample_size} 条公开可追溯信号；无披露的社交互动量保持为0。",
                "多个独立来源共同指向互动小物、高频随身配件、真实触感和系列收藏。",
            ]
        ),
        "inferences": _ordered_unique(
            [
                *_string_list(raw.get("inferences")),
                "‘支系可辨的可替换系统’是跨文化证据与市场信号形成的策划推断，并非现成销量结论。",
                "建议优先做概念访谈和材料样，而不是直接扩成SKU。",
            ]
        ),
        "unknowns_to_validate": _ordered_unique(
            [
                *_string_list(raw.get("unknowns_to_validate")),
                "哪一支系和合作社区愿意公开哪些纹样、故事与工艺步骤？",
                "真实绣片在耐磨、清洁、维修和数码配件热环境中的表现如何？",
                "目标用户对‘真手作限量’与‘授权机器转译’的价格接受区间分别是多少？",
                "署名、授权、收益回流和后续迭代的共同治理机制如何落地？",
            ]
        ),
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _safe_error(exc: Exception) -> str:
    import re

    message = re.sub(r"sk-[A-Za-z0-9_-]+", "<redacted>", str(exc))
    return f"{type(exc).__name__}: {message[:800]}"
