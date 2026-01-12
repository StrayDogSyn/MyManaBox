const OLLAMA_URL = import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434'

export async function* streamChat(
  model: string,
  prompt: string,
  system?: string
): AsyncGenerator<string> {
  const response = await fetch(`${OLLAMA_URL}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, prompt, system, stream: true }),
  })

  const reader = response.body?.getReader()
  if (!reader) throw new Error('No response body')

  const decoder = new TextDecoder()
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const chunk = decoder.decode(value)
    const lines = chunk.split('\n').filter(Boolean)
    for (const line of lines) {
      try {
        const data = JSON.parse(line) as { response?: string }
        if (data.response) yield data.response
      } catch {
        continue
      }
    }
  }
}

export async function checkOllamaConnection(): Promise<boolean> {
  try {
    const response = await fetch(`${OLLAMA_URL}/api/tags`)
    return response.ok
  } catch {
    return false
  }
}
