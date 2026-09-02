export interface CultureSource {
  source_id: string;
  source_title: string;
  publisher: string;
  source_url: string;
  source_type: string;
  published_at?: string;
  retrieved_at?: string;
}

export interface CultureLibraryRecord {
  id: string;
  name: string;
  aliases: string[];
  category: string;
  region: string[];
  crafts: string[];
  materials: string[];
  modernizableElements: string[];
  nonTransferableElements: string[];
  culturalTaboos: string[];
  sourceRefs: string[];
  missingSourceRefs: string[];
  sourceDetails: CultureSource[];
  evidenceScore: number;
  evidenceScoreBreakdown: {
    overall: number;
    verifiedSourceCount: number;
    sourceSufficiency: number;
    regionalSpecificity: number;
    translationCompleteness: number;
    formula: string;
  };
}

export interface CultureLibrary {
  schemaVersion: string;
  kind: 'culture';
  title: string;
  updatedAt: string;
  recordCount: number;
  sourceCount: number;
  records: CultureLibraryRecord[];
  promotionPolicy: string;
  evidenceScorePolicy: string;
}

export interface MarketRepresentativePost {
  platform: string;
  source_ref: string;
  title: string;
  content: string;
  author: string;
  published_at: string;
  retrieved_at: string;
  url: string;
  likes: number;
  favorites: number;
  comments: number;
  shares: number;
  views: number;
  platform_hot_score: number;
}

export interface ProductFormRecord {
  id: string;
  name: string;
  rank: number;
  hotScore: number;
  sampleSize: number;
  platformCoverage: number;
  platformScores: Record<string, number>;
  platformPostCounts: Record<string, number>;
  freshnessScore: number;
  whyHot: string[];
  representativePosts: MarketRepresentativePost[];
  sourceRefs: string[];
  renderer: string;
  rendererLabel: string;
  executable: boolean;
  evidenceReady: boolean;
}

export interface ProductFormLibrary {
  schemaVersion: string;
  kind: 'product_form';
  title: string;
  generatedAt: string;
  sampleSize: number;
  platforms: string[];
  recordCount: number;
  records: ProductFormRecord[];
  methodology: {
    name?: string;
    platform_hot_score?: string;
    cross_platform_hot_score?: string;
    high_hot_threshold?: number;
    claim_boundary?: string;
  };
  evidenceBoundary: string;
}

export interface CombinationScores {
  overall: number;
  cultureEvidence: number;
  marketEvidence: number;
  observedHotScore: number;
  compatibility: number;
  translationSpace: number;
  boundarySafety: number;
  formula: string;
  scoreVersion: string;
}

export interface StudioGenerationRecord {
  role: 'design_visual' | 'production_communication_visual' | string;
  provider: string;
  model: string;
  mode: 'text_to_image' | 'image_to_image' | string;
  prompt: string;
  promptSha256: string;
  inputAssetSha256: string;
}

export interface StudioGeneratedAsset {
  imageUrl: string;
  filename: string;
  sha256: string;
  width: number;
  height: number;
  generatedAt: string;
  generation?: StudioGenerationRecord;
}

export interface StudioDesign {
  schemaVersion: string;
  designId: string;
  batchId: string;
  origin: 'daily' | 'manual';
  trigger: string;
  dailyDate: string;
  dailyRank: number;
  superseded: boolean;
  status: string;
  version: number;
  createdAt: string;
  updatedAt: string;
  title: string;
  subtitle: string;
  cultureItems: CultureLibraryRecord[];
  productForms: ProductFormRecord[];
  scores: CombinationScores;
  selection: {
    policy: string;
    rank: number;
    candidateGate: string;
  };
  concept: {
    statement: string;
    audience: string;
    useScenarios: string[];
    contentTranslation: string[];
    formExpression: string[];
    materials: string[];
    interaction: string[];
    designNotes: string;
    doNotUse: string[];
  };
  visualDirection: {
    palette: 'slate' | 'indigo' | 'vermilion';
    renderer: string;
    rendererLabel: string;
    style: string;
  };
  workflow: {
    lastRegeneratedFrom: string;
    stages: Array<{
      id: string;
      label: string;
      status: string;
      editable: boolean;
    }>;
  };
  provenance: {
    cultureRecordIds: string[];
    cultureSourceRefs: string[];
    marketSourceRefs: string[];
    marketSampleSize: number;
    marketSnapshotGeneratedAt: string;
    renderer: string;
    imageGenerationUsed: boolean;
    imageProvider?: string;
    imageModel?: string;
    claim: string;
  };
  production: {
    status: string;
    visualStatus?: string;
    massProductionReady: boolean;
    boundary: string;
    asset?: StudioGeneratedAsset;
  };
  revisionHistory: Array<{
    version: number;
    at: string;
    title: string;
    cultureNames: string[];
    productFormNames: string[];
    concept: string;
    palette: string;
    scoreOverall: number;
    assetSha256: string;
    imageUrl: string;
    productionAssetSha256?: string;
    productionImageUrl?: string;
  }>;
  asset: StudioGeneratedAsset;
}

export interface StudioAutomation {
  schemaVersion: string;
  enabled: boolean;
  schedule: {
    hour: number;
    minute: number;
    timezone: string;
    limit: number;
  };
  scheduler: {
    status: string;
    instanceId: string;
    startedAt: string;
    heartbeatAt: string;
    threadAlive: boolean;
  };
  daily: {
    status: string;
    lastAttemptAt: string;
    lastSuccessAt: string;
    lastBatchId: string;
    nextRunAt: string;
    detail: string;
    runCount: number;
    consecutiveFailures: number;
    generatedCount: number;
  };
  today: {
    date: string;
    designCount: number;
    designIds: string[];
  };
  policy: string;
}

export interface CollectionSummary {
  enabled: boolean;
  scheduler: {
    status: string;
    heartbeatAt: string;
    threadAlive: boolean;
  };
  lanes: Record<
    'culture_watch' | 'market_refresh',
    {
      label: string;
      enabled: boolean;
      intervalMinutes: number;
      status: string;
      lastAttemptAt: string;
      lastSuccessAt: string;
      nextRunAt: string;
      detail: string;
      runCount: number;
      consecutiveFailures: number;
    }
  >;
  culture: {
    verifiedRecords: number;
    verifiedSources: number;
    candidateCounts: Record<string, number>;
  };
  market: {
    preflight: {
      research_ready: boolean;
      blockers: string[];
    };
  };
}

export interface StudioOverview {
  schemaVersion: string;
  today: {
    date: string;
    designCount: number;
    designs: StudioDesign[];
    policy: string;
  };
  libraries: {
    culture: { recordCount: number; sourceCount: number; updatedAt: string };
    forms: {
      recordCount: number;
      sampleSize: number;
      platforms: string[];
      generatedAt: string;
    };
  };
  automation: {
    dailyDesign: StudioAutomation;
    collection: CollectionSummary;
    imageGeneration: {
      provider: string;
      model: string;
      base_url_configured: boolean;
      credential_configured: boolean;
      configured: boolean;
      supports_image_to_image: boolean;
      detail: string;
    };
  };
  recentDesigns: StudioDesign[];
  truthBoundary: string;
}

export interface StudioEvent {
  id: string;
  at: string;
  event: string;
  status: string;
  detail: string;
  metadata: Record<string, unknown>;
}

export function formatStudioTime(value: string): string {
  if (!value) return '尚未运行';
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

export const STUDIO_STATUS_LABELS: Record<string, string> = {
  healthy: '正常',
  running: '运行中',
  scheduled: '已排程',
  paused: '已暂停',
  blocked: '受阻',
  degraded: '部分异常',
  failed: '失败',
  interrupted: '已中断',
  generated: '已生成',
  verified: '已核验',
  verified_snapshot: '历史实证',
  generated_local: '本地生成',
  generated_model: '模型生成',
  concept_visual_generated: '沟通图已生成',
  not_ready: '待验证',
};
