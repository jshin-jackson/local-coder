import { useState, useRef } from 'react'
import { Send, Square, Sliders, ChevronDown } from 'lucide-react'

const LANGUAGES = [
  { value: 'auto', label: 'Auto' },
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'shell', label: 'Shell' },
  { value: 'sql', label: 'SQL' },
  { value: 'html', label: 'HTML' },
  { value: 'css', label: 'CSS' },
]

interface PromptPanelProps {
  language: string
  onLanguageChange: (lang: string) => void
  isGenerating: boolean
  onGenerate: (params: {
    prompt: string
    language: string
    maxTokens: number
    temperature: number
  }) => void
  onStop: () => void
}

const selectStyle: React.CSSProperties = {
  background: 'var(--bg-input)',
  border: '1px solid var(--border)',
  borderRadius: '6px',
  color: 'var(--text-primary)',
  padding: '5px 28px 5px 10px',
  fontSize: '13px',
  cursor: 'pointer',
  outline: 'none',
  appearance: 'none',
  WebkitAppearance: 'none',
}

export function PromptPanel({
  language,
  onLanguageChange,
  isGenerating,
  onGenerate,
  onStop,
}: PromptPanelProps) {
  const [prompt, setPrompt] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [maxTokens, setMaxTokens] = useState(1024)
  const [temperature, setTemperature] = useState(0.2)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const canGenerate = prompt.trim().length > 0 && !isGenerating

  const handleSubmit = () => {
    if (!canGenerate) return
    onGenerate({ prompt: prompt.trim(), language, maxTokens, temperature })
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div
      style={{
        background: 'var(--bg-panel)',
        borderTop: '1px solid var(--border)',
        padding: '12px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        flexShrink: 0,
      }}
    >
      {/* Top row: language + settings toggle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {/* Language selector */}
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          <select
            value={language}
            onChange={e => onLanguageChange(e.target.value)}
            style={selectStyle}
          >
            {LANGUAGES.map(l => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
          <ChevronDown
            size={13}
            style={{ position: 'absolute', right: '8px', pointerEvents: 'none', color: 'var(--text-secondary)' }}
          />
        </div>

        {/* Settings toggle */}
        <button
          onClick={() => setShowSettings(s => !s)}
          style={{
            background: showSettings ? 'var(--bg-input)' : 'none',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            color: showSettings ? 'var(--accent)' : 'var(--text-secondary)',
            padding: '5px 8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '12px',
          }}
        >
          <Sliders size={13} />
          Settings
        </button>

        <div style={{ flex: 1 }} />

        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>⌘↵ to generate</span>
      </div>

      {/* Settings panel */}
      {showSettings && (
        <div
          style={{
            background: 'var(--bg-input)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            padding: '12px 16px',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
          }}
        >
          <label style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Max Tokens: {maxTokens}
            </span>
            <input
              type="range"
              min={64}
              max={4096}
              step={64}
              value={maxTokens}
              onChange={e => setMaxTokens(Number(e.target.value))}
              style={{ accentColor: 'var(--accent)', cursor: 'pointer' }}
            />
          </label>

          <label style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Temperature: {temperature.toFixed(2)}
            </span>
            <input
              type="range"
              min={0}
              max={2}
              step={0.05}
              value={temperature}
              onChange={e => setTemperature(Number(e.target.value))}
              style={{ accentColor: 'var(--accent)', cursor: 'pointer' }}
            />
          </label>
        </div>
      )}

      {/* Textarea + Send */}
      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
        <textarea
          ref={textareaRef}
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe the code you want to generate..."
          rows={3}
          style={{
            flex: 1,
            background: 'var(--bg-input)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            color: 'var(--text-primary)',
            padding: '10px 12px',
            fontSize: '13px',
            resize: 'vertical',
            outline: 'none',
            fontFamily: 'inherit',
            lineHeight: '1.5',
            transition: 'border-color 0.15s',
          }}
          onFocus={e => (e.currentTarget.style.borderColor = 'var(--accent)')}
          onBlur={e => (e.currentTarget.style.borderColor = 'var(--border)')}
          disabled={isGenerating}
        />

        <button
          onClick={isGenerating ? onStop : handleSubmit}
          disabled={!isGenerating && !canGenerate}
          style={{
            background: isGenerating ? 'var(--error)' : canGenerate ? 'var(--accent)' : 'var(--bg-input)',
            border: 'none',
            borderRadius: '8px',
            color: canGenerate || isGenerating ? '#fff' : 'var(--text-muted)',
            padding: '10px 18px',
            cursor: canGenerate || isGenerating ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            fontWeight: 600,
            transition: 'background 0.15s',
            height: '72px',
            flexShrink: 0,
          }}
        >
          {isGenerating ? (
            <>
              <Square size={14} fill="currentColor" />
              Stop
            </>
          ) : (
            <>
              <Send size={14} />
              Generate
            </>
          )}
        </button>
      </div>
    </div>
  )
}
