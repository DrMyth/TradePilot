from utils.mcp_client import mcp
from utils.logger import logger
from ._fetch_account_info import _fetch_account_info
from typing import Any, Dict

@mcp.tool()
def fetch_account_currency() -> Dict[str, Any]:
    """
    Retrieve the currency code used by the MT5 account.

    Returns the 3-letter ISO code for the deposit currency (e.g., "USD", "EUR").

    Returns:
        dict: A mapping with the following keys:
            - status (str): “success” if the currency was fetched correctly, otherwise an error code or "error".
            - currency (str): The 3-letter ISO code for the deposit currency (e.g., "USD", "EUR").

    Raises:
        RuntimeError: If account data cannot be retrieved.
    """
    logger.info("Retrieving account currency...")
    
    currency = _fetch_account_info()["currency"]
    logger.info(f"Account currency: {currency}")
    
    return {
        "status": "success",
        "currency": currency
    }