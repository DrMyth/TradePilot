from typing import Any, Dict
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mt5_client import mt5

@mcp.tool()
def shutdown() -> Dict[str, Any]:   
    """
    Shutdown the MetaTrader 5 terminal.
    
    Returns:
        dict: A mapping with the following keys:
            - status (str): "success" if shutdown was successful, "error" otherwise.
            - message (str): A message indicating the result of the shutdown.
            - shutdown (bool): True if shutdown was successful, False otherwise.
    """
    logger.info("Shutting down MT5...")
    
    if mt5.shutdown():
        logger.info("MT5 shutdown successfully")
        return {
            "status": "success",
            "message": "MT5 shutdown successfully",
            "shutdown": True
        }
    else:
        logger.error(f"MT5 shutdown failed, error code: {mt5.last_error()}")
        return {
            "status": "error",
            "message": f"MT5 shutdown failed, error code: {mt5.last_error()}",
            "shutdown": False
        }