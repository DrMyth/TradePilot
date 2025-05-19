from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mt5_client import mt5
from utils.mappings.timeframe_mapping import TIMEFRAME_MAP

def _parse_date(date_str: str, end_of_day: bool = False) -> datetime:
    """
    Parse a date string into a UTC datetime object.

    Supports formats:
      - YYYY-MM-DD
      - YYYY-MM-DD HH:MM

    If only date is provided, time is set to start or end of day.

    Parameters
    ----------
    date_str : str
        Date string to parse.
    end_of_day : bool, optional
        If True and only date format provided, set time to 23:59. Otherwise 00:00.

    Returns
    -------
    datetime
        Parsed datetime with UTC timezone.

    Raises
    ------
    ValueError
        If the date_str does not match supported formats.
    """
    logger.info(f"Parsing date '{date_str}' (end_of_day={end_of_day})")

    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(date_str, fmt)
            if fmt == "%Y-%m-%d":
                dt = dt.replace(hour=23, minute=59) if end_of_day else dt.replace(hour=0, minute=0)
            logger.info(f"Parsed datetime: {dt.isoformat()}")
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    logger.error(f"Invalid date format: {date_str}")
    raise RuntimeError(f"Invalid date format: {date_str}")

@mcp.tool()
def fetch_historical_candles(
    symbol_name: str,
    timeframe: str = "H1",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch historical OHLC candlestick data from MT5 for a symbol over a date range.

    Retrieves bars between two dates (inclusive), parsing inputs and falling back to
    the last 30 days or latest 1000 bars if limits are omitted.

    Parameters:
        symbol_name : str
            Trading symbol (e.g., 'EURUSD').
        timeframe : str
            Timeframe code (e.g., 'M1', 'H1', 'D1'). Must map via TIMEFRAME_MAP. Default is 'H1'.
        from_date : str, Optional
            Start date ('YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'). Defaults to 30 days ago if None.
        to_date : str, Optional
            End date ('YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'). Defaults to now if None.

    Returns:
        dict:
            - status (str):  
                "success" if the operation completed successfully; otherwise "error".
            - message (str):  
                Details about the retrieval outcome.
            - candles (List[Dict[str, Any]]):  
                List of candlestick records, each dict contains 'time', 'open', 'high',
                'low', 'close', 'tick_volume', 'spread', 'real_volume'. Ordered by descending time.

    Raises:
        RuntimeError:
            - If symbol not found.
            - If timeframe invalid.
            - If date parsing fails.
            - If unable to communicate with MT5.
    """
    logger.info(f"Fetching historical candles for {symbol_name} {timeframe} from {from_date} to {to_date}")

    logger.info(f"Symbol: {mt5.symbol_info(symbol_name)}")
    if not mt5.symbol_info(symbol_name):
        logger.error(f"Symbol '{symbol_name}' not found")
        
        raise RuntimeError(f"Symbol '{symbol_name}' not found")
    
    tf = TIMEFRAME_MAP.get(timeframe)
    if tf is None:
        logger.error(f"Invalid timeframe: '{timeframe}'")
        
        raise RuntimeError(f"Invalid timeframe: '{timeframe}'")

    end_dt = _parse_date(to_date, end_of_day=True) if to_date else datetime.now(timezone.utc)
    start_dt = _parse_date(from_date) if from_date else end_dt - timedelta(days=30)
    if start_dt > end_dt:
        return {
            "status": "error",
            "message": "Start date is greater than end date",
            "candles": []
        }

    try: 
        if from_date and to_date:
            logger.info("Getting candles from start date to end date")
            rates = mt5.copy_rates_range(symbol_name, tf, start_dt, end_dt)
        elif from_date:
            logger.info("Getting historical candles from start date")
            end_back = start_dt + timedelta(days=30)
            rates = mt5.copy_rates_range(symbol_name, tf, start_dt, end_back)
        elif to_date:
            logger.info("Getting historical candles from end date")
            start_back = end_dt - timedelta(days=30)
            rates = mt5.copy_rates_range(symbol_name, tf, start_back, end_dt)
        else:
            logger.info("Getting latest 100 bars")  
            rates = mt5.copy_rates_from_pos(symbol_name, tf, 0, 100)

        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"Failed to retrieve candles for {symbol_name} {timeframe}"
            )
        
        data: List[Dict[str, Any]] = []
        field_names = rates.dtype.names or []
        for entry in rates:
            row = {field: entry[field] for field in field_names}
            data.append(row)
        logger.info(f"Retrieved {len(data)} candles")

        return {
            "status": "success",
            "message": "Candles retrieved successfully",
            "candles": data
        }
    
    except Exception as e:
        logger.error(f"Error fetching candles: {e}")
        
        raise RuntimeError(f"Error fetching candles: {e}")