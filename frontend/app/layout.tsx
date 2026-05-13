"use client"
import '../styles/globals.css'
import React, { useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const { setUser } = useAuthStore()

  const checkAuth = async () => {
    try {
      const res = await fetch('/api/auth/me', { credentials: 'include' })
      if (res.ok) {
        const data = await res.json()
        if (data.authenticated) {
          setUser(data.user)
        }
      }
    } catch (e) {
      console.error('Auth check failed', e)
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  return (
    <html lang="en" className="dark h-full">
      <body className="h-full bg-background text-foreground">{children}</body>
    </html>
  )
}
