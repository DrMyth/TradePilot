from typing import Any, Dict
from utils.mcp_client import mcp
from utils.logger import logger
from ._fetch_terminal_info import _fetch_terminal_info

@mcp.tool()
def fetch_terminal_info() -> Dict[str, Any]:
    """
    Retrieve full MetaTrader 5 terminal information.

    Returns:
        Dict[str, Any]: A dictionary containing terminal properties, such as:
            - community_account (bool): Is a community account used
            - community_connection (bool): Is MQL5 community connected
            - connected (bool): Whether the terminal is connected to the broker
            - dlls_allowed (bool): Whether DLLs are allowed
            - trade_allowed (bool): Whether trading is currently permitted
            - tradeapi_disabled (bool): Whether trade API access is disabled
            - email_enabled (bool): Email functionality status
            - ftp_enabled (bool): FTP functionality status
            - notifications_enabled (bool): Push notifications status
            - mqid (bool): MQL5 ID availability
            - build (int): Terminal build number
            - maxbars (int): Max number of chart bars
            - codepage (int): Terminal code page
            - ping_last (int): Last ping duration in milliseconds
            - community_balance (float): MQL5 community account balance
            - retransmission (float): Data retransmission value
            - company (str): Broker or provider name
            - name (str): Terminal product name
            - language (str): Terminal language
            - path (str): Installation path
            - data_path (str): Terminal data folder
            - commondata_path (str): Shared data folder

    Raises:
        RuntimeError: If the terminal info cannot be fetched, propagates the error from `_get_terminal_info`.
    """
    logger.info("Retrieving terminal information...")
    
    terminal_info = _fetch_terminal_info()
    logger.info(f"Terminal information retrieved: {terminal_info}")
    
    return {
        "status": "success",
        "message": "Terminal information retrieved successfully",
        "terminal_info": terminal_info
    }