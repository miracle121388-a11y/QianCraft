import NodeDetail from '../../node-detail';

export default async function NodePage({
  params,
  searchParams,
}: {
  params: Promise<{ nodeId: string }>;
  searchParams: Promise<{ workspace?: string }>;
}) {
  const { nodeId } = await params;
  const { workspace = 'guizhou-miao-demo' } = await searchParams;
  return <NodeDetail nodeId={nodeId} workspaceId={workspace} />;
}
