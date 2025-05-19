from typing import Any, Dict
from utils.logger import logger
from utils.mcp_client import mcp
from utils.mt5_client import mt5

@mcp.tool()
def fetch_symbol_info(symbol_name: str) -> Dict[str, Any]:
    """
    Retrieve detailed symbol properties from MT5.

    This tool calls `mt5.symbols_get()` to fetch all symbol entries matching
    the given name, then returns the first match’s attributes as a dict.

    Parameters:
        symbol_name (str):
            Symbol name to query (e.g., 'GBPUSD').

    Returns:
        dict:
            - status (str):
                "success" if the operation completed successfully; otherwise "error".
            - message (str):
                Details about the retrieval outcome.
            - symbol_info (Dict[str, Any]):
                Mapping of symbol attributes (e.g., `name`, `path`, `session_*`, `trade_*`, etc.)
                to their values.

    Raises:
        RuntimeError:
            - If the symbol is not found.
            - If the MT5 API call fails.
    """
    logger.info(f"Fetching symbol info for {symbol_name}")

    try: 
        symbols = mt5.symbols_get(symbol_name)
        logger.info(f"Symbols: {symbols}")

        if not symbols or len(symbols) == 0:
            logger.error(f"Symbol '{symbol_name}' not found")
            raise RuntimeError(f"Symbol '{symbol_name}' not found")
        
        symbol_info = symbols[0]
        logger.info(f"Symbol info: {symbol_info}")

        result = {
            attr: getattr(symbol_info, attr)
            for attr in dir(symbol_info)
            if not attr.startswith('__') and not callable(getattr(symbol_info, attr))
        }

        logger.info(f"Symbol info fields: {list(result.keys())}")
        return {
            "status": "success",
            "message": "Symbol info retrieved successfully",
            "symbol_info": result
        }
    
    except Exception as e:
        logger.error(f"Error fetching symbol info: {e}")
        raise RuntimeError(f"Error fetching symbol info: {e}")