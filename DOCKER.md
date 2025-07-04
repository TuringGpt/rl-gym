# Docker Setup Guide

This guide explains how to run the SP-API Testing Dashboard using Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB of available RAM
- Ports 3000 and 8000 available

## 🚀 Quick Start

### Production Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd rl-gym
   ```

2. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Setup

For development with hot reloading:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

## 🐳 Docker Services

### Backend Service
- **Image**: Custom Python 3.11 image
- **Port**: 8000
- **Features**:
  - FastAPI with auto-reload in development
  - SQLite database with persistent volumes
  - Session management with isolated databases
  - Health checks and automatic restarts

### Frontend Service
- **Image**: Custom Node.js 18 + Nginx image
- **Port**: 3000
- **Features**:
  - React with Vite build system
  - Nginx reverse proxy for production
  - Hot reloading in development mode
  - Optimized static asset serving

### MCP Server (Local)
- **Runtime**: Local Python process
- **Transport**: stdio (standard input/output)
- **Features**:
  - Model Context Protocol server for Claude integration
  - Direct stdio communication with Claude
  - Session-aware API tools via backend HTTP calls
  - Simplified local deployment

## 📁 Docker Files Structure

```
rl-gym/
├── docker-compose.yml          # Production configuration
├── docker-compose.dev.yml      # Development configuration
├── backend/
│   ├── Dockerfile              # Backend production image
│   ├── mcp_server.py           # Local MCP server (stdio mode)
│   └── .dockerignore           # Backend ignore patterns
├── frontend/
│   ├── Dockerfile              # Frontend production image
│   ├── Dockerfile.dev          # Frontend development image
│   ├── nginx.conf              # Nginx configuration
│   └── .dockerignore           # Frontend ignore patterns
├── claude_mcp_config.json      # Claude MCP configuration
└── DOCKER.md                   # This file
```

## 🔧 Configuration

### Environment Variables

#### Backend
- `PYTHONPATH=/app` - Python module path
- `DATABASE_URL=sqlite:///./listings.db` - Database connection
- `RELOAD=true` - Enable auto-reload (development only)

#### Frontend
- `VITE_API_BASE_URL=http://localhost:8000` - Backend API URL
- `CHOKIDAR_USEPOLLING=true` - File watching (development only)

#### MCP Server (Local)
- `FASTAPI_BASE_URL=http://localhost:8000` - Backend API URL for local MCP server

### Volumes

#### Production
- `backend_data` - Session databases persistence
- `backend_db` - Main database persistence

#### Development
- `./backend:/app` - Backend source code mounting
- `./frontend:/app` - Frontend source code mounting
- `/app/node_modules` - Node modules isolation

## 🛠️ Common Commands

### Production

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Build and start
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

### Development

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Rebuild development images
docker-compose -f docker-compose.dev.yml up --build

# Stop development environment
docker-compose -f docker-compose.dev.yml down
```

### Maintenance

```bash
# Remove all containers and volumes
docker-compose down -v

# Remove unused images
docker image prune

# View container status
docker-compose ps

# Execute commands in running containers
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🔍 Health Checks

All containerized services include health checks:

### Backend Health Check
- **Endpoint**: `GET /health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3


### Frontend Health Check
- **Method**: HTTP GET to root path
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

## 🌐 Networking

### Production Network
- **Name**: `sp-api-network`
- **Driver**: bridge
- **Services**: backend, frontend

### Development Network
- **Name**: `sp-api-network-dev`
- **Driver**: bridge
- **Services**: backend, frontend

## 📊 Resource Usage

### Minimum Requirements
- **CPU**: 1 core
- **RAM**: 2GB
- **Storage**: 1GB

### Recommended
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 5GB

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Check if ports are in use
   lsof -i :3000
   lsof -i :8000
   
   # Stop conflicting services
   docker-compose down
   ```

2. **Build failures**:
   ```bash
   # Clean build cache
   docker system prune
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

3. **Volume issues**:
   ```bash
   # Remove volumes and restart
   docker-compose down -v
   docker-compose up --build
   ```

4. **Network connectivity**:
   ```bash
   # Check container networking
   docker network ls
   docker network inspect sp-api-network
   ```

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check container status
docker-compose ps

# Inspect container details
docker inspect sp-api-backend
docker inspect sp-api-frontend
```

## 🔒 Security Considerations

### Production Deployment
- Change default ports if needed
- Use environment files for sensitive data
- Enable HTTPS with reverse proxy
- Implement proper firewall rules
- Regular security updates

### Development
- Development mode includes additional debugging tools
- Source code is mounted as volumes
- Auto-reload is enabled for faster development

## 📈 Performance Optimization

### Production
- Multi-stage builds for smaller images
- Nginx for efficient static file serving
- Gzip compression enabled
- Proper caching headers
- Health checks for reliability

### Development
- Hot reloading for faster development
- Source code mounting for instant changes
- Development-specific optimizations

## 🚀 Deployment

### Local Production Test
```bash
# Test production build locally
docker-compose -f docker-compose.yml up --build
```

### Cloud Deployment
The Docker setup is ready for deployment to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Kubernetes clusters
- Any Docker-compatible hosting

## 📞 Support

For Docker-related issues:
1. Check the troubleshooting section above
2. Review Docker and Docker Compose logs
3. Ensure system requirements are met
4. Verify network and port availability

## 🤖 Claude MCP Integration

### Overview
The setup includes a local MCP (Model Context Protocol) server that allows Claude to interact with the SP-API testing backend through a standardized interface. The MCP server runs locally using stdio transport for optimal Claude integration.

### MCP Server Features
- **Session Management**: Create and manage isolated testing sessions
- **Listing Operations**: Full CRUD operations on product listings
- **Search Capabilities**: Advanced filtering and text search
- **Stdio Transport**: Direct communication with Claude via standard input/output
- **Local Deployment**: Simplified setup without containerization complexity

### Claude Configuration

The MCP server is configured to run locally and communicate with Claude via stdio. See `CLAUDE_MCP_SETUP.md` for detailed setup instructions.

### Usage Workflow

1. **Start the Docker services** (backend and frontend):
   ```bash
   docker-compose up -d
   ```

2. **Start the local MCP server** (handled automatically by Claude):
   The MCP server runs as a local Python process when Claude needs it.

3. **In Claude, interact with the API**:
   ```
   Please search for listings with seller SELLER001
   ```

### Available MCP Tools

- **get_listing_item**: Retrieve specific listing details
- **create_or_update_listing**: Create or fully update listings
- **update_listing_partial**: Partial updates to existing listings
- **delete_listing_item**: Remove listings (sets to INACTIVE)
- **search_listings**: Advanced search with filters

### Troubleshooting MCP Connection

1. **Check backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Verify MCP server configuration**:
   Check `claude_mcp_config.json` and `CLAUDE_MCP_SETUP.md`

3. **Test backend API directly**:
   ```bash
   curl http://localhost:8000/listings/search
   ```

### Architecture Benefits

#### Simplified Setup
- Only backend and frontend are containerized
- MCP server runs locally for optimal Claude integration
- No complex HTTP/SSE transport configuration needed

#### Reliable Communication
- Direct stdio communication with Claude
- No network connectivity issues between containers
- Simplified debugging and troubleshooting