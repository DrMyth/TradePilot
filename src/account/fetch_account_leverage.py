from utils.mcp_client import mcp
from utils.logger import logger
from ._fetch_account_info import _fetch_account_info
from typing import Any, Dict

@mcp.tool()
def fetch_account_leverage() -> Dict[str, Any]:
    """
    Retrieve the leverage ratio for the MT5 account.

    Leverage indicates the multiple of exposure allowed relative to your deposit.
    For example, 100 => 1:100.

    Returns:
        dict: A mapping with the following keys:
            - status (str): “success” if the leverage was fetched correctly, otherwise an error code or "error".
            - leverage (int): Leverage factor.

    Raises:
        RuntimeError: If account data cannot be retrieved, propagated from `_fetch_account_info()`.
    """
    logger.info("Retrieving account leverage...")
    
    leverage = _fetch_account_info()["leverage"]
    logger.info(f"Account leverage: {leverage}")
    
    return {
        "status": "success",
        "leverage": leverage
    }