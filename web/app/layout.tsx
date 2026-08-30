import type { Metadata } from 'next';
import '@fontsource-variable/noto-sans-sc';
import '@fontsource-variable/noto-serif-sc';
import './globals.css';
import './tonal-focus.css';

const impeccableDirectionContract = `THESIS: Tonal Focus Review uses restrained, functional color blocks to make evidence workspaces legible without becoming a marketing surface.
PALETTE: Shell #E6E2DA; command #D9E1E8; rail/evidence #D7E1DC; canvas #E3E8EB; Inspector #E7DDD4; node #F0EEE9; selected #CBD9E6; primary/focus #345C7D; text #20262C; secondary #626970; rule #C4C8C7.
STORY: Choose a phase, inspect bounded evidence, select or run a node, edit in its contextual Inspector, and open the deep record only when needed.
FIRST VIEWPORT: A 60px mist-blue command bar and 72px gray-green tool rail frame the dominant blue-gray plotting canvas; contextual Dock and warm Inspector appear at its edges while the primary Run control remains top-right.
FORM: User-approved Tonal Focus Review C2 composition, SHA 131cd5bedadd5be42888ace5d946ebaa2d4c3f3dc935e29393fd1127ebf7ffeb; selection changes color, border, and bound content, never node geometry.
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
        <script data-impeccable-contract="131cd5bedadd5be42888ace5d946ebaa2d4c3f3dc935e29393fd1127ebf7ffeb" dangerouslySetInnerHTML={{ __html: impeccableContractScript }} />
        {children}
      </body>
    </html>
  );
}
