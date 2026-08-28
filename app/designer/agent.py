from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from app.config import Settings
from app.schemas import (
    ComponentStatus,
    CulturalElementSpec,
    DesignerHandoff,
    DesignInputContract,
    DesignPackage,
    DesignSelection,
    DesignValidation,
    ManufacturingBrief,
    MaterialLineItem,
    PatternApplicationSpec,
    PosterRenderRequest,
    PriorityOpportunity,
    ProductDesignSpec,
    PrototypeDimension,
)

CONCRETE_PRODUCT_TERMS = (
    "毛绒",
    "玩偶",
    "挂饰",
    "包挂",
    "冰箱贴",
    "徽章",
    "织品",
    "礼盒",
    "收藏",
    "绣片",
    "配件",
    "首饰",
)
SENSITIVE_AUTODESIGN_TERMS = ("鸟纹", "蝶纹", "蝴蝶", "苗龙", "祖源", "祭祀", "丧葬")


def _ordered_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        clean = str(value).strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DesignAgent:
    """Turn the file-level DesignerHandoff contract into one prototype design package."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.prompt = (Path(__file__).with_name("prompt.md")).read_text(encoding="utf-8")

    def create_from_file(self, handoff_path: Path) -> tuple[DesignPackage, ComponentStatus]:
        resolved = handoff_path.resolve()
        handoff = DesignerHandoff.model_validate_json(resolved.read_text(encoding="utf-8"))
        if not handoff.ready:
            raise ValueError("DesignerHandoff is not ready")

        primary = max(handoff.priority_opportunities, key=self._selection_score)
        supporting = self._supporting_opportunity(handoff, primary.opportunity_id)
        if self._is_plush_direction(primary):
            package = self._plush_package(handoff, resolved, primary, supporting)
        elif self._is_magnet_direction(primary):
            package = self._magnet_package(handoff, resolved, primary, supporting)
        else:
            package = self._provenance_package(handoff, resolved, primary, supporting)

        return package, ComponentStatus(
            component="design_agent",
            mode="live",
            engine="QianCraft evidence-locked deterministic designer",
            ok=True,
            detail=(
                f"已从 {resolved.name} 选择 {primary.opportunity_id}，生成概念视觉、"
                "工厂首样拆解和海报渲染请求；未使用 reference_only 图像像素。"
            ),
        )

    @staticmethod
    def _selection_score(opportunity: PriorityOpportunity) -> tuple[int, int, int, float]:
        verification = opportunity.verification.status
        categories = " ".join(opportunity.potential_product_categories)
        concrete = sum(term in categories for term in CONCRETE_PRODUCT_TERMS)
        sensitive = sum(term in opportunity.title for term in SENSITIVE_AUTODESIGN_TERMS)
        return (
            100 if verification == "verified" else 0,
            -sensitive,
            concrete,
            float(opportunity.overall_score),
        )

    @staticmethod
    def _supporting_opportunity(handoff: DesignerHandoff, primary_id: str):
        others = [
            item
            for item in handoff.priority_opportunities
            if item.opportunity_id != primary_id and item.verification.status == "verified"
        ]
        if not others:
            return None
        provenance_terms = ("溯源", "署名", "工时", "社区", "包装")
        scored = [
            (
                sum(
                    term in f"{item.title} {' '.join(item.design_keywords)}"
                    for term in provenance_terms
                ),
                item.overall_score,
                item,
            )
            for item in others
        ]
        best = max(
            scored,
            key=lambda candidate: (candidate[0], candidate[1]),
        )
        if best[0] == 0:
            return None
        return best[2]

    @staticmethod
    def _is_plush_direction(opportunity: PriorityOpportunity) -> bool:
        text = " ".join(opportunity.potential_product_categories)
        return any(term in text for term in ("毛绒", "玩偶", "织品"))

    @staticmethod
    def _is_magnet_direction(opportunity: PriorityOpportunity) -> bool:
        text = " ".join(opportunity.potential_product_categories)
        return any(term in text for term in ("冰箱贴", "徽章", "包挂", "收藏", "绣片"))

    def _base_contract(self, handoff: DesignerHandoff, path: Path) -> DesignInputContract:
        return DesignInputContract(
            source_file=str(path),
            source_sha256=_sha256(path),
            ready=handoff.ready,
            input_stage=str(handoff.project.get("stage", "designer_handoff")),
            selected_opportunity_ids=[
                item.opportunity_id for item in handoff.priority_opportunities
            ],
        )

    @staticmethod
    def _selection(
        handoff: DesignerHandoff,
        primary: PriorityOpportunity,
        supporting: PriorityOpportunity | None,
    ) -> DesignSelection:
        held: dict[str, str] = {}
        for item in handoff.priority_opportunities:
            if item.opportunity_id == primary.opportunity_id:
                continue
            if supporting is not None and item.opportunity_id == supporting.opportunity_id:
                continue
            if any(term in item.title for term in SENSITIVE_AUTODESIGN_TERMS):
                reason = "包含高敏感动植物或祖源母题，须先完成对应社区核验。"
            elif item.verification.status == "verified":
                reason = "保留为后续变体；当前海报只呈现一个可验证主方向。"
            else:
                reason = "存在文化核验警告，未直接进入首版成品视觉。"
            held[item.opportunity_id] = reason
        return DesignSelection(
            primary_opportunity_id=primary.opportunity_id,
            primary_verification=primary.verification.status,
            supporting_opportunity_ids=(
                [supporting.opportunity_id] if supporting is not None else []
            ),
            selection_reason=[
                "主机会已通过文化二次核验。",
                "产品关系具体，能够同时验证成品形象、材料层次和拆解结构。",
                "首版只做单一地域/工艺方向，避免把多支系混成抽象苗绣风。",
            ],
            held_back_opportunities=held,
        )

    @staticmethod
    def _evidence(
        primary: PriorityOpportunity,
        supporting: PriorityOpportunity | None,
        handoff: DesignerHandoff,
    ) -> list[str]:
        candidate = [*primary.evidence_refs]
        if supporting is not None:
            candidate.extend(supporting.evidence_refs)
        candidate.extend(["C029"])
        allowed = set(handoff.evidence_refs)
        return _ordered_unique(ref for ref in candidate if ref in allowed)

    def _plush_package(
        self,
        handoff: DesignerHandoff,
        path: Path,
        primary: PriorityOpportunity,
        supporting: PriorityOpportunity | None,
    ) -> DesignPackage:
        evidence = self._evidence(primary, supporting, handoff)
        generated_at = datetime.now(UTC)
        design_id = f"QD-{_sha256(path)[:8].upper()}-PLUSH-01"
        cultural_elements = [
            CulturalElementSpec(
                element_id="CE-01",
                name="针脚浮层与软硬对比",
                region="贵州省雷山县（首版地域范围）",
                branch_or_community="雷山苗绣；具体合作社区待确认",
                visual_role="以平整织物、凸起绣线和边缘拼接形成触觉层次",
                transformation_rule=(
                    "只转译针脚方向、厚薄和层次关系，重新绘制非叙事几何单元；"
                    "不抽取完整传统纹样。"
                ),
                source_primitives=["P005"],
                reference_visual_ids=["V009", "V012"],
                rights_rule=(
                    "V009/V012 均为 reference_only；只读取书面结构描述，"
                    "不下载、不描摹、不作为生成图像输入。"
                ),
                do_not_copy=[
                    "完整盛装构图、银饰组合或馆藏纹样",
                    "祖源、祭祀、丧葬与支系身份性图式",
                    "具体传承人的作品、姓名或未经授权联名",
                ],
                evidence_refs=[ref for ref in evidence if ref.startswith("C")],
            )
        ]
        product = ProductDesignSpec(
            product_name="针层绒伴｜雷山苗绣触感挂偶（概念样）",
            product_type="毛绒包挂 / 刺绣触感玩偶",
            target_audience=str(handoff.design_mission.get("audience", "18-30岁")),
            use_scenarios=["通勤包挂", "旅行纪念", "桌面触感陪伴", "文化礼赠"],
            concept_statement=(
                "用一个原创、非图腾化的柔软轮廓承载可触摸的三层针脚面板，"
                "让用户通过摸、看、拆换理解雷山苗绣的线材层次；溯源卡明确"
                "地域、设计参与者、实际工艺和工时。"
            ),
            form_description=(
                "圆角椭圆主身体、顶部织带挂环、正面可替换刺绣触感片；"
                "不采用人物、神兽或完整传统服饰轮廓。"
            ),
            interaction=["触摸三种针脚高度", "拆换正面绣片", "扫描溯源卡查看工艺说明"],
            visual_style=["当代织物雕塑", "克制几何", "针脚层叠", "柔软与金属小比例对比"],
            color_direction=[
                "展示用深靛色主体；不是传统标准色",
                "红、白线作层次提示；量产色须由实物线卡与社区共同确认",
                "五金采用低反光深色，避免模拟苗银或锡绣",
            ],
            dimensions=[
                PrototypeDimension(item="成品高度（不含挂扣）", value_mm=135, tolerance_mm=3),
                PrototypeDimension(item="成品宽度", value_mm=90, tolerance_mm=3),
                PrototypeDimension(item="填充后厚度", value_mm=42, tolerance_mm=5),
                PrototypeDimension(item="可替换绣片高度", value_mm=68, tolerance_mm=1),
                PrototypeDimension(item="可替换绣片宽度", value_mm=58, tolerance_mm=1),
            ],
            target_weight_g="48±8 g（首样目标，含挂扣）",
            claims=[
                "首版为原创结构转译，不是传统纹样复刻。",
                "默认量产工艺标注为机器刺绣；只有真实手绣并经授权时才能另行声明。",
            ],
        )
        manufacturing = _plush_manufacturing(evidence)
        poster_request = _plush_poster_request(design_id)
        return DesignPackage(
            design_id=design_id,
            generated_at=generated_at,
            input_contract=self._base_contract(handoff, path),
            selection=self._selection(handoff, primary, supporting),
            cultural_elements=cultural_elements,
            product=product,
            manufacturing=manufacturing,
            poster_request=poster_request,
            cultural_review_gates=[
                "由雷山具体合作社区/保护单位确认针脚层次转译是否可公开商品化。",
                "共同确认地域、支系、针法与参与者署名，不以泛化‘苗绣风’命名。",
                "共同确认收益、返修、后续图案迭代和撤回机制。",
                "任何手绣版本须单独取得绣娘授权并记录实际工时。",
            ],
            engineering_review_gates=[
                "工厂按首样确认纸样、缝份、填充量、五金拉力和绣片拆装寿命。",
                "根据最终销售年龄与地区确定适用的玩具/纺织品/小部件标准。",
                "完成色牢度、耐摩擦、缝口强度、锐边和有害物质检测后再定量产。",
            ],
            evidence_refs=evidence,
            validation=DesignValidation(
                checks=[
                    "主机会来自 DesignerHandoff 且 verification=verified。",
                    "文化与市场证据编号均在输入白名单内。",
                    "馆藏参考图未作为像素、描摹底图或风格输入。",
                    "材料、尺寸和公差均标为首样目标，不宣称量产定稿。",
                    "机器刺绣与传统手工苗绣声明被明确区分。",
                ]
            ),
        )

    def _magnet_package(
        self,
        handoff: DesignerHandoff,
        path: Path,
        primary: PriorityOpportunity,
        supporting: PriorityOpportunity | None,
    ) -> DesignPackage:
        # A safe fallback for future handoffs: narrow a multi-branch opportunity to one
        # original counted-grid pilot rather than mixing branch-specific motifs.
        evidence = self._evidence(primary, supporting, handoff)
        design_id = f"QD-{_sha256(path)[:8].upper()}-MAGNET-01"
        product = ProductDesignSpec(
            product_name="针格模块｜花溪挑花互动冰箱贴（概念样）",
            product_type="可替换织物面板冰箱贴",
            target_audience=str(handoff.design_mission.get("audience", "18-30岁")),
            use_scenarios=["家居陈列", "系列收藏", "旅行礼赠"],
            concept_statement="以原创数纱网格模块展示针脚秩序，面板可拆换并连接溯源卡。",
            form_description="圆角方形框体、可拆织物面板和背部封闭磁体。",
            interaction=["更换织物面板", "系列编号", "溯源阅读"],
            visual_style=["模块化", "像素化", "清晰网格", "克制强对比"],
            color_direction=["深色中性框体", "原型彩线关系待实物线卡确认"],
            dimensions=[
                PrototypeDimension(item="框体高度", value_mm=76, tolerance_mm=1),
                PrototypeDimension(item="框体宽度", value_mm=76, tolerance_mm=1),
                PrototypeDimension(item="框体厚度", value_mm=8, tolerance_mm=0.5),
                PrototypeDimension(item="可替换织物面板高度", value_mm=58, tolerance_mm=1),
                PrototypeDimension(item="可替换织物面板宽度", value_mm=58, tolerance_mm=1),
            ],
            target_weight_g="55±10 g（首样目标）",
            claims=["只转译数纱结构，不复制完整馆藏纹样。"],
        )
        pattern_evidence = [ref for ref in evidence if ref in {"C001", "C029"}]
        manufacturing = _magnet_manufacturing(pattern_evidence)
        return DesignPackage(
            design_id=design_id,
            generated_at=datetime.now(UTC),
            input_contract=self._base_contract(handoff, path),
            selection=self._selection(handoff, primary, supporting),
            cultural_elements=[
                CulturalElementSpec(
                    element_id="CE-01",
                    name="数纱十字网格",
                    region="贵州省贵阳市花溪区（首版地域范围）",
                    branch_or_community="花溪挑花；具体合作社区待确认",
                    visual_role="作为模块尺寸、针脚方向和重复秩序",
                    transformation_rule="重新设计原创网格单元，不复制完整馆藏纹样。",
                    source_primitives=["P001"],
                    reference_visual_ids=["V001"],
                    rights_rule="V001 为 reference_only，不作为生成图像输入。",
                    do_not_copy=["完整背扇花块", "其他地域专属工艺或纹样"],
                    evidence_refs=pattern_evidence,
                )
            ],
            product=product,
            manufacturing=manufacturing,
            poster_request=_magnet_poster_request(design_id),
            cultural_review_gates=[
                "由花溪具体合作社区/保护单位确认原创数纱网格转译可公开商品化。",
                "共同确认花溪地域、挑花工艺、机器刺绣组成和参与者署名。",
                "共同确定收益、后续面板迭代、返修与撤回机制。",
            ],
            engineering_review_gates=[
                "确认磁体等级、封闭结构、吸附力、跌落和儿童小部件风险。",
                "验证框体卡合、面板拆装循环、绣线耐磨和背板平整度。",
                "根据最终销售年龄与地区确定材料、标签与适用合规测试。",
            ],
            evidence_refs=evidence,
            validation=DesignValidation(
                checks=[
                    "将多支系机会缩窄到花溪单一原型。",
                    "没有使用 reference_only 图像像素。",
                    "首样尺寸不等于量产定稿。",
                ]
            ),
        )

    def _provenance_package(
        self,
        handoff: DesignerHandoff,
        path: Path,
        primary: PriorityOpportunity,
        supporting: PriorityOpportunity | None,
    ) -> DesignPackage:
        # Last-resort generic template keeps the interface working without inventing a motif.
        evidence = self._evidence(primary, supporting, handoff)
        design_id = f"QD-{_sha256(path)[:8].upper()}-KIT-01"
        product = ProductDesignSpec(
            product_name="共作档案｜贵州苗绣材料体验套件（概念样）",
            product_type="材料卡 / 溯源档案套件",
            target_audience=str(handoff.design_mission.get("audience", "18-30岁")),
            use_scenarios=["文化教育", "礼赠", "共创工作坊"],
            concept_statement="不使用传统图案，只展示经授权的材料、针法名称和共作记录。",
            form_description="折页档案夹、可替换材料卡和二维码溯源页。",
            interaction=["翻阅", "触摸材料", "扫描溯源"],
            visual_style=["档案感", "材料优先", "留白"],
            color_direction=["无传统标准色声明；纸张与实物材料原色为主"],
            dimensions=[
                PrototypeDimension(item="折页高度", value_mm=210, tolerance_mm=1),
                PrototypeDimension(item="折页宽度", value_mm=148, tolerance_mm=1),
                PrototypeDimension(item="闭合厚度", value_mm=12, tolerance_mm=2),
            ],
            target_weight_g="180±30 g（首样目标）",
            claims=["所有姓名、材料与工时均须来自真实授权记录。"],
        )
        manufacturing = _kit_manufacturing(evidence)
        return DesignPackage(
            design_id=design_id,
            generated_at=datetime.now(UTC),
            input_contract=self._base_contract(handoff, path),
            selection=self._selection(handoff, primary, supporting),
            cultural_elements=[
                CulturalElementSpec(
                    element_id="CE-01",
                    name="材料与工艺档案关系",
                    region="贵州；具体合作点待确认",
                    branch_or_community="不作泛化支系声明",
                    visual_role="信息层级与材料触感",
                    transformation_rule="不使用传统纹样，仅呈现经授权事实。",
                    rights_rule="不使用 reference_only 图像。",
                    do_not_copy=["馆藏图像", "传承人作品"],
                    evidence_refs=[ref for ref in evidence if ref.startswith("C")],
                )
            ],
            product=product,
            manufacturing=manufacturing,
            poster_request=_kit_poster_request(design_id),
            cultural_review_gates=["确认合作主体、署名、材料公开范围和收益机制。"],
            engineering_review_gates=["确认纸材、装订、耐折和二维码可读性。"],
            evidence_refs=evidence,
            validation=DesignValidation(
                checks=["未虚构图案、授权或标准色。", "首样参数需工厂确认。"]
            ),
        )


def _material(
    part_id: str,
    component: str,
    material: str,
    specification: str,
    color_finish: str,
    quantity: str,
    process: str,
    assembly: str,
    target: str,
    qc: str,
) -> MaterialLineItem:
    return MaterialLineItem(
        part_id=part_id,
        component=component,
        material=material,
        specification=specification,
        color_finish=color_finish,
        quantity=quantity,
        process=process,
        assembly=assembly,
        tolerance_or_target=target,
        qc_check=qc,
    )


def _plush_manufacturing(evidence: list[str]) -> ManufacturingBrief:
    bom = [
        _material("A01", "前片", "短毛绒布", "涤纶；克重与绒高由工厂打样确认", "展示用深靛近似色", "1片", "刀模裁片", "与后片车缝", "外轮廓±2 mm", "无破洞、色差与异常掉毛"),
        _material("A02", "后片", "短毛绒布", "同A01", "同A01", "1片", "刀模裁片", "与前片车缝并留返口", "外轮廓±2 mm", "经纬方向一致"),
        _material("A03", "可替换绣片基底", "棉质斜纹布", "约200 g/m²；实样确认缩水率", "深色中性底", "1片", "圆角裁片+包边", "隐藏按扣/软质钩面固定", "58×68 mm；±1 mm", "拆装20次后不起毛、不明显变形"),
        _material("A04", "原创针层图案", "粘胶或涤纶绣线", "三种线迹高度；实际线号随设备确认", "红/白提示线；非标准传统色", "1组", "机器刺绣", "绣于A03", "套位±1 mm", "无线头、跳针、断线；工艺标注真实"),
        _material("A05", "填充", "再生涤纶纤维或合规替代物", "回弹与阻燃要求按销售地确认", "本色", "12±2 g", "称重填充", "返口填充后藏针缝合", "成品厚度42±5 mm", "无硬块、异物与明显空洞"),
        _material("A06", "挂环", "10 mm尼龙织带", "有效折叠长度约45 mm", "深色低反光", "1条", "热切/防散边", "夹入顶缝并回针", "外露22±2 mm", "拉力目标由工厂按用途验证"),
        _material("A07", "旋转挂扣", "锌合金或不锈钢", "总长约38 mm；无尖锐边", "深枪色低反光", "1件", "采购件", "穿入A06", "开合顺畅", "镀层、盐雾与过敏物质按销售地确认"),
        _material("A08", "溯源/洗护标", "织唛+可变数据纸卡", "标注地域、实际工艺、参与者、批次与护理", "高对比可读", "各1件", "织造/数字印刷", "织唛夹缝；纸卡随包装", "二维码≥15 mm", "信息与授权台账一致，扫码可读"),
    ]
    return ManufacturingBrief(
        bill_of_materials=bom,
        pattern_applications=[
            PatternApplicationSpec(
                pattern_id="PAT-01",
                name="原创针层格",
                originality_rule="从针脚高低、方向和边缘拼接关系重新构成，不含传统完整母题。",
                geometry=["中心低密网格", "中层折线短针", "外层离散凸起点"],
                placement="A03正面安全区内，四周保留5 mm包边净距",
                scale_and_repeat="单个原创单元约8–14 mm；不形成完整传统连续边饰",
                process="三道机器刺绣；先平针定位，再缎面线，最后局部凸起线迹",
                color_and_material="展示用红/白线与深色布；实物线卡共同确认后再编号",
                registration_tolerance="图案中心相对绣片中心±1 mm",
                cultural_boundary=[
                    "不得称为传统完整雷山纹样",
                    "不得使用蝴蝶妈妈、祖源、祭祀或完整服饰图式",
                    "若改为手绣，需重做授权、署名、工时与价格记录",
                ],
                evidence_refs=[ref for ref in evidence if ref.startswith("C")],
            )
        ],
        assembly_steps=[
            "确认纸样、缩水率与首样色卡，制作A01/A02/A03裁片。",
            "在A03完成原创针层格机器刺绣，检验套位和线迹后包边。",
            "把A06挂环夹入A01/A02顶缝；车缝外轮廓并保留返口。",
            "翻面、称重填充A05，整形后藏针闭合返口。",
            "安装不外露硬边的拆换结构，将A03固定到正面。",
            "装配A07，缝入A08织唛，配套溯源卡并记录样品批次。",
        ],
        qc_checks=[
            "成品外形135×90×42 mm目标范围及左右对称性。",
            "绣片中心、线迹高度、套位、跳针、线头和包边完整性。",
            "挂环、挂扣、缝口和拆换结构的拉力/循环测试方案由工厂提交。",
            "面料与绣线耐摩擦、汗渍/水洗色牢度按最终用途选标检测。",
            "小部件、锐边、异味、填充洁净度和受限物质按销售地法规检测。",
            "标签上的地域、工艺、材料、参与者与授权台账逐项一致。",
        ],
        packaging_direction=[
            "无塑或减塑纸套，露出触感面板，不印刷传统完整纹样。",
            "随附地域/工艺/参与者/机器或手工组成/护理/批次溯源卡。",
        ],
        safety_and_compliance=[
            "当前按14+文化配件概念管理；若面向儿童或按玩具销售，须另行完成适用标准评估与检测。",
            "五金、染料、胶黏剂和填充材料的适用法规由供应商与检测机构确认。",
        ],
        factory_open_questions=[
            "可替换绣片采用隐藏按扣、软质钩面还是其他结构，哪种最耐久且不刮手？",
            "目标成本、起订量、机器针数、线数和换色限制是多少？",
            "面料缩水率、掉毛、色牢度和五金镀层测试采用哪些适用标准？",
            "最终销售年龄、地区、包装法规与合规标签尚未确定。",
            "社区共创版本与纯机器刺绣版本是否分线生产、如何真实标注？",
        ],
    )


def _magnet_manufacturing(evidence: list[str]) -> ManufacturingBrief:
    bom = [
        _material("B01", "外框", "ABS或经工厂验证的替代材料", "圆角注塑框", "深色哑光", "1件", "注塑", "卡合B02", "76×76×8 mm", "无毛边、变形"),
        _material("B02", "织物面板", "棉质斜纹布", "原创数纱网格刺绣", "线卡待确认", "1件", "裁切+机器刺绣", "卡入B01", "58×58 mm", "套位与边缘完整"),
        _material("B03", "背板", "ABS", "封闭磁体", "同B01", "1件", "注塑", "与B01卡合/螺钉固定", "平面度待确认", "磁体不可外露"),
        _material("B04", "磁体", "烧结钕铁硼或合规替代物", "规格由吸附测试确定", "防腐镀层", "1件", "采购件", "封闭在B03", "吸附目标待测", "跌落后不得脱出"),
        _material("B05", "溯源标签", "合成纸", "批次与二维码", "高对比", "1件", "数字印刷", "贴于背板", "二维码≥15 mm", "扫码可读"),
    ]
    return ManufacturingBrief(
        bill_of_materials=bom,
        pattern_applications=[
            PatternApplicationSpec(
                pattern_id="PAT-01",
                name="原创数纱网格",
                originality_rule="只使用网格、镜像和平移规则，重新设计非传统单元。",
                geometry=["经纬网格", "十字针单元", "镜像重复"],
                placement="B02正面",
                scale_and_repeat="单元8–12 mm",
                process="机器刺绣首样",
                color_and_material="实物线卡待确认",
                registration_tolerance="±1 mm",
                cultural_boundary=["不复制V001完整图案", "不得与其他支系混标"],
                evidence_refs=[ref for ref in evidence if ref.startswith("C")],
            )
        ],
        assembly_steps=[
            "确认框体、背板和织物面板纸样，校核圆角、缝份与磁体封闭空间。",
            "注塑/机加工B01与B03首样，去毛边并检验卡合间隙和平面度。",
            "完成B02原创网格机器刺绣、裁切和包边，检验套位后装入框体。",
            "按安全方案把B04磁体完全封闭在B03内，不使用外露磁片。",
            "卡合或可逆固定B01/B03，验证面板可拆换且无锐边、夹手点。",
            "粘贴B05并录入批次、地域、实际工艺、参与者和护理信息。",
        ],
        qc_checks=[
            "框体76×76×8 mm与织物面板58×58 mm首样尺寸及圆角一致性。",
            "刺绣中心套位±1 mm、无线头/跳针，包边不露毛、不影响卡合。",
            "磁体完全封闭；跌落后不得移位、破壳或脱出。",
            "在目标冰箱门板与常见涂层钢板上记录吸附力和滑移表现。",
            "拆装循环次数、框体变形、面板磨损和背板刮擦由工厂提交方案。",
            "标签地域、工艺、材料、参与者和授权台账一致，二维码可读。",
        ],
        packaging_direction=[
            "纸质展示套突出可替换织物面板，不印刷完整传统纹样。",
            "随附花溪地域、机器/手工组成、设计参与者、批次和护理溯源卡。",
        ],
        safety_and_compliance=[
            "磁体和小部件风险须按最终销售年龄与地区验证；当前不按儿童玩具宣称。",
            "塑料、磁体镀层、油墨和胶黏剂的受限物质要求由供应商和检测机构确认。",
        ],
        factory_open_questions=[
            "外框采用ABS、再生ABS还是其他材料，模具结构、缩水率、MOQ和目标成本是多少？",
            "磁体等级、尺寸、封装方式与目标吸附力如何平衡重量和安全？",
            "织物面板采用卡扣、压框还是可逆胶层，拆装寿命目标是多少？",
            "机器针数、线数、换色限制、最小针距和包边方式是什么？",
            "最终销售年龄、地区、包装法规和测试标准尚未确定。",
        ],
    )


def _kit_manufacturing(evidence: list[str]) -> ManufacturingBrief:
    bom = [
        _material("C01", "折页外壳", "FSC或同等可追溯纸板", "约1.5 mm", "纸材原色", "1件", "裱糊模切", "折页", "210×148 mm", "耐折无爆边"),
        _material("C02", "内页", "无涂布纸", "约160 g/m²", "纸材原色", "8页", "数字印刷", "骑马钉/线装", "版心待确认", "文字可读"),
        _material("C03", "材料卡", "中性纸卡", "可替换插槽", "中性", "4张", "模切", "插入内袋", "90×55 mm", "边缘平整"),
        _material("C04", "材料样", "经授权的实际材料", "种类待合作方确认", "实物原色", "4份", "裁切锁边", "固定于C03", "小样尺寸待定", "来源一致"),
        _material("C05", "溯源标签", "可变数据贴纸", "批次二维码", "高对比", "1组", "数字印刷", "贴于内页", "二维码≥15 mm", "扫码可读"),
    ]
    return ManufacturingBrief(
        bill_of_materials=bom,
        pattern_applications=[
            PatternApplicationSpec(
                pattern_id="PAT-00",
                name="无传统纹样的信息网格",
                originality_rule="只使用通用排版网格。",
                geometry=["信息栏", "编号", "留白"],
                placement="封面与内页",
                scale_and_repeat="不适用",
                process="数字排版印刷",
                color_and_material="纸材原色",
                registration_tolerance="印刷厂标准待确认",
                cultural_boundary=["不使用馆藏或传承人图案"],
                evidence_refs=[ref for ref in evidence if ref.startswith("C")],
            )
        ],
        assembly_steps=["确认授权材料", "排版", "打样", "装订", "固定材料卡", "核对溯源"],
        qc_checks=["尺寸", "耐折", "文字", "二维码", "材料来源", "授权信息"],
        safety_and_compliance=["材料样的小部件与纤维风险按销售年龄验证。"],
        factory_open_questions=["授权材料、装订、成本、起订量与销售地区待确认。"],
    )


def _poster_request(
    design_id: str,
    title: str,
    subtitle: str,
    prompt: str,
    avoid: list[str],
) -> PosterRenderRequest:
    return PosterRenderRequest(
        request_id=f"PR-{design_id}",
        required_panels=["文化元素与转译规则", "成品主视觉", "爆炸拆解", "材料/BOM", "工艺与审核边界"],
        exact_copy={"title": title, "subtitle": subtitle},
        image_prompt=prompt,
        constraints=[
            "一张成品主视图和一组清晰爆炸拆解必须同时出现",
            "不使用任何馆藏参考图像作为输入或贴图",
            "画面不写文字；准确中文由QianCraft本地排版器叠加",
            "原创、可制造、无品牌、无水印",
        ],
        avoid=avoid,
        reference_policy="textual primitives only; reference_only museum pixels are prohibited",
        intended_output="data/outputs/design_poster.png",
    )


def _plush_poster_request(design_id: str) -> PosterRenderRequest:
    prompt = """Use case: product-mockup
Asset type: source visual for an A2-style vertical industrial design poster
Primary request: an original 13.5 cm tactile plush bag charm concept inspired only by the abstract layered stitch structure of Leishan Miao embroidery, plus a clean exploded view of its manufacturable parts
Scene/backdrop: warm off-white design studio board with restrained deep-indigo textile accents
Subject: one rounded non-figurative plush charm with a detachable central embroidered tactile panel; beside it, a six-part exploded view showing front shell, back shell, embroidered panel, fiber fill, woven loop, and dark metal swivel clasp
Style/medium: premium product visualization, realistic textile and embroidery texture, contemporary Chinese industrial design presentation, artistic but technically legible
Composition/framing: portrait board; large three-quarter hero product and smaller orthographic/exploded components with generous clean margins for later exact labels
Lighting/mood: soft museum-grade studio light, calm, tactile, refined
Color palette: display-only deep indigo body, red and white thread accents, low-reflection dark hardware; do not imply a standardized traditional palette
Materials/textures: short-pile plush, cotton twill, clearly raised machine-embroidered threads, polyester fill, woven nylon loop, matte metal clasp
Constraints: entirely original geometry; no text, no logos, no watermark; visually distinguish machine embroidery from handmade craft; no copied traditional motif or garment
Avoid: butterflies, dragons, sacred symbols, human faces, ethnic costume silhouettes, silver-horn headdresses, complete traditional borders, museum imagery, cheap sequins, kawaii character cliché"""
    return _poster_request(
        design_id,
        "针层绒伴",
        "雷山苗绣针脚层次启发的触感挂偶｜概念样",
        prompt,
        ["完整传统纹样", "神圣/身份图式", "馆藏图像", "虚假手工声明", "量产定稿字样"],
    )


def _magnet_poster_request(design_id: str) -> PosterRenderRequest:
    prompt = """Use case: product-mockup
Asset type: source visual for an A2-style vertical industrial design poster
Primary request: Create one original manufacturable 76 mm modular fridge magnet concept based only on counted-thread grid construction logic associated with a Huaxi cross-stitch pilot, together with a clean exploded view of its parts. This is a new original grid composition, not a traditional motif.
Scene/backdrop: warm off-white premium industrial-design presentation board with restrained deep-indigo textile accents.
Subject: a rounded-square matte deep-indigo frame holding a removable 58 mm cotton-twill embroidered insert. The insert uses a completely original abstract grid of simple cross-stitch units, mirror rhythm, and visible counted-thread direction—no animal, plant, ancestor, sacred, or garment motif. Beside it show a clear exploded view: front frame, removable embroidered textile insert, thin support plate, fully enclosed circular magnet, back plate, and small provenance label area.
Style/medium: polished premium product visualization, realistic textile grain and raised machine-embroidery, contemporary Chinese industrial design presentation, artistic but technically legible.
Composition/framing: portrait presentation board; large three-quarter hero product plus front, side, back, and exploded components; generous clean margins for exact labels that will be added later outside this image.
Lighting/mood: soft museum-grade studio lighting, calm, precise, collectible.
Color palette: display-only deep indigo frame and textile ground, restrained red and warm-white thread accents, matte dark back plate. Do not imply a standardized traditional palette.
Materials/textures: matte injection-molded polymer frame, cotton twill, visibly raised machine-embroidered thread, enclosed magnet, crisp removable fit.
Constraints: entirely original geometry; no text, no numbers, no letters, no logos, no watermark; magnet must be enclosed and not visible on the finished product; clear seams, reasonable part thickness and attachment logic; no copied traditional motif, museum work, clothing, or sacred imagery.
Avoid: butterflies, birds, dragons, fish, frogs, flowers, ancestor motifs, sacred symbols, ethnic costume silhouettes, silver-horn headdresses, complete traditional borders, museum imagery, cheap sequins, fake handmade appearance, souvenir-shop cliché."""
    return _poster_request(
        design_id,
        "针格模块",
        "花溪挑花数纱结构启发的互动冰箱贴｜概念样",
        prompt,
        ["完整传统纹样", "跨支系混用", "馆藏图像", "外露磁体"],
    )


def _kit_poster_request(design_id: str) -> PosterRenderRequest:
    prompt = """Use case: product-mockup
Asset type: source visual for a vertical design poster
Primary request: an archival material experience kit with a folded paper case, replaceable textile sample cards and provenance card, shown as hero product and exploded parts
Style/medium: refined editorial product visualization, tactile paper and textile
Composition/framing: portrait board with clean margins for later labels
Constraints: no text, no logos, no watermark, no traditional motif or museum image
Avoid: invented cultural symbols, fake endorsements"""
    return _poster_request(
        design_id,
        "共作档案",
        "贵州苗绣材料与溯源体验套件｜概念样",
        prompt,
        ["传统纹样复刻", "馆藏图像", "虚构授权"],
    )


def render_design_package_markdown(package: DesignPackage) -> str:
    product = package.product
    lines = [
        f"# {product.product_name}",
        "",
        "> 本文件是概念视觉与工厂首样/报价输入，不是量产工程图、合规证书或商业授权。",
        "",
        "## 1. 输入接口",
        "",
        f"- 设计 ID：`{package.design_id}`",
        f"- 输入：`{package.input_contract.source_file}`",
        f"- 输入 SHA-256：`{package.input_contract.source_sha256}`",
        f"- 主机会：`{package.selection.primary_opportunity_id}`（{package.selection.primary_verification}）",
        f"- 支持机会：{'、'.join(package.selection.supporting_opportunity_ids) or '无'}",
        "",
        "## 2. 概念与风格",
        "",
        f"- 类型：{product.product_type}",
        f"- 概念：{product.concept_statement}",
        f"- 形态：{product.form_description}",
        f"- 风格：{'、'.join(product.visual_style)}",
        f"- 色彩：{'；'.join(product.color_direction)}",
        f"- 交互：{'、'.join(product.interaction)}",
        "",
        "## 3. 文化元素与边界",
        "",
    ]
    for item in package.cultural_elements:
        lines.extend(
            [
                f"### {item.name}",
                "",
                f"- 地域/社区：{item.region}｜{item.branch_or_community}",
                f"- 视觉作用：{item.visual_role}",
                f"- 转译规则：{item.transformation_rule}",
                f"- 权利规则：{item.rights_rule}",
                f"- 禁止复制：{'；'.join(item.do_not_copy)}",
                f"- 证据：{'、'.join(item.evidence_refs)}",
                "",
            ]
        )
    lines.extend(["## 4. 首样尺寸", ""])
    lines.extend(
        f"- {item.item}：{item.value_mm:g} mm（±{item.tolerance_mm:g} mm）{item.note}"
        for item in product.dimensions
    )
    lines.extend(["", "## 5. BOM", "", "| ID | 部件 | 材料/规格 | 工艺 | 装配 | 首样目标 | QC |", "|---|---|---|---|---|---|---|"])
    for item in package.manufacturing.bill_of_materials:
        lines.append(
            f"| {item.part_id} | {item.component} | {item.material}；{item.specification} | "
            f"{item.process} | {item.assembly} | {item.tolerance_or_target} | {item.qc_check} |"
        )
    lines.extend(["", "## 6. 图案与工艺", ""])
    for item in package.manufacturing.pattern_applications:
        lines.extend(
            [
                f"### {item.pattern_id}｜{item.name}",
                "",
                f"- 原创规则：{item.originality_rule}",
                f"- 几何：{'、'.join(item.geometry)}",
                f"- 位置：{item.placement}",
                f"- 工艺：{item.process}",
                f"- 文化边界：{'；'.join(item.cultural_boundary)}",
                "",
            ]
        )
    lines.extend(["## 7. 装配顺序", ""])
    lines.extend(f"{index}. {step}" for index, step in enumerate(package.manufacturing.assembly_steps, 1))
    lines.extend(["", "## 8. QC / 安全 / 待确认", "", "### QC", ""])
    lines.extend(f"- {item}" for item in package.manufacturing.qc_checks)
    lines.extend(["", "### 安全与合规", ""])
    lines.extend(f"- {item}" for item in package.manufacturing.safety_and_compliance)
    lines.extend(["", "### 工厂开放问题", ""])
    lines.extend(f"- {item}" for item in package.manufacturing.factory_open_questions)
    lines.extend(["", "### 文化审核门", ""])
    lines.extend(f"- {item}" for item in package.cultural_review_gates)
    lines.extend(["", "## 9. 海报渲染接口", ""])
    lines.extend(
        [
            f"- Request ID：`{package.poster_request.request_id}`",
            f"- 画布：{package.poster_request.canvas_width_px}×{package.poster_request.canvas_height_px}px",
            f"- 目标：`{package.poster_request.intended_output}`",
            f"- 参考策略：{package.poster_request.reference_policy}",
            "",
            "```text",
            package.poster_request.image_prompt,
            "```",
            "",
            f"证据编号：{'、'.join(package.evidence_refs)}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
