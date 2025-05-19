from orders.fetchers.fetch_pending_orders import fetch_pending_orders
from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any

@mcp.tool()
def fetch_pending_order_by_id(order_id: int) -> Dict[str, Any]:
    """
    Fetch a single pending order from MT5 by its ticket ID.

    This tool wraps the lower‑level `fetch_pending_orders` call, filtering
    on a specific order ticket. It ensures consistent response structure
    and logs errors or unexpected issues.

    Parameters:
        order_id (int):  
            The MT5 ticket ID of the pending order to retrieve.

    Returns:
        Dict[str, Any]:
            - status (str):
                "success" if the order was retrieved; otherwise "error".
            - message (str):
                Human‑readable description of the outcome.
            - data (dict):
                - pending_orders (List[Dict[str, Any]]):
                    A list containing the matching order record, or empty if none.
    """
    logger.info(f"Getting pending order with ID: {order_id}")

    if not isinstance(order_id, int) or order_id < 0:
        logger.error(f"Invalid order_id provided: {order_id!r}")
        return {
            "status": "error",
            "message": f"Invalid order_id: {order_id!r}",
            "data": {"pending_orders": []}
        }

    if len(str(order_id)) != 9:
        logger.error(f"Invalid order_id provided: {order_id!r}")
        return {
            "status": "error",
            "message": f"Invalid order_id: {order_id!r}",
            "data": {"pending_orders": []}
        }
    
    try:
        response = fetch_pending_orders(ticket=order_id)
        status = response.get("status")
        message = response.get("message", "")
        orders = response.get("data", {}).get("pending_orders", [])

        if status != "success":
            logger.error(f"fetch_pending_orders() failed for ticket={order_id}: {message}")
            return {
                "status": "error",
                "message": f"Failed to fetch pending order {order_id}: {message}",
                "data": {"pending_orders": []}
            }

        if not orders:
            logger.info(f"No pending order found with ticket={order_id}")
            return {
                "status": "error",
                "message": f"No pending order found with ticket {order_id}",
                "data": {"pending_orders": []}
            }

        logger.info(f"Successfully fetched pending order: {orders[0]}")
        
        return {
            "status": "success",
            "message": f"Pending order {order_id} fetched successfully",
            "data": {"pending_orders": orders}
        }

    except Exception as exc:
        logger.error(f"Unexpected error in fetch_pending_order_by_id({order_id})")
        return {
            "status": "error",
            "message": f"Unexpected error: {exc}",
            "data": {"pending_orders": []}
        }
