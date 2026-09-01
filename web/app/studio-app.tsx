'use client';

/* Dynamic design assets are served by the audited Python API, so Next image
   optimization would hide the exact bytes and SHA-256 shown in the UI. */
/* eslint-disable @next/next/no-img-element */

import {
  Activity,
  ArrowRight,
  BookOpen,
  Check,
  ChevronDown,
  Clock3,
  Database,
  ExternalLink,
  FileDown,
  GitBranch,
  Home,
  Image as ImageIcon,
  Layers3,
  LibraryBig,
  LoaderCircle,
  Network,
  PackageOpen,
  PencilLine,
  Play,
  Plus,
  RefreshCw,
  Save,
  Search,
  Shapes,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  TriangleAlert,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  type FormEvent,
  type ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';

import {
  generateManualDesign,
  getCultureLibrary,
  getFormLibrary,
  getStudioDesign,
  getStudioEvents,
  getStudioOverview,
  listStudioDesigns,
  reviseStudioDesign,
  runCollectionLane,
  runDailyDesign,
  studioAssetUrl,
  updateDailySchedule,
} from './studio-api';
import type {
  CultureLibrary,
  CultureLibraryRecord,
  ProductFormLibrary,
  ProductFormRecord,
  StudioDesign,
  StudioEvent,
  StudioOverview,
} from './studio-model';
import { formatStudioTime, STUDIO_STATUS_LABELS } from './studio-model';

export type StudioView =
  | 'home'
  | 'culture'
  | 'forms'
  | 'create'
  | 'designs'
  | 'design'
  | 'edit'
  | 'operations';

const NAV_ITEMS = [
  { id: 'home', label: '今日设计', href: '/', icon: Home },
  { id: 'culture', label: '在地文化库', href: '/libraries/culture', icon: LibraryBig },
  { id: 'forms', label: '产品形态库', href: '/libraries/forms', icon: Shapes },
  { id: 'create', label: '自由组合', href: '/create', icon: Plus },
  { id: 'designs', label: '全部设计', href: '/designs', icon: ImageIcon },
  { id: 'operations', label: '运行中心', href: '/operations', icon: Activity },
] as const;

const PAGE_META: Record<StudioView, { title: string; description: string }> = {
  home: {
    title: '今日设计',
    description: '系统每天从两座知识库中选择最高分且互不重复的组合，最多生成 3 个概念设计。',
  },
  culture: {
    title: '在地文化内容库',
    description: '查看已经过来源核验的文化内容、可转译元素、边界和原始链接。',
  },
  forms: {
    title: '爆款产品形态库',
    description: '查看产品形态排名、历史样本、平台覆盖与代表原记录。',
  },
  create: {
    title: '自由组合',
    description: '自行选择 1–3 条文化内容和 1–3 个产品形态，立即生成可继续编辑的设计。',
  },
  designs: {
    title: '全部设计',
    description: '自动生成与手动创建的设计都保留版本、来源、评分和真实产物。',
  },
  design: {
    title: '设计详情',
    description: '先审阅结果与证据；确认值得继续后，再进入工作流逐步调整。',
  },
  edit: {
    title: '工作流编辑器',
    description: '调整内容、形态、融合文稿和视觉方向，并从变更点重新生成下游设计稿。',
  },
  operations: {
    title: '运行中心',
    description: '检查持续采集、每日生成、阻断原因、心跳、下次运行和历史事件。',
  },
};

function statusLabel(value: string) {
  return STUDIO_STATUS_LABELS[value] ?? (value || '未知');
}

function AppMark() {
  return (
    <div className="studio-mark" aria-hidden="true">
      <span />
      <span />
      <span />
      <span />
    </div>
  );
}

function StudioFrame({
  view,
  children,
  actions,
}: {
  view: StudioView;
  children: ReactNode;
  actions?: ReactNode;
}) {
  const meta = PAGE_META[view];
  return (
    <div className="studio-shell">
      <aside className="studio-sidebar" aria-label="产品导航">
        <Link className="studio-brand" href="/" aria-label="QianCraft 今日设计">
          <AppMark />
          <span>
            <strong>QianCraft</strong>
            <small>文化 × 形态设计系统</small>
          </span>
        </Link>
        <nav className="studio-nav">
          {NAV_ITEMS.map((item) => {
            const active = item.id === view || (view === 'design' && item.id === 'designs') || (view === 'edit' && item.id === 'designs');
            const Icon = item.icon;
            return (
              <a key={item.id} href={item.href} className={active ? 'is-active' : ''} aria-current={active ? 'page' : undefined}>
                <Icon size={18} strokeWidth={1.8} aria-hidden="true" />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>
        <div className="studio-sidebar__foot">
          <a href="/workflow">
            <Network size={17} aria-hidden="true" />
            高级流程画布
          </a>
          <p>概念设计工具</p>
          <small>止于生产前验证</small>
        </div>
      </aside>
      <div className="studio-workspace">
        <header className="studio-topbar">
          <div>
            <h1>{meta.title}</h1>
            <p>{meta.description}</p>
          </div>
          {actions ? <div className="studio-topbar__actions">{actions}</div> : null}
        </header>
        <main className="studio-main">{children}</main>
      </div>
    </div>
  );
}

function LoadingState({ label = '正在读取真实数据' }: { label?: string }) {
  return (
    <div className="studio-state" role="status">
      <LoaderCircle className="is-spinning" size={22} aria-hidden="true" />
      <strong>{label}</strong>
      <span>页面不会用占位数字替代接口结果。</span>
    </div>
  );
}

function ErrorState({ error, retry }: { error: string; retry?: () => void }) {
  return (
    <div className="studio-state studio-state--error" role="alert">
      <TriangleAlert size={22} aria-hidden="true" />
      <strong>真实接口没有返回可用结果</strong>
      <span>{error}</span>
      {retry ? <button type="button" onClick={retry}><RefreshCw size={17} />重新连接</button> : null}
    </div>
  );
}

function StatusPill({ status, children }: { status: string; children?: ReactNode }) {
  return (
    <span className="studio-status" data-status={status}>
      <i aria-hidden="true" />
      {children ?? statusLabel(status)}
    </span>
  );
}

function FactStrip({ overview }: { overview: StudioOverview }) {
  const facts = [
    {
      label: '在地文化库',
      value: overview.libraries.culture.recordCount,
      suffix: '条已核验记录',
      detail: `${overview.libraries.culture.sourceCount} 个登记来源`,
      href: '/libraries/culture',
    },
    {
      label: '产品形态库',
      value: overview.libraries.forms.recordCount,
      suffix: '种形态',
      detail: `${overview.libraries.forms.sampleSize} 条历史真实样本`,
      href: '/libraries/forms',
    },
    {
      label: '今日产出',
      value: overview.today.designCount,
      suffix: '个设计',
      detail: 'Top 3 是上限，不足不补位',
      href: '/designs',
    },
  ];
  return (
    <section className="studio-facts" aria-label="可核验数据概览">
      {facts.map((fact) => (
        <a key={fact.label} href={fact.href}>
          <span>{fact.label}</span>
          <strong>{fact.value}<small>{fact.suffix}</small></strong>
          <p>{fact.detail}</p>
          <ArrowRight size={18} aria-hidden="true" />
        </a>
      ))}
    </section>
  );
}

function DesignCard({ design, compact = false }: { design: StudioDesign; compact?: boolean }) {
  return (
    <article className={`studio-design-card ${compact ? 'is-compact' : ''}`}>
      <a className="studio-design-card__image" href={`/designs/${design.designId}`} aria-label={`查看设计：${design.title}`}>
        <img src={studioAssetUrl(design.asset.imageUrl)} alt={`${design.title}结构概念设计稿`} />
        {design.dailyRank ? <b>#{design.dailyRank}</b> : <b>手动</b>}
        <span>V{design.version}</span>
      </a>
      <div className="studio-design-card__body">
        <div className="studio-design-card__meta">
          <StatusPill status="generated">真实产物</StatusPill>
          <span>{design.scores.overall.toFixed(1)} 分</span>
        </div>
        <h2><a href={`/designs/${design.designId}`}>{design.title}</a></h2>
        <p>{design.subtitle}</p>
        <div className="studio-design-card__tags">
          {design.concept.contentTranslation.slice(0, 2).map((item) => <span key={item}>{item}</span>)}
          {design.productForms.map((item) => <span key={item.id}>{item.name}</span>)}
        </div>
        <footer>
          <span>{formatStudioTime(design.updatedAt)}</span>
          <a href={`/designs/${design.designId}`}>查看依据与工作流 <ArrowRight size={16} /></a>
        </footer>
      </div>
    </article>
  );
}

function HomePage() {
  const [overview, setOverview] = useState<StudioOverview | null>(null);
  const [error, setError] = useState('');
  const [running, setRunning] = useState(false);

  const load = useCallback(async () => {
    try {
      const payload = await getStudioOverview();
      setOverview(payload);
      setError('');
      return payload;
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
      return null;
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  useEffect(() => {
    if (!overview || (overview.today.designCount > 0 && overview.automation.dailyDesign.daily.status !== 'running')) return;
    const timer = window.setInterval(() => void load(), 1800);
    return () => window.clearInterval(timer);
  }, [load, overview]);

  const runNow = async () => {
    setRunning(true);
    setError('');
    try {
      await runDailyDesign();
      for (let attempt = 0; attempt < 30; attempt += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 700));
        const payload = await load();
        if (payload && payload.automation.dailyDesign.daily.status !== 'running') break;
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setRunning(false);
    }
  };

  return (
    <StudioFrame
      view="home"
      actions={(
        <>
          {overview ? <StatusPill status={overview.automation.dailyDesign.daily.status}>自动化 {statusLabel(overview.automation.dailyDesign.daily.status)}</StatusPill> : null}
          <button className="studio-primary" type="button" onClick={runNow} disabled={running || overview?.automation.dailyDesign.daily.status === 'running'}>
            {running || overview?.automation.dailyDesign.daily.status === 'running' ? <LoaderCircle className="is-spinning" size={17} /> : <Play size={17} />}
            立即重跑今日 Top 3
          </button>
        </>
      )}
    >
      {!overview && !error ? <LoadingState label="正在读取今日设计与两座知识库" /> : null}
      {error ? <ErrorState error={error} retry={() => void load()} /> : null}
      {overview ? (
        <>
          <FactStrip overview={overview} />
          <section className="studio-section-heading">
            <div>
              <span>{overview.today.date}</span>
              <h2>今天自动选出的设计</h2>
              <p>{overview.today.policy}</p>
            </div>
            <a href="/create"><Plus size={17} />自己搭配一个</a>
          </section>
          {overview.today.designs.length ? (
            <section className="studio-design-grid">
              {overview.today.designs.map((design) => <DesignCard key={design.designId} design={design} />)}
            </section>
          ) : (
            <section className="studio-empty">
              <Clock3 size={26} />
              <h2>今天还没有通过门槛的设计</h2>
              <p>{overview.automation.dailyDesign.daily.detail}</p>
            </section>
          )}
          <section className="studio-automation-band">
            <div>
              <span className="studio-eyebrow">AUTOMATION</span>
              <h2>双库持续维护，设计每日生成</h2>
              <p>采集负责更新原始材料；每日任务只读取已晋级的文化记录与有真实样本的产品形态。</p>
            </div>
            {(['culture_watch', 'market_refresh'] as const).map((laneId) => {
              const lane = overview.automation.collection.lanes[laneId];
              return (
                <a href="/operations" key={laneId}>
                  <StatusPill status={lane.status} />
                  <strong>{lane.label}</strong>
                  <span>{lane.detail}</span>
                  <small>下次 {formatStudioTime(lane.nextRunAt)}</small>
                </a>
              );
            })}
            <a href="/operations">
              <StatusPill status={overview.automation.dailyDesign.daily.status} />
              <strong>每日 Top 3</strong>
              <span>{overview.automation.dailyDesign.daily.detail}</span>
              <small>下次 {formatStudioTime(overview.automation.dailyDesign.daily.nextRunAt)}</small>
            </a>
          </section>
          <p className="studio-truth-note"><ShieldCheck size={17} />{overview.truthBoundary}</p>
        </>
      ) : null}
    </StudioFrame>
  );
}

function CultureCard({ record }: { record: CultureLibraryRecord }) {
  return (
    <article className="studio-library-card">
      <header>
        <span>{record.category}</span>
        <b>{record.evidenceScore.toFixed(1)}<small>证据分</small></b>
      </header>
      <h2>{record.name}</h2>
      <p>{record.region.slice(0, 3).join(' · ')}</p>
      <dl>
        <div><dt>可转译</dt><dd>{record.modernizableElements.slice(0, 3).join('；')}</dd></div>
        <div><dt>工艺</dt><dd>{record.crafts.slice(0, 4).join('、') || '以叙事与场景为主'}</dd></div>
        <div><dt>边界</dt><dd>{record.nonTransferableElements[0] || '按来源与社区核验结果执行'}</dd></div>
        <div><dt>计分</dt><dd>{record.evidenceScoreBreakdown.formula}（{record.evidenceScoreBreakdown.sourceSufficiency.toFixed(1)} / {record.evidenceScoreBreakdown.regionalSpecificity.toFixed(1)} / {record.evidenceScoreBreakdown.translationCompleteness.toFixed(1)}）</dd></div>
      </dl>
      <details>
        <summary>{record.sourceRefs.length} 条来源 <ChevronDown size={16} /></summary>
        <div className="studio-source-list">
          {record.sourceDetails.map((source) => (
            <a key={source.source_id} href={source.source_url} target="_blank" rel="noreferrer">
              <span>{source.source_id}</span>
              <strong>{source.source_title}</strong>
              <small>{source.publisher}</small>
              <ExternalLink size={14} />
            </a>
          ))}
        </div>
      </details>
    </article>
  );
}

function CulturePage() {
  const [library, setLibrary] = useState<CultureLibrary | null>(null);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('全部');
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    try {
      setLibrary(await getCultureLibrary());
      setError('');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    }
  }, []);
  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);
  const categories = useMemo(() => ['全部', ...new Set(library?.records.map((item) => item.category) ?? [])], [library]);
  const filtered = useMemo(() => (library?.records ?? []).filter((item) => {
    const haystack = [item.name, ...item.aliases, ...item.region, ...item.crafts, ...item.modernizableElements].join(' ').toLowerCase();
    return (category === '全部' || item.category === category) && (!query || haystack.includes(query.toLowerCase()));
  }), [category, library, query]);
  return (
    <StudioFrame view="culture" actions={<a className="studio-primary" href="/create"><Plus size={17} />用文化内容创建设计</a>}>
      {!library && !error ? <LoadingState /> : null}
      {error ? <ErrorState error={error} retry={() => void load()} /> : null}
      {library ? (
        <>
          <section className="studio-document-head">
            <div><BookOpen size={23} /><span>持续维护文档</span></div>
            <strong>{library.recordCount}<small>条正式记录</small></strong>
            <strong>{library.sourceCount}<small>个登记来源</small></strong>
            <p>{library.promotionPolicy}</p>
          </section>
          <div className="studio-filterbar">
            <label><Search size={17} /><span className="sr-only">搜索文化记录</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索文化、地域、工艺或可转译元素" /></label>
            <label><span className="sr-only">按类别筛选</span><select value={category} onChange={(event) => setCategory(event.target.value)}>{categories.map((item) => <option key={item}>{item}</option>)}</select></label>
            <span>{filtered.length} / {library.recordCount}</span>
          </div>
          <section className="studio-library-grid">
            {filtered.map((record) => <CultureCard key={record.id} record={record} />)}
          </section>
        </>
      ) : null}
    </StudioFrame>
  );
}

function metricTotal(post: ProductFormRecord['representativePosts'][number]) {
  return post.likes + post.favorites + post.comments + post.shares + post.views;
}

function FormPage() {
  const [library, setLibrary] = useState<ProductFormLibrary | null>(null);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    try {
      setLibrary(await getFormLibrary());
      setError('');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    }
  }, []);
  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);
  return (
    <StudioFrame view="forms" actions={<a className="studio-primary" href="/create"><Plus size={17} />选择形态开始组合</a>}>
      {!library && !error ? <LoadingState /> : null}
      {error ? <ErrorState error={error} retry={() => void load()} /> : null}
      {library ? (
        <>
          <section className="studio-document-head studio-document-head--forms">
            <div><Database size={23} /><span>历史证据文档</span></div>
            <strong>{library.recordCount}<small>种产品形态</small></strong>
            <strong>{library.sampleSize}<small>条真实样本</small></strong>
            <p>{library.evidenceBoundary}</p>
          </section>
          <p className="studio-method-note"><ShieldCheck size={17} />{library.methodology.cross_platform_hot_score} {library.methodology.claim_boundary}</p>
          <section className="studio-form-table" aria-label="产品形态排名">
            <header><span>排名 / 形态</span><span>跨平台热度</span><span>样本 / 覆盖</span><span>为什么进入榜单</span><span>原记录</span></header>
            {library.records.map((record) => (
              <article key={record.id}>
                <div className="studio-form-title"><b>{String(record.rank).padStart(2, '0')}</b><span><strong>{record.name}</strong><small>{record.rendererLabel} · {record.executable ? '可生成' : '未支持'}</small></span></div>
                <div className="studio-score-cell"><strong>{record.hotScore.toFixed(1)}</strong><meter min="0" max="100" value={record.hotScore}>{record.hotScore}</meter></div>
                <div><strong>{record.sampleSize} 条</strong><small>{record.platformCoverage} / 4 平台</small></div>
                <ul>{record.whyHot.slice(0, 3).map((reason) => <li key={reason}>{reason}</li>)}</ul>
                <details><summary>{record.representativePosts.length} 条 <ChevronDown size={15} /></summary><div className="studio-post-popover">{record.representativePosts.map((post) => <a key={post.source_ref} href={post.url} target="_blank" rel="noreferrer"><span>{post.platform.toUpperCase()} · {post.source_ref}</span><strong>{post.title || post.content.slice(0, 70)}</strong><small>{new Intl.NumberFormat('zh-CN').format(metricTotal(post))} 次可见互动/播放汇总</small><ExternalLink size={14} /></a>)}</div></details>
              </article>
            ))}
          </section>
        </>
      ) : null}
    </StudioFrame>
  );
}

function toggleLimited(current: string[], value: string, limit: number) {
  if (current.includes(value)) return current.filter((item) => item !== value);
  return current.length >= limit ? current : [...current, value];
}

function SelectionBadge({ selected, index }: { selected: boolean; index?: number }) {
  return <span className="studio-selection-badge">{selected ? index ?? <Check size={14} /> : <Plus size={14} />}</span>;
}

function CreatePage() {
  const router = useRouter();
  const [culture, setCulture] = useState<CultureLibrary | null>(null);
  const [forms, setForms] = useState<ProductFormLibrary | null>(null);
  const [cultureIds, setCultureIds] = useState<string[]>([]);
  const [formIds, setFormIds] = useState<string[]>([]);
  const [title, setTitle] = useState('');
  const [concept, setConcept] = useState('');
  const [palette, setPalette] = useState('slate');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    void Promise.all([getCultureLibrary(), getFormLibrary()])
      .then(([culturePayload, formPayload]) => { setCulture(culturePayload); setForms(formPayload); })
      .catch((cause) => setError(cause instanceof Error ? cause.message : String(cause)));
  }, []);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!cultureIds.length || !formIds.length) {
      setError('请至少选择 1 条文化内容和 1 个产品形态。');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const design = await generateManualDesign({ cultureIds, productFormIds: formIds, title, concept, palette });
      router.push(`/designs/${design.designId}`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
      setSubmitting(false);
    }
  };
  return (
    <StudioFrame view="create">
      {!culture || !forms ? (error ? <ErrorState error={error} /> : <LoadingState label="正在读取可选文化内容与产品形态" />) : (
        <form className="studio-composer" onSubmit={submit}>
          <div className="studio-composer__steps">
            <section>
              <header><span>01</span><div><h2>选择文化内容</h2><p>可选 1–3 条，所有条目都来自正式文化库。</p></div><b>{cultureIds.length} / 3</b></header>
              <div className="studio-choice-grid">
                {culture.records.map((record) => {
                  const selected = cultureIds.includes(record.id);
                  return <button key={record.id} type="button" className={selected ? 'is-selected' : ''} aria-pressed={selected} onClick={() => setCultureIds((value) => toggleLimited(value, record.id, 3))}><SelectionBadge selected={selected} index={selected ? cultureIds.indexOf(record.id) + 1 : undefined} /><span><strong>{record.name}</strong><small>{record.category} · {record.sourceRefs.length} 条来源</small><em>{record.modernizableElements[0]}</em></span></button>;
                })}
              </div>
            </section>
            <section>
              <header><span>02</span><div><h2>选择产品形态</h2><p>可选 1–3 个，排名和样本来自历史真实平台快照。</p></div><b>{formIds.length} / 3</b></header>
              <div className="studio-form-choice-grid">
                {forms.records.map((record) => {
                  const selected = formIds.includes(record.id);
                  return <button key={record.id} type="button" className={selected ? 'is-selected' : ''} aria-pressed={selected} disabled={!record.executable} onClick={() => setFormIds((value) => toggleLimited(value, record.id, 3))}><SelectionBadge selected={selected} index={selected ? formIds.indexOf(record.id) + 1 : undefined} /><b>{String(record.rank).padStart(2, '0')}</b><span><strong>{record.name}</strong><small>{record.sampleSize} 条样本 · {record.hotScore.toFixed(1)} 热度</small></span></button>;
                })}
              </div>
            </section>
            <section>
              <header><span>03</span><div><h2>可选的人工要求</h2><p>不填则由系统基于所选内容与形态生成。</p></div></header>
              <div className="studio-form-fields">
                <label>设计名称<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="例如：花溪针脚旅行徽章" maxLength={80} /></label>
                <label className="is-wide">融合想法<textarea value={concept} onChange={(event) => setConcept(event.target.value)} placeholder="可以指定要保留的文化内容、使用动作或不希望出现的表达。" maxLength={500} rows={4} /></label>
                <fieldset><legend>结构概念板配色</legend>{(['slate', 'indigo', 'vermilion'] as const).map((item) => <label key={item}><input type="radio" name="palette" value={item} checked={palette === item} onChange={() => setPalette(item)} /><span className={`studio-palette studio-palette--${item}`} />{item === 'slate' ? '冷灰蓝' : item === 'indigo' ? '靛青石' : '赭朱纸'}</label>)}</fieldset>
              </div>
            </section>
          </div>
          <aside className="studio-composer__summary">
            <span className="studio-eyebrow">COMBINATION</span>
            <h2>本次组合</h2>
            <div><small>文化内容</small>{cultureIds.length ? cultureIds.map((id) => <strong key={id}>{culture.records.find((item) => item.id === id)?.name}</strong>) : <p>尚未选择</p>}</div>
            <div><small>产品形态</small>{formIds.length ? formIds.map((id) => <strong key={id}>{id}</strong>) : <p>尚未选择</p>}</div>
            <p className="studio-composer__truth"><ShieldCheck size={17} />提交后系统会重新验证 ID、来源、样本和渲染器；不满足门槛会直接失败。</p>
            {error ? <p className="studio-inline-error" role="alert">{error}</p> : null}
            <button className="studio-primary" type="submit" disabled={submitting || !cultureIds.length || !formIds.length}>{submitting ? <LoaderCircle className="is-spinning" size={18} /> : <Sparkles size={18} />}生成设计</button>
          </aside>
        </form>
      )}
    </StudioFrame>
  );
}

function DesignsPage() {
  const [designs, setDesigns] = useState<StudioDesign[] | null>(null);
  const [filter, setFilter] = useState<'all' | 'daily' | 'manual'>('all');
  const [error, setError] = useState('');
  useEffect(() => { void listStudioDesigns().then((payload) => setDesigns(payload.designs)).catch((cause) => setError(cause instanceof Error ? cause.message : String(cause))); }, []);
  const filtered = (designs ?? []).filter((item) => !item.superseded && (filter === 'all' || item.origin === filter));
  return (
    <StudioFrame view="designs" actions={<a className="studio-primary" href="/create"><Plus size={17} />新建设计</a>}>
      {!designs && !error ? <LoadingState /> : null}
      {error ? <ErrorState error={error} /> : null}
      {designs ? <><div className="studio-tabs" role="group" aria-label="设计来源筛选">{([['all', '全部'], ['daily', '每日自动'], ['manual', '手动组合']] as const).map(([id, label]) => <button key={id} type="button" className={filter === id ? 'is-active' : ''} aria-pressed={filter === id} onClick={() => setFilter(id)}>{label}<span>{designs.filter((item) => !item.superseded && (id === 'all' || item.origin === id)).length}</span></button>)}</div><section className="studio-design-grid studio-design-grid--archive">{filtered.map((design) => <DesignCard key={design.designId} design={design} compact />)}</section>{!filtered.length ? <div className="studio-empty"><PackageOpen size={26} /><h2>这个分类还没有设计</h2><a href="/create">创建第一个</a></div> : null}</> : null}
    </StudioFrame>
  );
}

function ScoreBreakdown({ design }: { design: StudioDesign }) {
  const rows = [
    ['文化证据', design.scores.cultureEvidence],
    ['形态热度', design.scores.marketEvidence],
    ['品类兼容', design.scores.compatibility],
    ['转译空间', design.scores.translationSpace],
    ['边界安全', design.scores.boundarySafety],
  ] as const;
  return <div className="studio-score-breakdown">{rows.map(([label, value]) => <div key={label}><span>{label}</span><meter min="0" max="100" value={value}>{value}</meter><b>{value.toFixed(1)}</b></div>)}<p>{design.scores.formula} · {design.scores.scoreVersion}</p></div>;
}

function DesignPage({ designId }: { designId: string }) {
  const [design, setDesign] = useState<StudioDesign | null>(null);
  const [error, setError] = useState('');
  useEffect(() => { void getStudioDesign(designId).then(setDesign).catch((cause) => setError(cause instanceof Error ? cause.message : String(cause))); }, [designId]);
  return (
    <StudioFrame view="design" actions={design ? <><a className="studio-secondary" href={studioAssetUrl(design.asset.imageUrl)} download><FileDown size={17} />下载设计稿</a><a className="studio-primary" href={`/designs/${design.designId}/edit`}><PencilLine size={17} />进入工作流编辑</a></> : undefined}>
      {!design && !error ? <LoadingState /> : null}
      {error ? <ErrorState error={error} /> : null}
      {design ? (
        <div className="studio-design-detail">
          <section className="studio-design-hero">
            <div className="studio-design-hero__image"><img src={studioAssetUrl(design.asset.imageUrl)} alt={`${design.title}结构概念设计稿`} /><span>真实生成 · 本地结构渲染器 · V{design.version}</span></div>
            <div className="studio-design-hero__copy"><div><StatusPill status="generated" /><span>{design.origin === 'daily' ? `每日自动 #${design.dailyRank}` : '手动组合'}</span></div><h2>{design.title}</h2><p className="studio-design-subtitle">{design.subtitle}</p><p>{design.concept.statement}</p><dl><div><dt>组合评分</dt><dd>{design.scores.overall.toFixed(1)}</dd></div><div><dt>市场样本</dt><dd>{design.provenance.marketSampleSize} 条</dd></div><div><dt>来源引用</dt><dd>{design.provenance.cultureSourceRefs.length + design.provenance.marketSourceRefs.length} 条</dd></div></dl><a href={`/designs/${design.designId}/edit`}>调整内容、形态或文稿 <ArrowRight size={17} /></a></div>
          </section>
          <section className="studio-detail-grid">
            <article><span className="studio-eyebrow">CONTENT</span><h2>采用的文化内容</h2>{design.cultureItems.map((item) => <div className="studio-evidence-row" key={item.id}><span><strong>{item.name}</strong><small>{item.category} · {item.region.slice(0, 2).join(' / ')}</small></span><b>{item.sourceRefs.length} 条来源</b><details><summary>查看来源</summary><div>{item.sourceDetails.map((source) => <a key={source.source_id} href={source.source_url} target="_blank" rel="noreferrer">{source.source_id} · {source.source_title}<ExternalLink size={13} /></a>)}</div></details></div>)}</article>
            <article><span className="studio-eyebrow">FORM</span><h2>采用的产品形态</h2>{design.productForms.map((item) => <div className="studio-evidence-row" key={item.id}><span><strong>{item.name}</strong><small>榜单第 {item.rank} · 热度 {item.hotScore.toFixed(1)}</small></span><b>{item.sampleSize} 条样本</b><details><summary>查看代表原记录</summary><div>{item.representativePosts.map((post) => <a key={post.source_ref} href={post.url} target="_blank" rel="noreferrer">{post.platform.toUpperCase()} · {post.title || post.content.slice(0, 40)}<ExternalLink size={13} /></a>)}</div></details></div>)}</article>
            <article><span className="studio-eyebrow">SCORE</span><h2>评分是怎么来的</h2><ScoreBreakdown design={design} /></article>
            <article><span className="studio-eyebrow">LINEAGE</span><h2>产物与谱系</h2><dl className="studio-provenance"><div><dt>设计编号</dt><dd>{design.designId}</dd></div><div><dt>批次</dt><dd>{design.batchId}</dd></div><div><dt>生成时间</dt><dd>{formatStudioTime(design.asset.generatedAt)}</dd></div><div><dt>渲染方式</dt><dd>{design.provenance.renderer}</dd></div><div><dt>图像模型</dt><dd>{design.provenance.imageGenerationUsed ? '使用' : '未使用'}</dd></div><div><dt>SHA-256</dt><dd title={design.asset.sha256}>{design.asset.sha256.slice(0, 18)}…</dd></div></dl>{design.revisionHistory.length ? <details className="studio-version-log"><summary>查看 {design.revisionHistory.length} 个历史版本 <ChevronDown size={15} /></summary><ol>{[...design.revisionHistory].reverse().map((revision) => <li key={`${revision.version}-${revision.assetSha256}`}><span><strong>V{revision.version} · {revision.title}</strong><small>{revision.cultureNames.join(' × ')} / {revision.productFormNames.join(' + ')} · {revision.scoreOverall.toFixed(1)} 分</small><small>{formatStudioTime(revision.at)} · SHA {revision.assetSha256.slice(0, 12)}…</small></span><a href={studioAssetUrl(revision.imageUrl)} download>下载旧稿</a></li>)}</ol></details> : null}<p className="studio-boundary"><ShieldCheck size={17} />{design.provenance.claim}</p></article>
          </section>
          <section className="studio-workflow-preview"><div><span className="studio-eyebrow">WORKFLOW</span><h2>需要改动时再进入工作流</h2><p>每个阶段都显示当前状态；内容、形态、融合文稿和设计稿可重新生成，生产前验证保持明确未完成。</p></div><ol>{design.workflow.stages.map((stage, index) => <li key={stage.id} data-status={stage.status}><b>{String(index + 1).padStart(2, '0')}</b><span><strong>{stage.label}</strong><small>{statusLabel(stage.status)}</small></span>{stage.editable ? <Check size={16} /> : <TriangleAlert size={16} />}</li>)}</ol><a className="studio-primary" href={`/designs/${design.designId}/edit`}><SlidersHorizontal size={17} />打开工作流编辑器</a></section>
          <p className="studio-truth-note studio-truth-note--warning"><TriangleAlert size={17} />{design.production.boundary}</p>
        </div>
      ) : null}
    </StudioFrame>
  );
}

type EditStage = 'content' | 'form' | 'fusion' | 'visual' | 'production';

function EditPage({ designId }: { designId: string }) {
  const [design, setDesign] = useState<StudioDesign | null>(null);
  const [culture, setCulture] = useState<CultureLibrary | null>(null);
  const [forms, setForms] = useState<ProductFormLibrary | null>(null);
  const [stage, setStage] = useState<EditStage>('content');
  const [cultureIds, setCultureIds] = useState<string[]>([]);
  const [formIds, setFormIds] = useState<string[]>([]);
  const [title, setTitle] = useState('');
  const [concept, setConcept] = useState('');
  const [audience, setAudience] = useState('');
  const [useScenario, setUseScenario] = useState('');
  const [designNotes, setDesignNotes] = useState('');
  const [palette, setPalette] = useState('slate');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    void Promise.all([getStudioDesign(designId), getCultureLibrary(), getFormLibrary()]).then(([current, culturePayload, formPayload]) => {
      setDesign(current); setCulture(culturePayload); setForms(formPayload);
      setCultureIds(current.cultureItems.map((item) => item.id));
      setFormIds(current.productForms.map((item) => item.id));
      setTitle(current.title); setConcept(current.concept.statement); setAudience(current.concept.audience);
      setUseScenario(current.concept.useScenarios[0] ?? ''); setDesignNotes(current.concept.designNotes);
      setPalette(current.visualDirection.palette);
    }).catch((cause) => setError(cause instanceof Error ? cause.message : String(cause)));
  }, [designId]);
  const save = async () => {
    if (!design) return;
    setSaving(true); setError('');
    try {
      const updated = await reviseStudioDesign(design.designId, { cultureIds, productFormIds: formIds, title, concept, audience, useScenario, designNotes, palette });
      setDesign(updated);
      setStage('visual');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally { setSaving(false); }
  };
  const stages: Array<{ id: EditStage; label: string; icon: typeof Layers3 }> = [
    { id: 'content', label: '文化内容', icon: LibraryBig },
    { id: 'form', label: '产品形态', icon: Shapes },
    { id: 'fusion', label: '融合方案', icon: GitBranch },
    { id: 'visual', label: '设计稿', icon: ImageIcon },
    { id: 'production', label: '生产前验证', icon: ShieldCheck },
  ];
  return (
    <StudioFrame view="edit" actions={design ? <><a className="studio-secondary" href={`/designs/${design.designId}`}>返回设计详情</a><button className="studio-primary" type="button" onClick={save} disabled={saving}>{saving ? <LoaderCircle className="is-spinning" size={17} /> : <RefreshCw size={17} />}从此重新生成</button></> : undefined}>
      {!design || !culture || !forms ? (error ? <ErrorState error={error} /> : <LoadingState label="正在载入设计工作流" />) : (
        <div className="studio-editor">
          <aside className="studio-editor__stages" aria-label="设计工作流阶段">{stages.map((item, index) => { const Icon = item.icon; return <button key={item.id} type="button" className={stage === item.id ? 'is-active' : ''} onClick={() => setStage(item.id)}><b>{String(index + 1).padStart(2, '0')}</b><Icon size={18} /><span>{item.label}</span>{item.id === 'production' ? <TriangleAlert size={15} /> : <Check size={15} />}</button>; })}<a href={`/workflow?design=${design.designId}`}><Network size={17} />查看高级流程画布</a></aside>
          <section className="studio-editor__panel">
            {stage === 'content' ? <><header><span>01 / CONTENT</span><h2>调整文化内容</h2><p>替换或增加内容会使融合方案和设计稿重新生成；来源事实本身不可编辑。</p></header><div className="studio-editor-choice-list">{culture.records.map((record) => { const selected = cultureIds.includes(record.id); return <button key={record.id} type="button" className={selected ? 'is-selected' : ''} aria-pressed={selected} onClick={() => setCultureIds((value) => toggleLimited(value, record.id, 3))}><SelectionBadge selected={selected} index={selected ? cultureIds.indexOf(record.id) + 1 : undefined} /><span><strong>{record.name}</strong><small>{record.category} · {record.sourceRefs.length} 条来源</small><em>{record.modernizableElements.slice(0, 2).join('；')}</em></span></button>; })}</div></> : null}
            {stage === 'form' ? <><header><span>02 / FORM</span><h2>替换或增加产品形态</h2><p>所有选项都来自形态库；热度、样本和代表原记录保持只读。</p></header><div className="studio-editor-form-list">{forms.records.map((record) => { const selected = formIds.includes(record.id); return <button key={record.id} type="button" className={selected ? 'is-selected' : ''} aria-pressed={selected} onClick={() => setFormIds((value) => toggleLimited(value, record.id, 3))}><SelectionBadge selected={selected} index={selected ? formIds.indexOf(record.id) + 1 : undefined} /><b>#{record.rank}</b><span><strong>{record.name}</strong><small>{record.sampleSize} 条样本 · {record.platformCoverage}/4 平台 · {record.hotScore.toFixed(1)}</small></span></button>; })}</div></> : null}
            {stage === 'fusion' ? <><header><span>03 / FUSION</span><h2>编辑融合方案</h2><p>这里是可人工改写的方案文稿；保存后会形成新版本，不覆盖历史设计稿。</p></header><div className="studio-editor-fields"><label>设计名称<input value={title} onChange={(event) => setTitle(event.target.value)} maxLength={80} /></label><label>目标人群<input value={audience} onChange={(event) => setAudience(event.target.value)} maxLength={120} /></label><label>使用场景<input value={useScenario} onChange={(event) => setUseScenario(event.target.value)} maxLength={120} /></label><label className="is-wide">融合方案<textarea value={concept} onChange={(event) => setConcept(event.target.value)} rows={7} maxLength={500} /></label><label className="is-wide">给设计环节的补充要求<textarea value={designNotes} onChange={(event) => setDesignNotes(event.target.value)} rows={4} maxLength={500} placeholder="例如：更强调可替换结构；不要出现人物形象。" /></label></div></> : null}
            {stage === 'visual' ? <><header><span>04 / VISUAL</span><h2>设计稿与视觉方向</h2><p>当前图像是实际落盘的结构概念板。切换配色并重新生成会产生新版本与新 SHA-256。</p></header><div className="studio-editor-visual"><img src={studioAssetUrl(design.asset.imageUrl)} alt={`${design.title} V${design.version} 设计稿`} /><div><strong>版本 V{design.version}</strong><span>{design.visualDirection.rendererLabel}</span><small>{design.asset.width} × {design.asset.height} px</small><fieldset><legend>配色方向</legend>{(['slate', 'indigo', 'vermilion'] as const).map((item) => <label key={item}><input type="radio" value={item} checked={palette === item} onChange={() => setPalette(item)} /><span className={`studio-palette studio-palette--${item}`} />{item === 'slate' ? '冷灰蓝' : item === 'indigo' ? '靛青石' : '赭朱纸'}</label>)}</fieldset><p>{design.provenance.claim}</p></div></div></> : null}
            {stage === 'production' ? <><header><span>05 / PRODUCTION</span><h2>生产前验证</h2><p>这一步不会被自动标成完成。以下事项需要社区、工程、工厂和合规人员提供真实结果。</p></header><div className="studio-production-gates">{['地域与工艺表述共同审核', '文化内容商品化授权与收益机制', '材料、结构、耐久与安全测试', '成本、工艺、公差和供应商确认', '销售地区适用法规与标签'].map((item, index) => <div key={item}><b>{String(index + 1).padStart(2, '0')}</b><span><strong>{item}</strong><small>尚无可核验完成记录</small></span><StatusPill status="not_ready" /></div>)}</div><p className="studio-boundary"><TriangleAlert size={17} />{design.production.boundary}</p></> : null}
            {error ? <p className="studio-inline-error" role="alert">{error}</p> : null}
          </section>
          <aside className="studio-editor__result"><span className="studio-eyebrow">CURRENT RESULT</span><img src={studioAssetUrl(design.asset.imageUrl)} alt="当前设计稿缩略图" /><h2>{title}</h2><p>{cultureIds.map((id) => culture.records.find((item) => item.id === id)?.name).filter(Boolean).join(' × ')}</p><p>{formIds.join(' + ')}</p><dl><div><dt>当前版本</dt><dd>V{design.version}</dd></div><div><dt>组合评分</dt><dd>{design.scores.overall.toFixed(1)}</dd></div><div><dt>上次生成</dt><dd>{formatStudioTime(design.updatedAt)}</dd></div></dl><button className="studio-primary" type="button" onClick={save} disabled={saving || !cultureIds.length || !formIds.length}>{saving ? <LoaderCircle className="is-spinning" size={17} /> : <Save size={17} />}保存并重新生成</button></aside>
        </div>
      )}
    </StudioFrame>
  );
}

function OperationLane({
  title,
  status,
  detail,
  nextRun,
  lastSuccess,
  interval,
  onRun,
  disabled,
}: {
  title: string;
  status: string;
  detail: string;
  nextRun: string;
  lastSuccess: string;
  interval: string;
  onRun: () => void;
  disabled: boolean;
}) {
  return <article className="studio-operation-lane"><header><div><StatusPill status={status} /><h2>{title}</h2></div><button type="button" onClick={onRun} disabled={disabled}>{disabled ? <LoaderCircle className="is-spinning" size={17} /> : <Play size={17} />}立即运行</button></header><p>{detail}</p><dl><div><dt>计划</dt><dd>{interval}</dd></div><div><dt>上次成功</dt><dd>{formatStudioTime(lastSuccess)}</dd></div><div><dt>下次运行</dt><dd>{formatStudioTime(nextRun)}</dd></div></dl></article>;
}

function OperationsPage() {
  const [overview, setOverview] = useState<StudioOverview | null>(null);
  const [events, setEvents] = useState<StudioEvent[]>([]);
  const [error, setError] = useState('');
  const [running, setRunning] = useState('');
  const [hour, setHour] = useState(7);
  const [minute, setMinute] = useState(0);
  const load = useCallback(async () => {
    try {
      const [payload, eventPayload] = await Promise.all([getStudioOverview(), getStudioEvents(40)]);
      setOverview(payload); setEvents(eventPayload.events); setHour(payload.automation.dailyDesign.schedule.hour); setMinute(payload.automation.dailyDesign.schedule.minute); setError('');
    } catch (cause) { setError(cause instanceof Error ? cause.message : String(cause)); }
  }, []);
  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);
  const run = async (id: 'culture_watch' | 'market_refresh' | 'daily') => {
    setRunning(id); setError('');
    try { if (id === 'daily') await runDailyDesign(); else await runCollectionLane(id); await new Promise((resolve) => window.setTimeout(resolve, 800)); await load(); } catch (cause) { setError(cause instanceof Error ? cause.message : String(cause)); } finally { setRunning(''); }
  };
  const saveSchedule = async () => { setRunning('schedule'); try { await updateDailySchedule({ hour, minute }); await load(); } catch (cause) { setError(cause instanceof Error ? cause.message : String(cause)); } finally { setRunning(''); } };
  return (
    <StudioFrame view="operations" actions={overview ? <StatusPill status={overview.automation.dailyDesign.scheduler.threadAlive && overview.automation.collection.scheduler.threadAlive ? 'healthy' : 'failed'}>两个调度线程{overview.automation.dailyDesign.scheduler.threadAlive && overview.automation.collection.scheduler.threadAlive ? '在线' : '异常'}</StatusPill> : undefined}>
      {!overview && !error ? <LoadingState /> : null}
      {error ? <ErrorState error={error} retry={() => void load()} /> : null}
      {overview ? <><section className="studio-operation-summary"><div><Activity size={22} /><span><strong>自动化总览</strong><small>心跳来自实际进程，不是页面定时器</small></span></div><dl><div><dt>采集线程</dt><dd>{overview.automation.collection.scheduler.threadAlive ? '在线' : '离线'}</dd></div><div><dt>设计线程</dt><dd>{overview.automation.dailyDesign.scheduler.threadAlive ? '在线' : '离线'}</dd></div><div><dt>今日设计</dt><dd>{overview.today.designCount} / 3</dd></div><div><dt>市场实时前置</dt><dd>{overview.automation.collection.market.preflight.research_ready ? '就绪' : '受阻'}</dd></div></dl></section><section className="studio-operation-grid"><OperationLane title="文化来源巡检" status={overview.automation.collection.lanes.culture_watch.status} detail={overview.automation.collection.lanes.culture_watch.detail} nextRun={overview.automation.collection.lanes.culture_watch.nextRunAt} lastSuccess={overview.automation.collection.lanes.culture_watch.lastSuccessAt} interval={`每 ${overview.automation.collection.lanes.culture_watch.intervalMinutes} 分钟`} onRun={() => void run('culture_watch')} disabled={running === 'culture_watch' || overview.automation.collection.lanes.culture_watch.status === 'running'} /><OperationLane title="产品形态增量采集" status={overview.automation.collection.lanes.market_refresh.status} detail={overview.automation.collection.lanes.market_refresh.detail} nextRun={overview.automation.collection.lanes.market_refresh.nextRunAt} lastSuccess={overview.automation.collection.lanes.market_refresh.lastSuccessAt} interval={`每 ${overview.automation.collection.lanes.market_refresh.intervalMinutes} 分钟`} onRun={() => void run('market_refresh')} disabled={running === 'market_refresh' || overview.automation.collection.lanes.market_refresh.status === 'running'} /><OperationLane title="每日 Top 3 设计" status={overview.automation.dailyDesign.daily.status} detail={overview.automation.dailyDesign.daily.detail} nextRun={overview.automation.dailyDesign.daily.nextRunAt} lastSuccess={overview.automation.dailyDesign.daily.lastSuccessAt} interval={`每天 ${String(overview.automation.dailyDesign.schedule.hour).padStart(2, '0')}:${String(overview.automation.dailyDesign.schedule.minute).padStart(2, '0')} ${overview.automation.dailyDesign.schedule.timezone}`} onRun={() => void run('daily')} disabled={running === 'daily' || overview.automation.dailyDesign.daily.status === 'running'} /></section><section className="studio-operations-lower"><article><span className="studio-eyebrow">SCHEDULE</span><h2>每日生成时间</h2><div className="studio-schedule-form"><label>小时<input type="number" min="0" max="23" value={hour} onChange={(event) => setHour(Number(event.target.value))} /></label><span>:</span><label>分钟<input type="number" min="0" max="59" value={minute} onChange={(event) => setMinute(Number(event.target.value))} /></label><button className="studio-primary" type="button" onClick={() => void saveSchedule()} disabled={running === 'schedule'}><Save size={17} />保存计划</button></div><p>{overview.automation.dailyDesign.policy}</p></article><article><span className="studio-eyebrow">BLOCKERS</span><h2>市场实时采集前置</h2>{overview.automation.collection.market.preflight.research_ready ? <p className="studio-ready"><Check size={17} />全部前置已就绪</p> : <ul className="studio-blocker-list">{overview.automation.collection.market.preflight.blockers.map((item) => <li key={item}><TriangleAlert size={15} />{item}</li>)}</ul>}</article></section><section className="studio-event-log"><header><div><span className="studio-eyebrow">EVENTS</span><h2>每日设计事件</h2></div><button type="button" onClick={() => void load()}><RefreshCw size={16} />刷新</button></header>{events.length ? <ol>{events.map((event) => <li key={event.id}><time>{formatStudioTime(event.at)}</time><StatusPill status={event.status} /><span><strong>{event.event}</strong><small>{event.detail}</small></span></li>)}</ol> : <p>尚无事件记录。</p>}</section></> : null}
    </StudioFrame>
  );
}

export default function StudioApp({ view, designId = '' }: { view: StudioView; designId?: string }) {
  if (view === 'home') return <HomePage />;
  if (view === 'culture') return <CulturePage />;
  if (view === 'forms') return <FormPage />;
  if (view === 'create') return <CreatePage />;
  if (view === 'designs') return <DesignsPage />;
  if (view === 'design') return <DesignPage designId={designId} />;
  if (view === 'edit') return <EditPage designId={designId} />;
  return <OperationsPage />;
}
