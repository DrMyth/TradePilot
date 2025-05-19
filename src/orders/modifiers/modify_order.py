from typing import Dict, Optional, Any
from orders.modifiers.update_sltp import update_sltp
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def modify_order(
    order_ticket: int,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Modify an existing MT5 order's stop-loss and take-profit.

    Validates the order ticket, then delegates the SL/TP update logic
    to the centralized `update_sltp` function for consistent behavior and logging.

    Parameters:
        order_ticket : int
            Ticket number of the order to modify.
        stop_loss : float, optional
            New stop-loss level. If None, retains the current SL.
        take_profit : float, optional
            New take-profit level. If None, retains the current TP.
    
    Returns:
        dict:
            - status (str):
                'success' if modification succeeded; otherwise 'error'.
            - message (str):
                Details of the outcome or error description.
            - data (dict):
                MT5 OrderSendResult as dict if successful; None on error.
    """
    logger.info(f"Initiating modify order: order={order_ticket}, stop_loss={stop_loss}, take_profit={take_profit}")
    
    return update_sltp(position_ticket=order_ticket, stop_loss=stop_loss, take_profit=take_profit)
