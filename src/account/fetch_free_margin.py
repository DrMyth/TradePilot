from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any
from ._fetch_account_info import _fetch_account_info

@mcp.tool()
def fetch_free_margin() -> Dict[str, Any]:
    """
    Get the amount of free margin available for opening new positions.

    Free margin = equity - margin_in_use. A key safety indicator to ensure
    you have sufficient buffer before opening additional trades.

    Returns:
        dict: A mapping with the following keys:
            - status (str): "success" if the free margin was fetched correctly; otherwise "error".
            - free_margin (float): Free margin in deposit currency.

    Raises:
        RuntimeError: If account data cannot be retrieved, propagated from `_fetch_account_info()`.
    """
    logger.info("Retrieving free margin...")
    
    free_margin = _fetch_account_info()["margin_free"]
    logger.info(f"Free margin: {free_margin}")
    
    return {
        "status": "success",
        "free_margin": free_margin
    }