from typing import Dict, Any
from utils.mcp_client import mcp
from utils.logger import logger
from ._fetch_account_info import _fetch_account_info

@mcp.tool()
def fetch_trade_statistics() -> Dict[str, Any]:
    """
    Bundle key trading metrics into a single summary dict.

    This function retrieves a comprehensive snapshot including:
      - balance, equity, profit
      - free_margin, margin_level
      - account_type, leverage, currency

    Returns:
        dict: A mapping with the following keys:
            - status (str): "success" if the trade statistics were fetched correctly; otherwise "error".
            - trade_statistics (dict): Summary of trading statistics for quick monitoring or dashboards.

    Raises:
        RuntimeError: If account data cannot be retrieved, propagated from `_fetch_account_info()`.
    """
    logger.info("Retrieving trade statistics...")
    
    info = _fetch_account_info()
    stats = {
        "balance": info["balance"],
        "equity": info["equity"],
        "profit": info["profit"],
        "free_margin": info["margin_free"],
        "margin_level": info["margin_level"],
        "account_type": {0: "real", 1: "demo", 2: "contest"}
                        .get(info["trade_mode"], f"unknown({info['trade_mode']})"),
        "leverage": info["leverage"],
        "currency": info["currency"],
    }
    
    logger.info(f"Trade statistics: {stats}")
    
    return {
        "status": "success",
        "trade_statistics": stats
    }