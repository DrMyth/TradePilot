from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from utils.logger import logger
from utils.mt5_client import mt5
from utils.mcp_client import mcp

@mcp.tool()
def fetch_deals_count(
    from_date: Optional[str] = None,
    to_date:   Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the total count of historical deals in a specified date range.

    This tool calls `mt5.history_deals_total()` between two dates (inclusive),
    converting optional ISO-format strings into datetimes and defaulting to
    the last 30 days if no dates are supplied.

    Parameters:
        from_date (str, optional):
            Start of the query range in 'YYYY-MM-DD' format.
            Defaults to 30 days before now if None.
        to_date (str, optional):
            End of the query range in 'YYYY-MM-DD' format.
            Defaults to the current datetime if None.

    Returns:
        dict: A dictionary containing the following keys:
            - status (str): "success" if the deal count retrieval was successful, "error" otherwise.
            - message (str): A message indicating the result of the deal count retrieval.
            - deal_count (int): Total number of deals in the specified range.

    Raises:
        RuntimeError:
            - If MT5 returns an error code or the count is invalid.
            - If date parsing fails.
    """
    logger.debug(f"Fetching deals count from {from_date} to {to_date}")

    try:
        if to_date and not from_date:
            msg = "Invalid input: 'to_date' is provided but 'from_date' is missing"
            logger.error(msg)
            return {
                "status": "error",
                "message": msg
            }
        
        from_date = (datetime.strptime(from_date, '%Y-%m-%d') if from_date else datetime.now() - timedelta(days=30))
        to_date   = (datetime.strptime(to_date,   '%Y-%m-%d') if to_date   else datetime.now())

        logger.info(f"Retrieving deals by date range: {from_date} to {to_date}")

        if to_date < from_date:
            msg = f"Invalid date range: 'to_date' ({to_date}) is earlier than 'from_date' ({from_date})"
            logger.error(msg)
            return {
                "status": "error",
                "message": msg
        }

        deal_count = mt5.history_deals_total(from_date, to_date)

        if deal_count is None or deal_count < 0:
            error = mt5.last_error()
            msg = f"Failed to retrieve deal count: {error[1]}"
            logger.error(msg)
            raise RuntimeError(msg, error[0])

        logger.info(f"Retrieved deal count: {deal_count}")
        return {
            "status": "success",
            "message": "Deal count retrieved successfully",
            "deal_count": deal_count
        }

    except Exception as e:
        error_code = -1
        if hasattr(mt5, 'last_error'):
            error = mt5.last_error()
            if error and len(error) > 1:
                error_code = error[0]
        msg = f"Exception while retrieving deal count: {str(e)}"
        logger.error(msg)
        
        raise RuntimeError(msg, error_code)