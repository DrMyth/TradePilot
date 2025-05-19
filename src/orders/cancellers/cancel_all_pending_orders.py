from orders.fetchers.fetch_pending_orders import fetch_pending_orders
from utils.mcp_client import mcp
from utils.logger import logger
from orders.cancellers.cancel_pending_order_by_id import cancel_pending_order_by_id
from typing import Dict, Any

@mcp.tool()
def cancel_all_pending_orders() -> Dict[str, Any]:
    """
    Cancel all currently pending MT5 orders.

    Retrieves all pending orders via `fetch_pending_orders` and issues a cancel
    request for each, logging progress and errors.

    Returns:
        dict:
            - status (str):
                'success' if operation completed; 'error' on failure.
            - message (str):
                Summary of how many pending orders were cancelled or error details.
    """
    logger.info("Cancelling all pending orders")

    try: 
        pending_orders = fetch_pending_orders()
        logger.info(f"Found {len(pending_orders['data']['pending_orders'])} pending orders")
    except Exception as e:
        msg = f"Error fetching pending orders: {e}"
        logger.error(msg)
        return {"status": "error", "message": msg}
    
    if not pending_orders["data"]["pending_orders"]:
        msg = "No pending orders found"
        logger.info(msg)
        return {"status": "success", "message": msg}
    
    pending_orders = pending_orders["data"]["pending_orders"]

    cancel_count = 0    

    for order in pending_orders:
        try:
            cancel_pending_order_by_id(order["ticket"])
            cancel_count += 1
        except Exception as e:
            msg = f"Error cancelling order {order['ticket']}: {e}"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
    return {"status": "success", "message": f"Cancelled {cancel_count} pending orders successfully!"}