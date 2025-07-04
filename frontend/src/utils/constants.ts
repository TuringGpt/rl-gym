export const API_BASE_URL = 'http://localhost:8000';

export const FLOW_CATEGORIES = {
  CREATE: 'Create',
  UPDATE: 'Update',
  DELETE: 'Delete',
  SEARCH: 'Search',
  BULK: 'Bulk Operations',
  ANALYSIS: 'Analysis'
} as const;

export const FLOW_CATEGORY_MAP: Record<string, keyof typeof FLOW_CATEGORIES> = {
  'flow_1_create_laptop': 'CREATE',
  'flow_2_update_laptop_price': 'UPDATE',
  'flow_3_delete_cable': 'DELETE',
  'flow_4_search_bookwise': 'SEARCH',
  'flow_5_search_gaming': 'SEARCH',
  'flow_6_price_range_search': 'SEARCH',
  'flow_7_deactivate_fitness': 'BULK',
  'flow_8_add_canada_kitchen': 'BULK',
  'flow_9_most_expensive_per_seller': 'ANALYSIS',
  'flow_10_bulk_inventory_reduction': 'BULK',
};

export const STATUS_COLORS = {
  PASS: 'success',
  FAIL: 'error',
  PENDING: 'warning',
  ACTIVE: 'success',
  INACTIVE: 'error',
} as const;

export const LOCAL_STORAGE_KEYS = {
  CURRENT_SESSION: 'currentSession',
  THEME: 'theme',
} as const;