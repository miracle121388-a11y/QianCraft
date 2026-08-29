import type {
  CollectionCandidate,
  CollectionEvent,
  CollectionLaneId,
  CollectionRuntime,
  DesignBrief,
  DecisionProfile,
  NodeDetailPayload,
  ResearchJob,
  ResearchRuntime,
  WorkbenchBootstrap,
  WorkbenchWorkspace,
} from './workbench-model';

export const API_BASE = (
  process.env.NEXT_PUBLIC_QIANCRAFT_API_URL ?? ''
).replace(/\/$/, '');

export class WorkbenchApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'WorkbenchApiError';
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  });
  const payload = (await response.json().catch(() => ({}))) as { error?: string } & T;
  if (!response.ok) {
    throw new WorkbenchApiError(
      payload.error || `QianCraft API 返回 ${response.status}`,
      response.status,
    );
  }
  return payload;
}

export function getBootstrap(workspaceId?: string): Promise<WorkbenchBootstrap> {
  const query = workspaceId ? `?workspace_id=${encodeURIComponent(workspaceId)}` : '';
  return request<WorkbenchBootstrap>(`/api/workbench/bootstrap${query}`);
}

export function getResearchRuntime(
  workspaceId: string,
  allowInteractive = true,
): Promise<ResearchRuntime> {
  const query = new URLSearchParams({
    workspace_id: workspaceId,
    allow_interactive: String(allowInteractive),
  });
  return request<ResearchRuntime>(`/api/research/status?${query}`);
}

export function startResearchRun(
  workspaceId: string,
  allowInteractive = true,
): Promise<ResearchJob> {
  return request<ResearchJob>('/api/research/run', {
    method: 'POST',
    body: JSON.stringify({
      workspace_id: workspaceId,
      allow_interactive: allowInteractive,
    }),
  });
}

export function getResearchJob(jobId: string): Promise<ResearchJob> {
  return request<ResearchJob>(`/api/research/jobs/${encodeURIComponent(jobId)}`);
}

export function getCollectionRuntime(): Promise<CollectionRuntime> {
  return request<CollectionRuntime>('/api/collection/status');
}

export function getCollectionEvents(limit = 60): Promise<{ events: CollectionEvent[] }> {
  return request<{ events: CollectionEvent[] }>(`/api/collection/events?limit=${limit}`);
}

export function getCollectionCandidates(
  status = '',
  limit = 80,
): Promise<{ candidates: CollectionCandidate[] }> {
  const query = new URLSearchParams({ limit: String(limit) });
  if (status) query.set('status', status);
  return request<{ candidates: CollectionCandidate[] }>(`/api/collection/candidates?${query}`);
}

export function runCollectionLane(lane: CollectionLaneId | 'all'): Promise<CollectionRuntime> {
  return request<CollectionRuntime>('/api/collection/run', {
    method: 'POST',
    body: JSON.stringify({ lane }),
  });
}

export function updateCollectionSchedule(candidate: {
  enabled?: boolean;
  lanes?: Partial<Record<CollectionLaneId, { enabled?: boolean; intervalMinutes?: number }>>;
}): Promise<CollectionRuntime> {
  return request<CollectionRuntime>('/api/collection/schedule', {
    method: 'PUT',
    body: JSON.stringify(candidate),
  });
}

export function addCollectionCandidate(candidate: {
  url: string;
  title?: string;
  publisher?: string;
  reason?: string;
}): Promise<CollectionCandidate> {
  return request<CollectionCandidate>('/api/collection/candidates', {
    method: 'POST',
    body: JSON.stringify(candidate),
  });
}

export function reviewCollectionCandidate(
  candidateId: string,
  status: CollectionCandidate['status'],
  note = '',
): Promise<CollectionCandidate> {
  return request<CollectionCandidate>(
    `/api/collection/candidates/${encodeURIComponent(candidateId)}/review`,
    {
      method: 'POST',
      body: JSON.stringify({ status, note }),
    },
  );
}

export function getNodeDetail(
  workspaceId: string,
  nodeId: string,
): Promise<NodeDetailPayload> {
  return request<NodeDetailPayload>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/nodes/${encodeURIComponent(nodeId)}/detail`,
  );
}

export function saveWorkspace(
  workspace: WorkbenchWorkspace,
): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>(
    `/api/workbench/workspaces/${encodeURIComponent(workspace.workspace_id)}`,
    { method: 'PUT', body: JSON.stringify(workspace) },
  );
}

export function createWorkspace(name: string): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>('/api/workbench/workspaces', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
}

export function saveDesignBrief(
  workspaceId: string,
  brief: DesignBrief,
): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/brief`,
    { method: 'POST', body: JSON.stringify({ brief }) },
  );
}

export function generateWorkbenchDesign(
  workspaceId: string,
): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/design/run`,
    { method: 'POST', body: '{}' },
  );
}

export function saveDecisionProfile(
  workspaceId: string,
  decisionProfile: DecisionProfile,
): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/decisions`,
    { method: 'POST', body: JSON.stringify({ decision_profile: decisionProfile }) },
  );
}

export function activateConcept(
  workspaceId: string,
  conceptId: string,
): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/active-concept`,
    { method: 'POST', body: JSON.stringify({ concept_id: conceptId }) },
  );
}

export function runNode(
  workspaceId: string,
  nodeId: string,
): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/nodes/${encodeURIComponent(nodeId)}/run`,
    { method: 'POST', body: '{}' },
  );
}

export function duplicateConcept(
  workspaceId: string,
  conceptId: string,
): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/concepts/${encodeURIComponent(conceptId)}/duplicate`,
    { method: 'POST', body: '{}' },
  );
}

export function regenerateConcept(
  workspaceId: string,
  conceptId: string,
): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/concepts/${encodeURIComponent(conceptId)}/regenerate`,
    { method: 'POST', body: '{}' },
  );
}

export function generateMoreConcept(
  workspaceId: string,
  conceptId: string,
): Promise<WorkbenchWorkspace> {
  return request<WorkbenchWorkspace>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/concepts/${encodeURIComponent(conceptId)}/generate-more`,
    { method: 'POST', body: '{}' },
  );
}

export async function getDesignPackage(
  workspaceId: string,
): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(
    `/api/workbench/workspaces/${encodeURIComponent(workspaceId)}/design-package`,
  );
}
