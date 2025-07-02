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

## 🎯 Current Implementation Status

### ✅ Amazon Selling Partner API Mock - COMPREHENSIVE IMPLEMENTATION

**Available APIs (8 Complete API Sets):**
- **Orders API (v0)**: Complete order management with realistic data
- **FBA Inventory API (2020-12-01)**: Comprehensive inventory summaries and details
- **Listings API (2021-08-01)**: Product listing management with SKU operations
- **Reports API (2021-06-30)**: Report generation and retrieval system
- **Feeds API (2021-06-30)**: Data feed processing and submission
- **Catalog Items API (2022-04-01)**: Product catalog search and item details
- **Product Pricing API (v0)**: Competitive pricing and offer management
- **Finances API (v0)**: Financial events and settlement information

**🗄️ Advanced Database System:**
- ✅ **Alembic Migration Framework**: Complete database versioning and migration system
- ✅ **Comprehensive Schema**: 12+ tables covering all Amazon SP-API entities
- ✅ **Rich Seed Data**: Pre-populated with 50+ realistic orders, inventory, catalog items, pricing data
- ✅ **Automated Setup**: Database creation, migration, and seeding via startup script
- ✅ **Production-Ready**: Full relationship mapping and data integrity

**🔧 Key Features:**
- ✅ Authentication disabled for easy testing
- ✅ Rate limiting disabled for easy testing
- ✅ Realistic mock data with proper relationships (orders ↔ items ↔ inventory ↔ financials)
- ✅ Error responses matching real API behavior
- ✅ Comprehensive documentation via OpenAPI/Swagger
- ✅ Docker containerization with automated database setup
- ✅ Production-ready architecture with proper separation of concerns

### 🚧 Pipeline Services (Coming Soon)
- Slack API Mock
- Stripe API Mock
- Notion API Mock
- GitHub API Mock

## 🚦 Quick Start

### Prerequisites
- Docker and Docker Compose

### Simple Setup & Run Commands

1. **Clone the repository:**
```bash
git clone <repository-url>
cd api-mock-gym
```

2. **Create environment file:**
```bash
cp .env.template .env
```

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Wait for services to be ready (about 30 seconds), then test:**
```bash
# Check if Amazon API is running
curl http://localhost:8001/health

# Test orders endpoint
curl http://localhost:8001/orders/v0/orders

# 🎯 ACCESS COMPREHENSIVE SWAGGER UI DOCUMENTATION
open http://localhost:8001/docs
```

## 📖 Interactive API Documentation (Swagger UI)

### 🚀 **Access Complete API Documentation**

Once the service is running, visit: **`http://localhost:8001/docs`**

### ✨ **What You'll Find in Swagger UI:**

1. **📊 Complete API Overview**: All 8 Amazon SP-API collections organized by category
2. **🔍 Interactive Testing**: Click "Try it out" on any endpoint to test immediately
3. **📝 Request/Response Examples**: See exact request formats and realistic response data
4. **📋 Parameter Documentation**: Detailed parameter descriptions and validation rules
5. **🎯 No Authentication Required**: All endpoints ready to test without tokens

### 🎮 **How to Use Swagger UI:**

1. **Navigate to `http://localhost:8001/docs`**
2. **Browse API Collections**:
   - Orders API (v0)
   - FBA Inventory API (2020-12-01)
   - Listings API (2021-08-01)
   - Reports API (2021-06-30)
   - Feeds API (2021-06-30)
   - Catalog Items API (2022-04-01)
   - Product Pricing API (v0)
   - Finances API (v0)
3. **Click any endpoint** to expand details
4. **Click "Try it out"** to make live API calls
5. **Fill parameters** (or use defaults) and click "Execute"
6. **View realistic responses** with actual data from our seeded database

### 📱 **Alternative Documentation Views:**
- **ReDoc**: `http://localhost:8001/redoc` (Alternative documentation format)
- **OpenAPI Spec**: `http://localhost:8001/openapi.json` (Raw OpenAPI JSON)

### 🧪 Testing APIs in Postman

**Base URL:** `http://localhost:8001`

**Available Endpoints:**
```
GET  /health                           # Health check

# Orders API (v0)
GET  /orders/v0/orders                 # Get all orders
GET  /orders/v0/orders/{orderId}       # Get specific order
GET  /orders/v0/orders/{orderId}/orderItems  # Get order items

# FBA Inventory API (2020-12-01)
GET  /fba/inventory/v1/summaries       # Get inventory summaries

# Listings API (2021-08-01)
GET  /listings/2021-08-01/items/{sellerId}/{sku}  # Get listing
PUT  /listings/2021-08-01/items/{sellerId}/{sku}  # Create/update listing

# Reports API (2021-06-30)
POST /reports/2021-06-30/reports       # Create report
GET  /reports/2021-06-30/reports       # Get reports

# Feeds API (2021-06-30)
POST /feeds/2021-06-30/feeds           # Create feed
GET  /feeds/2021-06-30/feeds/{feedId}  # Get feed status

# Catalog Items API (2022-04-01)
GET  /catalog/2022-04-01/items         # Search catalog items
GET  /catalog/2022-04-01/items/{asin}  # Get catalog item details

# Product Pricing API (v0)
GET  /products/pricing/v0/pricing      # Get competitive pricing
GET  /products/pricing/v0/competitivePrice  # Get competitive pricing
GET  /products/pricing/v0/listings/{sku}/offers  # Get SKU offers
GET  /products/pricing/v0/items/{asin}/offers   # Get ASIN offers

# Finances API (v0)
GET  /finances/v0/financialEventGroups  # Get financial event groups
GET  /finances/v0/financialEvents       # Get financial events
GET  /finances/v0/financialEventGroups/{groupId}/financialEvents  # Get events by group
```

**Sample Postman Requests:**

1. **Get Orders:**
   - Method: GET
   - URL: `http://localhost:8001/orders/v0/orders`
   - Query params: `CreatedAfter=2024-01-01T00:00:00Z&OrderStatuses=Shipped,Pending`

2. **Get Specific Order:**
   - Method: GET
   - URL: `http://localhost:8001/orders/v0/orders/111-1111111-1111111`

3. **Get Inventory:**
   - Method: GET
   - URL: `http://localhost:8001/fba/inventory/v1/summaries`
   - Query params: `marketplaceIds=ATVPDKIKX0DER`

4. **Create Report:**
   - Method: POST
   - URL: `http://localhost:8001/reports/2021-06-30/reports`
   - Body (JSON):
   ```json
   {
     "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
     "marketplaceIds": ["ATVPDKIKX0DER"]
   }
   ```

5. **Get Listing:**
   - Method: GET
   - URL: `http://localhost:8001/listings/2021-08-01/items/SELLER001/SKU-TG-001`

### 🛑 Stop Services
```bash
docker-compose down
```

### 🧹 Clean Up (Reset Everything)
```bash
docker-compose down -v
docker system prune -f
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

**FBA Inventory API (2020-12-01)**
- `GET /fba/inventory/v1/summaries` - Get inventory summaries with detailed breakdown
- `GET /fba/inventory/v1/summaries/{granularityType}/{granularityId}` - Get filtered summaries

**Listings API (2021-08-01)**
- `PUT /listings/2021-08-01/items/{sellerId}/{sku}` - Create/update listing
- `GET /listings/2021-08-01/items/{sellerId}/{sku}` - Get listing details
- `DELETE /listings/2021-08-01/items/{sellerId}/{sku}` - Delete listing
- `PATCH /listings/2021-08-01/items/{sellerId}/{sku}` - Partially update listing

**Reports API (2021-06-30)**
- `POST /reports/2021-06-30/reports` - Create report request
- `GET /reports/2021-06-30/reports` - List reports with filtering
- `GET /reports/2021-06-30/reports/{reportId}` - Get report status
- `POST /reports/2021-06-30/reports/{reportId}/cancel` - Cancel report
- `GET /reports/2021-06-30/documents/{reportDocumentId}` - Get report document

**Feeds API (2021-06-30)**
- `POST /feeds/2021-06-30/feeds` - Create feed submission
- `GET /feeds/2021-06-30/feeds` - List feeds with filtering
- `GET /feeds/2021-06-30/feeds/{feedId}` - Get feed status
- `POST /feeds/2021-06-30/feeds/{feedId}/cancel` - Cancel feed
- `POST /feeds/2021-06-30/documents` - Create feed document
- `GET /feeds/2021-06-30/documents/{feedDocumentId}` - Get feed document

**Catalog Items API (2022-04-01)**
- `GET /catalog/2022-04-01/items` - Search catalog items by keywords/identifiers
- `GET /catalog/2022-04-01/items/{asin}` - Get catalog item details by ASIN

**Product Pricing API (v0)**
- `GET /products/pricing/v0/pricing` - Get pricing for SKUs or ASINs
- `GET /products/pricing/v0/competitivePrice` - Get competitive pricing data
- `GET /products/pricing/v0/listings/{sellerSku}/offers` - Get lowest priced offers for SKU
- `GET /products/pricing/v0/items/{asin}/offers` - Get lowest priced offers for ASIN

**Finances API (v0)**
- `GET /finances/v0/financialEventGroups` - List financial event groups
- `GET /finances/v0/financialEvents` - List financial events with date filtering
- `GET /finances/v0/financialEventGroups/{eventGroupId}/financialEvents` - Get events by group

#### Database Features:
- **🎯 Alembic Migrations**: Complete database versioning and migration system
- **📊 Comprehensive Schema**: 12+ tables covering all Amazon SP-API entities (orders, inventory, catalog, pricing, finances)
- **🌱 Seed Data**: Pre-populated with 50+ realistic orders, inventory items, catalog entries, and financial events
- **🔄 Automated Setup**: Database creation, migration, and seeding handled automatically on startup

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

### 🎯 **PRIMARY: Interactive Swagger UI**
**`http://localhost:8001/docs`** - Complete interactive documentation where you can:
- ✅ **Browse all 8 API collections** organized by functionality
- ✅ **Test endpoints directly** with "Try it out" buttons
- ✅ **See realistic responses** from actual seeded database
- ✅ **No authentication needed** - start testing immediately
- ✅ **Copy examples** for your own implementation

### 📖 **Additional Documentation Formats:**
- **ReDoc**: `http://localhost:8001/redoc` (Alternative clean documentation view)
- **OpenAPI Spec**: `http://localhost:8001/openapi.json` (Raw specification for tools/import)

### 🚀 **Swagger UI Features:**
- **Real-time Testing**: Execute actual API calls against live data
- **Parameter Validation**: See required/optional parameters with examples
- **Response Schemas**: Understand exact response structures
- **Error Examples**: See realistic error responses
- **Comprehensive Coverage**: All endpoints documented with examples

## 🔧 Notes

- **Authentication**: Currently disabled for easy testing
- **Rate Limiting**: Currently disabled for easy testing
- **Database**: Pre-populated with realistic mock data

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
    params={'CreatedAfter': '2024-01-01T00:00:00Z'}
)

training_data = {
    'input': f"GET /orders/v0/orders?CreatedAfter=2024-01-01T00:00:00Z",
    'output': response.json()
}
```

### API Interaction Patterns

The mock APIs provide realistic interaction patterns for training:
- Pagination handling with NextToken support
- Error scenarios and proper error responses
- Complex filtering and sorting parameters
- Realistic data relationships
- Multiple API versions and endpoints

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