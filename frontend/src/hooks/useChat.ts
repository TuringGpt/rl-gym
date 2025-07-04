import { useState, useCallback } from 'react';
import { ChatMessage, ChatRequest, AvailableModel } from '../types/chat';
import { chatService } from '../services/chatService';
import { useSession } from '../contexts/SessionContext';

export const useChat = () => {
  const { currentSession } = useSession();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<'openai' | 'anthropic'>('openai');
  const [availableModels, setAvailableModels] = useState<AvailableModel[]>([]);

  const loadAvailableModels = useCallback(async () => {
    try {
      const models = await chatService.getAvailableModels();
      setAvailableModels(models);
    } catch (err: any) {
      setError(err.message || 'Failed to load available models');
    }
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    if (!currentSession) {
      setError('No active session. Please create a session first.');
      return;
    }

    if (!message.trim()) {
      return;
    }

    setIsLoading(true);
    setError(null);

    // Add user message to chat
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const request: ChatRequest = {
        message,
        model: selectedModel,
        session_id: currentSession,
        conversation_history: messages,
      };

      const response = await chatService.sendMessage(request);

      // Add assistant response to chat
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: response.timestamp,
        tool_calls: response.tool_calls,
        tool_results: response.tool_results,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      // Remove the user message if the request failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }, [currentSession, selectedModel, messages]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const switchModel = useCallback((model: 'openai' | 'anthropic') => {
    setSelectedModel(model);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    selectedModel,
    availableModels,
    sendMessage,
    clearChat,
    switchModel,
    loadAvailableModels,
  };
};