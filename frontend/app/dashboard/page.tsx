"use client"
import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useRepoStore } from '@/store/repoStore'

export default function Dashboard() {
  const { importedRepos, statuses, setImportedRepos, updateStatus } = useRepoStore()
  const [loading, setLoading] = useState(false)

  const fetchImported = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/repos/imported`, { credentials: 'include' })
      if (res.ok) {
        const repos = await res.json()
        setImportedRepos(repos)
        repos.forEach(fetchStatus)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const fetchStatus = async (repo: any) => {
    try {
      const res = await fetch(`/api/repos/${repo.id}/status`, { credentials: 'include' })
      if (res.ok) {
        const status = await res.json()
        updateStatus(repo.id, status)
      }
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    fetchImported()
  }, [])

  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <Button asChild>
          <Link href="/dashboard/import">Import Repositories</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Imported Repositories</CardTitle>
          <CardDescription>View and manage the repositories you are tracking.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading && importedRepos.length === 0 ? (
            <div className="py-6 text-center text-muted-foreground">Loading repositories...</div>
          ) : importedRepos.length === 0 ? (
            <div className="text-center py-10 border-2 border-dashed rounded-lg">
              <h3 className="text-lg font-semibold mb-2">No repositories imported yet</h3>
              <p className="text-muted-foreground mb-4">
                Import a repository to start tracking alerts and analysis.
              </p>
              <Button variant="outline" asChild>
                <Link href="/dashboard/import">Import a repository</Link>
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Repository</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Analysis Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {importedRepos.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium">
                      <Link href={`/dashboard/repo/${r.id}`} className="text-primary font-semibold hover:underline">
                        {r.full_name}
                      </Link>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {r.description || 'No description provided.'}
                    </TableCell>
                    <TableCell>
                      {statuses[r.id]?.analyses[0]?.status ? (
                        <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                          statuses[r.id].analyses[0].status === 'completed' ? 'bg-green-500/10 text-green-500' :
                          statuses[r.id].analyses[0].status === 'running' ? 'bg-yellow-500/10 text-yellow-500' :
                          statuses[r.id].analyses[0].status === 'failed' ? 'bg-destructive/10 text-destructive' :
                          'bg-muted text-muted-foreground'
                        }`}>
                          {statuses[r.id].analyses[0].status.toUpperCase()}
                        </span>
                      ) : (
                        <span className="text-muted-foreground text-sm">N/A</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </main>
  )
}

