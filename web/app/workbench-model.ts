import type { Edge, Node, Viewport } from '@xyflow/react';

export const WORKBENCH_NODE_TYPES = [
  'CultureGraphNode',
  'MarketRadarNode',
  'StrategyNode',
  'DesignBriefNode',
  'VisualGenerationNode',
  'ConceptNode',
  'PosterBoardNode',
] as const;

export type WorkbenchNodeType = (typeof WORKBENCH_NODE_TYPES)[number];
export type NodeStatus =
  | 'idle'
  | 'running'
  | 'success'
  | 'warning'
  | 'error'
  | 'cached'
  | 'stale';

export interface WorkbenchHistoryItem {
  at: string;
  event: string;
}

export interface DesignBrief {
  title: string;
  objective: string;
  audience: string;
  productType: string;
  scenarios: string[];
  style: string[];
  constraints: string[];
  factoryBoundary: string;
}

export interface PosterConfig {
  title: string;
  subtitle: string;
  sections: string[];
  hiddenSections: string[];
  cultureElement: string;
  cultureRule: string;
  materials: string[];
  process: string[];
  boundary: string;
  theme?: DecisionPosterTheme;
}

export const DECISION_SCORE_FIELDS = [
  'culture_fit',
  'market_pull',
  'novelty',
  'visual_potential',
  'social_shareability',
  'product_feasibility',
] as const;

export type DecisionScoreField = (typeof DECISION_SCORE_FIELDS)[number];
export type DecisionPosterTheme = 'editorial' | 'workshop' | 'exhibition';
export type DecisionMode = 'guided' | 'manual';

export interface DecisionProfile {
  version: number;
  mode: DecisionMode;
  cultureRecordIds: string[];
  marketPlatforms: string[];
  marketProductForms: string[];
  opportunityIds: string[];
  scoreWeights: Record<DecisionScoreField, number>;
  culturalRiskPenalty: number;
  designIntent: {
    targetAudience: string;
    preferredProductForms: string[];
    priceBand: string;
    useScenarios: string[];
    materialPriorities: string[];
  };
  visualDirection: {
    referenceIds: string[];
    styleKeywords: string[];
    imageSize: string;
    notes: string;
  };
  conceptCompareIds: string[];
  activeConceptId: string;
  posterTheme: DecisionPosterTheme;
  posterSections: string[];
  notes: string;
  updatedAt: string;
}

export interface DecisionOpportunityCatalogItem {
  id: string;
  cultureElement: string;
  trendElement: string;
  systemScore: number;
  verification: string;
  culturalRisk: number;
  scores: Record<DecisionScoreField, number>;
  evidenceRefs: string[];
}

export interface DecisionCatalog {
  cultureRecords: CultureRecordSummary[];
  marketPlatforms: Array<{ id: string; status: string; sampleSize: number }>;
  productForms: Array<{
    id: string;
    rank: number;
    score: number;
    sampleSize: number;
    coverage: number;
  }>;
  opportunities: DecisionOpportunityCatalogItem[];
  visualReferences: Array<{
    id: string;
    title: string;
    region: string | string[];
    subjectType: string;
    rightsStatus: string;
  }>;
  concepts: Array<{ id: string; label: string; title: string; imageUrl: string }>;
  scoreFields: DecisionScoreField[];
  visualSizes: string[];
  posterThemes: DecisionPosterTheme[];
  posterSections: string[];
  recommendedProfile: DecisionProfile;
}

export interface DecisionOutput {
  profileVersion: number;
  mode: DecisionMode;
  selectedCulture: Array<{ id: string; name: string; category: string }>;
  marketScope: {
    platforms: string[];
    productForms: string[];
    selectedPlatformSamples: number;
    selectedFormSamples: number;
  };
  manualRanking: Array<{
    id: string;
    title: string;
    manualScore: number;
    systemScore: number;
    verification: string;
    selected: boolean;
  }>;
  selectedOpportunityIds: string[];
  designIntent: DecisionProfile['designIntent'];
  visualDirection: DecisionProfile['visualDirection'];
  conceptCompareIds: string[];
  activeConceptId: string;
  posterTheme: DecisionPosterTheme;
  posterSections: string[];
}

export interface WorkbenchNodeData extends Record<string, unknown> {
  label: string;
  eyebrow: string;
  title: string;
  summary: string;
  status: NodeStatus;
  stats?: Array<{ label: string; value: string | number }>;
  sourceRefs?: string[];
  history?: WorkbenchHistoryItem[];
  brief?: DesignBrief;
  poster?: PosterConfig;
  version?: number;
  imageUrl?: string;
  active?: boolean;
  labelCode?: string;
}

export type WorkbenchNode = Node<WorkbenchNodeData, WorkbenchNodeType>;
export type WorkbenchEdge = Edge<{ relation?: string }>;

export interface WorkbenchWorkspace {
  schema_version: string;
  workspace_id: string;
  name: string;
  created_at: string;
  updated_at: string;
  viewport: Viewport;
  selected_node_id: string;
  metadata: {
    topic: string;
    region: string;
    target_market: string;
    source_run_id: string;
    selected_concept_id: string;
    brief_version: number;
    node_types: WorkbenchNodeType[];
    product_stage: string;
    stop_before: string;
    research_run_id?: string;
    research_verified_at?: string;
    research_component_modes?: Record<string, string>;
    research_platform_modes?: Record<string, string>;
    design_run_id?: string;
    design_generated_at?: string;
    design_primary_opportunity_id?: string;
    decision_profile: DecisionProfile;
    decision_output: DecisionOutput;
  };
  nodes: WorkbenchNode[];
  edges: WorkbenchEdge[];
}

export interface WorkspaceSummary {
  workspace_id: string;
  name: string;
  updated_at: string;
  topic: string;
}

export interface CultureRecordSummary {
  id: string;
  name: string;
  category: string;
  region: string[];
  crafts: string[];
  patterns: string[];
  boundaries: string[];
  sourceRefs: string[];
}

export interface KnowledgeCenterData {
  culture: {
    recordCount: number;
    sourceCount: number;
    records: CultureRecordSummary[];
  };
  market: {
    status: string;
    sampleSize: number;
    platforms: Record<
      string,
      { status: string; sample_size: number; detail?: string; login_state?: string }
    >;
    ranking: Array<{
      rank: number;
      name: string;
      score: number;
      coverage: number;
      sampleSize: number;
    }>;
  };
}

export interface ImageProviderStatus {
  provider: string;
  model: string;
  base_url_configured: boolean;
  credential_configured: boolean;
  configured: boolean;
  detail: string;
}

export interface ResearchCheck {
  id: string;
  label: string;
  ok: boolean;
  detail: string;
}

export interface ResearchPreflight {
  research_ready: boolean;
  image_generation_ready: boolean;
  interactive_launch: boolean;
  login_method: string;
  checks: ResearchCheck[];
  blockers: string[];
}

export type ResearchJobStatus =
  | 'queued'
  | 'running'
  | 'live_verified'
  | 'failed_no_fallback'
  | 'error';

export interface ResearchJob {
  job_id: string;
  workspace_id: string;
  status: ResearchJobStatus;
  stage: string;
  created_at: string;
  started_at: string;
  finished_at: string;
  detail: string;
  component_modes: Record<string, string>;
  platform_modes: Record<string, string>;
  source_run_id?: string;
}

export interface ResearchRuntime {
  preflight: ResearchPreflight;
  activeJob: ResearchJob | null;
  lastJob: ResearchJob | null;
}

export interface WorkbenchBootstrap {
  workspace: WorkbenchWorkspace;
  workspaces: WorkspaceSummary[];
  knowledge: KnowledgeCenterData;
  decisionCatalog: DecisionCatalog;
  imageProvider: ImageProviderStatus;
  researchRuntime: ResearchRuntime;
  nodeTypes: WorkbenchNodeType[];
  statuses: NodeStatus[];
}

export interface EvidenceCitation {
  id: string;
  kind: 'culture' | 'market' | 'visual_reference' | 'platform_record' | string;
  title: string;
  publisher: string;
  sourceType: string;
  url: string;
  publishedAt: string;
  retrievedAt: string;
  supports: string[];
  rightsStatus: string;
  rightsNote?: string;
}

export interface MarketPostSummary {
  sourceRef: string;
  platform: string;
  title: string;
  publishedAt: string;
  url: string;
  productForm: string;
  searchKeyword: string;
  engagement: Record<'likes' | 'favorites' | 'comments' | 'shares' | 'views', number>;
  platformHotScore: number;
  viralScore: number;
  qualityScore: number;
  qualityReasons: string[];
}

export interface OpportunityDetail {
  opportunity_id: string;
  culture_element: string;
  culture_meaning: string;
  trend_element: string;
  market_signal: string;
  match_reason: string;
  potential_product_categories: string[];
  target_audience: string[];
  design_keywords: string[];
  cultural_constraints: string[];
  evidence_refs: string[];
  confidence_score: number;
  culture_fit: number;
  market_pull: number;
  novelty: number;
  visual_potential: number;
  social_shareability: number;
  product_feasibility: number;
  cultural_risk: number;
  overall_score: number;
  reason: string;
  verification: {
    status: string;
    retrieval_mode: string;
    warnings: string[];
    conflicts: string[];
    notes: string[];
  };
}

export interface NodeDetailPayload {
  workspace: {
    id: string;
    name: string;
    updatedAt: string;
    topic: string;
    sourceRunId: string;
  };
  node: WorkbenchNode;
  relatedNodes: Array<{
    id: string;
    type: WorkbenchNodeType;
    title: string;
    status: NodeStatus;
    relation: 'upstream' | 'downstream';
  }>;
  content: {
    records?: Array<CultureRecordSummary & Record<string, unknown>>;
    visualReferences?: Array<Record<string, unknown>>;
    platforms?: Record<string, { status: string; sample_size: number; detail?: string }>;
    sampleSize?: number;
    platformSampleSizes?: Record<string, number>;
    ranking?: Array<Record<string, unknown>>;
    representativePosts?: MarketPostSummary[];
    methodology?: Record<string, unknown> | string[];
    generatedAt?: string;
    opportunities?: OpportunityDetail[];
    scoring?: Record<string, unknown>;
    evidenceSummary?: Record<string, unknown>;
    recommendedCategories?: string[];
    designKeywords?: string[];
    culturalConstraints?: string[];
    brief?: DesignBrief;
    selection?: Record<string, unknown>;
    product?: Record<string, unknown>;
    reviewGates?: string[];
    engineeringGates?: string[];
    provider?: ImageProviderStatus;
    prompts?: string[];
    concepts?: WorkbenchNode[];
    posterRequest?: Record<string, unknown>;
    concept?: WorkbenchNode;
    culturalElements?: Array<Record<string, unknown>>;
    manufacturing?: Record<string, unknown>;
    validation?: Record<string, unknown>;
    poster?: PosterConfig;
    activeConcept?: WorkbenchNode | null;
    decisionProfile?: DecisionProfile;
    decisionOutput?: DecisionOutput;
  };
  citations: EvidenceCitation[];
  citationAudit: {
    requested: number;
    resolved: number;
    missing: string[];
  };
  boundary: string;
}

export const STATUS_LABELS: Record<NodeStatus, string> = {
  idle: '待运行',
  running: '运行中',
  success: '已完成',
  warning: '需配置',
  error: '失败',
  cached: '证据快照',
  stale: '待重跑',
};

export const NODE_TYPE_LABELS: Record<WorkbenchNodeType, string> = {
  CultureGraphNode: '文化图谱',
  MarketRadarNode: '市场雷达',
  StrategyNode: '机会策略',
  DesignBriefNode: '设计任务书',
  VisualGenerationNode: '视觉生成',
  ConceptNode: '概念方向',
  PosterBoardNode: '概念海报',
};

export function displayNodeSummary(type: WorkbenchNodeType, summary: string): string {
  if (
    type === 'VisualGenerationNode'
    && (summary.includes('Concept A / B / C') || summary.includes('Images API'))
  ) {
    return '三套概念方向已具备可展示视觉；文本链路已经实机验证，重新生成仍需配置独立图像服务。';
  }
  return summary;
}

export function downstreamNodeIds(
  edges: WorkbenchEdge[],
  startId: string,
): string[] {
  const adjacency = new Map<string, string[]>();
  for (const edge of edges) {
    adjacency.set(edge.source, [...(adjacency.get(edge.source) ?? []), edge.target]);
  }
  const queue = [...(adjacency.get(startId) ?? [])];
  const visited = new Set<string>();
  while (queue.length > 0) {
    const current = queue.shift();
    if (!current || visited.has(current)) continue;
    visited.add(current);
    queue.push(...(adjacency.get(current) ?? []));
  }
  return [...visited];
}

export function orderedRunNodeIds(
  nodes: WorkbenchNode[],
  edges: WorkbenchEdge[],
  startId?: string,
): string[] {
  const scope = startId
    ? new Set([startId, ...downstreamNodeIds(edges, startId)])
    : new Set(nodes.map((node) => node.id));
  const incoming = new Map<string, number>();
  const adjacency = new Map<string, string[]>();
  for (const id of scope) incoming.set(id, 0);
  for (const edge of edges) {
    if (!scope.has(edge.source) || !scope.has(edge.target)) continue;
    adjacency.set(edge.source, [...(adjacency.get(edge.source) ?? []), edge.target]);
    incoming.set(edge.target, (incoming.get(edge.target) ?? 0) + 1);
  }
  const queue = nodes
    .filter((node) => scope.has(node.id) && (incoming.get(node.id) ?? 0) === 0)
    .map((node) => node.id);
  const ordered: string[] = [];
  while (queue.length > 0) {
    const current = queue.shift();
    if (!current) continue;
    ordered.push(current);
    for (const next of adjacency.get(current) ?? []) {
      const count = (incoming.get(next) ?? 0) - 1;
      incoming.set(next, count);
      if (count === 0) queue.push(next);
    }
  }
  return ordered.length === scope.size ? ordered : nodes.filter((node) => scope.has(node.id)).map((node) => node.id);
}

export function markNodeStatus(
  nodes: WorkbenchNode[],
  nodeId: string,
  status: NodeStatus,
): WorkbenchNode[] {
  return nodes.map((node) =>
    node.id === nodeId ? { ...node, data: { ...node.data, status } } : node,
  );
}

export function markDownstreamStale(
  nodes: WorkbenchNode[],
  edges: WorkbenchEdge[],
  sourceId: string,
): WorkbenchNode[] {
  const downstream = new Set(downstreamNodeIds(edges, sourceId));
  return nodes.map((node) =>
    downstream.has(node.id)
      ? { ...node, data: { ...node.data, status: 'stale' as const } }
      : node,
  );
}

export function apiAssetUrl(path: string | undefined, apiBase: string): string {
  if (!path) return '';
  if (/^https?:\/\//.test(path) || path.startsWith('data:')) return path;
  return `${apiBase}${path.startsWith('/') ? path : `/${path}`}`;
}

export function updatePosterSection(
  poster: PosterConfig,
  section: string,
  visible: boolean,
): PosterConfig {
  const hidden = new Set(poster.hiddenSections);
  if (visible) hidden.delete(section);
  else hidden.add(section);
  return { ...poster, hiddenSections: [...hidden] };
}

export function calculateManualOpportunityScore(
  opportunity: DecisionOpportunityCatalogItem,
  weights: Record<DecisionScoreField, number>,
  riskPenalty: number,
): number {
  const totalWeight = DECISION_SCORE_FIELDS.reduce(
    (sum, field) => sum + Math.max(0, Number(weights[field] ?? 0)),
    0,
  );
  if (totalWeight <= 0) return 0;
  const weighted = DECISION_SCORE_FIELDS.reduce(
    (sum, field) => sum + Number(opportunity.scores[field] ?? 0) * Math.max(0, Number(weights[field] ?? 0)),
    0,
  ) / totalWeight;
  if (opportunity.verification === 'rejected') return 0;
  const warningPenalty = opportunity.verification === 'warning' ? 5 : 0;
  return Math.round(
    Math.max(0, Math.min(100, weighted - riskPenalty * opportunity.culturalRisk - warningPenalty)) * 10,
  ) / 10;
}

export function toggleDecisionSelection(
  values: string[],
  value: string,
  maxItems = Number.POSITIVE_INFINITY,
): string[] {
  if (values.includes(value)) return values.filter((item) => item !== value);
  return values.length >= maxItems ? values : [...values, value];
}
