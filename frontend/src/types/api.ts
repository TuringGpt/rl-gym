export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  errors?: ApiError[];
}

export interface ApiError {
  code: string;
  message: string;
  details?: string;
}

export interface PaginationInfo {
  total: number;
  skip: number;
  limit: number;
}

export interface ListingItem {
  sku: string;
  status: 'ACTIVE' | 'INACTIVE';
  summaries: ListingSummary[];
  attributes: ListingAttributes;
  issues: any[];
}

export interface ListingSummary {
  marketplace_id: string;
  asin: string;
  product_type: string;
  status: string;
}

export interface ListingAttributes {
  seller_name: string;
  title: string;
  description: string;
  price: number;
  quantity: number;
}

export interface ListingItemsSearchResponse {
  items: ListingItem[];
  pagination: PaginationInfo;
}

export interface DatabaseState {
  session_id: string;
  total_listings: number;
  active_listings: number;
  inactive_listings: number;
  seller_counts: Record<string, { name: string; count: number }>;
  price_stats: {
    min_price: number;
    max_price: number;
    avg_price: number;
  };
  total_inventory: number;
}