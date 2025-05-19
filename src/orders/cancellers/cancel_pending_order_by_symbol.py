from typing import Any, Dict
from orders.fetchers.fetch_pending_orders import fetch_pending_orders
from orders.cancellers.cancel_order import cancel_order
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mt5_client import mt5

@mcp.tool()
def cancel_pending_order_by_symbol(symbol: str) -> Dict[str, Any]:
    """
    Cancel all MT5 pending orders for a specified symbol.

    Retrieves all pending orders matching the given symbol using `fetch_pending_orders`,
    cancels each by delegating to `cancel_order`, and logs the process.

    Parameters:
        symbol : str
            Trading instrument symbol (e.g., 'EURUSD'). Only pending orders with this
            symbol will be cancelled.

    Returns:
        dict:
            - status (str):
                'success' if the operation completed; 'error' on failure.
            - message (str):
                Summary of how many pending orders were cancelled or error details.
    """
    logger.info(f"Cancelling all pending orders for {symbol}")

    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        msg = f"Symbol {symbol} not found"
        logger.error(msg)
        return {"status": "error", "message": msg}

    try: 
        pending_orders = fetch_pending_orders(symbol_name=symbol)
        logger.info(f"Pending orders: {len(pending_orders['data']['pending_orders'])}")
    except Exception as e:
        msg = f"Error fetching pending orders: {e}"
        logger.error(msg)
        return {"status": "error", "message": msg}

    if not pending_orders["data"]["pending_orders"]:
        msg = f"No pending orders found for {symbol}"
        logger.info(msg)
        return {"status": "success", "message": msg}
    
    pending_orders = pending_orders["data"]["pending_orders"]
    
    cancel_count = 0
    for order in pending_orders:
        try:
            cancel_order(order["ticket"])
            cancel_count += 1
        except Exception as e:
            msg = f"Error cancelling pending order {order['ticket']}: {e}"
            logger.error(msg)
            return {"status": "error", "message": msg}

    msg = f"Cancelled {cancel_count} pending orders for {symbol} successfully!"
    logger.info(msg)
    return {"status": "success", "message": msg}