from typing import Any, Dict
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mt5_client import mt5

@mcp.tool()
def initialize() -> Dict[str, Any]:
    """
    Initialize the MetaTrader 5 terminal.
    
    Returns:
        dict: A mapping with the following keys:
            - status (str): "success" if initialization was successful, "error" otherwise.
            - message (str): A message indicating the result of the initialization.
            - initialized (bool): True if initialization was successful, False otherwise.
    """
    logger.info("Initializing MT5...")
    
    mt5.initialize()

    if not mt5.initialize():
        logger.error(f"MT5 initialization failed, error code: {mt5.last_error()}")
        return {
            "status": "error",
            "message": f"MT5 initialization failed, error code: {mt5.last_error()}",
            "initialized": False
        }
    
    logger.info("MT5 initialized successfully")
    return {
        "status": "success",
        "message": "MT5 initialized successfully",
        "initialized": True
    }