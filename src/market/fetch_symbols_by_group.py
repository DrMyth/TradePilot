from typing import List
from utils.logger import logger
from utils.mcp_client import mcp
from utils.mt5_client import mt5

@mcp.tool()
def fetch_symbols_by_group(group: str) -> List[str]:
    """
    Retrieve all symbols whose names include a given currency code.

    This tool uses wildcard matching around the provided `group` string
    (e.g., "USD", "JPY") to find symbols like "EURUSDm", "USDJPYm", etc.,
    by calling `mt5.symbols_get()` with a pattern `*<group>*`.

    Parameters:
        group (str):
            Currency or code fragment to match within symbol names
            (e.g., 'USD', 'JPY').

    Returns:
        dict:
            - status (str):
                "success" if symbols were retrieved; otherwise "error".
            - message (str):
                Details about the retrieval outcome.
            - symbols (List[str]):
                A list of matching symbol names (e.g., ["EURUSDm", "USDJPYm", ...]).

    Raises:
        RuntimeError:
            - If the MT5 API call fails.
    """
    logger.info(f"Fetching symbols by group: {group}")

    try: 
        group = f"*{group}*"
        symbols = mt5.symbols_get(group)
        names = [symbol.name for symbol in symbols] if symbols else []

        logger.info(f"Symbols: {names}")
        logger.info(f"Number of symbols: {len(names)}")

        return {
            "status": "success",
            "message": "Symbols retrieved successfully",
            "symbols": names
        }
    
    except Exception as e:
        logger.error(f"Error fetching symbols by group: {e}")
        raise RuntimeError(f"Error fetching symbols by group: {e}")