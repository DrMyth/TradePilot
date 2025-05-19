from typing import Dict, Optional, Any
from orders.modifiers.update_sltp import update_sltp
from utils.mcp_client import mcp
from utils.logger import logger
from orders.fetchers.fetch_position_by_id import fetch_position_by_id

@mcp.tool()
def modify_position(
    position_ticket: int,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Modify an existing MT5 position's stop-loss and take-profit via a shared SL/TP updater.

    Validates that the position exists, then delegates the SL/TP update logic
    to the centralized `update_sltp` function for consistent behavior and logging.

    Parameters:
        position_ticket : int
            Ticket number of the position to modify.
        stop_loss : float, optional
            New stop-loss level. If None, retains the current SL.
        take_profit : float, optional
            New take-profit level. If None, retains the current TP.

    Returns:
        dict:
            - status (str):
                'success' if update succeeded; otherwise 'error'.
            - message (str):
                Description of the operation outcome or error.
            - data (dict):
                Resulting MT5 OrderSendResult dict if successful; None on error.
    """
    logger.info(f"Initiating modify position: position={position_ticket}, stop_loss={stop_loss}, take_profit={take_profit}")

    positions = fetch_position_by_id(position_ticket)
    if not positions:
        return {
            "status": "error",
            "message": f"No position found with ID {position_ticket}",
            "data": None,
        }

    return update_sltp(
        position_ticket=position_ticket,
        stop_loss=stop_loss,
        take_profit=take_profit,
    )