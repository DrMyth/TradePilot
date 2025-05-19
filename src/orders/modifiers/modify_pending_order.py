from typing import Dict, Optional, Any
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger
from orders.fetchers.fetch_pending_orders import fetch_pending_orders

@mcp.tool()
def modify_pending_order(
    order_ticket: int,
    price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Modify an existing MT5 pending order's price, stop-loss, and/or take-profit.

    Retrieves the specified pending order, applies any provided new values, and
    sends a modify request. Unspecified fields retain their current settings.

    Parameters:
        order_ticket : int
            Ticket number of the pending order to modify.
        price : float, optional
            New trigger price. If None, retains existing order price.
        stop_loss : float, optional
            New stop-loss level. If None, retains existing SL.
        take_profit : float, optional
            New take-profit level. If None, retains existing TP.

    Returns:
        dict:
            - status (str):
                'success' if modification succeeded; otherwise 'error'.
            - message (str):
                Details of the outcome or error description.
            - data (dict):
                MT5 OrderSendResult as dict if successful; None on error.
    """
    logger.info(f"Initiating modify pending order: order={order_ticket}, price={price}, stop_loss={stop_loss}, take_profit={take_profit}")

    try:
        order_id = int(order_ticket)
    except (TypeError, ValueError):
        msg = f"Invalid order ID: {order_ticket}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    if order_ticket <= 0:
        msg = f"Invalid order_ticket: {order_ticket}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    if len(str(order_ticket)) != 9:
        msg = "Order ticket must be a 9-digit number"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    orders = fetch_pending_orders(ticket=order_id)
    if not orders:
        msg = f"No pending order found with ID {order_id}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    existing_order = orders["data"]["pending_orders"][0]
    final_price = float(price) if price is not None else float(existing_order["open"])

    req = {
        "action": mt5.TRADE_ACTION_MODIFY, 
        "order": order_id,
        "price": final_price,
    }

    symbol = existing_order["symbol"]
    ocode = existing_order["type"]

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        msg = f"Cannot retrieve market price for: {symbol}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    p = float(price)
    sl = float(stop_loss) if stop_loss else None
    tp = float(take_profit) if take_profit else None
    current = tick.ask if ocode in (mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_BUY_STOP_LIMIT) else tick.bid
    mp = (tick.bid + tick.ask) / 2

    if ocode == mt5.ORDER_TYPE_BUY_LIMIT:
        if not (p < mp):
            msg = f"BUY_LIMIT requires price < market_price ({p} ≥ {mp})"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if sl is not None and not (sl < p):
            msg = f"BUY_LIMIT requires stop_loss < price ({sl} ≥ {p})"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if tp is not None and not (p < tp):
            msg = f"BUY_LIMIT requires price < take_profit ({p} ≥ {tp})"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
    elif ocode == mt5.ORDER_TYPE_SELL_LIMIT:
        if not (p > mp):
            msg = f"SELL_LIMIT requires price > market_price ({p} ≤ {mp})"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if tp is not None and not (tp < p):
            msg = f"SELL_LIMIT requires take_profit < price ({tp} ≥ {p})"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if sl is not None and not (p < sl):
            msg = f"SELL_LIMIT requires price < stop_loss ({p} ≥ {sl})"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
    elif ocode == mt5.ORDER_TYPE_BUY_STOP:
        if not (p > mp):
            msg = f"BUY_STOP requires price > market_price ({p} ≤ {mp})"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if sl is not None and not (sl < p):
            msg = f"BUY_STOP requires stop_loss < price ({sl} ≥ {p})"
            logger.error(msg)
            return {"status":"error","message":msg,"data":None}
        if tp is not None and not (p < tp):
            msg = f"BUY_STOP requires price < take_profit ({p} ≥ {tp})"
            logger.error(msg)
            return {"status":"error","message":msg,"data":None}
    elif ocode == mt5.ORDER_TYPE_SELL_STOP:
        if not (p < mp):
            msg = f"SELL_STOP requires price < market_price ({p} ≥ {mp})"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if sl is not None and not (p < sl):
            msg = f"SELL_STOP requires price < stop_loss ({p} ≥ {sl})"
            logger.error(msg)
            return {"status":"error","message":msg,"data":None}
        if tp is not None and not (tp < p):
            msg = f"SELL_STOP requires take_profit < price ({tp} ≥ {p})"
            logger.error(msg)
            return {"status":"error","message":msg,"data":None}
    elif ocode == mt5.ORDER_TYPE_BUY_STOP_LIMIT:
        if not (current < p):
            msg = f"BUY_STOP_LIMIT trigger price {p} must be above market {current}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if sl is not None and not (current < sl):
            msg = f"BUY_STOP_LIMIT stop_loss {sl} must sit above market {current}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if tp is not None and not (sl < tp if sl is not None else p < tp):
            msg = f"BUY_STOP_LIMIT requires stop_loss {sl or p} < take_profit {tp}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
    elif ocode == mt5.ORDER_TYPE_SELL_STOP_LIMIT:
        if not (current > p):
            msg = f"SELL_STOP_LIMIT trigger price {p} must be below market {current}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if sl is not None and not (sl < current):
            msg = f"SELL_STOP_LIMIT stop_loss {sl} must sit below market {current}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if tp is not None and not (tp < sl if sl is not None else tp < p):
            msg = f"SELL_STOP_LIMIT requires take_profit {tp} < stop_loss {sl or p}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}

    if stop_loss:
        req["sl"] = float(stop_loss)
    if take_profit:
        req["tp"] = float(take_profit)

    logger.info(f"Modify request payload: {req}")

    result = mt5.order_send(req)

    err, desc = mt5.last_error()
    if err != 1:
        msg = f"MT5 modify pending failed {err}: {desc}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    mt5_res = result._asdict()
    req_struct = result.request

    req_dict = {
        "action":         req_struct.action,
        "symbol":         req_struct.symbol,
        "volume":         req_struct.volume,
        "price":          req_struct.price,
        "sl":             req_struct.sl,
        "tp":             req_struct.tp,
        "deviation":      req_struct.deviation,
        "magic":          req_struct.magic,
        "order":          req_struct.order,
        "position":       req_struct.position,
        "type":           req_struct.type,
        "type_filling":   req_struct.type_filling,
        "type_time":      req_struct.type_time,
        "expiration":     req_struct.expiration,
        "comment":        req_struct.comment,
    }

    mt5_res["request"] = req_dict
    
    return {"status": "success", "message": "Order modified successfully!", "data": mt5_res}