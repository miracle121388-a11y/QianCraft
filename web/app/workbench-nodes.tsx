'use client';

import { Handle, Position, type NodeProps, type NodeTypes } from '@xyflow/react';

import {
  NODE_TYPE_LABELS,
  STATUS_LABELS,
  type NodeStatus,
  type WorkbenchNode,
} from './workbench-model';

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
  source = true,
  target = true,
  wide = false,
}: {
  node: Pick<WorkbenchNode, 'id' | 'type' | 'data'>;
  selected: boolean;
  source?: boolean;
  target?: boolean;
  wide?: boolean;
}) {
  const { data } = node;
  return (
    <article
      aria-current={selected ? 'step' : undefined}
      aria-label={`${NODE_TYPE_LABELS[node.type]}：${data.title}，${STATUS_LABELS[data.status]}`}
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
          {data.decisionVersion ? (
            <span className="node-human-tag">人工 v{String(data.decisionVersion)}</span>
          ) : null}
          <StatusBadge status={data.status} />
        </div>
      </header>
      {source ? <Handle type="source" position={Position.Right} /> : null}
    </article>
  );
}

function CultureGraphNode(props: NodeProps<WorkbenchNode>) {
  return <NodeFrame node={props} selected={props.selected} target={false} />;
}

function MarketRadarNode(props: NodeProps<WorkbenchNode>) {
  return <NodeFrame node={props} selected={props.selected} target={false} />;
}

function StrategyNode(props: NodeProps<WorkbenchNode>) {
  return <NodeFrame node={props} selected={props.selected} />;
}

function DesignBriefNode(props: NodeProps<WorkbenchNode>) {
  return <NodeFrame node={props} selected={props.selected} />;
}

function VisualGenerationNode(props: NodeProps<WorkbenchNode>) {
  return <NodeFrame node={props} selected={props.selected} wide />;
}

function ConceptNode(props: NodeProps<WorkbenchNode>) {
  return <NodeFrame node={props} selected={props.selected} wide />;
}

function PosterBoardNode(props: NodeProps<WorkbenchNode>) {
  return <NodeFrame node={props} selected={props.selected} source={false} wide />;
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
