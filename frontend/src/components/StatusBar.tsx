import { useEffect, useState } from 'react'
import { Circle, Loader2 } from 'lucide-react'

interface ModelStatus {
  loaded: boolean
  model_path: string | null
  error: string | null
}

interface StatusBarProps {
  language: string
  isGenerating: boolean
}

export function StatusBar({ language, isGenerating }: StatusBarProps) {
  const [status, setStatus] = useState<ModelStatus | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch('/api/model/status')
        if (res.ok) setStatus(await res.json())
      } catch {
        setStatus({ loaded: false, model_path: null, error: 'Backend unreachable' })
      } finally {
        setChecking(false)
      }
    }
    check()
    const interval = setInterval(check, 10000)
    return () => clearInterval(interval)
  }, [])

  const modelName = status?.model_path
    ? status.model_path.split('/').pop()
    : null

  return (
    <div
      style={{
        height: '24px',
        background: '#1f6feb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 12px',
        fontSize: '11px',
        color: '#ffffff',
        flexShrink: 0,
        userSelect: 'none',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Model status indicator */}
        {checking ? (
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Loader2 size={10} style={{ animation: 'spin 1s linear infinite' }} />
            Checking model...
          </span>
        ) : status?.loaded ? (
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Circle size={8} fill="#3fb950" color="#3fb950" />
            {modelName ?? 'Model loaded'}
          </span>
        ) : (
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#f85149' }}>
            <Circle size={8} fill="#f85149" color="#f85149" />
            {status?.error ?? 'Model not loaded'}
          </span>
        )}

        {isGenerating && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#d29922' }}>
            <Loader2 size={10} style={{ animation: 'spin 1s linear infinite' }} />
            Generating...
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', opacity: 0.85 }}>
        <span>Local Coder</span>
        <span>{language}</span>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}
