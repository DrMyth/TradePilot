from typing import Dict, Optional, Union, Any
from utils.mappings.mapping_utils import to_code
from utils.mappings.order_type_mapping import ORDER_TYPE_MAP
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger

@mcp.tool()
def send_pending_order(
    symbol: str,
    volume: float,
    order_type: Union[str, int],
    price: float,
    expiration: Optional[str] = None,      
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    type_filling: Optional[Union[str, int]] = None,
    type_time: Optional[Union[str, int]] = None,
    deviation: int = 20,
    magic: int = 0,
    comment: str = "via TradePilot"
) -> Dict[str, Any]:
    """
    Place a pending order (limit, stop, or stop-limit) on MT5.

    Supports placement of various pending order types with optional SL/TP,
    expiration, and filling/time modes.

    Parameters:
        symbol : str
            Trading instrument symbol (e.g., 'EURUSD').
        volume : float
            Trade volume in lots (>0 and ≤100).
        order_type : str or int
            Pending order type name or MT5 constant (e.g. 'BUY_LIMIT', mt5.ORDER_TYPE_SELL_STOP).
        price : float
            Order trigger price.
        expiration : datetime, optional
            Expiration time for ORDER_TIME_SPECIFIED; defaults to GTC if None.
        stop_loss : float, optional
            Stop-loss level.
        take_profit : float, optional
            Take-profit level.
        type_filling : str or int, optional
            Filling mode name or constant (e.g., 'FOK', mt5.ORDER_FILLING_IOC).
        type_time : str or int, optional
            Time mode name or constant (e.g., 'GTC', 'DAY', mt5.ORDER_TIME_SPECIFIED).
        deviation : int, optional
            Maximum slippage in points. Defaults to 20.
        magic : int, optional
            EA magic number. Defaults to 0.
        comment : str, optional
            Order comment. Defaults to 'via TradePilot'.

    Returns:
        dict:
            - status (str):
                'success' if order placed; otherwise 'error'.
            - message (str):
                Outcome description or error details.
            - data (dict):
                MT5 OrderSendResult dict including 'request' on success; None on error.
    """
    logger.info(f"Initiating pending order: {symbol}, volume={volume}, type={order_type}, price={price}")

    code = to_code(order_type, ORDER_TYPE_MAP)
    if code is None:
        msg = f"Invalid pending order_type '{order_type}'"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    logger.info(f"Resolved pending order type: {code}")

    valid = (
        mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT,
        mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_STOP,
        mt5.ORDER_TYPE_BUY_STOP_LIMIT, mt5.ORDER_TYPE_SELL_STOP_LIMIT
    )

    if code not in valid:
        msg = f"Invalid pending order type: {code}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    logger.info(f"Normalized order type: {code}")
    
    if not mt5.symbol_select(symbol, True):
        msg = f"Cannot select symbol '{symbol}'"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    logger.info(f"Selected symbol: {symbol}")

    if not price:
        msg = f"Price is required for pending order"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    req = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": float(volume),
        "type": code,
        "price": float(price),
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
    }

    if expiration:
        req["type_time"] = (type_time if isinstance(type_time, int)
                            else getattr(mt5, f"ORDER_TIME_{type_time.upper()}", mt5.ORDER_TIME_SPECIFIED))
        req["expiration"] = expiration
    else:
        req["type_time"] = (type_time if isinstance(type_time, int)
                              else mt5.ORDER_TIME_GTC)
        
    if type_filling:
        req["type_filling"] = (type_filling if isinstance(type_filling, int)
                                 else getattr(mt5, f"ORDER_FILLING_{type_filling.upper()}", None))
    
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        msg = f"Cannot get tick for symbol '{symbol}'"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    p = float(price)
    sl = float(stop_loss) if stop_loss else None
    tp = float(take_profit) if take_profit else None
    current = tick.ask if code in (mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_BUY_STOP_LIMIT) else tick.bid
    mp = (tick.bid + tick.ask) / 2

    if code == mt5.ORDER_TYPE_BUY_LIMIT:
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
    elif code == mt5.ORDER_TYPE_SELL_LIMIT:
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
    elif code == mt5.ORDER_TYPE_BUY_STOP:
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
    elif code == mt5.ORDER_TYPE_SELL_STOP:
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
    elif code == mt5.ORDER_TYPE_BUY_STOP_LIMIT:
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
    elif code == mt5.ORDER_TYPE_SELL_STOP_LIMIT:
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

    logger.info(f"Pending order request: {req}")

    result = mt5.order_send(req)
    err, desc = mt5.last_error()
    logger.info(f"Error code: {err}, Error description: {desc}")
    if err != 1:
        msg = f"MT5 pending order failed {err}: {desc}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    logger.info(f"Pending order sent successfully: {result}")
    data = result._asdict()
    data["request"] = result.request._asdict()
    
    return {"status": "success", "message": "Order sent successfully!", "data": data}