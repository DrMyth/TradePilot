from orders.fetchers.fetch_pending_orders import fetch_pending_orders
from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any

@mcp.tool()
def fetch_all_pending_orders() -> Dict[str, Any]:
    """
    Fetch all currently pending orders from MT5.

    This tool wraps the lower‐level `fetch_pending_orders` call, handling
    error conditions and ensuring a consistent return schema.

    Returns:
        Dict[str, Any]:
            - status (str):
                "success" if orders were retrieved; otherwise "error".
            - message (str):
                Human‐readable description of the outcome.
            - data (dict):
                - pending_orders (List[Dict[str, Any]]):
                    The list of pending order records, or an empty list if none.
    """
    logger.info("Fetching all pending orders")

    try:
        response = fetch_pending_orders()
        status = response.get("status")
        message = response.get("message", "")
        orders = response.get("data", {}).get("pending_orders", [])

        if status != "success":
            logger.error(f"fetch_pending_orders() failed: {message}")
            return {
                "status": "error",
                "message": f"Failed to fetch pending orders: {message}",
                "data": {"pending_orders": []}
            }

        count = len(orders)
        logger.info(f"Fetched {count} pending order{'s' if count != 1 else ''}.")
        
        return {
            "status": "success",
            "message": "All pending orders fetched successfully",
            "data": {"pending_orders": orders}
        }

    except Exception as exc:
        logger.error("Unexpected error in fetch_all_pending_orders()")
        return {
            "status": "error",
            "message": f"Unexpected error: {exc}",
            "data": {"pending_orders": []}
        }