import { useQuery } from '@tanstack/react-query'
import { getCollection, getCollectionStats } from '../client'
import type { SearchFilters, PaginationParams } from '@/types/api'

export const collectionKeys = {
  all: ['collection'] as const,
  lists: () => [...collectionKeys.all, 'list'] as const,
  list: (filters?: SearchFilters, pagination?: PaginationParams) =>
    [...collectionKeys.lists(), { filters, pagination }] as const,
  stats: () => [...collectionKeys.all, 'stats'] as const,
}

export function useCollection(filters?: SearchFilters, pagination?: PaginationParams) {
  return useQuery({
    queryKey: collectionKeys.list(filters, pagination),
    queryFn: () => getCollection(filters, pagination),
  })
}

export function useCollectionStats() {
  return useQuery({
    queryKey: collectionKeys.stats(),
    queryFn: getCollectionStats,
  })
}
