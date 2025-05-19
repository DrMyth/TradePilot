from typing import Dict, Optional, Union, Any
from utils.mt5_client import mt5
from utils.mcp_client import mcp
from utils.logger import logger
from utils.mappings.order_type_mapping import ORDER_TYPE_MAP

@mcp.tool()
def send_market_order(
    symbol: str,
    volume: float,
    order_type: Union[str, int],
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    deviation: int = 20,
    magic: int = 0,
    comment: str = "via TradePilot"
) -> Dict[str, Any]:
    """
    Place a market (instant execution) order on MT5 for a specified symbol.

    Sends a buy or sell market order with optional stop loss and take profit levels,
    handling symbol selection, price determination, and MT5 error reporting.

    Parameters:
        symbol : str
            Trading instrument symbol (e.g., 'EURUSD').
        volume : float
            Trade volume in lots. Must be >0 and ≤100.
        order_type : str or int
            'BUY' or 'SELL' (case-insensitive) or corresponding MT5 constant.
        stop_loss : float, Optional
            Stop-loss price level. Defaults to None (no stop loss).
        take_profit : float, Optional
            Take-profit price level. Defaults to None (no take profit).
        deviation : int, Optional
            Maximum allowed slippage in points. Defaults to 20.
        magic : int, Optional
            Expert Advisor magic number. Defaults to 0.
        comment : str, Optional
            Order comment. Defaults to 'via TradePilot'.

    Returns:
        dict:
            - status (str):  
                'success' if order placed; 'error' otherwise.
            - message (str): 
                Description of outcome or error details.
            - data (dict):  
                MT5 OrderSendResult as dict including 'request' fields if successful; None on failure.
    """
    logger.info(f"Initiating market order: symbol={symbol}, volume={volume}, type={order_type}")

    if isinstance(order_type, str):
        code = ORDER_TYPE_MAP.get(order_type.upper())
        if code is None:
            msg = f"Unknown market order_type '{order_type}'"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
    else:
        code = order_type
    logger.info(f"Normalized order type: {code}")

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        msg = f"Cannot retrieve market price for: {symbol}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    if stop_loss and take_profit:
        sl = float(stop_loss)
        tp = float(take_profit)
        if code == mt5.ORDER_TYPE_BUY and not (sl < tick.ask < tp):
            msg = "For BUY orders: stop_loss < entry_price < take_profit required"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}
        if code == mt5.ORDER_TYPE_SELL and not (tp < tick.ask < sl):
            msg = "For SELL orders: take_profit < entry_price < stop_loss required"
            logger.error(msg)
            return {"status": "error", "message": msg, "data": None}

    if not mt5.symbol_select(symbol, True):
        msg = f"Cannot select symbol '{symbol}'"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    logger.info(f"Selected symbol: {symbol}")

    if volume <= 0 or volume > 100:
        msg = f"Volume must be a number >0 and ≤100"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        msg = f"No tick data available for '{symbol}'"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    logger.info(f"Tick data: {tick}")

    entry_price = tick.ask if code == mt5.ORDER_TYPE_BUY else tick.bid
    logger.info(f"Entry price: {entry_price}")

    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": code,
        "price": entry_price,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
    }

    if stop_loss:
        req["sl"] = float(stop_loss)
    if take_profit:
        req["tp"] = float(take_profit)
    logger.debug(f"Market order request: {req}")

    result = mt5.order_send(req)
    error_code, error_desc = mt5.last_error()
    logger.info(f"Error code: {error_code}, Error description: {error_desc}")

    if error_code != 1:
        msg = f"MT5 market order failed {error_code}: {error_desc}"
        logger.error(msg)
        return {"status": "error", "message": msg, "data": None}
    
    logger.info(f"Market order placed successfully: {result}")
    data = result._asdict()
    data["request"] = result.request._asdict()
    return {"status": "success", "message": "Market order placed successfully!", "data": data}