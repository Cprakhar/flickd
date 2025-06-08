export interface Video {
  video_id: string
  video_url: string
  caption?: string
  hashtags?: string[]
  user_avatar?: string
  user_name?: string
}

export interface ProductRecommendation {
  title: string
  type: string
  name: string // Added for display
  color: string
  matched_product_id: string
  match_type: "exact" | "similar"
  image_url: string // Added for display
  confidence?: number // Confidence score for product match
}

export interface RecommendationData {
  video_id: string
  vibes: string[]
  products: ProductRecommendation[]
}

// API Response Types
export interface VideosApiResponse {
  status: "success" | "error"
  data: Video[]
  message?: string
  next_page?: number | null // For pagination/infinite scroll
}

export interface RecommendationApiResponse {
  status: "success" | "error"
  data: RecommendationData
  message?: string
}
