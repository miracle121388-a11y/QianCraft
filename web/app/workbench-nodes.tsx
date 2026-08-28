'use client';

import { Handle, Position, type NodeProps, type NodeTypes } from '@xyflow/react';

import { API_BASE } from './workbench-api';
import {
  NODE_TYPE_LABELS,
  STATUS_LABELS,
  apiAssetUrl,
  displayNodeSummary,
  type NodeStatus,
  type PosterConfig,
  type WorkbenchNode,
} from './workbench-model';

function emitNodeAction(nodeId: string, action: 'run' | 'run-from-here' | 'activate' | 'open') {
  window.dispatchEvent(
    new CustomEvent('qiancraft:node-action', { detail: { nodeId, action } }),
  );
}

function StatusBadge({ status }: { status: NodeStatus }) {
  return (
    <span className={`node-status node-status--${status}`}>
      <i aria-hidden="true" />
      {STATUS_LABELS[status]}
    </span>
  );
}

function NodeFrame({
  node,
  selected,
  children,
  source = true,
  target = true,
  wide = false,
}: {
  node: Pick<WorkbenchNode, 'id' | 'type' | 'data'>;
  selected: boolean;
  children: React.ReactNode;
  source?: boolean;
  target?: boolean;
  wide?: boolean;
}) {
  const { data } = node;
  return (
    <article
      className={`flow-node flow-node--${node.type} ${wide ? 'flow-node--wide' : ''} ${
        selected ? 'is-selected' : ''
      }`}
    >
      {target ? <Handle type="target" position={Position.Left} /> : null}
      <header className="flow-node__header">
        <div>
          <p>{NODE_TYPE_LABELS[node.type]}</p>
          <h3>{data.title}</h3>
        </div>
        <div className="flow-node__state-stack">
          {data.decisionVersion ? <span className="node-human-tag">人工 v{String(data.decisionVersion)}</span> : null}
          <StatusBadge status={data.status} />
        </div>
      </header>
      <div className="flow-node__body">{children}</div>
      <footer className="flow-node__footer">
        <button
          className="nodrag flow-node__detail"
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            emitNodeAction(node.id, 'open');
          }}
        >
          打开详情 ↗
        </button>
        <button
          className="nodrag"
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            emitNodeAction(node.id, 'run');
          }}
        >
          {data.status === 'idle' ? '运行' : '重新运行'}
        </button>
        <button
          className="nodrag"
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            emitNodeAction(node.id, 'run-from-here');
          }}
        >
          从此运行
        </button>
      </footer>
      {source ? <Handle type="source" position={Position.Right} /> : null}
    </article>
  );
}

function StatRow({ data }: { data: WorkbenchNode['data'] }) {
  if (!data.stats?.length) return null;
  return (
    <div className="node-stats">
      {data.stats.map((stat) => (
        <div key={stat.label}>
          <strong>{stat.value}</strong>
          <span>{stat.label}</span>
        </div>
      ))}
    </div>
  );
}

function CultureGraphNode(props: NodeProps<WorkbenchNode>) {
  return (
    <NodeFrame node={props} selected={props.selected} target={false}>
      <p className="node-summary">{props.data.summary}</p>
      <StatRow data={props.data} />
      <div className="motif-grid" aria-label="文化要素预览">
        <span>数纱</span>
        <span>挑花</span>
        <span>支系</span>
        <span>边界</span>
      </div>
    </NodeFrame>
  );
}

function MarketRadarNode(props: NodeProps<WorkbenchNode>) {
  const topForms = (props.data.topForms ?? []) as Array<{
    name: string;
    score: number;
    sampleSize: number;
  }>;
  return (
    <NodeFrame node={props} selected={props.selected} target={false}>
      <p className="node-summary">{props.data.summary}</p>
      <StatRow data={props.data} />
      <div className="mini-ranking">
        {topForms.slice(0, 3).map((item) => (
          <div key={item.name}>
            <span>{item.name}</span>
            <i style={{ width: `${Math.min(100, item.score)}%` }} />
            <b>{item.score}</b>
          </div>
        ))}
      </div>
    </NodeFrame>
  );
}

function StrategyNode(props: NodeProps<WorkbenchNode>) {
  const opportunities = (props.data.opportunities ?? []) as Array<{
    id: string;
    title: string;
    score: number;
  }>;
  return (
    <NodeFrame node={props} selected={props.selected}>
      <p className="node-summary">{props.data.summary}</p>
      <div className="opportunity-stack">
        {opportunities.slice(0, 3).map((item, index) => (
          <div key={item.id}>
            <span>0{index + 1}</span>
            <p>{item.title}</p>
            <strong>{item.score}</strong>
          </div>
        ))}
      </div>
    </NodeFrame>
  );
}

function DesignBriefNode(props: NodeProps<WorkbenchNode>) {
  const brief = props.data.brief;
  return (
    <NodeFrame node={props} selected={props.selected}>
      <p className="node-summary">{props.data.summary}</p>
      <div className="brief-keyline">
        <span>目标人群</span>
        <strong>{brief?.audience ?? '—'}</strong>
      </div>
      <div className="brief-keyline">
        <span>产品形态</span>
        <strong>{brief?.productType ?? '—'}</strong>
      </div>
      <div className="node-version">任务书 v{props.data.version ?? 1}</div>
    </NodeFrame>
  );
}

function VisualGenerationNode(props: NodeProps<WorkbenchNode>) {
  const provider = props.data.provider as
    | { provider?: string; model?: string; configured?: boolean; detail?: string }
    | undefined;
  return (
    <NodeFrame node={props} selected={props.selected} wide>
      <p className="node-summary">{displayNodeSummary('VisualGenerationNode', props.data.summary)}</p>
      <div className="visual-slots">
        {['A', 'B', 'C'].map((label) => (
          <div key={label}>
            <span>{label}</span>
            <i />
          </div>
        ))}
      </div>
      <div className="provider-line">
        <i className={provider?.configured ? 'is-ready' : ''} />
        <span>{provider?.configured ? provider.model : '图像服务未配置'}</span>
      </div>
    </NodeFrame>
  );
}

function ConceptNode(props: NodeProps<WorkbenchNode>) {
  const image = apiAssetUrl(props.data.imageUrl, API_BASE);
  return (
    <NodeFrame node={props} selected={props.selected} wide>
      <button
        className={`concept-preview nodrag ${props.data.active ? 'is-active' : ''}`}
        type="button"
        onClick={(event) => {
          event.stopPropagation();
          emitNodeAction(props.id, 'activate');
        }}
      >
        {image ? (
          // API assets are generated or project-owned concept images, not remote reference pixels.
          // eslint-disable-next-line @next/next/no-img-element
          <img src={image} alt={`${props.data.title} 概念图`} />
        ) : (
          <span className="concept-empty">
            <b>{String(props.data.label ?? '').replace('概念 ', '')}</b>
            等待生成
          </span>
        )}
        {props.data.active ? <em>当前</em> : <em>采用</em>}
      </button>
      <p className="concept-direction">{String(props.data.direction ?? props.data.summary)}</p>
      <div className="concept-meta">
        <span>v{props.data.version ?? 0}</span>
        <span>{props.data.active ? '当前采用' : props.data.inComparison ? '比较组' : '未选用'}</span>
      </div>
    </NodeFrame>
  );
}

function PosterBoardNode(props: NodeProps<WorkbenchNode>) {
  const poster = props.data.poster as PosterConfig | undefined;
  const image = apiAssetUrl(props.data.imageUrl, API_BASE);
  return (
    <NodeFrame node={props} selected={props.selected} source={false} wide>
      <div className="poster-preview">
        {image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={image} alt="QianCraft 当前概念海报" />
        ) : null}
        <div>
          <span>QianCraft · 概念提案</span>
          <strong>{poster?.title ?? props.data.title}</strong>
          <p>{poster?.subtitle ?? props.data.summary}</p>
        </div>
      </div>
      <div className="poster-sections">
        {(poster?.sections ?? []).map((section) => (
          <span
            className={poster?.hiddenSections.includes(section) ? 'is-hidden' : ''}
            key={section}
          >
            {section}
          </span>
        ))}
      </div>
    </NodeFrame>
  );
}

export const nodeTypes: NodeTypes = {
  CultureGraphNode,
  MarketRadarNode,
  StrategyNode,
  DesignBriefNode,
  VisualGenerationNode,
  ConceptNode,
  PosterBoardNode,
};
