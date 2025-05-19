from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from utils.logger import logger
from utils.mt5_client import mt5
from utils.mcp_client import mcp

@mcp.tool()
def fetch_deals(
    from_date: Optional[str] = None,
    to_date:   Optional[str] = None,
    group:     Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetches historical deals from the MetaTrader 5 terminal.

    Queries `mt5.history_deals_get()` over the given date range and optional symbol mask,
    returning a list of executed-deal records.

    Parameters:
        from_date (str, optional):
            Start of the query range in 'YYYY-MM-DD' format.  
            Defaults to 30 days before now if None.
        to_date (str, optional):
            End of the query range in 'YYYY-MM-DD' format.  
            Defaults to current datetime if None.
        group (str, optional):
            A symbol filter mask (e.g. 'EURUSD*', '*BTC*').  
            If None, all symbols are returned.

    Raises:
        RuntimeError:
            - If `mt5.history_deals_get()` throws or returns None (with MT5 error code).
            - If date parsing fails.

    Returns:
        dict:
            - status  (str): "success" or "error"
            - message (str): Details about the retrieval outcome
            - deals   (List[TradeDeal]):
                List of MT5 `TradeDeal` named tuples, each with fields such as:
                    - ticket       (int)
                    - order        (int)
                    - time         (int): Epoch seconds when deal executed
                    - time_msc     (int): Epoch milliseconds when executed
                    - type         (int)
                    - entry        (int)
                    - magic        (int)
                    - position_id  (int)
                    - reason       (int)
                    - volume       (float)
                    - price        (float)
                    - commission   (float)
                    - swap         (float)
                    - profit       (float)
                    - fee          (float)
                    - symbol       (str)
                    - comment      (str)
                    - external_id  (str)
                    - …and any other fields provided by MT5
    """
    logger.info(f"Fetching deals from {from_date} to {to_date} for group {group}")

    try:
        if to_date and not from_date:
            msg = "Invalid input: 'to_date' is provided but 'from_date' is missing"
            logger.error(msg)
            return {
                "status": "error",
                "message": msg
            }
        
        from_date = datetime.strptime(from_date, "%Y-%m-%d") if from_date else datetime.now() - timedelta(days=30)
        to_date = datetime.strptime(to_date, "%Y-%m-%d") if to_date else datetime.now()

        logger.info(f"Retrieving deals by date range: {from_date} to {to_date}")

        if to_date < from_date:
            msg = f"Invalid date range: 'to_date' ({to_date}) is earlier than 'from_date' ({from_date})"
            logger.error(msg)
            return {
                "status": "error",
                "message": msg
            }
        
        if group is not None:
            deals = mt5.history_deals_get(from_date, to_date, group=group)
        else:
            deals = mt5.history_deals_get(from_date, to_date)

    except Exception as e:
        error_code = -1
        if hasattr(mt5, 'last_error'):
            error = mt5.last_error()
            if error and len(error) > 1:
                error_code = error[0]
        msg = f"Failed to retrieve deals history: {str(e)}"
        logger.error(msg)
        
        raise RuntimeError(msg, error_code)
    
    if deals is None:
        error = mt5.last_error()
        msg = f"Failed to retrieve deals history: {error[1]}"
        logger.error(msg)
        
        raise RuntimeError(msg, error[0])
    
    if len(deals) == 0:
        logger.info("No deals found with the specified parameters.")
        
        return {
            "status": "success",
            "message": "No deals found with the specified parameters.",
            "deals": []
        }
    
    result = [deal._asdict() for deal in deals]
    logger.info(f"Retrieved {len(result)} deals.")
    
    return {
        "status": "success",
        "message": "Deals retrieved successfully",
        "deals": result
    }
