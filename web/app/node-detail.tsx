'use client';

/* eslint-disable @next/next/no-img-element */

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  CornerDownRight,
  Download,
  ExternalLink,
  Play,
  SlidersHorizontal,
} from 'lucide-react';

import {
  API_BASE,
  activateConcept,
  duplicateConcept,
  generateMoreConcept,
  getBootstrap,
  getDesignPackage,
  getNodeDetail,
  regenerateConcept,
  runNode,
  saveDesignBrief,
  saveWorkspace,
} from './workbench-api';
import {
  NODE_TYPE_LABELS,
  STATUS_LABELS,
  apiAssetUrl,
  displayNodeSummary,
  orderedRunNodeIds,
  updatePosterSection,
  type DesignBrief,
  type EvidenceCitation,
  type MarketPostSummary,
  type NodeDetailPayload,
  type OpportunityDetail,
  type PosterConfig,
  type WorkbenchNode,
  type WorkbenchNodeType,
} from './workbench-model';

const PLATFORM_LABELS: Record<string, string> = {
  xhs: '小红书',
  dy: '抖音',
  bili: 'B站',
  wb: '微博',
};

const NODE_DECISION_STAGE: Record<WorkbenchNodeType, string> = {
  CultureGraphNode: 'culture',
  MarketRadarNode: 'market',
  StrategyNode: 'score',
  DesignBriefNode: 'brief',
  VisualGenerationNode: 'visual',
  ConceptNode: 'concept',
  PosterBoardNode: 'poster',
};

const POSTER_SECTION_LABELS: Record<string, string> = {
  hero: '成品主视觉',
  culture: '文化元素与转译',
  breakdown: '结构拆解',
  bom: '用料 / BOM',
  process: '工艺路径',
};

const SCORE_FIELDS: Array<[keyof OpportunityDetail, string]> = [
  ['culture_fit', '文化适配'],
  ['market_pull', '市场拉力'],
  ['novelty', '原创空间'],
  ['visual_potential', '视觉潜力'],
  ['social_shareability', '社交传播'],
  ['product_feasibility', '产品可行'],
];

const FACT_LABELS: Record<string, string> = {
  product_name: '产品名称',
  product_type: '产品形态',
  prototype_level: '样品阶段',
  target_audience: '目标人群',
  concept_statement: '概念说明',
  form_description: '结构说明',
  target_weight_g: '目标重量',
  assembly_steps: '装配步骤',
  quality_checks: '质检项目',
  bill_of_materials: '用料清单',
};

function verificationLabel(value: string): string {
  if (value === 'verified') return '已核验';
  if (value === 'warning') return '待复核';
  if (value === 'rejected') return '已排除';
  return value;
}

function rightsLabel(value: string): string {
  if (value === 'reference_only') return '仅作研究参考';
  if (value === 'public_source') return '公开来源';
  return value;
}

function evidenceKindLabel(value: string): string {
  const labels: Record<string, string> = {
    culture: '文化来源',
    market: '市场来源',
    market_post: '平台记录',
    visual_reference: '视觉参考',
    legal: '法律与规范',
  };
  return labels[value] ?? value.replaceAll('_', ' ');
}

function platformStatusLabel(value: string): string {
  if (value === 'live') return '实时';
  if (value === 'cache' || value === 'cached') return '历史快照';
  if (value === 'unavailable') return '不可用';
  return value;
}

function factValueLabel(key: string, value: unknown): string {
  if (key === 'prototype_level' && value === 'appearance_and_structure_sample') return '外观与结构首样';
  return text(value);
}

function providerLabel(value: string | undefined): string {
  return value && value !== 'unconfigured' ? value : '未配置';
}

type Tone = 'neutral' | 'success' | 'error';
type Notice = { tone: Tone; text: string } | null;
type JsonRecord = Record<string, unknown>;

function asRecord(value: unknown): JsonRecord {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as JsonRecord)
    : {};
}

function asRecords(value: unknown): JsonRecord[] {
  return Array.isArray(value)
    ? (value.filter((item) => item && typeof item === 'object') as JsonRecord[])
    : [];
}

function asStrings(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String).filter(Boolean) : [];
}

function text(value: unknown, fallback = '—'): string {
  if (value === null || value === undefined || value === '') return fallback;
  return String(value);
}

function number(value: unknown): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatMetric(value: number): string {
  return new Intl.NumberFormat('zh-CN', { notation: value >= 10000 ? 'compact' : 'standard' }).format(value);
}

function saveJson(payload: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function TagList({ values }: { values: string[] }) {
  if (!values.length) return <p className="detail-empty">暂无结构化条目</p>;
  return <div className="detail-tags">{values.map((item) => <span key={item}>{item}</span>)}</div>;
}

function CitationBadges({ refs }: { refs: string[] }) {
  return <div className="citation-badges">{refs.map((ref) => <a href={`#citation-${ref}`} key={ref}>[{ref}]</a>)}</div>;
}

function CitationLedger({ citations, audit }: { citations: EvidenceCitation[]; audit: NodeDetailPayload['citationAudit'] }) {
  return (
    <section className="citation-ledger" id="citations">
      <header className="detail-section-heading">
        <div><h2>引用与证据台账</h2></div>
        <p><strong>{audit.resolved}</strong> / {audit.requested} 条引用已解析</p>
      </header>
      {audit.missing.length ? <div className="citation-warning">未解析引用：{audit.missing.join('、')}</div> : null}
      <div className="citation-grid">
        {citations.map((citation) => (
          <article id={`citation-${citation.id}`} key={citation.id}>
            <header><code>{citation.id}</code><span>{evidenceKindLabel(citation.kind)}</span></header>
            <h3>{citation.title}</h3>
            <p>{citation.publisher || citation.sourceType}</p>
            <dl>
              {citation.publishedAt ? <div><dt>发布</dt><dd>{citation.publishedAt}</dd></div> : null}
              {citation.retrievedAt ? <div><dt>检索</dt><dd>{citation.retrievedAt}</dd></div> : null}
              <div><dt>权利</dt><dd title={citation.rightsStatus}>{rightsLabel(citation.rightsStatus)}</dd></div>
            </dl>
            <TagList values={citation.supports.slice(0, 4)} />
            {citation.rightsNote ? <small>{citation.rightsNote}</small> : null}
            {citation.url ? <a className="citation-link" href={citation.url} target="_blank" rel="noreferrer">查看原始来源 ↗</a> : <span className="citation-link is-disabled">未登记公开链接</span>}
          </article>
        ))}
      </div>
    </section>
  );
}

function CultureDetail({ records, citations }: { records: JsonRecord[]; citations: EvidenceCitation[] }) {
  const [selectedId, setSelectedId] = useState(text(records[0]?.culture_id, ''));
  const selected = records.find((record) => text(record.culture_id, '') === selectedId) ?? records[0];
  const sourceMap = useMemo(() => new Map(citations.map((item) => [item.id, item])), [citations]);
  if (!selected) return <p className="detail-empty">文化图谱暂无记录。</p>;
  return (
    <>
      <section className="culture-detail-layout">
        <div className="culture-graph-board">
          <div className="culture-graph-core"><span>贵州</span><strong>在地文化</strong><small>{records.length} 条知识记录</small></div>
          <svg aria-hidden="true" viewBox="0 0 760 590" preserveAspectRatio="none">
            {records.slice(0, 16).map((_, index) => {
              const x = 80 + (index % 4) * 200;
              const y = 82 + Math.floor(index / 4) * 142;
              return <line key={index} x1="380" y1="295" x2={x} y2={y} />;
            })}
          </svg>
          <div className="culture-node-grid">
            {records.slice(0, 16).map((record) => {
              const id = text(record.culture_id, '');
              return <button className={id === text(selected.culture_id, '') ? 'is-active' : ''} key={id} type="button" onClick={() => setSelectedId(id)}><span>{text(record.category, '文化')}</span><strong>{text(record.culture_name)}</strong><small>{asStrings(record.source_refs).length} 条引用</small></button>;
            })}
          </div>
        </div>
        <article className="culture-record-panel">
          <header><span>{text(selected.category, '在地文化')}</span><code>{text(selected.culture_id)}</code></header>
          <h2>{text(selected.culture_name)}</h2>
          <p className="record-lead">{asStrings(selected.history)[0] ?? '已进入结构化文化知识图谱。'}</p>
          <div className="record-block"><h3>地域与支系</h3><TagList values={asStrings(selected.region)} /></div>
          <div className="record-block"><h3>工艺</h3><TagList values={asStrings(selected.crafts)} /></div>
          <div className="record-block"><h3>纹样 / 结构</h3><TagList values={asStrings(selected.patterns)} /></div>
          <div className="record-block"><h3>可转译方向</h3><TagList values={asStrings(selected.modernizable_elements)} /></div>
          <div className="record-block record-block--boundary"><h3>文化边界</h3>{asStrings(selected.cultural_taboos).map((item) => <p key={item}>{item}</p>)}</div>
          <CitationBadges refs={asStrings(selected.source_refs).filter((ref) => sourceMap.has(ref))} />
        </article>
      </section>
      <section className="detail-data-section">
        <header className="detail-section-heading"><div><h2>全部文化记录</h2></div><p>按地域、工艺与引用独立检索</p></header>
        <div className="record-index-grid">
          {records.map((record) => <button key={text(record.culture_id)} type="button" onClick={() => { setSelectedId(text(record.culture_id, '')); window.scrollTo({ top: 150, behavior: 'smooth' }); }}><span>{text(record.category, '在地文化')}</span><h3>{text(record.culture_name)}</h3><p>{asStrings(record.region).slice(0, 3).join(' · ')}</p><CitationBadges refs={asStrings(record.source_refs).slice(0, 5)} /></button>)}
        </div>
      </section>
    </>
  );
}

function MarketDetail({ detail }: { detail: NodeDetailPayload }) {
  const ranking = detail.content.ranking ?? [];
  const posts = detail.content.representativePosts ?? [];
  const platforms = detail.content.platforms ?? {};
  const [platform, setPlatform] = useState('all');
  const visiblePosts = platform === 'all' ? posts : posts.filter((post) => post.platform === platform);
  return (
    <>
      <section className="market-kpi-row">
        <div><span>历史样本</span><strong>{detail.content.sampleSize ?? 0}</strong><small>真实历史记录，不标成实时趋势</small></div>
        {Object.entries(platforms).map(([code, value]) => <div key={code}><span>{PLATFORM_LABELS[code] ?? code}</span><strong>{value.sample_size}</strong><small>{platformStatusLabel(value.status)}</small></div>)}
      </section>
      <section className="market-detail-grid">
        <div className="ranking-board">
          <header className="detail-section-heading"><div><h2>爆款形态排序</h2></div><p>跨平台热度为派生分，不是平台官方口径</p></header>
          {ranking.map((raw, index) => {
            const scores = asRecord(raw.platform_scores);
            return <article key={text(raw.product_form, String(index))}><b>{String(index + 1).padStart(2, '0')}</b><div><h3>{text(raw.product_form)}</h3><p>{asStrings(raw.why_hot).join('；')}</p><div className="platform-score-strip">{Object.entries(scores).map(([code, score]) => <span key={code}>{PLATFORM_LABELS[code] ?? code}<i style={{ width: `${Math.min(100, number(score))}%` }} /><em>{number(score).toFixed(1)}</em></span>)}</div></div><strong>{number(raw.cross_platform_hot_score).toFixed(1)}</strong></article>;
          })}
        </div>
        <aside className="market-method-card"><h2>评分方法</h2><p>综合平台内热度、样本占比、平台覆盖与近期性，仅用于这批有限样本的相对比较。</p><details><summary>查看字段说明</summary><pre>{JSON.stringify(detail.content.methodology ?? {}, null, 2)}</pre></details><small>生成于 {detail.content.generatedAt || '—'}</small></aside>
      </section>
      <section className="detail-data-section">
        <header className="detail-section-heading"><div><h2>已采集代表记录</h2></div><nav><button className={platform === 'all' ? 'is-active' : ''} type="button" onClick={() => setPlatform('all')}>全部</button>{Object.keys(platforms).map((code) => <button className={platform === code ? 'is-active' : ''} key={code} type="button" onClick={() => setPlatform(code)}>{PLATFORM_LABELS[code] ?? code}</button>)}</nav></header>
        <div className="market-post-grid">{visiblePosts.map((post) => <MarketPostCard key={post.sourceRef} post={post} />)}</div>
      </section>
    </>
  );
}

function MarketPostCard({ post }: { post: MarketPostSummary }) {
  return <article><header><span>{PLATFORM_LABELS[post.platform] ?? post.platform}</span><code>{post.sourceRef}</code></header><h3>{post.title || '无标题平台记录'}</h3><p>{post.productForm} · {post.searchKeyword}</p><div className="post-metrics"><span>赞 <b>{formatMetric(post.engagement.likes)}</b></span><span>藏 <b>{formatMetric(post.engagement.favorites)}</b></span><span>评 <b>{formatMetric(post.engagement.comments)}</b></span><span>转 <b>{formatMetric(post.engagement.shares)}</b></span></div><div className="post-score"><span>平台内热度</span><i><em style={{ width: `${Math.min(100, post.platformHotScore)}%` }} /></i><strong>{post.platformHotScore.toFixed(1)}</strong></div><small>{post.qualityReasons.join('；')}</small>{post.url ? <a href={post.url} target="_blank" rel="noreferrer">查看平台原记录 ↗</a> : null}</article>;
}

function StrategyDetail({ opportunities }: { opportunities: OpportunityDetail[] }) {
  const [selectedId, setSelectedId] = useState(opportunities[0]?.opportunity_id ?? '');
  const selected = opportunities.find((item) => item.opportunity_id === selectedId) ?? opportunities[0];
  if (!selected) return <p className="detail-empty">暂无评分机会。</p>;
  return (
    <section className="strategy-detail-layout">
      <div className="opportunity-list"><header><h2>机会量分</h2><p>同一权重、同一风险扣分规则下比较</p></header>{opportunities.map((item, index) => <button className={item.opportunity_id === selected.opportunity_id ? 'is-active' : ''} key={item.opportunity_id} type="button" onClick={() => setSelectedId(item.opportunity_id)}><b>{String(index + 1).padStart(2, '0')}</b><div><span>{item.opportunity_id} · {verificationLabel(item.verification.status)}</span><strong>{item.culture_element}</strong><small>{item.trend_element}</small></div><em>{item.overall_score}</em></button>)}</div>
      <article className="opportunity-detail-card"><header><div><span>{selected.opportunity_id} · {verificationLabel(selected.verification.status)}</span><h2>{selected.culture_element}<br />× {selected.trend_element}</h2></div><strong>{selected.overall_score}</strong></header><p className="opportunity-reason">{selected.match_reason}</p><div className="score-breakdown">{SCORE_FIELDS.map(([key, label]) => <div key={String(key)}><span>{label}</span><i><em style={{ width: `${number(selected[key])}%` }} /></i><strong>{number(selected[key])}</strong></div>)}<div className="is-risk"><span>文化风险</span><i><em style={{ width: `${number(selected.cultural_risk) * 10}%` }} /></i><strong>{selected.cultural_risk}</strong></div></div><section><h3>产品方向</h3><TagList values={selected.potential_product_categories} /></section><section><h3>设计关键词</h3><TagList values={selected.design_keywords} /></section><section className="boundary-card"><h3>文化约束</h3>{selected.cultural_constraints.map((item) => <p key={item}>{item}</p>)}</section><p className="formula-note">{selected.reason}</p><CitationBadges refs={selected.evidence_refs} /></article>
    </section>
  );
}

function BriefDetail({ draft, setDraft, onSave, busy, detail }: { draft: DesignBrief; setDraft: (value: DesignBrief) => void; onSave: () => void; busy: boolean; detail: NodeDetailPayload }) {
  return <section className="brief-detail-layout"><form className="detail-editor" onSubmit={(event) => { event.preventDefault(); onSave(); }}><header><h2>编辑设计任务书</h2><p>保存后只把下游标记为待更新，不自动调用外部服务。</p></header><label><span>方案标题</span><input value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} /></label><label><span>设计目标</span><textarea rows={5} value={draft.objective} onChange={(event) => setDraft({ ...draft, objective: event.target.value })} /></label><div className="editor-columns"><label><span>目标人群</span><input value={draft.audience} onChange={(event) => setDraft({ ...draft, audience: event.target.value })} /></label><label><span>产品形态</span><input value={draft.productType} onChange={(event) => setDraft({ ...draft, productType: event.target.value })} /></label></div><label><span>使用场景（每行一项）</span><textarea rows={4} value={draft.scenarios.join('\n')} onChange={(event) => setDraft({ ...draft, scenarios: event.target.value.split('\n').filter(Boolean) })} /></label><label><span>视觉风格（每行一项）</span><textarea rows={4} value={draft.style.join('\n')} onChange={(event) => setDraft({ ...draft, style: event.target.value.split('\n').filter(Boolean) })} /></label><label><span>设计与文化约束（每行一项）</span><textarea rows={7} value={draft.constraints.join('\n')} onChange={(event) => setDraft({ ...draft, constraints: event.target.value.split('\n').filter(Boolean) })} /></label><label><span>工厂边界</span><textarea rows={3} value={draft.factoryBoundary} onChange={(event) => setDraft({ ...draft, factoryBoundary: event.target.value })} /></label><button className="detail-primary" disabled={busy} type="submit">保存新版本</button></form><aside className="brief-context"><h2>固定输入与审核门</h2><h3>当前产品</h3><JsonFacts data={detail.content.product ?? {}} /><h3>文化审核</h3>{(detail.content.reviewGates ?? []).map((item) => <p key={item}>{item}</p>)}<h3>工程审核</h3>{(detail.content.engineeringGates ?? []).map((item) => <p key={item}>{item}</p>)}</aside></section>;
}

function VisualDetail({ detail, onOpen }: { detail: NodeDetailPayload; onOpen: (id: string) => void }) {
  const provider = detail.content.provider;
  const concepts = detail.content.concepts ?? [];
  const providerSummary = provider?.configured
    ? '服务已连接，可按当前任务书继续生成。'
    : '当前展示视觉可用；重新生成前需配置独立图像服务。';
  return <><section className="visual-provider-hero"><div><h2>{provider?.configured ? '图像生成服务已就绪' : '展示视觉已就绪'}</h2><p>{providerSummary}</p></div><dl><div><dt>服务</dt><dd>{providerLabel(provider?.provider)}</dd></div><div><dt>模型</dt><dd>{provider?.model || '—'}</dd></div><div><dt>尺寸</dt><dd>{text(detail.node.data.size, '1024×1024')}</dd></div></dl></section><section className="concept-gallery"><header className="detail-section-heading"><div><h2>视觉方向 A / B / C</h2></div><p>每个方向均可独立编辑和运行</p></header><div>{concepts.map((concept) => <ConceptTile key={concept.id} concept={concept} onOpen={onOpen} />)}</div></section><section className="prompt-ledger"><header className="detail-section-heading"><div><h2>生成提示词版本</h2></div></header>{(detail.content.prompts ?? []).map((prompt, index) => <article key={`${index}-${prompt.slice(0, 12)}`}><b>{String.fromCharCode(65 + index)}</b><p>{prompt}</p></article>)}</section></>;
}

function ConceptTile({ concept, onOpen }: { concept: WorkbenchNode; onOpen: (id: string) => void }) {
  const image = apiAssetUrl(concept.data.imageUrl, API_BASE);
  return <article className={concept.data.active ? 'is-active' : ''}>{image ? <img src={image} alt={`${concept.data.title} 概念视觉`} /> : <div className="concept-placeholder">等待图像服务</div>}<div><span>{text(concept.data.label, '概念方向')}</span><h3>{concept.data.title}</h3><p>{text(concept.data.direction, concept.data.summary)}</p><button type="button" onClick={() => onOpen(concept.id)}>进入独立概念页 ↗</button></div></article>;
}

function ConceptDetail({ detail, draft, setDraft, onSave, onAction, busy }: { detail: NodeDetailPayload; draft: { title: string; summary: string; direction: string; prompt: string }; setDraft: (value: { title: string; summary: string; direction: string; prompt: string }) => void; onSave: () => void; onAction: (action: 'activate' | 'duplicate' | 'regenerate' | 'generate-more') => void; busy: boolean }) {
  const image = apiAssetUrl(detail.node.data.imageUrl, API_BASE);
  const manufacturing = detail.content.manufacturing ?? {};
  const bom = asRecords(manufacturing.bill_of_materials);
  return <><section className="concept-detail-hero"><div className="concept-detail-image">{image ? <img src={image} alt={`${detail.node.data.title} 文创成品概念`} /> : <div className="concept-placeholder">当前方向尚无生成图</div>}<span>{detail.node.data.active ? '当前采用' : '候选方案'}</span></div><form className="detail-editor" onSubmit={(event) => { event.preventDefault(); onSave(); }}><header><h2>编辑概念方向</h2></header><label><span>概念标题</span><input value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} /></label><label><span>概念说明</span><textarea rows={4} value={draft.summary} onChange={(event) => setDraft({ ...draft, summary: event.target.value })} /></label><label><span>视觉方向</span><textarea rows={3} value={draft.direction} onChange={(event) => setDraft({ ...draft, direction: event.target.value })} /></label><label><span>图像生成提示词</span><textarea rows={9} value={draft.prompt} onChange={(event) => setDraft({ ...draft, prompt: event.target.value })} /></label><button className="detail-primary" disabled={busy} type="submit">保存概念编辑</button><div className="detail-action-grid"><button disabled={busy || Boolean(detail.node.data.active)} type="button" onClick={() => onAction('activate')}>设为当前方向</button><button disabled={busy} type="button" onClick={() => onAction('duplicate')}>复制方向</button><button disabled={busy} type="button" onClick={() => onAction('regenerate')}>单独重生成</button><button disabled={busy} type="button" onClick={() => onAction('generate-more')}>生成更多方向</button></div></form></section><section className="detail-data-section"><header className="detail-section-heading"><div><h2>文化元素与转译规则</h2></div></header><div className="culture-element-grid">{(detail.content.culturalElements ?? []).map((item, index) => <article key={text(item.element_id, String(index))}><code>{text(item.element_id, `E-${index + 1}`)}</code><h3>{text(item.name)}</h3><p>{text(item.transformation_rule)}</p><TagList values={asStrings(item.evidence_refs)} /></article>)}</div></section><section className="detail-data-section"><header className="detail-section-heading"><div><h2>BOM 与加工拆解</h2></div><p>仅用于询价与首样沟通</p></header><div className="bom-table"><div className="bom-row bom-row--head"><span>编号</span><span>部件</span><span>材料</span><span>工艺</span><span>尺寸 / 验收</span></div>{bom.map((item, index) => <div className="bom-row" key={text(item.item_id, String(index))}><code>{text(item.item_id, String(index + 1))}</code><strong>{text(item.component)}</strong><span>{text(item.material)}</span><span>{text(item.process)}</span><small>{text(item.dimension)}<br />{text(item.quality_check)}</small></div>)}</div></section></>;
}

function PosterDetail({ detail, draft, setDraft, onSave, busy }: { detail: NodeDetailPayload; draft: PosterConfig; setDraft: (value: PosterConfig) => void; onSave: () => void; busy: boolean }) {
  const image = apiAssetUrl(detail.node.data.imageUrl, API_BASE);
  const activeImage = apiAssetUrl(detail.content.activeConcept?.data.imageUrl, API_BASE);
  const manufacturing = detail.content.manufacturing ?? {};
  return <><section className="poster-detail-layout"><div className="poster-artboard">{image ? <img src={image} alt="QianCraft 完整设计海报" /> : activeImage ? <img src={activeImage} alt="当前概念视觉" /> : null}{!image ? <div className="poster-artboard-label"><span>QianCraft · 概念提案</span><strong>{draft.title}</strong><p>{draft.subtitle}</p></div> : null}</div><form className="detail-editor" onSubmit={(event) => { event.preventDefault(); onSave(); }}><header><h2>编辑海报内容</h2></header><label><span>标题</span><input value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} /></label><label><span>副标题</span><textarea rows={4} value={draft.subtitle} onChange={(event) => setDraft({ ...draft, subtitle: event.target.value })} /></label><fieldset><legend>展示板块</legend>{draft.sections.map((section) => <label className="section-toggle" key={section}><input checked={!draft.hiddenSections.includes(section)} type="checkbox" onChange={(event) => setDraft(updatePosterSection(draft, section, event.target.checked))} /><span>{POSTER_SECTION_LABELS[section] ?? section}</span></label>)}</fieldset><button className="detail-primary" disabled={busy} type="submit">保存海报版式</button>{image ? <a className="detail-download" href={image} download>下载项目海报 PNG</a> : null}</form></section><section className="poster-breakdown-grid"><article><h3>{draft.cultureElement}</h3><p>{draft.cultureRule}</p></article><article><h3>用料方向</h3>{draft.materials.map((item) => <p key={item}>{item}</p>)}</article><article><h3>加工路径</h3>{draft.process.map((item, index) => <p key={item}><b>{index + 1}</b>{item}</p>)}</article><article className="is-boundary"><h3>当前边界</h3><p>{draft.boundary}</p></article></section><section className="detail-data-section"><header className="detail-section-heading"><div><h2>工厂沟通信息</h2></div></header><JsonFacts data={manufacturing} /></section></>;
}

function JsonFacts({ data }: { data: JsonRecord }) {
  const entries = Object.entries(data).filter(([, value]) => ['string', 'number', 'boolean'].includes(typeof value)).slice(0, 14);
  if (!entries.length) return <pre className="json-facts-pre">{JSON.stringify(data, null, 2)}</pre>;
  return <dl className="json-facts">{entries.map(([key, value]) => <div key={key}><dt title={key}>{FACT_LABELS[key] ?? key.replaceAll('_', ' ')}</dt><dd>{factValueLabel(key, value)}</dd></div>)}</dl>;
}

export default function NodeDetail({ nodeId, workspaceId }: { nodeId: string; workspaceId: string }) {
  const [detail, setDetail] = useState<NodeDetailPayload | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<Notice>(null);
  const [briefDraft, setBriefDraft] = useState<DesignBrief | null>(null);
  const [conceptDraft, setConceptDraft] = useState({ title: '', summary: '', direction: '', prompt: '' });
  const [posterDraft, setPosterDraft] = useState<PosterConfig | null>(null);

  const load = useCallback(async () => {
    try {
      setError('');
      const next = await getNodeDetail(workspaceId, nodeId);
      setDetail(next);
      setBriefDraft(next.content.brief ?? next.node.data.brief ?? null);
      setPosterDraft(next.content.poster ?? next.node.data.poster ?? null);
      setConceptDraft({ title: next.node.data.title, summary: next.node.data.summary, direction: text(next.node.data.direction, ''), prompt: text(next.node.data.prompt, '') });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  }, [nodeId, workspaceId]);

  useEffect(() => {
    const initialLoad = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(initialLoad);
  }, [load]);

  const act = useCallback(async (operation: () => Promise<unknown>, success: string) => {
    if (busy) return;
    setBusy(true);
    setNotice(null);
    try {
      await operation();
      await load();
      setNotice({ tone: 'success', text: success });
    } catch (reason) {
      setNotice({ tone: 'error', text: reason instanceof Error ? reason.message : String(reason) });
    } finally { setBusy(false); }
  }, [busy, load]);

  if (!detail) return <main className="node-detail-loading"><div>Q</div><span>{error ? '载入失败' : '正在读取证据'}</span><h1>{error || '正在装载节点页面'}</h1>{error ? <button type="button" onClick={() => void load()}>重新连接</button> : null}</main>;

  const node = detail.node;
  const nodeLabel = NODE_TYPE_LABELS[node.type];
  const runCurrent = () => act(() => runNode(workspaceId, node.id), '当前节点已独立运行完成。');
  const runFromHere = () => act(async () => {
    const bootstrap = await getBootstrap(workspaceId);
    for (const id of orderedRunNodeIds(bootstrap.workspace.nodes, bootstrap.workspace.edges, node.id)) await runNode(workspaceId, id);
  }, '已按依赖顺序运行当前节点与下游。');
  const saveBriefDraft = () => briefDraft ? act(() => saveDesignBrief(workspaceId, briefDraft), '设计任务书已保存为新版本。') : undefined;
  const saveCurrentNode = (data: JsonRecord, success: string) => act(async () => {
    const bootstrap = await getBootstrap(workspaceId);
    const requestedStatus = typeof data.status === 'string' ? data.status : 'stale';
    const nodes = bootstrap.workspace.nodes.map((item) => item.id === node.id ? { ...item, data: { ...item.data, ...data, status: requestedStatus, history: [{ at: new Date().toISOString(), event: success }, ...(item.data.history ?? [])] } } : item) as WorkbenchNode[];
    await saveWorkspace({ ...bootstrap.workspace, nodes, selected_node_id: node.id });
  }, success);
  const conceptAction = (mode: 'activate' | 'duplicate' | 'regenerate' | 'generate-more') => {
    if (mode === 'duplicate' || mode === 'generate-more') {
      if (busy) return;
      setBusy(true);
      const request = mode === 'duplicate'
        ? duplicateConcept(workspaceId, node.id)
        : generateMoreConcept(workspaceId, node.id);
      void request.then((workspace) => { window.location.assign(`/nodes/${encodeURIComponent(workspace.selected_node_id)}?workspace=${encodeURIComponent(workspaceId)}`); }).catch((reason) => setNotice({ tone: 'error', text: reason instanceof Error ? reason.message : String(reason) })).finally(() => setBusy(false));
    } else {
      const operation = mode === 'activate'
        ? () => activateConcept(workspaceId, node.id)
        : () => regenerateConcept(workspaceId, node.id);
      void act(operation, mode === 'activate' ? '已设为海报当前概念。' : '概念重生成操作已完成。');
    }
  };

  return (
    <main className={`node-detail-page node-detail-page--${node.type}`}>
      <header className="detail-topbar">
        <Link className="detail-brand" href={`/?workspace=${encodeURIComponent(workspaceId)}`} aria-label="返回 QianCraft 工作台">
          <ArrowLeft aria-hidden="true" size={16} strokeWidth={1.8} />
          <b>Q</b>
          <strong>QianCraft</strong>
        </Link>
        <div className="detail-breadcrumb">
          <Link href={`/?workspace=${encodeURIComponent(workspaceId)}`}>工作台</Link>
          <i>/</i>
          <span>{nodeLabel}</span>
          <i>/</i>
          <strong>{node.data.title}</strong>
        </div>
        <div className="detail-top-actions">
          <Link aria-label="打开人工决策" className="detail-decision-link" href={`/?workspace=${encodeURIComponent(workspaceId)}&decision=${NODE_DECISION_STAGE[node.type]}`}>
            <SlidersHorizontal aria-hidden="true" size={14} />
            <span>人工决策</span>
          </Link>
          <button aria-label="运行当前节点" className="detail-run-button" disabled={busy} type="button" onClick={runCurrent}>
            <Play aria-hidden="true" size={14} fill="currentColor" />
            <span>运行当前</span>
          </button>
          <button aria-label="从当前节点开始运行" disabled={busy} type="button" onClick={runFromHere}>
            <CornerDownRight aria-hidden="true" size={14} />
            <span>从此处运行</span>
          </button>
          <button aria-label="导出当前节点数据" type="button" onClick={() => saveJson(detail, `QianCraft-${node.id}-detail.json`)}>
            <Download aria-hidden="true" size={14} />
            <span>导出数据</span>
          </button>
        </div>
      </header>

      <section className="detail-hero"><div className={`detail-node-mark detail-node-mark--${node.type}`}>{node.type === 'ConceptNode' ? text(node.data.label, 'C').slice(-1) : node.data.eyebrow.slice(0, 1)}</div><div><h1>{node.data.title}</h1><p>{displayNodeSummary(node.type, node.data.summary)}</p><div className="hero-meta"><em className={`is-${node.data.status}`}>{STATUS_LABELS[node.data.status]}</em><a href="#citations">{detail.citationAudit.resolved} 条引用</a><span>概念视觉 · 首样沟通前</span><details className="hero-run-details"><summary>运行信息</summary><div><span>工作区：{detail.workspace.name}</span><span>运行：{detail.workspace.sourceRunId || '未登记'}</span></div></details></div></div></section>

      <nav className="detail-related" aria-label="相关节点"><span>关联节点</span>{detail.relatedNodes.map((item) => <Link href={`/nodes/${encodeURIComponent(item.id)}?workspace=${encodeURIComponent(workspaceId)}`} key={item.id}><i className={`is-${item.status}`} /><small>{item.relation === 'upstream' ? '输入' : '下游'}</small><strong>{item.title}</strong><ExternalLink aria-hidden="true" size={13} /></Link>)}</nav>

      <div className="detail-content">
        {node.type === 'CultureGraphNode' ? <CultureDetail records={(detail.content.records ?? []) as JsonRecord[]} citations={detail.citations} /> : null}
        {node.type === 'MarketRadarNode' ? <MarketDetail detail={detail} /> : null}
        {node.type === 'StrategyNode' ? <StrategyDetail opportunities={detail.content.opportunities ?? []} /> : null}
        {node.type === 'DesignBriefNode' && briefDraft ? <BriefDetail draft={briefDraft} setDraft={setBriefDraft} onSave={saveBriefDraft} busy={busy} detail={detail} /> : null}
        {node.type === 'VisualGenerationNode' ? <VisualDetail detail={detail} onOpen={(id) => window.location.assign(`/nodes/${encodeURIComponent(id)}?workspace=${encodeURIComponent(workspaceId)}`)} /> : null}
        {node.type === 'ConceptNode' ? <ConceptDetail detail={detail} draft={conceptDraft} setDraft={setConceptDraft} onSave={() => saveCurrentNode({ ...conceptDraft }, '保存概念文本与生成参数；等待重生成')} onAction={conceptAction} busy={busy} /> : null}
        {node.type === 'PosterBoardNode' && posterDraft ? <PosterDetail detail={detail} draft={posterDraft} setDraft={setPosterDraft} onSave={() => saveCurrentNode({ title: posterDraft.title, summary: posterDraft.subtitle, poster: posterDraft, status: 'success' }, '保存海报标题与板块配置')} busy={busy} /> : null}
        <CitationLedger citations={detail.citations} audit={detail.citationAudit} />
      </div>

      <footer className="detail-footer"><div><strong>QianCraft</strong><span>有据可查的文化文创设计</span></div><p>文化事实、市场记录、策略推导与设计假设分层展示；引用可回到原始来源。</p><button type="button" onClick={() => void act(() => getDesignPackage().then((payload) => saveJson(payload, 'QianCraft-DesignPackage.json')), 'DesignPackage 已导出。')}>下载 DesignPackage</button></footer>
      {notice ? <div className={`detail-notice detail-notice--${notice.tone}`}>{notice.text}</div> : null}
    </main>
  );
}
