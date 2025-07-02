# API Mock Gym

A modular system for creating realistic mock APIs to train language models on authentic API interactions. Currently implements Amazon Selling Partner API with plans for additional services.

## 🚀 Features

- **Realistic API Mocking**: Faithful reproduction of real API endpoints, request/response patterns
- **Isolated Services**: Each API service runs in its own container with dedicated database
- **Production-Ready**: Full authentication, rate limiting, error handling, and logging
- **Training Optimized**: Designed specifically for LLM training on API interactions
- **Easily Extensible**: Modular architecture for adding new API services

## 🏗️ Architecture

```
├── services/
│   └── amazon/          # Amazon Selling Partner API mock
├── shared/              # Common utilities and models
├── scripts/             # Setup and utility scripts
└── docs/               # Documentation
```

Each service includes:
- FastAPI application with authentic endpoints
- PostgreSQL database with realistic schemas
- Docker containerization
- Comprehensive mock data generation

## 🚦 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for development)

### Setup

1. **Clone and setup the project:**
```bash
git clone <repository-url>
cd api-mock-gym
chmod +x scripts/setup.sh
./scripts/setup.sh
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Verify services are running:**
```bash
# Amazon SP-API Mock
curl http://localhost:8001/health

# View API documentation
open http://localhost:8001/docs
```

## 📊 Available Services

### Amazon Selling Partner API Mock
**Port:** 8001  
**Base URL:** `http://localhost:8001`

#### Implemented Endpoints:

**Orders API (v0)**
- `GET /orders/v0/orders` - List orders with filtering
- `GET /orders/v0/orders/{orderId}` - Get order details
- `GET /orders/v0/orders/{orderId}/orderItems` - Get order items

**Inventory API (v1)**
- `GET /fba/inventory/v1/summaries` - Get inventory summaries
- `GET /fba/inventory/v1/details` - Get detailed inventory

**Listings API (2021-08-01)**
- `PUT /listings/2021-08-01/items/{sellerId}/{sku}` - Create/update listing
- `GET /listings/2021-08-01/items/{sellerId}/{sku}` - Get listing details
- `DELETE /listings/2021-08-01/items/{sellerId}/{sku}` - Delete listing

**Reports API (2021-06-30)**
- `POST /reports/2021-06-30/reports` - Create report request
- `GET /reports/2021-06-30/reports/{reportId}` - Get report status

## 🔧 Development

### Environment Configuration

Each service has its own `.env` file generated from templates:

```bash
# Generate all environment files
./scripts/generate-env.sh

# Seed mock data
./scripts/seed-all-data.sh
```

### Adding New Services

1. Create service directory: `services/{service-name}/`
2. Implement FastAPI application following existing pattern
3. Add service to `docker-compose.yml`
4. Create database schema and seed data
5. Update documentation

### Testing

```bash
# Run tests for specific service
cd services/amazon
python -m pytest

# Run all tests
docker-compose -f docker-compose.test.yml up --build
```

## 📚 API Documentation

- **Interactive Docs**: `http://localhost:8001/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI Spec**: `http://localhost:8001/openapi.json`

## 🔐 Authentication

The mock APIs implement realistic authentication patterns:

- **Amazon SP-API**: Mock LWA (Login with Amazon) tokens using JWT
- Rate limiting matches real API constraints
- Proper error responses for auth failures

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| amazon-api | 8001 | Amazon SP-API Mock |
| amazon-db | 5432 | PostgreSQL for Amazon service |
| redis | 6379 | Rate limiting and caching |
| pgadmin | 8080 | Database administration (dev only) |

## 📈 Usage for ML Training

### Generating Training Data

```python
import requests
import json

# Example: Generate order data
response = requests.get(
    'http://localhost:8001/orders/v0/orders',
    headers={'Authorization': 'Bearer mock-token'},
    params={'CreatedAfter': '2023-01-01T00:00:00Z'}
)

training_data = {
    'input': f"GET /orders/v0/orders?CreatedAfter=2023-01-01T00:00:00Z",
    'output': response.json()
}
```

### API Interaction Patterns

The mock APIs provide realistic interaction patterns for training:
- Pagination handling
- Error scenarios (rate limits, auth failures)
- Complex filtering and sorting
- Webhook simulation
- Batch operations

## 🛠️ Configuration

### Environment Variables

**Global (.env)**
```bash
COMPOSE_PROJECT_NAME=api-mock-gym
POSTGRES_PASSWORD=your-secure-password
REDIS_PASSWORD=your-redis-password
```

**Amazon Service**
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
AMAZON_SERVICE_PORT=8001
LWA_CLIENT_ID=mock-client-id
RATE_LIMIT_REQUESTS=100
```

## 🚀 Production Deployment

### Docker Swarm
```bash
docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml api-mock-gym
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## 🔄 Roadmap

- [ ] **Additional Services**: Slack, Stripe, Notion, GitHub APIs
- [ ] **Gateway Layer**: Central routing and authentication
- [ ] **Monitoring**: Prometheus metrics and Grafana dashboards
- [ ] **Logging**: Centralized logging with ELK stack
- [ ] **ML Integration**: Built-in training data export
- [ ] **Performance**: Caching and optimization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-service`
3. Implement following existing patterns
4. Add tests and documentation
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Architecture**: See `architecture-plan.md`

---

**Note**: This is a mock API system for training purposes. Do not use with real credentials or in production environments with actual API keys.