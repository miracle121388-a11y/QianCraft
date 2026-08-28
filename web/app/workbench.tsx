'use client';

import { useEffect, useMemo, useState } from 'react';

const API = 'http://127.0.0.1:8787';
const views = [
  ['overview', '01', '总览与审计'],
  ['sources', '02', '信息仓库'],
  ['opportunities', '03', '机会池'],
  ['design', '04', '设计工作台'],
  ['runs', '05', '生成记录'],
] as const;

type ViewId = (typeof views)[number][0];
type Json = Record<string, unknown>;

type Summary = {
  project: { topic: string; run_id: string; finished_at: string };
  repositories: Array<{
    id: string; name: string; count: number; unit: string; secondary: string;
    status: string; source_file: string;
  }>;
  truth_audit: {
    culture: { actual: number; verified: boolean };
    market: { actual: number; meaning: string; raw_files_present: boolean };
    opportunities: { actual: number; model_generated: number; rule_baseline: number; meaning: string };
  };
  current_run: {
    market_status: string; live_post_count: number; cache_post_count: number;
    components: Array<{ component: string; mode: string; engine: string; detail: string; ok: boolean }>;
  };
  preflight: {
    research_ready: boolean; image_generation_ready: boolean;
    checks: Array<{ id: string; label: string; ok: boolean; detail: string }>;
    blockers: string[];
  };
  historical_snapshot: {
    file: string; generated_at: string; social_record_count: number;
    public_baseline_count: number; platform_counts: Record<string, number>;
  };
};

type Opportunity = {
  opportunity_id: string; culture_element: string; culture_meaning: string;
  trend_element: string; market_signal: string; match_reason: string;
  potential_product_categories: string[]; design_keywords: string[];
  cultural_constraints: string[]; evidence_refs: string[]; overall_score: number;
  culture_fit: number; market_pull: number; novelty: number; visual_potential: number;
  social_shareability: number; product_feasibility: number; cultural_risk: number;
  verification: { status: string; warnings: string[]; branch_region_findings: string[]; notes: string[] };
  origin: string; design_generator: string | null;
  score_audit: { stored: number; recomputed: number; matches: boolean };
  evidence_details: Array<{ source_id: string; source_title: string; source_url: string; publisher: string }>;
};

type OpportunityPayload = {
  count: number; generated_accepted: number; baseline_count: number;
  weights: Record<string, number>; ranked_ids: string[]; auto_top3_ids: string[];
  opportunities: Opportunity[];
};

type Workspace = {
  selection_mode: 'auto' | 'manual'; selected_opportunity_ids: string[];
  primary_opportunity_id: string; opportunity_edits: Record<string, Record<string, unknown>>;
  design_overrides: Record<string, unknown>; manual_brief: string;
  last_design_run_id: string; updated_at: string;
};

type DesignState = {
  selected_run_id: string; poster_url: string;
  image_generation: { available: boolean; reason: string };
  design: Record<string, any>;
  runs: Array<Record<string, any>>;
};

const emptyWorkspace: Workspace = {
  selection_mode: 'auto', selected_opportunity_ids: [], primary_opportunity_id: '',
  opportunity_edits: {}, design_overrides: {}, manual_brief: '',
  last_design_run_id: '', updated_at: '',
};

async function jsonRequest<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${url}`, { cache: 'no-store', ...options });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `请求失败：${response.status}`);
  return payload;
}

function tags(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(String);
  return String(value || '').split(/[，,\n]/).map((item) => item.trim()).filter(Boolean);
}

function statusName(status: string) {
  return ({ file_verified: '文件核验', historical_snapshot: '历史快照', live: '实时', cache: '缓存', unavailable: '不可用' } as Record<string, string>)[status] || status;
}

function generatorName(value: string | null) {
  return ({ magnet: '模块收藏品生成器', plush: '织物挂偶生成器', provenance: '溯源档案生成器' } as Record<string, string>)[value || ''] || '尚无匹配生成器';
}

export default function Workbench() {
  const [active, setActive] = useState<ViewId>('overview');
  const [summary, setSummary] = useState<Summary | null>(null);
  const [opportunityData, setOpportunityData] = useState<OpportunityPayload | null>(null);
  const [workspace, setWorkspace] = useState<Workspace>(emptyWorkspace);
  const [designState, setDesignState] = useState<DesignState | null>(null);
  const [cultureData, setCultureData] = useState<Record<string, any> | null>(null);
  const [marketData, setMarketData] = useState<Record<string, any> | null>(null);
  const [sourceType, setSourceType] = useState<'culture' | 'market'>('culture');
  const [marketSource, setMarketSource] = useState<'historical' | 'current'>('historical');
  const [platform, setPlatform] = useState('');
  const [query, setQuery] = useState('');
  const [marketOffset, setMarketOffset] = useState(0);
  const [editingOpportunityId, setEditingOpportunityId] = useState('');
  const [busy, setBusy] = useState('');
  const [notice, setNotice] = useState<{ kind: 'ok' | 'error'; text: string } | null>(null);
  const [fatal, setFatal] = useState('');

  const refreshCore = async () => {
    try {
      const [nextSummary, nextOpportunities, nextWorkspace, nextDesign] = await Promise.all([
        jsonRequest<Summary>('/api/summary'),
        jsonRequest<OpportunityPayload>('/api/opportunities'),
        jsonRequest<Workspace>('/api/workspace'),
        jsonRequest<DesignState>('/api/design'),
      ]);
      setSummary(nextSummary);
      setOpportunityData(nextOpportunities);
      setWorkspace(nextWorkspace);
      setDesignState(nextDesign);
      setEditingOpportunityId((current) => current || nextOpportunities.opportunities[0]?.opportunity_id || '');
      setFatal('');
    } catch (reason) {
      setFatal(String(reason));
    }
  };

  useEffect(() => { refreshCore(); }, []);

  const loadCulture = async () => {
    if (!cultureData) setCultureData(await jsonRequest('/api/culture'));
  };

  const loadMarket = async (nextOffset = marketOffset) => {
    const params = new URLSearchParams({ source: marketSource, offset: String(nextOffset), limit: '30' });
    if (platform) params.set('platform', platform);
    if (query) params.set('q', query);
    setMarketData(await jsonRequest(`/api/market?${params}`));
    setMarketOffset(nextOffset);
  };

  useEffect(() => {
    if (active === 'sources' && sourceType === 'culture') loadCulture().catch((error) => setNotice({ kind: 'error', text: String(error) }));
  }, [active, sourceType]);

  useEffect(() => {
    if (active === 'sources' && sourceType === 'market') loadMarket(0).catch((error) => setNotice({ kind: 'error', text: String(error) }));
  }, [active, sourceType, marketSource, platform]);

  const persistWorkspace = async (next: Workspace, success = '工作区已保存') => {
    setBusy('save');
    try {
      const saved = await jsonRequest<Workspace>('/api/workspace', {
        method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(next),
      });
      setWorkspace(saved);
      setNotice({ kind: 'ok', text: success });
      return saved;
    } catch (error) {
      setNotice({ kind: 'error', text: String(error) });
      throw error;
    } finally { setBusy(''); }
  };

  const switchMode = async (mode: 'auto' | 'manual') => {
    if (!opportunityData) return;
    const selected = mode === 'auto' ? opportunityData.auto_top3_ids : (workspace.selected_opportunity_ids.length ? workspace.selected_opportunity_ids : opportunityData.auto_top3_ids);
    const next = { ...workspace, selection_mode: mode, selected_opportunity_ids: selected, primary_opportunity_id: mode === 'manual' ? (workspace.primary_opportunity_id || selected[0]) : '' };
    await persistWorkspace(next, mode === 'auto' ? '已恢复系统 Top 3 自动选择' : '已切换为人工选择');
  };

  const toggleOpportunity = async (id: string) => {
    if (workspace.selection_mode !== 'manual') return;
    const selected = workspace.selected_opportunity_ids.includes(id)
      ? workspace.selected_opportunity_ids.filter((item) => item !== id)
      : [...workspace.selected_opportunity_ids, id];
    if (selected.length > 3) { setNotice({ kind: 'error', text: 'Designer Handoff 最多选择 3 条机会。' }); return; }
    if (!selected.length) { setNotice({ kind: 'error', text: '至少保留 1 条机会。' }); return; }
    const primary = selected.includes(workspace.primary_opportunity_id) ? workspace.primary_opportunity_id : selected[0];
    await persistWorkspace({ ...workspace, selected_opportunity_ids: selected, primary_opportunity_id: primary }, '人工选择已保存');
  };

  const updateOpportunityEdit = (id: string, key: string, value: unknown) => {
    setWorkspace((current) => ({ ...current, opportunity_edits: { ...current.opportunity_edits, [id]: { ...(current.opportunity_edits[id] || {}), [key]: value } } }));
  };

  const generateDesign = async () => {
    setBusy('generate'); setNotice(null);
    try {
      const saved = await jsonRequest<Workspace>('/api/workspace', {
        method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(workspace),
      });
      setWorkspace(saved);
      const result = await jsonRequest<Record<string, any>>('/api/design/generate', { method: 'POST' });
      const nextDesign = await jsonRequest<DesignState>('/api/design');
      setDesignState(nextDesign);
      setWorkspace(await jsonRequest<Workspace>('/api/workspace'));
      setNotice({ kind: 'ok', text: `已真实生成 ${result.product_name} 的设计规格与本地结构图。` });
    } catch (error) { setNotice({ kind: 'error', text: String(error) }); }
    finally { setBusy(''); }
  };

  const runResearch = async () => {
    setBusy('research'); setNotice(null);
    try {
      const result = await jsonRequest<Record<string, any>>('/api/research/run', { method: 'POST' });
      setNotice({ kind: result.status === 'live_verified' ? 'ok' : 'error', text: result.detail || `研究任务状态：${result.status}` });
      await refreshCore();
    } catch (error) { setNotice({ kind: 'error', text: String(error) }); }
    finally { setBusy(''); }
  };

  const activeOpportunity = opportunityData?.opportunities.find((item) => item.opportunity_id === editingOpportunityId) || null;
  const selectedPrimary = workspace.selection_mode === 'manual'
    ? workspace.primary_opportunity_id
    : designState?.design?.selection?.primary_opportunity_id || '';
  const primaryOpportunity = opportunityData?.opportunities.find((item) => item.opportunity_id === selectedPrimary);

  if (fatal) return <FatalState message={fatal} onRetry={refreshCore} />;

  return (
    <div className="tool-shell">
      <aside className="sidebar">
        <div className="tool-brand"><span>黔</span><div><strong>QianCraft</strong><small>证据设计工作台</small></div></div>
        <nav aria-label="工具模块">
          {views.map(([id, number, label]) => <button key={id} className={active === id ? 'active' : ''} onClick={() => setActive(id)}><i>{number}</i>{label}</button>)}
        </nav>
        <div className="sidebar-truth"><strong>NO FALLBACK</strong><span>缺数据就停止，不用缓存伪装实时</span></div>
        <div className="sidebar-foot"><span className="status-dot" />本地真实数据服务</div>
      </aside>

      <main className="workspace-main">
        <WorkspaceHeader summary={summary} active={active} busy={busy} onRefresh={refreshCore} onRun={runResearch} />
        {notice && <div className={`notice ${notice.kind}`}><span>{notice.kind === 'ok' ? '✓' : '!'}</span>{notice.text}<button onClick={() => setNotice(null)}>×</button></div>}
        {!summary || !opportunityData || !designState ? <section className="loading-state">正在从真实项目文件计算工作区…</section> : (
          <>
            {active === 'overview' && <Overview summary={summary} setActive={setActive} />}
            {active === 'sources' && <SourcesView sourceType={sourceType} setSourceType={setSourceType} cultureData={cultureData} marketData={marketData} marketSource={marketSource} setMarketSource={setMarketSource} platform={platform} setPlatform={setPlatform} query={query} setQuery={setQuery} loadMarket={loadMarket} marketOffset={marketOffset} />}
            {active === 'opportunities' && <OpportunityView data={opportunityData} workspace={workspace} activeOpportunity={activeOpportunity} setEditingOpportunityId={setEditingOpportunityId} switchMode={switchMode} toggleOpportunity={toggleOpportunity} persistWorkspace={persistWorkspace} setWorkspace={setWorkspace} updateOpportunityEdit={updateOpportunityEdit} busy={busy} />}
            {active === 'design' && <DesignView data={opportunityData} workspace={workspace} setWorkspace={setWorkspace} designState={designState} primaryOpportunity={primaryOpportunity || null} generateDesign={generateDesign} busy={busy} />}
            {active === 'runs' && <RunsView summary={summary} designState={designState} />}
          </>
        )}
      </main>
    </div>
  );
}

function FatalState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <div className="fatal-full"><strong>真实数据服务未连接</strong><p>{message}</p><small>页面不会使用静态假数据替代。</small><button onClick={onRetry}>重新连接</button></div>;
}

function WorkspaceHeader({ summary, active, busy, onRefresh, onRun }: { summary: Summary | null; active: ViewId; busy: string; onRefresh: () => void; onRun: () => void }) {
  const label = views.find(([id]) => id === active)?.[2];
  return <header className="workspace-header"><div><span className="crumb">WORKSPACE / {active.toUpperCase()}</span><h1>{label} · {summary?.project.topic || '加载中'}</h1></div><div className="header-actions"><span className="run-id">{summary?.project.run_id || '—'}</span><button className="outline-button" onClick={onRefresh}>刷新真实文件</button><button className="primary-button" disabled={!summary?.preflight.research_ready || busy === 'research'} onClick={onRun}>{busy === 'research' ? '运行中…' : '开始严格实时研究'}</button></div></header>;
}

function Overview({ summary, setActive }: { summary: Summary; setActive: (view: ViewId) => void }) {
  return <>
    <section className="audit-banner"><div><span className="audit-kicker">TRUTH AUDIT</span><h2>先看数据是真是假，再开始做设计。</h2></div><div className="audit-facts"><p><i className="ok" />22 条文化记录：<strong>文件中实有 {summary.truth_audit.culture.actual} 条</strong></p><p><i className="warn" />378 条市场记录：<strong>历史快照，不是当前实时抓取</strong></p><p><i className="warn" />8 条机会：<strong>{summary.truth_audit.opportunities.model_generated} 条模型生成，{summary.truth_audit.opportunities.rule_baseline} 条规则基线</strong></p><p><i className="blocked" />当前实时市场记录：<strong>{summary.current_run.live_post_count} 条</strong></p></div></section>
    <section className="repo-section"><SectionTitle code="01 / EVIDENCE REPOSITORIES" title="信息仓库" description="数字在每次加载时从真实文件重新计算，不在页面里写死。" /><div className="repo-grid">{summary.repositories.map((repo) => <button className="repo-card" key={repo.id} onClick={() => setActive('sources')}><div className="repo-card-head"><span className={`source-badge ${repo.status}`}>{statusName(repo.status)}</span><b>↗</b></div><h3>{repo.name}</h3><div className="repo-count"><strong>{repo.count}</strong><span>{repo.unit}</span></div><p>{repo.secondary}</p><code>{repo.source_file}</code></button>)}</div></section>
    <section className="truth-detail-section"><SectionTitle code="02 / WHAT THE NUMBERS MEAN" title="数字的真实含义" description="把可验证事实与当前缺口放在同一张表里。" /><div className="truth-table"><div><strong>文化记录</strong><span>22 / 22</span><p>来自 knowledge_graph.json；每条记录都有 Cxxx 来源编号。</p><b className="truth-ok">可逐条核验</b></div><div><strong>市场社交记录</strong><span>378</span><p>{summary.truth_audit.market.meaning}；原始 JSONL 当前{summary.truth_audit.market.raw_files_present ? '存在' : '缺失'}。</p><b className="truth-warn">历史派生快照</b></div><div><strong>机会池</strong><span>8</span><p>{summary.truth_audit.opportunities.meaning}</p><b className="truth-warn">规则基线</b></div><div><strong>当前实时抓取</strong><span>{summary.current_run.live_post_count}</span><p>严格模式未就绪时不会自动使用历史记录冒充本轮抓取。</p><b className="truth-blocked">未就绪</b></div></div></section>
    <section className="preflight-section"><SectionTitle code="03 / STRICT MODE PREFLIGHT" title="严格模式就绪检查" description="有一项未就绪，就不启动实时任务，也不会改用缓存兜底。" /><div className="check-list">{summary.preflight.checks.map((check) => <div className="check-row" key={check.id}><i className={check.ok ? 'ok' : 'blocked'} /><strong>{check.label}</strong><span>{check.detail}</span><small>{check.ok ? 'READY' : 'BLOCKED'}</small></div>)}</div></section>
  </>;
}

function SectionTitle({ code, title, description }: { code: string; title: string; description: string }) {
  return <div className="section-title"><div><span>{code}</span><h2>{title}</h2></div><p>{description}</p></div>;
}

function SourcesView(props: {
  sourceType: 'culture' | 'market'; setSourceType: (value: 'culture' | 'market') => void;
  cultureData: Record<string, any> | null; marketData: Record<string, any> | null;
  marketSource: 'historical' | 'current'; setMarketSource: (value: 'historical' | 'current') => void;
  platform: string; setPlatform: (value: string) => void; query: string; setQuery: (value: string) => void;
  loadMarket: (offset?: number) => Promise<void>; marketOffset: number;
}) {
  const { sourceType, setSourceType, cultureData, marketData, marketSource, setMarketSource, platform, setPlatform, query, setQuery, loadMarket, marketOffset } = props;
  return <section className="module-page"><SectionTitle code="02 / SOURCE EXPLORER" title="逐条查验信息" description="这里展示文件中的原始字段、来源 URL、平台指标与派生分数。" /><div className="segmented"><button className={sourceType === 'culture' ? 'active' : ''} onClick={() => setSourceType('culture')}>文化记录</button><button className={sourceType === 'market' ? 'active' : ''} onClick={() => setSourceType('market')}>市场记录</button></div>
    {sourceType === 'culture' ? <div className="source-panel"><div className="panel-summary"><strong>{cultureData?.count ?? '—'}</strong><span>条文化记录</span><small>{cultureData?.source_count ?? '—'} 个登记来源 · 更新 {cultureData?.updated_at || '—'}</small></div><div className="record-list">{cultureData?.records?.map((record: Record<string, any>) => <details className="record-row" key={record.culture_id}><summary><span>{record.culture_id}</span><strong>{record.culture_name}</strong><small>{record.region?.join(' / ')}</small><b>{record.source_refs?.length} 个来源</b></summary><div className="record-detail"><DataGroup label="工艺" values={record.crafts} /><DataGroup label="纹样与符号" values={[...(record.patterns || []), ...(record.symbols || [])]} /><DataGroup label="文化边界" values={[...(record.cultural_taboos || []), ...(record.non_transferable_elements || [])]} /><div className="evidence-links"><h4>来源证据</h4>{record.source_details?.map((source: Record<string, any>) => <a key={source.source_id} href={source.source_url} target="_blank" rel="noreferrer"><span>{source.source_id}</span><strong>{source.source_title}</strong><small>{source.publisher}</small><b>↗</b></a>)}</div></div></details>)}</div></div> : <div className="source-panel"><div className="source-toolbar"><select value={marketSource} onChange={(event) => setMarketSource(event.target.value as 'historical' | 'current')}><option value="historical">历史真实快照</option><option value="current">当前运行数据</option></select><select value={platform} onChange={(event) => setPlatform(event.target.value)}><option value="">全部平台</option><option value="xhs">小红书</option><option value="dy">抖音</option><option value="bili">B站</option><option value="wb">微博</option></select><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索标题、内容、关键词…" /><button className="primary-button" onClick={() => loadMarket(0)}>查询真实记录</button></div><div className="market-meta"><strong>{marketData?.total ?? '—'}</strong><span>条匹配记录</span><code>{marketData?.source_file}</code></div><div className="market-list">{marketData?.records?.map((record: Record<string, any>) => <details className="market-row" key={`${record.platform}-${record.post_id}`}><summary><span className={`platform-tag ${record.platform}`}>{record.platform}</span><div><strong>{record.title || '(无标题)'}</strong><small>{record.search_keyword} · {record.published_at || '时间未披露'}</small></div><div className="metrics"><span>赞 {record.likes || 0}</span><span>藏 {record.favorites || 0}</span><span>评 {record.comments || 0}</span><b>{Number(record.platform_hot_score || 0).toFixed(1)}</b></div></summary><div className="market-detail"><p>{record.content || '没有正文内容'}</p><div className="market-field-grid"><span>产品形态<strong>{record.product_form || '未识别'}</strong></span><span>证据类型<strong>{record.evidence_type}</strong></span><span>真实互动分<strong>{Number(record.real_engagement_score || 0).toFixed(2)}</strong></span><span>派生传播分<strong>{Number(record.derived_viral_score || 0).toFixed(2)}</strong></span></div>{record.url && <a href={record.url} target="_blank" rel="noreferrer">打开原始页面 ↗</a>}</div></details>)}</div><div className="pagination"><button disabled={marketOffset === 0} onClick={() => loadMarket(Math.max(0, marketOffset - 30))}>上一页</button><span>{marketOffset + 1}–{Math.min(marketOffset + 30, marketData?.total || 0)} / {marketData?.total || 0}</span><button disabled={marketOffset + 30 >= (marketData?.total || 0)} onClick={() => loadMarket(marketOffset + 30)}>下一页</button></div></div>}
  </section>;
}

function DataGroup({ label, values }: { label: string; values: string[] }) {
  return <div className="data-group"><h4>{label}</h4><div>{values?.length ? values.map((value) => <span key={value}>{value}</span>) : <small>无记录</small>}</div></div>;
}

function OpportunityView({ data, workspace, activeOpportunity, setEditingOpportunityId, switchMode, toggleOpportunity, persistWorkspace, setWorkspace, updateOpportunityEdit, busy }: {
  data: OpportunityPayload; workspace: Workspace; activeOpportunity: Opportunity | null;
  setEditingOpportunityId: (value: string) => void; switchMode: (mode: 'auto' | 'manual') => Promise<void>;
  toggleOpportunity: (id: string) => Promise<void>; persistWorkspace: (value: Workspace, success?: string) => Promise<Workspace>;
  setWorkspace: React.Dispatch<React.SetStateAction<Workspace>>; updateOpportunityEdit: (id: string, key: string, value: unknown) => void; busy: string;
}) {
  const edit = activeOpportunity ? workspace.opportunity_edits[activeOpportunity.opportunity_id] || {} : {};
  return <section className="module-page"><SectionTitle code="03 / OPPORTUNITY POOL" title="八条机会，逐条可查" description={`当前 ${data.generated_accepted} 条来自模型，${data.baseline_count} 条来自规则基线；评分按文件内权重重新计算。`} />
    <div className="selection-control"><div><strong>进入 Designer Handoff 的方式</strong><p>系统模式自动使用评分 Top 3；人工模式允许选择 1–3 条并指定主机会。</p></div><div className="segmented"><button className={workspace.selection_mode === 'auto' ? 'active' : ''} onClick={() => switchMode('auto')}>系统 Top 3</button><button className={workspace.selection_mode === 'manual' ? 'active' : ''} onClick={() => switchMode('manual')}>人工选择</button></div></div>
    <div className="opportunity-layout"><div className="opportunity-list">{data.opportunities.map((item, index) => { const selected = workspace.selected_opportunity_ids.includes(item.opportunity_id); const primary = workspace.primary_opportunity_id === item.opportunity_id; return <article className={`opportunity-tool-card ${selected ? 'selected' : ''}`} key={item.opportunity_id}><div className="op-card-summary"><button className="op-check" disabled={workspace.selection_mode !== 'manual'} onClick={() => toggleOpportunity(item.opportunity_id)} aria-label={`${selected ? '取消' : '选择'} ${item.opportunity_id}`}>{selected ? '✓' : ''}</button><span className="op-rank">{String(index + 1).padStart(2, '0')}</span><button className="op-title-button" onClick={() => setEditingOpportunityId(item.opportunity_id)}><strong>{item.culture_element}</strong><small>{item.trend_element}</small></button><div className="op-badges"><span className={`verify ${item.verification.status}`}>{item.verification.status}</span><span>{item.origin === 'rule_baseline' ? '规则基线' : '模型/规则混合'}</span></div><div className="op-score"><strong>{item.overall_score.toFixed(1)}</strong><small>复算 {item.score_audit.recomputed.toFixed(1)} {item.score_audit.matches ? '✓' : '!'}</small></div>{workspace.selection_mode === 'manual' && selected && <label className="primary-radio"><input type="radio" checked={primary} onChange={() => persistWorkspace({ ...workspace, primary_opportunity_id: item.opportunity_id }, '主机会已更新')} />主机会</label>}</div><details><summary>展开评分、证据与核验结果</summary><div className="op-audit"><ScoreGrid item={item} /><div className="op-explanation"><p><strong>为什么匹配</strong>{item.match_reason}</p><p><strong>市场信号</strong>{item.market_signal}</p><p><strong>文化约束</strong>{item.cultural_constraints.join('；')}</p><p><strong>生成能力</strong>{generatorName(item.design_generator)}</p></div><div className="evidence-chip-list">{item.evidence_details.map((source) => <a key={source.source_id} href={source.source_url} target="_blank" rel="noreferrer"><span>{source.source_id}</span>{source.source_title || source.publisher} ↗</a>)}</div></div></details></article>; })}</div>
      <aside className="op-editor"><div className="editor-sticky"><span className="editor-kicker">MANUAL INTERVENTION</span><h3>{activeOpportunity?.opportunity_id || '选择机会'}</h3><p className="editor-origin">分数与证据编号锁定不可手改；标题、设计方向和产品形态可以形成工作区草稿。</p>{activeOpportunity && <><label>设计交接标题<input value={String(edit.title || `${activeOpportunity.culture_element} × ${activeOpportunity.trend_element}`)} onChange={(event) => updateOpportunityEdit(activeOpportunity.opportunity_id, 'title', event.target.value)} /></label><label>为什么现在做<textarea rows={4} value={String(edit.why_now || activeOpportunity.match_reason)} onChange={(event) => updateOpportunityEdit(activeOpportunity.opportunity_id, 'why_now', event.target.value)} /></label><label>产品形态（逗号分隔）<input value={tags(edit.potential_product_categories || activeOpportunity.potential_product_categories).join('，')} onChange={(event) => updateOpportunityEdit(activeOpportunity.opportunity_id, 'potential_product_categories', tags(event.target.value))} /></label><label>设计关键词（逗号分隔）<input value={tags(edit.design_keywords || activeOpportunity.design_keywords).join('，')} onChange={(event) => updateOpportunityEdit(activeOpportunity.opportunity_id, 'design_keywords', tags(event.target.value))} /></label><label>人工设计简报<textarea rows={5} value={workspace.manual_brief} onChange={(event) => setWorkspace({ ...workspace, manual_brief: event.target.value })} placeholder="写下希望保留、修改或验证的设计方向…" /></label><button className="primary-button wide" disabled={busy === 'save'} onClick={() => persistWorkspace(workspace, '机会草稿与选择已保存')}>{busy === 'save' ? '保存中…' : '保存人工修改'}</button></>}</div></aside>
    </div>
  </section>;
}

function ScoreGrid({ item }: { item: Opportunity }) {
  const scores = [['文化契合', item.culture_fit], ['市场拉力', item.market_pull], ['新颖度', item.novelty], ['视觉潜力', item.visual_potential], ['社交传播', item.social_shareability], ['产品可行', item.product_feasibility], ['文化风险', item.cultural_risk]] as const;
  return <div className="score-grid">{scores.map(([label, score]) => <div key={label}><span>{label}</span><div><i style={{ width: `${score}%` }} /></div><strong>{score}</strong></div>)}</div>;
}

function DesignView({ workspace, setWorkspace, designState, primaryOpportunity, generateDesign, busy }: {
  data: OpportunityPayload; workspace: Workspace; setWorkspace: React.Dispatch<React.SetStateAction<Workspace>>;
  designState: DesignState; primaryOpportunity: Opportunity | null; generateDesign: () => Promise<void>; busy: string;
}) {
  const design = designState.design;
  const product = design.product || {};
  const overrides = workspace.design_overrides || {};
  const updateOverride = (key: string, value: unknown) => setWorkspace((current) => ({ ...current, design_overrides: { ...current.design_overrides, [key]: value } }));
  const manualPrimary = workspace.selection_mode === 'manual' ? workspace.primary_opportunity_id : design.selection?.primary_opportunity_id;
  const canGenerate = workspace.selection_mode === 'auto' || Boolean(primaryOpportunity?.design_generator);
  return <section className="module-page"><SectionTitle code="04 / DESIGN WORKBENCH" title="从机会到设计，血缘必须完整" description="生成器只消费已保存的 Designer Handoff；每次运行记录输入 SHA、主机会、覆盖字段和输出文件。" />
    <div className="lineage-bar"><div><span>机会池</span><strong>{workspace.selected_opportunity_ids.join(' / ')}</strong></div><b>→</b><div><span>主机会</span><strong>{manualPrimary || '系统自动判定'}</strong></div><b>→</b><div><span>地域缩窄</span><strong>{design.cultural_elements?.[0]?.region || '待生成'}</strong></div><b>→</b><div><span>真实产物</span><strong>{product.product_name || '待生成'}</strong></div></div>
    <div className="design-workspace"><div className="design-editor"><div className="design-truth-note"><strong>“针格模块”从哪里来？</strong><p>{design.selection?.primary_opportunity_id} 提出“{primaryOpportunity?.culture_element || '支系差异'} × {primaryOpportunity?.trend_element || '可替换收藏'}”；Design Agent 为避免多支系混用，把首版缩窄到 {design.cultural_elements?.[0]?.region}，再生成“{product.product_name}”。</p></div><label>产品名称<input value={String(overrides.product_name || product.product_name || '')} onChange={(event) => updateOverride('product_name', event.target.value)} /></label><label>产品类型<input value={String(overrides.product_type || product.product_type || '')} onChange={(event) => updateOverride('product_type', event.target.value)} /></label><label>概念说明<textarea rows={4} value={String(overrides.concept_statement || product.concept_statement || '')} onChange={(event) => updateOverride('concept_statement', event.target.value)} /></label><label>形态说明<textarea rows={4} value={String(overrides.form_description || product.form_description || '')} onChange={(event) => updateOverride('form_description', event.target.value)} /></label><label>使用场景（逗号分隔）<input value={tags(overrides.use_scenarios || product.use_scenarios || []).join('，')} onChange={(event) => updateOverride('use_scenarios', tags(event.target.value))} /></label><label>海报标题<input value={String(overrides.poster_title || design.poster_request?.exact_copy?.title || '')} onChange={(event) => updateOverride('poster_title', event.target.value)} /></label><div className="generation-actions"><button className="primary-button wide" disabled={!canGenerate || busy === 'generate'} onClick={generateDesign}>{busy === 'generate' ? '真实生成中…' : '生成设计规格 + 首样结构图'}</button><button className="outline-button wide" disabled={!designState.image_generation.available} title={designState.image_generation.reason}>生成 / 重绘 AI 主视觉</button></div>{!canGenerate && <p className="blocked-copy">当前主机会没有匹配的真实设计生成器。请在机会池中补充明确产品形态；系统不会套用通用兜底模板。</p>}<p className="image-provider-note">主视觉状态：{designState.image_generation.available ? '服务已配置' : designState.image_generation.reason}</p></div>
      <div className="design-output"><div className="output-head"><div><span>{designState.selected_run_id === 'official' ? 'OFFICIAL OUTPUT' : 'TOOL RUN'}</span><strong>{design.design_id}</strong></div><a href={`${API}${designState.poster_url}`} target="_blank" rel="noreferrer">打开原图 ↗</a></div><img src={`${API}${designState.poster_url}?v=${encodeURIComponent(workspace.updated_at || design.generated_at || '')}`} alt={`${product.product_name || '当前设计'}结构与首样海报`} /><div className="output-tabs"><details open><summary>BOM / {design.manufacturing?.bill_of_materials?.length || 0} 项</summary><div className="bom-table">{design.manufacturing?.bill_of_materials?.map((item: Record<string, any>) => <div key={item.part_id}><span>{item.part_id}</span><strong>{item.component}</strong><small>{item.material}</small><b>{item.tolerance_or_target}</b></div>)}</div></details><details><summary>装配步骤 / {design.manufacturing?.assembly_steps?.length || 0} 步</summary><ol>{design.manufacturing?.assembly_steps?.map((step: string) => <li key={step}>{step}</li>)}</ol></details><details><summary>文化与工程门禁</summary><ul>{[...(design.cultural_review_gates || []), ...(design.engineering_review_gates || [])].map((gate: string) => <li key={gate}>{gate}</li>)}</ul></details></div></div>
    </div>
  </section>;
}

function RunsView({ summary, designState }: { summary: Summary; designState: DesignState }) {
  return <section className="module-page"><SectionTitle code="05 / RUN HISTORY" title="每一次生成都有记录" description="这里不只显示成功，也保留模式、引擎、输入 SHA 和明确的失败原因。" /><div className="run-layout"><div><h3>当前正式流水线</h3><div className="component-list">{summary.current_run.components.map((item) => <div key={item.component}><i className={item.mode === 'live' ? 'live' : item.mode === 'cache' ? 'cache' : 'blocked'} /><div><strong>{item.component}</strong><small>{item.engine}</small><p>{item.detail}</p></div><span>{item.mode.toUpperCase()}</span></div>)}</div></div><div><h3>工具内设计生成</h3>{designState.runs.length ? <div className="tool-run-list">{designState.runs.map((run) => <article key={run.run_id}><div><span>{run.run_id}</span><strong>{run.product_name}</strong></div><p>{run.primary_opportunity_id} · {run.design_engine}</p><div><code>{run.source_handoff_sha256?.slice(0, 16)}…</code><b>{run.render_kind}</b></div></article>)}</div> : <div className="empty-panel">尚未从工具内触发新的设计生成。当前显示的是仓库正式输出。</div>}</div></div></section>;
}
