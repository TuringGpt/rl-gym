# AI Chat with MCP Integration Setup Guide (LangChain-Powered)

This guide explains how to set up and use the new AI Chat functionality with MCP (Model Context Protocol) integration, powered by LangChain for superior model management and tool integration.

## 🎯 Overview

The chat feature allows you to:
- Chat with multiple AI models (ChatGPT and Claude) via LangChain
- AI models can automatically call MCP tools based on your requests using LangChain agents
- Each chat is associated with a session for data isolation
- View tool execution results in real-time
- Advanced conversation memory and context management
- Unified tool interface across different AI providers

## 🔧 Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**New Dependencies Added:**
- `langchain` - Core LangChain framework
- `langchain-openai` - OpenAI integration
- `langchain-anthropic` - Anthropic integration
- `langchain-community` - Additional tools and utilities

### 2. Configure API Keys

Copy the environment template and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key

# Anthropic API Configuration  
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-api-key

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8001
FASTAPI_BASE_URL=http://localhost:8000
```

### 3. API Key Setup Instructions

#### OpenAI API Key:
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

#### Anthropic API Key:
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create a new API key
3. Copy the key (starts with `sk-ant-`)

## 🚀 Usage

### 1. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start the Frontend

```bash
cd frontend
npm run dev
```

### 3. Using the Chat Interface

1. **Create/Select Session**: First create or select a session from the Dashboard
2. **Navigate to Chat**: Click "AI Chat" in the sidebar or use the quick action
3. **Select AI Model**: Choose between GPT-4 Turbo (OpenAI) or Claude 3.5 Sonnet (Anthropic)
4. **Start Chatting**: Type your message and the AI will respond

## 🛠️ MCP Tool Integration

The AI models can automatically use these MCP tools:

### Available Tools:
- **`create_session`** - Create a new session
- **`get_listing_item`** - Get listing details by seller ID and SKU
- **`create_or_update_listing`** - Create or update a product listing
- **`update_listing_partial`** - Partially update a listing
- **`delete_listing_item`** - Delete a listing
- **`search_listings`** - Search listings with filters

### Example Conversations:

**User**: "Search for all listings from SELLER001"
**AI**: *Automatically calls `search_listings` tool with seller_id=SELLER001 and shows results*

**User**: "Get details for SKU LAPTOP-001 from SELLER001"  
**AI**: *Automatically calls `get_listing_item` tool and displays the listing details*

**User**: "Create a new listing for a smartphone with price $299"
**AI**: *Asks for required details and calls `create_or_update_listing` tool*

## 🎨 Features

### Chat Interface:
- **Model Selection**: Switch between OpenAI and Anthropic models
- **Session Integration**: Each chat uses your current session
- **Tool Visibility**: See when tools are called and their results
- **Auto-scroll**: Messages automatically scroll to bottom
- **Clear Chat**: Reset conversation history
- **Responsive Design**: Works on desktop and mobile

### LangChain-Powered AI Capabilities:
- **Intelligent Agents**: LangChain agents automatically decide when and how to use tools
- **Advanced Tool Calling**: Sophisticated tool selection and parameter handling
- **Conversation Memory**: Built-in conversation buffer memory for context retention
- **Error Recovery**: Robust error handling and retry mechanisms
- **Multi-Step Reasoning**: Agents can chain multiple tool calls for complex tasks
- **Unified Interface**: Consistent tool interface across OpenAI and Anthropic models
- **Usage Tracking**: Comprehensive token usage monitoring

## 🔍 Troubleshooting

### Common Issues:

1. **"No Active Session" Error**
   - Solution: Create a session from the Dashboard first

2. **API Key Errors**
   - Check that your API keys are correctly set in `.env`
   - Ensure you have sufficient credits/quota

3. **MCP Tool Errors**
   - Verify the backend is running on port 8000
   - Check that your session ID is valid

4. **Network Errors**
   - Ensure both frontend (port 3000) and backend (port 8000) are running
   - Check CORS settings if accessing from different domains

### Debug Mode:

Enable debug logging by checking the browser console and backend logs for detailed error information.

## 🔒 Security Notes

- API keys are stored server-side only
- Session-based data isolation ensures privacy
- All API calls are proxied through your backend
- No direct client-side API key exposure

## 🚀 Future Enhancements

Planned features:
- **Streaming Responses**: Real-time message streaming
- **Chat History**: Persistent conversation storage
- **File Uploads**: Document analysis capabilities
- **Custom Prompts**: Template system for common tasks
- **More AI Models**: Integration with additional providers

## 📊 Architecture

```
Frontend (React) → Backend (FastAPI) → LangChain Agents → AI APIs (OpenAI/Anthropic)
                                              ↓
                                         LangChain Tools
                                              ↓
                                         MCP Client → Your SP-API Backend
```

**LangChain Integration Benefits:**
- **Agent Framework**: Intelligent decision-making for tool usage
- **Tool Abstraction**: Unified tool interface regardless of AI provider
- **Memory Management**: Automatic conversation context handling
- **Error Recovery**: Built-in retry and error handling mechanisms
- **Extensibility**: Easy to add new models and tools
- **Observability**: Comprehensive logging and callback system

The chat system uses your existing session management and MCP server infrastructure, enhanced with LangChain's powerful agent framework for superior AI interactions.