from typing import Dict, Any
from utils.mcp_client import mcp
from utils.logger import logger
from ._fetch_terminal_info import _fetch_terminal_info  

@mcp.tool()
def is_connected() -> Dict[str, Any]:
    """ 
    Determine if the MT5 terminal is currently connected to its server.

    Returns:
        dict: A dictionary containing the following keys:
            - status (str): "success" if the connection status retrieval was successful, "error" otherwise.
            - message (str): A message indicating the result of the connection status retrieval.
            - connected (bool): True if connected, False otherwise.

    Raises:
        RuntimeError: If terminal info cannot be fetched.
    """
    logger.info("Checking connection status...")
    
    data = _fetch_terminal_info()
    logger.info(f"Terminal info: {data}")
    connected = bool(data.get("connected", False))
    logger.info(f"Terminal connected: {connected}")
    
    return {
        "status": "success",
        "message": "Terminal connection status retrieved successfully",
        "connected": connected
    }