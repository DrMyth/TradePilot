from utils.logger import logger
from utils.mt5_client import mt5
from typing import Dict, Any

def _fetch_account_info() -> Dict[str, Any]:
    """
    Internal helper to retrieve all account information from the MetaTrader 5 terminal.

    This function wraps the direct call to `mt5.account_info()` and centralizes error handling.
    It will attempt to fetch the latest account snapshot, convert the returned named tuple
    into a Python dictionary, and return it for downstream use.

    Raises:
        RuntimeError: If the call to `mt5.account_info()` returns None, indicating a failure
                      to communicate or retrieve data from the MT5 terminal. The exception
                      message includes the MT5 error code and description.

    Returns:
        dict: A mapping of all MT5 account fields, such as:
            - login (int): Account number
            - trade_mode (int): 0=real, 1=demo, 2=contest
            - leverage (int): Account leverage
            - limit_orders (int): Maximum pending orders allowed
            - margin_so_mode (int): Margin safety mode
            - trade_allowed (bool): Whether trading is allowed
            - trade_expert (bool): Whether expert advisors are allowed
            - margin_mode (int): Margin calculation mode
            - currency_digits (int): Decimal places for currency
            - fifo_close (bool): FIFO closing enabled?
            - balance (float): Current account balance
            - credit (float): Credit amount
            - profit (float): Current floating profit/loss
            - equity (float): Balance + floating profit/loss
            - margin (float): Margin currently in use
            - margin_free (float): Available margin left
            - margin_level (float): Equity / margin * 100
            - margin_so_call (float): Margin call threshold (%)
            - margin_so_so (float): Stop-out threshold (%)
            - margin_initial (float): Initial margin requirement
            - margin_maintenance (float): Maintenance margin requirement
            - assets (float): Total asset value
            - liabilities (float): Total liabilities
            - commission_blocked (float): Commission held in reserve
            - name (str): Client name registered on the account
            - server (str): Name of the connected trading server
            - currency (str): Account deposit currency (e.g., 'USD')
            - company (str): Brokerage company name
    """
    logger.info("Fetching account info...")
    
    info = mt5.account_info()
    if info is None:
        code, message = mt5.last_error()
        logger.error(f"mt5.account_info() failed: [{code}] {message}")
        raise RuntimeError(f"Failed to retrieve account info: [{code}] {message}")
    
    account_data = info._asdict()
    logger.info(f"Account info: {account_data}")
    return account_data