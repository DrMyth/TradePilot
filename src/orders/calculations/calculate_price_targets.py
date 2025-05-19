from typing import Any, Dict
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def calculate_price_targets(
    order_type: str,
    symbol: str,
    volume: float,
    entry_price: float,
    target: float
) -> Dict[str, Any]:
    """
    Estimate exit price or stop-loss for a desired profit/loss level.

    Calculates the price level needed to achieve a specified take-profit (TP)
    or stop-loss (SL) target, based on trade volume, entry price, and target
    P/L using MT5 contract specifications. This function can be used to
    compute both TP and SL price targets by passing a positive or negative 
    `target` value respectively.

    Parameters:
        order_type : str
            "BUY" or "SELL".
        symbol : str
            Trading symbol (e.g., 'EURUSD').
        volume : float
            Trade volume in lots (e.g., 0.1).
        entry_price : float
            Fill price of the trade.
        target : float
            DDesired profit (+) for TP or loss (–) for SL in account currency.

    Returns:
        dict:
            - status (str):  
                "success" if calculation succeeded; otherwise "error".
            - message (str):  
                Details about the outcome.
            - data (dict):  
                - price_target (float|None):  
                    Estimated exit price or None on failure.
    """
    logger.info(f"Calculating price targets for order_type: {order_type} symbol: {symbol} volume: {volume} entry_price: {entry_price} target: {target}")

    if(entry_price <= 0 or volume <= 0):
        logger.error(f"Price or volume is not valid: entry_price: {entry_price} volume: {volume}")
        return {
            "status": "error",
            "message": f"Price or volume is not valid: entry_price: {entry_price} volume: {volume}",
            "data": {
                "price_target": None
            }
        }
    
    order_type = order_type.upper()
    if order_type not in ("BUY", "SELL"):
        logger.error(f"Unsupported order type: {order_type}")
        return {
            "status": "error",
            "message": f"Unsupported order type: {order_type}",
            "data": {
                "price_target": None
            }
        }

    info = mt5.symbol_info(symbol)
    if not info or (not info.visible and not mt5.symbol_select(symbol, True)):
        logger.error(f"Symbol {symbol} not available")
        return {
            "status": "error",
            "message": f"Symbol {symbol} not available",
            "data": {
                "price_target": None
            }
        }

    contract_size = info.trade_contract_size
    logger.info(f"Contract Size: {contract_size}")  
    if contract_size <= 0:
        logger.error(f"Contract size for symbol {symbol} is not available")
        return {
            "status": "error",
            "message": f"Contract size for symbol {symbol} is not available",
            "data": {
                "price_target": None
            }
        }

    price_delta = target / (volume * contract_size)
    logger.info(f"Price Delta: {price_delta}")

    if order_type == "BUY":
        exit_price = entry_price + price_delta
    else:
        exit_price = entry_price - price_delta

    price_target = round(exit_price, info.digits)
    logger.info(f"Price Target: {price_target}")

    return {
        "status": "success",
        "message": f"Price targets calculated successfully for {symbol}",
        "data": {
            "price_target": price_target
        }
    }