from typing import Any, Dict
from utils.mt5_client import mt5
from utils.mappings.order_type_mapping import ORDER_TYPE_MAP
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def calculate_profit(
    order_type: str,
    symbol: str,
    volume: float,
    price_open: float,
    price_close: float
) -> Dict[str, Any]:
    """
    Calculate profit for a given trade.

    Determines the estimated P/L for a completed trade using MetaTrader 5's profit calculator.

    Parameters:
        order_type : str
            "BUY" or "SELL".
        symbol : str
            Trading symbol (e.g., 'EURUSD').
        volume : float
            Trade volume in lots.
        price_open : float
            Entry price.
        price_close : float
            Exit price.

    Returns:
        dict:
            - status (str):  
                "success" if calculation completed; otherwise "error".
            - message (str):  
                Details about the calculation outcome.
            - data (dict):  
                - profit (float|None):  
                    Calculated profit or None on failure.
    """
    logger.info(f"Calculating profit for order_type: {order_type} symbol: {symbol} volume: {volume} price_open: {price_open} price_close: {price_close}")
    
    if(price_open <= 0 or price_close <= 0 or volume <= 0):
        logger.error(f"Price or volume is not valid: price_open: {price_open} price_close: {price_close} volume: {volume}")
        return {
            "status": "error",
            "message": f"Price or volume is not valid: price_open: {price_open} price_close: {price_close} volume: {volume}",
            "data": {
                "profit": None
            }
        }

    if order_type not in ORDER_TYPE_MAP:
        logger.error(f"Invalid order type: {order_type}")
        return {
            "status": "error",
            "message": f"Invalid order type: {order_type}",
            "data": {
                "profit": None
            }
        }
    
    if not mt5.symbol_select(symbol, True):
        logger.error(f"Failed to select symbol: {symbol}")
        return {
            "status": "error",
            "message": f"Failed to select symbol: {symbol}",
            "data": {
                "profit": None
            }
        }
    
    order_code = ORDER_TYPE_MAP[order_type]
    profit = mt5.order_calc_profit(order_code, symbol, volume, price_open, price_close)
    
    if profit is None:
        logger.error(f"Error calculating profit: {mt5.last_error()}")
        return {
            "status": "error",
            "message": f"Error calculating profit: {mt5.last_error()}",
            "data": {
                "profit": None
            }
        }

    logger.info(f"Profit calculated successfully for {symbol}: {profit}")

    result = {
        "status": "success",
        "message": f"Profit calculated successfully for {symbol}",
        "data": {
            "profit": profit
        }
    }
    
    return result
