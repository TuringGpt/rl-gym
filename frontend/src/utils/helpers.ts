import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Utility function to merge Tailwind classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format date to readable string
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString();
}

// Format currency
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

// Format number with commas
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}

// Copy text to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy text: ', err);
    return false;
  }
}

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Get flow category from flow ID
export function getFlowCategory(flowId: string): string {
  if (flowId.includes('create')) return 'Create';
  if (flowId.includes('update')) return 'Update';
  if (flowId.includes('delete') || flowId.includes('deactivate')) return 'Delete';
  if (flowId.includes('search')) return 'Search';
  if (flowId.includes('bulk')) return 'Bulk Operations';
  if (flowId.includes('analysis') || flowId.includes('expensive')) return 'Analysis';
  return 'Other';
}

// Generate random ID
export function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}

// Validate session ID format
export function isValidSessionId(sessionId: string): boolean {
  return /^session_[a-f0-9]{12}$/.test(sessionId);
}

// Get status color class
export function getStatusColor(status: string): string {
  switch (status.toUpperCase()) {
    case 'PASS':
    case 'ACTIVE':
    case 'SUCCESS':
      return 'success';
    case 'FAIL':
    case 'INACTIVE':
    case 'ERROR':
      return 'error';
    case 'PENDING':
    case 'WARNING':
      return 'warning';
    default:
      return 'info';
  }
}

// Truncate text
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength) + '...';
}