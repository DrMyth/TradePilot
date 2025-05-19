from orders.fetchers.fetch_positions import fetch_positions
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mt5_client import mt5
from typing import Dict, Any

@mcp.tool()
def fetch_positions_by_currency(currency: str) -> Dict[str, Any]:
    """
    Fetch all open positions from MT5 filtered by currency substring.

    This tool wraps the lower‑level `fetch_positions`, applying a
    wildcard group filter based on the provided currency code.

    Parameters:
        currency (str):
            The currency substring to match (e.g., 'USD', 'EUR').

    Returns:
        Dict[str, Any]:
            - status (str):
                "success" if positions were retrieved; otherwise "error".
            - message (str):
                Human‑readable description of the outcome.
            - data (dict):
                - positions (List[Dict[str, Any]]):
                    The list of open positions whose symbol contains the currency,
                    or an empty list if none.
    """
    logger.info(f"Getting position with currency: {currency}")

    if not isinstance(currency, str) or not currency.strip():
        logger.error(f"Invalid currency provided: {currency!r}")
        return {
            "status": "error",
            "message": f"Invalid currency: {currency!r}",
            "data": {"positions": []}
        }

    currency_clean = currency.strip().upper()

    all_symbols = mt5.symbols_get()
    if not all_symbols:
        logger.error("Failed to fetch symbol list from MT5.")
        return {
            "status": "error",
            "message": "Failed to fetch symbols from MT5.",
            "data": {"positions": []}
        }

    matching_symbols = [s.name for s in all_symbols if currency_clean in s.name.upper()]
    
    if not matching_symbols:
        logger.info(f"No matching symbols found for currency: {currency_clean}")
        return {
            "status": "error",
            "message": f"Invalid currency: No matching symbols found for '{currency_clean}'",
            "data": {"positions": []}
        }
    
    group_filter = f"*{currency_clean}*"
    logger.info(f"Using group filter: {group_filter}")

    try:
        response = fetch_positions(group=group_filter)
        status = response.get("status")
        message = response.get("message", "")
        positions = response.get("data", {}).get("positions", [])

        if status != "success":
            logger.error(f"fetch_positions() failed with group={group_filter}: {message}")
            return {
                "status": "error",
                "message": f"Failed to fetch positions for currency '{currency}': {message}",
                "data": {"positions": []}
            }

        count = len(positions)
        logger.info(f"Fetched {count} position{'s' if count != 1 else ''} for currency '{currency_clean}'.")
        
        return {
            "status": "success",
            "message": f"Positions for '{currency_clean}' fetched successfully",
            "data": {"positions": positions}
        }

    except Exception as exc:
        logger.error("Unexpected error in fetch_positions_by_currency()")
        return {
            "status": "error",
            "message": f"Unexpected error: {exc}",
            "data": {"positions": []}
        }