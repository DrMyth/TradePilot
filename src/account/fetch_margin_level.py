from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any
from ._fetch_account_info import _fetch_account_info

@mcp.tool()
def fetch_margin_level() -> Dict[str, Any]:
    """
    Compute and return the margin level percentage (equity / used margin * 100).

    Margin level is a critical risk metric calculated as (equity / margin) * 100. 
    It indicates the account's health and risk exposure. Values above 100% mean your
    equity exceeds the required margin, while values below your broker’s threshold can
    trigger margin calls or forced liquidations (stop-outs). Generally, above 1000% is
    very safe, 300%–1000% is safe, 100%–300% is a caution zone, and below 100% is risky
    and may lead to auto-closeouts. The exact stop-out level varies by broker (e.g., 50%, 30%, 20%).

    Returns:
        dict: A mapping with the following keys:
            - status (str): "success" if the margin level was fetched correctly; otherwise "error".
            - margin_level (float): Margin level percentage.

    Raises:
        RuntimeError: If account data cannot be retrieved, propagated from `_fetch_account_info()`.
    """
    logger.info("Retrieving margin level...")
    
    level = _fetch_account_info()["margin_level"]
    logger.info(f"Margin level: {level}%")
    
    return {
        "status": "success",
        "margin_level": level
    }