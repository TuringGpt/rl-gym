import { apiService } from './api';
import { Session, SessionInfo } from '../types/session';

export class SessionService {
  // Create a new session
  async createSession(): Promise<Session> {
    return apiService.post<Session>('/sessions');
  }

  // Get session information
  async getSessionInfo(sessionId: string): Promise<SessionInfo> {
    return apiService.get<SessionInfo>(`/sessions/${sessionId}`);
  }

  // Reset database for current session
  async resetDatabase(): Promise<{ status: string; message: string; session_id: string }> {
    return apiService.post('/test/reset');
  }

  // Get current database state
  async getDatabaseState(): Promise<any> {
    return apiService.get('/test/state');
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return apiService.get('/health');
  }
}

export const sessionService = new SessionService();