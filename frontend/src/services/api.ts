import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ApiResponse } from '../types/api';

class ApiService {
  private client: AxiosInstance;
  private baseURL = 'http://localhost:8000';

  constructor() {
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add session header
    this.client.interceptors.request.use((config) => {
      const sessionId = localStorage.getItem('currentSession');
      if (sessionId && config.headers) {
        config.headers['X-Session-ID'] = sessionId;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        if (error.response?.status === 400 && error.response?.data?.detail?.includes('Invalid session ID')) {
          // Clear invalid session
          localStorage.removeItem('currentSession');
          window.dispatchEvent(new CustomEvent('sessionInvalid'));
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic request method
  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
    url: string,
    data?: any,
    headers?: Record<string, string>
  ): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.request({
        method,
        url,
        data,
        headers,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'API request failed');
    }
  }

  // GET request
  async get<T>(url: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('GET', url, undefined, headers);
  }

  // POST request
  async post<T>(url: string, data?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('POST', url, data, headers);
  }

  // PUT request
  async put<T>(url: string, data?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('PUT', url, data, headers);
  }

  // PATCH request
  async patch<T>(url: string, data?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('PATCH', url, data, headers);
  }

  // DELETE request
  async delete<T>(url: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('DELETE', url, undefined, headers);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.get('/health');
  }

  // Set session ID for requests
  setSessionId(sessionId: string | null) {
    if (sessionId) {
      localStorage.setItem('currentSession', sessionId);
    } else {
      localStorage.removeItem('currentSession');
    }
  }

  // Get current session ID
  getCurrentSessionId(): string | null {
    return localStorage.getItem('currentSession');
  }
}

export const apiService = new ApiService();