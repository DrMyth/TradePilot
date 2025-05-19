from typing import Dict, Any
from utils.mt5_client import mt5
from utils.mappings.order_type_mapping import ORDER_TYPE_MAP
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def calculate_margin(order_type: str, symbol: str, volume: float, price: float) -> Dict[str, Any]:
    """
    Calculate the margin required to open a trade without placing the order.

    Estimates how much margin will be reserved if a trade of the given type, volume,
    and price is executed using MetaTrader 5's API.

    Parameters:
        order_type : str
            The type of order (e.g., 'BUY', 'SELL', 'BUY_LIMIT', etc.).
        symbol : str
            Financial instrument symbol (e.g., 'EURUSD').
        volume : float
            Trade volume in lots.
        price : float
            Intended open price.

    Returns:
        dict:
            - status (str):  "success" if calculation succeeded; otherwise "error".
            - message (str): Details about the operation outcome.
            - data (dict):
                - margin (float|None): Margin required in account currency, or None if failed.
    """
    logger.info(f"Calculating margin for order_type: {order_type} symbol: {symbol} volume: {volume} price: {price}")

    if(price <= 0 or volume <= 0):
        logger.error(f"Price or volume is not valid: price: {price} volume: {volume}")
        return {
            "status": "error",
            "message": f"Price or volume is not valid: price: {price} volume: {volume}",
            "data": {
                "margin": None
            }
        }
    
    mt5_order_type = ORDER_TYPE_MAP.get(order_type.upper())
    if mt5_order_type is None:
        logger.error(f"Unsupported order type: {order_type}")
        return {
            "status": "error",
            "message": f"Unsupported order type: {order_type}",
            "data": {
                "margin": None
            }
        }

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(f"Symbol '{symbol}' not found.")
        return {
            "status": "error",
            "message": f"Symbol '{symbol}' not found.",
            "data": {
                "margin": None
            }
        }

    if not symbol_info.visible:
        logger.info(f"Symbol '{symbol}' is not visible. Attempting to enable...")
        if not mt5.symbol_select(symbol, True):
            logger.error(f"Could not enable symbol '{symbol}'.")
            return {
                "status": "error",
                "message": f"Could not enable symbol '{symbol}'.",
                "data": {
                    "margin": None
                }
            }

    margin = mt5.order_calc_margin(mt5_order_type, symbol, volume, price)
    if margin is None:
        logger.error(f"Margin calculation failed for {symbol}. Error: {mt5.last_error()}")
        return {
            "status": "error",
            "message": f"Margin calculation failed for {symbol}. Error: {mt5.last_error()}",
            "data": {
                "margin": None
            }
        }

    result = {
        "status": "success",
        "message": f"Margin calculated successfully for {symbol}",
        "data": {
            "margin": margin
        }
    }   

    logger.info(f"Margin calculated successfully for {symbol}: {margin}")
    return result