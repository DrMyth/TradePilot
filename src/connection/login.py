from typing import Any, Dict
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mt5_client import mt5

@mcp.tool()
def login(login: int, password: str, server: str) -> Dict[str, Any]:
    """
    Logs into the MetaTrader 5 terminal using the provided credentials.
    
    Args:
        login (str): The account login for MetaTrader 5.
        password (str): The account password for MetaTrader 5.
        server (str): The server address for MetaTrader 5 (e.g., 'Exness-MT5Trial14').
    
    Returns:
        dict: A mapping with the following keys:
            - status (str): "success" if the login is successful, "error" otherwise.
            - message (str): A message indicating the result of the login.
            - logged_in (bool): True if the login is successful, False otherwise.
        
    Raises:
        Exception: If MetaTrader 5 is not initialized or login fails.
    """
    logger.info(f"Logging in to account {login} on server {server}...")

    if not mt5.initialize():
        raise Exception("MT5 initialization failed. Please ensure the terminal is correctly initialized.")
    
    authorized = mt5.login(login, password, server)
    logger.info(f"Authorization result: {authorized}")
    
    if authorized:
        logger.info(f"Successfully logged in to account {login} on server {server}.")
        return {
            "status": "success",
            "message": f"Successfully logged in to account {login} on server {server}.",
            "logged_in": True
        }
    else:
        logger.error(f"Failed to log in to account {login}. Error code: {mt5.last_error()}")
        return {
            "status": "error",
            "message": f"Failed to log in to account {login}. Error code: {mt5.last_error()}",
            "logged_in": False
        }