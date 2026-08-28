import type { Metadata } from 'next';
import '@fontsource-variable/noto-sans-sc';
import '@fontsource-variable/noto-serif-sc';
import './globals.css';

const impeccableDirectionContract = `THESIS: The node canvas is the instrument; tools open around it only when summoned. QianCraft refuses both the permanent wall of panels and the showcase homepage.
OWN-WORLD: Warm parchment command surfaces, a warm-sand canvas, linen seams, charcoal working text, and one interaction-indigo active state; restrained inset edges, soft containers, one selected elevation.
STORY: Choose a phase, inspect evidence, select or run a node, edit in its contextual inspector, then open the deep record only when needed.
FIRST VIEWPORT: 56px command bar, 64px tool rail, optional 248px evidence dock, dominant node canvas, and 320px selected inspector; Run sits top-right, depth lives behind rail icons and tabs.
FORM: User-pinned Creative Instrument Workbench, grounded direction 3, seed 599c7281; selection moves one node forward while the canvas holds.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance`;

const impeccableContractScript = `document.currentScript?.parentNode?.insertBefore(document.createComment(${JSON.stringify(impeccableDirectionContract)}), document.currentScript);`;

const publicSiteUrl = process.env.NEXT_PUBLIC_QIANCRAFT_SITE_URL
  ?? 'https://qiancraft-studio-2026.zeabur.app';

export const metadata: Metadata = {
  metadataBase: new URL(publicSiteUrl),
  title: 'QianCraft｜文化文创智能工作台',
  description: '把贵州文化证据、四平台市场信号与可编辑概念设计连接成一条空间工作流。',
  openGraph: {
    title: 'QianCraft｜文化文创智能工作台',
    description: '从文化证据与市场信号，到可编辑、可追溯的文创概念。',
    images: [{ url: '/og.png', width: 1731, height: 909, alt: 'QianCraft｜黔艺前策' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'QianCraft｜文化文创智能工作台',
    description: '从文化证据与市场信号，到可编辑、可追溯的文创概念。',
    images: ['/og.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>
        <script data-impeccable-contract="599c7281" dangerouslySetInnerHTML={{ __html: impeccableContractScript }} />
        {children}
      </body>
    </html>
  );
}
