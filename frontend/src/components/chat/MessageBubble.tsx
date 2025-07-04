import { ChatMessage } from '../../types/chat';

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp).toLocaleTimeString();

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-3xl px-4 py-2 rounded-lg ${isUser
          ? 'bg-primary-500 text-white ml-12'
          : 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-100 mr-12'
        }`}>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium opacity-75">
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          <span className="text-xs opacity-50 ml-2">{timestamp}</span>
        </div>

        <div className="whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {/* Show tool calls if present */}
        {message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-3 pt-3 border-t border-opacity-20 border-white">
            <div className="text-xs font-medium opacity-75 mb-2">🛠️ Tools Used:</div>
            {message.tool_calls.map((tool, index) => (
              <div key={index} className="text-xs opacity-75 mb-1">
                • {tool.function?.name || tool.name}
              </div>
            ))}
          </div>
        )}

        {/* Show tool results if present */}
        {message.tool_results && message.tool_results.length > 0 && (
          <div className="mt-3 pt-3 border-t border-opacity-20 border-white">
            <div className="text-xs font-medium opacity-75 mb-2">📊 Tool Results:</div>
            {message.tool_results.map((result, index) => (
              <div key={index} className="text-xs opacity-75 mb-2">
                {result.success ? (
                  <div className="bg-green-500 bg-opacity-20 p-2 rounded">
                    ✅ Success
                  </div>
                ) : (
                  <div className="bg-red-500 bg-opacity-20 p-2 rounded">
                    ❌ Error: {result.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;