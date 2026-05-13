import '../styles/globals.css'
import React from 'react'

export const metadata = {
  title: 'Aegis',
  description: 'Aegis — AI-native AppSec platform',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark h-full">
      <body className="h-full">{children}</body>
    </html>
  )
}
