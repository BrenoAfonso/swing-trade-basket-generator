"""
FastAPI Main Application
Swing Trade Basket Generator API
Author: Breno Afonso
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import logging
from pathlib import Path
import io

from .models import TradeInput, BasketOutput, Client, TechnicalValidation
from .services.market_data import MarketDataService
from .services.trade_validator import TradeValidator
from .services.basket_calculator import BasketCalculator
from .services.excel_generator import ExcelGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Swing Trade Basket Generator",
    description="Automates order basket generation with technical validation",
    version="1.0.0"
)

# CORS configuration (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
market_service = MarketDataService()
trade_validator = TradeValidator(market_service)
basket_calculator = BasketCalculator()
excel_generator = ExcelGenerator(output_dir="./output")

# Ensure output directory exists
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Swing Trade Basket Generator",
        "version": "1.0.0",
        "author": "Breno Afonso"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/validate-trade", response_model=TechnicalValidation)
async def validate_trade(trade: TradeInput):
    """
    Validate trade against 4 internal rules
    
    Checks: liquidity, stop loss %, risk/reward, max quantity
    """
    try:
        logger.info(f"Validating trade: {trade.ticker}")
        result = trade_validator.validate_trade(trade)
        return result
    except Exception as e:
        logger.error(f"Error validating trade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-data/{ticker}")
async def get_market_data(ticker: str):
    """Get market data for a ticker from B3"""
    try:
        logger.info(f"Fetching market data: {ticker}")
        data = market_service.get_ticker_data(ticker)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"Market data not found for {ticker}"
            )
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/gerar-basket", response_model=BasketOutput)
async def gerar_basket(trade: TradeInput, clientes_file: UploadFile = File(...)):
    """
    Generate complete order basket
    
    Process:
    1. Validate trade technically
    2. Read client file (CSV)
    3. Filter eligible clients
    4. Calculate quantities
    5. Generate Excel for brokerage
    """
    try:
        logger.info(f"Generating basket for {trade.ticker}")
        
        # Validate trade
        validation = trade_validator.validate_trade(trade)
        
        if not validation.valid:
            return BasketOutput(
                trade_valid=False,
                technical_validation=validation,
                orders=[],
                total_clients=0,
                total_orders=0,
                total_invested_amount=0,
                summary={}
            )
        
        # Read client file
        content = await clientes_file.read()
        
        if clientes_file.filename.endswith('.csv'):
            df_clients = pd.read_csv(io.BytesIO(content))
        else:
            df_clients = pd.read_excel(io.BytesIO(content))
        
        logger.info(f"Clients loaded: {len(df_clients)}")
        
        # Convert DataFrame to client objects
        clients = []
        for _, row in df_clients.iterrows():
            try:
                client = Client(
                    account_number=str(row['NUMERO_CONTA']),
                    equity_advisor=str(row.get('ASSESSOR RV', '')),
                    advisor=str(row.get('ADVISOR', '')),
                    client_name=str(row['CLIENTE']),
                    strategy=str(row.get('ESTRATÉGIA', '')),
                    net_total=float(row['NET TOTAL']),
                    net_available=float(row.get('NET DISPONÍVEL', row['NET TOTAL'])),
                    average_operation_value=float(row.get('VALOR MEDIO POR OPERAÇÃO', 0))
                )
                clients.append(client)
            except Exception as e:
                logger.warning(f"Error processing client at row {_}: {str(e)}")
                continue
        
        # Filter eligible clients
        eligible_clients, messages = basket_calculator.filter_eligible_clients(clients)
        logger.info(f"Eligible: {len(eligible_clients)}/{len(clients)}")
        
        # Generate orders
        orders = basket_calculator.generate_basket(trade, eligible_clients, validation)
        
        # Generate Excel
        if orders:
            excel_path = excel_generator.generate_excel(orders, trade.ticker)
            logger.info(f"Excel generated: {excel_path}")
        
        # Calculate summary
        summary = basket_calculator.calculate_summary(orders)
        
        return BasketOutput(
            trade_valid=True,
            technical_validation=validation,
            orders=orders,
            total_clients=len(clients),
            total_orders=len(orders),
            total_invested_amount=summary['total_invested'],
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error generating basket: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download-excel/{ticker}")
async def download_excel(ticker: str):
    """Download most recent Excel file for ticker"""
    try:
        # Find most recent file
        files = list(OUTPUT_DIR.glob(f"basket_{ticker}_*.xlsx"))
        
        if not files:
            raise HTTPException(
                status_code=404,
                detail=f"No Excel file found for {ticker}"
            )
        
        # Get most recent by modification time
        most_recent = max(files, key=lambda p: p.stat().st_mtime)
        
        return FileResponse(
            path=most_recent,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=most_recent.name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cache/clear")
async def clear_cache():
    """Clear market data cache"""
    try:
        market_service.clear_cache()
        return {"message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)