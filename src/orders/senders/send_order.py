from typing import Dict, Union, Any
from utils.mappings.mapping_utils import to_code
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mappings.order_type_mapping import ORDER_TYPE_MAP
from utils.mappings.order_filling_mapping import ORDER_FILLING_MAP

@mcp.tool()
def send_order(
    action: Union[str, int] | None = None,
    symbol: str | None = None,
    volume: float | None = None,
    order_type: Union[str, int] | None = None,
    price: float | None = 0.0,
    stop_loss: float | None = 0.0,
    take_profit: float | None = 0.0,
    position: int | None = 0,
    position_by: int | None = 0,
    order: int | None = 0,
    expiration: str | None = None,
    type_filling: Union[int, str] | None = None,
    type_time: Union[int, str] | None = None,
    deviation: int = 20,
    magic: int = 0,
    comment: str = "via TradePilot",
) -> Dict[str, Any]:
    """
    Universal MT5 order helper with full action support and detailed logging.

    Wraps MT5's order_send to handle market, pending, SL/TP updates, modifications,
    cancellations, and close-by operations with consistent logging.

    Supports:
    - Market orders (DEAL)
    - Pending orders (PENDING)
    - Stop-loss/Take-profit updates (SLTP)
    - Pending-order modifications (MODIFY)
    - Pending-order cancellations (REMOVE)
    - Position closure by opposite ticket (CLOSE_BY)

    Parameters:
        action : str or int, optional
            MT5 trade action name or constant (e.g., 'DEAL', mt5.TRADE_ACTION_DEAL -> 1).
        symbol : str, optional
            Trading instrument symbol (e.g., 'EURUSD'). Required for most actions.
        volume : float, optional
            Trade volume in lots (>0 and ≤100). Required for new and pending orders.
        order_type : str or int, optional
            MT5 order type name or constant (e.g., 'BUY', 'SELL_STOP_LIMIT' -> 6).
        price : float, optional
            Entry or modification price; pulls current tick if omitted for DEAL.
        stop_loss : float, optional
            Stop-loss level.
        take_profit : float, optional
            Take-profit level.
        deviation : int, optional
            Maximum slippage in points. Defaults to 20.
        magic : int, optional
            EA magic number. Defaults to 0.
        comment : str, optional
            Order comment. Defaults to 'via TradePilot'.
        position : int, optional
            Position ticket for SLTP or CLOSE_BY actions.
        position_by : int, optional
            Opposite position ticket for CLOSE_BY action.
        order : int, optional
            Pending-order ticket for MODIFY or REMOVE actions.
        expiration : datetime, optional
            Expiration time for pending orders (ORDER_TIME_SPECIFIED).
        type_filling : str or int, optional
            Filling mode name or constant (e.g., 'FOK', mt5.ORDER_FILLING_IOC).
        type_time : str or int, optional
            Time mode name or constant (e.g., 'GTC', mt5.ORDER_TIME_DAY).

    Returns:
        dict:
            - status (str):
                'success' if order executed; otherwise 'error'.
            - message (str):
                Details of outcome or error description.
            - data (dict):
                MT5 OrderSendResult fields and 'request' details if successful; None on error.
    """

    logger.info(f"Initializing Order with: action={action}, symbol={symbol}, volume={volume}, order_type={order_type}")

    if action is None:
        msg = "Action is required"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    act = action if isinstance(action, int) else (action or "").upper()
    logger.info(f"Normalized action initial: {act}")
    if isinstance(act, str):
        try:
            act = getattr(mt5, f"TRADE_ACTION_{act}")
        except Exception:
            msg = f"Unknown action '{action}'"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
    logger.info(f"Resolved action constant: {act}")

    if isinstance(order_type, str):
        ocode = ORDER_TYPE_MAP.get(order_type.upper())
        if ocode is None:
            msg = f"Unknown order_type '{order_type}'"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
    else:
        ocode = order_type
    logger.info(f"Order type code: {ocode}")

    symbol_info = None
    if symbol:
        logger.info(f"Selecting symbol: {symbol}")
        if not mt5.symbol_select(symbol, True):
            msg = f"Cannot select symbol '{symbol}'"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        symbol_info = mt5.symbol_info(symbol)

        if symbol_info is None:
            msg = f"No symbol info for '{symbol}'"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        logger.info(f"Symbol info: {symbol_info}")

        selected_filling = to_code(type_filling, ORDER_FILLING_MAP) if type_filling is not None else None
        logger.info(f"Selected filling mode: {selected_filling}")

    price = float(price)
    if not isinstance(price, float):
        msg = "Invalid price"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    req: Dict = {"action": act}
    if symbol:   req["symbol"] = symbol
    if volume is not None:
        if not isinstance(volume, (int, float)) or volume <= 0 or volume > 100:
            logger.error(f"Invalid volume: {volume}")
            return {"status": "error", "message": "Volume must be a number >0 and ≤100", "data": None}
        req["volume"] = float(volume)

    if ocode is not None:
        req["type"] = ocode
    req["deviation"] = deviation
    req["magic"]     = magic
    req["comment"]   = comment or "via TradePilot"
    logger.info(f"Base request built: {req}")

    match act:
        case mt5.TRADE_ACTION_DEAL:
            logger.info("DEAL: Market Order Processing")

            if symbol is None:
                msg = "Symbol is required"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
        
            if not volume:
                msg = "Volume is required"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            if volume <= 0 or volume > 100:
                msg = "Volume must be a number >0 and ≤100"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            if ocode not in (mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL):
                msg = f"DEAL requires BUY or SELL, got: {ocode}"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                msg = f"Cannot retrieve market price for: {symbol}"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            req["price"] = tick.ask if ocode == mt5.ORDER_TYPE_BUY else tick.bid

            if stop_loss and take_profit:
                sl = float(stop_loss)
                tp = float(take_profit)
                if ocode == mt5.ORDER_TYPE_BUY and not (sl < tick.ask < tp):
                    msg = "For BUY orders: stop_loss < entry_price < take_profit required"
                    logger.error(msg)
                    return {"status": "error", "message": msg, "data": None}
                if ocode == mt5.ORDER_TYPE_SELL and not (tp < tick.ask < sl):
                    msg = "For SELL orders: take_profit < entry_price < stop_loss required"
                    logger.error(msg)
                    return {"status": "error", "message": msg, "data": None}

            if stop_loss:   req["sl"] = float(stop_loss)
            if take_profit: req["tp"] = float(take_profit)
            if selected_filling: req["type_filling"] = selected_filling

        case mt5.TRADE_ACTION_PENDING:
            logger.info("PENDING: Pending Order Processing")

            if symbol is None:
                msg = "Symbol is required"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            if not volume:
                msg = "Volume is required"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            if volume <= 0 or volume > 100:
                msg = "Volume must be a number >0 and ≤100"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
    
            valid = (
                mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT,
                mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_STOP,
                mt5.ORDER_TYPE_BUY_STOP_LIMIT, mt5.ORDER_TYPE_SELL_STOP_LIMIT
            )

            if ocode not in valid:
                msg = f"Invalid PENDING order type: {ocode}"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            if not price:
                msg = "PENDING orders require a price"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            req["price"] = float(price)
            if isinstance(type_filling, str) or isinstance(type_filling, int):
                req["type_filling"] = selected_filling

            if expiration:
                req["type_time"] = (
                    type_time if isinstance(type_time, int)
                    else getattr(mt5, f"ORDER_TIME_{type_time.upper()}", mt5.ORDER_TIME_SPECIFIED)
                )
                req["expiration"] = expiration
            else:
                req["type_time"] = (
                    type_time if isinstance(type_time, int)
                    else mt5.ORDER_TIME_GTC
                )
            
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
                
            if stop_loss:   req["sl"] = float(stop_loss)
            if take_profit: req["tp"] = float(take_profit)

        case mt5.TRADE_ACTION_SLTP:
            logger.info("SLTP: Modify SL/TP")

            if position is None:
                msg = "SLTP requires a position ticket"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}

            pos = mt5.positions_get(ticket=position)
            logger.info(f"Position: {pos}")

            if not pos or len(pos) != 1:
                msg = f"Failed to retrieve position with ticket {position}"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}

            current = pos[0]

            sl = float(stop_loss) if stop_loss else None
            tp = float(take_profit) if take_profit else None

            if current.type == 1:
                if current.price_current > sl:
                    msg = f"SLTP error: stop_loss {sl} must be greater than current price {current.price_current}"
                    logger.error(msg)
                    return {"status": "error", "message": msg, "data": None}
                if current.price_current < tp:
                    msg = f"SLTP error: take_profit {tp} must be less than current price {current.price_current}"
                    logger.error(msg)
                    return {"status": "error", "message": msg, "data": None}
            elif current.type == 0:
                if current.price_current < sl:
                    msg = f"SLTP error: stop_loss {sl} must be less than current price {current.price_current}"
                    logger.error(msg)
                    return {"status": "error", "message": msg, "data": None}
                if current.price_current > tp:
                    msg = f"SLTP error: take_profit {tp} must be greater than current price {current.price_current}"
                    logger.error(msg)
                    return {"status": "error", "message": msg, "data": None}
                
            req["position"] = position
            req["sl"] = sl if sl else current.sl
            req["tp"] = tp if tp else current.tp

        case mt5.TRADE_ACTION_MODIFY:
            logger.info("MODIFY: Modify pending order")

            if not order:
                msg = "MODIFY requires an order ticket"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            req["order"] = order

            if price:       req["price"] = float(price)
            if stop_loss:   req["sl"]    = float(stop_loss)
            if take_profit: req["tp"]    = float(take_profit)

        case mt5.TRADE_ACTION_REMOVE:
            logger.info("REMOVE: Remove pending order")

            if not order:
                msg = "REMOVE requires an order ticket"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            pending_orders = mt5.orders_get(ticket=order)
            if not pending_orders:
                msg = f"No pending orders found with ticket {order}"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            if len(pending_orders) != 1:
                msg = f"Expected 1 pending order, got {len(pending_orders)}"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}   
            
            req["order"] = order

        case mt5.TRADE_ACTION_CLOSE_BY:
            logger.info("CLOSE_BY: Close by")

            position_get = mt5.positions_get(ticket=position)
            logger.info(f"Position: {position_get}")
            position_by_get = mt5.positions_get(ticket=position_by)
            logger.info(f"Position by: {position_by_get}")

            if not position_get or len(position_get) != 1:
                msg = f"Failed to retrieve position with ticket {position}"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            if not position_by_get or len(position_by_get) != 1:
                msg = f"Failed to retrieve position with ticket {position_by}"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}

            position_symbol = position_get[0].symbol
            position_by_symbol = position_by_get[0].symbol
            position_vol = position_get[0].volume
            position_by_vol = position_by_get[0].volume

            if position_by_vol > position_vol:
                logger.info(f"Swapping close_by roles because position_by.volume ({position_by_vol}) > position.volume ({position_vol})")
                position, position_by = position_by, position
                position_vol, position_by_vol = position_by_vol, position_vol

            if position_symbol != position_by_symbol:
                msg = f"Position and position_by must be on the same symbol"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}

            if not position or not position_by:
                msg = "CLOSE_BY needs position & position_by"
                logger.error(msg)
                return {"status": "error", "message": msg, "data": None}
            
            req["position"]    = position
            req["position_by"] = position_by

        case _:
            msg = f"Unsupported action: {act}"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}

    logger.info(f"Final request payload: {req}")
    result = mt5.order_send(req)
    err, desc = mt5.last_error()
    logger.info(f"Error code: {err}, Error description: {desc}")
    
    if err != 1:
        msg = f"MT5 error {err}: {desc}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    logger.info(f"Order sent successfully: {result}")

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

    return {
        "status": "success",
        "message": "Order sent successfully!",
        "data": mt5_res
    }