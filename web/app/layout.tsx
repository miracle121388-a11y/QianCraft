import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL('http://localhost:3000'),
  title: 'QianCraft｜黔艺前策',
  description: '从贵州非遗文化证据与市场信号，到可制造的概念设计。',
  openGraph: {
    title: 'QianCraft｜黔艺前策',
    description: '从文化证据与市场信号，到可制造的概念设计。',
    images: [{ url: '/og.png', width: 1731, height: 909, alt: 'QianCraft｜黔艺前策' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'QianCraft｜黔艺前策',
    description: '从文化证据与市场信号，到可制造的概念设计。',
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
      <body>{children}</body>
    </html>
  );
}
