from typing import Dict, Optional, Any
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def update_sltp(
    position_ticket: int,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Modify stop-loss and take-profit levels for an existing MT5 position.

    Updates SL and/or TP for a given position, preserving any level not specified.

    Parameters:
        position_ticket : int
            Ticket number of the position to update.
        stop_loss : float, optional
            New stop-loss level. If None, retains existing level.
        take_profit : float, optional
            New take-profit level. If None, retains existing level.

    Returns:
        dict:
            - status (str):
                'success' if update executed; otherwise 'error'.
            - message (str):
                Details of outcome or error description.
            - data (dict):
                MT5 OrderSendResult fields as dict if successful; None on error.
    """
    logger.info(f"Initiating SLTP update for position={position_ticket}, stop_loss={stop_loss}, take_profit={take_profit}")

    if not position_ticket:
        msg = "Position ticket required for SLTP"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    if len(str(position_ticket)) != 9:
        msg = "Position ticket must be a 9-digit number"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    if position_ticket <= 0 :
        msg = "Position ticket must be a positive integer"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    pos = mt5.positions_get(ticket=position_ticket)
    logger.info(f"Position: {pos}") 

    if not pos or len(pos) != 1:
        msg = f"Failed to retrieve position with ticket {position_ticket}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    current = pos[0]

    req = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": position_ticket,
    }

    sl = float(stop_loss) if stop_loss else None
    tp = float(take_profit) if take_profit else None

    if current.type == 1:
        if current.price_current > sl:
            msg = f"Update SLTP error: stop_loss {sl} must be greater than current price {current.price_current}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if current.price_current < tp:
            msg = f"Update SLTP error: take_profit {tp} must be less than current price {current.price_current}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
    elif current.type == 0:
        if current.price_current < sl:
            msg = f"Update SLTP error: stop_loss {sl} must be less than current price {current.price_current}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if current.price_current > tp:
            msg = f"Update SLTP error: take_profit {tp} must be greater than current price {current.price_current}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
                
    req["sl"] = sl if sl else current.sl
    req["tp"] = tp if tp else current.tp

    logger.info(f"SLTP request payload: {req}")

    result = mt5.order_send(req)

    err, desc = mt5.last_error()
    if err != 1:
        msg = f"MT5 SLTP update failed {err}: {desc}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    return {"status": "success", "message": "Updated SLTP successfully!", "data": result._asdict()}