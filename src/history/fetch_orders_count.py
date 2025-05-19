from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from utils.logger import logger
from utils.mt5_client import mt5
from utils.mcp_client import mcp

@mcp.tool()
def fetch_orders_count(
    from_date: Optional[str] = None,
    to_date:   Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch the total number of historical orders executed over a given date range.

    This tool calls `mt5.history_orders_total()` to retrieve the count of all orders
    placed (and filled) between two dates. Dates must be provided in ISO format
    (YYYY-MM-DD); if omitted, the range defaults to the last 30 days up to now.

    Parameters:
        from_date (str, optional):
            Start of the query range, formatted as 'YYYY-MM-DD'.
            Defaults to 30 days before the current date if None.
        to_date (str, optional):
            End of the query range, formatted as 'YYYY-MM-DD'.
            Defaults to the current date and time if None.

    Raises:
        RuntimeError:
            - If `mt5.history_orders_total()` throws or returns None (with MT5 error code).
            - If date parsing fails.
    
    Returns:
        dict:
            - status (str):  
                "success" if the operation completed successfully; otherwise "error".
            - message (str):  
                Details about the retrieval outcome.
            - orders_count (int):  
                Total number of historical orders found in the specified range.
    """
    logger.debug(f"Fetching orders count from {from_date} to {to_date}")
    
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

        logger.info(f"Retrieving orders by date range: {from_date} to {to_date}")

        if to_date < from_date:
            msg = f"Invalid date range: 'to_date' ({to_date}) is earlier than 'from_date' ({from_date})"
            logger.error(msg)
            return {
                "status": "error",
                "message": msg
            }

        total_orders = mt5.history_orders_total(from_date, to_date)

        if total_orders is None:
            error = mt5.last_error()
            msg = f"Failed to get total orders: {error[1]}"
            logger.error(msg)
            
            raise RuntimeError(msg, error[0])

        logger.info(f"Total number of historical orders: {total_orders}")
        
        return {
            "status": "success",
            "message": "Orders count retrieved successfully",
            "orders_count": total_orders
        }

    except Exception as e:
        error_code = -1
        if hasattr(mt5, 'last_error'):
            error = mt5.last_error()
            if error and len(error) > 1:
                error_code = error[0]
        msg = f"Error while retrieving total historical orders: {str(e)}"
        logger.error(msg)
        
        raise RuntimeError(msg, error_code)