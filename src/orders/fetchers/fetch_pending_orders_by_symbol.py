from orders.fetchers.fetch_pending_orders import fetch_pending_orders
from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any

@mcp.tool()
def fetch_pending_orders_by_symbol(symbol: str) -> Dict[str, Any]:
    """
    Fetch all pending orders from MT5 for a specific trading symbol.

    This tool wraps the lower‑level `fetch_pending_orders` call, applying
    a symbol_name filter based on the provided symbol.

    Parameters:
        symbol (str):
            The exact trading symbol to match (e.g., 'EURUSDm').

    Returns:
        Dict[str, Any]:
            - status (str):
                "success" if orders were retrieved; otherwise "error".
            - message (str):
                Human‑readable description of the outcome.
            - data (dict):
                - pending_orders (List[Dict[str, Any]]):
                    The list of pending orders for the given symbol,
                    or an empty list if none.
    """
    logger.info(f"Getting pending order with symbol: {symbol}")

    if not isinstance(symbol, str) or not symbol.strip():
        logger.error(f"Invalid symbol provided: {symbol!r}")
        return {
            "status": "error",
            "message": f"Invalid symbol: {symbol!r}",
            "data": {"pending_orders": []}
        }
    
    try:
        response = fetch_pending_orders(symbol_name=symbol.strip())
        status = response.get("status")
        message = response.get("message", "")
        orders = response.get("data", {}).get("pending_orders", [])

        if status != "success":
            logger.error(f"fetch_pending_orders() failed for symbol={symbol}: {message}")
            return {
                "status": "error",
                "message": f"Failed to fetch pending orders for symbol '{symbol}': {message}",
                "data": {"pending_orders": []}
            }

        count = len(orders)
        logger.info(f"Fetched {count} pending order{'s' if count != 1 else ''} for symbol '{symbol}'.")
        
        return {
            "status": "success",
            "message": f"Pending orders for symbol '{symbol}' fetched successfully",
            "data": {"pending_orders": orders}
        }

    except Exception as exc:
        logger.error("Unexpected error in fetch_pending_orders_by_symbol()")
        return {
            "status": "error",
            "message": f"Unexpected error: {exc}",
            "data": {"pending_orders": []}
        }
