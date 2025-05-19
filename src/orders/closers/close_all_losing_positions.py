from typing import Any, Dict
from orders.fetchers.fetch_positions import fetch_positions
from orders.closers.close_position_by_id import close_position_by_id
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def close_all_losing_positions() -> Dict[str, Any]:
    """
    Close all currently open MT5 positions that are in loss.

    Retrieves all open positions via `fetch_positions`, identifies those with
    negative profit, and closes each by ticket. Emits logs for summary.

    Returns:
        dict:
            - status (str):
                'success' if operation completed; 'error' otherwise.
            - message (str):
                Summary of closed positions or error details.
    """
    logger.info("Closing all losing positions")

    try:
        positions = fetch_positions()
        logger.info(f"Found {len(positions['data']['positions'])} positions")
    except Exception as e:
        msg = f"Error fetching positions: {e}"
        logger.error(msg)
        return {"status": "error", "message": msg}
    
    if not positions["data"]["positions"]:
        msg = "No open positions to evaluate"
        logger.info(msg)
        return {"status": "success", "message": msg}
    
    positions = positions["data"]["positions"]

    close_count = 0

    for position in positions:
        if position["profit"] < 0:
            try:
                close_position_by_id(position["ticket"])
                close_count += 1
            except Exception as e:
                msg = f"Error closing position {position['ticket']}: {e}"
                logger.error(msg)
                return {"status": "error", "message": msg}
        
    msg = f"Closed {close_count} losing positions successfully!" if close_count > 0 else "No losing positions to close"
    logger.info(msg)
    return {"status": "success", "message": msg}