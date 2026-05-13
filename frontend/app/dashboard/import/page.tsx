"use client"
import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'

type Repo = {
  id: number
  owner: string
  name: string
  full_name: string
  html_url: string
  clone_url?: string
  description?: string
  visibility?: string
}

export default function ImportPage() {
  const [availableRepos, setAvailableRepos] = useState<Repo[]>([])
  const [importedRepos, setImportedRepos] = useState<Repo[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  const fetchAvailable = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/repos/available?q=${searchTerm}`, { credentials: 'include' })
      if (res.ok) {
        setAvailableRepos(await res.json())
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const fetchImported = async () => {
    try {
      const res = await fetch(`/api/repos/imported`, { credentials: 'include' })
      if (res.ok) {
        setImportedRepos(await res.json())
      }
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    fetchAvailable()
    fetchImported()
  }, [searchTerm])

  const handleImport = async (repo: Repo) => {
    try {
      const res = await fetch('/api/repos/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(repo),
        credentials: 'include',
      })
      if (res.ok) {
        // Refresh imported list
        fetchImported()
      }
    } catch (e) {
      console.error(e)
    }
  }

  const isImported = (fullName: string) => importedRepos.some(r => r.full_name === fullName)

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Import Repositories</h1>
          <p className="text-muted-foreground">Select repositories to import from your GitHub account.</p>
        </div>

        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search repositories..."
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Available Repositories</CardTitle>
              <CardDescription>Repositories you have access to on GitHub.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {loading ? (
                <div className="text-sm text-muted-foreground">Loading...</div>
              ) : availableRepos.length === 0 ? (
                <div className="text-sm text-muted-foreground">No repositories found.</div>
              ) : (
                availableRepos.map((repo) => (
                  <div key={repo.id} className="flex justify-between items-center p-3 border rounded-md">
                    <div>
                      <a href={repo.html_url} target="_blank" rel="noreferrer" className="font-semibold text-primary hover:underline">
                        {repo.full_name}
                      </a>
                      <p className="text-xs text-muted-foreground line-clamp-1 mt-1">{repo.description || 'No description'}</p>
                    </div>
                    <Button
                      size="sm"
                      variant={isImported(repo.full_name) ? "secondary" : "default"}
                      onClick={() => handleImport(repo)}
                      disabled={isImported(repo.full_name)}
                    >
                      {isImported(repo.full_name) ? 'Imported' : 'Import'}
                    </Button>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Currently Tracking</CardTitle>
              <CardDescription>Repositories already imported into Aegis.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {importedRepos.length === 0 ? (
                <div className="text-sm text-muted-foreground">No repositories imported yet.</div>
              ) : (
                importedRepos.map((repo) => (
                  <div key={repo.id} className="p-3 border rounded-md bg-muted/40">
                    <a href={repo.html_url} target="_blank" rel="noreferrer" className="font-semibold text-primary hover:underline">
                      {repo.full_name}
                    </a>
                    <p className="text-xs text-muted-foreground line-clamp-1 mt-1">{repo.description || 'No description'}</p>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  )
}
