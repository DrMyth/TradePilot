from typing import Dict, Any
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def cancel_order(
    order_ticket: int,
) -> Dict[str, Any]:
    """
    Cancel an existing MT5 pending order by its ticket ID.

    Issues a remove action to MT5 for the specified order ticket, handling
    validation, execution, and logging of the cancel operation.

    Parameters:
        order_ticket : int
            Ticket number of the pending order to cancel.

    Returns:
        dict:
            - status (str):
                'success' if cancellation succeeded; 'error' otherwise.
            - message (str):
                Outcome description or error details.
            - data (dict):
                MT5 OrderSendResult dict if successful; None on error.
    """
    logger.info(f"Cancelling order with ticket: {order_ticket}")

    if not order_ticket:
        msg = "Order ticket required for removal"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    if(len(str(order_ticket)) != 9):
        msg = f"Invalid order ticket '{order_ticket}'. Must be 9 digits."
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    try:
        order_ticket = int(order_ticket)
    except (ValueError, TypeError):
        msg = f"Invalid order ticket '{order_ticket}'. Must be integer."
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    order = mt5.orders_get(ticket=order_ticket)
    logger.info(f"Order: {order}")

    if not order:
        msg = f"Order {order_ticket} not found."
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    order = order[0]

    req = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": order.ticket
    }

    logger.info(f"Cancel Order request payload: {req}")

    result = mt5.order_send(req)
    err, desc = mt5.last_error()
    if err != 1:
        msg = f"MT5 cancel pending failed {err}: {desc}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    data = result._asdict()
    data['request'] = req
    msg = f"Order {order_ticket} cancelled successfully!"
    logger.info(msg)
    return {"status": "success", "message": msg, "data": data}