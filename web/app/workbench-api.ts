import type {
  DesignBrief,
  DecisionProfile,
  NodeDetailPayload,
  WorkbenchBootstrap,
  WorkbenchWorkspace,
} from './workbench-model';

export const API_BASE = (
  process.env.NEXT_PUBLIC_QIANCRAFT_API_URL ?? 'http://127.0.0.1:8787'
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

export async function getDesignPackage(): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>('/api/design');
}
