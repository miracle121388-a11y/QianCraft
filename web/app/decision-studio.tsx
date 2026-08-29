/* eslint-disable @next/next/no-img-element */
'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { Search, X } from 'lucide-react';

import { API_BASE } from './workbench-api';
import {
  DECISION_SCORE_FIELDS,
  apiAssetUrl,
  calculateManualOpportunityScore,
  toggleDecisionSelection,
  type DecisionCatalog,
  type DecisionProfile,
  type DecisionScoreField,
} from './workbench-model';

export type DecisionStage =
  | 'culture'
  | 'market'
  | 'score'
  | 'brief'
  | 'visual'
  | 'concept'
  | 'poster';

const PLATFORM_LABELS: Record<string, string> = {
  xhs: '小红书',
  dy: '抖音',
  bili: 'B站',
  wb: '微博',
};

const SCORE_LABELS: Record<DecisionScoreField, string> = {
  culture_fit: '文化适配',
  market_pull: '市场拉力',
  novelty: '原创空间',
  visual_potential: '视觉潜力',
  social_shareability: '社交传播',
  product_feasibility: '产品可行性',
};

const POSTER_SECTION_LABELS: Record<string, string> = {
  hero: '成品主视觉',
  culture: '文化元素',
  breakdown: '结构拆解',
  bom: '用料 / BOM',
  process: '工艺路径',
};

const THEME_LABELS = {
  editorial: ['编辑提案', '留白、叙事与展览感'],
  workshop: ['工坊拆解', '材料、尺寸与加工优先'],
  exhibition: ['展陈海报', '成品视觉与文化故事优先'],
} as const;

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

const STAGES: Array<{ id: DecisionStage; index: string; label: string; note: string }> = [
  { id: 'culture', index: '01', label: '文化选材', note: '选择可进入本轮的文化记录' },
  { id: 'market', index: '02', label: '市场范围', note: '平台与产品形态自由组合' },
  { id: 'score', index: '03', label: '评分与候选', note: '改变权重并选择 1–3 个机会' },
  { id: 'brief', index: '04', label: '设计意图', note: '人群、价格、场景与材料偏好' },
  { id: 'visual', index: '05', label: '视觉方向', note: '研究参考、风格与画幅' },
  { id: 'concept', index: '06', label: '方案比较', note: '选择比较组与当前采用方向' },
  { id: 'poster', index: '07', label: '海报呈现', note: '选择版式主题与展示板块' },
];

function cloneProfile(profile: DecisionProfile): DecisionProfile {
  return structuredClone(profile);
}

function lines(value: string): string[] {
  return value.split('\n').map((item) => item.trim()).filter(Boolean);
}

function countForStage(stage: DecisionStage, profile: DecisionProfile): string {
  if (stage === 'culture') return String(profile.cultureRecordIds.length);
  if (stage === 'market') return `${profile.marketPlatforms.length}/${profile.marketProductForms.length}`;
  if (stage === 'score') return String(profile.opportunityIds.length);
  if (stage === 'brief') return String(profile.designIntent.preferredProductForms.length);
  if (stage === 'visual') return String(profile.visualDirection.referenceIds.length);
  if (stage === 'concept') return String(profile.conceptCompareIds.length);
  return String(profile.posterSections.length);
}

export function DecisionStudio({
  profile,
  catalog,
  initialStage,
  busy,
  onClose,
  onSave,
}: {
  profile: DecisionProfile;
  catalog: DecisionCatalog;
  initialStage: DecisionStage;
  busy: boolean;
  onClose: () => void;
  onSave: (profile: DecisionProfile) => void;
}) {
  const [stage, setStage] = useState<DecisionStage>(initialStage);
  const [draft, setDraft] = useState<DecisionProfile>(() => cloneProfile(profile));
  const [cultureQuery, setCultureQuery] = useState('');
  const dialogRef = useRef<HTMLElement>(null);
  const initialFocusRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const previouslyFocused = document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null;
    const focusableSelector = [
      'button:not([disabled])',
      'a[href]',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
    ].join(',');
    const focusInitialControl = window.requestAnimationFrame(() => {
      initialFocusRef.current?.focus();
    });
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== 'Tab' || !dialogRef.current) return;
      const focusable = Array.from(
        dialogRef.current.querySelectorAll<HTMLElement>(focusableSelector),
      ).filter((element) => element.offsetParent !== null);
      if (focusable.length === 0) {
        event.preventDefault();
        dialogRef.current.focus();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      window.cancelAnimationFrame(focusInitialControl);
      document.removeEventListener('keydown', handleKeyDown);
      previouslyFocused?.focus();
    };
  }, [onClose]);

  const manualRanking = useMemo(
    () => catalog.opportunities
      .map((item) => ({
        ...item,
        manualScore: calculateManualOpportunityScore(
          item,
          draft.scoreWeights,
          draft.culturalRiskPenalty,
        ),
      }))
      .sort((a, b) => b.manualScore - a.manualScore),
    [catalog.opportunities, draft.culturalRiskPenalty, draft.scoreWeights],
  );
  const filteredCulture = useMemo(() => {
    const keyword = cultureQuery.trim().toLowerCase();
    if (!keyword) return catalog.cultureRecords;
    return catalog.cultureRecords.filter((item) =>
      [item.name, item.category, ...item.region, ...item.crafts]
        .join(' ')
        .toLowerCase()
        .includes(keyword),
    );
  }, [catalog.cultureRecords, cultureQuery]);
  const totalWeight = DECISION_SCORE_FIELDS.reduce(
    (sum, field) => sum + draft.scoreWeights[field],
    0,
  );
  const canSave = draft.cultureRecordIds.length > 0
    && draft.marketPlatforms.length > 0
    && draft.marketProductForms.length > 0
    && draft.opportunityIds.length > 0
    && draft.opportunityIds.length <= 3
    && draft.conceptCompareIds.length > 0
    && draft.posterSections.length > 0
    && totalWeight > 0;

  const applyRecommendation = () => {
    const recommended = cloneProfile(catalog.recommendedProfile);
    recommended.version = profile.version;
    recommended.mode = 'guided';
    recommended.updatedAt = profile.updatedAt;
    setDraft(recommended);
  };

  return (
    <div className="decision-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        aria-label="人工决策工作台"
        aria-modal="true"
        className="decision-studio"
        ref={dialogRef}
        role="dialog"
        tabIndex={-1}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="decision-studio__header">
          <div>
            <h2>人工决策工作台</h2>
            <p>第 {profile.version} 版选择；原始证据保持只读。</p>
          </div>
          <div className="decision-mode-switch" aria-label="决策模式">
            <button aria-pressed={draft.mode === 'guided'} className={draft.mode === 'guided' ? 'is-active' : ''} type="button" onClick={applyRecommendation}>系统建议</button>
            <button aria-pressed={draft.mode === 'manual'} className={draft.mode === 'manual' ? 'is-active' : ''} type="button" onClick={() => setDraft({ ...draft, mode: 'manual' })}>人工配置</button>
          </div>
          <button className="decision-close" type="button" onClick={onClose} aria-label="关闭人工决策工作台"><X aria-hidden="true" size={18} /></button>
        </header>

        <div className="decision-studio__layout">
          <nav className="decision-stage-nav" aria-label="人工决策阶段">
            {STAGES.map((item) => (
              <button aria-current={stage === item.id ? 'step' : undefined} className={stage === item.id ? 'is-active' : ''} key={item.id} ref={stage === item.id ? initialFocusRef : undefined} title={item.note} type="button" onClick={() => setStage(item.id)}>
                <b>{item.index}</b>
                <span><strong>{item.label}</strong></span>
                <em>{countForStage(item.id, draft)}</em>
              </button>
            ))}
          </nav>

          <div className="decision-stage-content">
            {stage === 'culture' ? (
              <section className="decision-panel">
                <header><h3>哪些文化记录进入本轮设计？</h3><p>可多选；地域、工艺与文化边界仍由知识图谱锁定。</p></header>
                <label className="decision-search"><Search aria-hidden="true" size={15} /><input value={cultureQuery} onChange={(event) => setCultureQuery(event.target.value)} placeholder="搜索地域、工艺、记录名称…" /><em>{draft.cultureRecordIds.length} / {catalog.cultureRecords.length} 已选</em></label>
                <div className="decision-culture-grid">
                  {filteredCulture.map((item) => {
                    const selected = draft.cultureRecordIds.includes(item.id);
                    return <button aria-pressed={selected} className={selected ? 'is-selected' : ''} key={item.id} type="button" onClick={() => setDraft({ ...draft, mode: 'manual', cultureRecordIds: toggleDecisionSelection(draft.cultureRecordIds, item.id, 22) })}><span><code>{item.id}</code><i>{item.sourceRefs.length} 条引用</i></span><strong>{item.name}</strong><p>{[...item.region.slice(0, 2), ...item.crafts.slice(0, 2)].join(' · ')}</p><em>{selected ? '本轮使用' : '加入本轮'}</em></button>;
                  })}
                </div>
              </section>
            ) : null}

            {stage === 'market' ? (
              <section className="decision-panel">
                <header><h3>选择平台与要观察的产品形态</h3><p>平台状态保持原样；历史快照不会因被选中而变成实时数据。</p></header>
                <h4>平台范围</h4>
                <div className="decision-platform-grid">
                  {catalog.marketPlatforms.map((item) => {
                    const selected = draft.marketPlatforms.includes(item.id);
                    return <button aria-pressed={selected} className={selected ? 'is-selected' : ''} key={item.id} type="button" onClick={() => setDraft({ ...draft, mode: 'manual', marketPlatforms: toggleDecisionSelection(draft.marketPlatforms, item.id, 4) })}><span>{PLATFORM_LABELS[item.id] ?? item.id}</span><strong>{item.sampleSize}</strong><em>{item.status === 'live' ? '实时' : '历史快照'}</em><i>{selected ? '使用中' : '选择'}</i></button>;
                  })}
                </div>
                <h4>产品形态</h4>
                <div className="decision-form-list">
                  {catalog.productForms.map((item) => {
                    const selected = draft.marketProductForms.includes(item.id);
                    return <button aria-pressed={selected} className={selected ? 'is-selected' : ''} key={item.id} type="button" onClick={() => setDraft({ ...draft, mode: 'manual', marketProductForms: toggleDecisionSelection(draft.marketProductForms, item.id, 10) })}><b>{String(item.rank).padStart(2, '0')}</b><span><strong>{item.id}</strong><small>{item.sampleSize} 条样本 · {item.coverage} 平台覆盖</small></span><i><em style={{ width: `${Math.min(100, item.score)}%` }} /></i><strong>{item.score}</strong></button>;
                  })}
                </div>
              </section>
            ) : null}

            {stage === 'score' ? (
              <section className="decision-panel decision-panel--score">
                <header><h3>你来定义“好机会”</h3><p>调整权重会即时重排；系统分与人工分分别保留。</p></header>
                <div className="decision-score-layout">
                  <div className="decision-weight-editor">
                    {DECISION_SCORE_FIELDS.map((field) => <label key={field}><span><strong>{SCORE_LABELS[field]}</strong><span className="decision-weight-number"><input aria-label={`${SCORE_LABELS[field]}权重百分比`} min="0" max="40" step="1" type="number" value={Math.round(draft.scoreWeights[field] * 100)} onChange={(event) => setDraft({ ...draft, mode: 'manual', scoreWeights: { ...draft.scoreWeights, [field]: Math.min(40, Math.max(0, Number(event.target.value))) / 100 } })} /><em>%</em></span></span><input min="0" max="40" step="1" type="range" value={Math.round(draft.scoreWeights[field] * 100)} onChange={(event) => setDraft({ ...draft, mode: 'manual', scoreWeights: { ...draft.scoreWeights, [field]: Number(event.target.value) / 100 } })} /></label>)}
                    <label className="is-risk"><span><strong>文化风险扣分</strong><span className="decision-weight-number"><input aria-label="文化风险扣分百分比" min="0" max="60" step="1" type="number" value={Math.round(draft.culturalRiskPenalty * 100)} onChange={(event) => setDraft({ ...draft, mode: 'manual', culturalRiskPenalty: Math.min(60, Math.max(0, Number(event.target.value))) / 100 })} /><em>%</em></span></span><input min="0" max="60" step="1" type="range" value={Math.round(draft.culturalRiskPenalty * 100)} onChange={(event) => setDraft({ ...draft, mode: 'manual', culturalRiskPenalty: Number(event.target.value) / 100 })} /></label>
                    <p>正向权重当前合计 {Math.round(totalWeight * 100)}%，保存时会自动归一化为 100%。</p>
                  </div>
                  <div className="decision-opportunity-list">
                    {manualRanking.map((item, index) => {
                      const selected = draft.opportunityIds.includes(item.id);
                      const limitReached = draft.opportunityIds.length >= 3 && !selected;
                      return <button aria-pressed={selected} className={selected ? 'is-selected' : ''} disabled={limitReached} key={item.id} type="button" onClick={() => setDraft({ ...draft, mode: 'manual', opportunityIds: toggleDecisionSelection(draft.opportunityIds, item.id, 3) })}><b>{String(index + 1).padStart(2, '0')}</b><span><code>{item.id} · {verificationLabel(item.verification)}</code><strong>{item.cultureElement}</strong><small>{item.trendElement}</small></span><div><em>人工 {item.manualScore}</em><small>系统 {item.systemScore}</small></div></button>;
                    })}
                  </div>
                </div>
              </section>
            ) : null}

            {stage === 'brief' ? (
              <section className="decision-panel">
                <header><h3>明确这次项目的设计意图</h3><p>保存后形成任务书新版本，后续视觉与海报标记为待更新。</p></header>
                <div className="decision-form-grid">
                  <label><span>目标人群</span><input value={draft.designIntent.targetAudience} onChange={(event) => setDraft({ ...draft, mode: 'manual', designIntent: { ...draft.designIntent, targetAudience: event.target.value } })} /></label>
                  <label><span>目标价格带</span><input value={draft.designIntent.priceBand} onChange={(event) => setDraft({ ...draft, mode: 'manual', designIntent: { ...draft.designIntent, priceBand: event.target.value } })} /></label>
                  <label className="is-wide"><span>偏好的产品形态（每行一项）</span><textarea rows={4} value={draft.designIntent.preferredProductForms.join('\n')} onChange={(event) => setDraft({ ...draft, mode: 'manual', designIntent: { ...draft.designIntent, preferredProductForms: lines(event.target.value) } })} /></label>
                  <label><span>使用场景（每行一项）</span><textarea rows={6} value={draft.designIntent.useScenarios.join('\n')} onChange={(event) => setDraft({ ...draft, mode: 'manual', designIntent: { ...draft.designIntent, useScenarios: lines(event.target.value) } })} /></label>
                  <label><span>材料优先级（每行一项）</span><textarea rows={6} value={draft.designIntent.materialPriorities.join('\n')} onChange={(event) => setDraft({ ...draft, mode: 'manual', designIntent: { ...draft.designIntent, materialPriorities: lines(event.target.value) } })} /></label>
                </div>
              </section>
            ) : null}

            {stage === 'visual' ? (
              <section className="decision-panel">
                <header><h3>选择研究参照，不复制馆藏像素</h3><p>参照只提供结构、节奏、材料与风格文字；图片不会进入生成贴图。</p></header>
                <div className="decision-reference-grid">
                  {catalog.visualReferences.map((item) => {
                    const selected = draft.visualDirection.referenceIds.includes(item.id);
                    return <button aria-pressed={selected} className={selected ? 'is-selected' : ''} key={item.id} type="button" onClick={() => setDraft({ ...draft, mode: 'manual', visualDirection: { ...draft.visualDirection, referenceIds: toggleDecisionSelection(draft.visualDirection.referenceIds, item.id, 8) } })}><span><code>{item.id}</code><em title={item.rightsStatus}>{rightsLabel(item.rightsStatus)}</em></span><strong>{item.title}</strong><p>{Array.isArray(item.region) ? item.region.join(' · ') : item.region} · {item.subjectType}</p></button>;
                  })}
                </div>
                <div className="decision-form-grid decision-form-grid--visual">
                  <label><span>输出画幅</span><select value={draft.visualDirection.imageSize} onChange={(event) => setDraft({ ...draft, mode: 'manual', visualDirection: { ...draft.visualDirection, imageSize: event.target.value } })}>{catalog.visualSizes.map((size) => <option key={size} value={size}>{size}</option>)}</select></label>
                  <label><span>风格关键词（每行一项）</span><textarea rows={5} value={draft.visualDirection.styleKeywords.join('\n')} onChange={(event) => setDraft({ ...draft, mode: 'manual', visualDirection: { ...draft.visualDirection, styleKeywords: lines(event.target.value) } })} /></label>
                  <label className="is-wide"><span>视觉补充说明 / 禁用项</span><textarea rows={4} value={draft.visualDirection.notes} onChange={(event) => setDraft({ ...draft, mode: 'manual', visualDirection: { ...draft.visualDirection, notes: event.target.value } })} /></label>
                </div>
              </section>
            ) : null}

            {stage === 'concept' ? (
              <section className="decision-panel">
                <header><h3>选择比较组与当前采用方案</h3><p>只生成比较组中的方向；当前采用方案继续驱动海报。</p></header>
                <div className="decision-concept-grid">
                  {catalog.concepts.map((item) => {
                    const compare = draft.conceptCompareIds.includes(item.id);
                    const active = draft.activeConceptId === item.id;
                    const image = apiAssetUrl(item.imageUrl, API_BASE);
                    return <article className={`${compare ? 'is-selected' : ''} ${active ? 'is-active' : ''}`} key={item.id}>{image ? <img src={image} alt={`${item.title} 概念方向`} decoding="async" loading="lazy" /> : <div className="decision-concept-empty">等待视觉</div>}<span>{item.label}</span><h4>{item.title}</h4><label><input checked={compare} type="checkbox" onChange={() => setDraft({ ...draft, mode: 'manual', conceptCompareIds: toggleDecisionSelection(draft.conceptCompareIds, item.id, 12) })} />加入比较组</label><label><input checked={active} name="active-concept" type="radio" onChange={() => setDraft({ ...draft, mode: 'manual', activeConceptId: item.id, conceptCompareIds: draft.conceptCompareIds.includes(item.id) ? draft.conceptCompareIds : [...draft.conceptCompareIds, item.id] })} />设为当前采用</label></article>;
                  })}
                </div>
              </section>
            ) : null}

            {stage === 'poster' ? (
              <section className="decision-panel">
                <header><h3>决定它最终如何被看见</h3><p>主题调整信息优先级；板块可显隐，概念与首样边界保持不变。</p></header>
                <div className="decision-theme-grid">
                  {catalog.posterThemes.map((theme) => <button aria-pressed={draft.posterTheme === theme} className={draft.posterTheme === theme ? 'is-selected' : ''} key={theme} type="button" onClick={() => setDraft({ ...draft, mode: 'manual', posterTheme: theme })}><span>{THEME_LABELS[theme][0]}</span><p>{THEME_LABELS[theme][1]}</p><em>{draft.posterTheme === theme ? '当前主题' : '选择主题'}</em></button>)}
                </div>
                <fieldset className="decision-section-toggles"><legend>海报展示板块</legend>{catalog.posterSections.map((section) => <label key={section}><input checked={draft.posterSections.includes(section)} type="checkbox" onChange={() => setDraft({ ...draft, mode: 'manual', posterSections: toggleDecisionSelection(draft.posterSections, section, catalog.posterSections.length) })} /><span>{POSTER_SECTION_LABELS[section] ?? section}</span></label>)}</fieldset>
                <label className="decision-notes"><span>本轮人工决策备注</span><textarea rows={5} value={draft.notes} onChange={(event) => setDraft({ ...draft, mode: 'manual', notes: event.target.value })} placeholder="记录为什么这样选择、还需要谁确认、下一轮要验证什么…" /></label>
              </section>
            ) : null}
          </div>
        </div>

        <footer className="decision-studio__footer">
          <div className="decision-studio__save-state">
            <span>当前将保存</span>
            <strong>{draft.cultureRecordIds.length} 文化 / {draft.marketPlatforms.length} 平台 / {draft.opportunityIds.length} 机会 / {draft.conceptCompareIds.length} 概念</strong>
            {!canSave ? <p>每个关键阶段至少选择一项，机会最多 3 项，评分权重不能全部为 0。</p> : null}
          </div>
          <div className="decision-studio__secondary-actions">
            <button className="decision-secondary" type="button" onClick={applyRecommendation}>恢复系统建议</button>
            <button className="decision-secondary" type="button" onClick={onClose}>取消</button>
          </div>
          <button className="decision-primary" disabled={busy || !canSave} type="button" onClick={() => onSave({ ...draft, mode: draft.mode === 'guided' ? 'guided' : 'manual' })}>{busy ? '正在保存…' : '保存人工决策并更新链路'}</button>
        </footer>
      </section>
    </div>
  );
}
