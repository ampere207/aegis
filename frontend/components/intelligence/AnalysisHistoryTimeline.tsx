'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { History, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface AnalysisRecord {
  id: number;
  status: string;
  analysis_type: string;
  created_at: string;
}

interface AnalysisHistoryTimelineProps {
  analyses: AnalysisRecord[];
}

export default function AnalysisHistoryTimeline({ analyses }: AnalysisHistoryTimelineProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <History className="h-4 w-4" /> Analysis History
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative space-y-4">
          <div className="absolute left-4 top-2 bottom-2 w-px bg-border" />
          
          {analyses.map((analysis, i) => (
            <div key={i} className="relative pl-10">
              <div className="absolute left-[0.95rem] top-1 h-3 w-3 rounded-full bg-background border-2 border-primary z-10" />
              
              <div className="flex flex-col space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    {analysis.analysis_type || 'FULL'} SCAN
                  </span>
                  <Badge variant={analysis.status === 'completed' ? 'outline' : 'secondary'} className="text-[10px] h-4">
                    {analysis.status.toUpperCase()}
                  </Badge>
                </div>
                
                <div className="flex items-center gap-2 text-xs">
                  <Clock className="h-3 w-3 text-muted-foreground" />
                  <span className="text-muted-foreground">
                    {formatDistanceToNow(new Date(analysis.created_at))} ago
                  </span>
                </div>
                
                <p className="text-[10px] text-muted-foreground font-mono">
                  ID: {analysis.id.toString().slice(0, 8)}...
                </p>
              </div>
            </div>
          ))}

          {analyses.length === 0 && (
            <div className="text-center py-8 text-xs text-muted-foreground italic">
              No analysis history found.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
