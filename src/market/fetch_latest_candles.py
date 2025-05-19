from typing import Any, Dict, List, Optional
from utils.logger import logger
from utils.mcp_client import mcp
from utils.mappings.timeframe_mapping import TIMEFRAME_MAP
from utils.mt5_client import mt5

@mcp.tool()
def fetch_latest_candles(
    symbol_name: str,
    timeframe: str,
    count: Optional[int] = 100
) -> Dict[str, Any]:
    """
    Fetch the latest N candlestick (OHLC) data for a symbol and timeframe.

    This tool calls `mt5.copy_rates_from_pos()` to retrieve the most recent bars.

    Parameters:
        symbol_name : str
            Trading symbol (e.g., 'EURUSD'). Must exist in MT5.
        timeframe : str
            Timeframe string (e.g., 'M1', 'H1', 'D1'). Must map via TIMEFRAME_MAP.
        count : int, optional
            Number of most recent candles to fetch. Default is 100.

    Returns:
        dict:
            - status (str):  
                "success" if the operation completed successfully; otherwise "error".
            - message (str):  
                Details about the retrieval outcome.
            - candles (List[Dict[str, Any]]):  
                List of latest candle data in descending time order. Each candle contains:
                'time', 'open', 'high', 'low', 'close', 'tick_volume', etc.

    Raises:
        RuntimeError
            - If symbol not found.
            - If timeframe is invalid.
            - If data retrieval fails.
    """
    logger.info(f"Fetching latest candles for {symbol_name} {timeframe} with count {count}")

    if not mt5.symbol_info(symbol_name):
        logger.error(f"Symbol '{symbol_name}' not found.")
        raise RuntimeError(f"Symbol '{symbol_name}' not found.")

    tf = TIMEFRAME_MAP.get(timeframe)
    if tf is None:
        logger.error(f"Invalid timeframe: '{timeframe}'")
        raise RuntimeError(f"Invalid timeframe: '{timeframe}'")

    try: 
        candles = mt5.copy_rates_from_pos(symbol_name, tf, 0, count)
        if candles is None or len(candles) == 0:
            logger.error(f"Failed to retrieve candle data for symbol '{symbol_name}' with timeframe '{timeframe}'")
            raise RuntimeError(
                f"Failed to retrieve candle data for symbol '{symbol_name}' with timeframe '{timeframe}'"
            )

        data: List[Dict[str, Any]] = []
        field_names = candles.dtype.names or []
        for entry in candles:
            row = {field: entry[field] for field in field_names}
            data.append(row)

        data.sort(key=lambda x: x['time'], reverse=True)
        logger.info(f"Retrieved {len(data)} candles")
        
        return {
            "status": "success",
            "message": "Candles retrieved successfully",
            "candles": data
        }

    except Exception as e:
        logger.error(f"Error fetching candles: {e}")
        raise RuntimeError(f"Error fetching candles: {e}")