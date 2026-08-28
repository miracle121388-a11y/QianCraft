from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class QianCraftModel(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)


class SourceRef(QianCraftModel):
    source_id: str
    source_url: str = ""
    source_title: str = ""
    source_type: str = ""
    publisher: str = ""
    published_at: str = ""
    retrieved_at: str = ""
    supports: list[str] = Field(default_factory=list)


class CultureRecord(QianCraftModel):
    culture_id: str
    culture_name: str
    aliases: list[str] = Field(default_factory=list)
    category: str = ""
    region: list[str] = Field(default_factory=list)
    ethnic_groups: list[str] = Field(default_factory=list)
    history: list[str] = Field(default_factory=list)
    myths: list[str] = Field(default_factory=list)
    cultural_narratives: list[str] = Field(default_factory=list)
    core_values: list[str] = Field(default_factory=list)
    totems: list[str] = Field(default_factory=list)
    symbols: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    crafts: list[str] = Field(default_factory=list)
    objects: list[str] = Field(default_factory=list)
    usage_scenarios: list[str] = Field(default_factory=list)
    festivals_rituals: list[str] = Field(default_factory=list)
    cultural_taboos: list[str] = Field(default_factory=list)
    branch_differences: list[str] = Field(default_factory=list)
    protection_info: list[str] = Field(default_factory=list)
    inheritors: list[str] = Field(default_factory=list)
    existing_cultural_products: list[str] = Field(default_factory=list)
    modern_translations: list[str] = Field(default_factory=list)
    modernizable_elements: list[str] = Field(default_factory=list)
    non_transferable_elements: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    field_sources: dict[str, list[str]] = Field(default_factory=dict)


class CultureDNA(QianCraftModel):
    culture_name: str
    aliases: list[str] = Field(default_factory=list)
    region: list[str] = Field(default_factory=list)
    ethnic_groups: list[str] = Field(default_factory=list)
    history: list[str] = Field(default_factory=list)
    core_stories: list[str] = Field(default_factory=list)
    core_values: list[str] = Field(default_factory=list)
    symbols: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    crafts: list[str] = Field(default_factory=list)
    objects: list[str] = Field(default_factory=list)
    visual_features: list[str] = Field(default_factory=list)
    emotional_meanings: list[str] = Field(default_factory=list)
    cultural_taboos: list[str] = Field(default_factory=list)
    branch_differences: list[str] = Field(default_factory=list)
    protection_info: list[str] = Field(default_factory=list)
    representative_inheritors: list[str] = Field(default_factory=list)
    modernizable_elements: list[str] = Field(default_factory=list)
    non_transferable_elements: list[str] = Field(default_factory=list)
    existing_cultural_products: list[str] = Field(default_factory=list)
    modern_translations: list[str] = Field(default_factory=list)
    visual_dna: dict[str, list[str]] = Field(default_factory=dict)
    semantic_dna: list[str] = Field(default_factory=list)
    cultural_boundary: dict[str, list[str]] = Field(default_factory=dict)
    source_refs: list[SourceRef] = Field(default_factory=list)
    retrieval: dict[str, Any] = Field(default_factory=dict)


class MarketPost(QianCraftModel):
    platform: str = ""
    post_id: str = ""
    title: str = ""
    content: str = ""
    author: str = ""
    published_at: str = ""
    url: str = ""
    likes: int = Field(default=0, ge=0)
    favorites: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list)
    search_keyword: str = ""
    product_form: str = ""
    product_category: str = ""
    styles: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    target_audiences: list[str] = Field(default_factory=list)
    price_range: str = ""
    usage_scenarios: list[str] = Field(default_factory=list)
    emotional_values: list[str] = Field(default_factory=list)
    verified_market_signal: str = ""
    verified_signal_strength: int = Field(default=0, ge=0, le=100)
    metrics_verified: bool = False
    evidence_type: Literal[
        "social_signal", "institutional_signal", "media_signal", "product_signal"
    ] = "social_signal"
    evidence_quality_score: int = Field(default=0, ge=0, le=100)
    evidence_quality_reasons: list[str] = Field(default_factory=list)
    source_ref: str = ""
    retrieved_at: str = ""
    platform_hot_score: float = Field(default=0, ge=0, le=100)
    real_engagement_score: float = Field(default=0, ge=0, le=100)
    institutional_signal_score: float = Field(default=0, ge=0, le=100)
    derived_viral_score: float = Field(default=0, ge=0, le=100)
    viral_score: float = Field(default=0, ge=0, le=100)
    viral_reasons: list[str] = Field(default_factory=list)


class ProductFormHotness(QianCraftModel):
    rank: int = Field(ge=1, le=10)
    product_form: str
    cross_platform_hot_score: float = Field(ge=0, le=100)
    platform_coverage: int = Field(ge=1, le=4)
    platform_scores: dict[str, float] = Field(default_factory=dict)
    platform_post_counts: dict[str, int] = Field(default_factory=dict)
    sample_size: int = Field(ge=1)
    high_hot_post_ratio: float = Field(ge=0, le=1)
    freshness_score: float = Field(ge=0, le=100)
    why_hot: list[str] = Field(default_factory=list)
    representative_posts: list[MarketPost] = Field(default_factory=list)


class ProductFormHotnessReport(QianCraftModel):
    generated_at: str
    platforms: list[str] = Field(default_factory=list)
    total_sample_size: int = Field(default=0, ge=0)
    platform_sample_sizes: dict[str, int] = Field(default_factory=dict)
    ranking: list[ProductFormHotness] = Field(default_factory=list)
    priority_product_forms: list[str] = Field(default_factory=list, max_length=5)
    methodology: dict[str, Any] = Field(default_factory=dict)


class TrendDNA(QianCraftModel):
    time_window: str = ""
    platforms: list[str] = Field(default_factory=list)
    sample_size: int = Field(default=0, ge=0)
    hot_categories: list[str] = Field(default_factory=list)
    rising_categories: list[str] = Field(default_factory=list)
    hot_styles: list[str] = Field(default_factory=list)
    hot_colors: list[str] = Field(default_factory=list)
    hot_materials: list[str] = Field(default_factory=list)
    target_audiences: list[str] = Field(default_factory=list)
    price_ranges: list[str] = Field(default_factory=list)
    usage_scenarios: list[str] = Field(default_factory=list)
    emotional_values: list[str] = Field(default_factory=list)
    viral_mechanisms: list[str] = Field(default_factory=list)
    visual_patterns: list[str] = Field(default_factory=list)
    saturated_categories: list[str] = Field(default_factory=list)
    white_space_opportunities: list[str] = Field(default_factory=list)
    hot_product_forms: list[ProductFormHotness] = Field(default_factory=list)
    priority_product_forms: list[str] = Field(default_factory=list, max_length=5)
    representative_cases: list[MarketPost] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    methodology_notes: list[str] = Field(default_factory=list)
    retrieval: dict[str, Any] = Field(default_factory=dict)


class BenchmarkCase(QianCraftModel):
    brand_or_institution: str
    culture_source: str = ""
    product_category: str = ""
    design_idea: str = ""
    visual_style: str = ""
    innovation_point: str = ""
    market_signal: str = ""
    why_it_worked: list[str] = Field(default_factory=list)
    transferable_lessons: list[str] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class OpportunityVerification(QianCraftModel):
    status: Literal["verified", "warning", "rejected"] = "warning"
    retrieval_mode: str = "structured_graph"
    queries: list[str] = Field(default_factory=list)
    culture_evidence_refs: list[str] = Field(default_factory=list)
    branch_region_findings: list[str] = Field(default_factory=list)
    taboo_findings: list[str] = Field(default_factory=list)
    modern_translation_findings: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class OpportunitySignal(QianCraftModel):
    opportunity_id: str = ""
    culture_element: str
    culture_meaning: str = ""
    trend_element: str = ""
    market_signal: str = ""
    match_reason: str = ""
    potential_product_categories: list[str] = Field(default_factory=list)
    target_audience: list[str] = Field(default_factory=list)
    design_keywords: list[str] = Field(default_factory=list)
    cultural_constraints: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    confidence_score: int = Field(default=0, ge=0, le=100)
    culture_fit: int = Field(default=0, ge=0, le=100)
    market_pull: int = Field(default=0, ge=0, le=100)
    novelty: int = Field(default=0, ge=0, le=100)
    visual_potential: int = Field(default=0, ge=0, le=100)
    social_shareability: int = Field(default=0, ge=0, le=100)
    product_feasibility: int = Field(default=0, ge=0, le=100)
    cultural_risk: int = Field(default=0, ge=0, le=100)
    overall_score: float = Field(default=0, ge=0, le=100)
    reason: str = ""
    verification: OpportunityVerification = Field(default_factory=OpportunityVerification)


class VisualReference(QianCraftModel):
    visual_id: str
    title: str
    subject_type: str
    region: str
    craft: str
    cultural_context: str
    source_ref: str
    source_url: str
    image_url: str
    local_path: str = ""
    rights_status: Literal["reference_only", "cleared", "public_domain"] = "reference_only"
    rights_note: str
    design_relevance: list[str] = Field(default_factory=list)
    not_to_copy: list[str] = Field(default_factory=list)


class PatternPrimitive(QianCraftModel):
    primitive_id: str
    name: str
    derived_from: list[str] = Field(default_factory=list)
    geometry: list[str] = Field(default_factory=list)
    transformation_guidance: list[str] = Field(default_factory=list)
    cultural_boundary: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class ColorPalette(QianCraftModel):
    palette_id: str
    name: str
    colors: list[str] = Field(default_factory=list)
    source_basis: str
    evidence_refs: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @field_validator("colors")
    @classmethod
    def reject_unmeasured_hex(cls, value: list[str]) -> list[str]:
        if any(item.strip().startswith("#") for item in value):
            raise ValueError("未进行色卡测量时不得伪造 HEX 色值")
        return value


class VisualReferencePack(QianCraftModel):
    project: str = "QianCraft"
    topic: str = "贵州苗绣"
    references: list[VisualReference] = Field(default_factory=list)
    pattern_primitives: list[PatternPrimitive] = Field(default_factory=list)
    color_palettes: list[ColorPalette] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    methodology_notes: list[str] = Field(default_factory=list)

    @field_validator("references")
    @classmethod
    def require_visual_coverage(cls, value: list[VisualReference]) -> list[VisualReference]:
        if len(value) < 10:
            raise ValueError("visual reference pack requires at least 10 references")
        return value


class PriorityOpportunity(QianCraftModel):
    rank: int = Field(ge=1, le=3)
    opportunity_id: str
    title: str
    culture_element: str
    trend_element: str
    why_now: str
    potential_product_categories: list[str] = Field(default_factory=list)
    design_keywords: list[str] = Field(default_factory=list)
    cultural_constraints: list[str] = Field(default_factory=list)
    score_breakdown: dict[str, float | int] = Field(default_factory=dict)
    overall_score: float = Field(ge=0, le=100)
    verification: OpportunityVerification
    evidence_refs: list[str] = Field(default_factory=list)


class DesignerHandoff(QianCraftModel):
    ready: bool = True
    project: dict[str, Any] = Field(default_factory=dict)
    design_mission: dict[str, Any] = Field(default_factory=dict)
    culture_context: dict[str, Any] = Field(default_factory=dict)
    market_context: dict[str, Any] = Field(default_factory=dict)
    priority_opportunities: list[PriorityOpportunity] = Field(default_factory=list)
    visual_reference_pack: VisualReferencePack
    hard_constraints: list[str] = Field(default_factory=list)
    soft_direction: list[str] = Field(default_factory=list)
    creative_brief: str
    output_requirements: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_designer_gate(self) -> DesignerHandoff:
        if not 1 <= len(self.priority_opportunities) <= 3:
            raise ValueError("designer handoff must contain one to three priority opportunities")
        if any(item.verification.status == "rejected" for item in self.priority_opportunities):
            raise ValueError("rejected opportunity cannot enter designer handoff")
        if not 150 <= len(self.creative_brief) <= 350:
            raise ValueError("creative brief must contain 150-350 characters")
        return self


class DesignInputContract(QianCraftModel):
    source_file: str
    source_sha256: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
    )
    schema_name: Literal["DesignerHandoff"] = "DesignerHandoff"
    ready: bool = True
    input_stage: str = "designer_handoff"
    authorized_scope: Literal["concept_visual_and_prototype_brief"] = (
        "concept_visual_and_prototype_brief"
    )
    selected_opportunity_ids: list[str] = Field(default_factory=list, min_length=1)


class DesignSelection(QianCraftModel):
    primary_opportunity_id: str
    primary_verification: Literal["verified", "warning"]
    supporting_opportunity_ids: list[str] = Field(default_factory=list)
    selection_reason: list[str] = Field(default_factory=list, min_length=1)
    held_back_opportunities: dict[str, str] = Field(default_factory=dict)


class CulturalElementSpec(QianCraftModel):
    element_id: str
    name: str
    region: str
    branch_or_community: str
    visual_role: str
    transformation_rule: str
    source_primitives: list[str] = Field(default_factory=list)
    reference_visual_ids: list[str] = Field(default_factory=list)
    rights_rule: str
    do_not_copy: list[str] = Field(default_factory=list, min_length=1)
    evidence_refs: list[str] = Field(default_factory=list, min_length=1)


class PrototypeDimension(QianCraftModel):
    item: str
    value_mm: float = Field(gt=0)
    tolerance_mm: float = Field(default=0, ge=0)
    note: str = ""


class ProductDesignSpec(QianCraftModel):
    product_name: str
    product_type: str
    prototype_level: Literal["appearance_and_structure_sample"] = (
        "appearance_and_structure_sample"
    )
    target_audience: str
    use_scenarios: list[str] = Field(default_factory=list, min_length=1)
    concept_statement: str
    form_description: str
    interaction: list[str] = Field(default_factory=list)
    visual_style: list[str] = Field(default_factory=list, min_length=1)
    color_direction: list[str] = Field(default_factory=list, min_length=1)
    dimensions: list[PrototypeDimension] = Field(default_factory=list, min_length=3)
    target_weight_g: str
    claims: list[str] = Field(default_factory=list)


class MaterialLineItem(QianCraftModel):
    part_id: str
    component: str
    material: str
    specification: str
    color_finish: str
    quantity: str
    process: str
    assembly: str
    tolerance_or_target: str
    qc_check: str
    supplier_confirmation_required: bool = True


class PatternApplicationSpec(QianCraftModel):
    pattern_id: str
    name: str
    originality_rule: str
    geometry: list[str] = Field(default_factory=list, min_length=1)
    placement: str
    scale_and_repeat: str
    process: str
    color_and_material: str
    registration_tolerance: str
    cultural_boundary: list[str] = Field(default_factory=list, min_length=1)
    evidence_refs: list[str] = Field(default_factory=list, min_length=1)


class ManufacturingBrief(QianCraftModel):
    readiness: Literal["prototype_quote_and_sample_only"] = (
        "prototype_quote_and_sample_only"
    )
    bill_of_materials: list[MaterialLineItem] = Field(default_factory=list, min_length=5)
    pattern_applications: list[PatternApplicationSpec] = Field(
        default_factory=list,
        min_length=1,
    )
    assembly_steps: list[str] = Field(default_factory=list, min_length=5)
    qc_checks: list[str] = Field(default_factory=list, min_length=5)
    packaging_direction: list[str] = Field(default_factory=list)
    safety_and_compliance: list[str] = Field(default_factory=list, min_length=1)
    factory_open_questions: list[str] = Field(default_factory=list, min_length=1)


class PosterRenderRequest(QianCraftModel):
    request_id: str
    use_case: Literal["product-mockup"] = "product-mockup"
    asset_type: str = "A2-style vertical design poster"
    canvas_width_px: int = Field(default=1800, ge=1200)
    canvas_height_px: int = Field(default=2400, ge=1600)
    orientation: Literal["portrait"] = "portrait"
    required_panels: list[str] = Field(default_factory=list, min_length=4)
    exact_copy: dict[str, str] = Field(default_factory=dict, min_length=2)
    image_prompt: str
    constraints: list[str] = Field(default_factory=list, min_length=1)
    avoid: list[str] = Field(default_factory=list, min_length=1)
    reference_policy: str
    intended_output: str


class DesignValidation(QianCraftModel):
    evidence_lock: bool = True
    reference_images_used_as_pixels: bool = False
    cultural_review_status: Literal["required_before_commercialization"] = (
        "required_before_commercialization"
    )
    engineering_review_required: bool = True
    mass_production_ready: bool = False
    checks: list[str] = Field(default_factory=list, min_length=1)


class DesignPackage(QianCraftModel):
    schema_version: str = "1.0"
    design_id: str
    generated_at: datetime
    stage: Literal["concept_visual_and_prototype_brief"] = (
        "concept_visual_and_prototype_brief"
    )
    input_contract: DesignInputContract
    selection: DesignSelection
    cultural_elements: list[CulturalElementSpec] = Field(default_factory=list, min_length=1)
    product: ProductDesignSpec
    manufacturing: ManufacturingBrief
    poster_request: PosterRenderRequest
    cultural_review_gates: list[str] = Field(default_factory=list, min_length=1)
    engineering_review_gates: list[str] = Field(default_factory=list, min_length=1)
    evidence_refs: list[str] = Field(default_factory=list, min_length=2)
    validation: DesignValidation

    @model_validator(mode="after")
    def validate_design_evidence(self) -> DesignPackage:
        if self.selection.primary_opportunity_id not in self.input_contract.selected_opportunity_ids:
            raise ValueError("primary design opportunity must come from DesignerHandoff")
        if not any(ref.startswith("C") for ref in self.evidence_refs):
            raise ValueError("design package requires at least one cultural evidence ref")
        if not any(ref.startswith("M") for ref in self.evidence_refs):
            raise ValueError("design package requires at least one market evidence ref")
        if self.validation.reference_images_used_as_pixels:
            raise ValueError("reference_only images cannot be used as design pixels")
        if self.validation.mass_production_ready:
            raise ValueError("concept design cannot claim mass-production readiness")
        return self


class DesignRenderManifest(QianCraftModel):
    design_id: str
    rendered_at: datetime
    engine: str
    poster_path: str
    poster_sha256: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
    )
    hero_asset_path: str = ""
    hero_asset_sha256: str = ""
    exact_text_compositor: bool = True
    reference_only_images_used: bool = False
    width_px: int = Field(gt=0)
    height_px: int = Field(gt=0)
    notes: list[str] = Field(default_factory=list)


class PreDesignStrategy(QianCraftModel):
    project: dict[str, Any] = Field(default_factory=dict)
    culture_dna: CultureDNA
    trend_dna: TrendDNA
    benchmark_cases: list[BenchmarkCase] = Field(default_factory=list)
    opportunity_signals: list[OpportunitySignal] = Field(default_factory=list)
    recommended_product_categories: list[str] = Field(default_factory=list)
    design_keywords: list[str] = Field(default_factory=list)
    cultural_constraints: list[str] = Field(default_factory=list)
    evidence_summary: dict[str, Any] = Field(default_factory=dict)
    handoff_to_designer: DesignerHandoff
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("opportunity_signals")
    @classmethod
    def require_opportunities(cls, value: list[OpportunitySignal]) -> list[OpportunitySignal]:
        if len(value) < 8:
            raise ValueError("at least 8 opportunity signals are required")
        return value


class DemoRequest(QianCraftModel):
    topic: str = "贵州苗绣"
    region: str = "贵州"
    target_market: str = "18-30岁年轻消费者"
    goal: str = "寻找具有爆款潜力的文创产品机会"


class ComponentStatus(QianCraftModel):
    component: str
    mode: str
    engine: str
    ok: bool
    detail: str = ""


class MarketSourceStatus(QianCraftModel):
    status: Literal["live", "cache", "unavailable"]
    login_state: Literal["authorized", "missing", "expired"]
    auth_method: Literal["cookie", "qrcode", "cdp"]
    platform: str = "multi"
    platforms: list[str] = Field(default_factory=list)
    live_post_count: int = Field(default=0, ge=0)
    cache_post_count: int = Field(default=0, ge=0)
    keyword_count: int = Field(default=0, ge=0)
    keywords: list[str] = Field(default_factory=list)
    raw_paths: list[str] = Field(default_factory=list)
    derived_path: str = ""
    hotness_path: str = ""
    detail: str = ""


class MarketPlatformStatus(QianCraftModel):
    status: Literal["live", "cache", "unavailable"]
    login_state: Literal["authorized", "missing", "expired"]
    auth_method: Literal["cookie", "qrcode", "cdp"]
    platform: Literal["xhs", "dy", "bili", "wb"]
    adapter_discovered: bool = True
    login_ok: bool = False
    search_ok: bool = False
    sample_size: int = Field(default=0, ge=0)
    live_post_count: int = Field(default=0, ge=0)
    cache_post_count: int = Field(default=0, ge=0)
    keyword_count: int = Field(default=0, ge=0)
    keywords: list[str] = Field(default_factory=list)
    raw_paths: list[str] = Field(default_factory=list)
    canonical_path: str = ""
    derived_path: str = ""
    detail: str = ""


class RunManifest(QianCraftModel):
    run_id: str
    started_at: datetime
    finished_at: datetime
    request: DemoRequest
    components: list[ComponentStatus]
    market_source: MarketSourceStatus
    market_platforms: dict[str, MarketPlatformStatus] = Field(default_factory=dict)
    outputs: dict[str, str]
    source_snapshot_date: str
