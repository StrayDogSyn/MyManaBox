export interface Card {
  name: string
  scryfall_id: string
  set_code: string
  mana_cost: string | null
  cmc: number
  type_line: string
  rarity: 'common' | 'uncommon' | 'rare' | 'mythic'
  colors: string[]
  prices: {
    usd: string | null
    usd_foil: string | null
  }
  image_uris?: {
    small: string
    normal: string
    large: string
    art_crop: string
  }
}

export interface CollectionCard {
  card: Card
  quantity: number
  foil: boolean
  condition: 'NM' | 'LP' | 'MP' | 'HP' | 'DMG'
}

export interface Deck {
  id: string
  name: string
  format: string
  commander?: Card
  cards: DeckCard[]
  created_at: string
  updated_at: string
}

export interface DeckCard {
  card: Card
  quantity: number
  is_sideboard: boolean
  is_commander: boolean
}

export interface Agent {
  id: string
  name: string
  description: string
  capabilities: string[]
  model: string
  system_prompt: string
}

export interface SearchFilters {
  query?: string
  colors?: string[]
  rarity?: string[]
  type?: string
  set?: string
  cmc_min?: number
  cmc_max?: number
  price_min?: number
  price_max?: number
}

export interface PaginationParams {
  page: number
  limit: number
}

export interface ApiResponse<T> {
  data: T
  success: boolean
  error?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  has_more: boolean
}

export interface CollectionStats {
  total_cards: number
  unique_cards: number
  total_value: number
  by_rarity: Record<string, number>
  by_color: Record<string, number>
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
}

export interface OllamaModel {
  name: string
  size: string
  modified_at: string
}
