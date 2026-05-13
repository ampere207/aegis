"use client"

import React, { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowLeft, GitBranch, Activity } from 'lucide-react'
import { ReactFlow, Controls, Background, MiniMap } from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import GraphExplorer from '@/components/intelligence/GraphExplorer'
import AnalysisHistoryTimeline from '@/components/intelligence/AnalysisHistoryTimeline'
import PRAnalysisWorkspace from '@/components/intelligence/PRAnalysisWorkspace'

export default function RepoDetailPage() {
  const params = useParams()
  const repoId = Number(params.id)

  const [repoDetails, setRepoDetails] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [analysisProgress, setAnalysisProgress] = useState<any>(null)
  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const res = await fetch(`/api/repos/${repoId}`, { credentials: 'include' })
        if (res.ok) {
          setRepoDetails(await res.json())
        }
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    if (repoId) fetchDetails()
  }, [repoId])

  useEffect(() => {
    if (!repoId) return
    const ws = new WebSocket(`ws://localhost:8000/api/ws/analysis/${repoId}`)
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setAnalysisProgress(data)
      if (data.stage === 'completed' || data.stage === 'failed') {
        setAnalyzing(false)
      }
    }
    return () => ws.close()
  }, [repoId])

  const triggerAnalyze = async () => {
    setAnalyzing(true)
    setAnalysisProgress({ stage: 'started', message: 'Requesting analysis...' })
    try {
      await fetch(`/api/repos/${repoId}/analyze`, { method: 'POST', credentials: 'include' })
    } catch (e) {
      console.error(e)
      setAnalyzing(false)
    }
  }

  if (loading) return <div className="p-8 text-muted-foreground animate-pulse">Initializing workspace...</div>
  if (!repoDetails) return <div className="p-8 text-destructive">Repository context lost.</div>

  return (
    <main className="min-h-screen bg-background text-foreground flex flex-col max-w-7xl mx-auto p-6 space-y-8">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors mb-2">
            <Link href="/dashboard" className="flex items-center gap-1">
              <ArrowLeft className="h-3 w-3" /> Dashboard
            </Link>
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            {repoDetails.full_name}
          </h2>
          <p className="text-muted-foreground text-sm max-w-2xl">{repoDetails.description}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" asChild>
            <a href={repoDetails.html_url} target="_blank" rel="noreferrer">GitHub</a>
          </Button>
          <Button onClick={triggerAnalyze} disabled={analyzing} size="sm" className="shadow-lg shadow-primary/20">
            {analyzing ? 'Analysis in Progress...' : 'Full System Scan'}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="intelligence" className="w-full">
        <TabsList className="grid grid-cols-3 w-full md:w-[400px] mb-8">
          <TabsTrigger value="intelligence">Intelligence</TabsTrigger>
          <TabsTrigger value="pr-security">PR Analysis</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="intelligence" className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="md:col-span-3 space-y-6">
              <Card className="overflow-hidden border-border/40 bg-card/50 backdrop-blur">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg font-bold">Security Knowledge Graph</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <GraphExplorer />
                </CardContent>
              </Card>

              {analysisProgress?.findings && (
                <Card className="border-primary/20 bg-primary/5">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5 text-primary" />
                      AI Architectural Reasoning
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {analysisProgress.findings.map((finding: any, i: number) => (
                      <div key={i} className="p-4 border border-border/50 rounded-xl bg-background/80 hover:border-primary/30 transition-all">
                        <h4 className="font-bold text-sm text-primary mb-2 uppercase tracking-wide">{finding.title}</h4>
                        <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap">{finding.description}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}
            </div>

            <div className="md:col-span-1 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Active Session</CardTitle>
                </CardHeader>
                <CardContent>
                  {analysisProgress ? (
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <div className="h-3 w-3 bg-primary rounded-full animate-ping absolute" />
                          <div className="h-3 w-3 bg-primary rounded-full" />
                        </div>
                        <span className="text-sm font-medium capitalize">{analysisProgress.stage}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{analysisProgress.message}</p>
                    </div>
                  ) : (
                    <div className="text-center py-6">
                      <p className="text-xs text-muted-foreground italic">No active scan session.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
              <AnalysisHistoryTimeline analyses={repoDetails.analyses || []} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="pr-security">
          <PRAnalysisWorkspace repoId={repoId} prNumber={1} />
        </TabsContent>

        <TabsContent value="history">
          <div className="max-w-2xl">
            <AnalysisHistoryTimeline analyses={repoDetails.analyses || []} />
          </div>
        </TabsContent>
      </Tabs>
    </main>
  )
}


