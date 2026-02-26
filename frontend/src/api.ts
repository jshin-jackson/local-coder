export interface GenerateParams {
  prompt: string
  language: string
  maxTokens: number
  temperature: number
}

export interface GenerateCallbacks {
  onToken: (token: string) => void
  onDone: () => void
  onError: (message: string) => void
}

/**
 * Stream code generation from the backend via Server-Sent Events.
 * Returns an AbortController so the caller can cancel the request.
 */
export function generateCode(
  params: GenerateParams,
  callbacks: GenerateCallbacks,
): AbortController {
  const controller = new AbortController()

  const run = async () => {
    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: params.prompt,
          language: params.language,
          max_tokens: params.maxTokens,
          temperature: params.temperature,
        }),
        signal: controller.signal,
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        callbacks.onError(err.detail ?? 'Generation failed')
        return
      }

      const reader = res.body?.getReader()
      if (!reader) {
        callbacks.onError('No response body')
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const raw = line.slice(5).trim()
            if (!raw) continue
            try {
              const payload = JSON.parse(raw)
              if (payload.token !== undefined) {
                callbacks.onToken(payload.token)
              } else if (payload.done) {
                callbacks.onDone()
                return
              }
            } catch {
              // ignore malformed SSE data lines
            }
          }
        }
      }

      callbacks.onDone()
    } catch (err) {
      if ((err as Error).name === 'AbortError') return
      callbacks.onError((err as Error).message ?? 'Unknown error')
    }
  }

  run()
  return controller
}
