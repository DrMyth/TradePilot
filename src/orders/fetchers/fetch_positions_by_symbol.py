from orders.fetchers.fetch_positions import fetch_positions
from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any

@mcp.tool()
def fetch_positions_by_symbol(symbol: str) -> Dict[str, Any]:
    """
    Fetch all open positions from MT5 for a specific trading symbol.

    This tool wraps the lower‑level `fetch_positions` call, applying
    a symbol_name filter based on the provided symbol.

    Parameters:
        symbol (str):
            The exact trading symbol to match (e.g., 'EURUSDm').

    Returns:
        Dict[str, Any]:
            - status (str):
                "success" if positions were retrieved; otherwise "error".
            - message (str):
                Human‑readable description of the outcome.
            - data (dict):
                - positions (List[Dict[str, Any]]):
                    The list of open positions for the given symbol,
                    or an empty list if none.
    """
    logger.info(f"Getting position with symbol: {symbol}")

    if not isinstance(symbol, str) or not symbol.strip():
        logger.error(f"Invalid symbol provided: {symbol!r}")
        return {
            "status": "error",
            "message": f"Invalid symbol: {symbol!r}",
            "data": {"positions": []}
        }

    try:
        response = fetch_positions(symbol_name=symbol.strip())
        status = response.get("status")
        message = response.get("message", "")
        positions = response.get("data", {}).get("positions", [])

        if status != "success":
            logger.error(f"fetch_positions() failed for symbol={symbol}: {message}")
            return {
                "status": "error",
                "message": f"Failed to fetch positions for symbol '{symbol}': {message}",
                "data": {"positions": []}
            }

        count = len(positions)
        logger.info(f"Fetched {count} position{'s' if count != 1 else ''} for symbol '{symbol}'.")
        
        return {
            "status": "success",
            "message": f"Positions for symbol '{symbol}' fetched successfully",
            "data": {"positions": positions}
        }

    except Exception as exc:
        logger.error(f"Unexpected error in fetch_positions_by_symbol()")
        return {
            "status": "error",
            "message": f"Unexpected error: {exc}",
            "data": {"positions": []}
        }