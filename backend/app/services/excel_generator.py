"""
Excel Generator Service
Generates order basket files in brokerage platform format
"""

from typing import List
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
from ..models import ClientOrder

logger = logging.getLogger(__name__)


class ExcelGenerator:
    """
    Generates Excel files in brokerage format
    
    The brokerage requires exactly 16 columns in specific order.
    Empty columns must remain blank (not null, not zero).
    """
    
    # Brokerage required columns (exact order)
    COLUMNS = [
        'NUMERO_CONTA', 'VALIDADE_PUSH', 'VALIDADE_ORDEM', 'ATIVO', 'ESTRATEGIA', 
        'DIRECAO', 'QUANTIDADE', 'QUANTIDADE_APARENTE', 'QUANTIDADE_MINIMA', 
        'TIPO_PRECO', 'PRECO_LIMITE', 'TIPO_DISPARO', 'PRECO_DISPARO_CIMA', 
        'PRECO_LIMITE_CIMA', 'PRECO_DISPARO_BAIXO', 'PRECO_LIMITE_BAIXO'
    ]
    
    def __init__(self, output_dir: str = "./output"):
        """Initialize generator and create output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Excel output directory: {self.output_dir}")
    
    def order_to_dict(self, order: ClientOrder) -> dict:
        """Convert order to brokerage dictionary format"""
        return {
            'NUMERO_CONTA': order.account_number,
            'VALIDADE_PUSH': order.push_validity,
            'VALIDADE_ORDEM': order.order_validity,
            'ATIVO': order.ticker,
            'ESTRATEGIA': order.strategy,
            'DIRECAO': order.direction,
            'QUANTIDADE': order.quantity,
            'QUANTIDADE_APARENTE': order.apparent_quantity,
            'QUANTIDADE_MINIMA': order.minimum_quantity,
            'TIPO_PRECO': order.price_type,
            'PRECO_LIMITE': order.limit_price,
            'TIPO_DISPARO': order.trigger_type,
            'PRECO_DISPARO_CIMA': order.upper_trigger_price,
            'PRECO_LIMITE_CIMA': order.upper_limit_price,
            'PRECO_DISPARO_BAIXO': order.lower_trigger_price,
            'PRECO_LIMITE_BAIXO': order.lower_limit_price
        }
    
    def generate_excel(self, orders: List[ClientOrder], ticker: str) -> str:
        """Generate Excel file ready for brokerage upload"""
        if not orders:
            raise ValueError("Cannot generate Excel: no orders provided")
        
        # Convert orders to dictionaries
        data = [self.order_to_dict(order) for order in orders]
        df = pd.DataFrame(data, columns=self.COLUMNS)
        
        # Keep empty columns as blank strings (brokerage requirement)
        empty_columns = [
            'QUANTIDADE_APARENTE', 'QUANTIDADE_MINIMA', 'TIPO_DISPARO',
            'PRECO_DISPARO_CIMA', 'PRECO_LIMITE_CIMA', 
            'PRECO_DISPARO_BAIXO', 'PRECO_LIMITE_BAIXO'
        ]
        for col in empty_columns:
            df[col] = df[col].fillna('')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"basket_{ticker}_{timestamp}.xlsx"
        filepath = self.output_dir / filename
        
        # Save Excel
        df.to_excel(filepath, index=False, engine='openpyxl')
        logger.info(f"Excel generated: {filepath} ({len(orders)} orders)")
        
        return str(filepath)
    
    def generate_preview_csv(self, orders: List[ClientOrder]) -> str:
        """Generate CSV preview (lighter than Excel, useful for debugging)"""
        data = [self.order_to_dict(order) for order in orders]
        df = pd.DataFrame(data, columns=self.COLUMNS)
        return df.to_csv(index=False)
    
    def validate_format(self, filepath: str) -> bool:
        """Check if Excel file has correct format"""
        try:
            df = pd.read_excel(filepath)
            
            # Check columns match
            if list(df.columns) != self.COLUMNS:
                logger.error(f"Invalid columns: {list(df.columns)}")
                return False
            
            # Check has data
            if len(df) == 0:
                logger.error("Excel file is empty")
                return False
            
            logger.info(f"Excel valid: {len(df)} rows")
            return True
            
        except Exception as e:
            logger.error(f"Error validating Excel: {str(e)}")
            return False