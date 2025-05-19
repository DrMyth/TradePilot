from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any
from ._fetch_account_info import _fetch_account_info

@mcp.tool()
def fetch_account_used_margin() -> Dict[str, Any]:
    """
    Get the total margin currently in use by open positions.

    Used margin is the sum of all margin requirements for your existing trades.
    A rising used margin reduces your free margin and increases risk.

    Returns:
        dict: A mapping with the following keys:
            - status (str): "success" if the used margin was fetched correctly; otherwise "error".
            - margin (float): Used margin in deposit currency.

    Raises:
        RuntimeError: If account data cannot be retrieved, propagated from `_fetch_account_info()`.
    """
    logger.info("Retrieving used margin...")
    
    margin = _fetch_account_info()["margin"]
    logger.info(f"Used margin: {margin}")
    
    return {
        "status": "success",
        "margin": margin
    }