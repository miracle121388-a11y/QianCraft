import type { Metadata } from 'next';
import '@fontsource-variable/noto-sans-sc';
import '@fontsource-variable/noto-serif-sc';
import './globals.css';

const impeccableDirectionContract = `THESIS: The node canvas is a precision instrument, never a parchment moodboard or a showcase homepage.
OWN-WORLD: Cool white working planes, soft-gray depth fields, graphite type, black selected states, hairline dividers, compact radii, and no chromatic interface accents.
STORY: Choose a phase, inspect bounded evidence, select or run a node, edit in its contextual inspector, and open the deep record only when needed.
FIRST VIEWPORT: A 60px white command bar and 56px gray tool rail frame the dominant plotting canvas; contextual Dock and Inspector appear at its edges while the black Run control remains top-right.
FORM: User-pinned Monochrome Precision Instrument, grounded direction 3, seed a403e052; selection changes contrast, never node geometry.
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
        <script data-impeccable-contract="a403e052" dangerouslySetInnerHTML={{ __html: impeccableContractScript }} />
        {children}
      </body>
    </html>
  );
}
