import { useQuery, useMutation } from '@tanstack/react-query'
import { getAgents, chatWithAgent } from '../client'
import type { OllamaModel } from '@/types/api'

const OLLAMA_URL = import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434'

export const agentKeys = {
  all: ['agents'] as const,
  lists: () => [...agentKeys.all, 'list'] as const,
  models: () => ['ollama', 'models'] as const,
}

export function useAgents() {
  return useQuery({
    queryKey: agentKeys.lists(),
    queryFn: getAgents,
  })
}

export function useAgentChat() {
  return useMutation({
    mutationFn: ({
      agentId,
      message,
      context,
    }: {
      agentId: string
      message: string
      context?: Record<string, unknown>
    }) => chatWithAgent(agentId, message, context),
  })
}

export function useAvailableModels() {
  return useQuery({
    queryKey: agentKeys.models(),
    queryFn: async (): Promise<OllamaModel[]> => {
      try {
        const response = await fetch(`${OLLAMA_URL}/api/tags`)
        if (!response.ok) {
          throw new Error('Failed to fetch models')
        }
        const data = (await response.json()) as { models: OllamaModel[] }
        return data.models || []
      } catch {
        return []
      }
    },
    retry: false,
    staleTime: 30000,
  })
}

export function useOllamaStatus() {
  return useQuery({
    queryKey: ['ollama', 'status'],
    queryFn: async (): Promise<boolean> => {
      try {
        const response = await fetch(`${OLLAMA_URL}/api/tags`)
        return response.ok
      } catch {
        return false
      }
    },
    retry: false,
    refetchInterval: 30000,
  })
}
