from typing import Union, Dict, Any
from utils.mcp_client import mcp
from utils.logger import logger
from orders.cancellers.cancel_order import cancel_order

@mcp.tool()
def cancel_pending_order_by_id(order_id: Union[int, str]) -> Dict[str, Any]:
    """
    Proxy for cancelling an MT5 pending order by ticket ID.

    Validates the provided ticket, converts it to an integer, and then delegates
    the actual cancellation logic to `cancel_order`, ensuring consistent logging
    and error handling.

    Parameters:
        order_id : int or str
            Ticket number of the pending order to cancel. Must be convertible to a
            positive integer.

    Returns:
        dict:
            - status (str):
                'success' if the cancellation succeeded; otherwise 'error'.
            - message (str):
                Description of the operation outcome or error details.
            - data (dict), optional:
                MT5 OrderSendResult dict including the request payload if successful.
    """
    logger.info(f"Cancelling pending order {order_id}")

    try:
        order_id = int(order_id)
    except ValueError:
        return {"status": "error", "message": f"Invalid order ID: {order_id}"}
    
    return cancel_order(order_id)