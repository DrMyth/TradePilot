from typing import Any, Dict
from orders.fetchers.fetch_positions import fetch_positions
from orders.closers.close_position_by_id import close_position_by_id
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def close_all_profitable_positions() -> Dict[str, Any]:
    """
    Close all MT5 positions currently in profit.

    Retrieves all open positions via `fetch_positions`, identifies those with
    non-negative profit, and issues a close request for each, logging actions.

    Returns:
        dict:
            - status (str):
                'success' if operation completed; 'error' on fetch failure.
            - message (str):
                Summary of how many profitable positions were closed.
    """
    logger.info("Closing all profitable positions")

    try:
        positions = fetch_positions()
        logger.info(f"Found {len(positions)} positions")
    except Exception as e:
        msg = f"Error fetching positions: {e}"
        logger.error(msg)
        return {"status": "error", "message": msg}
    
    if not positions["data"]["positions"]:
        msg = "No open positions to close"
        logger.info(msg)
        return {"status": "success", "message": msg}
    
    positions = positions["data"]["positions"]

    close_count = 0
    for position in positions:
        if position["profit"] >= 0:
            try:
                close_position_by_id(position["ticket"])
                close_count += 1
            except Exception as e:
                msg = f"Error closing position {position['ticket']}: {e}"
                logger.error(msg)
                return {"status": "error", "message": msg}

    msg = f"Closed {close_count} profitable positions successfully!" if close_count > 0 else "No profitable positions to close"
    logger.info(msg)
    
    return {"status": "success", "message": msg}