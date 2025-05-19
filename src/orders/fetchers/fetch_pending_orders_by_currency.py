from orders.fetchers.fetch_pending_orders import fetch_pending_orders
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mt5_client import mt5
from typing import Dict, Any

@mcp.tool()
def fetch_pending_orders_by_currency(currency: str) -> Dict[str, Any]:
    """
    Fetch all pending orders from MT5 filtered by currency substring.

    This tool wraps the lower‑level `fetch_pending_orders`, applying a
    wildcard group filter based on the provided currency code.

    Parameters:
        currency (str):
            The currency substring to match (e.g., 'USD', 'EUR').

    Returns:
        Dict[str, Any]:
            - status (str):
                "success" if orders were retrieved; otherwise "error".
            - message (str):
                Human‑readable description of the outcome.
            - data (dict):
                - pending_orders (List[Dict[str, Any]]):
                    The list of pending orders whose symbol contains the currency,
                    or an empty list if none.
    """
    logger.info(f"Getting pending orders for {currency}")

    if not isinstance(currency, str) or not currency.strip():
        logger.error(f"Invalid currency provided: {currency!r}")
        return {
            "status": "error",
            "message": f"Invalid currency: {currency!r}",
            "data": {"pending_orders": []}
        }
    
    currency = currency.strip().upper()

    all_symbols = mt5.symbols_get()
    if not all_symbols:
        logger.error("Failed to fetch symbol list from MT5.")
        return {
            "status": "error",
            "message": "Failed to fetch symbols from MT5.",
            "data": {"pending_orders": []}
        }

    matching_symbols = [s.name for s in all_symbols if currency in s.name.upper()]
    if not matching_symbols:
        logger.warning(f"No matching symbols found for currency: {currency}")
        
        return {
            "status": "error",
            "message": f"Invalid currency: No matching symbols found for '{currency}'",
            "data": {"pending_orders": []}
        }
    
    currency_filter = f"*{currency.strip().upper()}*"
    logger.info(f"Using group filter: {currency_filter}")

    try:
        response = fetch_pending_orders(group=currency_filter)
        status = response.get("status")
        message = response.get("message", "")
        orders = response.get("data", {}).get("pending_orders", [])

        if status != "success":
            logger.error(f"fetch_pending_orders() failed with group={currency_filter}: {message}")
            return {
                "status": "error",
                "message": f"Failed to fetch pending orders for currency '{currency}': {message}",
                "data": {"pending_orders": []}
            }

        count = len(orders)
        logger.info(f"Fetched {count} pending order{'s' if count != 1 else ''} for currency '{currency}'.")
        
        return {
            "status": "success",
            "message": f"Pending orders for '{currency}' fetched successfully",
            "data": {"pending_orders": orders}
        }

    except Exception as exc:
        logger.error(f"Unexpected error in fetch_pending_orders_by_currency()")
        return {
            "status": "error",
            "message": f"Unexpected error: {exc}",
            "data": {"pending_orders": []}
        }