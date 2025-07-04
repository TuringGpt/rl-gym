# SP-API Testing Dashboard

A comprehensive full-stack testing framework for Amazon's Selling Partner API mock implementation, featuring a React frontend and FastAPI backend with session-based testing capabilities.

## 🏗️ Architecture

```
rl-gym/
├── backend/           # FastAPI backend server
│   ├── app/          # Application code
│   ├── sessions/     # Session databases
│   └── ...
├── frontend/         # React frontend dashboard
│   ├── src/         # Source code
│   ├── public/      # Static assets
│   └── ...
└── README.md        # This file
```

## ✨ Features

### Backend (FastAPI)
- **Session Management**: Isolated databases per testing session
- **SP-API Mock**: Complete Amazon Selling Partner API simulation
- **Test Flows**: 10 predefined test scenarios for validation
- **Database Reset**: Restore to seed state between tests
- **Auto-generated Sessions**: Unique session IDs for parallel testing

### Frontend (React)
- **Dashboard**: Session management and quick stats
- **Test Flows**: Browse and execute test scenarios
- **Validation**: Automated test result validation
- **Database Viewer**: Real-time database state monitoring
- **Tools**: Database reset, connection testing, data export

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at `http://localhost:8000`

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 3. Access the Dashboard

1. Open `http://localhost:3000` in your browser
2. Create a new session or input an existing session ID
3. Browse test flows and start testing!

## 📋 Testing Workflow

### Basic Workflow
1. **Create Session**: Generate a unique testing session
2. **Browse Flows**: View available test scenarios
3. **Execute Test**: Ask Claude to perform the described action
4. **Validate Result**: Check if the action was performed correctly
5. **Reset Database**: Restore to original state for next test

### Available Test Flows
- **Create Operations**: Add new listings
- **Update Operations**: Modify existing listings
- **Delete Operations**: Remove or deactivate listings
- **Search Operations**: Find listings with various criteria
- **Bulk Operations**: Mass updates across multiple listings
- **Analysis Operations**: Data analysis and reporting

## 🤖 Claude Configuration

### MCP Server Integration
This project includes an MCP (Model Context Protocol) server that provides Claude with direct access to the SP-API testing framework.

#### MCP Server Setup
The MCP server (`mcp_server.py`) provides the following tools for Claude:
- **get_listing_item**: Get details about specific listings
- **create_or_update_listing**: Create or fully update listings
- **update_listing_partial**: Partially update existing listings
- **delete_listing_item**: Delete/deactivate listings
- **search_listings**: Search for listings with filters

#### Claude Integration Workflow
1. **Session Creation**: Claude can create isolated testing sessions
2. **API Operations**: Claude can perform all SP-API operations through MCP tools
3. **Validation**: Use the frontend to validate Claude's actions
4. **Testing Flows**: Claude can execute predefined test scenarios

#### MCP Server Configuration
```json
{
  "mcpServers": {
    "amazon-sp-api-mock": {
      "command": "/path/to/python",
      "args": ["/path/to/rl-gym/mcp_server.py"],
      "disabled": false,
      "alwaysAllow": [],
      "disabledTools": []
    }
  }
}
```

#### Example Claude Usage
```
Claude, please:
1. Create a session for testing
2. Create a new laptop listing for SELLER001 with SKU 'TEST-LAPTOP-001'
3. Set the title to 'Test Gaming Laptop' and price to $999.99
4. Make it active in the US marketplace
```

## 🔧 API Endpoints

### Session Management
- `POST /sessions` - Create new session
- `GET /sessions/{id}` - Get session info

### Test Flows
- `GET /test/flows` - List all test flows
- `GET /test/flows/{id}` - Get specific flow details
- `GET /test/validate/{id}` - Validate flow execution
- `GET /test/validate/all` - Validate all flows

### Database Operations
- `POST /test/reset` - Reset database to seed state
- `GET /test/state` - Get current database state
- `GET /test/help` - Get testing help information

### Listings API (SP-API Mock)
- `GET /listings/2021-08-01/items/{seller_id}/{sku}` - Get listing
- `PUT /listings/2021-08-01/items/{seller_id}/{sku}` - Create/update listing
- `PATCH /listings/2021-08-01/items/{seller_id}/{sku}` - Partial update
- `DELETE /listings/2021-08-01/items/{seller_id}/{sku}` - Delete listing
- `GET /listings/2021-08-01/items` - Search listings

## 🎯 Use Cases

### For AI Testing
- Test Claude's ability to interact with APIs
- Validate API request/response handling
- Verify data manipulation accuracy
- Test complex multi-step workflows

### For API Development
- Mock Amazon SP-API for development
- Test API integrations without real Amazon account
- Validate API client implementations
- Debug API interaction issues

### For Training & Learning
- Learn Amazon SP-API structure
- Practice API integration patterns
- Understand session-based testing
- Explore React + FastAPI architecture

## 🧪 Testing with Claude

### Prerequisites for Claude Integration
1. **MCP Server Running**: Ensure the MCP server is configured and running
2. **Backend Active**: FastAPI server must be running on port 8000
3. **Frontend Available**: React dashboard should be accessible on port 3000

### Claude Testing Workflow
1. **Session Setup**:
   ```
   Claude, create a new testing session for SP-API testing
   ```

2. **Execute Test Flows**:
   ```
   Please perform the following test:
   - Create a new laptop listing for SELLER001
   - SKU: TEST-LAPTOP-001
   - Title: Test Gaming Laptop
   - Price: $999.99
   - Status: ACTIVE
   - Marketplace: US (ATVPDKIKX0DER)
   ```

3. **Validation**:
   - Use the frontend dashboard to validate Claude's actions
   - Check the "Test Flows" page for predefined scenarios
   - Run validation to verify Claude performed actions correctly

4. **Database Reset**:
   ```
   Claude, reset the database to prepare for the next test
   ```

### Available Test Scenarios
- **Create Operations**: New product listings
- **Update Operations**: Price changes, inventory updates
- **Delete Operations**: Product deactivation
- **Search Operations**: Finding products by criteria
- **Bulk Operations**: Mass updates across multiple products
- **Analysis Operations**: Data analysis and reporting

### Claude Capabilities Testing
- **API Interaction**: Can Claude make proper HTTP requests?
- **Data Validation**: Does Claude handle response data correctly?
- **Error Handling**: How does Claude respond to API errors?
- **Complex Workflows**: Can Claude execute multi-step operations?
- **Data Consistency**: Does Claude maintain data integrity?

### Validation and Feedback
- **Automated Validation**: Built-in test flow validation
- **Visual Feedback**: Dashboard shows pass/fail results
- **Detailed Reports**: JSON validation results for debugging
- **Performance Metrics**: Track success rates and response times

## 🛠️ Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📊 Session Management

### Session Isolation
- Each session gets its own SQLite database
- Complete data isolation between sessions
- Parallel testing support
- Automatic cleanup capabilities

### Session Format
- Auto-generated: `session_xxxxxxxxxxxx`
- 12-character hexadecimal suffix
- Unique across all sessions
- Required for all API operations

## 🔍 Monitoring & Debugging

### Frontend Tools
- Real-time database state viewer
- Connection testing utilities
- Session data export
- API documentation links

### Backend Logging
- Comprehensive request/response logging
- Session activity tracking
- Error reporting and debugging
- Performance monitoring

## 📚 Documentation

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc` (Alternative API docs)
- **Testing Help**: `http://localhost:8000/test/help` (Testing guide)
- **Frontend README**: `frontend/README.md` (Frontend-specific docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: Use ESLint and Prettier configurations
- **TypeScript**: Strict type checking enabled
- **Comments**: Document complex logic and API interactions

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python version (3.8+)
   - Install dependencies: `pip install -r requirements.txt`
   - Verify port 8000 is available

2. **Frontend won't start**
   - Check Node.js version (16+)
   - Install dependencies: `npm install`
   - Verify port 3000 is available

3. **Session errors**
   - Ensure backend is running
   - Check session ID format
   - Create new session if expired

4. **API connection issues**
   - Verify CORS configuration
   - Check network connectivity
   - Confirm backend health: `http://localhost:8000/health`

### Performance Tips
- Use session reuse for multiple tests
- Reset database only when necessary
- Monitor session database sizes
- Clean up old sessions periodically

## 📄 License

This project is part of the SP-API Mock testing framework for educational and development purposes.

## 🙏 Acknowledgments

- Amazon Selling Partner API documentation
- FastAPI framework and community
- React and Vite development teams
- Tailwind CSS for styling framework