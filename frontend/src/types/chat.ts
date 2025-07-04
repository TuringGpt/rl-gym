export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  tool_calls?: ToolCall[];
  tool_results?: ToolResult[];
}

export interface ToolCall {
  id: string;
  function?: {
    name: string;
    arguments: string;
  };
  name?: string;
  input?: Record<string, any>;
}

export interface ToolResult {
  tool_call_id?: string;
  tool_use_id?: string;
  result: any;
  success: boolean;
  error?: string;
}

export interface ChatRequest {
  message: string;
  model: 'openai' | 'anthropic';
  session_id: string;
  conversation_history: ChatMessage[];
}

export interface ChatResponse {
  message: string;
  model: string;
  timestamp: string;
  tool_calls?: ToolCall[];
  tool_results?: ToolResult[];
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
    input_tokens?: number;
    output_tokens?: number;
  };
}

export interface AvailableModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  supports_function_calling: boolean;
}

export interface McpTool {
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}