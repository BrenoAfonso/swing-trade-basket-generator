# Swing Trade Basket Generator 

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)


Automated order basket generation system for swing trading operations with technical validation and risk management.

## Problem Statement

In equity trading desks, generating order baskets for swing trade strategies is a manual, time-consuming process prone to errors. Each operation takes 20-30 minutes, involving:
- Manual validation against 4 internal technical rules
- Checking client eligibility and available capital
- Calculating share quantities for each client
- Formatting orders in brokerage-specific Excel format

This system automates the entire workflow, reducing processing time by 85% and eliminating calculation errors.

## Features

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

### Order Generation
- Generates brokerage-ready Excel files (16-column format)
- Automatic quantity calculation per client
- Real-time market data from B3 (Brazilian Stock Exchange)
- Complete audit trail with validation messages

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI (REST API)
- Pandas 
- yfinance 
- Pydantic 
- openpyxl 

## Getting Started

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. Clone the repository
```bash
git clone https://github.com/BrenoAfonso/swing-trade-basket-generator.git
cd swing-trade-basket-generator
```

2. Create and activate virtual environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn app.main:app --reload
```

Server will start at `http://127.0.0.1:8000`
Interactive API documentation: `http://127.0.0.1:8000/docs`

## Usage

### 1. Validate Trade

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

### 2. Generate Order Basket

Generate complete basket with client data:
```
POST /api/gerar-basket
- trade: {"ticker":"PETR4","entry_price":35,"stop_loss":32.9,"target":40}
- clientes_file: Upload Excel/CSV with client data
```

**Required columns in client file:**
```
NUMERO_CONTA | ASSESSOR RV | ADVISOR | CLIENTE | ESTRATÉGIA | 
NET TOTAL | NET DISPONÍVEL | VALOR MEDIO POR OPERAÇÃO
```

### 3. Download Generated Excel

```
GET /api/download-excel/{ticker}
```

Excel file ready for brokerage platform upload.

## Project Structure

```
swing-trade-basket-generator/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application
│   │   ├── models.py                # Data models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── basket_calculator.py # Order calculation
│   │   │   ├── excel_generator.py   # Excel generation
│   │   │   ├── market_data.py       # B3 data fetching
│   │   │   └── trade_validator.py   # Technical validation
│   │   └── utils/
│   │       └── __init__.py
│   ├── output/                     
│   ├── venv/                        
│   ├── requirements.txt             
│   └── testeclientes.xlsx           # Sample client data
├── docs/                            
├── frontend/                        
├── .gitignore                       
└── README.md                        
```

## Key Components

### Trade Validator
Implements a 4-rule validation system ensuring only high-quality trades are executed.

### Basket Calculator
- Filters clients based on available capital
- Calculates share quantities using 50% allocation rule
- Applies volume limits (1% of daily volume)
- Prevents negative balances

### Excel Generator
Produces Excel files in exact brokerage format (16 columns) ready for immediate upload.

## 🎓 Business Impact

**Before:**
- 20-30 minutes per operation
- Manual calculations prone to errors
- Risk of account overdrafts

**After:**
- ~2 minutes per operation (>88% reduction)
- Automated validation and calculations
- Zero overdraft risk 
- Complete audit trail

## Development

### API Endpoints

- `GET /` - Health check
- `POST /api/validate-trade` - Validate trade technical criteria
- `GET /api/market-data/{ticker}` - Fetch B3 market data
- `POST /api/gerar-basket` - Generate complete order basket
- `GET /api/download-excel/{ticker}` - Download generated Excel

### Testing

Access interactive documentation at `/docs` for testing all endpoints with visual interface.


## Author

**Breno Afonso**
[Email](mailto:bbasbreno@gmail.com) | [LinkedIn](https://linkedin.com/in/breno-afonso) |
[GitHub](https://github.com/BrenoAfonso)

- Building automation systems for professional trading desks  
- Prioritizing performance, reliability, and operational safety

## License

This project was originally developed to enhance efficiency and agility in daily trading desk operations.

---

**Note:** This system is designed for professional trading environments and requires proper market data access and brokerage integration for production use.