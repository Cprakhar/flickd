import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Flickd',
  description: 'Discover and shop fashion through short, vibe-led videos with Flickd.',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
