from typing import Dict, Any
from utils.logger import logger
from utils.mcp_client import mcp
from utils.mt5_client import mt5

@mcp.tool()
def calculate_lot_size(
    symbol: str,
    account_equity: float,
    risk_pct: float,
    stop_loss_pips: float
) -> Dict[str, Any]:
    """
    Calculate lot size for a trade based on account equity, risk percentage, and stop-loss in pips.

    Computes the appropriate lot size by calculating the monetary risk per trade and converting 
    value-per-point into the account's base currency if needed. Ensures input validation and 
    handles symbol lookup and currency conversion.

    Parameters:
        symbol : str
            Trading symbol (e.g., 'EURUSD').
        account_equity : float
            Total account equity available for trading.
        risk_pct : float
            Percentage of the equity to risk per trade (e.g., 2 for 2%).
        stop_loss_pips : float
            Stop-loss value in pips.

    Returns:
        dict:
            - status (str):
                "success" if the lot size is calculated successfully; otherwise "error".
            - message (str):
                Describes the result or failure reason.
            - data (dict):
                - risk_amount (float or None):
                    Amount of money at risk in the trade.
                - value_per_point (float or None):
                    Monetary value of one pip in the account currency.
                - lot_size (float or None):
                    Suggested lot size for the trade, rounded to two decimal places.
    """
    logger.info(f"Calculating lot size for {symbol}: equity={account_equity}, risk_pct={risk_pct}%, SL_pips={stop_loss_pips}")

    if account_equity <= 0 or risk_pct <= 0 or stop_loss_pips <= 0:
        msg = "Equity, risk percentage, and stop-loss pips must be > 0"
        logger.error(msg)
        return {
            "status": "error",
            "message": msg,
            "data": {
                "risk_amount": None,
                "value_per_point": None,
                "lot_size": None
            }
        }

    info = mt5.symbol_info(symbol)
    if not info:
        msg = f"Symbol not found: {symbol}"
        logger.error(msg)
        return {
            "status": "error",
            "message": msg,
            "data": {
                "risk_amount": None,
                "value_per_point": None,
                "lot_size": None
            }
        }

    account_currency = "USD"  

    risk_amount = account_equity * (risk_pct / 100.0)

    point = info.point
    contract_size = info.trade_contract_size
    profit_currency = info.currency_profit

    value_per_point = contract_size * point

    if profit_currency != account_currency:
        conversion_symbol = f"{profit_currency}{account_currency}"
        conversion_info = mt5.symbol_info(conversion_symbol)
        if not conversion_info:
            msg = f"Cannot convert {profit_currency} to {account_currency}: symbol {conversion_symbol} not found"
            logger.error(msg)
            return {
                "status": "error",
                "message": msg,
                "data": {
                    "risk_amount": None,
                    "value_per_point": None,
                    "lot_size": None
                }
            }
        conversion_rate = mt5.symbol_info_tick(conversion_symbol).ask
        value_per_point *= conversion_rate

    try:
        lot_size = risk_amount / (stop_loss_pips * value_per_point)
    except ZeroDivisionError:
        msg = "Stop loss or value per point is zero"
        logger.error(msg)
        return {
            "status": "error",
            "message": msg,
            "data": {
                "risk_amount": None,
                "value_per_point": None,
                "lot_size": None
            }
        }
    
    if(risk_pct > 100):
        msg = "Lot size calculated successfully, but with a risk percentage exceeding 100%, you'll need to use leverage to execute this trade."
    else:
        msg = f"Lot size calculated successfully for {symbol}"

    result = {
        "status": "success",
        "message": msg,
        "data": {
            "risk_amount": round(risk_amount, 2),
            "value_per_point": round(value_per_point, 4),
            "lot_size": round(lot_size/10, 2),
        }
    }

    logger.info(f"Lot size calculated successfully for {symbol}: {result}")
    return result