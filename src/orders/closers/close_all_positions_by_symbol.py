from orders.fetchers.fetch_positions import fetch_positions
from orders.closers.close_position_by_id import close_position_by_id
from typing import Any, Dict
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mt5_client import mt5

@mcp.tool()
def close_all_positions_by_symbol(symbol: str) -> Dict[str, Any]:
    """
    Close all open MT5 positions for a specified trading symbol.

    Retrieves all positions matching the given symbol via `fetch_positions` and
    issues a close request for each. Logs progress and errors per position.

    Parameters:
        symbol : str
            Trading instrument symbol (e.g., 'EURUSD'). Positions with this symbol will be closed.

    Returns:
        dict:
            - status (str):
                'success' if operation completed; otherwise 'error'.
            - message (str):
                Summary of how many positions were closed or error details.
    """
    logger.info(f"Closing all positions for {symbol}")

    if not mt5.symbol_info(symbol):
        msg = f"Invalid symbol: {symbol}"
        logger.error(msg)
        return {"status": "error", "message": msg}

    try:
        positions = fetch_positions(symbol_name=symbol)
        logger.info(f"Found {len(positions)} positions")
    except Exception as e:
        msg = f"Error fetching positions: {e}"
        logger.error(msg)
        return {"status": "error", "message": msg}

    if not positions["data"]["positions"]:
        msg = f"No open positions found for symbol {symbol}"
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

    msg = f"Closed {close_count} positions for {symbol} successfully!" if close_count > 0 else f"No positions to close for {symbol}"
    logger.info(msg)
    return {"status": "success", "message": msg}