# Personal Expense Tracker

A comprehensive personal expense tracking system with automatic categorization and analysis capabilities.

## Architecture Overview

This project is designed in three iterations:

1. **Iteration 1 (✅ Complete)**: Core FastAPI Backend with PostgreSQL
2. **Iteration 2**: n8n Integration for email-based expense parsing  
3. **Iteration 3**: MCP (Model Context Protocol) for LM Studio integration

> 📋 **For complete project status and implementation details, see [PROJECT_STATUS.md](PROJECT_STATUS.md)**

## Current Features (Iteration 1)

### ✅ Core Backend (FastAPI + PostgreSQL)
- **Database Models**: Expenses, Categories, and Merchant Rules
- **RESTful API**: Full CRUD operations for all entities
- **Automatic Categorization**: Fuzzy string matching with merchant rules
- **Analytics**: Expense summaries and category breakdowns
- **Webhook Support**: Ready for n8n integration

### API Endpoints

#### Expenses
- `POST /expenses/` - Create new expense (with auto-categorization)
- `GET /expenses/` - List expenses (with filtering)
- `GET /expenses/{id}` - Get specific expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense
- `POST /expenses/webhook` - Webhook for n8n integration
- `POST /expenses/recategorize` - Bulk recategorize uncategorized expenses
- `GET /expenses/analytics/summary` - Get expense analytics

#### Categories
- `POST /categories/` - Create new category
- `GET /categories/` - List all categories
- `GET /categories/{id}` - Get specific category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

#### Merchant Rules
- `POST /merchant-rules/` - Create new merchant rule
- `GET /merchant-rules/` - List merchant rules
- `GET /merchant-rules/{id}` - Get specific rule
- `PUT /merchant-rules/{id}` - Update rule
- `DELETE /merchant-rules/{id}` - Delete rule
- `POST /merchant-rules/test-rule` - Test a rule pattern

### Authentication

All API endpoints (except documentation) require authentication using an API key:

- **Header**: `x-api-key`
- **Environment Variable**: `API_KEY`
- **Example**: `curl -H "x-api-key: your-secret-api-key" http://localhost:8000/expenses/`

> ⚠️ **Security Note**: Update the `API_KEY` in `docker-compose.yml` before deploying to production.

## Quick Start

### Option 1: Docker (Recommended for Local Development) 🐳

**Prerequisites:**
- Docker and Docker Compose installed

**Start with one command:**
```bash
# Make the helper script executable (first time only)
chmod +x docker-dev.sh

# Start the entire stack (API + PostgreSQL)
./docker-dev.sh start
```

**That's it!** The API will be available at:
- **API:** `http://localhost:8000`
- **Documentation:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

**Useful Docker commands:**
```bash
./docker-dev.sh status    # Check container status
./docker-dev.sh logs      # View API logs
./docker-dev.sh shell     # Open shell in API container
./docker-dev.sh db-shell  # Open PostgreSQL shell
./docker-dev.sh pgadmin   # Start with pgAdmin (http://localhost:8080)
./docker-dev.sh help      # See all available commands
```

### Option 2: Local Python Installation

**Prerequisites:**
- Python 3.8+
- PostgreSQL database
- pip or conda

**Installation:**

1. **Clone and setup the project:**
```bash
cd expense-tracker
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
# Copy the example and edit with your database credentials
cp .env.example .env
# Edit .env with your PostgreSQL connection details
```

3. **Initialize the database:**
```bash
cd app
python init_db.py
```

4. **Start the API server:**
```bash
cd app
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Cloud Deployment

### Render (Recommended)

Deploy to Render cloud platform with PostgreSQL database:

```bash
# Simple deployment - just push to GitHub and follow the guide
git add .
git commit -m "Initial expense tracker implementation"
git push origin main
```

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete Render deployment guide.**

Quick Render setup:
1. Create PostgreSQL database on Render
2. Create web service connected to your repo
3. Set environment variables: `DATABASE_URL`, `ENVIRONMENT=production`
4. Deploy with command: `python start.py`

## Docker Development Environment 🐳

The project includes a complete Docker setup for local development with PostgreSQL database.

### Docker Stack
- **FastAPI API** (Python 3.11-slim)
- **PostgreSQL 15** (Alpine)
- **pgAdmin 4** (Optional database management tool)

### Docker Files
- `Dockerfile` - Multi-stage build for the FastAPI application
- `docker-compose.yml` - Complete development stack
- `docker-dev.sh` - Helper script with common commands
- `.dockerignore` - Excludes unnecessary files from build

### Quick Docker Commands

```bash
# Essential commands
./docker-dev.sh start      # Start all services
./docker-dev.sh stop       # Stop all services
./docker-dev.sh status     # Check status
./docker-dev.sh logs       # View API logs

# Development commands
./docker-dev.sh build      # Build API image
./docker-dev.sh rebuild    # Rebuild from scratch
./docker-dev.sh restart    # Restart services
./docker-dev.sh shell      # Enter API container

# Database commands
./docker-dev.sh db-shell   # PostgreSQL shell
./docker-dev.sh db-logs    # Database logs
./docker-dev.sh pgadmin    # Start with pgAdmin

# Maintenance commands
./docker-dev.sh clean      # Remove containers/volumes
./docker-dev.sh reset      # Full reset + rebuild
./docker-dev.sh test       # Run tests
```

### Container Details

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| API | expense-tracker-api | 8000 | FastAPI application |
| Database | expense-tracker-db | 5432 | PostgreSQL database |
| pgAdmin | expense-tracker-pgadmin | 8080 | Database management |

**Database Connection:**
- Host: `postgres` (within Docker network)
- Database: `expense_tracker`
- User: `expense_user`
- Password: `expense_password`

**pgAdmin Access:**
- URL: `http://localhost:8080`
- Email: `admin@expense-tracker.local`
- Password: `admin`

### Example Usage

1. **Create categories (or use defaults):**
```bash
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Groceries", "description": "Food shopping", "color": "#FF6B6B"}'
```

2. **Create merchant rules for auto-categorization:**
```bash
curl -X POST "http://localhost:8000/merchant-rules/" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_pattern": "walmart",
    "category_id": 1,
    "is_regex": false,
    "priority": 1
  }'
```

3. **Add an expense (will auto-categorize):**
```bash
curl -X POST "http://localhost:8000/expenses/" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 45.67,
    "merchant": "Walmart Supercenter",
    "description": "Weekly groceries",
    "transaction_date": "2024-01-15T10:30:00"
  }'
```

## Database Schema

### Categories
- id, name, description, color
- created_at, updated_at

### Expenses  
- id, amount, merchant, description, transaction_date
- category_id (FK), source_email, raw_data
- auto_categorized, confidence_score
- created_at, updated_at

### MerchantRules
- id, merchant_pattern, category_id (FK)
- is_regex, priority, is_active
- created_at, updated_at

## Categorization System

The system uses a sophisticated categorization approach:

1. **Priority-based**: Rules with higher priority are checked first
2. **Fuzzy Matching**: Uses fuzzy string matching for merchant names
3. **Regex Support**: Advanced users can create regex patterns
4. **Confidence Scoring**: Each auto-categorization includes a confidence score
5. **Bulk Recategorization**: Re-run categorization on uncategorized expenses

## Next Steps

### Iteration 2: n8n Integration
- Set up email parsing workflows in n8n
- Configure bank email templates
- Use webhook endpoint for automated expense creation

### Iteration 3: MCP for LM Studio
- Implement Model Context Protocol server
- Create analytics and insight endpoints
- Connect with LM Studio for AI-powered expense analysis

## Development

### Project Structure
```
app/
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── init_db.py          # Database initialization
├── routers/             # API route handlers
│   ├── expenses.py
│   ├── categories.py
│   └── merchant_rules.py
└── services/            # Business logic
    └── categorization.py
```

### Running Tests
```bash
cd app
pytest
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Contributing

Follow SOLID and DRY principles when contributing to this project. Ensure all new features include appropriate tests and documentation. 