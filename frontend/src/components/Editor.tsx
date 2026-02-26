import MonacoEditor from '@monaco-editor/react'

interface EditorProps {
  value: string
  language: string
  onChange: (value: string) => void
}

const MONACO_LANGUAGE_MAP: Record<string, string> = {
  python: 'python',
  javascript: 'javascript',
  typescript: 'typescript',
  java: 'java',
  go: 'go',
  rust: 'rust',
  cpp: 'cpp',
  c: 'c',
  shell: 'shell',
  sql: 'sql',
  html: 'html',
  css: 'css',
  auto: 'plaintext',
}

export function Editor({ value, language, onChange }: EditorProps) {
  return (
    <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
      <MonacoEditor
        height="100%"
        language={MONACO_LANGUAGE_MAP[language] ?? 'plaintext'}
        value={value}
        onChange={v => onChange(v ?? '')}
        theme="vs-dark"
        options={{
          fontSize: 14,
          fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", Consolas, monospace',
          fontLigatures: true,
          lineNumbers: 'on',
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          wordWrap: 'on',
          automaticLayout: true,
          padding: { top: 16, bottom: 16 },
          smoothScrolling: true,
          cursorBlinking: 'smooth',
          renderLineHighlight: 'gutter',
          bracketPairColorization: { enabled: true },
          guides: {
            bracketPairs: true,
            indentation: true,
          },
        }}
      />
    </div>
  )
}
