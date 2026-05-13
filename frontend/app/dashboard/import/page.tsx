"use client"
import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { GithubIcon, Search, Loader2, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

interface GitHubRepo {
  id: number
  owner: string
  name: string
  full_name: string
  html_url: string
  description: string
  visibility: string
}

export default function ImportPage() {
  const [repos, setRepos] = useState<GitHubRepo[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [importing, setImporting] = useState<number | null>(null)
  const router = useRouter()

  const fetchRepos = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/repos/available`, { credentials: 'include' })
      if (res.ok) {
        const data = await res.json()
        setRepos(data)
      } else if (res.status === 401) {
        // Not logged in, redirect to landing
        router.push('/')
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleImport = async (repo: GitHubRepo) => {
    setImporting(repo.id)
    try {
      const res = await fetch(`/api/repos/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(repo),
        credentials: 'include'
      })
      if (res.ok) {
        router.push('/dashboard')
      }
    } catch (e) {
      console.error(e)
    } finally {
      setImporting(null)
    }
  }

  useEffect(() => {
    fetchRepos()
  }, [])

  const filteredRepos = repos.filter(r => 
    r.full_name.toLowerCase().includes(search.toLowerCase()) ||
    (r.description && r.description.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <main className="min-h-screen p-8 max-w-5xl mx-auto space-y-8">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <h2 className="text-3xl font-bold tracking-tight">Import Repositories</h2>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search repositories..."
          className="pl-10 h-12"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          suppressHydrationWarning
        />
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 space-y-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="text-muted-foreground">Fetching your GitHub repositories...</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredRepos.length === 0 ? (
            <div className="text-center py-20 border-2 border-dashed rounded-lg">
              <p className="text-muted-foreground">No repositories found.</p>
            </div>
          ) : (
            filteredRepos.map((repo) => (
              <Card key={repo.id} className="hover:bg-accent/50 transition-colors">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="space-y-1">
                    <CardTitle className="text-lg font-bold flex items-center">
                      <GithubIcon className="mr-2 h-4 w-4" />
                      {repo.full_name}
                    </CardTitle>
                    <CardDescription>{repo.description || 'No description provided.'}</CardDescription>
                  </div>
                  <Button 
                    onClick={() => handleImport(repo)} 
                    disabled={importing === repo.id}
                  >
                    {importing === repo.id ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Importing...
                      </>
                    ) : (
                      'Import'
                    )}
                  </Button>
                </CardHeader>
              </Card>
            ))
          )}
        </div>
      )}
    </main>
  )
}
