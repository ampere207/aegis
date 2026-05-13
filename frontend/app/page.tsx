"use client"
import React from 'react'
import Link from 'next/link'
import { Shield, Github as GithubIcon, ChevronRight, Activity, GitBranch, Terminal } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

export default function Home() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 max-w-screen-2xl items-center mx-auto px-4">
          <div className="flex items-center space-x-2 mr-4">
            <Shield className="h-6 w-6 text-primary" />
            <span className="font-bold text-xl tracking-tight">Aegis</span>
          </div>
          <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
            <nav className="flex items-center">
              {isAuthenticated ? (
                <Link
                  href="/dashboard"
                  className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4"
                >
                  Go to Dashboard
                </Link>
              ) : (
                <a
                  href="/api/auth/login"
                  className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4"
                >
                  <GithubIcon className="mr-2 h-4 w-4" />
                  Sign In with GitHub
                </a>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 w-full mx-auto px-4 max-w-7xl">
        <section className="space-y-6 pb-8 pt-16 md:pb-12 md:pt-24 lg:pb-32 lg:pt-32 text-center lg:text-left">
          <div className="container flex flex-col lg:flex-row items-center justify-center gap-12 mx-auto">
            <div className="flex max-w-[64rem] flex-col items-center gap-6 lg:items-start">
              <h1 className="font-bold text-4xl sm:text-5xl md:text-6xl lg:text-7xl tracking-tighter">
                Semantic AppSec Platform <br className="hidden sm:inline" />
                for <span className="text-primary text-sky-500">Modern Codebases.</span>
              </h1>
              <p className="max-w-[42rem] leading-normal text-muted-foreground sm:text-xl sm:leading-8">
                Aegis is an AI-native security intelligence platform that understands your distributed architecture. We detect complex privilege escalations, exploit chains, and trust boundary violations—not just regex matches.
              </p>
              <div className="space-x-4">
                <Link
                  href={isAuthenticated ? "/dashboard" : "/api/auth/login"}
                  className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8"
                >
                  {isAuthenticated ? "Go to Dashboard" : "Get Started"} <ChevronRight className="ml-2 h-4 w-4" />
                </Link>
              </div>
            </div>

            {/* Code / Visual Placeholder */}
            <div className="w-full max-w-[600px] border border-border/50 rounded-xl shadow-2xl bg-zinc-950/50 backdrop-blur-sm overflow-hidden flex flex-col">
              <div className="h-10 border-b border-border/50 bg-zinc-900/80 flex items-center px-4 space-x-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
              </div>
              <div className="p-6 font-mono text-sm min-h-[300px] text-left text-slate-300">
                <div className="flex items-center space-x-2 text-slate-400 mb-2">
                  <Terminal className="h-4 w-4" /> <span>aegis analyze --repo octocat/backend</span>
                </div>
                <div className="space-y-1 mt-4">
                  <p><span className="text-green-400">✔</span> Cloned repository</p>
                  <p><span className="text-green-400">✔</span> Extracted architecture graph to Neo4j</p>
                  <p><span className="text-green-400">✔</span> Computed AST semantics & Vectors</p>
                  <p className="animate-pulse">Building exploit chains...</p>
                </div>
                <div className="mt-8 border-l-2 border-red-500 pl-4 bg-red-500/10 py-2">
                  <p className="text-red-400 font-semibold">[HIGH] Privilege Escalation Detected</p>
                  <p className="text-slate-400 text-xs mt-1">Cross-service trust boundary violation between Auth Service and Billing API.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Highlights */}
        <section className="container mx-auto space-y-12 py-16 md:py-24 max-w-6xl">
          <div className="mx-auto flex max-w-[58rem] flex-col items-center space-y-4 text-center">
            <h2 className="font-bold text-3xl leading-[1.1] sm:text-3xl md:text-5xl">Beyond Static Analysis</h2>
            <p className="max-w-[85%] leading-normal text-muted-foreground sm:text-lg sm:leading-7">
              Aegis is built around comprehensive architectural visibility. We map out everything.
            </p>
          </div>
          <div className="mx-auto grid justify-center gap-4 sm:grid-cols-2 md:max-w-[64rem] md:grid-cols-3">
            <div className="relative overflow-hidden rounded-lg border bg-background p-6">
              <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                <GitBranch className="h-10 w-10 text-primary mb-4" />
                <div className="space-y-2">
                  <h3 className="font-bold text-xl">Graph-Based</h3>
                  <p className="text-sm text-muted-foreground">Code is parsed into graph models mapping caller relationships and untrusted sinks.</p>
                </div>
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background p-6">
              <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                <Activity className="h-10 w-10 text-primary mb-4" />
                <div className="space-y-2">
                  <h3 className="font-bold text-xl">Semantic Analysis</h3>
                  <p className="text-sm text-muted-foreground">Vector embeddings capture the true meaning and behavior of distributed microservices.</p>
                </div>
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background p-6">
              <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                <Shield className="h-10 w-10 text-primary mb-4" />
                <div className="space-y-2">
                  <h3 className="font-bold text-xl">Exploit Chains</h3>
                  <p className="text-sm text-muted-foreground">By combining Graph + AI, we reason about complex multi-step exploits accurately.</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row mx-auto px-4 max-w-7xl">
          <div className="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
            <Shield className="h-5 w-5" />
            <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
              Aegis Security Intelligence Platform. The foundation mapped for Phase 1.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
