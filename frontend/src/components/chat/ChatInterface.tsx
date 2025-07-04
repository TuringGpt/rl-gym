import { useState, useRef, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import { useSession } from '../../contexts/SessionContext';
import MessageBubble from './MessageBubble';
import ModelSelector from './ModelSelector';

const ChatInterface = () => {
  const { currentSession } = useSession();
  const {
    messages,
    isLoading,
    error,
    selectedModel,
    sendMessage,
    clearChat,
    switchModel,
    loadAvailableModels
  } = useChat();

  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load available models on mount
  useEffect(() => {
    loadAvailableModels();
  }, [loadAvailableModels]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputMessage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage.trim();
    setInputMessage('');
    await sendMessage(message);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  if (!currentSession) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-6xl mb-4">💬</div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
            No Active Session
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Please create or select a session to start chatting with AI models.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 dark:border-gray-600 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              AI Chat
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Session: {currentSession}
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={clearChat}
              disabled={messages.length === 0}
              className="btn-secondary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Clear Chat
            </button>
          </div>
        </div>

        <div className="mt-4">
          <ModelSelector
            selectedModel={selectedModel}
            onModelChange={switchModel}
            disabled={isLoading}
          />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-4xl mb-4">🚀</div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                Start a conversation
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Ask me anything! I can help you with Amazon SP-API operations using MCP tools.
              </p>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                <p>Try asking:</p>
                <ul className="mt-2 space-y-1">
                  <li>• "Search for listings from SELLER001"</li>
                  <li>• "Get details for SKU LAPTOP-001"</li>
                  <li>• "Create a new listing for a product"</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div>
            {messages.map((message, index) => (
              <MessageBubble key={index} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 rounded-lg mr-12">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-500"></div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      AI is thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="flex-shrink-0 p-4 bg-red-50 border-t border-red-200 dark:bg-red-900/20 dark:border-red-400">
          <div className="flex items-center">
            <span className="text-red-600 dark:text-red-400 text-sm">
              ❌ {error}
            </span>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-600 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Shift+Enter for new line)"
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 disabled:opacity-50 resize-none min-h-[40px] max-h-32"
              rows={1}
            />
          </div>
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              'Send'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;