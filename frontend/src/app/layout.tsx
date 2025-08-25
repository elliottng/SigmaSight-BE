import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SigmaSight GPT Agent',
  description: 'Portfolio analysis with GPT Agent',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}