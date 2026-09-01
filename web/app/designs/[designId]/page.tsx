import StudioApp from '../../studio-app';

export default async function DesignPage({ params }: { params: Promise<{ designId: string }> }) {
  const { designId } = await params;
  return <StudioApp view="design" designId={designId} />;
}
