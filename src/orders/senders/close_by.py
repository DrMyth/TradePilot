from typing import Dict, Any
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def close_by(
    position_ticket: int,
    position_by: int,
) -> Dict[str, Any]:
    """
    Close an open MT5 position by offsetting it against another open position.

    Issues a close-by request pairing two existing positions, allowing one
    position to be closed directly against another, reducing required margin.

    Parameters:
        position_ticket : int
            Ticket of the position to be closed.
        position_by : int
            Ticket of the position against which to close the first.

    Returns:
        dict:
            - status (str):
                'success' if the close-by was executed; otherwise 'error'.
            - message (str):
                Description of outcome or error details.
            - data (dict):
                MT5 OrderSendResult fields as dict if successful; None on error.
    """
    logger.info(f"Initiating close by: pos={position_ticket}, by={position_by}")

    if not position_ticket or not position_by or position_ticket <= 0 or position_by <= 0:
        msg = "Both position and position_by tickets required and must be positive integers"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    position_get = mt5.positions_get(ticket=position_ticket)
    logger.info(f"Position: {position_get}")
    position_by_get = mt5.positions_get(ticket=position_by)
    logger.info(f"Position by: {position_by_get}")

    if not position_get or len(position_get) != 1:
        msg = f"Failed to retrieve position with ticket {position_ticket}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    if not position_by_get or len(position_by_get) != 1:
        msg = f"Failed to retrieve position with ticket {position_by}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    position_symbol = position_get[0].symbol
    position_vol = position_get[0].volume
    position_by_symbol = position_by_get[0].symbol
    position_vol = position_get[0].volume

    if position_symbol != position_by_symbol:
        msg = f"Position and position_by must be on the same symbol"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    if position_by_vol > position_vol:
        logger.info(f"Swapping close_by roles because position_by.volume ({position_by_vol}) > position.volume ({position_vol})")
        position_ticket, position_by = position_by, position_ticket
        position_vol, position_by_vol = position_by_vol, position_vol

    req = {
        "action": mt5.TRADE_ACTION_CLOSE_BY,
        "position": position_ticket,
        "position_by": position_by
    }
    
    logger.info(f"Close_by request: {req}")
    result = mt5.order_send(req)
    err, desc = mt5.last_error()
    logger.info(f"Error code: {err}, Error description: {desc}")
    
    if err != 1:
        msg = f"MT5 close_by failed {err}: {desc}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    logger.info(f"Close by executed successfully: {result}")
    data = result._asdict()
    data["request"] = result.request._asdict()
    
    return {"status": "success", "message": "Close by executed successfully!", "data": data}