from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from utils.logger import logger
from utils.mt5_client import mt5
from utils.mcp_client import mcp

@mcp.tool()
def fetch_orders(
    from_date: Optional[str] = None,
    to_date:   Optional[str] = None,
    group:     Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch historical order records from the MetaTrader 5 terminal.

    This tool wraps the `mt5.history_orders_get()` API call to retrieve all orders
    executed within a specified date range, optionally filtered by a symbol mask.

    Parameters:
        from_date (str, optional):
            ISO-formatted start date ('YYYY-MM-DD'). Defaults to 30 days before now
            if omitted or None.
        to_date (str, optional):
            ISO-formatted end date ('YYYY-MM-DD'). Defaults to the current datetime
            if omitted or None.
        group (str, optional):
            Symbol filter mask (e.g. 'EURUSD*', '*USD*'). When provided, only orders
            whose symbol matches this pattern are returned; otherwise, all symbols
            are included.

    Raises:
        RuntimeError:
            - If date parsing fails.
            - If unable to communicate with the MT5 terminal.
            - If the MT5 API call returns None or reports an error code.

    Returns:
        dict:
            A response envelope containing:
            - status (str):
                "success" if the retrieval was successful.
            - message (str):
                Details about the retrieval outcome.
            - orders (List[Dict[str, Any]]):
                A list of order records, each represented as a dictionary with keys such as:
                    - ticket (int)
                    - time_setup (int): Epoch seconds when the order was placed
                    - time_setup_msc (int): Epoch milliseconds when placed
                    - time_done (int): Epoch seconds when executed
                    - time_done_msc (int): Epoch milliseconds when executed
                    - time_expiration (int): Expiration time for pending orders
                    - type (int): Order type code (market, limit, stop, etc.)
                    - type_time (int): Time type for order (GTC, IOC, etc.)
                    - type_filling (int): Filling policy (e.g., FOK, IOC)
                    - state (int): Current order state code
                    - magic (int): Expert Advisor identifier
                    - position_id (int): ID of the resulting position
                    - volume_initial (float): Original volume requested
                    - volume_current (float): Remaining volume after partial fills
                    - price_open (float): Opening price for market orders
                    - price_current (float): Current order price (for pending)
                    - sl (float): Stop-loss level
                    - tp (float): Take-profit level
                    - price_stoplimit (float): Stop-limit price (for stop-limit orders)
                    - symbol (str): Trading symbol
                    - comment (str): Order comment
                    - external_id (str): External identifier
                    - …and any additional fields provided by the MT5 API
    """

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

        if group is not None:
            orders = mt5.history_orders_get(from_date, to_date, group=group)
        else:
            orders = mt5.history_orders_get(from_date, to_date)

    except Exception as e:
        error_code = -1
        if hasattr(mt5, 'last_error'):
            error = mt5.last_error()
            if error and len(error) > 1:
                    error_code = error[0]
            msg = f"Failed to retrieve orders history: {str(e)}"
            logger.error(msg)
            
            raise RuntimeError(msg, error_code)
        
    if orders is None:
            error = mt5.last_error()
            msg = f"Failed to retrieve orders history: {error[1]}"
            logger.error(msg)
            
            raise RuntimeError(msg, error[0])
    
    if len(orders) == 0:
            logger.info("No orders found with the specified parameters.")
            
            return {
                "status": "success",
                "message": "No orders found with the specified parameters.",
                "orders": []
            }
    
    result = [order._asdict() for order in orders]
    logger.info(f"Retrieved {len(result)} orders.")
    
    return {
        "status": "success",
        "message": "Orders retrieved successfully",
        "orders": result
    }
