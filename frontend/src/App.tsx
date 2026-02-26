import { useCallback, useRef, useState } from 'react'
import { Copy, Check, Trash2, Code2 } from 'lucide-react'
import { Editor } from './components/Editor'
import { PromptPanel } from './components/PromptPanel'
import { Sidebar, type HistoryEntry } from './components/Sidebar'
import { StatusBar } from './components/StatusBar'
import { generateCode } from './api'

let historyCounter = 0

function genId() {
  return `entry-${++historyCounter}-${Date.now()}`
}

export default function App() {
  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const abortRef = useRef<AbortController | null>(null)
  const currentPromptRef = useRef('')

  const handleGenerate = useCallback(
    (params: { prompt: string; language: string; maxTokens: number; temperature: number }) => {
      setError(null)
      setCode('')
      setIsGenerating(true)
      currentPromptRef.current = params.prompt

      let accumulated = ''

      abortRef.current = generateCode(params, {
        onToken: token => {
          accumulated += token
          setCode(accumulated)
        },
        onDone: () => {
          setIsGenerating(false)
          if (accumulated.trim()) {
            setHistory(prev => [
              ...prev,
              {
                id: genId(),
                prompt: params.prompt,
                language: params.language,
                code: accumulated,
                timestamp: Date.now(),
              },
            ])
          }
        },
        onError: msg => {
          setIsGenerating(false)
          setError(msg)
        },
      })
    },
    [],
  )

  const handleStop = useCallback(() => {
    abortRef.current?.abort()
    setIsGenerating(false)
  }, [])

  const handleCopy = useCallback(async () => {
    if (!code) return
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [code])

  const handleSelectHistory = useCallback((entry: HistoryEntry) => {
    setCode(entry.code)
    setLanguage(entry.language)
    setError(null)
  }, [])

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg-base)',
        overflow: 'hidden',
      }}
    >
      {/* Title bar */}
      <div
        style={{
          height: '40px',
          background: 'var(--bg-sidebar)',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 16px',
          gap: '8px',
          flexShrink: 0,
        }}
      >
        <Code2 size={16} color="var(--accent)" />
        <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text-primary)' }}>
          Local Coder
        </span>
        <span
          style={{
            fontSize: '11px',
            color: 'var(--text-muted)',
            background: 'var(--bg-input)',
            padding: '2px 6px',
            borderRadius: '4px',
            border: '1px solid var(--border)',
          }}
        >
          gpt-oss-20b-Coding-Distill
        </span>
      </div>

      {/* Main layout */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden', minHeight: 0 }}>
        {/* Sidebar */}
        <Sidebar
          history={history}
          onSelect={handleSelectHistory}
          onClear={() => setHistory([])}
        />

        {/* Editor column */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
          {/* Editor toolbar */}
          <div
            style={{
              height: '36px',
              background: 'var(--bg-panel)',
              borderBottom: '1px solid var(--border)',
              display: 'flex',
              alignItems: 'center',
              padding: '0 12px',
              gap: '6px',
              flexShrink: 0,
            }}
          >
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)', flex: 1 }}>
              {isGenerating ? 'Generating...' : code ? 'Generated code' : 'Output'}
            </span>

            {code && (
              <>
                <button
                  onClick={() => setCode('')}
                  title="Clear editor"
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    padding: '4px 6px',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '12px',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.color = 'var(--text-primary)')}
                  onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
                >
                  <Trash2 size={13} />
                  Clear
                </button>

                <button
                  onClick={handleCopy}
                  style={{
                    background: copied ? 'var(--success)' : 'var(--bg-input)',
                    border: '1px solid var(--border)',
                    borderRadius: '5px',
                    color: copied ? '#fff' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    padding: '4px 10px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '12px',
                    transition: 'background 0.15s, color 0.15s',
                  }}
                >
                  {copied ? <Check size={13} /> : <Copy size={13} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </>
            )}
          </div>

          {/* Error banner */}
          {error && (
            <div
              style={{
                background: '#3d1212',
                borderBottom: '1px solid var(--error)',
                padding: '8px 16px',
                fontSize: '12px',
                color: '#f85149',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexShrink: 0,
              }}
            >
              <span>Error: {error}</span>
              <button
                onClick={() => setError(null)}
                style={{ background: 'none', border: 'none', color: '#f85149', cursor: 'pointer', fontSize: '16px', lineHeight: 1 }}
              >
                ×
              </button>
            </div>
          )}

          {/* Monaco Editor */}
          <Editor value={code} language={language} onChange={setCode} />

          {/* Prompt panel */}
          <PromptPanel
            language={language}
            onLanguageChange={setLanguage}
            isGenerating={isGenerating}
            onGenerate={handleGenerate}
            onStop={handleStop}
          />
        </div>
      </div>

      {/* Status bar */}
      <StatusBar language={language} isGenerating={isGenerating} />
    </div>
  )
}
