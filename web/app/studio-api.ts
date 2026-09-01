import type {
  CultureLibrary,
  ProductFormLibrary,
  StudioAutomation,
  StudioDesign,
  StudioEvent,
  StudioOverview,
} from './studio-model';

export const STUDIO_API_BASE = (
  process.env.NEXT_PUBLIC_QIANCRAFT_API_URL ?? ''
).replace(/\/$/, '');

export class StudioApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'StudioApiError';
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${STUDIO_API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  });
  const payload = (await response.json().catch(() => ({}))) as T & { error?: string };
  if (!response.ok) {
    throw new StudioApiError(payload.error || `QianCraft API 返回 ${response.status}`, response.status);
  }
  return payload;
}

export function studioAssetUrl(path: string): string {
  if (!path) return '';
  if (/^https?:\/\//.test(path) || path.startsWith('data:')) return path;
  return `${STUDIO_API_BASE}${path}`;
}

export function getStudioOverview(): Promise<StudioOverview> {
  return request<StudioOverview>('/api/studio/overview');
}

export function getCultureLibrary(): Promise<CultureLibrary> {
  return request<CultureLibrary>('/api/studio/libraries/culture');
}

export function getFormLibrary(): Promise<ProductFormLibrary> {
  return request<ProductFormLibrary>('/api/studio/libraries/forms');
}

export function listStudioDesigns(): Promise<{ count: number; designs: StudioDesign[] }> {
  return request<{ count: number; designs: StudioDesign[] }>('/api/studio/designs');
}

export function getStudioDesign(designId: string): Promise<StudioDesign> {
  return request<StudioDesign>(`/api/studio/designs/${encodeURIComponent(designId)}`);
}

export function generateManualDesign(candidate: {
  cultureIds: string[];
  productFormIds: string[];
  title?: string;
  concept?: string;
  audience?: string;
  useScenario?: string;
  designNotes?: string;
  palette?: string;
}): Promise<StudioDesign> {
  return request<StudioDesign>('/api/studio/combinations', {
    method: 'POST',
    body: JSON.stringify(candidate),
  });
}

export function reviseStudioDesign(
  designId: string,
  candidate: {
    cultureIds: string[];
    productFormIds: string[];
    title: string;
    concept: string;
    audience: string;
    useScenario: string;
    designNotes: string;
    palette: string;
  },
): Promise<StudioDesign> {
  return request<StudioDesign>(`/api/studio/designs/${encodeURIComponent(designId)}`, {
    method: 'PUT',
    body: JSON.stringify(candidate),
  });
}

export function runDailyDesign(): Promise<StudioAutomation> {
  return request<StudioAutomation>('/api/studio/automation/run', {
    method: 'POST',
    body: '{}',
  });
}

export function updateDailySchedule(candidate: {
  enabled?: boolean;
  hour?: number;
  minute?: number;
}): Promise<StudioAutomation> {
  return request<StudioAutomation>('/api/studio/automation/schedule', {
    method: 'PUT',
    body: JSON.stringify(candidate),
  });
}

export function getStudioEvents(limit = 60): Promise<{ events: StudioEvent[] }> {
  return request<{ events: StudioEvent[] }>(`/api/studio/automation/events?limit=${limit}`);
}

export function runCollectionLane(lane: 'culture_watch' | 'market_refresh' | 'all') {
  return request<StudioOverview['automation']['collection']>('/api/collection/run', {
    method: 'POST',
    body: JSON.stringify({ lane }),
  });
}
