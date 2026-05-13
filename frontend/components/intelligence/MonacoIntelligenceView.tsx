'use client';

import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';

interface Annotation {
  line: number;
  message: string;
  type: 'security' | 'api' | 'auth';
}

interface MonacoIntelligenceViewProps {
  code: string;
  language: string;
  annotations: Annotation[];
}

export default function MonacoIntelligenceView({ code, language, annotations }: MonacoIntelligenceViewProps) {
  const monacoRef = useRef<any>(null);

  function handleEditorDidMount(editor: any, monaco: any) {
    monacoRef.current = monaco;
    
    // Apply decorations
    const decorations = annotations.map(ann => ({
      range: new monaco.Range(ann.line, 1, ann.line, 1),
      options: {
        isWholeLine: true,
        className: ann.type === 'security' ? 'bg-destructive/20' : 'bg-primary/20',
        glyphMarginClassName: 'bg-primary',
        hoverMessage: { value: ann.message },
      },
    }));

    editor.deltaDecorations([], decorations);
  }

  return (
    <div className="h-[500px] w-full border border-border rounded-xl overflow-hidden shadow-lg">
      <Editor
        height="100%"
        defaultLanguage={language}
        defaultValue={code}
        theme="vs-dark"
        onMount={handleEditorDidMount}
        options={{
          readOnly: true,
          minimap: { enabled: false },
          fontSize: 14,
          padding: { top: 20 },
          glyphMargin: true,
        }}
      />
    </div>
  );
}
