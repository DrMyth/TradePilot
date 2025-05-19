from typing import Any, Dict
from utils.mcp_client import mcp
from utils.logger import logger
from ._fetch_account_info import _fetch_account_info

@mcp.tool()
def fetch_account_balance() -> Dict[str, Any]:
    """
    Get the current available balance on the MT5 account.

    This function fetches the `balance` field, representing the total funds
    excluding floating profit/loss. Use this before and after trades to assess
    realized gains or losses.

    Returns:
        dict: A mapping with the following keys:
            - status (str): “success” if the balance was fetched correctly, otherwise an error code or "error".
            - balance (float): The account balance in the deposit currency.

    Raises:
        RuntimeError: If account data cannot be retrieved.
    """
    logger.info("Retrieving account balance...")
    
    balance = _fetch_account_info()["balance"]
    logger.info(f"Account balance: {balance}")
    
    return {
        "status": "success",
        "balance": balance
    }