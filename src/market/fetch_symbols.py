from typing import List, Optional
from utils.logger import logger
from utils.mcp_client import mcp
from utils.mt5_client import mt5

@mcp.tool()
def fetch_symbols(group:Optional[str] = None) -> List[str]:
    """
    Retrieve a list of trading symbol names available in the MT5 terminal.

    This tool calls `mt5.symbols_get()` either with no filter (to fetch all symbols)
    or with the provided `group` string as a wildcard filter.

    Parameters:
        group (str, optional):
            The group name or pattern to filter symbols by (e.g., "Forex", "Crypto").
            If None, all available symbols are returned. Defaults to None.

    Raises:
        RuntimeError:
            - If the MT5 API call fails.

    Returns:
        dict:
            - status (str):
                "success" if the operation completed successfully; otherwise "error".
            - message (str):
                Details about the retrieval outcome.
            - symbols (List[str]):
                A list of symbol names (e.g., ["EURUSD", "XAUUSD", "USDJPY"]).
    """
    logger.info(f"Fetching symbols with group: {group}")

    try: 
        group_str = f"*{group}*" if group else None
        symbols = mt5.symbols_get(group_str) if group_str else mt5.symbols_get()
        names = [symbol.name for symbol in symbols] if symbols else []

        logger.info(f"Symbols: {names}")
        logger.info(f"Number of symbols: {len(names)}")

        return {
            "status": "success",
            "message": "Symbols retrieved successfully",
            "symbols": names
        }
    
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        raise RuntimeError(f"Error fetching symbols: {e}")