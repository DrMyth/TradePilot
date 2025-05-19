from typing import Any, Dict
from orders.fetchers.fetch_positions import fetch_positions
from orders.closers.close_position_by_id import close_position_by_id
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def close_all_positions() -> Dict[str, Any]:
    """
    Close all currently open MT5 positions regardless of symbol or profit.

    Retrieves all open positions via `fetch_positions` and issues a close
    request for each, logging progress and errors.

    Returns:
        dict:
            - status (str):
                'success' if operation completed; 'error' on failure.
            - message (str):
                Summary of how many positions were closed or error details.
    """
    logger.info("Closing all positions")

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
        try:
            close_position_by_id(position["ticket"])
            close_count += 1
        except Exception as e:
            msg = f"Error closing position {position['ticket']}: {e}"
            logger.error(msg)
            return {"status": "error", "message": msg}

    msg = f"Closed {close_count} positions successfully!" if close_count > 0 else "No positions to close"
    logger.info(msg)
    
    return {"status": "success", "message": msg}