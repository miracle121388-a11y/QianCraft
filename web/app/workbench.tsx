'use client';

/* eslint-disable @next/next/no-img-element -- API-served workspace assets use runtime URLs. */

import '@xyflow/react/dist/style.css';

import {
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
  MiniMap,
  ReactFlow,
  type ReactFlowInstance,
  useEdgesState,
  useNodesState,
} from '@xyflow/react';
import {
  ChevronDown,
  ExternalLink,
  History,
  Images,
  Library,
  PanelRight,
  Play,
  Plus,
  Save,
  Scale,
  Workflow,
  X,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import {
  API_BASE,
  activateConcept,
  createWorkspace,
  duplicateConcept,
  generateMoreConcept,
  getBootstrap,
  getDesignPackage,
  runNode as runNodeRequest,
  regenerateConcept,
  saveDecisionProfile,
  saveDesignBrief,
  saveWorkspace,
} from './workbench-api';
import {
  NODE_TYPE_LABELS,
  STATUS_LABELS,
  apiAssetUrl,
  displayNodeSummary,
  markNodeStatus,
  orderedRunNodeIds,
  updatePosterSection,
  type CultureRecordSummary,
  type DecisionCatalog,
  type DecisionProfile,
  type DesignBrief,
  type ImageProviderStatus,
  type KnowledgeCenterData,
  type PosterConfig,
  type WorkbenchEdge,
  type WorkbenchNode,
  type WorkbenchNodeType,
  type WorkbenchWorkspace,
  type WorkspaceSummary,
} from './workbench-model';
import { nodeTypes } from './workbench-nodes';
import { DecisionStudio, type DecisionStage } from './decision-studio';

type Toast = { tone: 'success' | 'error' | 'neutral'; message: string } | null;
type InspectorTab =
  | 'info'
  | 'inputs'
  | 'parameters'
  | 'outputs'
  | 'sources'
  | 'history'
  | 'actions';
type ConceptDraft = { title: string; summary: string; direction: string; prompt: string };
type ToolDock = 'evidence' | 'assets' | 'history' | null;

const PLATFORM_LABELS: Record<string, string> = {
  xhs: '小红书',
  dy: '抖音',
  bili: 'B站',
  wb: '微博',
};

const POSTER_SECTION_LABELS: Record<string, string> = {
  hero: '成品主视觉',
  culture: '文化元素与转译',
  breakdown: '结构拆解',
  bom: '用料 / BOM',
  process: '工艺路径',
};

const PHASE_NAVIGATION = [
  { id: 'culture', label: '文化', nodeId: 'culture' },
  { id: 'market', label: '市场', nodeId: 'market' },
  { id: 'strategy', label: '策略', nodeId: 'strategy' },
  { id: 'design', label: '设计', nodeId: 'brief' },
  { id: 'delivery', label: '交付', nodeId: 'poster' },
] as const;

function phaseForNode(nodeId: string) {
  if (nodeId === 'culture' || nodeId.startsWith('culture-')) return 'culture';
  if (nodeId === 'market' || nodeId.startsWith('market-')) return 'market';
  if (nodeId === 'strategy') return 'strategy';
  if (nodeId === 'poster') return 'delivery';
  return 'design';
}

const NODE_DECISION_STAGE: Record<WorkbenchNodeType, DecisionStage> = {
  CultureGraphNode: 'culture',
  MarketRadarNode: 'market',
  StrategyNode: 'score',
  DesignBriefNode: 'brief',
  VisualGenerationNode: 'visual',
  ConceptNode: 'concept',
  PosterBoardNode: 'poster',
};

const STAGE_LABELS: Record<DecisionStage, string> = {
  culture: '文化记录选择',
  market: '平台与形态范围',
  score: '评分权重与候选机会',
  brief: '目标人群与设计意图',
  visual: '视觉参考与生成方向',
  concept: '概念比较与当前采用',
  poster: '海报主题与展示板块',
};

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function downloadJson(payload: unknown, filename: string) {
  downloadBlob(
    new Blob([`${JSON.stringify(payload, null, 2)}\n`], { type: 'application/json' }),
    filename,
  );
}

function loadCanvasImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.crossOrigin = 'anonymous';
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error('概念图载入失败'));
    image.src = url;
  });
}

function drawWrappedText(
  context: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  maxWidth: number,
  lineHeight: number,
  maxLines: number,
): number {
  const characters = [...String(text)];
  const lines: string[] = [];
  let line = '';
  for (const character of characters) {
    const next = line + character;
    if (line && context.measureText(next).width > maxWidth) {
      lines.push(line);
      line = character;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  const visible = lines.slice(0, maxLines);
  if (lines.length > maxLines && visible.length) {
    visible[visible.length - 1] = `${visible[visible.length - 1].slice(0, -1)}…`;
  }
  visible.forEach((value, index) => context.fillText(value, x, y + index * lineHeight));
  return y + visible.length * lineHeight;
}

async function exportPosterPng(
  poster: PosterConfig,
  activeConcept: WorkbenchNode | undefined,
) {
  const width = 1800;
  const height = 2400;
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('浏览器未提供 Canvas 2D 能力。');

  const paper = '#f4f1e9';
  const white = '#fcfbf7';
  const ink = '#172033';
  const muted = '#6e746f';
  const indigo = '#142b43';
  const red = '#bf493f';
  const line = '#d7d0c1';
  context.fillStyle = paper;
  context.fillRect(0, 0, width, height);
  context.strokeStyle = 'rgba(20,43,67,.075)';
  context.lineWidth = 1;
  for (let x = 0; x < width; x += 48) {
    context.beginPath();
    context.moveTo(x, 0);
    context.lineTo(x, height);
    context.stroke();
  }
  for (let y = 0; y < height; y += 48) {
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(width, y);
    context.stroke();
  }

  context.fillStyle = indigo;
  context.fillRect(0, 0, width, 270);
  context.fillStyle = red;
  context.fillRect(88, 72, 14, 118);
  context.fillStyle = white;
  context.font = '700 76px "Microsoft YaHei", sans-serif';
  context.fillText(poster.title || 'QianCraft 概念提案', 140, 130);
  context.font = '400 28px "Microsoft YaHei", sans-serif';
  drawWrappedText(context, poster.subtitle, 144, 190, 1140, 38, 2);
  context.font = '700 22px Arial, sans-serif';
  context.fillText('QIANCRAFT / CULTURAL PRODUCT CONCEPT', 1270, 90);
  context.fillStyle = '#aab5be';
  context.font = '400 17px Arial, sans-serif';
  context.fillText('可编辑概念海报 · 首样沟通阶段', 1270, 130);

  const visibleSections = poster.sections.filter(
    (section) => !poster.hiddenSections.includes(section),
  );
  const sectionWeights: Record<string, number> = {
    hero: 3.15,
    culture: 1.25,
    breakdown: 1.35,
    bom: 1.65,
    process: 1.5,
  };
  const availableHeight = 1980;
  const totalWeight = visibleSections.reduce(
    (sum, section) => sum + (sectionWeights[section] ?? 1),
    0,
  );
  let y = 315;
  let heroImage: HTMLImageElement | null = null;
  const heroUrl = apiAssetUrl(activeConcept?.data.imageUrl, API_BASE);
  if (heroUrl) heroImage = await loadCanvasImage(heroUrl).catch(() => null);

  for (const [index, section] of visibleSections.entries()) {
    const sectionHeight = Math.max(
      180,
      Math.round((availableHeight * (sectionWeights[section] ?? 1)) / totalWeight) - 18,
    );
    const x = 88;
    const sectionWidth = width - 176;
    context.fillStyle = white;
    context.strokeStyle = line;
    context.lineWidth = 2;
    context.beginPath();
    context.roundRect(x, y, sectionWidth, sectionHeight, 28);
    context.fill();
    context.stroke();
    context.fillStyle = red;
    context.beginPath();
    context.roundRect(x + 30, y + 28, 58, 38, 19);
    context.fill();
    context.fillStyle = white;
    context.font = '700 18px Arial, sans-serif';
    context.fillText(`0${index + 1}`, x + 47, y + 54);
    context.fillStyle = ink;
    context.font = '700 27px "Microsoft YaHei", sans-serif';
    context.fillText(POSTER_SECTION_LABELS[section] ?? section, x + 112, y + 57);

    if (section === 'hero') {
      if (heroImage) {
        const target = { x: x + 34, y: y + 88, w: sectionWidth - 68, h: sectionHeight - 120 };
        const ratio = Math.min(target.w / heroImage.width, target.h / heroImage.height);
        const imageWidth = heroImage.width * ratio;
        const imageHeight = heroImage.height * ratio;
        context.drawImage(
          heroImage,
          target.x + (target.w - imageWidth) / 2,
          target.y + (target.h - imageHeight) / 2,
          imageWidth,
          imageHeight,
        );
      } else {
        context.fillStyle = '#e9e4d9';
        context.fillRect(x + 34, y + 88, sectionWidth - 68, sectionHeight - 120);
        context.fillStyle = muted;
        context.font = '500 24px "Microsoft YaHei", sans-serif';
        context.fillText('等待当前概念主视觉', x + 74, y + 148);
      }
    } else if (section === 'culture') {
      context.fillStyle = indigo;
      context.font = '700 38px "Microsoft YaHei", sans-serif';
      context.fillText(poster.cultureElement, x + 36, y + 120);
      context.fillStyle = ink;
      context.font = '400 23px "Microsoft YaHei", sans-serif';
      drawWrappedText(context, poster.cultureRule, x + 36, y + 170, sectionWidth - 72, 36, 5);
    } else if (section === 'breakdown') {
      const parts = poster.materials.slice(0, 5);
      const gap = (sectionWidth - 150) / Math.max(parts.length, 1);
      parts.forEach((part, partIndex) => {
        const center = x + 78 + gap * partIndex + gap / 2;
        context.fillStyle = partIndex % 2 ? '#263e55' : indigo;
        context.beginPath();
        context.roundRect(center - 54, y + 100, 108, 96, 24);
        context.fill();
        context.fillStyle = red;
        context.beginPath();
        context.arc(center, y + 228, 20, 0, Math.PI * 2);
        context.fill();
        context.fillStyle = white;
        context.font = '700 16px Arial, sans-serif';
        context.fillText(String(partIndex + 1), center - 5, y + 234);
        context.fillStyle = ink;
        context.font = '500 17px "Microsoft YaHei", sans-serif';
        drawWrappedText(context, part, center - 90, y + 270, 180, 25, 3);
      });
    } else if (section === 'bom') {
      context.font = '500 20px "Microsoft YaHei", sans-serif';
      poster.materials.slice(0, 6).forEach((material, materialIndex) => {
        const rowY = y + 92 + materialIndex * 54;
        context.fillStyle = materialIndex % 2 ? '#f2efe7' : '#e9e4d9';
        context.fillRect(x + 34, rowY, sectionWidth - 68, 44);
        context.fillStyle = red;
        context.font = '700 17px Arial, sans-serif';
        context.fillText(`B${String(materialIndex + 1).padStart(2, '0')}`, x + 54, rowY + 29);
        context.fillStyle = ink;
        context.font = '500 20px "Microsoft YaHei", sans-serif';
        context.fillText(material, x + 140, rowY + 29);
      });
    } else if (section === 'process') {
      poster.process.slice(0, 6).forEach((step, stepIndex) => {
        const rowY = y + 94 + stepIndex * 62;
        context.fillStyle = indigo;
        context.beginPath();
        context.arc(x + 58, rowY, 19, 0, Math.PI * 2);
        context.fill();
        context.fillStyle = white;
        context.font = '700 15px Arial, sans-serif';
        context.fillText(String(stepIndex + 1), x + 53, rowY + 5);
        context.fillStyle = ink;
        context.font = '400 19px "Microsoft YaHei", sans-serif';
        drawWrappedText(context, step, x + 94, rowY - 12, sectionWidth - 140, 29, 2);
      });
    }
    y += sectionHeight + 18;
  }

  context.fillStyle = ink;
  context.fillRect(0, height - 78, width, 78);
  context.fillStyle = white;
  context.font = '400 18px "Microsoft YaHei", sans-serif';
  context.fillText(
    poster.boundary || '概念视觉与工厂首样沟通输入｜不是量产定稿',
    90,
    height - 32,
  );
  context.textAlign = 'right';
  context.fillStyle = '#aab5be';
  context.fillText(new Date().toLocaleDateString('zh-CN'), width - 90, height - 32);
  context.textAlign = 'left';

  const blob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob(
      (value) => (value ? resolve(value) : reject(new Error('PNG 导出失败'))),
      'image/png',
      1,
    );
  });
  downloadBlob(blob, `QianCraft-${poster.title || 'concept-poster'}.png`);
}

function KnowledgeCenter({
  knowledge,
  profile,
  onOpenGraph,
  onOpenDecisions,
}: {
  knowledge: KnowledgeCenterData;
  profile: DecisionProfile;
  onOpenGraph: () => void;
  onOpenDecisions: (stage: DecisionStage) => void;
}) {
  const [query, setQuery] = useState('');
  const records = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return knowledge.culture.records.slice(0, 3);
    return knowledge.culture.records
      .filter((record) =>
        [record.name, record.category, ...record.region, ...record.crafts, ...record.patterns]
          .join(' ')
          .toLowerCase()
          .includes(keyword),
      )
              .slice(0, 6);
  }, [knowledge.culture.records, query]);

  return (
    <aside className="knowledge-center">
      <div className="panel-heading">
        <div>
          <h2>证据中心</h2>
        </div>
        <div className="panel-heading__actions"><b>{knowledge.culture.recordCount + knowledge.market.ranking.length}</b><button type="button" onClick={() => onOpenDecisions('culture')}>人工选材</button></div>
      </div>

      <section className="knowledge-section">
        <div className="section-title-row">
          <div>
            <span>市场雷达</span>
          </div>
          <button type="button" onClick={() => onOpenDecisions('market')}>调整范围</button>
        </div>
        <div className="platform-grid">
          {Object.entries(knowledge.market.platforms).map(([code, platform]) => (
            <div className={profile.marketPlatforms.includes(code) ? 'is-selected' : ''} key={code} title={platform.detail}>
              <span>{PLATFORM_LABELS[code] ?? code}</span>
              <strong>{platform.sample_size}</strong>
              <i className={`platform-state platform-state--${platform.status}`} />
            </div>
          ))}
        </div>
        <div className="market-total">
          <span>已验证历史样本</span>
          <strong>{knowledge.market.sampleSize}</strong>
        </div>
        <div className="market-ranking">
          {knowledge.market.ranking.slice(0, 3).map((item) => (
            <div
              className={profile.marketProductForms.includes(item.name) ? 'is-selected' : ''}
              draggable
              key={item.name}
              onDragStart={(event) => {
                event.dataTransfer.setData(
                  'application/qiancraft-knowledge',
                  JSON.stringify({ kind: 'market', item }),
                );
                event.dataTransfer.effectAllowed = 'copy';
              }}
            >
              <b>0{item.rank}</b>
              <span>{item.name}</span>
              <i>
                <em style={{ width: `${Math.min(100, item.score)}%` }} />
              </i>
              <strong>{item.score}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="knowledge-section knowledge-section--culture">
        <div className="section-title-row">
          <div>
            <span>贵州在地文化</span>
          </div>
          <div className="section-title-actions"><button type="button" onClick={onOpenGraph}>展开图谱</button><button type="button" onClick={() => onOpenDecisions('culture')}>选择记录</button></div>
        </div>
        <label className="knowledge-search">
          <span aria-hidden="true">⌕</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜索工艺、地域、纹样…"
          />
        </label>
        <div className="culture-list">
          {records.map((record) => (
            <article
              className={profile.cultureRecordIds.includes(record.id) ? 'is-selected' : ''}
              draggable
              key={record.id}
              onDragStart={(event) => {
                event.dataTransfer.setData(
                  'application/qiancraft-knowledge',
                  JSON.stringify({ kind: 'culture', item: record }),
                );
                event.dataTransfer.effectAllowed = 'copy';
              }}
            >
              <div>
                <span>{record.category || '在地文化'}</span>
                <small>{record.sourceRefs.length} 条引用</small>
              </div>
              <h3>{record.name}</h3>
              <p>{record.region.slice(0, 2).join(' · ')}</p>
              <div className="tag-row">
                {record.crafts.slice(0, 3).map((craft) => (
                  <em key={craft}>{craft}</em>
                ))}
              </div>
              <small className="culture-selection-state">{profile.cultureRecordIds.includes(record.id) ? '✓ 本轮使用' : '未选用'}</small>
            </article>
          ))}
        </div>
        <p className="drag-hint">拖到画布，可创建证据节点</p>
      </section>
    </aside>
  );
}

function AssetDock({
  nodes,
  onSelect,
}: {
  nodes: WorkbenchNode[];
  onSelect: (nodeId: string) => void;
}) {
  const assets = nodes.filter((node) => node.type === 'ConceptNode' || node.type === 'PosterBoardNode');

  return (
    <aside className="asset-dock">
      <header className="dock-heading">
        <div><h2>方案资产</h2></div>
        <b>{assets.length}</b>
      </header>
      <p className="dock-intro">比较概念方向与当前海报，点击即可定位。</p>
      <div className="asset-dock__list">
        {assets.map((node) => {
          const imageUrl = String(node.data.imageUrl ?? '');
          return (
            <button className={node.data.active ? 'is-active' : ''} key={node.id} type="button" onClick={() => onSelect(node.id)}>
              {imageUrl ? <img alt="" src={apiAssetUrl(imageUrl, API_BASE)} /> : <span className="asset-dock__empty">{String(node.data.label ?? '板')}</span>}
              <span><small>{NODE_TYPE_LABELS[node.type]}</small><strong>{node.data.title}</strong><em>{STATUS_LABELS[node.data.status]}</em></span>
            </button>
          );
        })}
      </div>
    </aside>
  );
}

function HistoryDock({ node }: { node: WorkbenchNode | undefined }) {
  const history = node?.data.history ?? [];

  return (
    <aside className="history-dock">
      <header className="dock-heading">
        <div><h2>节点历史</h2></div>
        <b>{history.length}</b>
      </header>
      {node ? (
        <>
          <div className="history-dock__subject"><span>{NODE_TYPE_LABELS[node.type]}</span><strong>{node.data.title}</strong><em>{STATUS_LABELS[node.data.status]}</em></div>
          <div className="history-dock__list">
            {history.length ? history.map((item, index) => (
              <article key={`${item.at}-${index}`}><i /><p>{item.event}</p><time>{new Date(item.at).toLocaleString('zh-CN')}</time></article>
            )) : <p className="dock-empty">当前节点尚无独立历史记录。</p>}
          </div>
        </>
      ) : <p className="dock-empty">先在画布中选择一个节点。</p>}
    </aside>
  );
}

function CultureGraphOverlay({
  records,
  onClose,
}: {
  records: CultureRecordSummary[];
  onClose: () => void;
}) {
  const [selectedId, setSelectedId] = useState(records[0]?.id ?? '');
  const selected = records.find((record) => record.id === selectedId) ?? records[0];
  return (
    <div className="graph-overlay" role="dialog" aria-modal="true" aria-label="贵州文化图谱">
      <header>
        <div>
          <h2>贵州文化知识图谱</h2>
          <p>地域、工艺、纹样与使用边界保持证据引用，不把支系差异压扁成一种风格。</p>
        </div>
        <button type="button" onClick={onClose} aria-label="关闭图谱">×</button>
      </header>
      <div className="graph-overlay__body">
        <div className="culture-orbit">
          <div className="orbit-core">
            <span>GUIZHOU</span>
            <strong>贵州在地文化</strong>
            <small>{records.length} records</small>
          </div>
          {records.slice(0, 14).map((record, index) => (
            <button
              className={record.id === selected?.id ? 'is-active' : ''}
              key={record.id}
              style={{ '--orbit-index': index } as React.CSSProperties}
              type="button"
              onClick={() => setSelectedId(record.id)}
            >
              {record.name.replace('贵州', '')}
            </button>
          ))}
        </div>
        {selected ? (
          <article className="culture-detail">
            <span>{selected.category}</span>
            <h3>{selected.name}</h3>
            <p>{selected.region.join(' · ')}</p>
            <h4>工艺</h4>
            <div className="tag-row">
              {selected.crafts.map((item) => <em key={item}>{item}</em>)}
            </div>
            <h4>纹样 / 结构</h4>
            <div className="tag-row">
              {selected.patterns.map((item) => <em key={item}>{item}</em>)}
            </div>
            <h4>边界</h4>
            {selected.boundaries.map((item) => <p className="boundary-item" key={item}>{item}</p>)}
            <div className="source-strip">{selected.sourceRefs.join(' · ')}</div>
          </article>
        ) : null}
      </div>
    </div>
  );
}

function DecisionEntry({
  profile,
  stage,
  onOpen,
}: {
  profile: DecisionProfile;
  stage: DecisionStage;
  onOpen: (stage: DecisionStage) => void;
}) {
  const stageLabel = STAGE_LABELS[stage];
  return (
    <section className="inspector-decision-card">
      <div><span>HUMAN DECISION</span><em>v{profile.version}</em></div>
      <strong>{stageLabel}</strong>
      <p>当前为{profile.mode === 'manual' ? '人工配置' : '系统建议'}；修改会建立新版本并保留事实原件。</p>
      <button type="button" onClick={() => onOpen(stage)}>打开人工决策配置 ↗</button>
    </section>
  );
}

function InspectorPanel({
  node,
  nodes,
  edges,
  provider,
  decisionProfile,
  busy,
  onOpenDetail,
  onRun,
  onRunFromHere,
  onSaveBrief,
  onSavePoster,
  onActivateConcept,
  onDuplicateConcept,
  onGenerateMoreConcept,
  onRegenerateConcept,
  onSaveConcept,
  onExportPoster,
  onDownloadPackage,
  onOpenDecisions,
}: {
  node: WorkbenchNode | undefined;
  nodes: WorkbenchNode[];
  edges: WorkbenchEdge[];
  provider: ImageProviderStatus;
  decisionProfile: DecisionProfile;
  busy: boolean;
  onOpenDetail: (nodeId: string) => void;
  onRun: (nodeId: string) => void;
  onRunFromHere: (nodeId: string) => void;
  onSaveBrief: (brief: DesignBrief) => void;
  onSavePoster: (poster: PosterConfig) => void;
  onActivateConcept: (nodeId: string) => void;
  onDuplicateConcept: (nodeId: string) => void;
  onGenerateMoreConcept: (nodeId: string) => void;
  onRegenerateConcept: (nodeId: string) => void;
  onSaveConcept: (nodeId: string, concept: ConceptDraft) => void;
  onExportPoster: () => void;
  onDownloadPackage: () => void;
  onOpenDecisions: (stage: DecisionStage) => void;
}) {
  const [tab, setTab] = useState<InspectorTab>('info');
  const [briefDraft, setBriefDraft] = useState<DesignBrief | null>(() =>
    node?.data.brief ? structuredClone(node.data.brief) : null,
  );
  const [posterDraft, setPosterDraft] = useState<PosterConfig | null>(() =>
    node?.data.poster ? structuredClone(node.data.poster) : null,
  );
  const [conceptDraft, setConceptDraft] = useState<ConceptDraft | null>(() =>
    node?.type === 'ConceptNode'
      ? {
          title: node.data.title,
          summary: node.data.summary,
          direction: String(node.data.direction ?? ''),
          prompt: String(node.data.prompt ?? ''),
        }
      : null,
  );

  if (!node) {
    return (
      <aside className="inspector inspector--empty">
        <div className="empty-inspector-mark">⌁</div>
        <h2>选择一个节点</h2>
        <p>查看输入、参数、证据来源与运行历史。</p>
      </aside>
    );
  }

  const upstreamIds = edges.filter((edge) => edge.target === node.id).map((edge) => edge.source);
  const upstream = nodes.filter((item) => upstreamIds.includes(item.id));
  const tabs: Array<[InspectorTab, string]> = [
    ['info', '概览'],
    ['inputs', '输入'],
    ['parameters', '配置'],
    ['outputs', '结果'],
    ['sources', '证据'],
    ['history', '记录'],
    ['actions', '操作'],
  ];
  const isBrief = node.type === 'DesignBriefNode';
  const isPoster = node.type === 'PosterBoardNode';
  const isConcept = node.type === 'ConceptNode';
  const decisionStage = NODE_DECISION_STAGE[node.type];

  return (
    <aside className="inspector">
      <header className="inspector__header">
        <div className={`inspector-icon inspector-icon--${node.type}`}>
          {node.type === 'ConceptNode' ? String(node.data.label ?? 'C').slice(-1) : node.data.eyebrow[0]}
        </div>
        <div>
          <span>{NODE_TYPE_LABELS[node.type]}</span>
          <h2>{node.data.title}</h2>
          <small className={`inspector-status-label is-${node.data.status}`}>{STATUS_LABELS[node.data.status]}</small>
        </div>
        <i className={`inspector-state inspector-state--${node.data.status}`} />
      </header>
      <nav className="inspector-tabs" aria-label="节点详情">
        {tabs.map(([id, label]) => (
          <button className={tab === id ? 'is-active' : ''} key={id} type="button" onClick={() => setTab(id)}>
            {label}
          </button>
        ))}
      </nav>
      <div className="inspector__content">
        {tab === 'info' ? (
          <>
            <section className="inspector-section inspector-section--summary">
              <p>{displayNodeSummary(node.type, node.data.summary)}</p>
            </section>
            {node.data.stats?.length ? (
              <section className="inspector-metrics">
                {node.data.stats.map((stat) => (
                  <div key={stat.label}><strong>{stat.value}</strong><span>{stat.label}</span></div>
                ))}
              </section>
            ) : null}
            {node.type === 'VisualGenerationNode' ? (
              <section className="provider-card">
                <div><i className={provider.configured ? 'is-ready' : ''} /><strong>{provider.configured ? '图像服务已就绪' : '图像服务未配置'}</strong></div>
                <p>{provider.configured ? '服务已连接，可按当前任务书继续生成。' : '当前展示视觉可用；重新生成前需配置独立图像服务。'}</p>
                <dl>
                  <div><dt>服务</dt><dd>{provider.provider === 'unconfigured' ? '未配置' : provider.provider}</dd></div>
                  <div><dt>模型</dt><dd>{provider.model || '—'}</dd></div>
                </dl>
              </section>
            ) : null}
          </>
        ) : null}

        {tab === 'inputs' ? (
          <section className="inspector-section">
            <span>上游输入</span>
            {upstream.length ? (
              <div className="input-list">
                {upstream.map((item) => (
                  <div key={item.id}>
                    <i className={`inspector-state inspector-state--${item.data.status}`} />
                    <p><strong>{item.data.title}</strong><span>{NODE_TYPE_LABELS[item.type]}</span></p>
                  </div>
                ))}
              </div>
            ) : <p>该节点是链路起点，直接读取证据仓。</p>}
          </section>
        ) : null}

        {tab === 'parameters' ? (
          <DecisionEntry profile={decisionProfile} stage={decisionStage} onOpen={onOpenDecisions} />
        ) : null}

        {tab === 'parameters' && isBrief && briefDraft ? (
          <form className="inspector-form" onSubmit={(event) => { event.preventDefault(); onSaveBrief(briefDraft); }}>
            <label><span>方案标题</span><input value={briefDraft.title} onChange={(event) => setBriefDraft({ ...briefDraft, title: event.target.value })} /></label>
            <label><span>设计目标</span><textarea rows={5} value={briefDraft.objective} onChange={(event) => setBriefDraft({ ...briefDraft, objective: event.target.value })} /></label>
            <label><span>目标人群</span><input value={briefDraft.audience} onChange={(event) => setBriefDraft({ ...briefDraft, audience: event.target.value })} /></label>
            <label><span>产品形态</span><input value={briefDraft.productType} onChange={(event) => setBriefDraft({ ...briefDraft, productType: event.target.value })} /></label>
            <label><span>设计约束（每行一项）</span><textarea rows={7} value={briefDraft.constraints.join('\n')} onChange={(event) => setBriefDraft({ ...briefDraft, constraints: event.target.value.split('\n').filter(Boolean) })} /></label>
            <button className="primary-button" disabled={busy} type="submit">保存为 v{(node.data.version ?? 1) + 1}</button>
            <p className="form-note">保存只会让下游节点变为 stale，不会自动运行或产生费用。</p>
          </form>
        ) : null}

        {tab === 'parameters' && isPoster && posterDraft ? (
          <form className="inspector-form" onSubmit={(event) => { event.preventDefault(); onSavePoster(posterDraft); }}>
            <label><span>海报标题</span><input value={posterDraft.title} onChange={(event) => setPosterDraft({ ...posterDraft, title: event.target.value })} /></label>
            <label><span>海报副标题</span><textarea rows={4} value={posterDraft.subtitle} onChange={(event) => setPosterDraft({ ...posterDraft, subtitle: event.target.value })} /></label>
            <fieldset className="poster-order">
              <legend>板块显示与顺序</legend>
              {posterDraft.sections.map((section, index) => {
                const visible = !posterDraft.hiddenSections.includes(section);
                return (
                  <div key={section}>
                    <label><input checked={visible} type="checkbox" onChange={(event) => setPosterDraft(updatePosterSection(posterDraft, section, event.target.checked))} /><span>{POSTER_SECTION_LABELS[section] ?? section}</span></label>
                    <button disabled={index === 0} type="button" onClick={() => { const sections = [...posterDraft.sections]; [sections[index - 1], sections[index]] = [sections[index], sections[index - 1]]; setPosterDraft({ ...posterDraft, sections }); }}>↑</button>
                    <button disabled={index === posterDraft.sections.length - 1} type="button" onClick={() => { const sections = [...posterDraft.sections]; [sections[index + 1], sections[index]] = [sections[index], sections[index + 1]]; setPosterDraft({ ...posterDraft, sections }); }}>↓</button>
                  </div>
                );
              })}
            </fieldset>
            <button className="primary-button" disabled={busy} type="submit">保存海报版式</button>
            <button className="secondary-button" type="button" onClick={onExportPoster}>导出当前 PNG</button>
          </form>
        ) : null}

        {tab === 'parameters' && isConcept && conceptDraft ? (
          <form className="inspector-form" onSubmit={(event) => { event.preventDefault(); onSaveConcept(node.id, conceptDraft); }}>
            <label><span>概念标题</span><input value={conceptDraft.title} onChange={(event) => setConceptDraft({ ...conceptDraft, title: event.target.value })} /></label>
            <label><span>概念说明</span><textarea rows={4} value={conceptDraft.summary} onChange={(event) => setConceptDraft({ ...conceptDraft, summary: event.target.value })} /></label>
            <label><span>视觉方向</span><textarea rows={3} value={conceptDraft.direction} onChange={(event) => setConceptDraft({ ...conceptDraft, direction: event.target.value })} /></label>
            <label><span>生成提示词</span><textarea rows={8} value={conceptDraft.prompt} onChange={(event) => setConceptDraft({ ...conceptDraft, prompt: event.target.value })} /></label>
            <button className="primary-button" disabled={busy} type="submit">保存概念编辑</button>
            <div className="concept-parameter-actions">
              <button className="secondary-button" type="button" onClick={() => onActivateConcept(node.id)}>{node.data.active ? '当前采用方向' : '设为当前方向'}</button>
              <button className="secondary-button" type="button" onClick={() => onDuplicateConcept(node.id)}>复制方向</button>
              <button className="secondary-button" disabled={busy} type="button" onClick={() => onRegenerateConcept(node.id)}>重新生成</button>
              <button className="secondary-button" disabled={busy} type="button" onClick={() => onGenerateMoreConcept(node.id)}>生成新方向</button>
            </div>
          </form>
        ) : null}

        {tab === 'parameters' && !isBrief && !isPoster && !isConcept ? (
          <section className="inspector-section">
            <span>运行参数</span>
            <dl className="parameter-list">
              <div><dt>状态</dt><dd>{node.data.status}</dd></div>
              <div><dt>节点类型</dt><dd>{node.type}</dd></div>
              {node.data.version !== undefined ? <div><dt>版本</dt><dd>v{node.data.version}</dd></div> : null}
            </dl>
          </section>
        ) : null}

        {tab === 'outputs' ? (
          <section className="inspector-section">
            <span>节点输出</span>
            <pre>{JSON.stringify(node.data.outputs ?? node.data.brief ?? node.data.poster ?? { title: node.data.title, summary: node.data.summary, status: node.data.status, imageUrl: node.data.imageUrl }, null, 2)}</pre>
            <button className="secondary-button" type="button" onClick={onDownloadPackage}>下载 DesignPackage JSON</button>
          </section>
        ) : null}

        {tab === 'sources' ? (
          <section className="inspector-section">
            <span>证据来源</span>
            <div className="source-list">{(node.data.sourceRefs ?? []).length ? node.data.sourceRefs?.map((source) => <code key={source}>{source}</code>) : <p>该节点没有独立来源，读取上游输出。</p>}</div>
          </section>
        ) : null}

        {tab === 'history' ? (
          <section className="inspector-section">
            <span>版本记录</span>
            <div className="history-list">
              {(node.data.history ?? []).map((item, index) => (
                <div key={`${item.at}-${index}`}><i /><p>{item.event}</p><time>{new Date(item.at).toLocaleString('zh-CN')}</time></div>
              ))}
            </div>
          </section>
        ) : null}

        {tab === 'actions' ? (
          <section className="inspector-actions">
            <button type="button" onClick={() => onOpenDetail(node.id)}><span><ExternalLink aria-hidden="true" size={16} /></span><p><strong>打开完整页面</strong><small>查看该节点的独立展示与引用信息</small></p></button>
            <button disabled={busy} type="button" onClick={() => onRun(node.id)}><span>▶</span><p><strong>{node.data.status === 'idle' ? '运行节点' : '重新运行'}</strong><small>仅运行当前节点</small></p></button>
            <button disabled={busy} type="button" onClick={() => onRunFromHere(node.id)}><span>↳</span><p><strong>从此处运行</strong><small>按依赖顺序运行当前节点与下游</small></p></button>
            {isConcept ? <button disabled={busy} type="button" onClick={() => onActivateConcept(node.id)}><span>◎</span><p><strong>采用此方案</strong><small>设为海报当前概念</small></p></button> : null}
            {isConcept ? <button disabled={busy} type="button" onClick={() => onDuplicateConcept(node.id)}><span>⧉</span><p><strong>复制方案</strong><small>保留当前版本并创建独立分支</small></p></button> : null}
            {isConcept ? <button disabled={busy} type="button" onClick={() => onRegenerateConcept(node.id)}><span>↻</span><p><strong>重新生成</strong><small>只重生成当前方向；需真实图像服务</small></p></button> : null}
            {isConcept ? <button disabled={busy} type="button" onClick={() => onGenerateMoreConcept(node.id)}><span>＋</span><p><strong>生成新方向</strong><small>服务就绪时建立独立方向</small></p></button> : null}
            {isPoster ? <button type="button" onClick={onExportPoster}><span>⇩</span><p><strong>导出 PNG</strong><small>按当前配置输出 1800 × 2400</small></p></button> : null}
          </section>
        ) : null}
      </div>
    </aside>
  );
}

function LoadingScreen({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <main className="loading-screen">
      <div className="loading-mark">Q</div>
      <span>黔艺造物 · 文化创意工作台</span>
      {error ? (
        <><h1>工作台 API 尚未连接</h1><p>{error}</p><code>python -m app.tool_api --port 8787</code><button type="button" onClick={onRetry}>重新连接</button></>
      ) : (
        <><h1>正在装载文化与市场证据</h1><div className="loading-line"><i /></div></>
      )}
    </main>
  );
}

export function Workbench() {
  const [workspace, setWorkspace] = useState<WorkbenchWorkspace | null>(null);
  const [knowledge, setKnowledge] = useState<KnowledgeCenterData | null>(null);
  const [decisionCatalog, setDecisionCatalog] = useState<DecisionCatalog | null>(null);
  const [provider, setProvider] = useState<ImageProviderStatus | null>(null);
  const [workspaceList, setWorkspaceList] = useState<WorkspaceSummary[]>([]);
  const [nodes, setNodes, onNodesChange] = useNodesState<WorkbenchNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<WorkbenchEdge>([]);
  const [selectedNodeId, setSelectedNodeId] = useState('');
  const [flowInstance, setFlowInstance] = useState<ReactFlowInstance<WorkbenchNode, WorkbenchEdge> | null>(null);
  const [connectionError, setConnectionError] = useState('');
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState<Toast>(null);
  const [showGraph, setShowGraph] = useState(false);
  const [activeDock, setActiveDock] = useState<ToolDock>('evidence');
  const [showInspector, setShowInspector] = useState(true);
  const [dialog, setDialog] = useState<'new' | 'rename' | null>(null);
  const [dialogName, setDialogName] = useState('');
  const [showDecisionStudio, setShowDecisionStudio] = useState(false);
  const [decisionStage, setDecisionStage] = useState<DecisionStage>('culture');
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const dockPanelRef = useRef<HTMLDivElement>(null);
  const inspectorPanelRef = useRef<HTMLDivElement>(null);
  const dockTriggerRef = useRef<HTMLElement | null>(null);
  const inspectorTriggerRef = useRef<HTMLElement | null>(null);
  const previousDockRef = useRef<ToolDock>(activeDock);
  const previousInspectorRef = useRef(showInspector);

  const showToast = useCallback((next: Toast) => {
    setToast(next);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 3600);
  }, []);

  const applyWorkspace = useCallback((next: WorkbenchWorkspace) => {
    setWorkspace(next);
    setNodes(next.nodes);
    setEdges(next.edges);
    setSelectedNodeId((current) => next.nodes.some((node) => node.id === current) ? current : next.selected_node_id || next.nodes[0]?.id || '');
  }, [setEdges, setNodes]);

  const load = useCallback(async (workspaceId?: string) => {
    setConnectionError('');
    try {
      const payload = await getBootstrap(workspaceId);
      applyWorkspace(payload.workspace);
      setKnowledge(payload.knowledge);
      setDecisionCatalog(payload.decisionCatalog);
      setProvider(payload.imageProvider);
      setWorkspaceList(payload.workspaces);
    } catch (error) {
      setConnectionError(error instanceof Error ? error.message : String(error));
    }
  }, [applyWorkspace]);

  useEffect(() => {
    const requestedWorkspace = new URLSearchParams(window.location.search).get('workspace');
    const requestedDecision = new URLSearchParams(window.location.search).get('decision');
    const initialLoad = window.setTimeout(
      () => {
        if (requestedDecision && requestedDecision in STAGE_LABELS) {
          setDecisionStage(requestedDecision as DecisionStage);
          setShowDecisionStudio(true);
        }
        void load(requestedWorkspace || undefined);
      },
      0,
    );
    return () => {
      window.clearTimeout(initialLoad);
      if (toastTimer.current) clearTimeout(toastTimer.current);
    };
  }, [load]);

  useEffect(() => {
    const compactViewport = window.matchMedia('(max-width: 760px)');
    const collapsePeripheralPanels = (event?: MediaQueryListEvent) => {
      if ((event ?? compactViewport).matches) {
        setActiveDock(null);
        setShowInspector(false);
      }
    };
    collapsePeripheralPanels();
    compactViewport.addEventListener('change', collapsePeripheralPanels);
    return () => compactViewport.removeEventListener('change', collapsePeripheralPanels);
  }, []);

  useEffect(() => {
    const previousDock = previousDockRef.current;
    previousDockRef.current = activeDock;
    if (!window.matchMedia('(max-width: 760px)').matches) return undefined;
    const focusFrame = window.requestAnimationFrame(() => {
      if (activeDock) {
        const target = dockPanelRef.current?.querySelector<HTMLElement>(
          'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ) ?? dockPanelRef.current;
        target?.focus();
      } else if (previousDock) {
        dockTriggerRef.current?.focus();
      }
    });
    return () => window.cancelAnimationFrame(focusFrame);
  }, [activeDock]);

  useEffect(() => {
    const wasOpen = previousInspectorRef.current;
    previousInspectorRef.current = showInspector;
    if (!window.matchMedia('(max-width: 760px)').matches) return undefined;
    const focusFrame = window.requestAnimationFrame(() => {
      if (showInspector) {
        const target = inspectorPanelRef.current?.querySelector<HTMLElement>(
          'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ) ?? inspectorPanelRef.current;
        target?.focus();
      } else if (wasOpen) {
        inspectorTriggerRef.current?.focus();
      }
    });
    return () => window.cancelAnimationFrame(focusFrame);
  }, [showInspector]);

  useEffect(() => {
    const handleOverlayEscape = (event: KeyboardEvent) => {
      if (event.key !== 'Escape'
        || !window.matchMedia('(max-width: 760px)').matches
        || showDecisionStudio
        || showGraph
        || dialog) return;
      if (showInspector) {
        event.preventDefault();
        setShowInspector(false);
      } else if (activeDock) {
        event.preventDefault();
        setActiveDock(null);
      }
    };
    document.addEventListener('keydown', handleOverlayEscape);
    return () => document.removeEventListener('keydown', handleOverlayEscape);
  }, [activeDock, dialog, showDecisionStudio, showGraph, showInspector]);

  const currentDecisionCatalog = useMemo(() => decisionCatalog ? {
    ...decisionCatalog,
    concepts: nodes
      .filter((node) => node.type === 'ConceptNode')
      .map((node) => ({
        id: node.id,
        label: String(node.data.label ?? node.id),
        title: node.data.title,
        imageUrl: String(node.data.imageUrl ?? ''),
      })),
  } : null, [decisionCatalog, nodes]);

  useEffect(() => {
    if (flowInstance && workspace?.viewport) void flowInstance.setViewport(workspace.viewport, { duration: 300 });
  }, [flowInstance, workspace?.workspace_id, workspace?.viewport]);

  useEffect(() => {
    setNodes((current) => current.map((node) => {
      const selected = node.id === selectedNodeId;
      return node.selected === selected ? node : { ...node, selected };
    }));
  }, [selectedNodeId, setNodes]);

  const snapshotWorkspace = useCallback((overrides?: Partial<WorkbenchWorkspace>): WorkbenchWorkspace => {
    if (!workspace) throw new Error('工作区尚未载入。');
    return { ...workspace, ...overrides, nodes, edges, viewport: flowInstance?.getViewport() ?? workspace.viewport, selected_node_id: selectedNodeId };
  }, [edges, flowInstance, nodes, selectedNodeId, workspace]);

  const persist = useCallback(async (overrides?: Partial<WorkbenchWorkspace>, quiet = false) => {
    const saved = await saveWorkspace(snapshotWorkspace(overrides));
    applyWorkspace(saved);
    if (!quiet) showToast({ tone: 'success', message: '工作区已保存到本地 JSON。' });
    return saved;
  }, [applyWorkspace, showToast, snapshotWorkspace]);

  const openDecisionStudio = useCallback((stage: DecisionStage) => {
    setDecisionStage(stage);
    setShowDecisionStudio(true);
    const url = new URL(window.location.href);
    url.searchParams.set('decision', stage);
    window.history.replaceState({}, '', url);
  }, []);

  const closeDecisionStudio = useCallback(() => {
    setShowDecisionStudio(false);
    const url = new URL(window.location.href);
    url.searchParams.delete('decision');
    window.history.replaceState({}, '', url);
  }, []);

  const openWorkspace = useCallback(async (workspaceId: string) => {
    await load(workspaceId);
    setShowDecisionStudio(false);
    const url = new URL(window.location.href);
    url.searchParams.set('workspace', workspaceId);
    url.searchParams.delete('decision');
    window.history.replaceState({}, '', url);
  }, [load]);

  const handleSaveDecisionProfile = useCallback(async (profile: DecisionProfile) => {
    if (!workspace || busy) return;
    setBusy(true);
    try {
      await persist(undefined, true);
      const updated = await saveDecisionProfile(workspace.workspace_id, profile);
      applyWorkspace(updated);
      closeDecisionStudio();
      showToast({
        tone: 'success',
        message: `人工决策配置已保存为 v${updated.metadata.decision_profile.version}；后续节点已标记待确认。`,
      });
    } catch (error) {
      showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) });
    } finally {
      setBusy(false);
    }
  }, [applyWorkspace, busy, closeDecisionStudio, persist, showToast, workspace]);

  const runSequence = useCallback(async (startId: string | undefined, fromHere: boolean) => {
    if (!workspace || busy) return;
    setBusy(true);
    let runningNodeId = '';
    try {
      let current = await persist(undefined, true);
      const ids = startId
        ? fromHere
          ? orderedRunNodeIds(current.nodes, current.edges, startId)
          : [startId]
        : orderedRunNodeIds(current.nodes, current.edges);
      for (const nodeId of ids) {
        runningNodeId = nodeId;
        setNodes((currentNodes) => markNodeStatus(currentNodes, nodeId, 'running'));
        current = await runNodeRequest(current.workspace_id, nodeId);
        applyWorkspace(current);
      }
      showToast({ tone: 'success', message: fromHere ? `已按依赖顺序完成 ${ids.length} 个节点。` : '节点运行完成。' });
    } catch (error) {
      if (runningNodeId) {
        setNodes((currentNodes) => markNodeStatus(currentNodes, runningNodeId, 'error'));
      }
      showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) });
    } finally {
      setBusy(false);
    }
  }, [applyWorkspace, busy, persist, setNodes, showToast, workspace]);

  const activate = useCallback(async (nodeId: string) => {
    if (!workspace || busy) return;
    setBusy(true);
    try {
      await persist(undefined, true);
      const updated = await activateConcept(workspace.workspace_id, nodeId);
      applyWorkspace(updated);
      showToast({ tone: 'success', message: '已切换当前概念，海报节点已标记待刷新。' });
    } catch (error) {
      showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) });
    } finally { setBusy(false); }
  }, [applyWorkspace, busy, persist, showToast, workspace]);

  useEffect(() => {
    const listener = (event: Event) => {
      const detail = (event as CustomEvent<{ nodeId: string; action: string }>).detail;
      if (detail.action === 'open') {
        window.location.assign(`/nodes/${encodeURIComponent(detail.nodeId)}?workspace=${encodeURIComponent(workspace?.workspace_id ?? 'guizhou-miao-demo')}`);
      } else if (detail.action === 'activate') void activate(detail.nodeId);
      else void runSequence(detail.nodeId, detail.action === 'run-from-here');
    };
    window.addEventListener('qiancraft:node-action', listener);
    return () => window.removeEventListener('qiancraft:node-action', listener);
  }, [activate, runSequence, workspace?.workspace_id]);

  const selectedNode = nodes.find((node) => node.id === selectedNodeId);
  const activeConcept = nodes.find((node) => node.type === 'ConceptNode' && node.data.active);
  const activePhase = phaseForNode(selectedNodeId);

  const handleSaveBrief = useCallback(async (brief: DesignBrief) => {
    if (!workspace || busy) return;
    setBusy(true);
    try {
      await persist(undefined, true);
      const updated = await saveDesignBrief(workspace.workspace_id, brief);
      applyWorkspace(updated);
      showToast({ tone: 'success', message: `任务书已保存为 v${updated.metadata.brief_version}。` });
    } catch (error) {
      showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) });
    } finally { setBusy(false); }
  }, [applyWorkspace, busy, persist, showToast, workspace]);

  const mutateConcept = useCallback(async (nodeId: string, mode: 'duplicate' | 'regenerate' | 'generate-more') => {
    if (!workspace || busy) return;
    setBusy(true);
    try {
      await persist(undefined, true);
      const updated = mode === 'duplicate'
        ? await duplicateConcept(workspace.workspace_id, nodeId)
        : mode === 'generate-more'
          ? await generateMoreConcept(workspace.workspace_id, nodeId)
          : await regenerateConcept(workspace.workspace_id, nodeId);
      applyWorkspace(updated);
      if (mode === 'duplicate' || mode === 'generate-more') {
        setSelectedNodeId(updated.selected_node_id);
        const created = updated.nodes.find((item) => item.id === updated.selected_node_id);
        showToast({
          tone: created?.data.status === 'warning' ? 'neutral' : 'success',
          message: mode === 'duplicate'
            ? '已复制为独立概念分支。'
            : created?.data.status === 'warning'
              ? '新方向已建立；图像服务未配置，没有生成假图片。'
              : '已生成新的概念方向。',
        });
      } else {
        const concept = updated.nodes.find((item) => item.id === nodeId);
        showToast({
          tone: concept?.data.status === 'warning' ? 'neutral' : 'success',
          message: concept?.data.status === 'warning'
            ? '图像服务未配置；已记录 warning，没有生成假图片。'
            : '当前概念已生成新版本。',
        });
      }
    } catch (error) {
      showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) });
    } finally { setBusy(false); }
  }, [applyWorkspace, busy, persist, showToast, workspace]);

  const handleSaveConcept = useCallback(async (nodeId: string, concept: ConceptDraft) => {
    if (!workspace || busy) return;
    setBusy(true);
    try {
      const nextNodes = nodes.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              ...concept,
              status: 'stale' as const,
              history: [{ at: new Date().toISOString(), event: '编辑概念文本与生成参数；等待重生成' }, ...(node.data.history ?? [])],
            },
          };
        }
        if (node.type === 'PosterBoardNode' && nodes.find((item) => item.id === nodeId)?.data.active) {
          return { ...node, data: { ...node.data, status: 'stale' as const } };
        }
        return node;
      });
      const saved = await saveWorkspace({ ...snapshotWorkspace(), nodes: nextNodes });
      applyWorkspace(saved);
      showToast({ tone: 'success', message: '概念编辑已保存；视觉与海报按需重跑。' });
    } catch (error) {
      showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) });
    } finally { setBusy(false); }
  }, [applyWorkspace, busy, nodes, showToast, snapshotWorkspace, workspace]);

  const handleSavePoster = useCallback(async (poster: PosterConfig) => {
    if (!workspace || busy) return;
    setBusy(true);
    try {
      const nextNodes = nodes.map((node) => node.type === 'PosterBoardNode' ? { ...node, data: { ...node.data, title: poster.title, summary: poster.subtitle, poster, status: 'success' as const, history: [{ at: new Date().toISOString(), event: '保存海报标题、板块显示与顺序' }, ...(node.data.history ?? [])] } } : node);
      setNodes(nextNodes);
      const saved = await saveWorkspace({ ...snapshotWorkspace(), nodes: nextNodes });
      applyWorkspace(saved);
      showToast({ tone: 'success', message: '海报版式已保存。' });
    } catch (error) {
      showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) });
    } finally { setBusy(false); }
  }, [applyWorkspace, busy, nodes, setNodes, showToast, snapshotWorkspace, workspace]);

  const handleExportPoster = useCallback(async () => {
    const poster = nodes.find((node) => node.type === 'PosterBoardNode')?.data.poster;
    if (!poster) return;
    try {
      await exportPosterPng(poster, activeConcept);
      showToast({ tone: 'success', message: '已按当前版式导出 1800 × 2400 PNG。' });
    } catch (error) {
      showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) });
    }
  }, [activeConcept, nodes, showToast]);

  const handleDownloadPackage = useCallback(async () => {
    try { downloadJson(await getDesignPackage(), 'QianCraft-DesignPackage.json'); }
    catch (error) { showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) }); }
  }, [showToast]);

  const handleDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (!flowInstance) return;
    const raw = event.dataTransfer.getData('application/qiancraft-knowledge');
    if (!raw) return;
    try {
      const payload = JSON.parse(raw) as { kind: 'culture' | 'market'; item: CultureRecordSummary | { name: string; score: number; sampleSize: number } };
      const type: WorkbenchNodeType = payload.kind === 'culture' ? 'CultureGraphNode' : 'MarketRadarNode';
      const template = nodes.find((node) => node.type === type);
      if (!template) return;
      const name = payload.item.name;
      const next: WorkbenchNode = {
        ...structuredClone(template),
        id: `${payload.kind}-${Date.now().toString(36)}`,
        position: flowInstance.screenToFlowPosition({ x: event.clientX, y: event.clientY }),
        selected: true,
        data: {
          ...structuredClone(template.data),
          title: name,
          summary: payload.kind === 'culture' ? `来自文化证据中心的 ${name} 专题节点。` : `来自四平台产品形态排序的 ${name} 专题节点。`,
          status: 'cached',
          sourceRefs: payload.kind === 'culture' ? (payload.item as CultureRecordSummary).sourceRefs : template.data.sourceRefs,
        },
      };
      setNodes((current) => [...current.map((node) => ({ ...node, selected: false })), next]);
      setSelectedNodeId(next.id);
      showToast({ tone: 'neutral', message: `已在画布创建“${name}”证据节点，保存后持久化。` });
    } catch { showToast({ tone: 'error', message: '拖拽数据无法解析。' }); }
  }, [flowInstance, nodes, setNodes, showToast]);

  const focusNode = useCallback((nodeId: string) => {
    if (!flowInstance || !nodes.some((node) => node.id === nodeId)) return;
    if (document.activeElement instanceof HTMLElement) inspectorTriggerRef.current = document.activeElement;
    setSelectedNodeId(nodeId);
    setShowInspector(true);
    void flowInstance.fitView({
      nodes: [{ id: nodeId }],
      padding: 0.24,
      minZoom: 0.82,
      maxZoom: 1.05,
      duration: 420,
    });
  }, [flowInstance, nodes]);

  const selectNode = useCallback((nodeId: string) => {
    if (document.activeElement instanceof HTMLElement) inspectorTriggerRef.current = document.activeElement;
    setSelectedNodeId(nodeId);
    setShowInspector(true);
    if (!flowInstance || !nodes.some((node) => node.id === nodeId)) return;
    void flowInstance.fitView({
      nodes: [{ id: nodeId }],
      padding: 0.32,
      minZoom: 0.76,
      maxZoom: 0.96,
      duration: 360,
    });
  }, [flowInstance, nodes]);

  const initializeFlow = useCallback((instance: ReactFlowInstance<WorkbenchNode, WorkbenchEdge>) => {
    setFlowInstance(instance);
    if (!window.matchMedia('(max-width: 760px)').matches || !selectedNodeId) return;
    window.setTimeout(() => {
      void instance.fitView({
        nodes: [{ id: selectedNodeId }],
        padding: 0.28,
        minZoom: 0.72,
        maxZoom: 0.88,
        duration: 0,
      });
    }, 120);
  }, [selectedNodeId]);

  const submitDialog = useCallback(async () => {
    if (!dialog || !dialogName.trim() || busy) return;
    setBusy(true);
    try {
      if (dialog === 'new') {
        const created = await createWorkspace(dialogName.trim());
        await openWorkspace(created.workspace_id);
        showToast({ tone: 'success', message: '已创建并打开新工作区。' });
      } else {
        await persist({ name: dialogName.trim() });
        setWorkspaceList((current) => current.map((item) => item.workspace_id === workspace?.workspace_id ? { ...item, name: dialogName.trim() } : item));
      }
      setDialog(null);
    } catch (error) {
      showToast({ tone: 'error', message: error instanceof Error ? error.message : String(error) });
    } finally { setBusy(false); }
  }, [busy, dialog, dialogName, openWorkspace, persist, showToast, workspace?.workspace_id]);

  if (!workspace || !knowledge || !provider || !currentDecisionCatalog) return <LoadingScreen error={connectionError} onRetry={() => void load()} />;

  return (
    <main className="workbench-shell workbench-shell--instrument">
      <header className="app-bar">
        <div className="brand-lockup"><div className="brand-mark">Q</div><strong>QianCraft</strong></div>
        <details className="workspace-command">
          <summary><span>{workspace.name}</span><ChevronDown aria-hidden="true" size={15} /></summary>
          <div className="workspace-command__popover">
            <label><span>当前工作区</span><select value={workspace.workspace_id} onChange={(event) => void openWorkspace(event.target.value)} aria-label="切换工作区">{workspaceList.map((item) => <option key={item.workspace_id} value={item.workspace_id}>{item.name}</option>)}</select></label>
            <div>
              <button type="button" onClick={() => { setDialogName('新文化文创工作区'); setDialog('new'); }}><Plus aria-hidden="true" size={14} />新建</button>
              <button type="button" onClick={() => { setDialogName(workspace.name); setDialog('rename'); }}>重命名</button>
              <button disabled={busy} type="button" onClick={() => void persist()}><Save aria-hidden="true" size={14} />{busy ? '保存中' : '保存'}</button>
            </div>
            <p title={`${API_BASE}/api/health`}><i />API 已连接 · 本地 JSON 持久化</p>
          </div>
        </details>
        <nav className="phase-switcher" aria-label="工作流阶段">
          {PHASE_NAVIGATION.map((phase) => (
            <button className={activePhase === phase.id ? 'is-active' : ''} key={phase.id} type="button" onClick={() => focusNode(phase.nodeId)}>{phase.label}</button>
          ))}
        </nav>
        <div className="app-bar__actions">
          <button className="human-decision-button" type="button" onClick={() => openDecisionStudio(NODE_DECISION_STAGE[selectedNode?.type ?? 'CultureGraphNode'])}><Scale aria-hidden="true" size={17} /><span>人工决策</span><em>v{workspace.metadata.decision_profile.version}</em></button>
          <button className="run-all-button" disabled={busy} type="button" onClick={() => void runSequence(undefined, true)}><Play aria-hidden="true" fill="currentColor" size={16} /><span>{busy ? '运行中' : '运行链路'}</span></button>
        </div>
      </header>

      <div className={`workbench-grid ${activeDock ? 'workbench-grid--dock-open' : ''} ${showInspector ? 'workbench-grid--inspector-open' : ''}`}>
        <nav className="tool-rail" aria-label="工作台工具">
          <div>
            <button aria-label="证据库" aria-pressed={activeDock === 'evidence'} className={activeDock === 'evidence' ? 'is-active' : ''} title="证据库" type="button" onClick={(event) => { dockTriggerRef.current = event.currentTarget; setActiveDock((current) => current === 'evidence' ? null : 'evidence'); }}><Library aria-hidden="true" size={21} /></button>
            <button aria-label="专注画布" aria-pressed={!activeDock} className={!activeDock ? 'is-active' : ''} title="专注画布" type="button" onClick={(event) => { dockTriggerRef.current = event.currentTarget; setActiveDock(null); }}><Workflow aria-hidden="true" size={21} /></button>
            <button aria-label="人工决策" title="人工决策" type="button" onClick={() => openDecisionStudio(NODE_DECISION_STAGE[selectedNode?.type ?? 'CultureGraphNode'])}><Scale aria-hidden="true" size={21} /></button>
            <button aria-label="方案资产" aria-pressed={activeDock === 'assets'} className={activeDock === 'assets' ? 'is-active' : ''} title="方案资产" type="button" onClick={(event) => { dockTriggerRef.current = event.currentTarget; setActiveDock((current) => current === 'assets' ? null : 'assets'); }}><Images aria-hidden="true" size={21} /></button>
            <button aria-label="节点历史" aria-pressed={activeDock === 'history'} className={activeDock === 'history' ? 'is-active' : ''} title="节点历史" type="button" onClick={(event) => { dockTriggerRef.current = event.currentTarget; setActiveDock((current) => current === 'history' ? null : 'history'); }}><History aria-hidden="true" size={21} /></button>
          </div>
          <button aria-label={showInspector ? '收起 Inspector' : '打开 Inspector'} aria-pressed={showInspector} className={showInspector ? 'is-active' : ''} title={showInspector ? '收起 Inspector' : '打开 Inspector'} type="button" onClick={(event) => { inspectorTriggerRef.current = event.currentTarget; setShowInspector((current) => !current); }}><PanelRight aria-hidden="true" size={21} /></button>
        </nav>

        <div aria-label="上下文工具面板" className={`tool-dock ${activeDock ? 'is-open' : ''}`} ref={dockPanelRef} role="region" tabIndex={-1}>
          {activeDock ? <div className="tool-dock__mobile-toolbar"><span>{activeDock === 'evidence' ? '证据库' : activeDock === 'assets' ? '方案资产' : '节点历史'}</span><button aria-label="关闭上下文工具面板" type="button" onClick={() => setActiveDock(null)}><X aria-hidden="true" size={17} /></button></div> : null}
          {activeDock === 'evidence' ? <KnowledgeCenter knowledge={knowledge} profile={workspace.metadata.decision_profile} onOpenGraph={() => setShowGraph(true)} onOpenDecisions={openDecisionStudio} /> : null}
          {activeDock === 'assets' ? <AssetDock nodes={nodes} onSelect={selectNode} /> : null}
          {activeDock === 'history' ? <HistoryDock node={selectedNode} /> : null}
        </div>

        <section className="flow-stage" onDrop={handleDrop} onDragOver={(event) => { event.preventDefault(); event.dataTransfer.dropEffect = 'copy'; }}>
          <ReactFlow<WorkbenchNode, WorkbenchEdge>
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onInit={initializeFlow}
            onNodeClick={(event, node) => { if (event.currentTarget instanceof HTMLElement) inspectorTriggerRef.current = event.currentTarget; setSelectedNodeId(node.id); setShowInspector(true); }}
            onNodeDoubleClick={(_, node) => window.location.assign(`/nodes/${encodeURIComponent(node.id)}?workspace=${encodeURIComponent(workspace.workspace_id)}`)}
            onPaneClick={() => setShowInspector(false)}
            defaultViewport={workspace.viewport}
            defaultEdgeOptions={{ type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: '#8b8984', width: 14, height: 14 }, style: { stroke: '#d4d3d0', strokeWidth: 1.25 } }}
            minZoom={0.3}
            maxZoom={1.65}
            nodesConnectable={false}
            deleteKeyCode={null}
            selectionOnDrag
            panOnDrag={[1, 2]}
          >
            <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#dedbd4" />
            <Controls position="bottom-left" showInteractive={false} />
            <MiniMap pannable zoomable position="bottom-right" nodeBorderRadius={4} nodeColor={(node) => { if (node.type === 'CultureGraphNode') return '#6f8fa4'; if (node.type === 'MarketRadarNode') return '#bd8a76'; if (node.type === 'ConceptNode') return '#6d77a7'; if (node.type === 'PosterBoardNode') return '#1d2836'; return '#9b9994'; }} maskColor="rgba(252, 251, 248, .84)" />
          </ReactFlow>
          <div className="canvas-context"><div><span>当前链路</span><strong>{workspace.metadata.topic}</strong></div><p>{nodes.length} 个节点 · {edges.length} 条关系</p><button type="button" onClick={() => openDecisionStudio('score')}>{workspace.metadata.decision_profile.mode === 'manual' ? '人工配置' : '系统建议'} v{workspace.metadata.decision_profile.version}</button></div>
          <div className="canvas-legend"><span><i className="legend-success" />已就绪</span><span><i className="legend-cached" />证据快照</span><span><i className="legend-stale" />待更新</span></div>
          {showGraph ? <CultureGraphOverlay records={knowledge.culture.records} onClose={() => setShowGraph(false)} /> : null}
        </section>

        <div aria-label="节点 Inspector" className={`inspector-slot ${showInspector ? 'is-open' : ''}`} ref={inspectorPanelRef} role="region" tabIndex={-1}>
          {showInspector ? (
            <>
              <div className="inspector-slot__toolbar"><span>节点信息</span><button aria-label="收起 Inspector" type="button" onClick={() => setShowInspector(false)}><X aria-hidden="true" size={17} /></button></div>
              <InspectorPanel
                key={`${selectedNode?.id ?? 'empty'}-${selectedNode?.data.version ?? workspace.updated_at}`}
                node={selectedNode}
                nodes={nodes}
                edges={edges}
                provider={provider}
                decisionProfile={workspace.metadata.decision_profile}
                busy={busy}
                onOpenDetail={(nodeId) => window.location.assign(`/nodes/${encodeURIComponent(nodeId)}?workspace=${encodeURIComponent(workspace.workspace_id)}`)}
                onRun={(nodeId) => void runSequence(nodeId, false)}
                onRunFromHere={(nodeId) => void runSequence(nodeId, true)}
                onSaveBrief={(brief) => void handleSaveBrief(brief)}
                onSavePoster={(poster) => void handleSavePoster(poster)}
                onActivateConcept={(nodeId) => void activate(nodeId)}
                onDuplicateConcept={(nodeId) => void mutateConcept(nodeId, 'duplicate')}
                onGenerateMoreConcept={(nodeId) => void mutateConcept(nodeId, 'generate-more')}
                onRegenerateConcept={(nodeId) => void mutateConcept(nodeId, 'regenerate')}
                onSaveConcept={(nodeId, concept) => void handleSaveConcept(nodeId, concept)}
                onExportPoster={() => void handleExportPoster()}
                onDownloadPackage={() => void handleDownloadPackage()}
                onOpenDecisions={openDecisionStudio}
              />
            </>
          ) : null}
        </div>
      </div>

      {toast ? <div className={`toast toast--${toast.tone}`}>{toast.message}</div> : null}
      {dialog ? (
        <div className="dialog-backdrop" role="presentation" onMouseDown={() => setDialog(null)}>
          <form className="workspace-dialog" onMouseDown={(event) => event.stopPropagation()} onSubmit={(event) => { event.preventDefault(); void submitDialog(); }}>
            <span>{dialog === 'new' ? 'NEW WORKSPACE' : 'RENAME WORKSPACE'}</span>
            <h2>{dialog === 'new' ? '创建新的文化文创链路' : '重命名当前工作区'}</h2>
            <input autoFocus maxLength={80} value={dialogName} onChange={(event) => setDialogName(event.target.value)} />
            <div><button type="button" onClick={() => setDialog(null)}>取消</button><button className="primary-button" disabled={!dialogName.trim() || busy} type="submit">{dialog === 'new' ? '创建并打开' : '保存名称'}</button></div>
          </form>
        </div>
      ) : null}
      {showDecisionStudio ? (
        <DecisionStudio
          busy={busy}
          catalog={currentDecisionCatalog}
          initialStage={decisionStage}
          profile={workspace.metadata.decision_profile}
          onClose={closeDecisionStudio}
          onSave={(profile) => void handleSaveDecisionProfile(profile)}
        />
      ) : null}
    </main>
  );
}

export default Workbench;
