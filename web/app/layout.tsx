import type { Metadata } from 'next';
import '@fontsource-variable/noto-sans-sc';
import '@fontsource-variable/noto-serif-sc';
import './globals.css';
import './tonal-focus.css';
import './studio.css';

const impeccableDirectionContract = `THESIS: QianCraft is a result-first operating tool: two living evidence libraries continuously feed daily, inspectable product designs; the workflow appears only when a result needs intervention.
PALETTE: Shell #E6E2DA; command #D9E1E8; rail/evidence #D7E1DC; canvas #E3E8EB; Inspector #E7DDD4; node #F0EEE9; selected #CBD9E6; primary/focus #345C7D; text #20262C; secondary #626970; rule #C4C8C7.
STORY: Verify the culture and form libraries, review today's highest-scoring designs, open one result to inspect provenance, then edit its content, form, copy or visual stage only when needed.
FIRST VIEWPORT: A labeled 224px navigation rail and compact command bar expose actual library counts, today's generated designs, automation status and a direct manual-combination action; no workflow canvas competes with the results.
FORM: Result-first desktop tool composition for QianCraft 0.10.0; the existing Tonal Focus palette remains functional and the legacy spatial workbench survives at /workflow as an advanced surface.
FINISH: no fallback facts, fake scores or placeholder success; every count, source, score, design byte, version and scheduler state comes from the API and stays inspectable`;

const impeccableContractScript = `document.currentScript?.parentNode?.insertBefore(document.createComment(${JSON.stringify(impeccableDirectionContract)}), document.currentScript);`;

const publicSiteUrl = process.env.NEXT_PUBLIC_QIANCRAFT_SITE_URL
  ?? 'https://qiancraft-studio-2026.zeabur.app';

export const metadata: Metadata = {
  metadataBase: new URL(publicSiteUrl),
  title: 'QianCraft｜文化 × 形态自动设计工具',
  description: '持续维护在地文化与产品形态两座知识库，每日自动生成可追溯、可编辑的文创设计。',
  openGraph: {
    title: 'QianCraft｜文化 × 形态自动设计工具',
    description: '从两座真实知识库到每日可编辑的文创产品设计。',
    images: [{ url: '/og.png', width: 1731, height: 909, alt: 'QianCraft｜黔艺前策' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'QianCraft｜文化 × 形态自动设计工具',
    description: '从两座真实知识库到每日可编辑的文创产品设计。',
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
        <script data-impeccable-contract="dual-library-result-first-0.10.0" dangerouslySetInnerHTML={{ __html: impeccableContractScript }} />
        {children}
      </body>
    </html>
  );
}
