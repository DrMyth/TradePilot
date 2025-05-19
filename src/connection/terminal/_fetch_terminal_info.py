from typing import Any, Dict
from utils.logger import logger
from utils.mt5_client import mt5

def _fetch_terminal_info() -> Dict[str, Any]:
    """
    Internal helper to fetch and validate MT5 terminal info.

    Calls `mt5.terminal_info()` and converts the resulting named tuple to a dict.

    Raises:
        RuntimeError: If the terminal info cannot be retrieved (i.e, result is None).

    Returns:
        Dict[str, Any]: A dictionary containing detailed terminal properties, including:
            - community_account (bool): Is a community account being used
            - community_connection (bool): Is the terminal connected to the MQL5 community
            - connected (bool): Whether the terminal is connected to the broker's server
            - dlls_allowed (bool): Whether DLLs are allowed in this terminal
            - trade_allowed (bool): Whether trading operations are allowed
            - tradeapi_disabled (bool): Whether the trade API is disabled
            - email_enabled (bool): Whether email notifications are enabled
            - ftp_enabled (bool): Whether FTP is enabled
            - notifications_enabled (bool): Whether push notifications are enabled
            - mqid (bool): Is the MQL5 ID active
            - build (int): Terminal build number
            - maxbars (int): Maximum number of bars in charts
            - codepage (int): Code page used in the terminal
            - ping_last (int): Last ping time in milliseconds
            - community_balance (float): Community account balance
            - retransmission (float): Data retransmission rate
            - company (str): Terminal provider or brokerage name
            - name (str): Terminal name
            - language (str): Language setting of the terminal
            - path (str): Installation path of the terminal
            - data_path (str): Path to terminal-specific data files
            - commondata_path (str): Path to shared/common data folder
    """
    logger.info("Retrieving terminal info...")
    
    info = mt5.terminal_info()
    if info is None:
        code, msg = mt5.last_error()
        logger.error(f"mt5.terminal_info() failed: [{code}] {msg}")
        raise RuntimeError(f"Failed to retrieve terminal info: [{code}] {msg}")
    
    terminal_info = info._asdict()
    logger.info(f"Terminal info retrieved successfully: {terminal_info}")
    
    return terminal_info