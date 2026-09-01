import StudioApp from '../../../studio-app';

export default async function DesignEditPage({ params }: { params: Promise<{ designId: string }> }) {
  const { designId } = await params;
  return <StudioApp view="edit" designId={designId} />;
}
