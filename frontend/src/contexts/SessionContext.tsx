import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { SessionContextType, Session } from '../types/session';
import { sessionService } from '../services/sessionService';
import { apiService } from '../services/api';

const SessionContext = createContext<SessionContextType | undefined>(undefined);

interface SessionProviderProps {
  children: ReactNode;
}

export const SessionProvider: React.FC<SessionProviderProps> = ({ children }) => {
  const [currentSession, setCurrentSessionState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSession = localStorage.getItem('currentSession');
    if (savedSession) {
      setCurrentSessionState(savedSession);
      apiService.setSessionId(savedSession);
    }
  }, []);

  // Listen for session invalidation events
  useEffect(() => {
    const handleSessionInvalid = () => {
      setCurrentSessionState(null);
      setError('Session expired or invalid. Please create a new session.');
    };

    window.addEventListener('sessionInvalid', handleSessionInvalid);
    return () => window.removeEventListener('sessionInvalid', handleSessionInvalid);
  }, []);

  const setCurrentSession = (sessionId: string | null) => {
    setCurrentSessionState(sessionId);
    apiService.setSessionId(sessionId);
    if (sessionId) {
      localStorage.setItem('currentSession', sessionId);
    } else {
      localStorage.removeItem('currentSession');
    }
    setError(null);
  };

  const createSession = async (): Promise<Session> => {
    setIsLoading(true);
    setError(null);

    try {
      const session = await sessionService.createSession();
      setCurrentSession(session.session_id);
      return session;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create session';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const value: SessionContextType = {
    currentSession,
    setCurrentSession,
    createSession,
    isLoading,
    error,
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = (): SessionContextType => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};