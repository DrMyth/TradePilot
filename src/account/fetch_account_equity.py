from utils.mcp_client import mcp
from utils.logger import logger
from ._fetch_account_info import _fetch_account_info
from typing import Any, Dict

@mcp.tool()
def fetch_account_equity() -> Dict[str, Any]:
    """
    Get the current equity on the MT5 account (balance + floating P/L).

    Equity reflects both realized and unrealized profit and loss, offering a live view
    of account health when positions are open.

    Returns:
        dict: A mapping with the following keys:
            - status (str): “success” if the equity was fetched correctly, otherwise an error code or "error".
            - equity (float): The account equity in the deposit currency.

    Raises:
        RuntimeError: If account data cannot be retrieved.
    """
    logger.info("Retrieving account equity...")
    
    equity = _fetch_account_info()["equity"]
    logger.info(f"Account equity: {equity}")
    
    return {
        "status": "success",
        "equity": equity
    }