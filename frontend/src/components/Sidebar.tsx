import { Clock, Code2, Trash2 } from 'lucide-react'

export interface HistoryEntry {
  id: string
  prompt: string
  language: string
  code: string
  timestamp: number
}

interface SidebarProps {
  history: HistoryEntry[]
  onSelect: (entry: HistoryEntry) => void
  onClear: () => void
}

const LANGUAGE_ICONS: Record<string, string> = {
  python: 'py',
  javascript: 'js',
  typescript: 'ts',
  java: 'java',
  go: 'go',
  rust: 'rs',
  cpp: 'cpp',
  c: 'c',
  shell: 'sh',
  sql: 'sql',
  html: 'html',
  css: 'css',
  auto: '?',
}

function formatTime(ts: number) {
  const d = new Date(ts)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function Sidebar({ history, onSelect, onClear }: SidebarProps) {
  return (
    <div
      style={{
        width: '220px',
        minWidth: '220px',
        background: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '12px 12px 8px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)' }}>
          <Clock size={13} />
          History
        </div>
        {history.length > 0 && (
          <button
            onClick={onClear}
            title="Clear history"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '2px',
              borderRadius: '3px',
              display: 'flex',
              alignItems: 'center',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = 'var(--error)')}
            onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
          >
            <Trash2 size={13} />
          </button>
        )}
      </div>

      {/* List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '4px 0' }}>
        {history.length === 0 ? (
          <div
            style={{
              padding: '24px 12px',
              color: 'var(--text-muted)',
              fontSize: '12px',
              textAlign: 'center',
            }}
          >
            <Code2 size={24} style={{ margin: '0 auto 8px', display: 'block', opacity: 0.4 }} />
            No generations yet
          </div>
        ) : (
          [...history].reverse().map(entry => (
            <button
              key={entry.id}
              onClick={() => onSelect(entry)}
              style={{
                width: '100%',
                textAlign: 'left',
                background: 'none',
                border: 'none',
                padding: '8px 12px',
                cursor: 'pointer',
                color: 'var(--text-primary)',
                borderBottom: '1px solid transparent',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'var(--bg-input)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'none')}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
                <span
                  style={{
                    fontSize: '10px',
                    fontFamily: 'monospace',
                    background: 'var(--bg-input)',
                    padding: '1px 5px',
                    borderRadius: '3px',
                    color: 'var(--accent)',
                    border: '1px solid var(--border)',
                    flexShrink: 0,
                  }}
                >
                  {LANGUAGE_ICONS[entry.language] ?? entry.language}
                </span>
                <span
                  style={{
                    fontSize: '11px',
                    color: 'var(--text-secondary)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    flex: 1,
                  }}
                >
                  {formatTime(entry.timestamp)}
                </span>
              </div>
              <div
                style={{
                  fontSize: '12px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  color: 'var(--text-secondary)',
                }}
              >
                {entry.prompt}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  )
}
