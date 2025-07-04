# Claude MCP Setup Instructions

This guide walks you through setting up the MCP server with Claude Desktop for testing the SP-API Testing Dashboard.

## 📋 Prerequisites

1. **Claude Desktop App** - Download from [Claude.ai](https://claude.ai/download)
2. **Python 3.8+** - For running the MCP server
3. **Docker** - For running the backend and frontend services

## 🚀 Step-by-Step Setup

### Step 1: Start the Docker Services

First, start the containerized backend and frontend:

```bash
# Navigate to your project directory
cd /path/to/rl-gym

# Start the services
docker-compose up -d

# Verify services are running
docker-compose ps
```

You should see:
- `sp-api-backend` - Running on port 8000
- `sp-api-frontend` - Running on port 3000

### Step 2: Install Python Dependencies

The MCP server needs Python dependencies installed locally:

```bash
# Navigate to the backend directory
cd backend

# Install the required packages
pip install -r requirements.txt
```

### Step 3: Test the MCP Server

Test that the MCP server works locally:

```bash
# From the backend directory, test the MCP server
python mcp_server.py --help

# You should see the help output with available options
```

### Step 4: Configure Claude Desktop

#### Option A: Automatic Configuration (Recommended)

```bash
# From the project root directory
cp claude_mcp_config.json ~/.config/claude-desktop/

# If the directory doesn't exist, create it first:
mkdir -p ~/.config/claude-desktop/
cp claude_mcp_config.json ~/.config/claude-desktop/
```

#### Option B: Manual Configuration

1. **Locate Claude's config directory:**
   - **macOS**: `~/Library/Application Support/Claude/`
   - **Linux**: `~/.config/claude-desktop/`
   - **Windows**: `%APPDATA%\Claude\`

2. **Create or edit the `claude_desktop_config.json` file:**

```json
{
  "mcpServers": {
    "amazon-sp-api-mock": {
      "command": "python",
      "args": [
        "/full/path/to/rl-gym/backend/mcp_server.py"
      ],
      "disabled": false,
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Important**: Replace `/full/path/to/rl-gym/` with the actual full path to your project directory.

### Step 5: Restart Claude Desktop

1. **Quit Claude Desktop completely**
2. **Restart Claude Desktop**
3. **Look for MCP connection indicators** in the Claude interface

### Step 6: Test the Integration

Once Claude is restarted, you can test the MCP integration:

#### Test 1: Create a Session
```
Please create a new session for SP-API testing
```

#### Test 2: Get Listing Information
```
Get the details for listing LAPTOP-001 from seller SELLER001
```

#### Test 3: Search Listings
```
Search for all active listings from SELLER001
```

## 🔍 Troubleshooting

### MCP Server Not Connecting

1. **Check Claude's logs** (if available in Claude Desktop)
2. **Verify the path** in the configuration file is correct
3. **Test the MCP server manually:**
   ```bash
   cd backend
   python mcp_server.py
   # Should start without errors
   ```

### Backend Connection Issues

1. **Verify Docker services are running:**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

2. **Check backend logs:**
   ```bash
   docker-compose logs backend
   ```

### Python Dependencies Issues

1. **Install missing packages:**
   ```bash
   cd backend
   pip install fastapi uvicorn sqlalchemy pydantic python-multipart mcp httpx starlette anyio requests
   ```

2. **Use a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Configuration File Issues

1. **Check file location:**
   ```bash
   # macOS/Linux
   ls -la ~/.config/claude-desktop/claude_desktop_config.json
   
   # Or check the Claude app's expected location
   ```

2. **Validate JSON syntax:**
   ```bash
   python -m json.tool ~/.config/claude-desktop/claude_desktop_config.json
   ```

## 🧪 Testing Workflow

Once everything is set up, here's a typical testing workflow:

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Create a Session in Claude
```
Please create a new session for testing the SP-API mock
```

### 3. Perform API Operations
```
Create a new product listing:
- Seller: SELLER001
- SKU: TEST-PRODUCT-001
- Title: Test Product
- Price: $29.99
- Status: ACTIVE
- Marketplace: US (ATVPDKIKX0DER)
```

### 4. Validate Results
- Use the frontend dashboard at http://localhost:3000
- Check the Database page to see the new listing
- Use the Validation page to verify the operation

### 5. Reset for Next Test
```
Please reset the database to prepare for the next test
```

## 📱 Frontend Dashboard

While testing with Claude, you can monitor the results using the web dashboard:

- **Dashboard**: http://localhost:3000 - Session management and overview
- **Test Flows**: View predefined test scenarios
- **Validation**: Validate Claude's actions
- **Database**: Monitor database state in real-time
- **Tools**: Reset database, manage sessions

## 🔧 Advanced Configuration

### Custom Environment Variables

You can customize the MCP server behavior by modifying the environment variables in the Claude configuration:

```json
{
  "mcpServers": {
    "amazon-sp-api-mock": {
      "command": "python",
      "args": ["/path/to/rl-gym/backend/mcp_server.py"],
      "disabled": false,
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000",
        "DEBUG": "true"
      }
    }
  }
}
```

### Multiple Environments

You can set up different configurations for different environments:

```json
{
  "mcpServers": {
    "sp-api-local": {
      "command": "python",
      "args": ["/path/to/rl-gym/backend/mcp_server.py"],
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000"
      }
    },
    "sp-api-staging": {
      "command": "python",
      "args": ["/path/to/rl-gym/backend/mcp_server.py"],
      "env": {
        "FASTAPI_BASE_URL": "http://staging.example.com:8000"
      }
    }
  }
}
```

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Verify all prerequisites are installed**
3. **Test each component individually**
4. **Check the project documentation** in [`README.md`](README.md) and [`DOCKER.md`](DOCKER.md)

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ Claude shows MCP server connection indicators
2. ✅ Claude can create sessions and get session IDs
3. ✅ Claude can perform CRUD operations on listings
4. ✅ The frontend dashboard shows Claude's actions in real-time
5. ✅ Validation tests pass for Claude's operations

Happy testing! 🚀