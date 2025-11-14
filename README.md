# Swing Trade Basket Generator 

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat&logo=docker)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)


Automated order basket generation system for swing trading operations 
with technical validation and risk management.

## The Problem

In equity trading desks, generating order baskets for swing trade strategies 
is a manual, time-consuming process prone to errors. Each operation 
takes 20-30 minutes, involving:
- Manual validation against 4 internal technical rules
- Checking client eligibility and available capital
- Calculating share quantities for each client
- Formatting orders in brokerage-specific Excel format

> This system **automates the entire workflow**, reducing processing time by 85% and eliminating calculation errors.

## Key Features

### Technical Validation
Automated validation against 4 trading desk rules:
1. **Daily Liquidity:** Minimum R$ 30 million
2. **Stop Loss:** Maximum 8% 
3. **Risk/Reward Ratio:** Minimum 1:1.33
4. **Position Size:** Maximum 1% of daily volume

### Client Management
- Filters eligible clients based on allocated capital (min R$ 20k)
- Calculates share quantities (50% of allocated capital)
- Ensures account never goes negative (safety-first)
- Handles multiple clients simultaneously

### Excel Export
- Generates brokerage-ready Excel files (16-column format)
- Automatic quantity calculation per client
- Ready for immediate platform upload

### Market Dada
- Real-time market data from B3 (Brazilian Stock Exchange)
- Automatic ticker validation
- Price and volume tracking 


## Quick Start 
### Using Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/BrenoAfonso/swing-trade-basket-generator.git
cd swing-trade-basket-generator

# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop environment
docker-compose down
```

### Local Installation
```bash
# Clone the repository
git clone https://github.com/BrenoAfonso/swing-trade-basket-generator.git
cd swing-trade-basket-generator

# Create and activate virtual environment
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload
```

### Access Points

- **API:** http://localhost:8000
- **Interactive API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc


## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI 
- Pandas 
- yfinance 
- Pydantic 
- openpyxl 

**DevOps:**
- Docker (multi-stage builds)
- Docker Compose 
- Non-root container execution
- Health checks

## API Usage

### Health Check
```http
GET /
```

### Validate Trade
Test if a trade meets technical criteria:
```json
POST /api/validate-trade
{
  "ticker": "PETR4",
  "entry_price": 35.00,
  "stop_loss": 32.90,
  "target": 40.00
}
```

### Get Market Data
```http
GET /api/market-data/{ticker}
```

### Generate Basket
Generate complete basket with client data.
```http
POST /api/gerar-basket
```

**Form Data:**
- `trade`: JSON with trade details
- `clientes_file`: Excel/CSV with client data

**Required columns in client file:**
```
NUMERO_CONTA | ASSESSOR RV | ADVISOR | CLIENTE | ESTRATÉGIA | 
NET TOTAL | NET DISPONÍVEL | VALOR MEDIO POR OPERAÇÃO
```

### Download Excel Basket
```
GET /api/download-excel/{ticker}
```

Excel file ready for brokerage platform upload.

## Project Structure

```
swing-trade-basket-generator/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── basket_calculator.py
│   │   │   ├── excel_generator.py
│   │   │   ├── market_data.py
│   │   │   └── trade_validator.py
│   │   ├── utils/
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── main.py                     
│   │   └── models.py
│   ├── output/                         # Generated Excel files
│   ├── .dockerignore
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                               # Generated Excel files
├── frontend/                           # For future frontend implementation
├── .gitignore
├── docker-compose.prod.yml
├── docker-compose.yml
└── README.md        
```

## 🐳 Docker

### Architecture

This project uses **Docker multi-stage builds** for optimized images:

**Benefits:**
- **Smaller images:** ~400MB vs ~720MB (44% reduction)
- **Enhanced security:** Non-root user, minimal attack surface
- **Faster builds:** Optimized layer caching
- **Production-ready:** Health checks and resource limits

### Docker Commands

#### Development Environment
```bash
# Start containers
docker-compose up -d

# View logs in real-time
docker-compose logs -f api

# Restart containers
docker-compose restart api

# Stop containers
docker-compose down

# Open shell in container
docker-compose exec api /bin/bash
```

#### Production Environment
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f api

# Stop production environment
docker-compose -f docker-compose.prod.yml down
```
### Development vs Production

**Development:** Hot-reload enabled, source code mounted  
**Production:** Resource limits, always restart, no code mounting


## How It Works 
### Technical Rules Validation
Implements a 4-rule validation system ensuring only high-quality trades are executed

### Client Allocation Logic
- Filters clients based on available capital
- Calculates share quantities using 50% allocation rule
- Applies volume limits (1% of daily volume)
- Prevents negative balances

### Excel Generator
Produces Excel files in exact brokerage format (16 columns) ready for immediate upload


## Business Impact

**Before Automation:**
- 20-30 minutes per operation
- Manual calculations prone to errors
- Risk of account overdrafts

**After Automation:**
- ~2 minutes per operation (**88% reduction**)
- Automated validation and calculations
- Zero overdraft risk 
- Complete audit trail

---
### Testing
### Quick Test
```bash
# Start the API
docker-compose up -d

# Health check
curl http://localhost:8000/

# Should return: {"message":"Swing Trade Basket Generator API","status":"running"}

# Access interactive docs
open http://localhost:8000/docs
```


## Author

**Breno Afonso**

- Email: [bbasbreno@gmail.com](mailto:bbasbreno@gmail.com)
- LinkedIn: [linkedin.com/in/breno-afonso](https://linkedin.com/in/breno-afonso)
- GitHub: [@BrenoAfonso](https://github.com/BrenoAfonso)

## License

This project is licensed under the MIT [LICENSE](LICENSE) </br>
Project was originally developed to enhance efficiency and agility in daily trading desk operations.

---

## ⚠️ Disclaimer 
>This system is designed for professional trading environments and requires proper market data access and brokerage integration for production use. Use at your own risk in production environments. Always validate outputs before executing real trades.
