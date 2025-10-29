"""
Basket Calculator Service
Calculates order quantities for eligible clients
"""

from typing import List, Tuple
import logging
from ..models import TradeInput, Client, ClientOrder, TechnicalValidation

logger = logging.getLogger(__name__)


class BasketCalculator:
    """
    Calculates order basket for eligible clients
    
    Rules:
    1. Client needs minimum R$ 20k allocated
    2. Each entry uses 50% of capital
    3. Never leave account negative (round down)
    """
    
    # Business rules
    MIN_NET_TOTAL = 20_000
    CAPITAL_PERCENT_PER_OPERATION = 0.50
    
    def __init__(self):
        """Initialize calculator"""
        pass
    
    def filter_eligible_clients(self, clients: List[Client]) -> Tuple[List[Client], List[str]]:
        """Filter which clients can participate in this trade"""
        eligible = []
        messages = []
        
        for client in clients:
            # Check minimum allocation
            if client.net_total < self.MIN_NET_TOTAL:
                messages.append(
                    f"❌ {client.client_name} ({client.account_number}): "
                    f"Insufficient net total R$ {client.net_total:,.2f} "
                    f"(minimum: R$ {self.MIN_NET_TOTAL:,.2f})"
                )
                continue
            
            # Check if has enough balance (needs 50% of net total)
            required_amount = client.net_total * self.CAPITAL_PERCENT_PER_OPERATION
            if client.net_available < required_amount:
                messages.append(
                    f"❌ {client.client_name} ({client.account_number}): "
                    f"Insufficient balance R$ {client.net_available:,.2f} "
                    f"(needs: R$ {required_amount:,.2f})"
                )
                continue
            
            # Client approved
            eligible.append(client)
            messages.append(
                f"✅ {client.client_name} ({client.account_number}): "
                f"Eligible - R$ {required_amount:,.2f} available"
            )
        
        logger.info(f"Eligible clients: {len(eligible)}/{len(clients)}")
        return eligible, messages
    
    def calculate_share_quantity(self, client: Client, entry_price: float,
                                  max_quantity: int) -> Tuple[int, float]:
        """Calculate how many shares client should buy"""
        
        # Use 50% of allocated capital
        available_capital = client.net_total * self.CAPITAL_PERCENT_PER_OPERATION
        
        # Calculate quantity (int automatically rounds down)
        ideal_quantity = int(available_capital / entry_price)
        
        # Apply volume limit from validator
        final_quantity = min(ideal_quantity, max_quantity)
        
        # Calculate real invested amount
        invested_amount = final_quantity * entry_price
        
        # Safety check - never exceed available balance
        if invested_amount > client.net_available:
            final_quantity = int(client.net_available / entry_price)
            invested_amount = final_quantity * entry_price
        
        logger.debug(f"Client {client.account_number}: {final_quantity} shares (R$ {invested_amount:,.2f})")
        
        return final_quantity, invested_amount
    
    def generate_basket(self, trade: TradeInput, clients: List[Client],
                        validation: TechnicalValidation) -> List[ClientOrder]:
        """Generate order basket for all eligible clients"""
        orders = []
        
        for client in clients:
            quantity, invested_amount = self.calculate_share_quantity(
                client,
                trade.entry_price,
                validation.max_quantity
            )
            
            if quantity == 0:
                logger.warning(f"Zero quantity for {client.account_number} - skipping")
                continue
            
            # Create order in brokerage format
            order = ClientOrder(
                account_number=client.account_number,
                ticker=trade.ticker,
                quantity=quantity,
                price_type="l",  # limit order
                limit_price=trade.entry_price,
                client_name=client.client_name,
                invested_amount=invested_amount
            )
            
            orders.append(order)
        
        logger.info(f"Basket generated: {len(orders)} orders")
        return orders
    
    def calculate_summary(self, orders: List[ClientOrder]) -> dict:
        """Calculate basket statistics"""
        if not orders:
            return {
                'total_orders': 0,
                'total_shares': 0,
                'total_invested': 0,
                'average_investment': 0,
                'min_investment': 0,
                'max_investment': 0
            }
        
        amounts = [order.invested_amount for order in orders if order.invested_amount]
        
        return {
            'total_orders': len(orders),
            'total_shares': sum(order.quantity for order in orders),
            'total_invested': sum(amounts),
            'average_investment': sum(amounts) / len(amounts),
            'min_investment': min(amounts),
            'max_investment': max(amounts)
        }
    