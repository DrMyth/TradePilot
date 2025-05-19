import fnmatch
import re
from typing import Dict, List, Optional, Any
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mappings.mapping_utils import to_code
from utils.mappings.order_type_mapping import ORDER_TYPE_MAP

@mcp.tool()
def fetch_positions(
    ticket: Optional[int] = None,
    symbol_name: Optional[str] = None,
    group: Optional[str] = None,
    order_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch open positions from MT5 with optional filters.

    Retrieves current open positions, optionally filtered by ticket, symbol,
    group mask, or order type. Filters are applied in order of priority: ticket,
    symbol_name, group, then no filter.

    Parameters:
        ticket : int | str, Optional
            Fetch only the position with this ticket ID.
        symbol_name : str, Optional
            Fetch positions for this trading symbol (e.g., 'EURUSD').
        group : str, Optional
            Fetch positions matching this group mask. (e.g., '*USD', '*EUR*')
        order_type : str, Optional
            Order type key from ORDER_TYPE_MAP (e.g., 'BUY', 'SELL_STOP').

    Returns:
        dict:
            - status (str):  
                "success" if positions retrieved; otherwise "error".
            - message (str):  
                Details about the retrieval outcome.
            - data (List[Dict[str, Any]]):  
                List of position records or empty list on error.
    """
    logger.info(f"Getting positions with filters: ticket: {ticket}, symbol_name: {symbol_name}, group: {group}, order_type: {order_type}")

    invalid = []
    if order_type is not None and order_type not in ORDER_TYPE_MAP:
        invalid.append(("order_type", ORDER_TYPE_MAP))

    if invalid:
        field, mapping = invalid[0]
        return {
            "status": "error",
            "message": f"Invalid {field!r}: must be one of {list(mapping)}",
            "data": {"positions": []}
        }
    
    raw = mt5.positions_get()

    if not raw: 
        return {
            "status": "success",
            "message": "No open positions found on Terminal",
            "data": {
                "positions": []
            }
        }
    
    positions: List[Dict[str, Any]] = [p._asdict() for p in raw]

    if ticket is not None:
        try:
            ticket = int(ticket)
            positions = [p for p in positions if p.get("ticket") == ticket]
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid ticket",
                "data": {
                    "positions": []
                }
            }

    if symbol_name is not None:
        if not mt5.symbols_get(symbol_name):
            return {
                "status": "error",
                "message": "Invalid symbol name",
                "data": {
                    "positions": []
                }
            }
        positions = [p for p in positions if p.get("symbol") == symbol_name]

    if group is not None:
        positions = [p for p in positions if fnmatch.fnmatch(p.get("symbol"), group)]

    if order_type is not None:
        type_code = to_code(order_type, ORDER_TYPE_MAP)
        positions = [p for p in positions if p.get("type") == type_code]

    if len(positions) == 0:
        return {
            "status": "success",
            "message": "No positions found with the given filters",
            "data": {
                "positions": []
            }
        }
    
    logger.info(f"Positions: {positions}")
    
    return {
        "status": "success",
        "message": "Positions fetched successfully",
        "data": {
            "positions": positions
        }
    }