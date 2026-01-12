import axios, { type AxiosError, type AxiosResponse } from 'axios'
import type {
  ApiResponse,
  PaginatedResponse,
  CollectionCard,
  Card,
  Deck,
  Agent,
  SearchFilters,
  PaginationParams,
  CollectionStats,
} from '@/types/api'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    console.error('API Error:', message)
    return Promise.reject(new Error(message))
  }
)

export async function getCollection(
  filters?: SearchFilters,
  pagination?: PaginationParams
): Promise<PaginatedResponse<CollectionCard>> {
  const params = { ...filters, ...pagination }
  const response = await apiClient.get<PaginatedResponse<CollectionCard>>('/api/collection', { params })
  return response.data
}

export async function getCollectionStats(): Promise<CollectionStats> {
  const response = await apiClient.get<ApiResponse<CollectionStats>>('/api/collection/stats')
  return response.data.data
}

export async function searchCards(
  filters: SearchFilters,
  pagination?: PaginationParams
): Promise<PaginatedResponse<Card>> {
  const params = { ...filters, ...pagination }
  const response = await apiClient.get<PaginatedResponse<Card>>('/api/cards/search', { params })
  return response.data
}

export async function getDecks(): Promise<Deck[]> {
  const response = await apiClient.get<ApiResponse<Deck[]>>('/api/decks')
  return response.data.data
}

export async function getDeck(id: string): Promise<Deck> {
  const response = await apiClient.get<ApiResponse<Deck>>(`/api/decks/${id}`)
  return response.data.data
}

export async function createDeck(deck: Partial<Deck>): Promise<Deck> {
  const response = await apiClient.post<ApiResponse<Deck>>('/api/decks', deck)
  return response.data.data
}

export async function updateDeck(id: string, deck: Partial<Deck>): Promise<Deck> {
  const response = await apiClient.put<ApiResponse<Deck>>(`/api/decks/${id}`, deck)
  return response.data.data
}

export async function deleteDeck(id: string): Promise<void> {
  await apiClient.delete(`/api/decks/${id}`)
}

export async function getAgents(): Promise<Agent[]> {
  const response = await apiClient.get<ApiResponse<Agent[]>>('/api/agents')
  return response.data.data
}

export async function chatWithAgent(
  agentId: string,
  message: string,
  context?: Record<string, unknown>
): Promise<string> {
  const response = await apiClient.post<ApiResponse<{ response: string }>>(`/api/agents/${agentId}/chat`, {
    message,
    context,
  })
  return response.data.data.response
}

export async function addToCollection(
  scryfallId: string,
  quantity: number,
  foil: boolean,
  condition: string
): Promise<CollectionCard> {
  const response = await apiClient.post<ApiResponse<CollectionCard>>('/api/collection', {
    scryfall_id: scryfallId,
    quantity,
    foil,
    condition,
  })
  return response.data.data
}

export async function removeFromCollection(scryfallId: string): Promise<void> {
  await apiClient.delete(`/api/collection/${scryfallId}`)
}
