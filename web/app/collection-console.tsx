'use client';

import {
  Activity,
  Check,
  Clock3,
  Database,
  ExternalLink,
  Pause,
  Play,
  Plus,
  Radar,
  RefreshCw,
  ShieldCheck,
  X,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  addCollectionCandidate,
  getCollectionCandidates,
  getCollectionEvents,
  getCollectionRuntime,
  reviewCollectionCandidate,
  runCollectionLane,
  updateCollectionSchedule,
} from './workbench-api';
import type {
  CollectionCandidate,
  CollectionEvent,
  CollectionLaneId,
  CollectionLaneRuntime,
  CollectionRuntime,
} from './workbench-model';

type CollectionFocus = 'culture' | 'market' | 'all';

const LANE_LABELS: Record<CollectionLaneId, { title: string; short: string }> = {
  culture_watch: { title: '文化来源巡检', short: '文化' },
  market_refresh: { title: '四平台增量采集', short: '市场' },
};

const STATUS_LABELS: Record<string, string> = {
  scheduled: '已排程',
  running: '运行中',
  healthy: '正常',
  degraded: '部分失败',
  blocked: '等待授权',
  failed: '运行失败',
  paused: '已暂停',
  interrupted: '已中断',
  starting: '启动中',
  stopped: '已停止',
};

const CANDIDATE_LABELS: Record<CollectionCandidate['status'], string> = {
  pending_review: '待核验',
  ready_to_structure: '可结构化',
  rejected: '已排除',
};

const INTERVAL_OPTIONS = [60, 120, 240, 360, 720, 1440];
const SYNC_STALE_AFTER_MS = 35_000;
const HEARTBEAT_STALE_AFTER_MS = 45_000;
const PLATFORM_LABELS: Record<string, string> = {
  xhs: '小红书',
  dy: '抖音',
  bili: 'B站',
  wb: '微博',
};

function formatDate(value: string): string {
  if (!value) return '尚无';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date);
}

function formatCountdown(value: string, now: number): string {
  if (!value) return '等待排程';
  const target = new Date(value).getTime();
  if (Number.isNaN(target)) return '等待排程';
  const minutes = Math.ceil((target - now) / 60_000);
  if (minutes <= 0) return '即将运行';
  if (minutes < 60) return `${minutes} 分钟后`;
  const hours = Math.floor(minutes / 60);
  const remainder = minutes % 60;
  return remainder ? `${hours} 小时 ${remainder} 分后` : `${hours} 小时后`;
}

function intervalLabel(minutes: number): string {
  if (minutes < 60) return `${minutes} 分钟`;
  if (minutes % 1440 === 0) return `${minutes / 1440} 天`;
  return `${minutes / 60} 小时`;
}

function laneIcon(laneId: CollectionLaneId) {
  return laneId === 'culture_watch'
    ? <Database aria-hidden="true" size={17} />
    : <Radar aria-hidden="true" size={17} />;
}

function LanePipeline({
  laneId,
  lane,
  runtime,
  now,
  busy,
  onRun,
  onToggle,
  onInterval,
}: {
  laneId: CollectionLaneId;
  lane: CollectionLaneRuntime;
  runtime: CollectionRuntime;
  now: number;
  busy: string;
  onRun: (laneId: CollectionLaneId) => void;
  onToggle: (laneId: CollectionLaneId, enabled: boolean) => void;
  onInterval: (laneId: CollectionLaneId, minutes: number) => void;
}) {
  const isCulture = laneId === 'culture_watch';
  const steps = isCulture
    ? ['巡检已核验来源', '识别页面变化', '发现同域候选', '人工核验后入图']
    : ['检查授权与运行时', '四平台独立采集', '统一字段与去重', '全 live 才晋级'];
  const blocked = lane.status === 'blocked';
  const disabled = busy !== '' || !runtime.enabled || !lane.enabled;
  return (
    <article className={`collection-lane is-${lane.status}`}>
      <header className="collection-lane-header">
        <div className="collection-lane-title">
          <span>{laneIcon(laneId)}</span>
          <div>
            <h3>{LANE_LABELS[laneId].title}</h3>
            <p>{lane.detail}</p>
          </div>
        </div>
        <div className="collection-lane-status">
          <i aria-hidden="true" />
          <strong>{STATUS_LABELS[lane.status] ?? lane.status}</strong>
        </div>
      </header>

      <ol className="collection-pipeline" aria-label={`${LANE_LABELS[laneId].title}处理步骤`}>
        {steps.map((step, index) => (
          <li key={step} className={lane.status === 'running' && index < 3 ? 'is-active' : ''}>
            <span>{index + 1}</span>
            <strong>{step}</strong>
          </li>
        ))}
      </ol>

      {!isCulture ? (
        <div className="collection-platform-matrix" aria-label="四平台授权与采集状态">
          {['xhs', 'dy', 'bili', 'wb'].map((code) => {
            const check = runtime.market.preflight.checks.find((item) => item.id === `auth_${code}`);
            const runMode = (lane.metrics.platformModes as Record<string, string> | undefined)?.[code];
            const ready = check?.ok ?? false;
            return (
              <div className={ready ? 'is-ready' : 'is-blocked'} key={code}>
                <span>{PLATFORM_LABELS[code]}</span>
                <strong>{runMode ? `本轮 ${runMode}` : ready ? '授权可用' : '等待授权'}</strong>
                <small>{check?.detail || '尚未执行授权预检'}</small>
              </div>
            );
          })}
        </div>
      ) : null}

      <div className="collection-lane-facts">
        <dl>
          <div><dt>上次尝试</dt><dd>{formatDate(lane.lastAttemptAt)}</dd></div>
          <div><dt>上次成功</dt><dd>{formatDate(lane.lastSuccessAt)}</dd></div>
          <div><dt>下次运行</dt><dd>{formatCountdown(lane.nextRunAt, now)}</dd></div>
          <div><dt>连续失败</dt><dd>{lane.consecutiveFailures}</dd></div>
        </dl>
        <div className="collection-lane-controls">
          <label>
            <span>运行间隔</span>
            <select
              aria-label={`${LANE_LABELS[laneId].title}运行间隔`}
              disabled={busy !== ''}
              value={lane.intervalMinutes}
              onChange={(event) => onInterval(laneId, Number(event.target.value))}
            >
              {INTERVAL_OPTIONS.map((minutes) => <option key={minutes} value={minutes}>每 {intervalLabel(minutes)}</option>)}
            </select>
          </label>
          <button
            className="collection-secondary-action"
            disabled={busy !== ''}
            type="button"
            onClick={() => onToggle(laneId, !lane.enabled)}
          >
            {lane.enabled ? <Pause aria-hidden="true" size={15} /> : <Play aria-hidden="true" size={15} />}
            {lane.enabled ? '暂停通道' : '恢复通道'}
          </button>
          <button
            className="collection-primary-action"
            disabled={disabled || lane.status === 'running'}
            type="button"
            onClick={() => onRun(laneId)}
          >
            <RefreshCw aria-hidden="true" className={lane.status === 'running' ? 'is-spinning' : ''} size={15} />
            {lane.status === 'running' ? '正在运行' : '立即运行'}
          </button>
        </div>
      </div>

      {blocked && !isCulture ? (
        <div className="collection-blockers">
          <header><ShieldCheck aria-hidden="true" size={16} /><strong>自动运行前必须补齐</strong></header>
          <ul>
            {runtime.market.preflight.blockers.slice(0, 5).map((item) => <li key={item}>{item}</li>)}
          </ul>
          <p>调度器会继续复检，不会自动弹出登录窗口，也不会把历史快照写成实时结果。</p>
        </div>
      ) : null}
    </article>
  );
}

function CandidateQueue({
  candidates,
  busy,
  onReview,
  onSubmit,
}: {
  candidates: CollectionCandidate[];
  busy: string;
  onReview: (candidate: CollectionCandidate, status: CollectionCandidate['status']) => void;
  onSubmit: (candidate: { url: string; title: string }) => Promise<boolean>;
}) {
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const actionable = candidates.filter((item) => item.status !== 'rejected');
  const visible = actionable.slice(0, 8);
  return (
    <section className="collection-candidates">
      <header className="collection-section-heading">
        <div>
          <h3>文化候选队列</h3>
          <p>新来源先进入队列，完成出处、字段证据和文化边界核验后才进入正式图谱。</p>
        </div>
        <span>{actionable.length} 条待处理{actionable.length > visible.length ? ` · 显示前 ${visible.length} 条` : ''}</span>
      </header>
      <form
        className="candidate-add-form"
        onSubmit={async (event) => {
          event.preventDefault();
          if (!url.trim()) return;
          const submitted = await onSubmit({ url: url.trim(), title: title.trim() });
          if (submitted) {
            setUrl('');
            setTitle('');
          }
        }}
      >
        <label><span>公开来源地址</span><input required type="url" placeholder="https://…" value={url} onChange={(event) => setUrl(event.target.value)} /></label>
        <label><span>资料标题</span><input placeholder="可稍后补充" value={title} onChange={(event) => setTitle(event.target.value)} /></label>
        <button disabled={busy !== ''} type="submit"><Plus aria-hidden="true" size={15} />加入候选</button>
      </form>
      {visible.length ? (
        <div className="candidate-queue-list">
          {visible.map((candidate) => (
            <article key={candidate.id}>
              <div className="candidate-source">
                <span>{CANDIDATE_LABELS[candidate.status]}</span>
                <h4>{candidate.title || '待核对来源'}</h4>
                <p>{candidate.publisher || candidate.originSourceId} · {candidate.reason}</p>
                <a href={candidate.url} target="_blank" rel="noreferrer">核对原始页面 <ExternalLink aria-hidden="true" size={13} /></a>
              </div>
              <div className="candidate-actions">
                <button
                  aria-label={`标记 ${candidate.title || '待核对来源'} 可结构化`}
                  disabled={busy !== '' || candidate.status === 'ready_to_structure'}
                  title="来源已核对，可进入结构化整理"
                  type="button"
                  onClick={() => onReview(candidate, 'ready_to_structure')}
                ><Check aria-hidden="true" size={16} /><span>可结构化</span></button>
                <button
                  aria-label={`排除 ${candidate.title || '待核对来源'}`}
                  disabled={busy !== ''}
                  title="排除不相关或不可信来源"
                  type="button"
                  onClick={() => onReview(candidate, 'rejected')}
                ><X aria-hidden="true" size={16} /><span>排除</span></button>
              </div>
            </article>
          ))}
        </div>
      ) : <p className="collection-empty">暂无待处理候选。来源巡检会持续发现同域相关页面，也可以手动加入公开来源。</p>}
    </section>
  );
}

function EventTimeline({ events, focus }: { events: CollectionEvent[]; focus: CollectionFocus }) {
  const lane = focus === 'culture' ? 'culture_watch' : focus === 'market' ? 'market_refresh' : '';
  const visible = events
    .filter((item) => !lane || item.lane === lane || item.lane === 'system')
    .filter((item) => item.event !== 'culture_candidate_reviewed' || item.status !== 'rejected')
    .slice(0, 10);
  return (
    <section className="collection-events">
      <header className="collection-section-heading">
        <div><h3>最近运行事件</h3><p>失败、阻断和恢复都保留在本机持久化审计中。</p></div>
      </header>
      {visible.length ? (
        <ol>
          {visible.map((event) => (
            <li key={event.id}>
              <i className={`is-${event.status}`} aria-hidden="true" />
              <time dateTime={event.at}>{formatDate(event.at)}</time>
              <div><strong>{event.detail}</strong><span>{event.lane === 'system' ? '系统' : LANE_LABELS[event.lane].short}</span></div>
            </li>
          ))}
        </ol>
      ) : <p className="collection-empty">调度器尚未写入运行事件。</p>}
    </section>
  );
}

export function CollectionConsole({
  focus = 'all',
  recordCount = 0,
  sourceCount = 0,
}: {
  focus?: CollectionFocus;
  recordCount?: number;
  sourceCount?: number;
}) {
  const [runtime, setRuntime] = useState<CollectionRuntime | null>(null);
  const [events, setEvents] = useState<CollectionEvent[]>([]);
  const [candidates, setCandidates] = useState<CollectionCandidate[]>([]);
  const [busy, setBusy] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [now, setNow] = useState(() => Date.now());
  const [lastSuccessfulSyncAt, setLastSuccessfulSyncAt] = useState<number | null>(null);

  const lanes = useMemo<CollectionLaneId[]>(() => {
    if (focus === 'culture') return ['culture_watch'];
    if (focus === 'market') return ['market_refresh'];
    return ['culture_watch', 'market_refresh'];
  }, [focus]);

  const load = useCallback(async (quiet = false) => {
    try {
      if (!quiet) setError('');
      const [nextRuntime, nextEvents, nextCandidates] = await Promise.all([
        getCollectionRuntime(),
        getCollectionEvents(80),
        focus === 'market' ? Promise.resolve({ candidates: [] }) : getCollectionCandidates('', 100),
      ]);
      setRuntime(nextRuntime);
      setEvents(nextEvents.events);
      setCandidates(nextCandidates.candidates);
      const syncedAt = Date.now();
      setLastSuccessfulSyncAt(syncedAt);
      setNow(syncedAt);
      setError('');
    } catch (reason) {
      const detail = reason instanceof Error ? reason.message : String(reason);
      setError(`采集控制面连接中断：${detail}`);
      setNow(Date.now());
      throw reason;
    }
  }, [focus]);

  useEffect(() => {
    const initial = window.setTimeout(() => void load().catch(() => undefined), 0);
    const poll = window.setInterval(() => void load(true).catch(() => undefined), 12_000);
    const clock = window.setInterval(() => setNow(Date.now()), 5_000);
    return () => {
      window.clearTimeout(initial);
      window.clearInterval(poll);
      window.clearInterval(clock);
    };
  }, [load]);

  const act = useCallback(async (key: string, operation: () => Promise<unknown>, success: string) => {
    if (busy) return false;
    setBusy(key);
    setNotice('');
    setError('');
    try {
      await operation();
      await load(true);
      setNotice(success);
      return true;
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
      return false;
    } finally {
      setBusy('');
    }
  }, [busy, load]);

  if (!runtime) {
    return (
      <section className="collection-console collection-console--loading" aria-busy="true">
        <Activity aria-hidden="true" size={20} />
        <div><h2>{error ? '持续采集控制面不可用' : '正在连接持续采集控制面'}</h2><p>{error || '读取调度、授权、候选和最近事件。'}</p></div>
        {error ? <button type="button" onClick={() => void load().catch(() => undefined)}>重新连接</button> : null}
      </section>
    );
  }

  const pending = runtime.culture.candidateCounts.pending_review ?? 0;
  const ready = runtime.culture.candidateCounts.ready_to_structure ?? 0;
  const heartbeatAt = new Date(runtime.scheduler.heartbeatAt).getTime();
  const heartbeatFresh = Number.isFinite(heartbeatAt)
    && now - heartbeatAt <= HEARTBEAT_STALE_AFTER_MS;
  const syncFresh = lastSuccessfulSyncAt !== null
    && now - lastSuccessfulSyncAt <= SYNC_STALE_AFTER_MS;
  const connected = !error && syncFresh && heartbeatFresh && runtime.scheduler.threadAlive;
  const connectionBusy = connected ? busy : busy || 'connection';
  const liveLabel = error
    ? '采集控制面连接中断'
    : !heartbeatFresh || !runtime.scheduler.threadAlive
      ? '调度心跳已过期'
      : runtime.enabled
        ? '持续维护已开启'
        : '持续维护已暂停';
  return (
    <section className={`collection-console collection-console--${focus}`}>
      <header className="collection-console-heading">
        <div>
          <span className={`collection-live-state is-${connected ? runtime.scheduler.status : 'disconnected'}`}><i aria-hidden="true" />{liveLabel}</span>
          <h2>{focus === 'culture' ? '知识库更新控制面' : focus === 'market' ? '采集运行控制面' : '素材持续采集'}</h2>
          <p>{focus === 'culture'
            ? '监测已核验来源的变化，发现新候选，但不跳过人工证据审核。'
            : focus === 'market'
              ? '按计划复检四个平台；每个平台独立记账，失败轮不覆盖已核验快照。'
              : '文化来源与平台市场两条通道各自排程、可暂停、可追溯。'}</p>
        </div>
        <button
          className="collection-scheduler-toggle"
          disabled={busy !== '' || !connected}
          type="button"
          onClick={() => void act(
            'scheduler',
            () => updateCollectionSchedule({ enabled: !runtime.enabled }),
            runtime.enabled ? '持续维护已暂停。' : '持续维护已恢复。',
          )}
        >
          {runtime.enabled ? <Pause aria-hidden="true" size={15} /> : <Play aria-hidden="true" size={15} />}
          {runtime.enabled ? '暂停全部' : '恢复全部'}
        </button>
      </header>

      <div className="collection-overview-strip" aria-label="持续采集摘要">
        {focus !== 'market' ? <div><Database aria-hidden="true" size={16} /><span>正式知识</span><strong>{recordCount || runtime.culture.verifiedRecords}</strong><small>条已核验记录</small></div> : null}
        {focus !== 'market' ? <div><ShieldCheck aria-hidden="true" size={16} /><span>登记来源</span><strong>{sourceCount || runtime.culture.verifiedSources}</strong><small>个公开来源</small></div> : null}
        {focus !== 'market' ? <div><Clock3 aria-hidden="true" size={16} /><span>待核验</span><strong>{pending}</strong><small>{ready} 条可结构化</small></div> : null}
        <div><Activity aria-hidden="true" size={16} /><span>调度心跳</span><strong>{connected ? '在线' : error ? '中断' : '离线'}</strong><small>{connected ? formatDate(runtime.scheduler.heartbeatAt) : `最后同步 ${lastSuccessfulSyncAt ? formatDate(new Date(lastSuccessfulSyncAt).toISOString()) : '尚无'}`}</small></div>
      </div>

      <div className="collection-lane-stack">
        {lanes.map((laneId) => (
          <LanePipeline
            busy={connectionBusy}
            key={laneId}
            lane={runtime.lanes[laneId]}
            laneId={laneId}
            now={now}
            runtime={runtime}
            onInterval={(id, minutes) => void act(
              `${id}-interval`,
              () => updateCollectionSchedule({ lanes: { [id]: { intervalMinutes: minutes } } }),
              `${LANE_LABELS[id].title}间隔已更新。`,
            )}
            onRun={(id) => void act(
              `${id}-run`,
              () => runCollectionLane(id),
              `${LANE_LABELS[id].title}已进入后台队列。`,
            )}
            onToggle={(id, enabled) => void act(
              `${id}-toggle`,
              () => updateCollectionSchedule({ lanes: { [id]: { enabled } } }),
              `${LANE_LABELS[id].title}${enabled ? '已恢复' : '已暂停'}。`,
            )}
          />
        ))}
      </div>

      {focus !== 'market' ? (
        <CandidateQueue
          busy={connectionBusy}
          candidates={candidates}
          onReview={(candidate, status) => void act(
            `${candidate.id}-${status}`,
            () => reviewCollectionCandidate(candidate.id, status),
            status === 'rejected' ? '候选已排除。' : '候选已标记为可结构化；正式入图仍需字段证据审核。',
          )}
          onSubmit={(candidate) => act(
            'candidate-add',
            () => addCollectionCandidate(candidate),
            '公开来源已加入待核验队列。',
          )}
        />
      ) : null}
      <EventTimeline events={events} focus={focus} />
      {notice ? <div className="collection-notice" role="status">{notice}</div> : null}
      {error ? <div className="collection-error" role="alert">{error}<button type="button" onClick={() => void load().catch(() => undefined)}>重新连接</button></div> : null}
    </section>
  );
}
