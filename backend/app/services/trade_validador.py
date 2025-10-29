"""
Trade Validator Service
Validates trades against internal trading desk rules (4 filter rule)

"""

from typing import Tuple
import logging
from ..models import TradeInput, TechnicalValidation
from .market_data import MarketDataService

logger = logging.getLogger(__name__)


class TradeValidator:
    """
    Validates if a trade meets internal technical criteria
    
    Internal Rules:
    1. Daily liquidity > R$ 30 million
    2. Stop loss < 8% 
    3. Risk/Reward ratio > 1:1.33
    4. Maximum quantity = 1% of daily volume
    
    If any rule fails, trade is REJECTED.
    """
    
    # INTERNAL RULES (can adjust if needed)
    MIN_LIQUIDITY = 30_000_000  # R$ 30M
    MAX_STOP_LOSS = 0.08  # 8%
    MIN_RISK_REWARD = 1.33  # 1:1.33
    MAX_VOLUME_PERCENT = 0.01  # 1% of daily volume
    
    def __init__(self, market_data_service: MarketDataService):
        """Initialize validator with market data service"""
        self.market_service = market_data_service
    
    def validate_trade(self, trade: TradeInput) -> TechnicalValidation:
        """Validate trade against all 4 rules"""
        messages = []
        valid = True
        
        # Fetch market data
        market_data = self.market_service.get_ticker_data(trade.ticker)
        
        if not market_data:
            return TechnicalValidation(
                valid=False,
                daily_liquidity=0,
                stop_loss_percent=0,
                risk_reward_ratio=0,
                max_quantity=0,
                messages=[f"❌ Could not fetch market data for {trade.ticker}"]
            )
        
        daily_liquidity = market_data['daily_liquidity']
        avg_volume = market_data['average_daily_volume']
        
        # RULE 1: Daily Liquidity
        if daily_liquidity < self.MIN_LIQUIDITY:
            valid = False
            messages.append(
                f"❌ Insufficient daily liquidity: R$ {daily_liquidity:,.2f} "
                f"(minimum required: R$ {self.MIN_LIQUIDITY:,.2f})"
            )
        else:
            messages.append(
                f"✅ Daily liquidity OK: R$ {daily_liquidity:,.2f}"
            )
        
        # RULE 2: Stop Loss Percentage
        stop_loss_percent = abs((trade.stop_loss - trade.entry_price) / trade.entry_price)
        
        if stop_loss_percent > self.MAX_STOP_LOSS:
            valid = False
            messages.append(
                f"❌ Stop loss too high: {stop_loss_percent:.2%} "
                f"(maximum allowed: {self.MAX_STOP_LOSS:.2%})"
            )
        else:
            messages.append(
                f"✅ Stop loss OK: {stop_loss_percent:.2%}"
            )
        
        # RULE 3: Risk/Reward Ratio
        risk = abs(trade.entry_price - trade.stop_loss)
        reward = abs(trade.target - trade.entry_price)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        if risk_reward_ratio < self.MIN_RISK_REWARD:
            valid = False
            messages.append(
                f"❌ Low Risk/Reward ratio: 1:{risk_reward_ratio:.2f} "
                f"(minimum required: 1:{self.MIN_RISK_REWARD:.2f})"
            )
        else:
            messages.append(
                f"✅ Risk/Reward ratio OK: 1:{risk_reward_ratio:.2f}"
            )
        
        # RULE 4: Maximum Quantity (1% of volume)
        max_quantity = int(avg_volume * self.MAX_VOLUME_PERCENT)
        messages.append(
            f"ℹ️ Maximum quantity per operation: {max_quantity:,} shares "
            f"({self.MAX_VOLUME_PERCENT:.1%} of daily volume)"
        )
        
        # Final
        if valid:
            messages.insert(0, f"✅ Trade APPROVED for {trade.ticker}")
        else:
            messages.insert(0, f"❌ Trade REJECTED for {trade.ticker}")
        
        return TechnicalValidation(
            valid=valid,
            daily_liquidity=daily_liquidity,
            stop_loss_percent=stop_loss_percent,
            risk_reward_ratio=risk_reward_ratio,
            max_quantity=max_quantity,
            messages=messages
        )
    
    def quick_validate(self, ticker: str, entry_price: float, 
                       stop_loss: float, target: float) -> Tuple[bool, str]:
        """Quick validation"""
        try:
            trade = TradeInput(
                ticker=ticker,
                entry_price=entry_price,
                stop_loss=stop_loss,
                target=target
            )
            result = self.validate_trade(trade)
            return result.valid, "\n".join(result.messages)
        except Exception as e:
            return False, f"Validation error: {str(e)}"