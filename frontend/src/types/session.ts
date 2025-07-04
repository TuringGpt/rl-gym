export interface Session {
  session_id: string;
  created_at: string;
  message: string;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_accessed: string;
  db_path: string;
  file_size: number;
  exists: boolean;
}

export interface SessionContextType {
  currentSession: string | null;
  setCurrentSession: (sessionId: string | null) => void;
  createSession: () => Promise<Session>;
  isLoading: boolean;
  error: string | null;
}