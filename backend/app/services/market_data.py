"""
Market Data Service
Fetches stock data from B3 using yfinance
"""

import yfinance as yf
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service to fetch market data for Brazilian stocks"""
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
    
    def get_ticker_data(self, ticker: str) -> Optional[Dict]:
        """Get complete market data for a ticker"""
        try:
            # Brazilian stocks need .SA suffix
            ticker_b3 = ticker if '.SA' in ticker.upper() else f"{ticker}.SA"
            
            # Return cached data if available
            if ticker_b3 in self.cache:
                cached_data, timestamp = self.cache[ticker_b3]
                return cached_data
            
            # Fetch from yfinance
            logger.info(f"Fetching market data: {ticker_b3}")
            stock = yf.Ticker(ticker_b3)
            
            # Get last 30 days
            hist = stock.history(period="1mo")
            
            if hist.empty:
                logger.error(f"No data found for {ticker_b3}")
                return None
            
            info = stock.info
            
            # Calculate average daily liquidity (last 20 days)
            avg_volume = hist['Volume'].tail(20).mean()
            avg_price = hist['Close'].tail(20).mean()
            daily_liquidity = avg_volume * avg_price
            
            # Current price
            current_price = hist['Close'].iloc[-1]
            
            # Build response
            data = {
                'ticker': ticker,
                'ticker_b3': ticker_b3,
                'current_price': float(current_price),
                'average_daily_volume': float(avg_volume),
                'daily_liquidity': float(daily_liquidity),
                'open_price': float(hist['Open'].iloc[-1]),
                'high_price': float(hist['High'].iloc[-1]),
                'low_price': float(hist['Low'].iloc[-1]),
                'change_percent': float(((current_price / hist['Close'].iloc[-2]) - 1) * 100) if len(hist) > 1 else 0,
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
            }
            
            # Cache it
            self.cache[ticker_b3] = (data, None)
            
            logger.info(f"Data fetched: {ticker_b3} - Liquidity: R$ {daily_liquidity:,.2f}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {str(e)}")
            return None
    
    def get_daily_liquidity(self, ticker: str) -> Optional[float]:
        """Get only liquidity value"""
        data = self.get_ticker_data(ticker)
        return data['daily_liquidity'] if data else None
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get only current price"""
        data = self.get_ticker_data(ticker)
        return data['current_price'] if data else None
    
    def clear_cache(self):
        """Clear cached data"""
        self.cache.clear()
        logger.info("Cache cleared")