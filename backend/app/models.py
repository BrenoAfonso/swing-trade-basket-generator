"""
Data Models for Swing Trade Basket Generator
Author: Breno Afonso
Purpose: Automate swing trade order basket generation with technical validation

"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class TradeInput(BaseModel):
    """
    Trade call received from analyst
    
    Represents the entry signal with price levels:
    - Entry: limit price for buying
    - Stop Loss: risk management exit
    - Target: profit-taking exit
    """
    ticker: str = Field(..., description="Stock ticker (e.g., PETR4, VALE3)")
    entry_price: float = Field(..., gt=0, description="Entry limit price in BRL")
    stop_loss: float = Field(..., gt=0, description="Stop loss price in BRL")
    target: float = Field(..., gt=0, description="Target price in BRL")
    
    @validator('ticker')
    def validate_ticker(cls, v):
        """Ensure ticker is uppercase and not empty"""
        v = v.upper().strip()
        if not v:
            raise ValueError("Ticker cannot be empty")
        return v
    
    @validator('stop_loss')
    def validate_stop_loss(cls, v, values):
        """Stop loss must be below entry price (long position)"""
        if 'entry_price' in values and v >= values['entry_price']:
            raise ValueError("Stop loss must be below entry price for long positions")
        return v
    
    @validator('target')
    def validate_target(cls, v, values):
        """Target must be above entry price"""
        if 'entry_price' in values and v <= values['entry_price']:
            raise ValueError("Target must be above entry price")
        return v


class Client(BaseModel):
    """Client portfolio data from Google Sheets"""
    account_number: str
    equity_advisor: str
    advisor: str
    client_name: str
    strategy: str
    net_total: float  
    net_available: float  
    average_operation_value: float


class TechnicalValidation(BaseModel):
    """
    Internal 4 rules before execution:
    1. Liquidity > R$ 30M/day
    2. Stop loss < 8%
    3. Risk/Reward > 1:1.33
    4. Max position = 1% of daily volume
    """
    valid: bool
    daily_liquidity: float
    stop_loss_percent: float
    risk_reward_ratio: float
    max_quantity: int  # Max shares 1% volume rule
    messages: List[str] = []


class ClientOrder(BaseModel):
    """
    Exact 16-column format required by the brokerage.
    Empty fields must remain empty (not null, not zero).
    """
    account_number: str  
    push_validity: str = "hoje"  
    order_validity: str = "hoje"  
    ticker: str  # ATIVO
    strategy: str = "position"  
    direction: str = "compra"  # long position
    quantity: int  
    apparent_quantity: str = ""  
    minimum_quantity: str = ""  
    price_type: str  
    limit_price: float  
    trigger_type: str = ""  
    upper_trigger_price: str = ""  
    upper_limit_price: str = ""  
    lower_trigger_price: str = ""  
    lower_limit_price: str = ""  
    
    """ Internal control (not exported to Excel)"""
    client_name: Optional[str] = None
    invested_amount: Optional[float] = None


class BasketOutput(BaseModel):
    """Complete basket generation result """
    trade_valid: bool
    technical_validation: TechnicalValidation
    orders: List[ClientOrder]
    total_clients: int
    total_orders: int
    total_invested_amount: float
    summary: dict
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Standard API error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)