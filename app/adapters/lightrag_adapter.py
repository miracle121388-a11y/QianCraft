from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np

from app.config import Settings
from app.schemas import (
    ComponentStatus,
    CultureDNA,
    CultureRecord,
    OpportunitySignal,
    OpportunityVerification,
    SourceRef,
    VisualReferencePack,
)


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        clean = str(value).strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


class LightRAGAdapter:
    """Build Culture DNA from the curated graph and optionally persist it in LightRAG."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._payload = self._load_payload(settings.culture_graph_path)
        self._sources = {
            source["source_id"]: SourceRef.model_validate(source)
            for source in self._payload.get("sources", [])
        }
        self._records = [
            CultureRecord.model_validate(record) for record in self._payload.get("records", [])
        ]

    @staticmethod
    def _load_payload(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Culture knowledge graph not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _select_records(self, topic: str) -> list[CultureRecord]:
        normalized = re.sub(r"\s+", "", topic).lower()
        scored: list[tuple[int, CultureRecord]] = []
        for record in self._records:
            names = [record.culture_name, *record.aliases]
            compact_names = [re.sub(r"\s+", "", name).lower() for name in names]
            score = 0
            if normalized == re.sub(r"\s+", "", record.culture_name).lower():
                score = 100
            elif normalized in compact_names:
                score = 95
            elif any(normalized in name or name in normalized for name in compact_names):
                score = 70
            elif "苗绣" in normalized and any("苗绣" in name for name in compact_names):
                score = 60
            if score:
                scored.append((score, record))

        if not scored:
            available = "、".join(record.culture_name for record in self._records[:12])
            raise LookupError(f"知识图谱中未找到“{topic}”；当前示例包括：{available}")

        scored.sort(key=lambda item: (-item[0], item[1].culture_id))
        selected = [record for _, record in scored]
        if "苗绣" in normalized:
            embroidery_variants = [
                record
                for record in self._records
                if "苗绣" in record.culture_name or any("苗绣" in alias for alias in record.aliases)
            ]
            selected = _unique_records([*selected, *embroidery_variants])
        return selected

    def build_culture_dna(self, topic: str) -> CultureDNA:
        selected = self._select_records(topic)
        primary = selected[0]

        def collect(field: str) -> list[str]:
            return _unique(
                value
                for record in selected
                for value in getattr(record, field, [])
            )

        source_ids = _unique(
            source_id for record in selected for source_id in record.source_refs
        )
        for boundary_source in ("C009", "C010"):
            if boundary_source in self._sources and boundary_source not in source_ids:
                source_ids.append(boundary_source)

        patterns = collect("patterns")
        symbols = _unique([*collect("totems"), *collect("symbols")])
        crafts = collect("crafts")
        objects = collect("objects")
        branch_differences = collect("branch_differences")
        myths = collect("myths")
        narratives = collect("cultural_narratives")
        values = collect("core_values")
        taboos = collect("cultural_taboos")
        non_transferable = collect("non_transferable_elements")
        modernizable = collect("modernizable_elements")

        return CultureDNA(
            culture_name=primary.culture_name,
            aliases=_unique(alias for record in selected for alias in record.aliases),
            region=collect("region"),
            ethnic_groups=collect("ethnic_groups"),
            history=collect("history"),
            core_stories=_unique([*myths, *narratives]),
            core_values=values,
            symbols=symbols,
            patterns=patterns,
            colors=collect("colors"),
            materials=collect("materials"),
            crafts=crafts,
            objects=objects,
            visual_features=_unique(
                [
                    "动植物、几何与神话形象经过夸张、变形、多维立体造型与“型中型”复合构图",
                    "藏青或黑色底与高饱和彩线形成强对比",
                    "针法、线材与金属材料共同形成明显触觉层次",
                    *branch_differences[:4],
                ]
            ),
            emotional_meanings=_unique([*values, "可穿戴的家族与地方记忆"]),
            cultural_taboos=taboos,
            branch_differences=branch_differences,
            protection_info=collect("protection_info"),
            representative_inheritors=collect("inheritors"),
            modernizable_elements=modernizable,
            non_transferable_elements=non_transferable,
            existing_cultural_products=collect("existing_cultural_products"),
            modern_translations=collect("modern_translations"),
            visual_dna={
                "graphics": _unique([*symbols, *patterns]),
                "colors": collect("colors"),
                "materials": collect("materials"),
                "crafts": crafts,
                "forms": objects,
                "composition": _unique(
                    ["复合动植物", "对称与连续边饰", "主体纹样与密集填充", *branch_differences]
                ),
            },
            semantic_dna=_unique([*values, *myths]),
            cultural_boundary={
                "must_keep": [
                    "明确标注地域、支系、工艺和材料",
                    "重要纹样释义必须回到对应社区或传承人核验",
                    "共同创作、署名并建立公平收益机制",
                ],
                "can_modernize": modernizable,
                "review_required": taboos,
                "avoid": non_transferable,
            },
            source_refs=[self._sources[source_id] for source_id in source_ids if source_id in self._sources],
            retrieval={
                "mode": "structured_graph",
                "records_matched": len(selected),
                "record_ids": [record.culture_id for record in selected],
                "graph_snapshot": self._payload.get("updated_at", ""),
            },
        )

    def build_visual_reference_pack(self, topic: str) -> VisualReferencePack:
        """Load the reviewed visual evidence layer without downloading protected images."""

        payload = self._load_payload(self.settings.visual_references_path)
        payload["topic"] = topic
        pack = VisualReferencePack.model_validate(payload)
        known_sources = set(self._sources)
        unknown = sorted(set(pack.source_refs) - known_sources)
        if unknown:
            raise ValueError(f"视觉参考包存在未登记来源：{', '.join(unknown)}")
        return pack

    async def verify_opportunities(
        self,
        opportunities: list[OpportunitySignal],
        candidate_limit: int = 6,
    ) -> dict[str, OpportunityVerification]:
        """Run the Strategist's secondary culture-evidence gate through this LightRAG adapter."""

        ordered = sorted(
            opportunities,
            key=lambda item: (item.overall_score, len(item.evidence_refs), -item.cultural_risk),
            reverse=True,
        )
        candidate_ids = {item.opportunity_id for item in ordered[:candidate_limit]}
        results: dict[str, OpportunityVerification] = {}
        for item in opportunities:
            if item.opportunity_id not in candidate_ids:
                results[item.opportunity_id] = OpportunityVerification(
                    status="warning",
                    retrieval_mode="candidate_gate",
                    queries=[],
                    culture_evidence_refs=[
                        ref for ref in item.evidence_refs if ref.startswith("C")
                    ],
                    warnings=["该机会未进入本轮最高分候选集，未送入 Designer Handoff。"],
                    notes=["仅对评分靠前的候选执行二次文化核验。"],
                )
                continue

            verification, probe_term = self._verify_structured(item)
            if self.settings.live_mode and verification.status != "rejected":
                try:
                    probe = await self._index_and_probe_lightrag(probe_term)
                    verification.retrieval_mode = "LightRAG local KG"
                    verification.queries.append(str(probe.get("probe_node", probe_term)))
                    verification.notes.append(
                        f"LightRAG 节点命中，关联边 {probe.get('probe_edge_count', 0)} 条。"
                    )
                except Exception as exc:  # noqa: BLE001 - external runtime failures become warnings
                    verification.status = "warning"
                    verification.warnings.append(
                        f"LightRAG 运行时复核失败，保留结构化图谱结论：{_safe_error(exc)}"
                    )
            results[item.opportunity_id] = verification
        return results

    def _verify_structured(
        self, opportunity: OpportunitySignal
    ) -> tuple[OpportunityVerification, str]:
        text = " ".join(
            [
                opportunity.culture_element,
                opportunity.culture_meaning,
                opportunity.match_reason,
                *opportunity.cultural_constraints,
                *opportunity.design_keywords,
            ]
        )
        claim_text = (
            f"{opportunity.culture_element} {opportunity.culture_meaning} "
            f"{opportunity.match_reason}"
        )
        culture_refs = [ref for ref in opportunity.evidence_refs if ref.startswith("C")]
        known_refs = [ref for ref in culture_refs if ref in self._sources]
        conflicts: list[str] = []
        warnings: list[str] = []
        branch_findings: list[str] = []
        taboo_findings: list[str] = []
        modern_findings: list[str] = []

        if not culture_refs:
            conflicts.append("缺少文化证据编号。")
        unknown_refs = sorted(set(culture_refs) - set(known_refs))
        if unknown_refs:
            conflicts.append(f"文化证据编号未登记：{'、'.join(unknown_refs)}。")

        region_rules = {
            "花溪": {"C001", "C029"},
            "剑河": {"C002", "C029"},
            "松桃": {"C003", "C008", "C032"},
            "雷山": {"C001", "C006", "C007", "C029"},
            "台江": {"C004", "C005", "C029", "C030", "C031"},
            "施秉": {"C005", "C029"},
        }
        for region, accepted_refs in region_rules.items():
            if region not in claim_text:
                continue
            if set(known_refs) & accepted_refs:
                branch_findings.append(f"{region}地域声明有对应来源支持。")
            else:
                conflicts.append(f"提到{region}但缺少对应地域来源。")

        region_hits = [region for region in region_rules if region in claim_text]
        if len(region_hits) > 1:
            if any(term in text for term in ("不混", "分开", "一地一档", "逐项", "对应地区")):
                branch_findings.append("多地域比较已声明分档、不混用边界。")
            else:
                warnings.append("同时涉及多个地域，需在概念图中保持支系分档。")

        exclusive_conflicts = {
            "花溪": ("锡丝", "锡绣", "迷宫式核心", "破线绣", "不打底稿"),
            "剑河": ("花溪挑花", "破线绣", "不打底稿", "心法刺绣"),
            "松桃": ("锡丝", "锡绣", "迷宫式核心", "花溪挑花", "破线绣"),
            "雷山": ("锡丝", "锡绣", "迷宫式核心", "花溪挑花", "不打底稿"),
        }
        if len(region_hits) == 1:
            claimed_region = region_hits[0]
            crossed_terms = [
                term
                for term in exclusive_conflicts[claimed_region]
                if term in claim_text
            ]
            if crossed_terms:
                conflicts.append(
                    f"{claimed_region}地域主张混入其他支系特征：{'、'.join(crossed_terms)}。"
                )

        sensitive_terms = [
            term
            for term in (
                "祖源",
                "祖先",
                "蝴蝶妈妈",
                "鹡宇",
                "姜央",
                "开天辟地",
                "射日月",
                "洪水",
                "史诗",
                "古歌",
                "祭祀",
                "鼓藏",
                "宗教",
            )
            if term in text
        ]
        if sensitive_terms:
            if any(term in text for term in ("核验", "社区", "不拆", "不收录", "仪式")):
                taboo_findings.append(
                    f"识别高敏感语义（{'、'.join(sensitive_terms)}），候选已包含社区核验或禁用约束。"
                )
                warnings.append("高敏感母题即使通过规则核验，进入设计前仍需社区人工复核。")
            else:
                conflicts.append(
                    f"高敏感语义（{'、'.join(sensitive_terms)}）缺少社区核验或禁用边界。"
                )

        matched_records = [
            record
            for record in self._records
            if set(record.source_refs) & set(known_refs)
            or record.culture_name in text
            or any(alias in text for alias in record.aliases)
        ]
        modern_findings = _unique(
            value for record in matched_records for value in record.modern_translations
        )[:8]
        query_terms = _unique(
            value
            for record in matched_records
            for value in [
                record.culture_name,
                *record.aliases,
                *record.symbols,
                *record.patterns,
                *record.crafts,
            ]
            if value and value in text
        )
        if not query_terms and matched_records:
            query_terms = [matched_records[0].culture_name]
        if not query_terms:
            query_terms = ["贵州苗绣"]
            warnings.append("未从候选文本提取到精确文化节点，使用贵州苗绣总节点复核。")

        status = "rejected" if conflicts else ("warning" if warnings else "verified")
        verification = OpportunityVerification(
            status=status,
            retrieval_mode="LightRAG structured KG query",
            queries=query_terms[:8],
            culture_evidence_refs=known_refs,
            branch_region_findings=branch_findings,
            taboo_findings=taboo_findings,
            modern_translation_findings=modern_findings,
            warnings=warnings,
            conflicts=conflicts,
            notes=[f"结构化图谱匹配 {len(matched_records)} 条记录。"],
        )
        return verification, query_terms[0]

    async def query(self, topic: str) -> tuple[CultureDNA, ComponentStatus]:
        dna = self.build_culture_dna(topic)
        if not self.settings.live_mode:
            return dna, ComponentStatus(
                component="culture_knowledge",
                mode="cache",
                engine="QianCraft curated graph",
                ok=True,
                detail=f"结构化图谱命中 {dna.retrieval['records_matched']} 条文化记录；未启动外部运行时。",
            )

        try:
            probe = await self._index_and_probe_lightrag(topic)
            dna.retrieval.update(probe)
            return dna, ComponentStatus(
                component="culture_knowledge",
                mode="live",
                engine="LightRAG local KG",
                ok=True,
                detail=(
                    f"已索引 {probe['indexed_entities']} 个实体、"
                    f"{probe['indexed_relationships']} 条关系；主题节点与边查询成功。"
                ),
            )
        except Exception as exc:  # External runtime must not hide the curated evidence layer.
            dna.retrieval.update({"lightrag_status": "fallback", "error": _safe_error(exc)})
            if not self.settings.demo_mode:
                raise
            return dna, ComponentStatus(
                component="culture_knowledge",
                mode="cache",
                engine="QianCraft curated graph",
                ok=True,
                detail=f"LightRAG 暂不可用，回退结构化图谱：{_safe_error(exc)}",
            )

    async def _index_and_probe_lightrag(self, topic: str) -> dict[str, Any]:
        source_root = self.settings.lightrag_path
        if not (source_root / "lightrag").exists():
            raise FileNotFoundError(f"LightRAG source not found: {source_root}")
        source_text = str(source_root)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)

        from lightrag import LightRAG  # type: ignore
        from lightrag.utils import (  # type: ignore
            normalize_entity_name,
            wrap_embedding_func_with_attrs,
        )

        @wrap_embedding_func_with_attrs(embedding_dim=384, max_token_size=8192)
        async def local_hash_embedding(texts: list[str]) -> np.ndarray:
            return np.vstack([_hash_embedding(text, 384) for text in texts])

        async def no_generation_needed(
            prompt: str,
            system_prompt: str | None = None,
            history_messages: list[dict[str, str]] | None = None,
            **_: Any,
        ) -> str:
            del prompt, system_prompt, history_messages
            return "本查询使用QianCraft已审核的结构化知识图谱，不执行生成式文化事实补写。"

        custom_kg = self._to_custom_kg()
        graph_bytes = self.settings.culture_graph_path.read_bytes()
        graph_hash = hashlib.sha256(graph_bytes).hexdigest()[:12]
        working_dir = (
            self.settings.root_dir / "data" / "culture" / "lightrag_storage" / graph_hash
        )
        working_dir.mkdir(parents=True, exist_ok=True)
        marker = working_dir / ".qiancraft_indexed"

        rag = LightRAG(
            working_dir=str(working_dir),
            workspace="qiancraft_guizhou",
            embedding_func=local_hash_embedding,
            llm_model_func=no_generation_needed,
            llm_model_name="qiancraft-structured-kg",
            enable_llm_cache=False,
        )
        await rag.initialize_storages()
        try:
            if not marker.exists():
                await rag.ainsert_custom_kg(custom_kg, full_doc_id=f"qiancraft-{graph_hash}")
                marker.write_text(graph_hash, encoding="utf-8")

            candidates = [topic, "贵州苗绣", "苗绣"]
            node = None
            matched_name = ""
            for candidate in candidates:
                name = normalize_entity_name(candidate)
                node = await rag.chunk_entity_relation_graph.get_node(name)
                if node:
                    matched_name = name
                    break
            if not node:
                raise RuntimeError("LightRAG index completed but the topic node was not retrievable")
            edges = await rag.chunk_entity_relation_graph.get_node_edges(matched_name)
            return {
                "lightrag_status": "indexed_and_queried",
                "lightrag_workspace": str(working_dir.relative_to(self.settings.root_dir)),
                "dataset_hash": graph_hash,
                "indexed_entities": len(custom_kg["entities"]),
                "indexed_relationships": len(custom_kg["relationships"]),
                "probe_node": matched_name,
                "probe_edge_count": len(edges or []),
            }
        finally:
            await rag.finalize_storages()

    def _to_custom_kg(self) -> dict[str, list[dict[str, Any]]]:
        chunks: list[dict[str, Any]] = []
        entities_by_name: dict[str, dict[str, Any]] = {}
        relationships_by_key: dict[tuple[str, str], dict[str, Any]] = {}

        relation_fields = {
            "region": ("REGION", "流布于", "region,geography"),
            "ethnic_groups": ("COMMUNITY", "由相关社区传承", "community,heritage"),
            "totems": ("TOTEM", "关联图腾", "totem,meaning"),
            "symbols": ("SYMBOL", "使用文化符号", "symbol,visual"),
            "patterns": ("PATTERN", "使用纹样", "pattern,visual"),
            "colors": ("COLOR", "使用色彩", "color,visual"),
            "materials": ("MATERIAL", "使用材料", "material,craft"),
            "crafts": ("TECHNIQUE", "采用技艺", "technique,craft"),
            "objects": ("OBJECT", "体现于器物", "object,usage"),
            "core_values": ("VALUE", "表达价值", "value,semantic"),
            "festivals_rituals": ("CONTEXT", "用于节庆或仪式", "context,ritual"),
        }

        for record in self._records:
            record_content = json.dumps(record.model_dump(), ensure_ascii=False, indent=2)
            chunks.append(
                {
                    "content": record_content,
                    "source_id": record.culture_id,
                    "file_path": "data/culture/knowledge_graph.json",
                    "chunk_order_index": 0,
                }
            )
            entities_by_name[record.culture_name] = {
                "entity_name": record.culture_name,
                "entity_type": "CULTURE",
                "description": _record_summary(record),
                "source_id": record.culture_id,
                "file_path": "data/culture/knowledge_graph.json",
            }

            for alias in record.aliases:
                entities_by_name.setdefault(
                    alias,
                    {
                        "entity_name": alias,
                        "entity_type": "ALIAS",
                        "description": f"{record.culture_name}的别称或检索名。",
                        "source_id": record.culture_id,
                        "file_path": "data/culture/knowledge_graph.json",
                    },
                )
                _add_relationship(
                    relationships_by_key,
                    record.culture_name,
                    alias,
                    "别名",
                    "alias,identity",
                    record.culture_id,
                )

            for field, (entity_type, description, keywords) in relation_fields.items():
                for value in getattr(record, field):
                    entities_by_name.setdefault(
                        value,
                        {
                            "entity_name": value,
                            "entity_type": entity_type,
                            "description": f"与{record.culture_name}相关的{entity_type.lower()}：{value}",
                            "source_id": record.culture_id,
                            "file_path": "data/culture/knowledge_graph.json",
                        },
                    )
                    _add_relationship(
                        relationships_by_key,
                        record.culture_name,
                        value,
                        description,
                        keywords,
                        record.culture_id,
                    )

            for source_id in record.source_refs:
                source = self._sources.get(source_id)
                if not source:
                    continue
                source_name = f"[{source_id}] {source.source_title}"
                entities_by_name.setdefault(
                    source_name,
                    {
                        "entity_name": source_name,
                        "entity_type": "SOURCE",
                        "description": f"{source.publisher}：{source.source_url}",
                        "source_id": record.culture_id,
                        "file_path": "data/culture/knowledge_graph.json",
                    },
                )
                _add_relationship(
                    relationships_by_key,
                    record.culture_name,
                    source_name,
                    "由来源支持",
                    "evidence,source",
                    record.culture_id,
                )

        return {
            "chunks": chunks,
            "entities": list(entities_by_name.values()),
            "relationships": list(relationships_by_key.values()),
        }


def _unique_records(records: Iterable[CultureRecord]) -> list[CultureRecord]:
    seen: set[str] = set()
    result: list[CultureRecord] = []
    for record in records:
        if record.culture_id not in seen:
            seen.add(record.culture_id)
            result.append(record)
    return result


def _add_relationship(
    target: dict[tuple[str, str], dict[str, Any]],
    source: str,
    destination: str,
    description: str,
    keywords: str,
    evidence_alias: str,
) -> None:
    if source == destination:
        return
    key = tuple(sorted((source, destination)))
    target[key] = {
        "src_id": source,
        "tgt_id": destination,
        "description": description,
        "keywords": keywords,
        "source_id": evidence_alias,
        "weight": 1.0,
        "file_path": "data/culture/knowledge_graph.json",
    }


def _record_summary(record: CultureRecord) -> str:
    parts = [
        f"{record.culture_name}（{record.category}）",
        f"地域：{'、'.join(record.region)}" if record.region else "",
        f"社区：{'、'.join(record.ethnic_groups)}" if record.ethnic_groups else "",
        f"价值：{'、'.join(record.core_values[:8])}" if record.core_values else "",
        f"来源：{'、'.join(record.source_refs)}",
    ]
    return "；".join(part for part in parts if part)


def _hash_embedding(text: str, dimensions: int) -> np.ndarray:
    vector = np.zeros(dimensions, dtype=np.float32)
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    units = re.findall(r"[\u3400-\u9fff]|[a-z0-9_]+", normalized)
    features = [*units, *(f"{units[i]}::{units[i + 1]}" for i in range(len(units) - 1))]
    for feature in features or [normalized or "empty"]:
        digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        number = int.from_bytes(digest, "big")
        index = number % dimensions
        sign = -1.0 if number & (1 << 63) else 1.0
        vector[index] += sign
    norm = math.sqrt(float(np.dot(vector, vector)))
    if norm:
        vector /= norm
    return vector


def _safe_error(exc: Exception) -> str:
    message = re.sub(r"sk-[A-Za-z0-9_-]+", "<redacted>", str(exc))
    return f"{type(exc).__name__}: {message[:500]}"
