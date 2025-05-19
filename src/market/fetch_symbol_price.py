from datetime import timezone
from typing import Any, Dict
from utils.logger import logger
from utils.mcp_client import mcp
from utils.mt5_client import mt5
from datetime import datetime

@mcp.tool()
def fetch_symbol_price(symbol_name: str) -> Dict[str, Any]:
    """
    Retrieve the latest tick price data for a given trading symbol.

    This tool calls `mt5.symbol_select()` and `mt5.symbol_info_tick()` to fetch
    the most recent market data for the specified symbol.

    Parameters:
        symbol_name (str):
            The name of the trading symbol (e.g., "EURUSD", "XAUUSD").

    Returns:
        dict:
            - status (str):
                "success" if the operation completed successfully; otherwise "error".
            - message (str):
                Details about the retrieval outcome.
            - price (Dict[str, Any]):
                A dictionary containing:
                  - bid (float): current bid price
                  - ask (float): current ask price
                  - last (float): last trade price
                  - volume (float): tick volume
                  - time (datetime): UTC timestamp of the tick

    Raises:
        RuntimeError:
            - If the symbol could not be selected in the MT5 terminal.
            - If price data for the symbol is unavailable.
    """
    logger.info(f"Fetching symbol price for {symbol_name}")

    try: 
        if not mt5.symbol_select(symbol_name, True):
            logger.error(f"Failed to select symbol '{symbol_name}'")
            raise RuntimeError(f"Failed to select symbol '{symbol_name}'")

        tick = mt5.symbol_info_tick(symbol_name)
        if tick is None:
            logger.error(f"Could not get price data for symbol '{symbol_name}'")
            raise RuntimeError(f"Could not get price data for symbol '{symbol_name}'")

        tick_time = datetime.fromtimestamp(tick.time, tz=timezone.utc)

        result = {
            "bid": tick.bid,
            "ask": tick.ask,
            "last": tick.last,
            "volume": tick.volume,
            "time": tick_time
        }

        logger.info(f"Symbol price: {result}")

        return {
            "status": "success",
            "message": "Symbol price retrieved successfully",
            "price": result
        }
    
    except Exception as e:
        logger.error(f"Error fetching symbol price: {e}")
        raise RuntimeError(f"Error fetching symbol price: {e}")