from typing import Dict, Union, Any
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def close_position_by_id(position_ticket: Union[int, str]) -> Dict[str, Any]:
    """
    Close an open MT5 position by its ticket ID.

    Validates the ticket, retrieves the position details, and submits a close order
    by executing the opposite trade. Detailed logging is emitted for each step.

    Parameters:
        position_ticket : int or str
            Ticket of the open position to close.

    Returns:
        dict:
            - status (str):
                'success' if the position was closed; 'error' otherwise.
            - message (str):
                Outcome description or error details.
            - data (dict):
                MT5 OrderSendResult dict including 'request' if successful; None on error.
    """

    logger.info(f"Closing position for ticket: {position_ticket}")

    try:
        ticket = int(position_ticket)
    except (ValueError, TypeError):
        msg = f"Invalid position ticket '{position_ticket}'. Must be integer."
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    if(len(str(position_ticket)) != 9):
        msg = f"Invalid position ticket '{position_ticket}'. Must be 9 digits."
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    pos_info = mt5.positions_get(ticket=ticket)
    if not pos_info:
        msg = f"No open position found with ticket {ticket}."
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    pos = pos_info[0]._asdict()

    symbol   = pos["symbol"]
    volume   = pos["volume"]
    pos_type = pos["type"] 

    close_type = (mt5.ORDER_TYPE_SELL 
                  if pos_type == mt5.ORDER_TYPE_BUY 
                  else mt5.ORDER_TYPE_BUY)
                  
    request = {
        "action":    mt5.TRADE_ACTION_DEAL,
        "position":  ticket,
        "symbol":    symbol,
        "volume":    volume,
        "type":      close_type,
    }

    logger.info(f"Closing position request payload: {request}")

    result = mt5.order_send(request)

    err, desc = mt5.last_error()
    if err != 1:
        msg = f"MT5 failed to close position {ticket}: error {err} ({desc})"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    res_dict = result._asdict()
    res_dict["request"] = request
    msg = f"Position {ticket} closed successfully!"
    logger.info(msg)
    
    return {"status": "success", "message": msg, "data": res_dict}