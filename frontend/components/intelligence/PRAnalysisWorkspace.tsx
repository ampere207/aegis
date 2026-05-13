'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { GitPullRequest, ShieldAlert, FileCode, CheckCircle2 } from 'lucide-react';

interface PRFinding {
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: string;
}

interface PRAnalysisWorkspaceProps {
  repoId: number;
  prNumber: number;
}

export default function PRAnalysisWorkspace({ repoId, prNumber }: PRAnalysisWorkspaceProps) {
  const [analyzing, setAnalyzing] = useState(false);
  const [findings, setFindings] = useState<PRFinding[]>([]);
  const [impactedFiles, setImpactedFiles] = useState<string[]>([]);

  const startAnalysis = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch(`/api/v1/repos/${repoId}/pr/${prNumber}/analyze`, { method: 'POST' });
      if (res.ok) {
        // In a real app, we'd listen to the WebSocket here
        // For demonstration, we'll simulate the findings
        setTimeout(() => {
          setFindings([
            {
              title: 'Architectural Trust Boundary Modification',
              description: 'This PR modifies core auth middleware. Direct privilege propagation detected into internal services.',
              severity: 'high',
              type: 'trust_boundary'
            }
          ]);
          setImpactedFiles(['app/middleware/auth.py', 'app/services/internal.py']);
          setAnalyzing(false);
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to trigger PR analysis', error);
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-xl font-bold flex items-center gap-2">
              <GitPullRequest className="h-5 w-5 text-primary" />
              PR Security Review: #{prNumber}
            </CardTitle>
            <CardDescription>Analyze architectural security impact of this change</CardDescription>
          </div>
          <Button 
            onClick={startAnalysis} 
            disabled={analyzing}
            className="bg-primary hover:bg-primary/90"
          >
            {analyzing ? 'Analyzing Architecture...' : 'Analyze PR Impact'}
          </Button>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <FileCode className="h-4 w-4" /> Impacted Files
            </CardTitle>
          </CardHeader>
          <CardContent>
            {impactedFiles.length > 0 ? (
              <div className="space-y-2">
                {impactedFiles.map((file, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 rounded bg-muted/50 text-xs font-mono">
                    <span className="text-primary">M</span> {file}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-xs text-muted-foreground italic">No architectural files detected in diff.</div>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-primary" /> Security Implications
            </CardTitle>
          </CardHeader>
          <CardContent>
            {findings.length > 0 ? (
              <div className="space-y-4">
                {findings.map((finding, i) => (
                  <div key={i} className="p-4 rounded-lg border border-border bg-card hover:border-primary/30 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-sm">{finding.title}</h4>
                      <Badge variant={finding.severity === 'high' ? 'destructive' : 'secondary'}>
                        {finding.severity.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {finding.description}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                {analyzing ? (
                  <div className="animate-pulse space-y-2">
                    <div className="h-4 w-48 bg-muted rounded"></div>
                    <div className="h-3 w-32 bg-muted rounded"></div>
                  </div>
                ) : (
                  <>
                    <CheckCircle2 className="h-12 w-12 text-muted mb-4 opacity-20" />
                    <p className="text-sm text-muted-foreground">Trigger analysis to view architectural impact.</p>
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
