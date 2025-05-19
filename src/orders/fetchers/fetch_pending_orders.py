import fnmatch
from typing import Dict, List, Any
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mappings.mapping_utils import to_code
from utils.mappings.order_type_mapping import ORDER_TYPE_MAP
from utils.mappings.order_state_mapping import ORDER_STATE_MAP
from utils.mappings.order_filling_mapping import ORDER_FILLING_MAP
from utils.mappings.order_lifetime_mapping import ORDER_LIFETIME_MAP

@mcp.tool()
def fetch_pending_orders(
    ticket: int | None = None,
    symbol_name: str | None = None,
    group: str | None = None,
    order_type: str | None = None,
    order_state: str | None = None,
    order_filling: str | None = None,
    order_lifetime: str | None = None,
) -> Dict[str, Any]:
    """
    Fetch pending orders from MT5 with optional filters.

    Retrieves current pending (unfilled) orders, optionally filtered by ticket,
    symbol, group mask, order type, state, filling type, or lifetime. Filters are
    applied in order of priority: ticket, symbol_name, group, then full dataset.

    Parameters:
        ticket : int | str, Optional
            Order ticket ID to fetch (overrides other filters).
        symbol_name : str, Optional
            Trading symbol to filter by (e.g., 'EURUSD').
        group : str, Optional
            Symbol group mask to filter by (e.g., '*USD*').
        order_type : str, Optional
            Order type key from ORDER_TYPE_MAP (e.g., 'BUY_LIMIT').
        order_state : str, Optional
            Order state key from ORDER_STATE_MAP (e.g., 'PLACED').
        order_filling : str, Optional
            Filling type key from ORDER_FILLING_MAP (e.g., 'FOK').
        order_lifetime : str, Optional
            Lifetime type key from ORDER_LIFETIME_MAP (e.g., 'GTC').

    Returns:
        dict:
            - status (str):  
                "success" if orders retrieved; otherwise "error".
            - message (str):  
                Details about the retrieval outcome.
            - data (List[Dict[str, Any]]):  
                List of pending order records (as dicts), or empty list on error.
    """
    logger.info(f"Getting pending orders with filters: ticket: {ticket}, symbol_name: {symbol_name}, group: {group}, order_type: {order_type}, order_state: {order_state}, order_filling: {order_filling}, order_lifetime: {order_lifetime}")

    invalid = []
    if order_type      is not None and order_type      not in ORDER_TYPE_MAP:      invalid.append(("order_type",      ORDER_TYPE_MAP))
    if order_state     is not None and order_state     not in ORDER_STATE_MAP:     invalid.append(("order_state",     ORDER_STATE_MAP))
    if order_filling   is not None and order_filling   not in ORDER_FILLING_MAP:   invalid.append(("order_filling",   ORDER_FILLING_MAP))
    if order_lifetime  is not None and order_lifetime  not in ORDER_LIFETIME_MAP:  invalid.append(("order_lifetime",  ORDER_LIFETIME_MAP))
    if invalid:
        field, mapping = invalid[0]
        return {
            "status": "error",
            "message": f"Invalid {field!r}: must be one of {list(mapping)}",
            "data": {"pending_orders": []}
        }
    
    raw = mt5.orders_get()

    if not raw:
        return {
            "status": "success",
            "message": "No pending orders found on Terminal",
            "data": {
                "pending_orders": []
            }
        }

    orders: List[Dict] = [o._asdict() for o in raw]

    if ticket is not None:
        try:
            ticket = int(ticket)
            orders = [o for o in orders if o.get("ticket") == ticket]
        except (ValueError, TypeError):
            return {
                "status": "error",
                "message": "Invalid ticket",
                "data": {
                    "pending_orders": []
                }
            }
    
    if symbol_name is not None:
        if not mt5.symbols_get(symbol_name):
            return {
                "status": "error",
                "message": "Invalid symbol",
                "data": {
                    "pending_orders": []
                }
            }
        orders = [o for o in orders if o.get("symbol") == symbol_name]

    if group is not None:
        orders = [o for o in orders if fnmatch.fnmatch(o.get("symbol"), group)]


    result = []

    type_code = to_code(order_type, ORDER_TYPE_MAP)
    state_code = to_code(order_state, ORDER_STATE_MAP)
    filling_code = to_code(order_filling, ORDER_FILLING_MAP)
    lifetime_code = to_code(order_lifetime, ORDER_LIFETIME_MAP)

    logger.info(f"Type Code: {type_code}, State Code: {state_code}, Filling Code: {filling_code}, Lifetime Code: {lifetime_code}")

    for o in orders:
        if type_code is not None and o["type"] != type_code:
            continue
        if state_code is not None and o["state"] != state_code:
            continue
        if filling_code is not None and o["type_filling"] != filling_code:
            continue
        if lifetime_code is not None and o["type_time"] != lifetime_code:
            continue

        result.append(o)
    
    if not result:
        return {
            "status": "success",
            "message": "No pending orders found with the given filters",
            "data": {
                "pending_orders": []
            }
        }
    
    logger.info(f"Pending orders after filtering: {result}")

    return {
        "status": "success",
        "message": "Pending orders fetched successfully",
        "data": {
            "pending_orders": result
        }
    }