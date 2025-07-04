import { apiService } from './api';
import { ChatRequest, ChatResponse, AvailableModel, McpTool } from '../types/chat';

class ChatService {
  async getAvailableModels(): Promise<AvailableModel[]> {
    return apiService.get<AvailableModel[]>('/chat/models');
  }

  async sendMessageToOpenAI(request: ChatRequest): Promise<ChatResponse> {
    return apiService.post<ChatResponse>('/chat/openai', request);
  }

  async sendMessageToAnthropic(request: ChatRequest): Promise<ChatResponse> {
    return apiService.post<ChatResponse>('/chat/anthropic', request);
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    if (request.model === 'openai') {
      return this.sendMessageToOpenAI(request);
    } else if (request.model === 'anthropic') {
      return this.sendMessageToAnthropic(request);
    } else {
      throw new Error(`Unsupported model: ${request.model}`);
    }
  }

  async getMcpTools(): Promise<{ tools: McpTool[] }> {
    return apiService.get<{ tools: McpTool[] }>('/chat/mcp/tools');
  }
}

export const chatService = new ChatService();