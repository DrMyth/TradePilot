from typing import Any, Dict
from utils.mcp_client import mcp
from utils.logger import logger
from ._fetch_terminal_info import _fetch_terminal_info

@mcp.tool()
def is_trading_allowed() -> Dict[str, Any]:
    """
    Check if the MT5 terminal currently permits new trade operations.

    Queries `mt5.terminal_info()` for the `trade_allowed` flag. If trading is disabled
    (e.g., account disconnected, market closed), this returns False.

    Returns:
        dict: A dictionary containing the following keys:
            - status (str): "success" if the trading permission check was successful, "error" otherwise.
            - message (str): A message indicating the result of the trading permission check.
            - trading_allowed (bool): True if trading is allowed, False otherwise.

    Raises:
        RuntimeError: If the call to `mt5.terminal_info()` fails.
    """
    logger.info("Checking trading permission...")
    
    data = _fetch_terminal_info()
    allowed = bool(data.get("trade_allowed", True))
    logger.info(f"Trading allowed: {allowed}")
    
    return {
        "status": "success",
        "message": "Trading allowed status retrieved successfully",
        "trading_allowed": allowed
    }