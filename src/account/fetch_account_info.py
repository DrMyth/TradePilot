from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any
from ._fetch_account_info import _fetch_account_info

@mcp.tool()
def fetch_account_info() -> Dict[str, Any]:
    """
    Retrieve and return the full set of MT5 account details as a dictionary.

    This tool calls the internal `_fetch_account_info()` helper to fetch the latest
    snapshot of all account attributes from the MetaTrader 5 API. It logs both the
    request initiation and the final retrieved data for traceability.

    Returns:
        dict: A mapping with the following keys:
            - status (str): "success" if the account info was fetched correctly; otherwise "error".
            - account_info (dict): A mapping of all MT5 account fields, such as:
                - login (int): Account number
                - trade_mode (int): 0 = real, 1 = demo, 2 = contest
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
                - currency (str): Account deposit currency (e.g., "USD")
                - company (str): Brokerage company name

    Raises:
        RuntimeError: If fetching the account data fails, propagated from `_fetch_account_info()`.
    """
    logger.info("Retrieving full account information...")
    
    account_info = _fetch_account_info()
    logger.info(f"Account information: {account_info}")
    
    return {
        "status": "success",
        "account_info": account_info
    }