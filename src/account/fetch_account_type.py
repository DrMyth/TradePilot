from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any
from ._fetch_account_info import _fetch_account_info

@mcp.tool()
def fetch_account_type() -> Dict[str, Any]:
    """
    Determine the human-readable type of the MT5 account (real/demo/contest).

    This function fetches the raw `trade_mode` integer from the account info and
    maps it to a descriptive string:
      - 0 => "real"
      - 1 => "demo"
      - 2 => "contest"
    If the integer is outside these known values, it returns "unknown(<code>)".

    Returns:
        dict: A mapping with the following keys:
            - status (str): "success" if the account type was fetched correctly; otherwise "error".
            - account_type (str): The account type in plain English.

    Raises:
        RuntimeError: If account data cannot be retrieved, propagated from `_fetch_account_info()`.
    """
    logger.info("Retrieving account type...")
    
    trade_mode = _fetch_account_info()["trade_mode"]
    mapping = {0: "real", 1: "demo", 2: "contest"}
    account_type = mapping.get(trade_mode, f"unknown({trade_mode})")
    logger.info(f"Account type: {account_type}")
    
    return {
        "status": "success",
        "account_type": account_type
    }